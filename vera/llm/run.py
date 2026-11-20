"""Chạy L2 trên một tập item và ghi data/runs/<run>/<config>/fn_XX.analysis.json.

    python -m vera.llm.run --run E0 --fns fn_01,fn_05,fn_08,fn_15,fn_18
    python -m vera.llm.run --run E1                       # 20 hàm × 3 cấu hình
    python -m vera.llm.run --run E4 --configs obf --temperature 0.7 --samples 5

Mỗi file gồm output thô của model, claim sau bộ lọc, claim bị loại kèm lý do, và thông
tin tái lập (model, prompt_version, options, cache key).
"""
from __future__ import annotations

import argparse
import json
import time

from vera.common import ARTIFACTS, CONFIGS, DATA, FN_IDS
from vera.llm import client
from vera.llm.schema import filter_claims

RUNS = DATA / "runs"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--fns", default=",".join(FN_IDS))
    ap.add_argument("--configs", default=",".join(CONFIGS))
    ap.add_argument("--model", default=client.DEFAULT_MODEL)
    ap.add_argument("--temperature", type=float, default=0.0)
    ap.add_argument("--samples", type=int, default=1)
    ap.add_argument("--think", choices=["on", "off"], default=None, help="chế độ suy nghĩ (chỉ model hỗ trợ)")
    ap.add_argument("--num-predict", type=int, default=3072)
    ap.add_argument("--num-ctx", type=int, default=8192)
    a = ap.parse_args()
    think = None if a.think is None else a.think == "on"

    backend = json.loads((ARTIFACTS / "backend.json").read_text())
    run_dir = RUNS / a.run
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "run.json").write_text(json.dumps({
        "run": a.run, "started": time.strftime("%Y-%m-%d %H:%M:%S"), "backend": backend,
        "model": client.model_info(a.model), "temperature": a.temperature, "samples": a.samples, "think": think,
        "num_predict": a.num_predict, "num_ctx": a.num_ctx,
        "fns": a.fns.split(","), "configs": a.configs.split(","),
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    for cfg in a.configs.split(","):
        for fn_id in a.fns.split(","):
            pseudo = (ARTIFACTS / cfg / f"{fn_id}.pseudocode.c").read_text()
            for s in range(a.samples):
                res = client.analyze(fn_id, pseudo, backend["backend"], a.model, a.temperature, sample=s, think=think,
                                     num_predict=a.num_predict, num_ctx=a.num_ctx)
                res["config"] = cfg
                if res["output"] and res["schema_valid"]:
                    kept, dropped = filter_claims(res["output"]["claims"])
                    res["claims"], res["dropped_claims"] = kept, dropped
                suffix = f".s{s}" if a.samples > 1 else ""
                out = run_dir / cfg / f"{fn_id}{suffix}.analysis.json"
                out.parent.mkdir(exist_ok=True)
                out.write_text(json.dumps(res, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
                o = res["output"] or {}
                last = res["attempts"][-1]
                print(f"[{a.run}] {cfg}/{fn_id}{suffix}: valid={res['schema_valid']} tries={len(res['attempts'])} "
                      f"{last['seconds']}s{' (cache)' if last['cached'] else ''} alg={o.get('algorithm')!r} "
                      f"claims={len(res.get('claims', []))}+{len(res.get('dropped_claims', []))}dropped", flush=True)


if __name__ == "__main__":
    main()
