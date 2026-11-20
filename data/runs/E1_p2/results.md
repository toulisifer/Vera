# Kết quả lượt chạy E1_p2

Model `qwen2.5-coder:7b` (Q4_K_M, digest `dae161e27b0e`), Ollama 0.34.3, temperature 0.0, think=None, backend ghidra 12.1.4.

60/60 item có output đúng schema. HR_strict = contradicted / tổng claim (hallucination). HR_loose = (contradicted + unsupported) / tổng claim (**không kiểm chứng được**, không phải hallucination).

## RQ1 — HR theo cấu hình

| Cấu hình | Claim | HR_strict | HR_loose |
|---|---|---|---|
| tổng | 378 | 5.0% [3.2%–7.7%] (19/378) | 64.3% [59.3%–69.0%] (243/378) |
| plain | 110 | 3.6% [1.4%–9.0%] (4/110) | 71.8% [62.8%–79.4%] (79/110) |
| opt | 112 | 8.0% [4.3%–14.6%] (9/112) | 67.0% [57.8%–75.0%] (75/112) |
| obf | 156 | 3.8% [1.8%–8.1%] (6/156) | 57.1% [49.2%–64.6%] (89/156) |

## RQ1 — HR theo nhóm hàm

| Nhóm | Claim | HR_strict | HR_loose |
|---|---|---|---|
| classic | 129 | 7.8% [4.3%–13.7%] (10/129) | 64.3% [55.8%–72.1%] (83/129) |
| near_miss | 132 | 4.5% [2.1%–9.6%] (6/132) | 62.9% [54.4%–70.6%] (83/132) |
| custom | 117 | 2.6% [0.9%–7.3%] (3/117) | 65.8% [56.8%–73.8%] (77/117) |

## RQ1 — HR theo loại claim

| Loại | Claim | HR_strict | HR_loose |
|---|---|---|---|
| ALG | 2 | 0.0% [0.0%–65.8%] (0/2) | 0.0% [0.0%–65.8%] (0/2) |
| CONST | 102 | 0.0% [0.0%–3.6%] (0/102) | 18.6% [12.3%–27.3%] (19/102) |
| IO | 87 | 4.6% [1.8%–11.2%] (4/87) | 93.1% [85.8%–96.8%] (81/87) |
| CF | 106 | 0.0% [0.0%–3.5%] (0/106) | 100.0% [96.5%–100.0%] (106/106) |
| SIDE | 77 | 19.5% [12.2%–29.7%] (15/77) | 42.9% [32.4%–54.0%] (33/77) |
| NAME | 4 | 0.0% [0.0%–49.0%] (0/4) | 100.0% [51.0%–100.0%] (4/4) |

## RQ1 — HR_strict theo loại claim × cấu hình (so sánh công bằng khi mật độ claim khác nhau)

| Loại | plain | opt | obf |
|---|---|---|---|
| ALG | 0.0% [0.0%–79.3%] (0/1) | 0.0% [0.0%–79.3%] (0/1) | — |
| CONST | 0.0% [0.0%–17.6%] (0/18) | 0.0% [0.0%–15.5%] (0/21) | 0.0% [0.0%–5.7%] (0/63) |
| IO | 3.6% [0.6%–17.7%] (1/28) | 6.7% [1.8%–21.3%] (2/30) | 3.4% [0.6%–17.2%] (1/29) |
| CF | 0.0% [0.0%–9.4%] (0/37) | 0.0% [0.0%–12.1%] (0/28) | 0.0% [0.0%–8.6%] (0/41) |
| SIDE | 13.6% [4.7%–33.3%] (3/22) | 21.9% [11.0%–38.8%] (7/32) | 21.7% [9.7%–41.9%] (5/23) |
| NAME | 0.0% [0.0%–49.0%] (0/4) | — | — |

Claim IO có trường `io` parse được theo DSL (kiểm được bằng vector): 11.5% [6.4%–19.9%] (10/87); phần còn lại luôn unsupported.

## Kiểm soát prompt — claim chép ví dụ

Claim trùng câu ví dụ của prompt: 1.3% [0.6%–3.1%] (5/378); trong đó bị contradicted: 80.0% [37.6%–96.4%] (4/5).

- obf/fn_01: Writes the hash value to out[0] and out[1] only.
- obf/fn_03: Writes the hash value to out[0] and out[1] only.
- obf/fn_09: Writes the final hash value to out[0] and out[1] only.
- obf/fn_17: Writes the result to out[0] and out[1] only.
- opt/fn_10: Writes the 2-byte checksum to out[0] and out[1] only.

## Biến kiểm soát

| Cấu hình | Claim/item | Từ/claim | Claim bị lọc/item |
|---|---|---|---|
| plain | 5.5 | 11.0 | 0.3 |
| opt | 5.6 | 11.0 | 0.5 |
| obf | 7.8 | 9.5 | 0.5 |

## V1 — mã khôi phục

| Cấu hình | Compile | FEPR = 1 | FEPR trung vị |
|---|---|---|---|
| plain | 90.0% [69.9%–97.2%] (18/20) | 60.0% [38.7%–78.1%] (12/20) | 1.00 |
| opt | 95.0% [76.4%–99.1%] (19/20) | 30.0% [14.5%–51.9%] (6/20) | 0.33 |
| obf | 35.0% [18.1%–56.7%] (7/20) | 0.0% [0.0%–16.1%] (0/20) | 0.00 |

## RQ2 — bảng chéo E2 (mức hàm)

| | V1 đạt (FEPR = 1) | V1 không đạt |
|---|---|---|
| Giải thích sạch | 9 | 32 |
| Có claim contradicted | 9 | 10 |

Ô lệch đường chéo (nguồn case study):

- Giải thích sạch nhưng mã sai: obf/fn_04, obf/fn_05, obf/fn_06, obf/fn_10, obf/fn_11, obf/fn_12, obf/fn_13, obf/fn_14, obf/fn_15, obf/fn_16, obf/fn_17, obf/fn_18, obf/fn_19, obf/fn_20, opt/fn_04, opt/fn_05, opt/fn_07, opt/fn_11, opt/fn_12, opt/fn_13, opt/fn_15, opt/fn_17, opt/fn_18, opt/fn_20, plain/fn_05, plain/fn_06, plain/fn_07, plain/fn_13, plain/fn_14, plain/fn_15, plain/fn_18, plain/fn_19
- Mã đúng nhưng giải thích sai: opt/fn_02, opt/fn_08, opt/fn_09, opt/fn_10, opt/fn_16, plain/fn_01, plain/fn_03, plain/fn_16, plain/fn_17

## RQ5 — gán nhầm thuật toán (E3)

| Nhóm | Claim ALG | Gán nhầm (V1b contradicted) | Item có gọi tên thuật toán |
|---|---|---|---|
| classic | 2 | 0.0% [0.0%–65.8%] (0/2) | 9.5% [2.7%–28.9%] (2/21) |
| near_miss | 0 | — | 0.0% [0.0%–15.5%] (0/21) |
| custom | 0 | — | 0.0% [0.0%–17.6%] (0/18) |

## RQ3 — độ tự tin tự khai

AUROC của (1 − confidence) để dự báo claim contradicted: 0.54 (19 claim contradicted, 359 claim khác; 0,5 = ngẫu nhiên).

## So sánh cặp giữa cấu hình (McNemar chính xác, mức hàm)

| Cặp | Chỉ cấu hình 1 có hallucination | Chỉ cấu hình 2 | p |
|---|---|---|---|
| plain_vs_opt | 1 | 6 | 0.125 |
| opt_vs_obf | 4 | 1 | 0.375 |
| plain_vs_obf | 2 | 4 | 0.688 |
