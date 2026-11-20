"""In các claim đã gán nhãn của một lượt chạy — để đọc bằng mắt và chọn case study.

    python -m vera.verify.show --run E0 --labels contradicted,verified
"""
from __future__ import annotations

import argparse
import json

from vera.common import DATA


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--labels", default="contradicted")
    a = ap.parse_args()
    want = set(a.labels.split(","))
    for f in sorted((DATA / "runs" / a.run).glob("*/*.verdicts.json")):
        v = json.loads(f.read_text(encoding="utf-8"))
        for c in v["claims"]:
            vd = c["verdict"]
            if vd["label"] not in want:
                continue
            why = vd.get("counterexample") or vd.get("detail") or vd.get("found") or vd.get("reason") or ""
            print(f"{v['config']:5} {v['fn']} {vd['label']:12} {vd.get('method', ''):4} [{c['type']}] "
                  f"{c['text'][:90]}\n{'':24}→ {json.dumps(why, ensure_ascii=False)[:150]}")


if __name__ == "__main__":
    main()
