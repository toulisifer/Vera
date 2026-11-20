# VeRA — hướng dẫn chạy (cho người nhận bản mã nguồn)

VeRA kiểm chứng lời giải thích của AI về một hàm nhị phân: tách câu trả lời thành từng nhận định nhỏ (claim) rồi kiểm
từng claim bằng bằng chứng lấy từ chính binary. Bản đồ toàn hệ thống: `docs/BOC_TACH_HE_THONG.md`.

Có 3 mức dùng, chọn mức phù hợp với máy của bạn.

## Mức 1 — Xem kết quả (không cài gì)

Mở file `data/demo/VeRA_demo.html` bằng trình duyệt: giới thiệu, 4 kịch bản demo, toàn bộ kết quả, tra cứu 60 bài.

## Mức 2 — Chạy lại toàn bộ kết quả (chỉ cần Docker)

Máy cần Docker (Linux) hoặc Docker Desktop đang chạy (Windows/macOS). Không cần GPU, AI, Ghidra, Python hay GCC.

Windows — mở PowerShell trong thư mục `vera`:
```powershell
powershell -ExecutionPolicy Bypass -File repro\run.ps1
```

Linux / macOS / WSL — mở Terminal trong thư mục `vera`:
```bash
repro/run.sh
```

Lần đầu tải khoảng 200 MB; chạy 20–40 phút (`repro/run.sh E1` chỉ chạy lượt chính, ~5 phút). Dòng cuối
**"TÁI LẬP ĐẠT"** nghĩa là mọi con số trùng với kết quả đã công bố.

## Mức 3 — Dùng hệ thống đầy đủ (gọi AI thật, demo chạy trực tiếp, thí nghiệm mới)

Cần Ubuntu 24.04 (máy thật, máy ảo hoặc WSL2) và một máy có Ollama (có GPU thì nhanh hơn).

1. Gói hệ thống:
   ```bash
   sudo apt install -y gcc binutils make python3-venv openjdk-21-jdk docker.io
   sudo usermod -aG docker $USER      # rồi đăng xuất, đăng nhập lại
   ```
2. Ghidra 12.1.4: tải bản PUBLIC từ trang phát hành chính thức của NSA trên GitHub (`NationalSecurityAgency/ghidra`),
   giải nén vào `~/tools/` (hoặc đặt biến `VERA_GHIDRA` trỏ tới thư mục Ghidra).
3. Ollama + model (trên máy có GPU, có thể là chính máy này):
   ```bash
   ollama pull qwen2.5-coder:7b
   ```
   Nếu Ollama ở máy khác: `export VERA_OLLAMA=http://<ip-máy-đó>:11434`.
4. Cài và dựng lại dataset:
   ```bash
   make setup && make         # tạo .venv, build 60 binary + 1.000 vector, chạy test
   make extract               # Ghidra → mã giả (chỉ cần nếu muốn sinh lại)
   ```
5. Dùng:

   | Việc | Lệnh |
   |---|---|
   | Demo web, thẻ "▶ Chạy trực tiếp" | `scripts/demo_web.sh` → `http://localhost:8765/#tructiep` |
   | Demo trên terminal | `scripts/live_demo.sh` |
   | Chạy một lượt thí nghiệm mới (vd. model khác) | `VERA_MODEL=<tên model> scripts/run_experiment.sh <tên-lượt>` |
   | Xem kết quả một lượt | `data/runs/<tên-lượt>/results.md` |

Tài liệu khác: `README.md` (tổng quan), `docs/demo.md` (demo), `repro/README.md` (tái lập, tiếng Anh),
`docs/conventions.md` (quy ước), `data/SUMMARY.md` (tổng hợp kết quả).
