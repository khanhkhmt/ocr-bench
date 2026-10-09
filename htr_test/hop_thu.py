"""Hộp thư điều khiển server qua GitHub (nhánh `dieu-khien`) — người dùng không ngồi máy, server Colab có thể sập.

PHÍA SERVER (chạy ngầm trong tmux, python hệ thống, chỉ dùng thư viện chuẩn + git):
    python3 -m htr_test.hop_thu chay [--phut 20] [--kiem-lenh 5]
  - mỗi --phut phút: đẩy trang_thai/STATUS.md (còn sống, giờ, GPU, phiên tmux, commit code, địa chỉ ngrok, dung lượng ổ,
    dòng cuối các log benchmark/chẩn đoán — đã lọc cảnh báo và che token) + chép báo cáo của agent
    (/kaggle/working/hop_thu/bao_cao/*.md → bao_cao/)
  - mỗi --kiem-lenh phút: đọc lenh/PROMPT.md; có ID mới → ghi /kaggle/working/hop_thu/PROMPT_MOI.md cho agent đọc,
    đẩy STATUS ngay (xác nhận đã nhận). Script KHÔNG tự chạy lệnh trong prompt.
PHÍA NGƯỜI ĐIỀU KHIỂN (máy có quyền push):
    python -m htr_test.hop_thu doc                 # in STATUS mới nhất + nhật ký
    python -m htr_test.hop_thu gui <file.md>       # đặt prompt mới cho agent (lenh/PROMPT.md, ID theo giờ UTC)
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
import shutil
import socket
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BRANCH = "dieu-khien"
WORK = Path(os.environ.get("HOP_THU_WORK", "/kaggle/working"))
BOX = WORK / "hop_thu"
CODE = Path(__file__).resolve().parents[1]
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
        remote = subprocess.run(["git", "-C", str(CODE), "remote", "get-url", "origin"], capture_output=True,
                                text=True).stdout.strip()
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
         f"- prompt đã nhận gần nhất: `{prompt_seen or '(chưa có)'}`", "",
         "## GPU", "```", sh("nvidia-smi --query-gpu=name,memory.used,memory.total,utilization.gpu --format=csv,noheader"),
         sh("nvidia-smi --query-compute-apps=pid,used_memory,process_name --format=csv,noheader") or "(không có tiến trình)",
         "```", "", "## Phiên tmux", "```", sh("tmux ls") or "(không có)", "```", ""]
    files = sorted({f for pat in LOGS for f in glob.glob(str(WORK / pat))}, key=os.path.getmtime, reverse=True)[:5]
    for f in files:
        age = (time.time() - os.path.getmtime(f)) / 60
        L += [f"## {Path(f).name} (sửa {age:.0f} phút trước)", "```", *log_tail(f), "```", ""]
    return "\n".join(L) + "\n"


def run_server(phut: float, kiem: float) -> None:
    BOX.mkdir(parents=True, exist_ok=True)
    (BOX / "bao_cao").mkdir(exist_ok=True)
    repo = WORK / ".dieu-khien-repo"
    seen_f = BOX / "da_nhan.txt"
    seen = seen_f.read_text().strip() if seen_f.exists() else ""
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


def local_repo() -> Path:
    return ensure(Path(os.environ.get("HOP_THU_LOCAL", Path.home() / ".cache" / "hop_thu_dieu_khien")))


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="lenh", required=True)
    c = sub.add_parser("chay")
    c.add_argument("--phut", type=float, default=20)
    c.add_argument("--kiem-lenh", type=float, default=5)
    sub.add_parser("doc")
    g = sub.add_parser("gui")
    g.add_argument("file")
    n = sub.add_parser("nhat_ky")
    n.add_argument("noi_dung")
    a = ap.parse_args()
    if a.lenh == "chay":
        run_server(a.phut, a.kiem_lenh)
        return 0
    repo = local_repo()
    if a.lenh == "doc":
        for f in ["trang_thai/STATUS.md", "nhat_ky.md"]:
            p = repo / f
            print(p.read_text(encoding="utf-8") if p.exists() else f"(chưa có {f})")
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
