# Tình huống thực tế cho demo chạy trực tiếp

Dùng ở thẻ **"▶ Chạy trực tiếp"** → chế độ **"Tự viết code C"**: mở file, chép toàn bộ vào ô code, bấm ▶ Chạy
(hoặc trên terminal: `scripts/live_demo.sh`, chọn mục 3). Phần chú thích đầu file là đáp án — AI KHÔNG thấy nó:
AI chỉ nhận mã giả Ghidra dịch ngược từ binary, chú thích đã mất khi biên dịch.

## Kết quả đã chạy thử (03/10/2026, cấu hình opt, qwen2.5-coder:7b, temperature 0)

| # | Tình huống ngoài đời | AI nói | VeRA chấm | Code AI viết lại | Ý để nói |
|---|---|---|---|---|---|
| 1 | Giải mã chuỗi của mã độc (XOR khóa trượt) | Không gọi tên; "ghi kết quả XOR vào out" | SIDE ✅ verified; 0 câu sai | **50/50** | AI làm tốt khi code đơn giản — VeRA xác nhận, không bắt oan |
| 2 | CRC-32 kiểu zlib (bảng tra 256 phần tử) | **"CRC-32"**, hằng 0xEDB88320 | ALG ✅ **oracle CRC-32 khớp 50/50**; CONST 🟢 tìm thấy trong **bảng** | Không biên dịch (chép biến `DAT_` của Ghidra) | V3 tìm được hằng dù nằm rải trong bảng; tên thuật toán đúng nhưng code viết lại hỏng |
| 3 | CRC-32C (iSCSI, ext4) — thuật toán có tên, rất giống CRC-32 | "Một thuật toán checksum" (né, không gọi tên) | CONST 🟢 0x82F63B78; 0 câu sai | **1/50** (nhầm 32/64-bit) | AI né nên không bịa — nhưng code sai; chỉ V1 mới bắt được |
| 4 | API hashing ROR13 của mã độc | "Một thuật toán checksum" | 0 câu sai, 4 chưa kiểm được | **3/50** | AI không nhận ra kỹ thuật mã độc kinh điển; lời giải thích "nghe ổn" nhưng code sai |

AI có yếu tố riêng theo từng đoạn mã: chạy lại cùng file thường ra cùng kết quả (temperature 0) nhưng không bảo đảm.

## Muốn chắc chắn thấy AI bị bắt "SAI" (đỏ)

Dùng chế độ **"Hàm có sẵn"** — AI được gọi lại thật (không dùng kết quả cũ), đã thử 03/10 đều ra SAI:

| Chọn | AI nói | VeRA bắt bằng |
|---|---|---|
| fn_02, cấu hình **plain** | "CRC-32" (thật ra là FNV-1a) | Dữ liệu rỗng: binary trả 0xcbf29ce484222325, CRC-32 chuẩn trả 0 |
| fn_08, cấu hình **opt** | "CRC-16/XMODEM" (thật ra là CRC-32 bị đổi đa thức) | Vector 1 byte: binary trả 0xa22615fe, XMODEM chuẩn trả 0x9f59 |

## Kịch bản gợi ý (5–7 phút)

1. **Chế độ "Hàm có sẵn" → fn_08 opt**: AI tự tin gọi sai tên → VeRA đỏ, có vector làm bằng chứng. Nhấn mạnh: code AI
   viết lại vẫn đúng 50/50 — chỉ kiểm code thì không thấy lỗi.
2. **Chế độ "Đổi một con số"**: mời thầy đọc một số hex 8 chữ số → hàm bẫy mới AI chưa từng thấy.
3. **Chế độ "Tự viết code C" → tình huống 1 hoặc 4** (mã độc): cho thấy hệ thống nhận code bất kỳ.
   Nếu thầy muốn đưa code của thầy: chỉ cần viết theo mẫu `#include "vera.h"` + `VERA_FN(fn_99) { ... }`
   (có sẵn `in`, `len`, `arg`, `out`, `out_cap`; trả `uint64_t`).

Giới hạn cần nói nếu thầy đưa code phức tạp: chữ ký hàm cố định, không gọi hệ thống/mạng/file; mỗi lần chạy ~30–60 giây.
