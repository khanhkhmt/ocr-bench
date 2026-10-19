"""Hộp thư điều khiển server qua GitHub (nhánh `dieu-khien`) — người dùng không ngồi máy, server Colab có thể sập.

PHÍA SERVER (chạy ngầm trong tmux, python hệ thống, chỉ dùng thư viện chuẩn + git):
    python3 -m htr_test.hop_thu chay [--phut 20] [--kiem-lenh 5]
  - mỗi --phut phút: đẩy trang_thai/STATUS.md (còn sống, giờ, GPU, phiên tmux, commit code, địa chỉ ngrok, dung lượng ổ,
    dòng cuối các log benchmark/chẩn đoán — đã lọc cảnh báo và che token) + chép báo cáo của agent
    (/kaggle/working/hop_thu/bao_cao/*.md → bao_cao/)
  - mỗi --kiem-lenh phút: đọc lenh/PROMPT.md; có ID mới → ghi /kaggle/working/hop_thu/PROMPT_MOI.md cho agent đọc,
    đẩy STATUS ngay (xác nhận đã nhận). Script KHÔNG tự chạy lệnh trong prompt.
  - GIÁM SÁT VIỆC (việc đăng ký bằng `viec`): mỗi --kiem-lenh phút xem phiên tmux còn sống / log có lỗi / đã xong.
    Việc CHẾT hoặc có lỗi → đẩy NGAY su_co/<giờ>-<việc>.md (40 dòng cuối log, đã lọc + che token). Lỗi MẠNG (mất kết
    nối, HTTP 5xx, timeout…) → tự chạy lại ĐÚNG lệnh cũ (huấn luyện / chấm điểm tự đi tiếp từ checkpoint), tối đa
    --tu-chay-lai lần mỗi việc. Lỗi khác (hết VRAM, "✘ LỖI", lỗi code) → KHÔNG tự làm gì, chờ lệnh.
  - NHẬN LỆNH từ lenh/LENH.md (ID mới → chạy, kết quả → trang_thai/LENH_KET_QUA.md, đẩy ngay). CHỈ các lệnh cố định:
        keo_code            git pull nhánh code (thu-2-model-htr) — vd. sau khi sửa lỗi
        chay_lai <việc>     dừng (nếu còn) rồi chạy lại ĐÚNG lệnh đã đăng ký
        dung <việc>         dừng phiên tmux của việc
        log <việc> [n]      đẩy n dòng cuối log (mặc định 100, tối đa 400) lên su_co/
        trang_thai          đẩy STATUS ngay
    Không có lệnh shell tuỳ ý: nội dung trên GitHub chỉ CHỌN trong danh sách trên, lệnh thật nằm trên server.
    python3 -m htr_test.hop_thu viec <tên> --log <file.log> [--xong "✔ XONG"] -- <lệnh…>
        đăng ký + chạy việc trong tmux <tên> (lệnh chạy trong thư mục code, ghi tee -a vào log; truyền GITHUB_TOKEN /
        HF_TOKEN của môi trường hiện tại vào phiên). Chạy lại đúng lệnh này = chạy lại việc.
PHÍA NGƯỜI ĐIỀU KHIỂN (máy có quyền push):
    python -m htr_test.hop_thu doc                 # in STATUS mới nhất + kết quả lệnh + sự cố mới nhất + nhật ký
    python -m htr_test.hop_thu gui <file.md>       # đặt prompt mới cho agent (lenh/PROMPT.md, ID theo giờ UTC)
    python -m htr_test.hop_thu lenh keo_code "chay_lai ft3"   # gửi lệnh cho server (lenh/LENH.md)
    python -m htr_test.hop_thu theo_doi [--phut 5] # chạy mãi: có sự cố / kết quả lệnh mới → in ra + thông báo desktop
    python -m htr_test.hop_thu nhat_ky "<nội dung>" # ghi một dòng vào nhat_ky.md (việc đã làm qua SSH)

An toàn: chỉ đọc log trong danh sách cho phép (benchmark / chẩn đoán HTR trên dữ liệu CÔNG KHAI); bỏ mọi dòng có
"real_docs"; che mọi chuỗi giống token (ghp_, github_pat_, hf_...). Token GitHub chỉ đi qua header (biến GITHUB_TOKEN),
không ghi vào .git/config.
"""

from __future__ import annotations

import argparse
import base64
import glob
import json
import os
import re
import shlex
import shutil
import socket
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BRANCH = "dieu-khien"
CODE_BRANCH = "thu-2-model-htr"
WORK = Path(os.environ.get("HOP_THU_WORK", "/kaggle/working"))
BOX = WORK / "hop_thu"
CODE = Path(os.environ.get("HOP_THU_CODE", Path(__file__).resolve().parents[1]))
VIEC_F = BOX / "viec.json"
LOI = re.compile(r"✘ LỖI|CUDA out of memory|OutOfMemoryError|Traceback \(most recent call last\)|^\w*Error: |Killed|"
                 r"Segmentation fault|core dumped")
LOI_MANG = re.compile(r"ConnectionError|ConnectTimeout|ReadTimeout|RemoteDisconnected|Temporary failure in name resolution|"
                      r"Connection (reset|refused|aborted)|HTTPError: 5\d\d|50[234] Server Error|IncompleteRead|"
                      r"Max retries exceeded")
LOI_KHONG_TU_SUA = re.compile(r"CUDA out of memory|OutOfMemoryError|✘ LỖI|SyntaxError|ImportError|ModuleNotFoundError|"
                              r"NameError|AttributeError|TypeError|KeyError")
LOGS = ["htr_bench*.log", "htr_chan_doan*.log", "htr_eval*.log", "htr_cd*.log"]
SECRET = re.compile(r"(ghp_|gho_|github_pat_|hf_)[A-Za-z0-9_]{16,}")
NOISE = re.compile(r"warn\(|UserWarning|FutureWarning|DeprecationWarning|Fetching \d+ files|it/s\]|s/it\]|^\s*$")


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def sh(cmd: str, timeout: int = 30) -> str:
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return (r.stdout + r.stderr).strip()
    except Exception as e:  # noqa: BLE001
        return f"(lỗi: {e})"


def git(repo: Path, *args, check: bool = True) -> subprocess.CompletedProcess:
    cmd = ["git"]
    tok = os.environ.get("GITHUB_TOKEN")
    if tok:
        basic = base64.b64encode(f"x-access-token:{tok}".encode()).decode()
        cmd += ["-c", f"http.extraHeader=Authorization: Basic {basic}"]
    p = subprocess.run([*cmd, "-C", str(repo), *args], capture_output=True, text=True, timeout=300)
    if check and p.returncode:
        raise RuntimeError(SECRET.sub("***", f"git {args[0]}: {(p.stderr or p.stdout).strip()[-300:]}"))
    return p


def ensure(repo: Path) -> Path:
    if not (repo / ".git").exists():
        repo.mkdir(parents=True, exist_ok=True)
        remote = os.environ.get("HOP_THU_REMOTE") or subprocess.run(
            ["git", "-C", str(CODE), "remote", "get-url", "origin"], capture_output=True, text=True).stdout.strip()
        git(repo, "init", "-q")
        git(repo, "remote", "add", "origin", remote)
        git(repo, "config", "user.name", f"hop_thu ({socket.gethostname()})")
        git(repo, "config", "user.email", "ocrbench@users.noreply.github.com")
    if git(repo, "fetch", "-q", "origin", BRANCH, check=False).returncode == 0:
        git(repo, "checkout", "-q", "-B", BRANCH, "FETCH_HEAD")
        git(repo, "reset", "-q", "--hard", "FETCH_HEAD")
    elif not git(repo, "rev-parse", "--verify", "-q", "HEAD", check=False).stdout.strip():
        git(repo, "checkout", "-q", "--orphan", BRANCH)
    return repo


def push(repo: Path, msg: str) -> str:
    git(repo, "add", "-A")
    if git(repo, "diff", "--cached", "--quiet", check=False).returncode == 0:
        return "không có gì mới"
    git(repo, "commit", "-q", "-m", msg)
    if git(repo, "push", "-q", "origin", f"HEAD:{BRANCH}", check=False).returncode:
        git(repo, "fetch", "-q", "origin", BRANCH)
        git(repo, "rebase", "-q", "-X", "theirs", "FETCH_HEAD")
        git(repo, "push", "-q", "origin", f"HEAD:{BRANCH}")
    return git(repo, "rev-parse", "--short", "HEAD").stdout.strip()


def prompt_id(text: str) -> str:
    m = re.search(r"^ID:\s*(\S+)", text, re.M)
    return m.group(1) if m else ""


# --- phía server ------------------------------------------------------------------------


def log_tail(path: str, n: int = 8) -> list[str]:
    try:
        lines = Path(path).read_text(encoding="utf-8", errors="replace").splitlines()[-400:]
    except Exception:  # noqa: BLE001
        return []
    keep = [ln for ln in lines if not NOISE.search(ln) and "real_docs" not in ln]
    return [SECRET.sub("***", ln)[:300] for ln in keep[-n:]]


def ngrok_urls() -> list[str]:
    try:
        with urllib.request.urlopen("http://127.0.0.1:4040/api/tunnels", timeout=5) as r:
            return [t["public_url"] for t in json.load(r).get("tunnels", [])]
    except Exception:  # noqa: BLE001
        return []


def status(prompt_seen: str, note: str) -> str:
    L = [f"# Trạng thái server — {now()}", "", f"**Còn sống** · {note}", "",
         f"- máy: `{socket.gethostname()}` · {sh('uptime -p')}",
         f"- ngrok (SSH): {', '.join(ngrok_urls()) or '(không thấy)'}",
         f"- code: `{sh(f'git -C {CODE} log --oneline -1')}` (nhánh `{sh(f'git -C {CODE} branch --show-current')}`)",
         f"- ổ {WORK}: {sh(f'df -h {WORK} | tail -1')}",
         f"- RAM: {sh('free -g | grep Mem:')} (cột: tổng / đã dùng / trống / … / còn dùng được, GB)",
         f"- prompt đã nhận gần nhất: `{prompt_seen or '(chưa có)'}`", "",
         "## GPU", "```", sh("nvidia-smi --query-gpu=name,memory.used,memory.total,utilization.gpu --format=csv,noheader"),
         sh("nvidia-smi --query-compute-apps=pid,used_memory,process_name --format=csv,noheader") or "(không có tiến trình)",
         "```", "", "## Phiên tmux", "```", sh("tmux ls") or "(không có)", "```", "", *bang_viec()]
    pats = [str(WORK / p) for p in LOGS] + [v["log"] for v in doc_viec().values()]
    files = sorted({f for pat in pats for f in glob.glob(pat)}, key=os.path.getmtime, reverse=True)[:6]
    for f in files:
        age = (time.time() - os.path.getmtime(f)) / 60
        L += [f"## {Path(f).name} (sửa {age:.0f} phút trước)", "```", *log_tail(f), "```", ""]
    return "\n".join(L) + "\n"


# --- việc (tmux) + giám sát ---------------------------------------------------------------


def doc_viec() -> dict:
    return json.loads(VIEC_F.read_text(encoding="utf-8")) if VIEC_F.exists() else {}


def ghi_viec(v: dict) -> None:
    BOX.mkdir(parents=True, exist_ok=True)
    VIEC_F.write_text(json.dumps(v, ensure_ascii=False, indent=1), encoding="utf-8")


def phien_song(ten: str) -> bool:
    return subprocess.run(["tmux", "has-session", "-t", ten], capture_output=True).returncode == 0


def chay_phien(ten: str, v: dict) -> None:
    """Chạy việc trong tmux <ten>: cd thư mục code; lệnh 2>&1 | tee -a log. Token chỉ qua -e (không in, không ghi file)."""
    log = Path(v["log"])
    log.parent.mkdir(parents=True, exist_ok=True)
    v["vi_tri_log"] = log.stat().st_size if log.exists() else 0  # chỉ xét log từ lần chạy này
    v["lan_chay"] = v.get("lan_chay", 0) + 1
    v["bat_dau"] = now()
    v["trang_thai"] = "đang chạy"
    env = [x for k in ("GITHUB_TOKEN", "HF_TOKEN") if os.environ.get(k) for x in ("-e", f"{k}={os.environ[k]}")]
    cmd = f"cd {shlex.quote(str(CODE))} && ( {v['lenh']} ) 2>&1 | tee -a {shlex.quote(str(log))}"
    subprocess.run(["tmux", "new", "-d", "-s", ten, *env, cmd], check=True)


def dung_phien(ten: str) -> None:
    subprocess.run(["tmux", "kill-session", "-t", ten], capture_output=True)


def log_moi(v: dict) -> list[str]:
    """Các dòng log từ lần chạy hiện tại (sau vi_tri_log)."""
    try:
        with open(v["log"], "rb") as f:
            f.seek(v.get("vi_tri_log", 0))
            return f.read().decode("utf-8", errors="replace").replace("\r", "\n").splitlines()
    except OSError:
        return []


def danh_gia_viec(ten: str, v: dict) -> tuple[str, list[str]]:
    """→ (trạng thái, dòng lỗi): "đang chạy" | "XONG" | "LỖI" (còn sống nhưng log có lỗi) | "CHẾT" (phiên đã thoát)."""
    song = phien_song(ten)  # xem sống/chết TRƯỚC rồi mới đọc log: việc vừa ghi lỗi rồi thoát vẫn thấy được dòng lỗi
    lines = log_moi(v)
    if v.get("xong") and any(v["xong"] in ln for ln in lines):
        return "XONG", []
    loi = [ln for ln in lines if LOI.search(ln)]
    if not song:
        return "CHẾT", loi
    return ("LỖI" if loi else "đang chạy"), loi


def ghi_su_co(repo: Path, ten: str, v: dict, tieu_de: str, n: int = 40) -> Path:
    tail = [ln for ln in log_moi(v) if not NOISE.search(ln) and "real_docs" not in ln][-n:]
    (repo / "su_co").mkdir(exist_ok=True)
    f = repo / "su_co" / f"{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M')}-{ten}.md"
    f.write_text(f"# {tieu_de}\n\n- việc: `{ten}` · lần chạy {v.get('lan_chay')} · bắt đầu {v.get('bat_dau')}\n"
                 f"- lệnh: `{SECRET.sub('***', v['lenh'])}`\n- log: `{v['log']}`\n\n## {len(tail)} dòng cuối log\n```\n"
                 + "\n".join(SECRET.sub("***", ln)[:400] for ln in tail) + "\n```\n", encoding="utf-8")
    return f


def giam_sat(repo: Path, tu_chay_lai: int) -> list[str]:
    """Xem mọi việc; đổi trạng thái → ghi sự cố / tự chạy lại (chỉ lỗi mạng). → danh sách ghi chú (rỗng = không có gì mới)."""
    viec, notes = doc_viec(), []
    for ten, v in viec.items():
        if v.get("trang_thai") in ("XONG", "đã dừng", "CHỜ LỆNH"):
            continue
        tt, loi = danh_gia_viec(ten, v)
        if tt == v.get("trang_thai"):
            continue
        if tt == "XONG":
            v["trang_thai"] = "XONG"
            notes.append(f"{ten} XONG")
            continue
        if tt == "LỖI":  # còn sống mà log có lỗi: báo một lần, để việc tự xử (vd. traceback của luồng phụ)
            v["trang_thai"] = "LỖI"
            ghi_su_co(repo, ten, v, f"⚠ {ten}: log có lỗi nhưng phiên VẪN CHẠY")
            notes.append(f"{ten} có lỗi trong log (vẫn chạy)")
            continue
        if tt == "đang chạy":
            v["trang_thai"] = tt
            continue
        # CHẾT
        duoi = "\n".join(log_moi(v)[-60:])
        mang = bool(LOI_MANG.search(duoi)) and not LOI_KHONG_TU_SUA.search(duoi)
        if mang and v.get("tu_chay_lai", 0) < tu_chay_lai:
            v["tu_chay_lai"] = v.get("tu_chay_lai", 0) + 1
            ghi_su_co(repo, ten, v, f"↻ {ten} chết vì lỗi MẠNG → tự chạy lại (lần {v['tu_chay_lai']}/{tu_chay_lai})")
            chay_phien(ten, v)
            notes.append(f"{ten} chết (lỗi mạng) → tự chạy lại")
        else:
            v["trang_thai"] = "CHỜ LỆNH"
            ly_do = ("lỗi mạng nhưng đã tự chạy lại đủ số lần" if mang else "lỗi không tự sửa được" if loi
                     else "phiên thoát, không thấy dòng lỗi")
            ghi_su_co(repo, ten, v, f"✘ {ten} CHẾT — {ly_do} → CHỜ LỆNH")
            notes.append(f"{ten} CHẾT ({ly_do}) → chờ lệnh")
    if notes:
        ghi_viec(viec)
    return notes


def chay_lenh(repo: Path, text: str) -> list[str]:
    """Thực hiện các dòng lệnh (danh sách cố định) trong lenh/LENH.md. → các dòng kết quả."""
    viec, out = doc_viec(), []
    for raw in text.splitlines():
        ln = raw.strip()
        if not ln or ln.startswith("#") or re.match(r"^(ID|Gửi lúc):", ln):
            continue
        p = ln.split()
        verb, args = p[0], p[1:]
        try:
            if verb == "keo_code":
                git(CODE, "pull", "-q", "origin", CODE_BRANCH)
                out.append(f"✔ keo_code → {sh(f'git -C {shlex.quote(str(CODE))} log --oneline -1')}")
            elif verb in ("chay_lai", "dung", "log") and (not args or args[0] not in viec):
                out.append(f"✘ {ln}: không có việc '{args[0] if args else ''}' (có: {', '.join(viec) or 'chưa có'})")
            elif verb == "chay_lai":
                ten = args[0]
                dung_phien(ten)
                time.sleep(3)
                viec[ten]["tu_chay_lai"] = 0
                chay_phien(ten, viec[ten])
                out.append(f"✔ chay_lai {ten} (lần chạy {viec[ten]['lan_chay']})")
            elif verb == "dung":
                dung_phien(args[0])
                viec[args[0]]["trang_thai"] = "đã dừng"
                out.append(f"✔ dung {args[0]}")
            elif verb == "log":
                n = min(400, int(args[1])) if len(args) > 1 else 100
                f = ghi_su_co(repo, args[0], viec[args[0]], f"log {args[0]} (theo lệnh)", n)
                out.append(f"✔ log {args[0]} {n} dòng → {f.relative_to(repo)}")
            elif verb == "trang_thai":
                out.append("✔ trang_thai")
            else:
                out.append(f"✘ {ln}: lệnh lạ (chỉ có keo_code, chay_lai, dung, log, trang_thai)")
        except Exception as e:  # noqa: BLE001
            out.append(f"✘ {ln}: {SECRET.sub('***', str(e))[:300]}")
    ghi_viec(viec)
    return out


def bang_viec() -> list[str]:
    viec = doc_viec()
    if not viec:
        return []
    L = ["## Việc (giám sát)", "", "| việc | trạng thái | lần chạy | tự chạy lại | bắt đầu | dòng log mới nhất |",
         "|---|---|---:|---:|---|---|"]
    for ten, v in viec.items():
        cuoi = next((ln for ln in reversed(log_moi(v)) if ln.strip() and not NOISE.search(ln)), "")
        L.append(f"| {ten} | {v.get('trang_thai')} | {v.get('lan_chay', 0)} | {v.get('tu_chay_lai', 0)} | "
                 f"{v.get('bat_dau', '')} | `{SECRET.sub('***', cuoi)[:160].replace('|', '/')}` |")
    return L + [""]


def run_server(phut: float, kiem: float, tu_chay_lai: int = 2) -> None:
    BOX.mkdir(parents=True, exist_ok=True)
    (BOX / "bao_cao").mkdir(exist_ok=True)
    repo = WORK / ".dieu-khien-repo"
    seen_f = BOX / "da_nhan.txt"
    seen = seen_f.read_text().strip() if seen_f.exists() else ""
    lenh_f = BOX / "lenh_da_chay.txt"
    lenh_seen = lenh_f.read_text().strip() if lenh_f.exists() else None
    last_push = 0.0
    print(f"hộp thư: đẩy trạng thái mỗi {phut} phút, kiểm lệnh mỗi {kiem} phút → nhánh {BRANCH}", flush=True)
    while True:
        note, force = "định kỳ", False
        try:
            ensure(repo)
            pf = repo / "lenh" / "PROMPT.md"
            if pf.exists():
                text = pf.read_text(encoding="utf-8")
                pid = prompt_id(text)
                if pid and pid != seen:
                    (BOX / "PROMPT_MOI.md").write_text(text, encoding="utf-8")
                    seen = pid
                    seen_f.write_text(pid)
                    note, force = f"ĐÃ NHẬN prompt {pid} → {BOX / 'PROMPT_MOI.md'}", True
                    print(f"[{now()}] {note}", flush=True)
            lf = repo / "lenh" / "LENH.md"
            if lenh_seen is None:  # server MỚI (Kaggle xoá /kaggle/working): lệnh đang có trên GitHub là lệnh CŨ → chỉ ghi nhận
                lenh_seen = prompt_id(lf.read_text(encoding="utf-8")) if lf.exists() else ""
                lenh_f.write_text(lenh_seen)
                print(f"[{now()}] lệnh cũ trên GitHub: {lenh_seen or '(không có)'} — KHÔNG chạy; chỉ chạy lệnh gửi sau lúc này",
                      flush=True)
            if lf.exists():
                text = lf.read_text(encoding="utf-8")
                lid = prompt_id(text)
                if lid and lid != lenh_seen:
                    lenh_seen = lid
                    lenh_f.write_text(lid)  # ghi TRƯỚC khi chạy: server khởi động lại không chạy lại lệnh cũ
                    kq = chay_lenh(repo, text)
                    (repo / "trang_thai").mkdir(exist_ok=True)
                    (repo / "trang_thai" / "LENH_KET_QUA.md").write_text(
                        f"# Kết quả lệnh {lid} — {now()}\n\n" + "\n".join(f"- {x}" for x in kq) + "\n", encoding="utf-8")
                    note, force = f"ĐÃ CHẠY lệnh {lid}: " + "; ".join(kq), True
                    print(f"[{now()}] {note}", flush=True)
            gs = giam_sat(repo, tu_chay_lai)
            if gs:
                note, force = "; ".join(gs), True
                print(f"[{now()}] {note}", flush=True)
            if force or time.time() - last_push >= phut * 60:
                (repo / "trang_thai").mkdir(exist_ok=True)
                (repo / "trang_thai" / "STATUS.md").write_text(status(seen, note), encoding="utf-8")
                for f in (BOX / "bao_cao").glob("*.md"):
                    (repo / "bao_cao").mkdir(exist_ok=True)
                    shutil.copy2(f, repo / "bao_cao" / f.name)
                sha = push(repo, f"trạng thái {now()}: {note}")
                last_push = time.time()
                print(f"[{now()}] ✔ đẩy trạng thái ({sha})", flush=True)
        except Exception as e:  # noqa: BLE001 — không bao giờ chết vì lỗi mạng
            print(f"[{now()}] ✘ {SECRET.sub('***', str(e))}", flush=True)
        time.sleep(kiem * 60)


# --- phía người điều khiển ----------------------------------------------------------------


def theo_doi(repo: Path, phut: float) -> None:
    """Máy người điều khiển: cứ --phut phút kéo nhánh dieu-khien; sự cố / kết quả lệnh MỚI → in + thông báo desktop."""
    def snap() -> dict[str, float]:
        fs = [*(repo / "su_co").glob("*.md")] if (repo / "su_co").exists() else []
        fs += [p for p in [repo / "trang_thai" / "LENH_KET_QUA.md"] if p.exists()]
        return {str(p): p.read_text(encoding="utf-8") for p in fs}
    cu = snap()
    print(f"theo dõi nhánh {BRANCH} mỗi {phut} phút (Ctrl+C để dừng)…", flush=True)
    while True:
        time.sleep(phut * 60)
        try:
            ensure(repo)
        except Exception as e:  # noqa: BLE001
            print(f"[{now()}] ✘ {SECRET.sub('***', str(e))}", flush=True)
            continue
        moi = snap()
        for f, nd in moi.items():
            if cu.get(f) != nd:
                tieu_de = nd.splitlines()[0].lstrip("# ") if nd else f
                print(f"\n[{now()}] ===== {Path(f).name}\n{nd}", flush=True)
                if shutil.which("notify-send"):
                    subprocess.run(["notify-send", "Server OCR", tieu_de], check=False)
        cu = moi


def local_repo() -> Path:
    return ensure(Path(os.environ.get("HOP_THU_LOCAL", Path.home() / ".cache" / "hop_thu_dieu_khien")))


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="lenh", required=True)
    c = sub.add_parser("chay")
    c.add_argument("--phut", type=float, default=20)
    c.add_argument("--kiem-lenh", type=float, default=5)
    c.add_argument("--tu-chay-lai", type=int, default=2, help="số lần tự chạy lại tối đa mỗi việc khi chết vì lỗi mạng")
    v = sub.add_parser("viec")
    v.add_argument("ten")
    v.add_argument("--log", required=True)
    v.add_argument("--xong", default="", help='dòng đánh dấu việc đã xong, vd. "✔ XONG HUẤN LUYỆN"')
    sub.add_parser("doc")
    le = sub.add_parser("lenh")
    le.add_argument("dong", nargs="+")
    td = sub.add_parser("theo_doi")
    td.add_argument("--phut", type=float, default=5)
    g = sub.add_parser("gui")
    g.add_argument("file")
    n = sub.add_parser("nhat_ky")
    n.add_argument("noi_dung")
    argv, cmd = sys.argv[1:], []
    if "--" in argv:  # viec <tên> --log … -- <lệnh…>: mọi thứ sau "--" là lệnh của việc
        i = argv.index("--")
        argv, cmd = argv[:i], argv[i + 1:]
    a = ap.parse_args(argv)
    if a.lenh == "chay":
        run_server(a.phut, a.kiem_lenh, a.tu_chay_lai)
        return 0
    if a.lenh == "viec":
        if not cmd:
            sys.exit("thiếu lệnh sau --")
        if phien_song(a.ten):
            sys.exit(f"✘ phiên tmux {a.ten} đang chạy — dừng nó trước (tmux kill-session -t {a.ten}) hoặc dùng tên khác")
        viec = doc_viec()
        v = {"lenh": " ".join(cmd) if len(cmd) > 1 else cmd[0], "log": str(Path(a.log).resolve()), "xong": a.xong,
             "lan_chay": viec.get(a.ten, {}).get("lan_chay", 0)}
        chay_phien(a.ten, v)
        viec[a.ten] = v
        ghi_viec(viec)
        print(f"✔ việc {a.ten}: tmux {a.ten} · log {v['log']} · hộp thư sẽ giám sát (cần phiên hop_thu đang chạy)")
        return 0
    repo = local_repo()
    if a.lenh == "lenh":
        lid = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        (repo / "lenh").mkdir(exist_ok=True)
        (repo / "lenh" / "LENH.md").write_text(f"ID: {lid}\nGửi lúc: {now()}\n\n" + "\n".join(a.dong) + "\n",
                                              encoding="utf-8")
        print("✔ lệnh", lid, "→", push(repo, f"lệnh {lid}: {'; '.join(a.dong)}"))
        return 0
    if a.lenh == "theo_doi":
        theo_doi(repo, a.phut)
        return 0
    if a.lenh == "doc":
        su_co = sorted((repo / "su_co").glob("*.md"))[-1:] if (repo / "su_co").exists() else []
        for p in [repo / "trang_thai/STATUS.md", repo / "trang_thai/LENH_KET_QUA.md", *su_co, repo / "nhat_ky.md"]:
            print(p.read_text(encoding="utf-8") if p.exists() else f"(chưa có {p.relative_to(repo)})")
        print("commit gần nhất:", git(repo, "log", "-3", "--format=%h %ad %s", "--date=format:%m-%d %H:%M").stdout)
        return 0
    if a.lenh == "gui":
        body = Path(a.file).read_text(encoding="utf-8")
        pid = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M")
        (repo / "lenh").mkdir(exist_ok=True)
        (repo / "lenh" / "PROMPT.md").write_text(f"ID: {pid}\nGửi lúc: {now()}\n\n{body}", encoding="utf-8")
        (repo / "lenh" / "da_gui").mkdir(exist_ok=True)
        shutil.copy2(repo / "lenh" / "PROMPT.md", repo / "lenh" / "da_gui" / f"{pid}.md")
        print("✔ prompt", pid, "→", push(repo, f"prompt {pid}"))
        return 0
    f = repo / "nhat_ky.md"
    old = f.read_text(encoding="utf-8") if f.exists() else "# Nhật ký điều khiển server\n\n"
    f.write_text(old + f"- {now()} — {a.noi_dung}\n", encoding="utf-8")
    print("✔ nhật ký →", push(repo, f"nhật ký {now()}"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
