"""Dao động ở temperature 0 có đến từ GPU không? (góp ý G1, minor 7)

Gửi đúng một prompt L2 (pseudocode archived, prompt p3, seed 0) nhiều lần liên tiếp, không dùng cache, một lượt chạy
trên GPU và một lượt chỉ dùng CPU (num_gpu = 0). So hash nội dung trả về giữa các lần.

    python -m vera.llm.determinism --fn fn_02 --config opt --runs 5
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter

from vera.common import ARTIFACTS, DATA
from vera.llm import client
from vera.llm import prompt as P


def once(model: str, system: str, user: str, gpu: bool) -> dict:
    options = {"temperature": 0.0, "seed": 0, "num_ctx": 8192, "num_predict": 3072}
    if not gpu:
        options["num_gpu"] = 0  # không đẩy lớp nào lên GPU
    rec = client._chat(model, system, user, options, use_cache=False)
    try:
        doc = json.loads(rec["content"])
        summary = {"algorithm": doc.get("algorithm"), "n_claims": len(doc.get("claims", []))}
    except json.JSONDecodeError:
        summary = {"algorithm": None, "n_claims": None}
    return {"sha256": hashlib.sha256(rec["content"].encode()).hexdigest()[:16], "seconds": rec["seconds"],
            "eval_count": rec["eval_count"], **summary}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fn", default="fn_02")
    ap.add_argument("--config", default="opt")
    ap.add_argument("--runs", type=int, default=5)
    ap.add_argument("--model", default=client.DEFAULT_MODEL)
    a = ap.parse_args()
    pseudo = (ARTIFACTS / a.config / f"{a.fn}.pseudocode.c").read_text(encoding="utf-8")
    system, user = P.build(a.fn, pseudo, "ghidra")
    res = {"fn": a.fn, "config": a.config, "model": a.model, "model_info": client.model_info(a.model)}
    for gpu in (True, False):
        runs = []
        for i in range(a.runs):
            r = once(a.model, system, user, gpu)
            runs.append(r)
            print(f"{'gpu' if gpu else 'cpu'} {i + 1}: {r}")
        res["gpu" if gpu else "cpu"] = {"runs": runs, "distinct_outputs": len(Counter(r["sha256"] for r in runs))}
    (DATA / "runs" / "determinism.json").write_text(json.dumps(res, indent=1, ensure_ascii=False) + "\n",
                                                   encoding="utf-8")
    print(json.dumps({k: res[k]["distinct_outputs"] for k in ("gpu", "cpu")}))


if __name__ == "__main__":
    main()
