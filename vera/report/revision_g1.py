"""Số liệu bổ sung theo góp ý G1 (30/10/2026), chỉ tính lại từ dữ liệu đã có của E1 và gold set.

    python -m vera.report.revision_g1        # ghi data/revision_g1.json và in tóm tắt

M1  recall nhãn contradicted có trọng số tầng (cùng trọng số với HR hiệu chỉnh), CI bootstrap claim và cụm theo hàm
M2  precision tách theo nhãn verified / supported và theo loại claim; số claim sai mang nhãn tích cực (có trọng số)
M3  bảng E2 đối chiếu với nhãn người trên các claim đã lấy mẫu
M5  CI bootstrap cụm theo hàm cho HR_strict; số cặp bất đồng của McNemar
minor: claim bị lọc theo cấu hình, item near-miss sai schema, AUROC T=0 kèm CI, các claim ALG near-miss
"""
from __future__ import annotations

import csv
import json
import random
from collections import Counter, defaultdict

from vera.common import DATA
from vera.gold.score import read_labels

RUN = DATA / "runs" / "E1"
GOLD = DATA / "gold" / "E1"
CFGS = ("plain", "opt", "obf")
N_BOOT = 2000
SEED = 7


def ci(vals: list) -> list:
    v = sorted(x for x in vals if x is not None)
    return [round(v[int(0.025 * len(v))], 4), round(v[int(0.975 * len(v)) - 1], 4)] if v else [None, None]


def load_claims() -> list[dict]:
    """Mọi claim của E1 kèm fn, cấu hình, nhãn, độ tự tin."""
    out = []
    for cfg in CFGS:
        for p in sorted((RUN / cfg).glob("fn_*.verdicts.json")):
            d = json.loads(p.read_text(encoding="utf-8"))
            for c in d.get("claims", []):
                out.append({"fn": d["fn"], "cfg": cfg, "type": c["type"], "label": c["verdict"]["label"],
                            "conf": c.get("confidence"), "text": c["text"]})
    return out


def load_gold() -> list[dict]:
    key = {c["gold_id"]: c for c in json.loads((GOLD / "key.json").read_text(encoding="utf-8"))}
    la, lb = read_labels(GOLD / "annotator_A.csv"), read_labels(GOLD / "annotator_B.csv")
    with open(GOLD / "adjudication.csv", encoding="utf-8-sig") as fh:
        adj = {r["gold_id"]: r["final_label"].strip().upper() for r in csv.DictReader(fh)}
    return [{"id": i, "fn": k["fn"], "cfg": k["config"], "type": k["type"], "v": k["verifier_label"],
             "h": la[i] if la[i] == lb[i] else adj[i], "text": k["text"]} for i, k in sorted(key.items())]


def weighted(rows: list[dict], pop: Counter) -> dict | None:
    """Số claim sai ước lượng theo từng nhãn bộ kiểm chứng: N_nhãn × P(FALSE | nhãn) trên gold set."""
    f = {}
    for lab, n in pop.items():
        s = [r for r in rows if r["v"] == lab]
        if not s:
            return None
        f[lab] = n * sum(r["h"] == "FALSE" for r in s) / len(s)
    tot = sum(f.values())
    return {"false": f, "total_false": tot, "recall": f["contradicted"] / tot if tot else None,
            "hr": tot / sum(pop.values())}


def auroc(pos: list[float], neg: list[float]) -> float | None:
    if not pos or not neg:
        return None
    return sum((p > n) + 0.5 * (p == n) for p in pos for n in neg) / (len(pos) * len(neg))


def glmm(claims: list[dict], near: set, classic: set) -> dict:
    """M5: logistic contradicted ~ cấu hình + nhóm hàm, (a) hiệu ứng ngẫu nhiên theo hàm, Gauss-Hermite 20 điểm;
    (b) hệ số thường với sai số chuẩn sandwich theo cụm hàm. Mốc so sánh: plain, classic."""
    import numpy as np
    from scipy import optimize, stats

    names = ["intercept", "opt", "obf", "near_miss", "custom"]
    X = np.array([[1, c["cfg"] == "opt", c["cfg"] == "obf", c["fn"] in near,
                   c["fn"] not in near and c["fn"] not in classic] for c in claims], dtype=float)
    y = np.array([c["label"] == "contradicted" for c in claims], dtype=float)
    fns = sorted({c["fn"] for c in claims})
    idx = [np.array([i for i, c in enumerate(claims) if c["fn"] == f]) for f in fns]
    gh_x, gh_w = np.polynomial.hermite.hermgauss(20)

    def nll(theta):
        b, s = theta[:-1], np.exp(theta[-1])
        tot = 0.0
        for ix in idx:
            eta = X[ix] @ b  # (n_i,)
            u = np.sqrt(2) * s * gh_x  # (20,)
            lin = eta[:, None] + u[None, :]
            ll = (y[ix, None] * lin - np.logaddexp(0, lin)).sum(axis=0)
            m = ll.max()
            tot += m + np.log((gh_w * np.exp(ll - m)).sum() / np.sqrt(np.pi))
        return -tot

    fit = optimize.minimize(nll, np.r_[np.zeros(5), np.log(0.5)], method="BFGS")
    th = fit.x
    h = 1e-4  # Hessian số bằng sai phân trung tâm
    H = np.zeros((6, 6))
    for i in range(6):
        for j in range(6):
            e_i, e_j = np.eye(6)[i] * h, np.eye(6)[j] * h
            H[i, j] = (nll(th + e_i + e_j) - nll(th + e_i - e_j) - nll(th - e_i + e_j) + nll(th - e_i - e_j)) / (4 * h * h)
    se = np.sqrt(np.diag(np.linalg.inv(H)))
    re = {n: {"OR": float(np.exp(th[k])), "ci": [float(np.exp(th[k] - 1.96 * se[k])), float(np.exp(th[k] + 1.96 * se[k]))],
              "p": float(2 * stats.norm.sf(abs(th[k] / se[k])))} for k, n in enumerate(names) if k}
    out = {"random_intercept": {"converged": bool(fit.success), "sd_function": float(np.exp(th[-1])), "terms": re}}

    # (b) logistic thường + sandwich theo cụm hàm
    b = np.zeros(5)
    for _ in range(50):
        p = 1 / (1 + np.exp(-X @ b))
        W = p * (1 - p)
        step = np.linalg.solve(X.T @ (X * W[:, None]), X.T @ (y - p))
        b += step
        if np.abs(step).max() < 1e-10:
            break
    p = 1 / (1 + np.exp(-X @ b))
    bread = np.linalg.inv(X.T @ (X * (p * (1 - p))[:, None]))
    meat = sum(np.outer(X[ix].T @ (y[ix] - p[ix]), X[ix].T @ (y[ix] - p[ix])) for ix in idx)
    G = len(idx)
    V = bread @ meat @ bread * G / (G - 1)
    se2 = np.sqrt(np.diag(V))
    out["cluster_robust"] = {n: {"OR": float(np.exp(b[k])), "ci": [float(np.exp(b[k] - 1.96 * se2[k])),
                                                                  float(np.exp(b[k] + 1.96 * se2[k]))],
                                 "p": float(2 * stats.norm.sf(abs(b[k] / se2[k])))} for k, n in enumerate(names) if k}
    out["n_claims"], out["n_functions"] = len(claims), G
    return out


def side_sensitivity(gold: list[dict], claims: list[dict]) -> dict:
    """M2: nếu SIDE "có ghi out" chỉ được nhãn supported (vì V1 chỉ kiểm có ghi hay không, không kiểm nội dung),
    precision của verified/supported trên gold set và số claim verified trong E1 đổi thế nào. Chỉ là phân tích độ
    nhạy: nhãn chính của bài không đổi, vì sửa verifier theo gold set là học trên tập kiểm tra."""
    def writes(r):
        return r["type"] == "SIDE" and not r["text"].lower().startswith(("does not", "doesn't", "never"))

    def relabel(r):
        return "supported" if r["v"] == "verified" and writes(r) else r["v"]

    out = {}
    for name, f in (("original", lambda r: r["v"]), ("side_write_as_supported", relabel)):
        d = {}
        for lab in ("verified", "supported"):
            s = [r for r in gold if f(r) == lab and r["h"] in ("TRUE", "FALSE")]
            d[lab] = {"n": len(s), "true": sum(r["h"] == "TRUE" for r in s),
                      "precision": sum(r["h"] == "TRUE" for r in s) / len(s) if s else None}
        out[name] = d
    out["e1_verified_side_writes"] = sum(c["label"] == "verified" and c["type"] == "SIDE" and
                                         not c["text"].lower().startswith(("does not", "doesn't", "never"))
                                         for c in claims)
    out["e1_verified_total"] = sum(c["label"] == "verified" for c in claims)
    return out


def main() -> None:
    rng = random.Random(SEED)
    claims, gold = load_claims(), load_gold()
    pop = Counter(c["label"] for c in claims)
    res: dict = {"n_claims": len(claims), "population": dict(pop)}

    # M1 ------------------------------------------------------------------------------------
    w = weighted(gold, pop)
    by_fn_gold = defaultdict(list)
    for r in gold:
        by_fn_gold[r["fn"]].append(r)
    fns = sorted(by_fn_gold)

    def boot_claim():
        return weighted([rng.choice(gold) for _ in gold], pop)

    def boot_cluster():
        return weighted([r for f in (rng.choice(fns) for _ in fns) for r in by_fn_gold[f]], pop)

    bc = [boot_claim() for _ in range(N_BOOT)]
    bf = [boot_cluster() for _ in range(N_BOOT)]
    tf = [r for r in gold if r["h"] == "FALSE"]
    res["M1"] = {
        "recall_unweighted": sum(r["v"] == "contradicted" for r in tf) / len(tf),
        "recall_weighted": w["recall"], "recall_weighted_ci_claim": ci([b and b["recall"] for b in bc]),
        "recall_weighted_ci_cluster_fn": ci([b and b["recall"] for b in bf]),
        "est_false_claims": w["total_false"], "est_false_by_label": w["false"],
        "hr_corrected": w["hr"], "hr_corrected_ci_claim": ci([b and b["hr"] for b in bc]),
        "hr_corrected_ci_cluster_fn": ci([b and b["hr"] for b in bf]),
        "gold_functions": len(fns),
    }

    # M2 ------------------------------------------------------------------------------------
    def prec(rows, labs):
        s = [r for r in rows if r["v"] in labs and r["h"] in ("TRUE", "FALSE")]
        return (sum(r["h"] == "TRUE" for r in s), len(s))

    m2 = {}
    for name, labs in (("verified", {"verified"}), ("supported", {"supported"}),
                       ("verified_or_supported", {"verified", "supported"})):
        k, n = prec(gold, labs)
        m2[name] = {"true": k, "n": n, "precision": k / n,
                    "ci": ci([(lambda kn: kn[0] / kn[1] if kn[1] else None)(prec([rng.choice(gold) for _ in gold], labs))
                              for _ in range(N_BOOT)])}
    m2["by_type_positive"] = {}
    for t in sorted({r["type"] for r in gold}):
        s = [r for r in gold if r["type"] == t and r["v"] in ("verified", "supported")]
        if s:
            m2["by_type_positive"][t] = {"n": len(s), "false": sum(r["h"] == "FALSE" for r in s)}
    m2["by_type_contradicted"] = {}
    for t in sorted({r["type"] for r in gold}):
        s = [r for r in gold if r["type"] == t and r["v"] == "contradicted"]
        if s:
            m2["by_type_contradicted"][t] = {"n": len(s), "false": sum(r["h"] == "FALSE" for r in s)}
    m2["est_false_positive_labelled"] = w["false"]["verified"] + w["false"]["supported"]
    m2["positive_false_examples"] = [{"id": r["id"], "fn": r["fn"], "cfg": r["cfg"], "type": r["type"],
                                      "label": r["v"], "text": r["text"]}
                                     for r in gold if r["v"] in ("verified", "supported") and r["h"] == "FALSE"]
    res["M2"] = m2

    # M3 ------------------------------------------------------------------------------------
    results = json.loads((RUN / "results.json").read_text(encoding="utf-8"))
    gold_by_item = defaultdict(list)
    for r in gold:
        gold_by_item[f"{r['cfg']}/{r['fn']}"].append(r)
    m3 = {}
    for cell, items in results["e2_cells"].items():
        sampled = [i for i in items if gold_by_item.get(i)]
        m3[cell] = {"items": len(items), "items_with_gold_claims": len(sampled),
                    "items_with_human_false": sum(any(r["h"] == "FALSE" for r in gold_by_item[i]) for i in sampled),
                    "gold_claims": sum(len(gold_by_item[i]) for i in sampled),
                    "human_false_claims": sum(r["h"] == "FALSE" for i in sampled for r in gold_by_item[i])}
    res["M3"] = {"e2_vs_human": m3, "io_dsl": results["io_dsl"]["parsed"],
                 "unresolved_share": results["overall"]["HR_loose"]["rate"],
                 "claims_without_checker": sum(c["type"] in ("CF", "NAME") for c in claims)}

    # M5 ------------------------------------------------------------------------------------
    by_fn = defaultdict(list)
    for c in claims:
        by_fn[c["fn"]].append(c)
    allfns = sorted(by_fn)

    def hr(cs):
        return sum(c["label"] == "contradicted" for c in cs) / len(cs) if cs else None

    m5 = {}
    for scope in ("all",) + CFGS:
        sel = (lambda c: True) if scope == "all" else (lambda c, s=scope: c["cfg"] == s)
        base = [c for c in claims if sel(c)]
        boots = [hr([c for f in (rng.choice(allfns) for _ in allfns) for c in by_fn[f] if sel(c)])
                 for _ in range(N_BOOT)]
        m5[scope] = {"k": sum(c["label"] == "contradicted" for c in base), "n": len(base), "rate": hr(base),
                     "ci_cluster_fn": ci(boots)}
    diff = [((lambda b: (hr([c for c in b if c["cfg"] == "obf"]) or 0) - (hr([c for c in b if c["cfg"] == "plain"]) or 0))
             ([c for f in (rng.choice(allfns) for _ in allfns) for c in by_fn[f]])) for _ in range(N_BOOT)]
    m5["obf_minus_plain_ci_cluster_fn"] = ci(diff)
    m5["mcnemar"] = results["paired_config_tests"]
    res["M5"] = m5

    # minor -----------------------------------------------------------------------------------
    dropped = {}
    for cfg in CFGS:
        n_drop = n_items = 0
        for p in sorted((RUN / cfg).glob("fn_*.analysis.json")):
            a = json.loads(p.read_text(encoding="utf-8"))
            if a.get("schema_valid"):
                n_items += 1
                n_drop += len(a.get("dropped_claims") or [])
        dropped[cfg] = {"valid_items": n_items, "dropped_total": n_drop,
                        "retained": sum(c["cfg"] == cfg for c in claims)}
    invalid = [f"{cfg}/{p.name.split('.')[0]}" for cfg in CFGS for p in sorted((RUN / cfg).glob("fn_*.analysis.json"))
               if not json.loads(p.read_text(encoding="utf-8")).get("schema_valid")]
    pos = [1 - c["conf"] for c in claims if c["label"] == "contradicted" and c["conf"] is not None]
    neg = [1 - c["conf"] for c in claims if c["label"] != "contradicted" and c["conf"] is not None]

    def boot_auc_cluster():
        cs = [c for f in (rng.choice(allfns) for _ in allfns) for c in by_fn[f] if c["conf"] is not None]
        return auroc([1 - c["conf"] for c in cs if c["label"] == "contradicted"],
                     [1 - c["conf"] for c in cs if c["label"] != "contradicted"])

    near = {f"fn_{i:02d}" for i in range(8, 15)}
    classic = {f"fn_{i:02d}" for i in range(1, 8)}
    res["minor"] = {
        "dropped": dropped, "invalid_items": invalid,
        "auroc_T0": auroc(pos, neg), "auroc_T0_ci_cluster_fn": ci([boot_auc_cluster() for _ in range(N_BOOT)]),
        "auroc_T0_n_pos": len(pos), "conf_share_1": sum(c["conf"] == 1.0 for c in claims) / len(claims),
        "alg_claims": [{"fn": c["fn"], "cfg": c["cfg"], "group": "near_miss" if c["fn"] in near else
                        "classic" if c["fn"] in classic else "custom", "label": c["label"], "text": c["text"]}
                       for c in claims if c["type"] == "ALG"],
    }
    res["M5c"] = glmm(claims, near, classic)
    res["M2b"] = side_sensitivity(gold, claims)
    (DATA / "revision_g1.json").write_text(json.dumps(res, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(res, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
