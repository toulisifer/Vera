"""Gọi Ollama với structured output, cache theo hash, kiểm schema và thử lại một lần."""
from __future__ import annotations

import hashlib
import json
import os
import time
import urllib.request

from vera.common import DATA
from vera.llm import prompt as P
from vera.llm.schema import SCHEMA, validate

OLLAMA_URL = os.environ.get("VERA_OLLAMA", "http://localhost:11434")
DEFAULT_MODEL = os.environ.get("VERA_MODEL", "qwen2.5-coder:7b")
CACHE = DATA / "cache" / "llm"
OFFLINE = os.environ.get("VERA_OFFLINE") == "1"  # phát lại từ cache, không gọi Ollama


def model_info(model: str) -> dict:
    """Tên, digest và mức quantization của model — ghi vào run.json để tái lập."""
    if OFFLINE:
        return {"model": model, "offline_replay": True}
    with urllib.request.urlopen(f"{OLLAMA_URL}/api/tags", timeout=30) as r:
        tags = json.load(r)["models"]
    m = next((t for t in tags if t["name"] == model), None)
    if m is None:
        raise SystemExit(f"Ollama không có model {model}")
    with urllib.request.urlopen(f"{OLLAMA_URL}/api/version", timeout=30) as r:
        version = json.load(r)["version"]
    return {"model": model, "digest": m["digest"], "details": m.get("details", {}), "ollama": version}


def _chat(model: str, system: str, user: str, options: dict, think: bool | None = None,
          use_cache: bool = True) -> dict:
    body = {"model": model, "stream": False, "format": SCHEMA, "options": options,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}
    if think is not None:  # chỉ model có chế độ suy nghĩ (vd. qwen3) mới nhận tham số này
        body["think"] = think
    key = hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()
    path = CACHE / f"{key}.json"
    if use_cache and path.exists():
        return {**json.loads(path.read_text(encoding="utf-8")), "cached": True}
    if OFFLINE:
        raise SystemExit(f"VERA_OFFLINE=1 nhưng cache thiếu {key} — lượt chạy không phát lại được")
    req = urllib.request.Request(f"{OLLAMA_URL}/api/chat", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=900) as r:
        resp = json.load(r)
    rec = {"key": key, "content": resp["message"]["content"], "seconds": round(time.time() - t0, 1),
           "thinking_chars": len(resp["message"].get("thinking") or ""),
           "eval_count": resp.get("eval_count"), "prompt_eval_count": resp.get("prompt_eval_count")}
    if use_cache:  # gọi trực tiếp (demo) không được ghi đè cache của các lượt thí nghiệm
        CACHE.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(rec, ensure_ascii=False) + "\n", encoding="utf-8")
    return {**rec, "cached": False}


def analyze(fn_id: str, pseudocode: str, backend: str, model: str = DEFAULT_MODEL,
            temperature: float = 0.0, sample: int = 0, think: bool | None = None,
            num_predict: int = 3072, num_ctx: int = 8192, use_cache: bool = True) -> dict:
    """Một lần phân tích. `sample` phân biệt các lần lặp (E4/E6) để không trúng cache của nhau."""
    system, user = P.build(fn_id, pseudocode, backend)
    # Với think=True, phần suy nghĩ cũng tiêu num_predict — cần ngân sách lớn hơn, nếu không câu trả lời rỗng.
    options = {"temperature": temperature, "seed": sample, "num_ctx": num_ctx, "num_predict": num_predict}
    attempts = []
    for attempt in range(2):  # một lần gọi + tối đa một lần thử lại
        u = user if attempt == 0 else (
            user + "\n\nYour previous answer was invalid: " + "; ".join(attempts[-1]["errors"])
            + ". Answer again with valid JSON following every rule.")
        rec = _chat(model, system, u, options, think, use_cache)
        try:
            doc = json.loads(rec["content"])
            errors = validate(doc, fn_id)
        except json.JSONDecodeError as e:
            doc, errors = None, [f"JSON lỗi: {e}"]
        attempts.append({"errors": errors, "seconds": rec["seconds"], "cached": rec["cached"],
                         "eval_count": rec["eval_count"], "cache_key": rec["key"]})
        if not errors:
            break
    return {"fn": fn_id, "prompt_version": P.PROMPT_VERSION, "model": model, "options": options, "think": think,
            "schema_valid": not attempts[-1]["errors"], "attempts": attempts, "output": doc}
