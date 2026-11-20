"""Chấm gold set: Cohen's kappa, danh sách bất đồng, precision/recall của bộ kiểm chứng, HR hiệu chỉnh.

    python -m vera.gold.score --run E1                 # sau khi A và B điền xong: kappa + file phân xử
    python -m vera.gold.score --run E1 --final         # sau khi phân xử: precision/recall + HR hiệu chỉnh

Nhãn của người gán (cột `label`):
  TRUE       claim đúng với mã nguồn/ground truth
  FALSE      claim sai
  UNCLEAR    claim quá mơ hồ để phán đúng/sai
Nhãn chung cuộc = nhãn khi A và B đồng ý, ngược lại lấy nhãn trong adjudication.csv (M2 điền).

Đối chiếu với bộ kiểm chứng:
  "contradicted" đúng khi người nói FALSE; "supported/verified" đúng khi người nói TRUE.
  precision(contradicted) = P(FALSE | contradicted);  recall(contradicted) = P(contradicted | FALSE)
HR hiệu chỉnh: ước lượng tỉ lệ claim thật sự sai trong từng tầng nhãn của bộ kiểm chứng,
nhân với tỉ trọng của tầng đó trong toàn lượt chạy → khoảng HR thật (bootstrap 95%).
"""
from __future__ import annotations

import argparse
import csv
import json
import random
from collections import Counter

from vera.common import DATA

LABELS = ["TRUE", "FALSE", "UNCLEAR"]


def read_labels(path) -> dict[str, str]:
    with open(path, encoding="utf-8-sig") as fh:
        return {r["gold_id"]: r["label"].strip().upper() for r in csv.DictReader(fh)}


def cohen_kappa(a: list[str], b: list[str]) -> float:
    n = len(a)
    po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    pe = sum(ca[k] * cb[k] for k in set(a) | set(b)) / (n * n)
    return 1.0 if pe == 1 else (po - pe) / (1 - pe)


def bootstrap(fn, data: list, n: int = 2000, seed: int = 7) -> tuple[float, float]:
    rng = random.Random(seed)
    # một lần lấy mẫu lại có thể không chứa claim nào của tầng → fn trả None, bỏ qua
    vals = sorted(v for v in (fn([rng.choice(data) for _ in data]) for _ in range(n)) if v is not None)
    return (vals[int(0.025 * len(vals))], vals[int(0.975 * len(vals)) - 1]) if vals else (float("nan"),) * 2


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--final", action="store_true")
    a = ap.parse_args()
    d = DATA / "gold" / a.run
    key = {c["gold_id"]: c for c in json.loads((d / "key.json").read_text(encoding="utf-8"))}
    la, lb = read_labels(d / "annotator_A.csv"), read_labels(d / "annotator_B.csv")
    ids = sorted(key)
    bad = [i for i in ids if la.get(i) not in LABELS or lb.get(i) not in LABELS]
    if bad:
        raise SystemExit(f"Nhãn thiếu hoặc sai ({len(bad)}), vd. {bad[:5]} — chỉ dùng {LABELS}")
    kappa = cohen_kappa([la[i] for i in ids], [lb[i] for i in ids])
    dis = [i for i in ids if la[i] != lb[i]]
    print(f"[gold] Cohen's kappa = {kappa:.3f} (mục tiêu ≥ 0,70); {len(dis)} bất đồng / {len(ids)}")

    adj_path = d / "adjudication.csv"
    if not a.final:
        with open(adj_path, "w", newline="", encoding="utf-8-sig") as fh:
            w = csv.DictWriter(fh, fieldnames=["gold_id", "fn", "claim_text", "label_A", "label_B", "final_label", "note"])
            w.writeheader()
            for i in dis:
                w.writerow({"gold_id": i, "fn": key[i]["fn"], "claim_text": key[i]["text"],
                            "label_A": la[i], "label_B": lb[i], "final_label": "", "note": ""})
        print(f"[gold] đã ghi {adj_path} cho M2 phân xử; xong thì chạy lại với --final")
        return

    adj = {}
    with open(adj_path, encoding="utf-8-sig") as fh:
        for r in csv.DictReader(fh):
            adj[r["gold_id"]] = r["final_label"].strip().upper()
    final = {i: (la[i] if la[i] == lb[i] else adj.get(i)) for i in ids}
    missing = [i for i in ids if final[i] not in LABELS]
    if missing:
        raise SystemExit(f"Chưa phân xử xong: {missing[:10]}")

    rows = [(key[i]["verifier_label"], final[i]) for i in ids]
    pos_pred = [h for v, h in rows if v == "contradicted"]
    true_false = [v for v, h in rows if h == "FALSE"]
    sup = [h for v, h in rows if v in ("supported", "verified")]

    def prec(pairs, want):
        return sum(h == want for h in pairs) / len(pairs) if pairs else None

    res = {
        "kappa": kappa, "n": len(ids), "disagreements": len(dis),
        "precision_contradicted": prec(pos_pred, "FALSE"),
        "precision_contradicted_ci": bootstrap(lambda s: prec([h for v, h in s if v == "contradicted"], "FALSE"), rows),
        "recall_contradicted": (sum(v == "contradicted" for v in true_false) / len(true_false)) if true_false else None,
        "recall_contradicted_ci": bootstrap(
            lambda s: (lambda tf: sum(v == "contradicted" for v in tf) / len(tf) if tf else None)(
                [v for v, h in s if h == "FALSE"]), rows),
        "precision_supported": prec(sup, "TRUE"),
        "precision_supported_ci": bootstrap(lambda s: prec([h for v, h in s if v in ("supported", "verified")], "TRUE"), rows),
    }
    # HR hiệu chỉnh: P(FALSE | tầng) ước lượng từ gold set, trọng số = tỉ trọng tầng trong toàn lượt chạy
    all_labels = Counter()
    for f in (DATA / "runs" / a.run).glob("*/*.verdicts.json"):
        for c in json.loads(f.read_text(encoding="utf-8"))["claims"]:
            all_labels[c["verdict"]["label"]] += 1
    total = sum(all_labels.values())

    def corrected(sample_rows):
        hr = 0.0
        for lab, cnt in all_labels.items():
            rs = [h for v, h in sample_rows if v == lab]
            if not rs:
                return None
            hr += cnt / total * sum(h == "FALSE" for h in rs) / len(rs)
        return hr

    res["hr_strict_raw"] = all_labels["contradicted"] / total if total else None
    res["hr_corrected"] = corrected(rows)
    res["hr_corrected_ci"] = bootstrap(corrected, rows)
    (d / "score.json").write_text(json.dumps(res, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
