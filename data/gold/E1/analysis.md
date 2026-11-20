# Gold set E1 — phân tích (RQ4)

120 claim lấy mẫu phân tầng từ E1 (nhãn bộ kiểm chứng × cấu hình), 2 người gán nhãn độc lập,
1 người phân xử 4 bất đồng. Số liệu: `score.json` (`python -m vera.gold.score --run E1 --final`).

| Chỉ số | Giá trị [95% bootstrap] |
|---|---|
| Cohen's kappa (A vs B) | 0,929 — 4 bất đồng / 120 |
| Precision nhãn contradicted (người nói FALSE) | 88% [75%–100%] (22/25) |
| Recall nhãn contradicted (trong claim người nói FALSE) | 52% [37%–67%] |
| Precision nhãn supported + verified (người nói TRUE) | 83% [72%–93%] (40/48) |
| HR_strict thô | 6,4% |
| HR hiệu chỉnh theo độ chính xác bộ kiểm chứng | 26,2% [18,3%–34,7%] |

Bảng chéo (nhãn bộ kiểm chứng × nhãn người, sau phân xử):

| Bộ kiểm chứng \ Người | TRUE | FALSE | UNCLEAR |
|---|---|---|---|
| verified | 22 | 5 | 0 |
| supported | 18 | 3 | 0 |
| unsupported | 34 | 12 | 1 |
| contradicted | 3 | 22 | 0 |

## Ba nhóm lỗi của bộ kiểm chứng

1. **SIDE kiểm quá thô (5 claim verified nhưng sai).** Mẫu "writes … to out" chỉ kiểm hàm có ghi `out`
   hay không, không kiểm nội dung/khoảng: g016 "Writes the hash value to out[0..7]" (fn_05 ghi bản mã TEA),
   g013, g011, g019, g031.
2. **Hằng do compiler sinh (3 claim supported nhưng người chấm sai).** Hằng có thật trong binary nhưng
   không có trong mã nguồn: g027 `0x3910C8E0` = −0xC6EF3720 (tổng TEA sau 32 vòng, -O2 tính sẵn),
   g042 `0x290A3A20` (tương tự cho fn_12), g029 `0xFFFFFFFF` (fn_15). V3 đúng ở mức binary; hướng dẫn gán
   nhãn yêu cầu phán theo mã nguồn → định nghĩa "claim CONST đúng" cần nói rõ trong báo cáo.
3. **Trường `io` lệch câu chữ (3 claim contradicted nhưng người chấm đúng).** g110, g116 (câu "returns the
   length of the output" nhưng `io.returns = "len"`), g119 (câu "returns 8 when … successfully" nhưng
   `io.when = "always"`). Kiểm IO dựa vào trường cấu trúc model tự điền.

Claim unsupported mà người chấm FALSE (12): IO 4, CF 3, CONST 3, NAME 1, ALG 1 — nguồn chính của khoảng
cách giữa HR thô và HR hiệu chỉnh: phần lớn claim sai nằm ngoài vùng phủ của bộ kiểm chứng.

Không sửa bộ kiểm chứng theo các ca trên: gold set là tập đánh giá; sửa theo nó là học trên tập kiểm tra.

## Sửa bộ kiểm chứng sau khi chấm gold set

Hai lỗi phát hiện khi chuẩn bị demo, đã sửa và gán nhãn lại mọi lượt chạy. Precision/recall ở trên giữ
nguyên vì chúng tính trên nhãn tại thời điểm lấy mẫu (`key.json`); chỉ trọng số tầng của HR hiệu chỉnh
cập nhật theo nhãn mới.

1. V1b gộp "CRC-16/XMODEM" vào CRC-16/CCITT-FALSE (khác giá trị khởi tạo) → thêm oracle XMODEM và KERMIT.
2. V3 coi hằng hex thiếu tiền tố `0x` trong `asserted_values` (vd. `cbf29ce484222325`) là chuỗi → nay đọc là số.
