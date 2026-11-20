"""L3 — gán nhãn cho mọi claim của một lượt chạy.

    python -m vera.verify.label --run E1

Nhãn cuối của claim:
  verified      đúng khi kiểm bằng thực thi (V1b, IO, SIDE)
  supported     có bằng chứng tĩnh ủng hộ (V3)
  unsupported   không tìm được bằng chứng, hoặc loại claim nằm ngoài vùng phủ
  contradicted  có bằng chứng dương tính mâu thuẫn (luôn kèm vector phản ví dụ)
Chỉ "contradicted" được gọi là hallucination (HR_strict).

Trường `algorithm` ở mức hàm được coi là một claim ALG ngầm (id "alg_field") nếu khác
"unknown" và không claim ALG nào đã nêu cùng thuật toán — để RQ5 không phụ thuộc việc
model có viết claim ALG riêng hay không.

Ghi data/runs/<run>/<config>/fn_XX.verdicts.json.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter

from vera.common import ARTIFACTS, DATA, load_vectors
from vera.verify import behaviour
from vera.verify.fingerprints import find_algorithm, is_variant_claim
from vera.verify.v3 import Evidence, check_alg, check_const

LABELS = ["verified", "supported", "unsupported", "contradicted"]


def label_alg(text: str, ev: Evidence, vectors: list[dict]) -> dict:
    alg = find_algorithm(text)
    if alg is None:
        return {"label": "unsupported", "method": "ALG", "reason": "không nhận ra tên thuật toán trong claim"}
    v3 = check_alg(alg, ev)
    res = {"algorithm": alg, "v3": v3}
    if is_variant_claim(text):
        # "biến thể của X": không khẳng định là X chuẩn → không dùng oracle để bác bỏ.
        return {**res, "label": v3["label"], "method": "V3", "variant_claim": True}
    v1b = behaviour.check_oracle(alg, vectors)
    if v1b is None:
        return {**res, "label": v3["label"], "method": "V3", "reason_v1b": f"không có oracle cho {alg}"}
    return {**res, **v1b}


def label_claim(c: dict, ev: Evidence, vectors: list[dict]) -> dict:
    t = c["type"]
    if t == "CONST":
        return check_const(c, ev)
    if t == "ALG":
        return label_alg(c["text"], ev, vectors)
    if t == "IO":
        return behaviour.check_io(c, vectors)
    if t == "SIDE":
        return behaviour.check_side(c, vectors)
    return {"label": "unsupported", "method": "—", "reason": f"loại {t} ngoài vùng phủ kiểm tự động"}


def label_item(analysis: dict, ev: Evidence | None = None, vectors: list[dict] | None = None) -> dict:
    """ev/vectors: truyền vào khi gán nhãn một hàm ngoài corpus (demo trực tiếp)."""
    fn_id, cfg = analysis["fn"], analysis["config"]
    if ev is None:
        ev = Evidence(json.loads((ARTIFACTS / cfg / f"{fn_id}.evidence.json").read_text()))
    if vectors is None:
        vectors = load_vectors(fn_id)
    claims = [dict(c) for c in analysis.get("claims", [])]
    out = analysis.get("output") or {}
    field_alg = re.sub(r"^\s*implements\s+", "", (out.get("algorithm") or ""), flags=re.I).strip().rstrip(".")
    if field_alg and field_alg.lower() != "unknown":
        named = find_algorithm(field_alg)
        already = {find_algorithm(c["text"]) for c in claims if c["type"] == "ALG"}
        if named is None or named not in already:
            claims.append({"id": "alg_field", "type": "ALG", "text": f"The function implements {field_alg}.",
                           "asserted_values": [], "confidence": out.get("self_confidence"),
                           "source": "algorithm_field", "raw_algorithm": field_alg})
    for c in claims:
        text = c["text"] if c.get("source") != "algorithm_field" else c["raw_algorithm"]
        c["verdict"] = label_claim({**c, "text": text}, ev, vectors)
    counts = Counter(c["verdict"]["label"] for c in claims)
    return {
        "fn": fn_id, "config": cfg, "schema_valid": analysis.get("schema_valid"),
        "claims": claims,
        "counts": {k: counts.get(k, 0) for k in LABELS},
        "n_claims": len(claims),
        "explanation_clean": counts.get("contradicted", 0) == 0,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    a = ap.parse_args()
    total = Counter()
    for f in sorted((DATA / "runs" / a.run).glob("*/*.analysis.json")):
        analysis = json.loads(f.read_text(encoding="utf-8"))
        if not analysis.get("schema_valid"):
            continue
        analysis.setdefault("config", f.parent.name)
        v = label_item(analysis)
        f.with_name(f.name.replace(".analysis.json", ".verdicts.json")).write_text(
            json.dumps(v, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        total.update(v["counts"])
        print(f"[L3] {a.run} {v['config']}/{v['fn']}: " + " ".join(f"{k}={v['counts'][k]}" for k in LABELS))
    n = sum(total.values()) or 1
    print(f"[L3] tổng {n} claim — " + ", ".join(f"{k} {total[k]} ({total[k] / n:.0%})" for k in LABELS))


if __name__ == "__main__":
    main()
