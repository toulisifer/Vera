"""Tính metric của một lượt chạy và xuất results.json + report.md.

    python -m vera.report.metrics --run E1

Đọc analysis/verdicts/v1 của lượt chạy cùng manifest. Mọi tỉ lệ kèm khoảng tin cậy
Wilson 95%. Chỉ "contradicted" được gọi là hallucination (HR_strict); HR_loose được mô tả
là "không kiểm chứng được", phản ánh vùng phủ của bộ kiểm chứng nhiều hơn chất lượng model.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from statistics import mean, median

from vera.common import CONFIGS, DATA, load_manifest
from vera.llm.schema import parse_io
from vera.report.stats import auroc, fmt_rate, mcnemar_exact, rate

# Cụm từ đặc trưng của câu ví dụ trong từng phiên bản prompt — claim chứa cụm này là "chép prompt".
# p3 không còn câu ví dụ, chỉ có khuôn mẫu: dấu hiệu chép là khuôn mẫu chưa điền ("<...>").
PROMPT_ECHO_PHRASES = {
    "p1": ["0x5bd1e995", "returns vera_err when out_cap is smaller than len", "writes exactly len bytes to out",
           "never modifies in"],
    "p2": ["folded with the mask 0xffff", "returns 0x10000", "2-byte sum", "out[0] and out[1] only"],
    "p3": [],
}
TEMPLATE_LEFTOVER = re.compile(r"<[a-z ]+>")


def echoes_prompt(text: str, prompt_version: str) -> bool:
    low = text.lower()
    return (any(ph in low for ph in PROMPT_ECHO_PHRASES.get(prompt_version, []))
            or bool(TEMPLATE_LEFTOVER.search(low)))


GROUPS = ["classic", "near_miss", "custom"]
TYPES = ["ALG", "CONST", "IO", "CF", "SIDE", "NAME"]


def load_run(run: str) -> list[dict]:
    items = []
    for f in sorted((DATA / "runs" / run).glob("*/*.analysis.json")):
        a = json.loads(f.read_text(encoding="utf-8"))
        cfg = f.parent.name
        vf = f.with_name(f.name.replace(".analysis.json", ".verdicts.json"))
        v1f = f.with_name(f.name.replace(".analysis.json", ".v1.json"))
        man = load_manifest(a["fn"])
        items.append({
            "fn": a["fn"], "config": cfg, "group": man["group"], "analysis": a,
            "verdicts": json.loads(vf.read_text(encoding="utf-8")) if vf.exists() else None,
            "v1": json.loads(v1f.read_text(encoding="utf-8")) if v1f.exists() else None,
        })
    return items


def hr_block(claims: list[dict]) -> dict:
    n = len(claims)
    c = Counter(x["verdict"]["label"] for x in claims)
    return {
        "n_claims": n,
        "labels": dict(c),
        "HR_strict": rate(c["contradicted"], n),
        "HR_loose": rate(c["contradicted"] + c["unsupported"], n),
        "verified_or_supported": rate(c["verified"] + c["supported"], n),
    }


def compute(run: str) -> dict:
    items = load_run(run)
    valid = [i for i in items if i["verdicts"]]
    claims = [dict(c, config=i["config"], group=i["group"], fn=i["fn"],
                   prompt_version=i["analysis"].get("prompt_version"))
              for i in valid for c in i["verdicts"]["claims"]]

    res: dict = {"run": run, "n_items": len(items), "n_schema_valid": len(valid)}
    run_json = DATA / "runs" / run / "run.json"
    if run_json.exists():
        res["run_info"] = json.loads(run_json.read_text(encoding="utf-8"))

    # RQ1 — HR tổng, theo cấu hình, nhóm hàm, loại claim, và cấu hình × nhóm
    res["overall"] = hr_block(claims)
    res["by_config"] = {cfg: hr_block([c for c in claims if c["config"] == cfg]) for cfg in CONFIGS}
    res["by_group"] = {g: hr_block([c for c in claims if c["group"] == g]) for g in GROUPS}
    res["by_type"] = {t: hr_block([c for c in claims if c["type"] == t]) for t in TYPES}
    res["by_config_group"] = {f"{cfg}/{g}": hr_block([c for c in claims if c["config"] == cfg and c["group"] == g])
                              for cfg in CONFIGS for g in GROUPS}
    # Hướng dẫn: khi mật độ claim khác nhau giữa cấu hình, so HR TRONG TỪNG loại claim.
    res["by_type_config"] = {f"{t}/{cfg}": hr_block([c for c in claims if c["type"] == t and c["config"] == cfg])
                             for t in TYPES for cfg in CONFIGS}

    # Claim IO: bao nhiêu có trường io parse được theo DSL (phần còn lại luôn unsupported)
    io_claims = [c for c in claims if c["type"] == "IO"]
    res["io_dsl"] = {"parsed": rate(sum(parse_io(c) is not None for c in io_claims), len(io_claims))}

    # Claim chép ví dụ trong prompt (kiểm soát chất lượng prompt)
    echo = [c for c in claims if echoes_prompt(c["text"], c["prompt_version"] or "")]
    res["prompt_echo"] = {"claims": rate(len(echo), len(claims)),
                          "contradicted_among_echo": rate(sum(c["verdict"]["label"] == "contradicted" for c in echo),
                                                          len(echo)),
                          "examples": [f"{c['config']}/{c['fn']}: {c['text']}" for c in echo[:10]]}

    # Biến kiểm soát — mật độ claim
    ctrl = {}
    for cfg in CONFIGS:
        its = [i for i in valid if i["config"] == cfg]
        cl = [c for c in claims if c["config"] == cfg]
        ctrl[cfg] = {
            "claims_per_item": mean(len(i["verdicts"]["claims"]) for i in its) if its else None,
            "mean_claim_words": mean(len(c["text"].split()) for c in cl) if cl else None,
            "dropped_per_item": mean(len(i["analysis"].get("dropped_claims", [])) for i in its) if its else None,
            "type_share": {t: sum(c["type"] == t for c in cl) / len(cl) for t in TYPES} if cl else {},
        }
    res["controls"] = ctrl

    # V1 — compile rate, FEPR
    v1 = {}
    for cfg in CONFIGS:
        its = [i for i in items if i["config"] == cfg and i["v1"]]
        fe = [i["v1"]["fepr"] or 0.0 for i in its]
        v1[cfg] = {"compile_rate": rate(sum(i["v1"]["compiled"] for i in its), len(its)),
                   "fepr_1": rate(sum(f == 1.0 for f in fe), len(fe)),
                   "fepr_median": median(fe) if fe else None, "fepr_all": fe}
    res["v1"] = v1

    # RQ2 / E2 — bảng chéo mức hàm: giải thích sạch (không claim contradicted) × V1 đạt (FEPR = 1)
    matrix = Counter()
    cells = defaultdict(list)
    for i in valid:
        if not i["v1"]:
            continue
        key = ("clean" if i["verdicts"]["explanation_clean"] else "contradicted",
               "v1_pass" if i["v1"]["fepr"] == 1.0 else "v1_fail")
        matrix[key] += 1
        cells["/".join(key)].append(f"{i['config']}/{i['fn']}")
    res["e2_matrix"] = {"/".join(k): v for k, v in matrix.items()}
    res["e2_cells"] = dict(cells)

    # RQ5 / E3 — gán nhầm thuật toán: claim ALG bị V1b đánh contradicted / tổng claim ALG, theo nhóm
    e3 = {}
    for g in GROUPS:
        alg = [c for c in claims if c["group"] == g and c["type"] == "ALG"]
        items_g = [i for i in valid if i["group"] == g]
        named = [i for i in items_g if any(c["type"] == "ALG" for c in i["verdicts"]["claims"])]
        e3[g] = {"alg_claims": len(alg),
                 "misattribution": rate(sum(c["verdict"]["label"] == "contradicted" for c in alg), len(alg)),
                 "items_naming_an_algorithm": rate(len(named), len(items_g)),
                 "named": Counter(c["verdict"].get("algorithm") or "?" for c in alg)}
    res["e3"] = e3

    # RQ3 — độ tự tin tự khai có phân biệt claim contradicted không (AUROC; 0,5 = ngẫu nhiên)
    pos = [c["confidence"] for c in claims if c["verdict"]["label"] == "contradicted"
           and isinstance(c.get("confidence"), (int, float))]
    neg = [c["confidence"] for c in claims if c["verdict"]["label"] != "contradicted"
           and isinstance(c.get("confidence"), (int, float))]
    # điểm "nghi ngờ" = 1 − confidence: claim sai nên có confidence thấp hơn
    res["rq3_confidence_auroc"] = auroc([1 - x for x in pos], [1 - x for x in neg])
    res["rq3_n"] = {"contradicted": len(pos), "other": len(neg)}

    # So sánh cặp giữa cấu hình (cùng hàm): hàm có ≥ 1 claim contradicted
    paired = {}
    by_fn_cfg = {(i["fn"], i["config"]): i for i in valid}
    for a_cfg, b_cfg in (("plain", "opt"), ("opt", "obf"), ("plain", "obf")):
        b = c = 0
        for fn in {i["fn"] for i in valid}:
            ia, ib = by_fn_cfg.get((fn, a_cfg)), by_fn_cfg.get((fn, b_cfg))
            if not ia or not ib:
                continue
            ha, hb = not ia["verdicts"]["explanation_clean"], not ib["verdicts"]["explanation_clean"]
            b += ha and not hb
            c += hb and not ha
        paired[f"{a_cfg}_vs_{b_cfg}"] = {"only_first_hallucinates": b, "only_second_hallucinates": c,
                                         "mcnemar_p": mcnemar_exact(b, c)}
    res["paired_config_tests"] = paired
    return res


def to_markdown(r: dict) -> str:
    L = [f"# Kết quả lượt chạy {r['run']}", ""]
    info = r.get("run_info", {})
    if info:
        m = info.get("model", {})
        L += [f"Model `{m.get('model')}` ({m.get('details', {}).get('quantization_level', '?')}, digest "
              f"`{str(m.get('digest', ''))[:12]}`), Ollama {m.get('ollama')}, temperature {info.get('temperature')}, "
              f"think={info.get('think')}, backend {info.get('backend', {}).get('backend')} "
              f"{info.get('backend', {}).get('version')}.", ""]
    L += [f"{r['n_schema_valid']}/{r['n_items']} item có output đúng schema. "
          "HR_strict = contradicted / tổng claim (hallucination). "
          "HR_loose = (contradicted + unsupported) / tổng claim (**không kiểm chứng được**, không phải hallucination).", "",
          "## RQ1 — HR theo cấu hình", "", "| Cấu hình | Claim | HR_strict | HR_loose |", "|---|---|---|---|"]
    for k, b in [("tổng", r["overall"]), *r["by_config"].items()]:
        L.append(f"| {k} | {b['n_claims']} | {fmt_rate(b['HR_strict'])} | {fmt_rate(b['HR_loose'])} |")
    L += ["", "## RQ1 — HR theo nhóm hàm", "", "| Nhóm | Claim | HR_strict | HR_loose |", "|---|---|---|---|"]
    for k, b in r["by_group"].items():
        L.append(f"| {k} | {b['n_claims']} | {fmt_rate(b['HR_strict'])} | {fmt_rate(b['HR_loose'])} |")
    L += ["", "## RQ1 — HR theo loại claim", "", "| Loại | Claim | HR_strict | HR_loose |", "|---|---|---|---|"]
    for k, b in r["by_type"].items():
        L.append(f"| {k} | {b['n_claims']} | {fmt_rate(b['HR_strict'])} | {fmt_rate(b['HR_loose'])} |")
    L += ["", "## RQ1 — HR_strict theo loại claim × cấu hình (so sánh công bằng khi mật độ claim khác nhau)", "",
          "| Loại | plain | opt | obf |", "|---|---|---|---|"]
    for t in TYPES:
        cells = [r["by_type_config"][f"{t}/{cfg}"] for cfg in CONFIGS]
        if any(b["n_claims"] for b in cells):
            L.append(f"| {t} | " + " | ".join(fmt_rate(b["HR_strict"]) for b in cells) + " |")
    L += ["", f"Claim IO có trường `io` parse được theo DSL (kiểm được bằng vector): {fmt_rate(r['io_dsl']['parsed'])}; "
              "phần còn lại luôn unsupported."]
    pe = r["prompt_echo"]
    L += ["", "## Kiểm soát prompt — claim chép ví dụ", "",
          f"Claim trùng câu ví dụ của prompt: {fmt_rate(pe['claims'])}; trong đó bị contradicted: "
          f"{fmt_rate(pe['contradicted_among_echo'])}.", ""] + [f"- {x}" for x in pe["examples"]]
    L += ["", "## Biến kiểm soát", "", "| Cấu hình | Claim/item | Từ/claim | Claim bị lọc/item |", "|---|---|---|---|"]
    for cfg, c in r["controls"].items():
        if c["claims_per_item"] is not None and c["mean_claim_words"] is not None:
            L.append(f"| {cfg} | {c['claims_per_item']:.1f} | {c['mean_claim_words']:.1f} | {c['dropped_per_item']:.1f} |")
    L += ["", "## V1 — mã khôi phục", "", "| Cấu hình | Compile | FEPR = 1 | FEPR trung vị |", "|---|---|---|---|"]
    for cfg, v in r["v1"].items():
        med = "—" if v["fepr_median"] is None else f"{v['fepr_median']:.2f}"
        L.append(f"| {cfg} | {fmt_rate(v['compile_rate'])} | {fmt_rate(v['fepr_1'])} | {med} |")
    m = r["e2_matrix"]
    L += ["", "## RQ2 — bảng chéo E2 (mức hàm)", "", "| | V1 đạt (FEPR = 1) | V1 không đạt |", "|---|---|---|",
          f"| Giải thích sạch | {m.get('clean/v1_pass', 0)} | {m.get('clean/v1_fail', 0)} |",
          f"| Có claim contradicted | {m.get('contradicted/v1_pass', 0)} | {m.get('contradicted/v1_fail', 0)} |", "",
          "Ô lệch đường chéo (nguồn case study):", "",
          f"- Giải thích sạch nhưng mã sai: {', '.join(r['e2_cells'].get('clean/v1_fail', [])) or '—'}",
          f"- Mã đúng nhưng giải thích sai: {', '.join(r['e2_cells'].get('contradicted/v1_pass', [])) or '—'}", "",
          "## RQ5 — gán nhầm thuật toán (E3)", "", "| Nhóm | Claim ALG | Gán nhầm (V1b contradicted) | Item có gọi tên thuật toán |",
          "|---|---|---|---|"]
    for g, e in r["e3"].items():
        L.append(f"| {g} | {e['alg_claims']} | {fmt_rate(e['misattribution'])} | {fmt_rate(e['items_naming_an_algorithm'])} |")
    au = r["rq3_confidence_auroc"]
    L += ["", "## RQ3 — độ tự tin tự khai", "",
          f"AUROC của (1 − confidence) để dự báo claim contradicted: {'—' if au is None else f'{au:.2f}'} "
          f"({r['rq3_n']['contradicted']} claim contradicted, {r['rq3_n']['other']} claim khác; 0,5 = ngẫu nhiên).", "",
          "## So sánh cặp giữa cấu hình (McNemar chính xác, mức hàm)", "", "| Cặp | Chỉ cấu hình 1 có hallucination | Chỉ cấu hình 2 | p |",
          "|---|---|---|---|"]
    for k, p in r["paired_config_tests"].items():
        L.append(f"| {k} | {p['only_first_hallucinates']} | {p['only_second_hallucinates']} | {p['mcnemar_p']:.3f} |")
    return "\n".join(L) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    a = ap.parse_args()
    r = compute(a.run)
    run_dir = DATA / "runs" / a.run
    (run_dir / "results.json").write_text(json.dumps(r, indent=1, ensure_ascii=False, default=dict) + "\n",
                                          encoding="utf-8")
    md = to_markdown(r)
    (run_dir / "results.md").write_text(md, encoding="utf-8")
    print(md)


if __name__ == "__main__":
    main()
