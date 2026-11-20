# Kết quả lượt chạy E1_llm4decompile

Model `hf.co/RichardErkhov/LLM4Binary_-_llm4decompile-6.7b-v2-gguf:Q4_K_M` (Q4_K_M, digest `811c74b0fbcc`), Ollama 0.34.3, temperature 0.0, think=None, backend None None.

60/60 item có output đúng schema. HR_strict = contradicted / tổng claim (hallucination). HR_loose = (contradicted + unsupported) / tổng claim (**không kiểm chứng được**, không phải hallucination).

## RQ1 — HR theo cấu hình

| Cấu hình | Claim | HR_strict | HR_loose |
|---|---|---|---|
| tổng | 0 | — | — |
| plain | 0 | — | — |
| opt | 0 | — | — |
| obf | 0 | — | — |

## RQ1 — HR theo nhóm hàm

| Nhóm | Claim | HR_strict | HR_loose |
|---|---|---|---|
| classic | 0 | — | — |
| near_miss | 0 | — | — |
| custom | 0 | — | — |

## RQ1 — HR theo loại claim

| Loại | Claim | HR_strict | HR_loose |
|---|---|---|---|
| ALG | 0 | — | — |
| CONST | 0 | — | — |
| IO | 0 | — | — |
| CF | 0 | — | — |
| SIDE | 0 | — | — |
| NAME | 0 | — | — |

## RQ1 — HR_strict theo loại claim × cấu hình (so sánh công bằng khi mật độ claim khác nhau)

| Loại | plain | opt | obf |
|---|---|---|---|

Claim IO có trường `io` parse được theo DSL (kiểm được bằng vector): —; phần còn lại luôn unsupported.

## Kiểm soát prompt — claim chép ví dụ

Claim trùng câu ví dụ của prompt: —; trong đó bị contradicted: —.


## Biến kiểm soát

| Cấu hình | Claim/item | Từ/claim | Claim bị lọc/item |
|---|---|---|---|

## V1 — mã khôi phục

| Cấu hình | Compile | FEPR = 1 | FEPR trung vị |
|---|---|---|---|
| plain | 100.0% [83.9%–100.0%] (20/20) | 45.0% [25.8%–65.8%] (9/20) | 0.36 |
| opt | 80.0% [58.4%–91.9%] (16/20) | 15.0% [5.2%–36.0%] (3/20) | 0.05 |
| obf | 55.0% [34.2%–74.2%] (11/20) | 0.0% [0.0%–16.1%] (0/20) | 0.00 |

## RQ2 — bảng chéo E2 (mức hàm)

| | V1 đạt (FEPR = 1) | V1 không đạt |
|---|---|---|
| Giải thích sạch | 12 | 48 |
| Có claim contradicted | 0 | 0 |

Ô lệch đường chéo (nguồn case study):

- Giải thích sạch nhưng mã sai: obf/fn_01, obf/fn_02, obf/fn_03, obf/fn_04, obf/fn_05, obf/fn_06, obf/fn_07, obf/fn_08, obf/fn_09, obf/fn_10, obf/fn_11, obf/fn_12, obf/fn_13, obf/fn_14, obf/fn_15, obf/fn_16, obf/fn_17, obf/fn_18, obf/fn_19, obf/fn_20, opt/fn_02, opt/fn_03, opt/fn_05, opt/fn_06, opt/fn_07, opt/fn_08, opt/fn_09, opt/fn_10, opt/fn_11, opt/fn_12, opt/fn_13, opt/fn_14, opt/fn_16, opt/fn_17, opt/fn_18, opt/fn_19, opt/fn_20, plain/fn_02, plain/fn_05, plain/fn_08, plain/fn_09, plain/fn_10, plain/fn_11, plain/fn_12, plain/fn_13, plain/fn_16, plain/fn_19, plain/fn_20
- Mã đúng nhưng giải thích sai: —

## RQ5 — gán nhầm thuật toán (E3)

| Nhóm | Claim ALG | Gán nhầm (V1b contradicted) | Item có gọi tên thuật toán |
|---|---|---|---|
| classic | 0 | — | 0.0% [0.0%–15.5%] (0/21) |
| near_miss | 0 | — | 0.0% [0.0%–15.5%] (0/21) |
| custom | 0 | — | 0.0% [0.0%–17.6%] (0/18) |

## RQ3 — độ tự tin tự khai

AUROC của (1 − confidence) để dự báo claim contradicted: — (0 claim contradicted, 0 claim khác; 0,5 = ngẫu nhiên).

## So sánh cặp giữa cấu hình (McNemar chính xác, mức hàm)

| Cặp | Chỉ cấu hình 1 có hallucination | Chỉ cấu hình 2 | p |
|---|---|---|---|
| plain_vs_opt | 0 | 0 | 1.000 |
| opt_vs_obf | 0 | 0 | 1.000 |
| plain_vs_obf | 0 | 0 | 1.000 |
