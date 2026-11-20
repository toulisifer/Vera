"""Đọc shared object của corpus: byte mã của fn_XX, các section dữ liệu, bảng import."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from elftools.elf.elffile import ELFFile

DATA_SECTIONS = (".rodata", ".data", ".data.rel.ro")


@dataclass
class Section:
    name: str
    addr: int
    data: bytes


@dataclass
class SharedObject:
    fn_name: str
    fn_addr: int
    code: bytes
    sections: list[Section]
    imports: list[str]

    def section_of(self, addr: int) -> str | None:
        for s in self.sections:
            if s.addr <= addr < s.addr + len(s.data):
                return s.name
        return None


def load(so: Path) -> SharedObject:
    with open(so, "rb") as fh:
        elf = ELFFile(fh)
        dynsym = elf.get_section_by_name(".dynsym")
        fn = next(s for s in dynsym.iter_symbols() if s.name.startswith("fn_") and s["st_shndx"] != "SHN_UNDEF")
        addr, size = fn["st_value"], fn["st_size"]
        code = b""
        for seg in elf.iter_segments():
            if seg["p_type"] == "PT_LOAD" and seg["p_vaddr"] <= addr < seg["p_vaddr"] + seg["p_filesz"]:
                fh.seek(addr - seg["p_vaddr"] + seg["p_offset"])
                code = fh.read(size)
        sections = []
        for name in DATA_SECTIONS:
            sec = elf.get_section_by_name(name)
            if sec is not None and sec["sh_type"] != "SHT_NOBITS":
                sections.append(Section(name, sec["sh_addr"], sec.data()))
        imports = sorted({s.name for s in dynsym.iter_symbols()
                          if s["st_shndx"] == "SHN_UNDEF" and s.name})
    return SharedObject(fn.name, addr, code, sections, imports)
