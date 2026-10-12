"""Hiệu chỉnh độ tin cậy trên tập DEV có đáp án: hồi quy logistic (numpy, không cần thêm thư viện) trên các đặc trưng
của fuse.FEATURES → P(từ đúng); rồi chọn ngưỡng "read" nhỏ nhất sao cho tỉ lệ sai trong phần KHÔNG đánh dấu ≤ mục tiêu
(vd. 2% từ thường, 0,5% từ quan trọng). Ngưỡng chọn trên dev; holdout chỉ dùng để báo cáo một lần.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from .fuse import FEATURES


def fit_logistic(rows: list[dict], l2: float = 1.0, iters: int = 3000, lr: float = 0.5) -> dict:
    X = np.array([[r[k] for k in FEATURES] for r in rows], float)
    y = np.array([r["y"] for r in rows], float)
    mu, sd = X.mean(0), X.std(0) + 1e-6
    Z = (X - mu) / sd
    w, b = np.zeros(Z.shape[1]), 0.0
    n = len(y)
    for _ in range(iters):
        p = 1 / (1 + np.exp(-(Z @ w + b)))
        g = p - y
        w -= lr * (Z.T @ g / n + l2 * w / n)
        b -= lr * g.mean()
    # trả về trọng số trên đặc trưng GỐC (fuse.confidence dùng trực tiếp)
    W = w / sd
    B = b - float((w * mu / sd).sum())
    return {"weights": {k: float(v) for k, v in zip(FEATURES, W)}, "bias": float(B), "n": int(n),
            "base_rate": float(y.mean()) if n else 0.0}


def predict(cal: dict, rows: list[dict]) -> np.ndarray:
    X = np.array([[r[k] for k in FEATURES] for r in rows], float)
    W = np.array([cal["weights"][k] for k in FEATURES])
    return 1 / (1 + np.exp(-(X @ W + cal["bias"])))


def pick_threshold(p: np.ndarray, y: np.ndarray, target_residual: float) -> tuple[float, float, float]:
    """Ngưỡng τ nhỏ nhất mà tỉ lệ sai trong {p ≥ τ} ≤ target → (τ, tỉ lệ được in không kèm [؟], tỉ lệ sai thực tế)."""
    order = np.argsort(-p)
    ps, ys = p[order], y[order]
    err = np.cumsum(1 - ys) / np.arange(1, len(ys) + 1)
    ok = np.flatnonzero(err <= target_residual)
    if not ok.size:
        return 1.01, 0.0, 0.0
    k = ok[-1]
    return float(ps[k]), float((k + 1) / len(ys)), float(err[k])


def calibrate(rows: list[dict], target=0.02, target_critical=0.005) -> dict:
    cal = fit_logistic(rows)
    p = predict(cal, rows)
    y = np.array([r["y"] for r in rows], float)
    crit = np.array([r["critical"] > 0 for r in rows])
    tau, cov, res = pick_threshold(p, y, target)
    cal["tau_read"], cal["coverage"], cal["residual"] = tau, cov, res
    if crit.any():
        tc, cc, rc = pick_threshold(p[crit], y[crit], target_critical)
        cal["tau_read_critical"], cal["coverage_critical"], cal["residual_critical"] = max(tc, tau), cc, rc
    return cal


def save(cal: dict, path: Path) -> None:
    path.write_text(json.dumps(cal, indent=1), encoding="utf-8")
