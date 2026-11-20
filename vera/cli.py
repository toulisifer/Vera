"""VeRA trên dòng lệnh, in kiểu nhật ký công cụ: lệnh thật được chạy và kết quả thô.

    python -m vera.cli fn_08                    # hàm có sẵn: binary + pseudocode của corpus, gọi AI thật
    python -m vera.cli demo/tinh_huong/1_giai_ma_chuoi_malware.c --config opt
    python -m vera.cli my.c --profile text      # file C bất kỳ có VERA_FN(...)

Mọi bước dùng đúng các hàm của trang demo (vera.live, vera.verify.*), chỉ khác cách in.
Kết quả lưu ở data/live/cli-<thời gian>/ (pseudocode.c, analysis.json, verdicts.json, v1.json).
"""
from __future__ import annotations

import argparse
import json
import re
import shlex
import sys
import time
from pathlib import Path

from vera import live
from vera.common import (ARTIFACTS, BUILD, BUILD_CONFIGS, COMMON_CFLAGS, DATA, FN_IDS, INCLUDE, ROOT,
                         load_vectors, so_path)
from vera.corpus.build import build_runner
from vera.corpus.vectors import PROFILES
from vera.extract.evidence import extract
from vera.llm import client
from vera.llm.schema import filter_claims
from vera.verify import sandbox
from vera.verify.label import label_item
from vera.verify.v1 import verify
from vera.verify.v3 import Evidence


def rel(p) -> str:
    try:
        return str(Path(p).relative_to(ROOT))
    except ValueError:
        return str(p)


def cmd(*parts) -> None:
    print("$ " + " ".join(shlex.quote(str(x)) for x in parts), flush=True)


def log(tag: str, msg: str) -> None:
    print(f"[{tag}] {msg}", flush=True)


def why(v: dict) -> str:
    ce = v.get("counterexample") or {}
    if ce.get("oracle_ret"):
        return (f"oracle {v.get('algorithm', '')}: {ce['vector']} ({ce.get('tag')}) "
                f"binary={ce['expected_ret']} oracle={ce['oracle_ret']}")
    if ce:
        return f"{ce.get('vector')} ({ce.get('tag', '')}): {ce.get('observed', '')}"
    if v.get("found"):
        return "found in binary: " + ", ".join(f"{f['value']} ({f.get('form')})" for f in v["found"])
    if v.get("fingerprint"):
        return "fingerprint: " + ", ".join(f"{f['value']} ({f.get('form')})" for f in v["fingerprint"])
    if v.get("missing"):
        return "not found in binary: " + ", ".join(m["value"] for m in v["missing"])
    return v.get("detail") or v.get("reason") or ""


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("target", help="fn_01 … fn_20, hoặc đường dẫn file .c")
    ap.add_argument("--config", default="opt", choices=list(BUILD_CONFIGS))
    ap.add_argument("--profile", default="bytes", choices=list(PROFILES), help="kiểu dữ liệu thử cho file .c")
    ap.add_argument("--show-pseudo", action="store_true", help="in toàn bộ pseudocode")
    run(ap.parse_args())


def run(a: argparse.Namespace) -> None:
    """Một lượt phân tích; vera.shell gọi trực tiếp hàm này."""
    t0 = time.time()
    work = DATA / "live" / f"cli-{time.strftime('%Y%m%d-%H%M%S')}"
    work.mkdir(parents=True, exist_ok=True)
    if not (BUILD / "runner").exists():
        build_runner()
    cfg = BUILD_CONFIGS[a.config]

    if a.target in FN_IDS:
        fn_id, so = a.target, so_path(a.target, a.config)
        log("input", f"{fn_id} from corpus, config {a.config}: {rel(so)}")
        pseudo = (ARTIFACTS / a.config / f"{fn_id}.pseudocode.c").read_text()
        vectors, ev = load_vectors(fn_id), None
        log("vectors", f"{len(vectors)} inputs with expected outputs: data/vectors/{fn_id}.json")
        log("ghidra", f"pseudocode from the archived headless run: {rel(ARTIFACTS / a.config / f'{fn_id}.pseudocode.c')}")
    else:
        src_path = Path(a.target)
        src = src_path.read_text(encoding="utf-8")
        if "VERA_FN(" not in src:
            sys.exit('file must #include "vera.h" and define VERA_FN(fn_99)')
        fn_id = live.LIVE_FN
        c_file, so = work / f"{fn_id}.c", work / f"{fn_id}.so"
        log("input", f"{src_path} (renamed to {fn_id}), config {a.config}")
        cmd("gcc", *[f for f in COMMON_CFLAGS if not f.startswith("-ffile-prefix-map")], *cfg.cflags,
            f"-I{rel(INCLUDE)}", "-o", rel(so), rel(c_file))
        so = live.build(src, a.config, work)
        if cfg.strip:
            cmd("strip", "--strip-all", rel(so))
        log("build", f"{so.stat().st_size} bytes")
        vectors = live.ground_truth_vectors(so, a.profile)
        n_err = sum(v["ret"] == "0xffffffffffffffff" for v in vectors)
        log("vectors", f"{len(vectors)} inputs (profile {a.profile}); expected outputs taken by running the "
                       f"compiled function; {n_err} return VERA_ERR")
        cmd("analyzeHeadless", "<tmp-project>", "live", "-import", rel(so), "-postScript",
            "VeraExportDecomp.java", "<out>", "-deleteProject")
        t = time.time()
        pseudo = live.decompile(so)
        log("ghidra", f"{len(pseudo.splitlines())} lines of pseudocode ({time.time() - t:.1f} s)")
        ev = Evidence(extract(so))
        log("evidence", "immediates (capstone), .rodata, strings and imports read from the binary")
    (work / "pseudocode.c").write_text(pseudo)
    if a.show_pseudo:
        print(pseudo.rstrip())

    log("llm", f"POST {client.OLLAMA_URL}/api/chat  model={client.DEFAULT_MODEL}  temperature=0  (no cache)")
    t = time.time()
    for attempt in range(3):
        try:
            res = client.analyze(fn_id, pseudo, "ghidra", use_cache=False)
            break
        except OSError as e:
            if attempt == 2:
                sys.exit(f"[llm] cannot reach {client.OLLAMA_URL}: {e}")
            log("llm", f"no answer ({e}); retrying in 5 s")
            time.sleep(5)
    res["config"] = a.config
    if not res["schema_valid"]:
        sys.exit("[llm] answer failed the JSON schema twice; run again")
    kept, dropped = filter_claims(res["output"]["claims"])
    res["claims"] = kept
    out = res["output"]
    (work / "analysis.json").write_text(json.dumps(res, indent=1, ensure_ascii=False))
    log("llm", f"{time.time() - t:.1f} s  algorithm={out.get('algorithm')!r}  claims={len(kept)} "
               f"(+{len(dropped)} vague dropped)  -> {rel(work / 'analysis.json')}")

    verdicts = label_item({**res, "fn": fn_id}, ev, vectors)
    (work / "verdicts.json").write_text(json.dumps(verdicts, indent=1, ensure_ascii=False))
    counts: dict[str, int] = {}
    for i, c in enumerate(verdicts["claims"], 1):
        v = c["verdict"]
        counts[v["label"]] = counts.get(v["label"], 0) + 1
        log("verify", f"c{i} {c['type']:5} {v['label'].upper():12} {c['text'][:70]}")
        detail = why(v)
        if detail:
            print(f"{'':10}{v.get('method', '')}: {detail[:150]}")

    lim = " ".join(sandbox.DOCKER_LIMITS)
    cmd(*f"docker run --rm -i {lim} {sandbox.IMAGE} /w/runner /w/recovered.so {fn_id} 2".split())
    v1 = verify({**res, "fn": fn_id}, vectors)
    (work / "v1.json").write_text(json.dumps(v1, indent=1, ensure_ascii=False))
    if not v1.get("compiled"):
        log("v1", f"recovered C does not compile: {str(v1.get('compile_error', '')).strip().splitlines()[0][:140]}")
    else:
        log("v1", f"recovered C: {v1['n_match']}/{v1['n_vectors']} vectors match the binary (FEPR {v1['fepr']})")
        for f in v1.get("failures", [])[:2]:
            print(f"{'':10}{f['vector']} ({f['tag']}): expected {f['expected_ret']}  got {f['got_ret']}")

    order = ["verified", "supported", "unsupported", "contradicted"]
    print("summary: " + ", ".join(f"{counts.get(k, 0)} {k}" for k in order)
          + f"  |  total {time.time() - t0:.0f} s  |  {rel(work)}")


if __name__ == "__main__":
    main()
