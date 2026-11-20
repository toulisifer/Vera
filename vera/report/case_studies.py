"""Trích ứng viên case study từ một lượt chạy (O4: ≥ 2 case study bộ kiểm chứng bắt được hallucination).

    python -m vera.report.case_studies --run E1

Bốn loại ứng viên:
  A. Gán nhầm thuật toán (RQ5): claim ALG bị V1b bác bỏ, kèm vector phản ví dụ.
  B. Giải thích sai nhưng mã khôi phục đúng (ô E2 "contradicted / V1 đạt").
  C. Giải thích sạch nhưng mã khôi phục sai (ô E2 "sạch / V1 không đạt").
  D. Claim IO/SIDE bị vector bác bỏ.
Mỗi ứng viên kèm claim, bằng chứng, đoạn pseudocode model đã đọc và mã nguồn gốc.
Ghi data/runs/<run>/case_studies.md.
"""
from __future__ import annotations

import argparse
import json

from vera.common import ARTIFACTS, DATA, SRC, load_manifest


def snippet(text: str, n: int = 30) -> str:
    lines = text.strip().splitlines()
    return "\n".join(lines[:n]) + ("\n..." if len(lines) > n else "")


def item_block(fn: str, cfg: str, run_dir, extra: list[str]) -> list[str]:
    man = load_manifest(fn)
    v1f = run_dir / cfg / f"{fn}.v1.json"
    v1 = json.loads(v1f.read_text()) if v1f.exists() else {}
    a = json.loads((run_dir / cfg / f"{fn}.analysis.json").read_text(encoding="utf-8"))
    out = a.get("output") or {}
    return [
        f"### {cfg}/{fn} — {man['algorithm_label']} ({man['group']})", "",
        f"- Model: algorithm = `{out.get('algorithm')}`, tên đề xuất = `{out.get('proposed_name')}`",
        f"- V1: compiled = {v1.get('compiled')}, FEPR = {v1.get('fepr')}",
        *extra, "",
        "<details><summary>Pseudocode model đã đọc</summary>", "", "```c",
        snippet((ARTIFACTS / cfg / f"{fn}.pseudocode.c").read_text()), "```", "</details>", "",
        "<details><summary>Mã nguồn gốc</summary>", "", "```c", snippet((SRC / f"{fn}.c").read_text()), "```",
        "</details>", "",
        "<details><summary>recovered_c của model</summary>", "", "```c", snippet(out.get("recovered_c", "")), "```",
        "</details>", "",
    ]


def claim_line(c: dict) -> str:
    v = c["verdict"]
    ev = v.get("counterexample") or v.get("detail") or v.get("fingerprint") or v.get("found") or v.get("reason")
    return f"- `{v['label']}` ({v.get('method')}) [{c['type']}] “{c['text']}” → {json.dumps(ev, ensure_ascii=False)}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    a = ap.parse_args()
    run_dir = DATA / "runs" / a.run
    res = json.loads((run_dir / "results.json").read_text(encoding="utf-8"))
    verdicts = {}
    for f in run_dir.glob("*/*.verdicts.json"):
        if ".s" in f.name:
            continue
        v = json.loads(f.read_text(encoding="utf-8"))
        verdicts[(v["config"], v["fn"])] = v

    md = [f"# Ứng viên case study — {a.run}", ""]
    md += ["## A. Gán nhầm thuật toán (V1b bác bỏ claim ALG)", ""]
    for (cfg, fn), v in sorted(verdicts.items()):
        bad = [c for c in v["claims"] if c["type"] == "ALG" and c["verdict"]["label"] == "contradicted"]
        if bad:
            md += item_block(fn, cfg, run_dir, [claim_line(c) for c in bad])
    for title, cell in (("B. Giải thích có claim sai nhưng mã khôi phục đúng (E2)", "contradicted/v1_pass"),
                        ("C. Giải thích sạch nhưng mã khôi phục sai (E2)", "clean/v1_fail")):
        md += [f"## {title}", ""]
        for key in res["e2_cells"].get(cell, [])[:8]:
            cfg, fn = key.split("/")
            v = verdicts[(cfg, fn)]
            lines = [claim_line(c) for c in v["claims"] if c["verdict"]["label"] in ("contradicted", "verified")]
            md += item_block(fn, cfg, run_dir, lines[:6])
    md += ["## D. Claim IO/SIDE bị vector bác bỏ", ""]
    for (cfg, fn), v in sorted(verdicts.items()):
        for c in v["claims"]:
            if c["type"] in ("IO", "SIDE") and c["verdict"]["label"] == "contradicted":
                md.append(f"- {cfg}/{fn}: {claim_line(c)[2:]}")
    (run_dir / "case_studies.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"[case] {run_dir / 'case_studies.md'}")


if __name__ == "__main__":
    main()
