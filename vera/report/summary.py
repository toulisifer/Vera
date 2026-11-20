"""Bảng tổng hợp số liệu mọi lượt chạy — data/SUMMARY.md (nguồn số cho báo cáo).

    python -m vera.report.summary
"""
from __future__ import annotations

import json

from vera.common import DATA
from vera.report.stats import fmt_rate

RUNS = [
    ("E1", "Lượt chính — qwen2.5-coder:7b, prompt p3"),
    ("E1_p2", "Ablation prompt p2 (có câu ví dụ) — qwen2.5-coder:7b"),
    ("E1_qwen3", "Model thứ hai — qwen3:8b, tắt thinking, prompt p3"),
    ("E1_llm4decompile", "Baseline V1 — LLM4Decompile-Ref v2 6.7B (chỉ sinh mã)"),
]


def load(run: str) -> dict | None:
    f = DATA / "runs" / run / "results.json"
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else None


def main() -> None:
    L = ["# Tổng hợp kết quả", "", "Sinh bởi `python -m vera.report.summary`. Chi tiết từng lượt: "
         "`data/runs/<lượt>/results.md`. Mọi tỉ lệ kèm khoảng tin cậy Wilson 95%.", "",
         "## Các lượt chạy", "", "| Lượt | Mô tả | Item đúng schema |", "|---|---|---|"]
    res = {r: load(r) for r, _ in RUNS}
    for r, desc in RUNS:
        if res[r]:
            L.append(f"| {r} | {desc} | {res[r]['n_schema_valid']}/{res[r]['n_items']} |")

    L += ["", "## RQ1 — HR_strict (hallucination) theo cấu hình", "", "| Lượt | Tổng | plain | opt | obf |", "|---|---|---|---|---|"]
    for r, _ in RUNS[:3]:
        x = res[r]
        if x:
            L.append(f"| {r} | {fmt_rate(x['overall']['HR_strict'])} | "
                     + " | ".join(fmt_rate(x['by_config'][c]['HR_strict']) for c in ("plain", "opt", "obf")) + " |")
    L += ["", "## RQ1 — HR_strict theo nhóm hàm", "", "| Lượt | classic | near_miss | custom |", "|---|---|---|---|"]
    for r, _ in RUNS[:3]:
        x = res[r]
        if x:
            L.append(f"| {r} | " + " | ".join(fmt_rate(x['by_group'][g]['HR_strict'])
                                             for g in ("classic", "near_miss", "custom")) + " |")
    L += ["", "## V1 — FEPR = 1 (mã khôi phục khớp 50/50 vector)", "", "| Lượt | plain | opt | obf |", "|---|---|---|---|"]
    for r, _ in RUNS:
        x = res[r]
        if x:
            L.append(f"| {r} | " + " | ".join(fmt_rate(x['v1'][c]['fepr_1']) for c in ("plain", "opt", "obf")) + " |")
    L += ["", "## RQ2 — bảng chéo E2 (mức hàm)", "", "| Lượt | sạch & V1 đạt | sạch & V1 hỏng | sai & V1 đạt | sai & V1 hỏng |",
          "|---|---|---|---|---|"]
    for r, _ in RUNS[:3]:
        x = res[r]
        if x:
            m = x["e2_matrix"]
            L.append(f"| {r} | {m.get('clean/v1_pass', 0)} | {m.get('clean/v1_fail', 0)} | "
                     f"{m.get('contradicted/v1_pass', 0)} | {m.get('contradicted/v1_fail', 0)} |")
    L += ["", "## RQ5 — gán nhầm thuật toán (claim ALG bị V1b bác bỏ)", "", "| Lượt | classic | near_miss |", "|---|---|---|"]
    for r, _ in RUNS[:3]:
        x = res[r]
        if x:
            L.append(f"| {r} | {fmt_rate(x['e3']['classic']['misattribution'])} | "
                     f"{fmt_rate(x['e3']['near_miss']['misattribution'])} |")
    L += ["", "## RQ3 — dự báo claim sai", ""]
    if res["E1"]:
        L.append(f"- E1 (temperature 0): AUROC của 1 − confidence = {res['E1']['rq3_confidence_auroc']:.2f}")
    c4 = DATA / "runs" / "E4" / "consistency.md"
    if c4.exists():
        L += ["- E4 (temperature 0,7, 5 lần, cấu hình obf):", "", *[ln for ln in c4.read_text(encoding="utf-8").splitlines()
                                                                  if ln.startswith("|") or ln.startswith("Độ nhất")]]
    s6 = DATA / "runs" / "E6" / "stability.md"
    if s6.exists():
        L += ["", "## E6 — độ ổn định (temperature 0, 3 lần)", "",
              *[ln for ln in s6.read_text(encoding="utf-8").splitlines()[2:] if ln.strip()]]
    L += ["", "## Kiểm soát prompt", ""]
    for r in ("E1_p2", "E1"):
        if res[r]:
            pe = res[r]["prompt_echo"]
            L.append(f"- {r}: claim chép ví dụ {fmt_rate(pe['claims'])}, trong đó bị bác bỏ "
                     f"{fmt_rate(pe['contradicted_among_echo'])}")
    gs = DATA / "gold" / "E1" / "score.json"
    if gs.exists():
        g = json.loads(gs.read_text())

        def ci(x):
            return f"[{x[0]:.0%}–{x[1]:.0%}]"
        L += ["", "## RQ4 — độ chính xác bộ kiểm chứng (gold set 120 claim, E1)", "",
              f"- Cohen's kappa giữa 2 người gán nhãn: {g['kappa']:.2f} ({g['disagreements']} bất đồng / {g['n']})",
              f"- Precision nhãn contradicted: {g['precision_contradicted']:.0%} {ci(g['precision_contradicted_ci'])}",
              f"- Recall nhãn contradicted: {g['recall_contradicted']:.0%} {ci(g['recall_contradicted_ci'])}",
              f"- Precision nhãn supported + verified: {g['precision_supported']:.0%} {ci(g['precision_supported_ci'])}",
              f"- HR_strict thô {g['hr_strict_raw']:.1%} → HR hiệu chỉnh {g['hr_corrected']:.1%} "
              f"[{g['hr_corrected_ci'][0]:.1%}–{g['hr_corrected_ci'][1]:.1%}]",
              "- Phân tích lỗi: `data/gold/E1/analysis.md`"]
    st = DATA / "v3_selftest.json"
    if st.exists():
        s = json.loads(st.read_text())
        L += ["", "## Cổng V3 (self-test)", "",
              f"- Bỏ sót hằng: -O0 {s['false_alarm_rate']['-O0']:.0%}, -O2 {s['false_alarm_rate']['-O2']:.0%} (ngưỡng ≤ 5%)",
              f"- Ủng hộ nhầm thuật toán: {len(s['false_support'])}/{s['false_support_trials']}"]
    (DATA / "SUMMARY.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
