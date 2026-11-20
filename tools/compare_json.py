"""So hai file JSON kết quả (bản tái lập với bản đã commit), in một dòng kết luận.

    python tools/compare_json.py <nhãn> <mới.json> <cũ.json> [khóa ...]

Không có khóa → so toàn bộ, bỏ qua các khóa thời gian/môi trường (IGNORE). Thoát mã 1 nếu khác.
"""
import json
import sys

IGNORE = {"run_info", "generated", "started", "elapsed", "timestamp"}


def strip(x):
    if isinstance(x, dict):
        return {k: strip(v) for k, v in x.items() if k not in IGNORE}
    if isinstance(x, list):
        return [strip(v) for v in x]
    return x


def main() -> None:
    label, new_p, old_p, *keys = sys.argv[1:]
    new, old = (strip(json.load(open(p, encoding="utf-8"))) for p in (new_p, old_p))
    keys = keys or sorted(set(new) | set(old))
    diff = [k for k in keys
            if json.dumps(new.get(k), sort_keys=True, default=str) != json.dumps(old.get(k), sort_keys=True, default=str)]
    print(f"   {label}: " + ("giống hệt bản commit" if not diff else f"KHÁC ở {diff}"))
    sys.exit(1 if diff else 0)


if __name__ == "__main__":
    main()
