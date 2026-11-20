# Bóc tách hệ thống VeRA — có những gì bên trong

Tài liệu tra cứu cho cả nhóm: mỗi thành phần của hệ thống là gì, có bao nhiêu, nằm ở đâu.
Mọi con số lấy từ dữ liệu đã commit (02/10/2026); nguồn chi tiết ghi ở cuối mỗi mục.

## 0. Toàn cảnh bằng con số

| Thành phần | Số lượng |
|---|---|
| Hàm C nhóm tự viết (đề thi) | 20 (7 kinh điển, 7 near-miss, 6 tự thiết kế) |
| Cấu hình biên dịch | 3 (plain, opt, obf) |
| Bài phân tích (item) = hàm × cấu hình | 60 |
| Bộ dữ liệu thử (vector I/O) | 50 mỗi hàm → 1.000 |
| Loại claim | 6 (ALG, CONST, IO, CF, SIDE, NAME) |
| Nhãn | 4 (verified, supported, unsupported, contradicted) |
| Bộ kiểm chứng | V3, V1b, IO, SIDE, V1 (+ self-test cho V3) |
| Cài đặt thuật toán chuẩn (oracle V1b) | 20 |
| Lượt chạy thí nghiệm | 11 (5 lượt E0 thử + E1, E1_p2, E1_qwen3, E1_llm4decompile, E4, E6) |
| Claim chấm tay (gold set) | 120 |
| Test tự động | 45 |
| Câu trả lời AI lưu trong cache | 481 |

---

## 1. Hai mươi hàm (đề thi) — `corpus/src/fn_XX.c`, đáp án ở `corpus/manifest/fn_XX.json`

Mọi hàm có chung một chữ ký, tên trung tính để không lộ đáp án:

```c
uint64_t fn_XX(const uint8_t *in, size_t len, uint64_t arg, uint8_t *out, size_t out_cap);
```
`in`/`len`: dữ liệu vào · `arg`: tham số (khóa, seed) · `out`/`out_cap`: vùng ghi kết quả · trả về: checksum, hash, độ dài hoặc mã lỗi `VERA_ERR`.

### 1.1. Nhóm kinh điển (7 hàm) — đo khả năng nhận diện đúng

| Hàm | Thuật toán | Dùng để làm gì ngoài đời | Hằng số đặc trưng ("dấu vân tay") | Ghi `out`? |
|---|---|---|---|---|
| fn_01 | CRC-32 | Mã kiểm tra lỗi trong ZIP, PNG, Ethernet | `0xEDB88320`, `0xFFFFFFFF` | Không |
| fn_02 | FNV-1a 64-bit | Hàm băm nhanh cho bảng băm | `0xCBF29CE484222325`, `0x100000001B3` | Không |
| fn_03 | Adler-32 | Mã kiểm tra trong zlib | `0xFFF1` (65521) | Không |
| fn_04 | djb2 | Băm chuỗi kinh điển | `0x1505` (5381) | Không |
| fn_05 | TEA (1 khối) | Mã hóa khối nhỏ gọn, hay gặp trong mã độc | `0x9E3779B9`, `0xC6EF3720` | Có (bản mã) |
| fn_06 | RC4 keystream XOR | Mã hóa dòng, rất hay gặp trong mã độc | `0x100`, `0xFF` | Có |
| fn_07 | Base64 encode | Mã hóa nhị phân thành chữ | bảng `A–Z a–z 0–9 + /` | Có |

### 1.2. Nhóm near-miss (7 hàm) — "đề bẫy": giống hệt bản kinh điển, bị sửa đúng một chỗ

| Hàm | Bẫy của | Chỗ bị sửa |
|---|---|---|
| fn_08 | fn_01 CRC-32 | Đa thức `0xF7179BF5` thay cho `0xEDB88320` |
| fn_09 | fn_02 FNV-1a | Số nguyên tố `0x100000001B5` thay cho `0x100000001B3` |
| fn_10 | fn_03 Adler-32 | Modulus 65519 thay cho 65521 |
| fn_11 | fn_04 djb2 | Khởi tạo 7477 thay cho 5381, hệ số 41 thay cho 33 |
| fn_12 | fn_05 TEA | Delta `0x8EB7AE2F` thay cho `0x9E3779B9` |
| fn_13 | fn_06 RC4 | Bước trộn khóa (KSA) thêm `XOR i` |
| fn_14 | fn_07 Base64 | Bảng chữ cái bị xáo trộn (kỹ thuật mã độc thật hay dùng) |

Mỗi hằng mới đã được tra để không trùng một thuật toán có tên khác (ví dụ không dùng `0x82F63B78` vì đó là CRC-32C).

### 1.3. Nhóm tự thiết kế (6 hàm) — AI chưa từng thấy, gần như không có hằng để nhận diện

| Hàm | Làm gì |
|---|---|
| fn_15 | Nén run-length: dãy byte giống nhau → cặp (độ dài, giá trị) |
| fn_16 | Checksum cuộn tự chế: xoay 7 bit, cộng byte × 0x9D, trộn cuối bằng `0x3B9D` |
| fn_17 | Parser định dạng TLV: duyệt bản ghi [type][độ dài][giá trị], báo lỗi nếu bị cắt |
| fn_18 | Máy trạng thái kiểm tra ngoặc `() [] {}` cân bằng, bỏ qua nội dung trong chuỗi |
| fn_19 | XOR xoay theo vị trí: mỗi byte XOR với byte khóa đã xoay và với vị trí |
| fn_20 | Hoán vị byte theo khóa: xáo 8 byte mỗi khối theo hoán vị sinh từ `arg` |

---

## 2. Ba cấu hình biên dịch — `vera/corpus/build.py`, GCC 13.3.0

| Cấu hình | Cờ | Ý nghĩa | Ví von |
|---|---|---|---|
| plain | `-O0 -g` | Không tối ưu, giữ tên biến và kiểu | Đề dễ |
| opt | `-O2` + `strip` | Tối ưu mạnh, xóa sạch tên | Phần mềm thật |
| obf | `-O2 -DVERA_OBF` + `strip` | Như opt, thêm nhánh giả và mã rác | Mã độc tự che giấu |

Làm rối (`corpus/include/vera.h`): `OBF_GUARD` (opaque predicate — điều kiện luôn đúng nhưng compiler không chứng minh
được vì đọc qua biến `volatile`), `OBF_JUNK` (phép tính rác), `OBF_SPIN`. Kiểm tra bắt buộc: bản obf phải có ≥ 30% lệnh
rẽ nhánh nhiều hơn bản opt — hàm thấp nhất đạt +38% (`data/cfg_stats.json`, `data/corpus_report.md`).

---

## 3. Năm mươi bộ dữ liệu thử mỗi hàm — `data/vectors/fn_XX.json`

Output kỳ vọng sinh bằng cách chạy chính hàm gốc. Mỗi hàm có đủ các trường hợp biên thầy yêu cầu:

| Nhãn vector | Kiểm cái gì |
|---|---|
| `len0`, `len1`, `len3`, `len8`, `len23`, `len24`, `len64` | Dữ liệu rỗng, 1 byte, đúng/lệch biên khối 8 và 64 |
| `all00`, `allff` | Toàn byte 0x00, toàn byte 0xFF |
| `cap0`, `cap_half`, `cap7_len24` | Vùng ghi `out` thiếu chỗ |
| `arg0`, `argmax` | Tham số bằng 0 và lớn nhất |
| `rand14` … `rand49` | Dữ liệu ngẫu nhiên (seed cố định) |
| `run_255`, `tlv_hdr_cut`, `nest_65`, `escaped_quote`… | Biên riêng của từng hàm tự thiết kế |

---

## 4. Năm tầng xử lý

| Tầng | Làm gì | Công cụ | Code |
|---|---|---|---|
| L0 — Ra đề | Biên dịch 60 binary, sinh 1.000 vector, kiểm làm rối | GCC 13.3.0 | `vera/corpus/` |
| L1 — Dịch ngược | Mã giả C cho AI đọc; bằng chứng lấy thẳng từ binary (số trong lệnh máy, bảng `.rodata`, chuỗi, import) | Ghidra 12.1.4 headless, capstone, pyelftools | `vera/extract/`, `harness/ghidra/` |
| L2 — AI làm bài | Gửi mã giả, nhận JSON đúng mẫu, sai mẫu thì hỏi lại 1 lần, lưu cache | Ollama, qwen2.5-coder:7b (Q4_K_M), prompt p3 | `vera/llm/` |
| L3 — Chấm | Gán nhãn từng claim bằng V3/V1b/IO/SIDE; chạy code AI (V1) | Docker | `vera/verify/` |
| L4 — Tổng kết | Tỉ lệ, khoảng tin cậy, kiểm định, bảng, biểu đồ | Python | `vera/report/` |

Máy: VM Ubuntu 24.04.3 (OpenJDK 21, Docker); AI chạy trên Windows (RTX 4060 8 GB).

---

## 5. Câu trả lời của AI — `vera/llm/schema.py`, `vera/llm/prompt.py`

AI phải trả JSON gồm: `summary` (tóm tắt), `proposed_name` (tên đề xuất), `algorithm` (tên thuật toán hoặc "unknown"),
`claims` (danh sách nhận định nhỏ, mỗi cái có loại, câu chữ, con số, độ tự tin, trường `io` có cấu trúc), `recovered_c`
(code C viết lại). Prompt p3 có 7 quy tắc claim, **mẫu câu** cho từng loại claim (thay cho ví dụ claim tốt cụ thể) và
3 ví dụ claim xấu. Lý do: bản p2 có ví dụ cụ thể thì AI chép nguyên ví dụ vào câu trả lời — giữ lại làm thí nghiệm
E1_p2. Đây là chỗ lệch có chủ đích so với hướng dẫn ("3 ví dụ tốt, 3 ví dụ xấu"), cần ghi trong báo cáo.
Bộ lọc hậu xử lý loại claim mơ hồ và ghi số bị loại.

### Sáu loại claim

| Loại | Nói về | Ví dụ | Ai kiểm |
|---|---|---|---|
| ALG | Thuật toán | "Hàm tính CRC-32" | V1b (+ V3 dấu vân tay) |
| CONST | Con số, chuỗi | "Dùng hằng 0x9E3779B9" | V3 |
| IO | Vào/ra | "Trả 0 khi len = 0" | Chạy vector (DSL) |
| SIDE | Tác dụng phụ | "Không ghi vào out" | Chạy vector, so bộ nhớ |
| CF | Luồng điều khiển | "Lặp qua từng byte" | Chưa kiểm tự động |
| NAME | Tên, mục đích | "Đây là hàm checksum" | Chưa kiểm tự động |

## 6. Bốn nhãn

| Nhãn | Nghĩa | Tính là "bịa"? |
|---|---|---|
| verified | Đã chứng minh đúng bằng cách chạy thật | Không |
| supported | Có bằng chứng tĩnh ủng hộ (tìm thấy con số…) | Không |
| unsupported | Không đủ bằng chứng, hoặc loại claim chưa kiểm được | Không — chỉ là "không kiểm chứng được" |
| contradicted | Có bằng chứng dương tính là sai (kèm vector làm chứng) | **Có** — chỉ nhãn này |

Không tìm thấy bằng chứng **không bao giờ** đủ để gán contradicted.

---

## 7. Các bộ kiểm chứng — `vera/verify/`

### V3 — tìm con số trong binary (`v3.py`, `fingerprints.py`, `vera/constants.py`)
- Chỉ lấy số hex ≥ 3 chữ số hoặc thập phân ≥ 4 chữ số (bỏ "CRC-32", "32-bit"…).
- Tìm cả các dạng compiler biến đổi: nguyên dạng, đảo byte (little-endian), số âm/bù hai, mở rộng dấu 64-bit, tách
  đôi 16-bit cao/thấp, nằm trong bảng `.rodata`, dạng dịch bit, số nhân "magic" của phép chia, nằm trong chuỗi.
- ALG khớp chặt hơn: phải có đủ bộ hằng đặc trưng của thuật toán.

### V1b — chạy thuật toán chuẩn để so (`vera/oracles.py`), 20 oracle
| Họ | Oracle |
|---|---|
| CRC (7) | CRC-32, CRC-32/BZIP2, CRC-32C, CRC-16/ARC, CRC-16/CCITT-FALSE, CRC-16/XMODEM, CRC-16/KERMIT |
| FNV (3) | FNV-1a-32, FNV-1a-64, FNV-1-64 |
| Checksum (2) | Adler-32, Fletcher-32 |
| Băm chuỗi (3) | djb2, djb2-xor, sdbm |
| Mã hóa (3) | TEA, XTEA, RC4 |
| Mã hóa ký tự (2) | Base64, Base64url |

AI nói "đây là X" → chạy oracle X trên 50 vector, so với binary: khớp hết → verified; lệch → contradicted (kèm vector);
X không có trong thư viện → giữ nhãn V3. Mỗi oracle đã kiểm bằng giá trị chuẩn công bố (`tests/test_oracles.py`).
Thư viện cố ý gồm cả các thuật toán hay bị nhầm (CRC-32C, CRC-16, FNV-1, sdbm, XTEA…).

### IO và SIDE — chạy vector (`behaviour.py`)
- IO dùng DSL nhỏ, ví dụ `{"when": "len == 0", "returns": "0"}` → chạy binary trên vector thỏa điều kiện.
- SIDE: "không ghi out", "ghi out", "không đổi in" → so bộ nhớ trước/sau, có byte canh.

### V1 — chạy code AI viết lại (`v1.py`, `sandbox.py`, `harness/runner.c`)
Biên dịch `recovered_c` → chạy trên 50 vector trong Docker `python:3.12-slim`: không mạng, hệ thống file chỉ đọc,
user nobody, 256 MB RAM, 1 CPU, 64 tiến trình, bỏ mọi quyền, timeout 2 giây mỗi vector và 300 giây tổng; mỗi vector
một tiến trình con riêng. **FEPR** = số vector khớp / 50. FEPR = 1 không phải chứng minh tương đương.

### Self-test V3 (`selftest.py`)
20 hằng đã biết, mỗi hằng trong một ngữ cảnh (lệnh trực tiếp, bảng, số âm, mặt nạ, bị -O2 tách…), biên dịch -O0 và -O2.
Kết quả: bỏ sót 5% (ngưỡng ≤ 5%), nhận nhầm thuật toán sai 0/1.290 lần (`data/v3_selftest.json`).

---

## 8. Mười một lượt chạy — `data/runs/`

| Lượt | Nội dung | Trả lời |
|---|---|---|
| E0, E0_p1, E0_p2, E0_qwen3_think, E0_qwen3_nothink | Thử 5 hàm × 3 cấu hình để chọn prompt và model | Cổng chất lượng |
| **E1** | **Lượt chính**: 60 item, qwen2.5-coder:7b, temperature 0, prompt p3 | RQ1, RQ2 (E2), RQ5 (E3) |
| E1_p2 | Như E1 nhưng prompt p2 (ablation) | Ảnh hưởng của prompt |
| E1_qwen3 | Model thứ hai qwen3:8b | So model |
| E1_llm4decompile | LLM4Decompile-Ref v2 6.7B, chỉ sinh code | Baseline V1 |
| E4 | 20 hàm obf × 5 lần, temperature 0,7 | RQ3 (self-consistency, AUROC) |
| E6 | 10 hàm × 3 cấu hình × 3 lần, temperature 0 | Độ ổn định |

E2 (bảng chéo V1 × V3) và E3 (gán nhầm thuật toán theo nhóm) tính trên E1; E5 là gold set.

## 9. Gold set (E5) — `data/gold/E1/`

120 claim lấy mẫu phân tầng theo nhãn VeRA × cấu hình (đủ 12 ô), ẩn nhãn VeRA và xáo thứ tự. 2 người chấm độc lập
(không viết V3), 1 người phân xử 4 bất đồng. Hướng dẫn chấm: `docs/gold-annotation-guideline.md`.
Kết quả: kappa 0,93; precision contradicted 88%, recall 52%; precision supported+verified 83%; HR hiệu chỉnh 26,2%.

## 10. Phép đo và thống kê — `vera/report/`

HR_strict, HR_loose, tỉ lệ gán nhầm thuật toán, compile rate, FEPR, precision/recall, AUROC, kappa; biến kiểm soát
(số claim/item, độ dài claim, số claim bị lọc, tỉ lệ loại claim). Khoảng tin cậy Wilson và bootstrap 95%; so cấu hình
bằng McNemar trên cặp. Tổng hợp: `data/SUMMARY.md`.

---

## 11. Kết quả lượt chính E1 theo từng item

Mỗi ô: **thuật toán AI nói / số vector code AI viết chạy đúng (trên 50) / số claim bị bắt sai**.
"ko dịch" = code AI viết không biên dịch được.

| Hàm | plain | opt | obf |
|---|---|---|---|
| fn_01 CRC-32 | CRC-32 / 49 / 0 | CRC-32 / 50 / 0 | unknown / ko dịch / 1 |
| fn_02 FNV-1a | CRC-32 / 50 / 1 | CRC-32 / 50 / 1 | unknown / ko dịch / 0 |
| fn_03 Adler-32 | unknown / 50 / 1 | unknown / 1 / 1 | unknown / ko dịch / 1 |
| fn_04 djb2 | unknown / 50 / 1 | unknown / 3 / 0 | unknown / 0 / 0 |
| fn_05 TEA | unknown / 50 / 0 | unknown / 16 / 0 | unknown / ko dịch / 0 |
| fn_06 RC4 | unknown / 4 / 0 | unknown / ko dịch / 0 | unknown / ko dịch / 0 |
| fn_07 Base64 | Base64 / ko dịch / 0 | unknown / 4 / 0 | unknown / ko dịch / 1 |
| fn_08 ≈CRC-32 | unknown / 50 / 1 | CRC-16/XMODEM / 50 / 1 | unknown / ko dịch / 0 |
| fn_09 ≈FNV-1a | CRC-32 / 50 / 1 | CRC-32 / 49 / 1 | unknown / ko dịch / 0 |
| fn_10 ≈Adler | unknown / 49 / 1 | unknown / 1 / 1 | unknown / ko dịch / 1 |
| fn_11 ≈djb2 | unknown / 49 / 1 | unknown / 4 / 0 | unknown / 0 / 0 |
| fn_12 ≈TEA | unknown / 50 / 0 | unknown / 17 / 0 | unknown / ko dịch / 1 |
| fn_13 ≈RC4 | RC4 / 50 / 1 | AI trả sai mẫu | AI trả sai mẫu |
| fn_14 ≈Base64 | Base64 / ko dịch / 1 | unknown / ko dịch / 0 | unknown / ko dịch / 3 |
| fn_15 RLE | unknown / 3 / 0 | unknown / 2 / 0 | unknown / ko dịch / 1 |
| fn_16 checksum cuộn | unknown / 49 / 0 | unknown / 50 / 0 | unknown / ko dịch / 1 |
| fn_17 parser TLV | unknown / 50 / 0 | unknown / ko dịch / 0 | unknown / ko dịch / 0 |
| fn_18 kiểm ngoặc | unknown / ko dịch / 0 | unknown / 2 / 0 | unknown / 1 / 0 |
| fn_19 XOR xoay | unknown / 5 / 0 | unknown / 50 / 0 | unknown / ko dịch / 0 |
| fn_20 hoán vị | unknown / ko dịch / 0 | unknown / 15 / 1 | unknown / ko dịch / 0 |

Đọc nhanh: AI thường né bằng "unknown"; khi gọi tên thì hay gọi "CRC-32" (kể cả cho FNV-1a và bẫy FNV); code viết lại
đúng nhiều ở plain, sụp hẳn ở obf. Mã giả, claim và bằng chứng từng ô xem trong trang demo (thẻ "Tra cứu 60 item").

---

## 12. Demo — `docs/demo.md`

| Cách | Chạy | Cần |
|---|---|---|
| Trang web tĩnh (4 kịch bản, kết quả, tra cứu 60 item) | `data/demo/VeRA_demo.html` | Không cần gì |
| Web + thẻ "▶ Chạy trực tiếp" (đổi con số / hàm có sẵn / tự viết C; dịch tiếng Việt, ô "Vì sao", chú thích code) | `scripts/demo_web.sh` | Máy ảo + Ollama |
| Terminal từng bước | `VERA_OFFLINE=1 scripts/demo.sh fn_08 opt` | Máy ảo |
| Terminal trực tiếp | `scripts/live_demo.sh` | Máy ảo + Ollama |

## 13. Tái lập — `repro/`

`repro/run.sh` (hoặc `repro\run.ps1` trên Windows) dựng Ubuntu 24.04 sạch, build lại 60 binary và 1.000 vector, phát lại
mọi câu trả lời AI từ cache, tính lại mọi kết quả và so với bản commit. Đã đạt trên máy sạch; chờ người ngoài nhóm chạy
(`repro/RESULTS.md`).

## 14. Bản đồ thư mục

| Thư mục | Chứa |
|---|---|
| `corpus/` | 20 hàm C, header chung, đáp án (manifest) |
| `harness/` | runner C chạy hàm trên vector, script Ghidra |
| `vera/corpus`, `vera/extract`, `vera/llm`, `vera/verify`, `vera/report`, `vera/gold` | L0, L1, L2, L3, L4, gold set |
| `vera/live.py`, `vera/webapp.py` | Demo trực tiếp (terminal, web) |
| `data/binaries`, `data/vectors`, `data/artifacts` | 60 binary, 1.000 vector, mã giả + bằng chứng |
| `data/cache/llm` | 481 câu trả lời AI đã lưu |
| `data/runs/` | Kết quả 11 lượt chạy |
| `data/gold/E1/` | Gold set: phiếu chấm, phân xử, điểm |
| `data/SUMMARY.md` | Tổng hợp mọi kết quả |
| `docs/` | Quy ước, nhật ký đáp án, hướng dẫn chấm, demo, kiểm tài liệu |
| `scripts/`, `repro/`, `tests/` | Script chạy, gói tái lập, 45 test |

---
