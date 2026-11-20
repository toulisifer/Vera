# Kịch bản demo bằng terminal (không dùng trang web)

Khởi động hệ thống một lần, sau đó gõ lệnh ở dấu nhắc `vera>`. Mọi kết quả mẫu là output thật chạy trên máy ảo
(25–28/10/2026). Thời lượng 11–12 phút: bảng cả 20 hàm, chạy trực tiếp fn_01, fn_08, fn_09, fn_20 rồi hàm do hội đồng ra đề.

## Trước giờ bảo vệ

1. Bật máy ảo. Ollama trên Windows tự chạy (biểu tượng con lạc đà ở khay hệ thống).
2. Mở terminal Ubuntu, phóng chữ to (Ctrl + Shift + `+` vài lần).
3. Khởi động hệ thống một lần để nạp model AI (lần đầu sau khi bật máy ~30–50 giây), gõ `exit`.
   Lúc khởi động `vera.shell` tự nạp model và giữ trong GPU đến khi Ollama tắt.
4. (Tùy chọn) Mở Ghidra giao diện với `data/binaries/opt/fn_08.so`, mở hàm `fn_08` trong Decompiler.

## Khởi động hệ thống (trước hội đồng)

```bash
cd ~/vera && source .venv/bin/activate && PYTHONPATH=. python -m vera.shell
```
```
VeRA — verification of LLM explanations of binary functions
checking components:
  [ ok ] ollama   0.40.11  model qwen2.5-coder:7b  (http://localhost:11434)
  [ ok ] docker   29.1.3  sandbox image python:3.12-slim
  [ ok ] ghidra   ~/tools/ghidra_12.1.4_PUBLIC
  [ ok ] corpus   20 functions x 3 configs = 60 binaries, 1000 vectors
vera>
```
> Nói: "Hệ thống gồm bốn thành phần: AI chạy cục bộ, Docker để cách ly, Ghidra để dịch ngược, và bộ dữ liệu
> 20 hàm × 3 cấu hình, 1.000 vector thử."

Gõ `help` để xem danh sách lệnh.

## 1 — Bộ dữ liệu (30 giây)

```
vera> list
```
> Nói: "7 hàm kinh điển, 7 hàm near-miss — bản sao của 7 hàm kinh điển bị đổi một chi tiết, 6 hàm tự thiết kế."

## 1b — Kết quả cả 20 hàm × 3 cấu hình (1 phút)

```
vera> results
```
In bảng 20 dòng từ thí nghiệm E1 (đã lưu, không gọi AI nên ra ngay). Mỗi ô: `câu bị bác/tổng câu | vector code khớp`.
Dòng cuối: `tổng: 25/389 câu bị bác; code đúng 50/50: plain 9/20, opt 5/20, obf 0/20` — khớp báo cáo.
> Nói: "Đây là kết quả của toàn bộ 60 binary trong thí nghiệm chính. Dấu ! là ô có câu bị bác. Near-miss gần như hàng
> nào cũng có !, hàm tự thiết kế thì ít — AI hay sai khi hàm giống thuật toán nổi tiếng. Cột obf: code AI viết lại
> không ô nào đúng 50/50, đa số không biên dịch được. Giờ em chạy trực tiếp bốn hàm đại diện cho cả ba nhóm."

Xem chi tiết một hàm bất kỳ thầy chỉ: `results fn_13` (câu nào bị bác, vector nào làm bằng chứng).
Lưu ý: bảng là E1 (Ollama 0.34.3); chạy `analyze` hôm nay (Ollama 0.40.11) có thể khác ở vài ô, ví dụ fn_20 opt:
E1 code 15/50, hôm nay code lỗi biên dịch. Câu bị bác c4 của fn_20 thì giống nhau.

## 2 — Đối chứng: VeRA không bắt oan (45 giây)

```
vera> source fn_01
vera> analyze fn_01
```
```
[llm] 10.8 s  algorithm='Implements CRC-32.'
[verify] c5 ALG   VERIFIED     The function implements CRC-32.
          V1b: oracle CRC-32 khớp 50/50 vector
[v1] recovered C: 50/50 vectors match the binary (FEPR 1.0)
summary: 3 verified, 0 supported, 2 unsupported, 0 contradicted
```
> Nói: "Trước hết VeRA phải không bắt oan. fn_01 là CRC-32 chuẩn: AI nói CRC-32, VeRA chạy bản chuẩn, khớp 50/50 → xác nhận.
> Giờ em đổi đúng một con số."

## 2b — Một hàm bẫy (30 giây)

```
vera> diff fn_01 fn_08
```
Chỉ khác tên hàm và `0xEDB88320u` → `0xF7179BF5u`.
> Nói: "fn_01 là CRC-32 chuẩn, fn_08 chỉ đổi đa thức. Hai hàm cho kết quả khác hẳn nhau."

## 3 — Thứ người phân tích nhận được (45 giây)

```
vera> inspect fn_08
vera> pseudo fn_08
```
`inspect`: `ELF 64-bit … stripped`, chỉ còn ký hiệu `fn_08`. `pseudo`: mã giả Ghidra, thấy hằng `0xf7179bf5`.
(Hoặc chuyển sang cửa sổ Ghidra đã mở.)
> Nói: "Binary đã xóa tên, không có chữ CRC. Mã giả này là thứ duy nhất AI được xem."

## 4 — Hỏi AI và kiểm chứng (1 phút)

```
vera> analyze fn_08
```
```
[llm] 17.5 s  algorithm='Implements CRC-16/XMODEM.'  claims=4 (+1 vague dropped)
[verify] c1 IO    VERIFIED     Returns 0 when len == 0.
[verify] c3 SIDE  VERIFIED     Does not write to out.
[verify] c5 ALG   CONTRADICTED The function implements CRC-16/XMODEM.
          V1b: oracle CRC-16/XMODEM: v01 (len1) binary=0x00000000a22615fe oracle=0x0000000000009f59
$ docker run --rm -i --network none --read-only ... python:3.12-slim /w/runner /w/recovered.so fn_08 2
[v1] recovered C: 50/50 vectors match the binary (FEPR 1.0)
summary: 2 verified, 0 supported, 2 unsupported, 1 contradicted  |  total 18 s
```
> Nói: "AI nói CRC-16/XMODEM. VeRA chạy bản chuẩn trên 1 byte: binary ra 0xa22615fe, bản chuẩn ra 0x9f59 — câu này sai.
> Nhưng code AI viết lại đúng 50/50: chỉ kiểm code thì không thấy lời giải thích sai. Code AI chạy trong Docker không mạng."

Nếu bị hỏi vì sao c2 ("Returns 0xFFFF… when len != 0") chỉ là UNSUPPORTED dù sai: VeRA chỉ bác khi có bằng chứng kiểm
được bằng máy; câu không viết đúng dạng điều kiện kiểm tự động được nên bị bỏ sót. Precision bác bỏ 88%. Recall:
báo cáo ghi 52%, nhưng đó là số tính thẳng trên mẫu gold set lấy phân tầng (lấy hết 25 claim contradicted). Tính có
trọng số tầng — cùng cách đã dùng cho HR hiệu chỉnh 26,2% — recall chỉ ≈ 21,5% [15,7%–31,3%] (bootstrap 2.000 lần,
seed 7): VeRA bắt khoảng 1/5 số claim sai, không phải một nửa. Góp ý G1 (M1) chỉ ra; nhóm đã kiểm lại 30/10/2026.

## 4a0 — fn_02: FNV-1a chuẩn mà AI vẫn gọi là CRC-32 (1 phút)

```
vera> source fn_02
vera> analyze fn_02
```
Chạy thử 29/10/2026 hai lần: cả hai `algorithm='ALG: CRC-32'`, c6 ALG CONTRADICTED
(`V1b: oracle CRC-32: v00 (len0) binary=0xcbf29ce484222325 oracle=0x0000000000000000`). Phần còn lại lệch giữa hai lần:
lần 1 c2 IO CONTRADICTED và code 49/50, lần 2 c2 UNSUPPORTED và code 50/50.
> Nói: "fn_02 là FNV-1a 64-bit chuẩn, không đổi gì. Vậy mà AI nói CRC-32. Hằng 0xcbf29ce484222325 là offset basis
> nổi tiếng của FNV, AI đọc đúng hằng nhưng gán cho CRC. Trên input rỗng, binary trả chính hằng đó, CRC-32 trả 0 → bác."

## 4a — Hàm thứ ba: fn_09, AI gọi sai hẳn tên thuật toán (1 phút)

```
vera> diff fn_02 fn_09
```
Chỉ khác tên hàm và số nhân `0x00000100000001B3` → `0x00000100000001B5`.
> Nói: "fn_02 là băm FNV-1a 64-bit chuẩn. fn_09 chỉ đổi chữ số cuối của hằng nhân, 3 thành 5."

```
vera> analyze fn_09
```
```
[llm] 18.5 s  algorithm='Implements CRC-32.'  claims=5 (+1 vague dropped)
[verify] c1 CONST SUPPORTED    The initial value for the CRC-32 computation is 0xcbf29ce484222325.
          V3: found in binary: 0xcbf29ce484222325 (imm)
[verify] c3 IO    UNSUPPORTED  Returns 0xFFFFFFFFFFFFFFFF when the input length is zero.
[verify] c4 SIDE  VERIFIED     Does not write to out.
[verify] c6 ALG   CONTRADICTED The function implements CRC-32.
          V1b: oracle CRC-32: v00 (len0) binary=0xcbf29ce484222325 oracle=0x0000000000000000
[v1] recovered C: 49/50 vectors match the binary (FEPR 0.98)
          v00 (len0): expected 0xcbf29ce484222325  got 0xffffffffffffffff
summary: 1 verified, 1 supported, 3 unsupported, 1 contradicted  |  total 19 s
```
> Nói: "Lần này AI không chỉ nhầm biến thể mà gọi sai hẳn họ thuật toán: đây là băm FNV, AI nói CRC-32. AI còn đọc đúng
> hằng 0xcbf29ce484222325 nhưng gán sai vai trò: đó là offset basis của FNV, không phải giá trị khởi tạo CRC. Hằng có
> thật trong binary nên V3 chỉ nói SUPPORTED, tức 'có mặt', không phải 'đúng nghĩa'. V1b chạy CRC-32 chuẩn trên input
> rỗng: binary trả 0xcbf2…, CRC-32 trả 0 → bác. Code AI viết lại đúng 49/50, sai đúng vector rỗng, cũng là chỗ AI
> khai sai ở c3."

## 4c — Hàm tự thiết kế: fn_20, AI không thể nhớ đáp án (1 phút)

```
vera> source fn_20
vera> analyze fn_20
```
```
[llm] 24.0 s  algorithm='unknown'  claims=6 (+2 vague dropped)
[verify] c1 CONST SUPPORTED    The function uses the constant 0xffffffffffffffff.
[verify] c3 SIDE  VERIFIED     Writes to out[0..7] if param_2 >= 8.
          SIDE: hàm có ghi out trên vector hợp lệ
[verify] c4 SIDE  CONTRADICTED Does not write to out if param_2 < 8.
          SIDE: v01 (len1): hàm có ghi out
[v1] recovered C does not compile: recovered.c:14:14: error: ‘pbVar4’ undeclared (first use in this function); did you mean ‘pbVar3’?
summary: 1 verified, 1 supported, 3 unsupported, 1 contradicted  |  total 24 s
```
> Nói: "fn_20 do nhóm tự viết, không có trên mạng: hoán vị byte trong từng khối 8 byte theo khóa, phần đuôi dưới 8 byte
> chép nguyên. AI không nhận ra thuật toán và trung thực trả 'unknown'. Nhưng AI khẳng định input dưới 8 byte thì không
> ghi gì ra out. VeRA chạy vector v01 chỉ 1 byte: hàm có ghi out (chép nguyên byte 0x03) → bác. Code AI viết lại còn
> không biên dịch được: dùng biến pbVar4 không khai báo. Với hàm lạ, AI bỏ sót đúng nhánh phụ — phần đuôi."

Chạy thử 29/10/2026 ba lần liên tiếp đều ra c4 CONTRADICTED và lỗi biên dịch giống hệt (temperature 0).
Dự phòng nếu cần hàm tự thiết kế khác: `analyze fn_15` (nén run-length) — AI nói "so sánh hai chuỗi" (NAME, UNSUPPORTED
vì ngoài vùng phủ), code đúng 2/50.

Chạy thử 28/10/2026 hai lần liên tiếp đều ra `CRC-32` + CONTRADICTED + 49/50 (temperature 0).

## 4b — (Tùy chọn, 20 giây) bộ làm rối

```
vera> pseudo fn_01 obf
```
> Nói: "Cùng mã nguồn, bật -DVERA_OBF: mã giả từ 25 dòng thành 59 dòng — nhánh giả, code rác, vòng lặp giả; lõi
> 0xedb88320 bị vùi ở giữa."

## 5 — Hội đồng tự ra đề ⭐ (2 phút)

Mời hội đồng đọc một số hex 8 chữ số, ví dụ CAFEBABE:
```
vera> mutate fn_01 CAFEBABE
```
```
Biến thể tạo lúc demo: hằng 0xEDB88320 của fn_01 (CRC-32) được đổi thành 0xCAFEBABE.
-            OBF_GUARD(h, len + b, h = (h >> 1) ^ (0xEDB88320u & (0u - (h & 1u))));
+            OBF_GUARD(h, len + b, h = (h >> 1) ^ (0xCAFEBABEu & (0u - (h & 1u))));
$ gcc -std=c11 -fPIC -shared -Wall -Wextra -O2 ... fn_99.c
$ strip --strip-all .../fn_99.so
[vectors] 50 inputs (profile bytes); expected outputs taken by running the compiled function
$ analyzeHeadless '<tmp-project>' live -import .../fn_99.so ...
[ghidra] 25 lines of pseudocode (9.1 s)
[llm] 19.4 s  algorithm='unknown'  claims=5
[verify] c1 CONST SUPPORTED    The function uses the constant 0xcafebabe.
          V3: found in binary: 0xcafebabe (imm)
[verify] c4 SIDE  CONTRADICTED Writes the computed checksum to out[0].
          SIDE: v00 (): không vector hợp lệ nào ghi out
[v1] recovered C: 1/50 vectors match the binary (FEPR 0.02)
          v01 (len1): expected 0x0000000005ff138e  got 0xffffffff05ff138e
```
> Nói: "Hàm này vừa được tạo từ con số thầy đọc — AI chưa từng thấy. AI đọc đúng hằng mới (V3 tìm thấy trong lệnh máy),
> nhưng bịa rằng hàm ghi ra out — 50 lần chạy không lần nào ghi. Code AI viết lại chỉ đúng 1/50: nửa sau đúng, nửa trước
> toàn chữ f — AI nhầm số 32-bit với 64-bit."

Kết quả thật với DEADBEEF (27/10): `algorithm='unknown'`, c1 CONST SUPPORTED 0xdeadbeef, không câu nào CONTRADICTED,
`[v1] 1/50` (`expected 0x000000002dfa3e7c got 0xffffffff2dfa3e7c`).

AI có thể trả lời khác giữa các con số. Đọc kết quả theo ba khả năng:
- Có `CONTRADICTED` → "AI nói sai, bằng chứng ở dòng ngay dưới."
- `algorithm='unknown'` và `[v1]` thấp → "AI không bịa tên, nhưng code chỉ đúng x/50."
- Mọi thứ đúng → "VeRA xác nhận chứ không bắt oan."

## 6 — (Nếu còn thời gian) code kiểu mã độc

```
vera> check demo/tinh_huong/4_bam_api_hashing_malware.c
```
> Nói: "API hashing ROR13 — kỹ thuật mã độc giấu tên hàm Windows. Hệ thống nhận bất kỳ hàm C nào theo chữ ký chung."

Thoát: `exit`.

## Xử lý sự cố

| Hiện tượng | Xử lý |
|---|---|
| `[FAIL] ollama` khi khởi động | Mở Ollama trên Windows, gõ `status` |
| `[FAIL] docker` | Thoát, `sudo systemctl start docker`, khởi động lại |
| `answer failed the JSON schema` | Gõ lại lệnh (mũi tên ↑) |
| Lệnh chạy quá lâu | Ctrl + C dừng lệnh, vẫn ở dấu nhắc `vera>` |
| Mọi thứ hỏng | `cat` các file kết quả trong `data/live/cli-*/` của buổi tập |

Lệnh một lần không cần dấu nhắc vẫn dùng được: `python -m vera.cli fn_08`, `python -m vera.cli file.c`.
Phiên bản Ollama hiện tại có thể khác bản dùng cho thí nghiệm chính (0.34.3); kết quả lưu trữ của E1–E6 không đổi.
