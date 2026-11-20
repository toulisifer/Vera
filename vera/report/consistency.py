"""E4 (RQ3) — self-consistency; E6 — độ ổn định giữa các lần lặp.

    python -m vera.report.consistency --e4 E4 --e6 E6

E4: mỗi hàm được phân tích K lần ở temperature 0,7 (file fn_XX.sK.*). Với mỗi claim của lần k,
độ nhất quán = tỉ lệ các lần còn lại có một claim "tương đương" (cùng loại, và cùng giá trị
hằng nếu có, ngược lại độ trùng từ Jaccard ≥ 0,5). Giả thuyết H3: claim bị contradicted có độ
nhất quán thấp hơn; đo bằng AUROC của (1 − nhất quán), so với AUROC của (1 − confidence) tự khai.

E6: cùng tập hàm chạy K lần ở temperature 0 — báo cáo HR_strict của từng lần và phương sai.

Ghi data/runs/<E4>/consistency.json|md và data/runs/<E6>/stability.json|md.
"""
from __future__ import annotations

import argparse
import json
import random
import re
from collections import defaultdict
from statistics import mean, pvariance

from vera.common import DATA
from vera.report.stats import auroc
from vera.verify.v3 import qualifying_values

STOP = set("the a an of to and or in on for with by is are be this that it its as at from function uses using "
           "value values when returns return".split())


def words(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9_]+", text.lower()) if w not in STOP}


def equivalent(c1: dict, c2: dict) -> bool:
    if c1["type"] != c2["type"]:
        return False
    n1, s1 = qualifying_values(c1)
    n2, s2 = qualifying_values(c2)
    if n1 or s1 or n2 or s2:
        return bool(set(n1) & set(n2) or set(s1) & set(s2))
    w1, w2 = words(c1["text"]), words(c2["text"])
    return bool(w1 and w2) and len(w1 & w2) / len(w1 | w2) >= 0.5


def load_samples(run: str) -> dict[tuple[str, str], dict[int, list[dict]]]:
    """(config, fn) -> {sample: [claim có verdict]}."""
    out: dict = defaultdict(dict)
    # sorted: thứ tự glob phụ thuộc hệ thống file; bootstrap bên dưới phụ thuộc thứ tự hàng → kết quả phải tất định
    for f in sorted((DATA / "runs" / run).glob("*/*.s*.verdicts.json")):
        m = re.match(r"(fn_\d\d)\.s(\d+)\.verdicts\.json", f.name)
        v = json.loads(f.read_text(encoding="utf-8"))
        out[(f.parent.name, m.group(1))][int(m.group(2))] = v["claims"]
    return out


def bootstrap_auroc(pairs: list[tuple[float, bool]], n: int = 2000, seed: int = 11) -> list[float]:
    rng = random.Random(seed)
    vals = []
    for _ in range(n):
        s = [rng.choice(pairs) for _ in pairs]
        a = auroc([x for x, y in s if y], [x for x, y in s if not y])
        if a is not None:
            vals.append(a)
    vals.sort()
    return [vals[int(0.025 * len(vals))], vals[int(0.975 * len(vals)) - 1]] if vals else [None, None]


def e4(run: str) -> dict:
    data = load_samples(run)
    rows = []  # (consistency, confidence, contradicted)
    for (cfg, fn), samples in data.items():
        ks = sorted(samples)
        for k in ks:
            others = [samples[j] for j in ks if j != k]
            for c in samples[k]:
                if c.get("source") == "algorithm_field":
                    continue
                cons = mean(any(equivalent(c, d) for d in o) for o in others) if others else None
                conf = c.get("confidence") if isinstance(c.get("confidence"), (int, float)) else None
                rows.append({"fn": fn, "config": cfg, "sample": k, "type": c["type"], "consistency": cons,
                             "confidence": conf, "contradicted": c["verdict"]["label"] == "contradicted"})
    sc = [(1 - r["consistency"], r["contradicted"]) for r in rows if r["consistency"] is not None]
    cf = [(1 - r["confidence"], r["contradicted"]) for r in rows if r["confidence"] is not None]
    res = {
        "run": run, "n_items": len(data), "n_claims": len(rows),
        "n_contradicted": sum(r["contradicted"] for r in rows),
        "auroc_self_consistency": auroc([x for x, y in sc if y], [x for x, y in sc if not y]),
        "auroc_self_consistency_ci": bootstrap_auroc(sc),
        "auroc_confidence": auroc([x for x, y in cf if y], [x for x, y in cf if not y]),
        "auroc_confidence_ci": bootstrap_auroc(cf),
        "mean_consistency": {"contradicted": mean([r["consistency"] for r in rows if r["contradicted"]] or [0]),
                             "other": mean([r["consistency"] for r in rows if not r["contradicted"]] or [0])},
        "rows": rows,
    }
    return res


def e6(run: str) -> dict:
    data = load_samples(run)
    per_sample = defaultdict(lambda: [0, 0])
    per_fn = {}
    for (cfg, fn), samples in data.items():
        per_fn[f"{cfg}/{fn}"] = {k: sum(c["verdict"]["label"] == "contradicted" for c in cl) / len(cl) if cl else None
                                 for k, cl in samples.items()}
        for k, cl in samples.items():
            per_sample[k][0] += sum(c["verdict"]["label"] == "contradicted" for c in cl)
            per_sample[k][1] += len(cl)
    hrs = {k: (a / b if b else None) for k, (a, b) in sorted(per_sample.items())}
    vals = [v for v in hrs.values() if v is not None]
    identical = sum(len(set(v.values())) == 1 for v in per_fn.values())
    return {"run": run, "hr_strict_by_repeat": hrs, "variance": pvariance(vals) if len(vals) > 1 else None,
            "range": [min(vals), max(vals)] if vals else None, "per_function": per_fn,
            "functions_with_identical_hr": identical, "n_functions": len(per_fn)}


def fmt(x, ci=None):
    if x is None:
        return "—"
    s = f"{x:.2f}"
    if ci and ci[0] is not None:
        s += f" [{ci[0]:.2f}–{ci[1]:.2f}]"
    return s


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--e4")
    ap.add_argument("--e6")
    a = ap.parse_args()
    if a.e4:
        r = e4(a.e4)
        d = DATA / "runs" / a.e4
        (d / "consistency.json").write_text(json.dumps(r, indent=1) + "\n", encoding="utf-8")
        md = [f"# E4 — độ bất định ({a.e4})", "",
              f"{r['n_items']} item, {r['n_claims']} claim, {r['n_contradicted']} claim contradicted.", "",
              "| Tín hiệu dự báo claim contradicted | AUROC [95% bootstrap] |", "|---|---|",
              f"| 1 − self-consistency | {fmt(r['auroc_self_consistency'], r['auroc_self_consistency_ci'])} |",
              f"| 1 − confidence tự khai | {fmt(r['auroc_confidence'], r['auroc_confidence_ci'])} |", "",
              f"Độ nhất quán trung bình: claim contradicted {r['mean_consistency']['contradicted']:.2f}, "
              f"claim khác {r['mean_consistency']['other']:.2f}. AUROC 0,5 = ngẫu nhiên."]
        (d / "consistency.md").write_text("\n".join(md) + "\n", encoding="utf-8")
        print("\n".join(md))
    if a.e6:
        r = e6(a.e6)
        d = DATA / "runs" / a.e6
        (d / "stability.json").write_text(json.dumps(r, indent=1) + "\n", encoding="utf-8")
        md = [f"# E6 — độ ổn định ({a.e6})", "", "| Lần lặp | HR_strict |", "|---|---|",
              *[f"| {k} | {fmt(v)} |" for k, v in r["hr_strict_by_repeat"].items()], "",
              f"Phương sai HR_strict giữa các lần: {r['variance']}; khoảng {r['range']}. "
              f"{r['functions_with_identical_hr']}/{r['n_functions']} hàm có HR giống hệt ở mọi lần."]
        (d / "stability.md").write_text("\n".join(md) + "\n", encoding="utf-8")
        print("\n".join(md))


if __name__ == "__main__":
    main()
