"""Trích bằng chứng cho V3 trực tiếp từ binary (không qua decompiler).

    python -m vera.extract.evidence

Ghi data/artifacts/<config>/fn_XX.evidence.json gồm:
  immediates   mọi toán hạng immediate trong fn_XX (giá trị không dấu theo kích thước toán hạng)
  displacements displacement khác 0 của toán hạng bộ nhớ (không tính RIP-relative)
  data_refs    địa chỉ đích của tham chiếu RIP-relative và section chứa nó (bảng hằng)
  sections     nội dung .rodata / .data dạng hex (V3 tìm hằng nằm trong bảng)
  strings      chuỗi in được ≥ 4 ký tự trong các section dữ liệu
  imports      symbol import (UND) của shared object

Evidence lấy từ binary để lỗi của decompiler không trở thành "bằng chứng".
"""
from __future__ import annotations

import json
import re

from capstone import CS_ARCH_X86, CS_MODE_64, Cs
from capstone.x86 import X86_OP_IMM, X86_OP_MEM, X86_REG_RIP

from vera.common import ARTIFACTS, CONFIGS, FN_IDS, so_path
from vera.elfutil import load

STRING_RE = re.compile(rb"[\x20-\x7e]{4,}")


def extract(so) -> dict:
    obj = load(so)
    md = Cs(CS_ARCH_X86, CS_MODE_64)
    md.detail = True
    imms, disps, refs = [], [], []
    n_insn = 0
    for ins in md.disasm(obj.code, obj.fn_addr):
        n_insn += 1
        for op in ins.operands:
            if op.type == X86_OP_IMM:
                bits = op.size * 8 or 64
                imms.append({"addr": ins.address, "insn": f"{ins.mnemonic} {ins.op_str}",
                             "value": op.imm & ((1 << bits) - 1), "size": op.size})
            elif op.type == X86_OP_MEM:
                if op.mem.base == X86_REG_RIP:
                    target = ins.address + ins.size + op.mem.disp
                    refs.append({"addr": ins.address, "target": target, "section": obj.section_of(target)})
                elif op.mem.disp:
                    disps.append({"addr": ins.address, "value": op.mem.disp & 0xFFFFFFFFFFFFFFFF})
    strings = []
    for s in obj.sections:
        for m in STRING_RE.finditer(s.data):
            strings.append({"section": s.name, "addr": s.addr + m.start(), "text": m.group().decode()})
    return {
        "backend": "capstone+pyelftools",
        "function": obj.fn_name,
        "n_instructions": n_insn,
        "immediates": imms,
        "displacements": disps,
        "data_refs": refs,
        "sections": [{"name": s.name, "addr": s.addr, "hex": s.data.hex()} for s in obj.sections],
        "strings": strings,
        "imports": obj.imports,
    }


def main() -> None:
    for cfg in CONFIGS:
        (ARTIFACTS / cfg).mkdir(parents=True, exist_ok=True)
        for fn_id in FN_IDS:
            ev = extract(so_path(fn_id, cfg))
            (ARTIFACTS / cfg / f"{fn_id}.evidence.json").write_text(json.dumps(ev, indent=1) + "\n", encoding="utf-8")
        print(f"[evidence] {cfg}: {len(FN_IDS)} file")


if __name__ == "__main__":
    main()
