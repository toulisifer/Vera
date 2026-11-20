"""Thống kê cho mẫu nhỏ: khoảng tin cậy Wilson, AUROC (Mann–Whitney), McNemar chính xác."""
from __future__ import annotations

import math


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Khoảng tin cậy 95% Wilson cho tỉ lệ k/n."""
    if n == 0:
        return (math.nan, math.nan)
    p = k / n
    den = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (max(0.0, centre - half), min(1.0, centre + half))


def rate(k: int, n: int) -> dict:
    lo, hi = wilson(k, n)
    return {"k": k, "n": n, "rate": k / n if n else None, "ci95": [lo, hi]}


def fmt_rate(r: dict) -> str:
    if not r["n"]:
        return "—"
    return f"{r['rate']:.1%} [{r['ci95'][0]:.1%}–{r['ci95'][1]:.1%}] ({r['k']}/{r['n']})"


def auroc(scores_pos: list[float], scores_neg: list[float]) -> float | None:
    """Xác suất một mẫu dương có điểm cao hơn một mẫu âm (tính cả hòa = 0,5)."""
    if not scores_pos or not scores_neg:
        return None
    wins = 0.0
    for p in scores_pos:
        for q in scores_neg:
            wins += 1.0 if p > q else 0.5 if p == q else 0.0
    return wins / (len(scores_pos) * len(scores_neg))


def mcnemar_exact(b: int, c: int) -> float:
    """p-value hai phía của kiểm định McNemar chính xác (b, c = số cặp bất đồng mỗi chiều)."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    p = sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n
    return min(1.0, 2 * p)
