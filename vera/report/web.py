"""Dựng trang web demo (một file HTML tự chứa, mở được cả khi không có mạng).

    python -m vera.report.web            # → data/demo/VeRA_demo.html

Gom dữ liệu thật từ các lượt chạy (E1 là chính; E1_p2, E1_qwen3, E1_llm4decompile, E4, E6,
gold set, self-test) thành một JSON, rồi chèn vào mẫu `demo/web/template.html`.
Không tính lại gì: mọi con số lấy từ results.json / score.json / consistency.json đã commit.
"""
from __future__ import annotations

import json
import re

from vera.common import ARTIFACTS, CONFIGS, DATA, FN_IDS, ROOT, SRC, load_manifest
from vera.report import explain as X

RUN = "E1"
OUT = DATA / "demo" / "VeRA_demo.html"
TEMPLATE = ROOT / "demo" / "web" / "template.html"


def _j(path):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def evidence(v: dict) -> str:
    ce = v.get("counterexample")
    if ce:
        if ce.get("oracle_ret"):
            return (f"Vector {ce['vector']} ({ce.get('tag')}): binary thật trả {ce['expected_ret']}, "
                    f"cài đặt chuẩn trả {ce['oracle_ret']}")
        return f"Vector {ce.get('vector')} ({ce.get('tag', '')}): thực tế {ce.get('observed', '')}"
    if v.get("found"):
        return "Tìm thấy trong binary: " + "; ".join(
            f"{f['value']} ({f.get('form')})" for f in v["found"])
    if v.get("fingerprint"):
        return "Dấu vân tay khớp: " + ", ".join(f"{f['value']} ({f['form']})" for f in v["fingerprint"])
    if v.get("missing"):
        return "Không tìm thấy trong binary: " + ", ".join(m["value"] for m in v["missing"])
    return v.get("detail") or v.get("reason") or ""


def build_item(fn: str, cfg: str, pseudo: str, analysis: dict, vclaims: list[dict], v1raw: dict, truth: dict,
               changed: str | None = None, others: dict | None = None, live_translate: bool = False) -> dict:
    """Gói một item cho giao diện: claim kèm bản dịch + lời giải thích, mã kèm chú thích.

    truth = {group, algLabel, diff, desc, src, writes_out, highlight: [hằng cần tô], note}
    """
    out = analysis.get("output") or {}
    claims = []
    alg_texts = {re.sub(r"\W+", " ", c["text"].lower()).strip() for c in vclaims
                 if c["type"] == "ALG" and c.get("source") != "algorithm_field"}
    for c in vclaims:
        # Hiển thị: bỏ claim ALG ngầm (từ trường algorithm) khi nó trùng câu ALG model đã viết
        if c.get("source") == "algorithm_field" and (
                re.sub(r"\W+", " ", ("implements " + c.get("raw_algorithm", "")).lower()).strip() in alg_texts
                or c["verdict"].get("reason", "").startswith("không nhận ra")):
            continue
        v = c["verdict"]
        text = f"Implements {c['raw_algorithm']}" if c.get("raw_algorithm") else c["text"]
        claims.append({"type": c["type"], "text": text, "conf": c.get("confidence"), "label": v["label"],
                       "method": v.get("method"), "ev": evidence(v), "why": X.explain(c, v),
                       "fromField": c.get("source") == "algorithm_field"})
    texts = [c["text"] for c in claims] + ([out["summary"]] if out.get("summary") else [])
    vi = X.translate(texts, save=False) if live_translate else [X.cached_translation(t) for t in texts]
    for c, t in zip(claims, vi):
        c["vi"] = t
    v1 = {"compiled": v1raw.get("compiled"), "fepr": v1raw.get("fepr"), "n": v1raw.get("n_vectors"),
          "match": v1raw.get("n_match"), "err": v1raw.get("compile_error") or v1raw.get("error"),
          "fails": [{"v": f["vector"], "tag": f["tag"], "exp": f["expected_ret"], "got": f["got_ret"]}
                    for f in v1raw.get("failures", [])[:3]]}
    v1["why"] = X.explain_v1(v1) if analysis.get("schema_valid") else ""
    rc = out.get("recovered_c", "")
    return {
        "fn": fn, "cfg": cfg, "group": truth["group"], "algLabel": truth["algLabel"], "diff": truth.get("diff"),
        "desc": truth["desc"], "src": truth["src"], "pseudo": pseudo, "valid": bool(analysis.get("schema_valid")),
        "model": {"alg": out.get("algorithm"), "name": out.get("proposed_name"), "summary": out.get("summary"),
                  "summaryVi": vi[-1] if out.get("summary") else ""},
        "claims": claims, "dropped": len(analysis.get("dropped_claims", [])), "rc": rc, "v1": v1,
        "others": others or {},
        "notes": {"pseudo": X.annotate_pseudo(pseudo, claims, changed, truth.get("highlight")),
                  "rc": X.annotate_recovered(rc, truth.get("writes_out"), v1),
                  "src": X.annotate_source(truth["src"], truth.get("highlight", []), truth.get("note", ""))},
    }


def truth_of(fn: str) -> dict:
    m = load_manifest(fn)
    key = [c["value"] for c in m["characteristic_constants"][:1]] + m.get("characteristic_strings", [])[:1]
    note = ("khác chuẩn ở đây" if m["group"] == "near_miss" else
            f"hằng đặc trưng của {m['algorithm_label']}" if m["group"] == "classic" else "")
    return {"group": m["group"], "algLabel": m["algorithm_label"], "diff": m.get("difference_from_standard"),
            "desc": m["description"], "src": (SRC / f"{fn}.c").read_text(encoding="utf-8"),
            "writes_out": m["io_semantics"]["writes_out"], "highlight": key if note else [], "note": note}


def item(fn: str, cfg: str) -> dict:
    d = DATA / "runs" / RUN / cfg
    a = _j(d / f"{fn}.analysis.json") or {}
    vd = _j(d / f"{fn}.verdicts.json") or {}
    v1 = _j(d / f"{fn}.v1.json") or {}
    others = {}
    for run, key in (("E1_qwen3", "qwen3"), ("E1_llm4decompile", "l4d")):
        o = _j(DATA / "runs" / run / cfg / f"{fn}.v1.json")
        others[key] = None if o is None else o.get("fepr")
    pseudo = (ARTIFACTS / cfg / f"{fn}.pseudocode.c").read_text(encoding="utf-8")
    return build_item(fn, cfg, pseudo, a, vd.get("claims", []), v1, truth_of(fn), others=others)


def summary() -> dict:
    runs = {r: _j(DATA / "runs" / r / "results.json") for r in ("E1", "E1_p2", "E1_qwen3", "E1_llm4decompile")}
    e1 = runs["E1"]
    keep = ("overall", "by_config", "by_group", "by_type_config", "e2_matrix", "e3", "v1", "controls",
            "rq3_confidence_auroc", "rq3_n", "paired_config_tests", "io_dsl", "prompt_echo", "n_items", "n_schema_valid")
    slim = {r: ({k: x.get(k) for k in keep} if x else None) for r, x in runs.items()}
    for x in slim.values():
        if x and x.get("v1"):
            for c in x["v1"].values():
                c.pop("fepr_all", None)
    info = e1.get("run_info", {})
    cons = _j(DATA / "runs" / "E4" / "consistency.json") or {}
    cons.pop("rows", None)
    stab = _j(DATA / "runs" / "E6" / "stability.json") or {}
    stab.pop("per_function", None)
    st = _j(DATA / "v3_selftest.json") or {}
    gold = _j(DATA / "gold" / "E1" / "score.json")
    key = _j(DATA / "gold" / "E1" / "key.json") or []
    cfg_stats = _j(DATA / "cfg_stats.json") or {}
    return {
        "runs": slim,
        "model": {"name": info.get("model", {}).get("model"), "quant": info.get("model", {}).get("details", {}).get("quantization_level"),
                  "backend": info.get("backend", {}).get("version")},
        "gold": gold, "goldN": len(key),
        "e4": cons, "e6": stab,
        "selftest": {"rate": st.get("false_alarm_rate"), "falseSupport": len(st.get("false_support", [])),
                     "trials": st.get("false_support_trials")},
        "obf": {fn: round(s["obf"]["jcc"] / max(s["opt"]["jcc"], 1), 2) for fn, s in cfg_stats.items()},
    }


def translate_all(model: str = "qwen3:8b") -> None:
    """Dịch trước mọi câu nhận định + tóm tắt của E1 (một lần gọi mỗi item), lưu cache."""
    for fn in FN_IDS:
        for cfg in CONFIGS:
            d = DATA / "runs" / RUN / cfg
            a, vd = _j(d / f"{fn}.analysis.json") or {}, _j(d / f"{fn}.verdicts.json") or {}
            texts = [f"Implements {c['raw_algorithm']}" if c.get("raw_algorithm") else c["text"]
                     for c in vd.get("claims", [])]
            if (a.get("output") or {}).get("summary"):
                texts.append(a["output"]["summary"])
            if texts:
                got = X.translate(texts, model=model)
                print(f"[dịch] {cfg}/{fn}: {sum(bool(g) for g in got)}/{len(texts)}", flush=True)


def main() -> None:
    import sys
    if "--translate" in sys.argv:
        translate_all()
    html = render(live=False)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html, encoding="utf-8", newline="\n")
    print(f"[web] {OUT} ({OUT.stat().st_size // 1024} KB)")


def render(live: bool = False) -> str:
    """HTML tự chứa. live=True: bật thẻ “Chạy trực tiếp” (chỉ dùng khi phục vụ qua vera.webapp)."""
    data = {"items": [item(fn, cfg) for fn in FN_IDS for cfg in CONFIGS], "summary": summary()}
    blob = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return (TEMPLATE.read_text(encoding="utf-8").replace("/*__VERA_DATA__*/null", blob)
            .replace("/*__VERA_LIVE__*/false", "true" if live else "false"))


if __name__ == "__main__":
    main()
