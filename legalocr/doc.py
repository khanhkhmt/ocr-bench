"""Cấu trúc dữ liệu của một trang đã xử lý — cũng là định dạng JSON lưu ra đĩa (to_dict / from_dict).

Mỗi từ mang đủ để KIỂM CHỨNG: các model đã đọc gì (`readings`), độ đồng thuận, độ tin cậy, vì sao bị đánh dấu
(`reasons`), loại thông tin quan trọng (`entity`), khung ước tính trên ảnh gốc (`box`), gợi ý của LLM (`suggestion`,
KHÔNG BAO GIỜ tự thay vào `text`) và nguồn gốc của chữ đang hiển thị (`origin`: "ocr" = đọc từ ảnh, "human" = người
duyệt đã sửa / xác nhận).

Trạng thái từ:
  read       — các model khớp nhau, đủ tin cậy → in nguyên văn
  uncertain  — có cách đọc nhưng chưa chắc → in "từ[؟]", cần người duyệt
  illegible  — không có cách đọc đáng tin → in "[؟]"
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field

READ, UNCERTAIN, ILLEGIBLE = "read", "uncertain", "illegible"
MARK = "[؟]"


@dataclass
class Word:
    id: str
    text: str
    status: str = UNCERTAIN
    confidence: float = 0.0
    readings: dict[str, str] = field(default_factory=dict)
    features: dict = field(default_factory=dict)
    alternatives: list[str] = field(default_factory=list)
    entity: str | None = None
    critical: bool = False
    reasons: list[str] = field(default_factory=list)
    origin: str = "ocr"
    suggestion: dict | None = None
    box: list[int] | None = None
    review: dict | None = None

    def flag(self, reason: str, status: str = UNCERTAIN) -> None:
        """Hạ trạng thái (read → uncertain → illegible), không bao giờ nâng; ghi lý do."""
        if reason not in self.reasons:
            self.reasons.append(reason)
        order = {READ: 0, UNCERTAIN: 1, ILLEGIBLE: 2}
        if order[status] > order[self.status]:
            self.status = status


@dataclass
class Line:
    id: str
    bbox: list[int]
    polygon: list[list[int]] = field(default_factory=list)
    region: str = "Text"            # Text | Signature | Stamp | Picture (vùng không phải chữ thường)
    script: str = "ar"
    words: list[Word] = field(default_factory=list)
    hyps: dict[str, str] = field(default_factory=dict)     # nguyên văn từng model đọc cả dòng
    hyp_probs: dict[str, list] = field(default_factory=dict)  # xác suất từng từ model tự báo (để chạy lại bỏ phiếu)
    pivot: str | None = None
    reasons: list[str] = field(default_factory=list)
    dropped: list[dict] = field(default_factory=list)      # chữ chỉ thiểu số model đọc ra (nghi bịa) — không in
    crop: str | None = None                                # ảnh bằng chứng của dòng (đường dẫn tương đối)


@dataclass
class Page:
    id: str
    image: str
    image_sha256: str = ""
    size: list[int] = field(default_factory=list)
    lines: list[Line] = field(default_factory=list)
    issues: list[dict] = field(default_factory=list)       # kết quả kiểm tra chéo (crosscheck.py)
    fields: list[dict] = field(default_factory=list)       # thông tin quan trọng đã gom (tên, số tiền, ngày...)
    provenance: dict = field(default_factory=dict)         # model, tham số, tiền xử lý, phiên bản — để tái lập

    def words(self):
        for ln in self.lines:
            yield from ln.words

    def word(self, wid: str) -> Word:
        for w in self.words():
            if w.id == wid:
                return w
        raise KeyError(wid)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "Page":
        lines = [Line(**{**ln, "words": [Word(**w) for w in ln.get("words", [])]}) for ln in d.get("lines", [])]
        return cls(**{**d, "lines": lines})
