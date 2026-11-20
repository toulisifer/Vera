"""Ablation M7 (góp ý G1): decompiler đoán sai prototype hay model kém?

Decompile lại binary của một cấu hình với chữ ký đúng áp sẵn trong Ghidra (VeraExportDecompTrueSig.java), chạy L2
(cùng model, prompt p3, temperature 0, seed 0), V1 và L3 như E1, rồi so với kết quả E1 của cấu hình đó.

    python -m vera.llm.ablation_sig --config obf --decompile    # chạy Ghidra, ghi data/artifacts/<cfg>_truesig/
    python -m vera.llm.ablation_sig --config obf                # L2 + V1 + L3 → data/runs/E7_truesig/<cfg>/
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from vera.common import ARTIFACTS, DATA, FN_IDS, so_path
from vera.extract.pseudocode import GHIDRA_SCRIPT_DIR, ghidra_home
from vera.llm import client
from vera.llm.schema import filter_claims
from vera.verify import v1
from vera.verify.label import label_item

RUN = "E7_truesig"


def decompile(cfg: str) -> None:
    out_dir = ARTIFACTS / f"{cfg}_truesig"
    out_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="vera-ghidra-") as proj, tempfile.TemporaryDirectory() as tmp:
        cmd = [str(ghidra_home() / "support" / "analyzeHeadless"), proj, f"vera_{cfg}_sig",
               "-import", *[str(so_path(f, cfg)) for f in FN_IDS], "-scriptPath", str(GHIDRA_SCRIPT_DIR),
               "-postScript", "VeraExportDecompTrueSig.java", tmp, "-deleteProject"]
        p = subprocess.run(cmd, capture_output=True, text=True)
        ok = set(re.findall(r"VERA_OK (fn_\d\d)", p.stdout + p.stderr))
        if len(ok) != len(FN_IDS):
            raise SystemExit(f"Ghidra lỗi: {re.findall(r'VERA_FAIL .*', p.stdout + p.stderr)}\n{p.stderr[-1500:]}")
        for f in FN_IDS:
            shutil.copy(Path(tmp) / f"{f}.c", out_dir / f"{f}.pseudocode.c")
    print(f"[ablation] {len(FN_IDS)} pseudocode → {out_dir}")


def summarize(run_dir: Path) -> dict:
    s = {"items": 0, "schema_valid": 0, "compiled": 0, "fepr_1": 0, "claims": 0, "contradicted": 0}
    for f in FN_IDS:
        a = json.loads((run_dir / f"{f}.analysis.json").read_text(encoding="utf-8"))
        s["items"] += 1
        s["schema_valid"] += bool(a.get("schema_valid"))
        p = run_dir / f"{f}.v1.json"
        if p.exists():
            v = json.loads(p.read_text(encoding="utf-8"))
            s["compiled"] += bool(v.get("compiled"))
            s["fepr_1"] += v.get("fepr") == 1.0
        p = run_dir / f"{f}.verdicts.json"
        if p.exists():
            cl = json.loads(p.read_text(encoding="utf-8")).get("claims", [])
            s["claims"] += len(cl)
            s["contradicted"] += sum(c["verdict"]["label"] == "contradicted" for c in cl)
    return s


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="obf")
    ap.add_argument("--decompile", action="store_true")
    a = ap.parse_args()
    if a.decompile:
        decompile(a.config)
        return
    backend = json.loads((ARTIFACTS / "backend.json").read_text())["backend"]
    # Đối chứng: pseudocode gốc chạy lại trên cùng phiên bản Ollama, không dùng cache (cache E1 là Ollama 0.34.3),
    # để khác biệt không bị lẫn với việc đổi phiên bản.
    arms = {"truesig": (ARTIFACTS / f"{a.config}_truesig", True),
            "control": (ARTIFACTS / a.config, False)}
    s = {}
    for arm, (src, use_cache) in arms.items():
        out = DATA / "runs" / RUN / f"{a.config}_{arm}"
        out.mkdir(parents=True, exist_ok=True)
        for f in FN_IDS:
            pseudo = (src / f"{f}.pseudocode.c").read_text(encoding="utf-8")
            res = client.analyze(f, pseudo, backend, use_cache=use_cache)
            res["config"] = a.config  # bằng chứng V3 và vector lấy từ đúng binary của cấu hình này
            if res["output"] and res["schema_valid"]:
                res["claims"], res["dropped_claims"] = filter_claims(res["output"]["claims"])
            (out / f"{f}.analysis.json").write_text(json.dumps(res, indent=1, ensure_ascii=False) + "\n",
                                                    encoding="utf-8")
            (out / f"{f}.v1.json").write_text(json.dumps(v1.verify(res), indent=1) + "\n", encoding="utf-8")
            if res["schema_valid"]:
                (out / f"{f}.verdicts.json").write_text(
                    json.dumps(label_item(res), indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
            print(f"[ablation] {arm} {a.config}/{f} valid={res['schema_valid']}", flush=True)
        s[arm] = summarize(out)
    s["E1"] = summarize(DATA / "runs" / "E1" / a.config)
    s["model"] = client.model_info(client.DEFAULT_MODEL)
    (DATA / "runs" / RUN / "summary.json").write_text(json.dumps(s, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(s, indent=1))


if __name__ == "__main__":
    main()
