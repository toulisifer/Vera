"""Máy chủ web cho demo: trang VeRA + thẻ "Chạy trực tiếp" chạy thật toàn bộ pipeline.

    python -m vera.webapp [--port 8765]        # rồi mở http://localhost:8765

Chạy trên máy ảo. AI gọi qua Ollama (VERA_OLLAMA; mặc định localhost:11434). Chỉ chạy một lượt một lúc; tiến độ trả qua /api/job (trang tự hỏi mỗi giây).

API:
  GET  /                      trang demo (dữ liệu E1 + thẻ Chạy trực tiếp)
  GET  /api/status            Ollama/Docker/Ghidra có sẵn không
  GET  /api/constants?fn=     các hằng hex của một hàm (hằng đặc trưng đứng đầu)
  GET  /api/example           mã C mẫu cho chế độ tự viết
  GET  /api/examples          các tình huống thực tế (demo/tinh_huong/*.c)
  POST /api/run               {mode: mutate|fn|code, fn, const, to, code, config} → {job}
  GET  /api/job?id=           {steps: [...], done, error, item}
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import threading
import time
import traceback
import urllib.request
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from vera import live
from vera.common import ARTIFACTS, BUILD, BUILD_CONFIGS, DATA, FN_IDS, ROOT, load_manifest, load_vectors
from vera.corpus.build import build_runner
from vera.extract.evidence import extract
from vera.llm import client
from vera.llm.schema import filter_claims
from vera.report import web
from vera.verify.label import label_item
from vera.verify.v1 import verify
from vera.verify.v3 import Evidence

STEPS = [("build", "Biên dịch hàm thành mã máy"), ("vectors", "Sinh 50 bộ dữ liệu và đáp án"),
         ("ghidra", "Ghidra dịch ngược"), ("evidence", "Trích bằng chứng từ binary"),
         ("ai", "AI phân tích"), ("label", "VeRA chấm từng câu"), ("v1", "Chạy code AI viết lại trong Docker"),
         ("translate", "Dịch câu của AI sang tiếng Việt")]
JOBS: dict[str, dict] = {}
LOCK = threading.Lock()


def pick_ollama() -> str:
    for url in [os.environ.get("VERA_OLLAMA"), "http://localhost:11434"]:
        if not url:
            continue
        try:
            with urllib.request.urlopen(f"{url}/api/version", timeout=3):
                return url
        except OSError:
            pass
    return os.environ.get("VERA_OLLAMA") or "http://localhost:11434"


def examples() -> list[dict]:
    """[{title, code}] — hàm mẫu + các tình huống thực tế; tiêu đề lấy từ dòng chú thích đầu file."""
    out = []
    for f in [ROOT / "demo" / "example_fn.c", *sorted((ROOT / "demo" / "tinh_huong").glob("*.c"))]:
        code = f.read_text(encoding="utf-8")
        m = re.search(r"/\*\s*(.+)", code)
        out.append({"title": (m.group(1) if m else f.stem).rstrip(". "), "code": code})
    return out


def status() -> dict:
    client.OLLAMA_URL = pick_ollama()
    try:
        with urllib.request.urlopen(f"{client.OLLAMA_URL}/api/version", timeout=3) as r:
            ollama = json.load(r).get("version")
    except OSError:
        ollama = None
    docker = subprocess.run(["docker", "info"], capture_output=True).returncode == 0
    try:
        ghidra = live.ghidra_home().exists()
    except SystemExit:
        ghidra = False
    return {"ollama": ollama, "ollamaUrl": client.OLLAMA_URL, "docker": docker, "ghidra": ghidra,
            "model": client.DEFAULT_MODEL}


# ------------------------------------------------------------------ một lượt chạy
def run_job(job: dict, p: dict) -> None:
    steps = {k: job["steps"][i] for i, (k, _) in enumerate(STEPS)}

    def go(key, fn, *a):
        s = steps[key]
        s.update(state="run", t0=time.time())
        try:
            r = fn(*a)
        except SystemExit as e:  # các hàm của live.py báo lỗi bằng sys.exit
            raise RuntimeError(str(e.code)) from None
        s.update(state="done", sec=round(time.time() - s["t0"], 1))
        return r

    def skip(key, why):
        steps[key].update(state="skip", note=why)

    try:
        cfg = p.get("config", "opt")
        if cfg not in BUILD_CONFIGS:
            raise RuntimeError("Cấu hình phải là plain, opt hoặc obf")
        if not (BUILD / "runner").exists():
            build_runner()
        work = DATA / "live" / time.strftime("%Y%m%d-%H%M%S")
        work.mkdir(parents=True, exist_ok=True)
        mode, changed = p.get("mode"), None
        if mode == "fn":
            fn = p.get("fn")
            if fn not in FN_IDS:
                raise RuntimeError(f"Không có hàm {fn}")
            fn_id, pseudo, vectors, ev = fn, (ARTIFACTS / cfg / f"{fn}.pseudocode.c").read_text(), load_vectors(fn), None
            for k in ("build", "vectors", "ghidra", "evidence"):
                skip(k, "dùng binary có sẵn của corpus")
            truth = web.truth_of(fn)
            job["title"] = f"{fn} có sẵn · {cfg} · gọi AI trực tiếp"
        else:
            if mode == "mutate":
                base = p.get("fn") or "fn_01"
                if base not in FN_IDS:
                    raise RuntimeError(f"Không có hàm {base}")
                to = live.normalize_hex(p.get("to")) if p.get("to") else None
                src, note = live.mutate(base, p.get("const") or None, to)
                changed = re.search(r"được đổi thành (0x[0-9A-F]+)", note).group(1)
                m = load_manifest(base)
                profile = m["input_profile"]
                truth = {"group": "near-miss tạo lúc demo", "algLabel": f"biến thể của {m['algorithm_label']}",
                         "diff": note, "desc": m["description"], "writes_out": m["io_semantics"]["writes_out"],
                         "highlight": [changed], "note": "con số vừa đổi"}
                job["title"] = note
            elif mode == "code":
                src = p.get("code") or ""
                if "VERA_FN(" not in src:
                    raise RuntimeError('Mã phải có #include "vera.h" và hàm VERA_FN(fn_99)')
                profile = "bytes"
                truth = {"group": "tự viết lúc demo", "algLabel": "hàm tự viết", "diff": None,
                         "desc": "Hàm C do người dùng nhập trực tiếp trên trang demo.", "writes_out": None,
                         "highlight": [], "note": ""}
                job["title"] = "Hàm C tự viết"
            else:
                raise RuntimeError("Chế độ không hợp lệ")
            fn_id = live.LIVE_FN
            so = go("build", live.build, src, cfg, work)
            vectors = go("vectors", live.ground_truth_vectors, so, profile)
            pseudo = go("ghidra", live.decompile, so)
            ev = go("evidence", lambda: Evidence(extract(so)))
            truth["src"] = re.sub(r"VERA_FN\(\s*fn_\d+\s*\)", f"VERA_FN({live.LIVE_FN})", src)

        def ai():
            for attempt in range(3):
                try:
                    return client.analyze(fn_id, pseudo, "ghidra", use_cache=False)
                except OSError:
                    if attempt == 2:
                        raise RuntimeError(f"Không gọi được Ollama ở {client.OLLAMA_URL}") from None
                    time.sleep(5)
        res = go("ai", ai)
        res["config"] = cfg
        if not res["schema_valid"]:
            raise RuntimeError("AI trả lời sai định dạng sau 2 lần thử — bấm chạy lại.")
        kept, _ = filter_claims(res["output"]["claims"])
        res["claims"] = kept
        verdicts = go("label", label_item, {**res, "fn": fn_id}, ev, vectors)
        v1raw = go("v1", verify, {**res, "fn": fn_id}, vectors)
        item = go("translate", web.build_item, fn_id, cfg, pseudo, res, verdicts["claims"], v1raw, truth,
                  changed, None, True)
        item["aiSeconds"] = res["attempts"][-1]["seconds"]
        (work / "item.json").write_text(json.dumps(item, ensure_ascii=False, indent=1))
        job["item"] = item
    except (Exception, SystemExit) as e:  # noqa: BLE001 — mọi lỗi phải hiện lên trang, không làm sập máy chủ
        for s in job["steps"]:
            if s["state"] == "run":
                s["state"] = "fail"
        job["error"] = str(getattr(e, "code", None) or e) or e.__class__.__name__
        job["trace"] = traceback.format_exc()[-1500:]
    finally:
        job["done"] = True
        job["total"] = round(time.time() - job["t0"], 1)


# ------------------------------------------------------------------ HTTP
class Handler(BaseHTTPRequestHandler):
    page: bytes = b""

    def log_message(self, fmt, *args):  # yên lặng, chỉ in lỗi
        pass

    def send(self, code: int, body, ctype="application/json; charset=utf-8"):
        data = body if isinstance(body, bytes) else json.dumps(body, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        u = urlparse(self.path)
        q = parse_qs(u.query)
        if u.path in ("/", "/index.html"):
            return self.send(200, self.page, "text/html; charset=utf-8")
        if u.path == "/api/status":
            return self.send(200, status())
        if u.path == "/api/constants":
            fn = (q.get("fn") or ["fn_01"])[0]
            return self.send(200, live.constants_of(fn) if fn in FN_IDS else [])
        if u.path == "/api/example":
            return self.send(200, {"code": (ROOT / "demo" / "example_fn.c").read_text()})
        if u.path == "/api/examples":
            return self.send(200, examples())
        if u.path == "/api/job":
            j = JOBS.get((q.get("id") or [""])[0])
            return self.send(200 if j else 404, j or {"error": "không có lượt chạy này"})
        self.send(404, {"error": "không có"})

    def do_POST(self):
        if urlparse(self.path).path != "/api/run":
            return self.send(404, {"error": "không có"})
        try:
            p = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0)) or 0) or b"{}")
        except ValueError:
            return self.send(400, {"error": "dữ liệu gửi lên không hợp lệ"})
        with LOCK:
            if any(not j["done"] for j in JOBS.values()):
                return self.send(409, {"error": "Đang có một lượt chạy, chờ xong rồi chạy tiếp."})
            client.OLLAMA_URL = pick_ollama()
            jid = uuid.uuid4().hex[:8]
            JOBS[jid] = {"id": jid, "t0": time.time(), "done": False, "error": None, "item": None, "title": "",
                         "steps": [{"key": k, "label": lab, "state": "wait"} for k, lab in STEPS]}
        threading.Thread(target=run_job, args=(JOBS[jid], p), daemon=True).start()
        self.send(200, {"job": jid})


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--host", default="0.0.0.0")
    a = ap.parse_args()
    Handler.page = web.render(live=True).encode()
    st = status()
    print(f"VeRA demo: http://localhost:{a.port}  (Ollama: {st['ollama'] or 'KHÔNG KẾT NỐI'} ở {st['ollamaUrl']}, "
          f"Docker: {'có' if st['docker'] else 'KHÔNG'}, Ghidra: {'có' if st['ghidra'] else 'KHÔNG'})", flush=True)
    print(f"Đang chạy. Mở Firefox: http://localhost:{a.port}/#tructiep — GIỮ cửa sổ này mở; Ctrl+C để dừng.", flush=True)
    try:
        ThreadingHTTPServer((a.host, a.port), Handler).serve_forever()
    except KeyboardInterrupt:
        print("\nĐã dừng demo VeRA.")


if __name__ == "__main__":
    main()
