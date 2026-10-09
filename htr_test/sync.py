"""Đồng bộ kết quả chấm (htr_test/eval_lines.py) với GitHub — server (Colab) có thể sập và MẤT ổ bất cứ lúc nào.

Nhánh riêng `results-htr` (không lẫn với nhánh `results` của benchmark), thư mục <tên lần chạy>/:
<model>.jsonl (từng dòng đoán), tom_tat.md / tom_tat.json (kết quả tạm hoặc cuối), chi_tiet.csv + xem_ket_qua.html
(từng dòng, có % đúng). Chỉ dùng cho dữ liệu CÔNG KHAI
(Omar Al-Saleh) — tuyệt đối không dùng cho real_docs. Token: GITHUB_TOKEN qua header (như ocrbench status), không ghi
vào .git/config, không in ra. Lỗi mạng / thiếu token → chỉ cảnh báo, không làm dừng việc chấm.
"""

from __future__ import annotations

import shutil
import time
from datetime import datetime, timezone
from pathlib import Path

from ocrbench.status import _git, _git_out, github_token

FILES = ("*.jsonl", "tom_tat.md", "tom_tat.json", "chi_tiet.csv", "xem_ket_qua.html", "BENCHMARK_HTR.md", "BENCHMARK_HTR.json")


class Sync:
    def __init__(self, out: Path, branch: str = "results-htr", every_min: float = 10):
        if "real_docs" in str(out):
            raise SystemExit("Không đồng bộ kết quả real_docs lên GitHub (dữ liệu khách hàng).")
        self.out, self.branch, self.every = Path(out), branch, every_min * 60
        self.sub = self.out.name  # thư mục con trên nhánh = tên thư mục kết quả
        self.repo = self.out.parent / f".{self.branch}-repo"
        self.remote = _git_out("remote", "get-url", "origin")
        self.last = 0.0
        self.ok = bool(self.remote) and github_token() is not None
        if not self.ok:
            print("⚠ ĐỒNG BỘ GITHUB TẮT: thiếu GITHUB_TOKEN hoặc remote origin — kết quả chỉ nằm trên server", flush=True)

    def _ensure(self) -> None:
        r = self.repo
        if (r / ".git").exists():
            return
        r.mkdir(parents=True, exist_ok=True)
        _git(r, "init", "-q")
        _git(r, "remote", "add", "origin", self.remote)
        _git(r, "config", "user.name", "htr_eval")
        _git(r, "config", "user.email", "ocrbench@users.noreply.github.com")
        if _git(r, "fetch", "-q", "origin", self.branch, remote=self.remote, check=False).returncode == 0:
            _git(r, "checkout", "-q", "-B", self.branch, "FETCH_HEAD")
        else:
            _git(r, "checkout", "-q", "--orphan", self.branch)

    def restore(self) -> list[str]:
        """Kéo kết quả cũ về <out>/ — chỉ chép file .jsonl nào trên GitHub NHIỀU dòng hơn bản ở máy này."""
        if not self.ok:
            return []
        try:
            self._ensure()
            if _git(self.repo, "fetch", "-q", "origin", self.branch, remote=self.remote, check=False).returncode == 0:
                _git(self.repo, "reset", "-q", "--hard", "FETCH_HEAD")
            got = []
            for f in (self.repo / self.sub).glob("*.jsonl"):
                dest = self.out / f.name
                n_remote = len(f.read_text(encoding="utf-8").splitlines())
                n_local = len(dest.read_text(encoding="utf-8").splitlines()) if dest.exists() else 0
                if n_remote > n_local:
                    self.out.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(f, dest)
                    got.append(f"{f.name}: {n_remote} dòng")
            if got:
                print("✔ KHÔI PHỤC từ GitHub: " + ", ".join(got), flush=True)
            return got
        except Exception as e:
            print(f"⚠ khôi phục từ GitHub lỗi: {e}", flush=True)
            return []

    def push(self, note: str) -> bool:
        if not self.ok:
            return False
        try:
            self._ensure()
            dst = self.repo / self.sub
            dst.mkdir(parents=True, exist_ok=True)
            for pat in FILES:
                for f in self.out.glob(pat):
                    shutil.copy2(f, dst / f.name)
            _git(self.repo, "add", "-A")
            if _git(self.repo, "diff", "--cached", "--quiet", check=False).returncode == 0:
                return True
            stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
            _git(self.repo, "commit", "-q", "-m", f"htr_eval {stamp}: {note}")
            if _git(self.repo, "push", "-q", "origin", f"HEAD:{self.branch}", remote=self.remote,
                    check=False).returncode != 0:
                _git(self.repo, "fetch", "-q", "origin", self.branch, remote=self.remote)
                _git(self.repo, "rebase", "-q", "-X", "theirs", "FETCH_HEAD")
                _git(self.repo, "push", "-q", "origin", f"HEAD:{self.branch}", remote=self.remote)
            sha = _git(self.repo, "rev-parse", "--short", "HEAD").stdout.strip()
            print(f"✔ GITHUB: đã đẩy lên nhánh {self.branch}/{self.sub} (commit {sha}) — {note}", flush=True)
            self.last = time.time()
            return True
        except Exception as e:
            print(f"✘ ĐẨY GITHUB THẤT BẠI (chạy tiếp, lần sau thử lại): {e}", flush=True)
            return False

    def due(self) -> bool:
        return self.ok and time.time() - self.last >= self.every
