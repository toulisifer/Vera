"""Baseline LLM-as-judge cho verifier (góp ý G1, minor 8).

Model chỉ được xem pseudocode (đúng thứ L2 đã xem) và một claim, rồi trả TRUE / FALSE / UNCLEAR. Không có bằng chứng
binary, không chạy vector. So với nhãn người trên 120 claim gold set E1 và với nhãn của VeRA trên cùng các claim.

    python -m vera.llm.judge --model qwen2.5-coder:7b
    python -m vera.llm.judge --model qwen3:8b --no-think
    python -m vera.llm.judge --report                 # gộp các model đã chạy → data/gold/E1/judge.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import time
import urllib.request
from collections import Counter

from vera.common import ARTIFACTS, DATA
from vera.llm.client import OLLAMA_URL
from vera.llm.prompt import SIGNATURE
from vera.report.revision_g1 import load_claims, load_gold

OUT = DATA / "gold" / "E1" / "judge"
CACHE = DATA / "cache" / "judge"
JUDGE_VERSION = "j1"

SCHEMA = {"type": "object", "required": ["verdict", "reason"],
          "properties": {"verdict": {"type": "string", "enum": ["TRUE", "FALSE", "UNCLEAR"]},
                         "reason": {"type": "string"}}}

SYSTEM = """You are a reverse engineer checking ONE claim about ONE function from a stripped x86-64 Linux shared object.
You receive decompiler output and a claim that another analyst wrote about the function.
The real prototype is: {signature}
(the decompiler may show different parameter types or fewer parameters).
VERA_ERR means the return value 0xFFFFFFFFFFFFFFFF.

Decide whether the claim is true for every valid input of the function:
- TRUE: the code shows the claim holds.
- FALSE: the code shows the claim is wrong, or names an algorithm the function does not implement exactly.
- UNCLEAR: the code does not let you decide.
Answer with JSON only: {{"verdict": "TRUE" | "FALSE" | "UNCLEAR", "reason": "<one sentence>"}}."""

USER = """Function name: {fn}

```
{pseudocode}
```

Claim: {claim}"""


def ask(model: str, fn: str, cfg: str, claim: str, think: bool | None) -> dict:
    pseudo = (ARTIFACTS / cfg / f"{fn}.pseudocode.c").read_text(encoding="utf-8").strip()
    body = {"model": model, "stream": False, "format": SCHEMA,
            "options": {"temperature": 0.0, "seed": 0, "num_ctx": 8192, "num_predict": 512},
            "messages": [{"role": "system", "content": SYSTEM.format(signature=SIGNATURE.format(fn=fn))},
                         {"role": "user", "content": USER.format(fn=fn, pseudocode=pseudo, claim=claim)}]}
    if think is not None:
        body["think"] = think
    key = hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()
    path = CACHE / f"{key}.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    req = urllib.request.Request(f"{OLLAMA_URL}/api/chat", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=600) as r:
        resp = json.load(r)
    try:
        doc = json.loads(resp["message"]["content"])
        verdict = doc["verdict"] if doc.get("verdict") in ("TRUE", "FALSE", "UNCLEAR") else "UNCLEAR"
    except (json.JSONDecodeError, TypeError):
        doc, verdict = None, "UNCLEAR"  # trả lời hỏng tính là không quyết được
    rec = {"verdict": verdict, "reason": (doc or {}).get("reason"), "seconds": round(time.time() - t0, 1)}
    CACHE.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rec, ensure_ascii=False) + "\n", encoding="utf-8")
    return rec


def run(model: str, think: bool | None) -> None:
    gold = load_gold()
    with urllib.request.urlopen(f"{OLLAMA_URL}/api/version", timeout=10) as r:
        ver = json.load(r)["version"]
    rows = []
    for i, g in enumerate(gold, 1):
        rec = ask(model, g["fn"], g["cfg"], g["text"], think)
        rows.append({"id": g["id"], "judge": rec["verdict"], "reason": rec["reason"]})
        print(f"[{i:3}/{len(gold)}] {g['id']} human={g['h']:7} verifier={g['v']:12} judge={rec['verdict']}")
    OUT.mkdir(parents=True, exist_ok=True)
    name = model.replace(":", "_").replace("/", "_") + ("_nothink" if think is False else "")
    (OUT / f"{name}.json").write_text(json.dumps({"model": model, "think": think, "ollama": ver,
                                                  "judge_version": JUDGE_VERSION, "rows": rows},
                                                 indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def metrics(gold: list[dict], pred: dict[str, bool], pop: Counter) -> dict:
    """pred[id] = True nếu bộ chấm nói claim sai. Precision, recall thô và recall có trọng số tầng nhãn VeRA."""
    tf = [g for g in gold if g["h"] in ("TRUE", "FALSE")]
    flagged = [g for g in tf if pred[g["id"]]]
    false = [g for g in tf if g["h"] == "FALSE"]
    hit_w = tot_w = 0.0
    for lab, n in pop.items():  # mẫu số tầng gồm cả claim UNCLEAR, như HR hiệu chỉnh và revision_g1
        s = [g for g in gold if g["v"] == lab]
        if s:
            hit_w += n * sum(g["h"] == "FALSE" and pred[g["id"]] for g in s) / len(s)
            tot_w += n * sum(g["h"] == "FALSE" for g in s) / len(s)
    return {"flagged": len(flagged), "precision": sum(g["h"] == "FALSE" for g in flagged) / len(flagged) if flagged else None,
            "recall_unweighted": sum(pred[g["id"]] for g in false) / len(false),
            "recall_weighted": hit_w / tot_w if tot_w else None}


def kappa(a: list[str], b: list[str]) -> float:
    n = len(a)
    po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    pe = sum(ca[k] * cb[k] for k in set(a) | set(b)) / (n * n)
    return (po - pe) / (1 - pe)


def report() -> None:
    gold, claims = load_gold(), load_claims()
    pop = Counter(c["label"] for c in claims)
    res = {"verifier": metrics(gold, {g["id"]: g["v"] == "contradicted" for g in gold}, pop)}
    rng = random.Random(7)
    for p in sorted(OUT.glob("*.json")):
        d = json.loads(p.read_text(encoding="utf-8"))
        j = {r["id"]: r["judge"] for r in d["rows"]}
        m = metrics(gold, {g["id"]: j[g["id"]] == "FALSE" for g in gold}, pop)
        tf = [g for g in gold if g["h"] in ("TRUE", "FALSE")]
        m["kappa_vs_human"] = kappa([g["h"] for g in tf], [j[g["id"]] for g in tf])
        m["verdicts"] = dict(Counter(j.values()))
        # VeRA và judge cùng nói sai → precision của tổ hợp "cả hai"; "một trong hai" → recall
        m["union_with_verifier"] = metrics(gold, {g["id"]: j[g["id"]] == "FALSE" or g["v"] == "contradicted"
                                                  for g in gold}, pop)
        boots = []
        for _ in range(2000):
            s = [rng.choice(gold) for _ in gold]
            boots.append(metrics(s, {g["id"]: j[g["id"]] == "FALSE" for g in s}, pop)["recall_weighted"])
        b = sorted(x for x in boots if x is not None)
        m["recall_weighted_ci"] = [b[int(0.025 * len(b))], b[int(0.975 * len(b)) - 1]]
        res[d["model"] + ("" if d["think"] is not False else " (no think)")] = {**m, "ollama": d["ollama"]}
    (DATA / "gold" / "E1" / "judge.json").write_text(json.dumps(res, indent=1, ensure_ascii=False) + "\n",
                                                     encoding="utf-8")
    print(json.dumps(res, indent=1, ensure_ascii=False))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model")
    ap.add_argument("--no-think", action="store_true")
    ap.add_argument("--report", action="store_true")
    a = ap.parse_args()
    if a.report:
        report()
    else:
        run(a.model, False if a.no_think else None)


if __name__ == "__main__":
    main()
