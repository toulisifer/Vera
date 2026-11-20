# Hướng dẫn demo VeRA

Có ba cách, từ an toàn nhất đến ấn tượng nhất.

| Cách | Mở thế nào | Cần gì |
|---|---|---|
| Trang tĩnh | nhấp đúp `VeRA_demo.html` (dựng lại: `python -m vera.report.web`) | không cần gì, chạy offline |
| Trang web có “▶ Chạy trực tiếp” | `scripts/demo_web.sh` rồi mở http://localhost:8765 | Ollama + Docker + Ghidra |
| Terminal | `scripts/live_demo.sh` | Ollama + Docker + Ghidra |

## Thẻ “▶ Chạy trực tiếp”

1. Chọn cách tạo hàm: **Đổi một con số** (tạo hàm “bẫy” mới), **Hàm có sẵn** (hỏi AI lại từ đầu), hoặc **Tự viết code C**.
2. Bấm **▶ Chạy**. Thanh tiến độ đi qua 8 bước: biên dịch → 50 bộ dữ liệu → Ghidra → bằng chứng → AI → VeRA → Docker → dịch.
3. Khoảng 30–60 giây sau, kết quả hiện theo 5 bước (phím ← → để chuyển), có bản dịch tiếng Việt, ô “Vì sao” và chú thích code.

Mẹo: mời hội đồng đọc một số hex 8 chữ số rồi gõ vào ô “Đổi thành”.

## Ollama ở máy khác

Đặt `export VERA_OLLAMA=http://<địa-chỉ>:11434` trước khi chạy. Chỉ mở cổng 11434 cho mạng nội bộ, không mở ra Internet.

## Nếu có sự cố

| Hiện tượng | Xử lý |
|---|---|
| Ô trạng thái “✕ AI (Ollama)” | Mở Ollama, kiểm tra `VERA_OLLAMA`; chờ 10 giây, trạng thái tự cập nhật |
| “AI trả lời sai định dạng” | Bấm Chạy lại (AI đôi khi trả lời lỗi) |
| Trình duyệt không mở được trang | Kiểm tra `scripts/demo_web.sh` còn chạy; thử `http://localhost:8765` |
| Bất kỳ lỗi nào khi đang trình bày | Chuyển sang trang tĩnh `VeRA_demo.html` |
