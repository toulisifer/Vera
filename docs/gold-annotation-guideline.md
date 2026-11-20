# Hướng dẫn gán nhãn gold set (RQ4)

Bạn nhận một file `annotator_A.csv` (hoặc `_B`) gồm khoảng 120 câu nhận định ("claim") do một
mô hình AI viết ra khi đọc mã nhị phân của một hàm C. Việc của bạn: với **từng dòng**, đọc claim,
mở mã nguồn gốc của hàm (cột `source_file`, ví dụ `corpus/src/fn_05.c`) và mô tả tham chiếu
(cột `reference_description`), rồi điền **một** nhãn vào cột `label`.

**Làm độc lập.** Không bàn với người gán nhãn còn lại, không xem kết quả của hệ thống VeRA,
không chạy code của dự án. File được xáo thứ tự riêng cho mỗi người. Mất khoảng 2–3 giờ.

## Ba nhãn

| Nhãn | Khi nào dùng |
|---|---|
| `TRUE` | Claim **đúng** với mã nguồn gốc, xét trên mọi đầu vào hợp lệ theo chữ ký chung. |
| `FALSE` | Claim **sai**: có ít nhất một điều nó khẳng định mâu thuẫn với mã nguồn. |
| `UNCLEAR` | Claim quá mơ hồ để phán đúng/sai (ví dụ "hàm xử lý dữ liệu đầu vào"). |

Cột `note` để ghi lý do ngắn khi bạn phân vân — rất có ích cho bước phân xử.

## Quy tắc

1. **Phán theo mã nguồn gốc**, không theo pseudocode hay theo việc claim nghe có hợp lý không.
2. Claim có **nhiều ý**: chỉ `TRUE` khi *mọi* ý đều đúng; một ý sai → `FALSE`.
3. Claim nói về **hằng số**: đúng nếu hằng đó thật sự được dùng trong mã nguồn với vai trò claim nêu
   (hằng rác do macro `OBF_*` sinh ra cũng tính là "được dùng" ở bản obf — xem `corpus/include/vera.h`).
   Cấu hình (`config`) cho biết claim viết về bản plain/opt/obf.
4. Claim **gọi tên thuật toán** ("computes CRC-32"): chỉ `TRUE` nếu hàm đúng là thuật toán chuẩn đó
   (xem trường `algorithm_label` trong `corpus/manifest/fn_XX.json`). Hàm near-miss (fn_08–fn_14)
   **không phải** thuật toán chuẩn → claim gọi tên chuẩn là `FALSE`. Claim nói "một biến thể của X"
   hoặc "giống X" với hàm near-miss của X → `TRUE`.
5. Claim về **out / out_cap**: hàm hash/checksum (fn_01–04, 08–11, 16, 18) **không ghi** `out` và
   không đọc `out_cap`; claim nói chúng ghi kết quả vào `out` là `FALSE`.
6. Tên biến kiểu Ghidra (`param_1`, `uVar3`) trong claim là bình thường — hiểu `param_1` = `in`,
   `param_2` = `len`, `param_3` = `arg`, `param_4` = `out`, `param_5` = `out_cap`.
7. Không chắc sau 3 phút → chọn nhãn gần nhất, ghi `note`, đi tiếp.

## Ví dụ

| Hàm | Claim | Nhãn | Vì sao |
|---|---|---|---|
| fn_01 (CRC-32) | Uses the polynomial 0xEDB88320. | `TRUE` | Có trong mã nguồn. |
| fn_01 | Returns 0xFFFFFFFF when len is 0. | `FALSE` | len = 0 → h = 0xFFFFFFFF, trả h ^ 0xFFFFFFFF = 0. |
| fn_01 | Writes the checksum to the output buffer. | `FALSE` | Hàm không ghi `out`. |
| fn_08 (near-miss CRC) | Implements CRC-32. | `FALSE` | Đa thức khác chuẩn. |
| fn_08 | Computes a CRC-like checksum with a non-standard polynomial. | `TRUE` | Mô tả đúng biến thể. |
| fn_05 (TEA) | Returns VERA_ERR when len < 24 or out_cap < 8. | `TRUE` | Đúng điều kiện trong mã. |
| fn_05 | Implements MurmurHash3. | `FALSE` | Là TEA. |
| fn_18 | Iterates over the input string in a loop. | `TRUE` | Có vòng lặp qua `in`. |
| fn_15 | Processes the data efficiently. | `UNCLEAR` | Không kiểm được. |

## Sau khi xong

Lưu file CSV (giữ nguyên tên và các cột khác), gửi lại cho trưởng nhóm.

## Dành cho người phân xử

File của bạn (`PHAN_XU.csv`) chỉ chứa các dòng hai người gán nhãn **khác nhau** — thường vài dòng,
không phải 120. Với mỗi dòng: đọc claim, mở mã nguồn hàm đó, xem nhãn và ghi chú của A và B để tham
khảo, rồi **tự quyết** một nhãn theo đúng các quy tắc ở trên và điền vào cột `final_label`
(`TRUE` / `FALSE` / `UNCLEAR`), kèm một câu lý do ở cột `note`. Không điền ngẫu nhiên: nhãn phân xử
là đáp án cuối cùng dùng để chấm bộ kiểm chứng. Lưu dạng CSV UTF-8, giữ tên file.
