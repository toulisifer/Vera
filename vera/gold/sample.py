"""Lấy mẫu phân tầng 120 claim và xuất file gán nhãn MÙ cho hai người gán nhãn.

    python -m vera.gold.sample --run E1 --n 120

Tầng = nhãn của bộ kiểm chứng (supported+verified / unsupported / contradicted) × cấu hình
(plain / opt / obf): 9 tầng, chia đều; tầng thiếu claim thì lấy hết và dồn phần dư sang tầng khác.

Ghi vào data/gold/<run>/:
  key.json           ÁNH XẠ id → claim + nhãn bộ kiểm chứng (KHÔNG đưa cho người gán nhãn)
  annotator_A.csv    cùng tập claim, thứ tự xáo khác nhau, không có nhãn bộ kiểm chứng
  annotator_B.csv
"""
from __future__ import annotations

import argparse
import csv
import json
import random

from vera.common import CONFIGS, DATA, load_manifest

STRATA_LABELS = {"verified": "supported", "supported": "supported",
                 "unsupported": "unsupported", "contradicted": "contradicted"}
COLUMNS = ["gold_id", "fn", "config", "claim_type", "claim_text", "asserted_values", "source_file",
           "reference_description", "label", "note"]


def collect(run: str) -> list[dict]:
    out = []
    for f in sorted((DATA / "runs" / run).glob("*/*.verdicts.json")):
        v = json.loads(f.read_text(encoding="utf-8"))
        for c in v["claims"]:
            out.append({"fn": v["fn"], "config": v["config"], "claim_id": c["id"], "type": c["type"],
                        "text": c.get("raw_algorithm") and f"The function implements {c['raw_algorithm']}." or c["text"],
                        "asserted_values": c.get("asserted_values", []), "verifier_label": c["verdict"]["label"],
                        "stratum": (STRATA_LABELS[c["verdict"]["label"]], v["config"])})
    return out


def stratified(claims: list[dict], n: int, rng: random.Random) -> list[dict]:
    strata = {(lab, cfg): [c for c in claims if c["stratum"] == (lab, cfg)]
              for lab in ("supported", "unsupported", "contradicted") for cfg in CONFIGS}
    for pool in strata.values():
        rng.shuffle(pool)
    quota = {k: 0 for k in strata}
    remaining = n
    while remaining > 0:  # chia vòng tròn, bỏ qua tầng đã cạn
        progressed = False
        for k in strata:
            if remaining and quota[k] < len(strata[k]):
                quota[k] += 1
                remaining -= 1
                progressed = True
        if not progressed:
            break
    return [c for k in strata for c in strata[k][:quota[k]]]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--n", type=int, default=120)
    ap.add_argument("--seed", type=int, default=20260924)
    a = ap.parse_args()
    rng = random.Random(a.seed)
    sample = stratified(collect(a.run), a.n, rng)
    for i, c in enumerate(sample):
        c["gold_id"] = f"g{i:03d}"
    out_dir = DATA / "gold" / a.run
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "key.json").write_text(json.dumps(sample, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    for who in ("A", "B"):
        rows = sample[:]
        random.Random(f"{a.seed}-{who}").shuffle(rows)
        with open(out_dir / f"annotator_{who}.csv", "w", newline="", encoding="utf-8-sig") as fh:
            w = csv.DictWriter(fh, fieldnames=COLUMNS)
            w.writeheader()
            for c in rows:
                w.writerow({"gold_id": c["gold_id"], "fn": c["fn"], "config": c["config"], "claim_type": c["type"],
                            "claim_text": c["text"], "asserted_values": " ".join(map(str, c["asserted_values"])),
                            "source_file": f"corpus/src/{c['fn']}.c",
                            "reference_description": load_manifest(c["fn"])["description"],
                            "label": "", "note": ""})
    counts = {}
    for c in sample:
        counts[c["stratum"]] = counts.get(c["stratum"], 0) + 1
    print(f"[gold] {len(sample)} claim → {out_dir}")
    for k, v in sorted(counts.items()):
        print(f"  {k[0]:12} {k[1]:5} {v}")


if __name__ == "__main__":
    main()
