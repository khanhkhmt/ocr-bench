"""Gương checkpoint lên Hugging Face — server (Kaggle/Colab) sập giữa chừng thì phiên sau chạy tiếp, không mất bước nào
quá --save-every.

    g = GuongHF("khanh99/htr-ckpt", out)      # repo RIÊNG TƯ (tự tạo); thư mục con = tên thư mục out (vd. ft3)
    g.khoi_phuc()                             # chưa có ckpt-* trong out → tải ckpt mới nhất + best/ + nhat_ky.jsonl về
    g.day(buoc)                               # sau mỗi lần lưu: đẩy ckpt-<buoc>/, best/, nhat_ky.jsonl (luồng nền)
    g.cho()                                   # đợi lần đẩy đang chạy xong (trước khi ghi đè best/, và lúc kết thúc)

Token: biến môi trường HF_TOKEN (hoặc token đã lưu của huggingface_hub). Không bao giờ in token.
Lỗi mạng khi đẩy chỉ CẢNH BÁO — không làm dừng huấn luyện (bản trên máy vẫn còn).
"""

from __future__ import annotations

import os
import re
import shutil
import tempfile
import threading
from pathlib import Path


class GuongHF:
    def __init__(self, repo: str, out: Path, giu: int = 2, api=None):
        from huggingface_hub import HfApi

        self.repo, self.out, self.run, self.giu = repo, Path(out), Path(out).name, giu
        self.api = api or HfApi(token=os.environ.get("HF_TOKEN") or None)
        self.api.create_repo(repo, repo_type="model", private=True, exist_ok=True)
        if not self.api.model_info(repo).private:
            print(f"⚠ repo {repo} đang CÔNG KHAI — checkpoint sẽ ai cũng xem được", flush=True)
        self._luong: threading.Thread | None = None

    def _ckpt_tren_hf(self) -> list[int]:
        bat = re.compile(rf"^{re.escape(self.run)}/ckpt-(\d+)/trang_thai\.pt$")  # chỉ ckpt ĐỦ file (trang_thai.pt)
        return sorted({int(m.group(1)) for f in self.api.list_repo_files(self.repo) if (m := bat.match(f))})

    def khoi_phuc(self) -> int | None:
        """Thư mục out chưa có ckpt nào → tải ckpt mới nhất trên HF (+ best/, nhat_ky.jsonl). → bước, hoặc None."""
        if any(self.out.glob("ckpt-*")):
            return None
        co = self._ckpt_tren_hf()
        if not co:
            print(f"   HF {self.repo}/{self.run}: chưa có checkpoint — chạy từ đầu", flush=True)
            return None
        from huggingface_hub import snapshot_download

        b = co[-1]
        tmp = Path(tempfile.mkdtemp(prefix="guong_"))
        snapshot_download(self.repo, local_dir=tmp, token=self.api.token,
                          allow_patterns=[f"{self.run}/ckpt-{b}/*", f"{self.run}/best/*", f"{self.run}/nhat_ky.jsonl"])
        src = tmp / self.run
        self.out.mkdir(parents=True, exist_ok=True)
        for ten in (f"ckpt-{b}", "best", "nhat_ky.jsonl"):
            if (src / ten).exists() and not (self.out / ten).exists():
                shutil.move(str(src / ten), str(self.out / ten))
        shutil.rmtree(tmp, ignore_errors=True)
        print(f"✔ HF: đã tải ckpt-{b} (+ best, nhật ký) từ {self.repo}/{self.run} → chạy tiếp", flush=True)
        return b

    def _day(self, buoc: int) -> None:
        try:
            self.api.upload_folder(repo_id=self.repo, folder_path=str(self.out), path_in_repo=self.run,
                                   allow_patterns=[f"ckpt-{buoc}/*", "best/*", "nhat_ky.jsonl", "tham_so.json"],
                                   commit_message=f"{self.run} ckpt-{buoc}")
            for cu in self._ckpt_tren_hf()[:-self.giu]:
                self.api.delete_folder(f"{self.run}/ckpt-{cu}", repo_id=self.repo,
                                       commit_message=f"{self.run}: xoá ckpt-{cu} cũ")
            print(f"✔ HF: đã đẩy ckpt-{buoc} → {self.repo}/{self.run}", flush=True)
        except Exception as e:  # noqa: BLE001 — mạng lỗi không được làm dừng huấn luyện
            print(f"⚠ HF: đẩy ckpt-{buoc} lỗi ({e.__class__.__name__}: {str(e)[:200]}) — huấn luyện vẫn tiếp tục", flush=True)

    def day(self, buoc: int) -> None:
        self.cho()
        self._luong = threading.Thread(target=self._day, args=(buoc,), daemon=True)
        self._luong.start()

    def cho(self) -> None:
        if self._luong is not None:
            self._luong.join()
            self._luong = None
