# Kết quả lượt chạy E4

Model `qwen2.5-coder:7b` (Q4_K_M, digest `dae161e27b0e`), Ollama 0.34.3, temperature 0.7, think=None, backend ghidra 12.1.4.

98/100 item có output đúng schema. HR_strict = contradicted / tổng claim (hallucination). HR_loose = (contradicted + unsupported) / tổng claim (**không kiểm chứng được**, không phải hallucination).

## RQ1 — HR theo cấu hình

| Cấu hình | Claim | HR_strict | HR_loose |
|---|---|---|---|
| tổng | 724 | 5.8% [4.3%–7.7%] (42/724) | 64.6% [61.1%–68.0%] (468/724) |
| plain | 0 | — | — |
| opt | 0 | — | — |
| obf | 724 | 5.8% [4.3%–7.7%] (42/724) | 64.6% [61.1%–68.0%] (468/724) |

## RQ1 — HR theo nhóm hàm

| Nhóm | Claim | HR_strict | HR_loose |
|---|---|---|---|
| classic | 249 | 5.2% [3.1%–8.7%] (13/249) | 59.8% [53.6%–65.7%] (149/249) |
| near_miss | 250 | 6.4% [4.0%–10.1%] (16/250) | 63.2% [57.1%–68.9%] (158/250) |
| custom | 225 | 5.8% [3.4%–9.6%] (13/225) | 71.6% [65.3%–77.1%] (161/225) |

## RQ1 — HR theo loại claim

| Loại | Claim | HR_strict | HR_loose |
|---|---|---|---|
| ALG | 22 | 0.0% [0.0%–14.9%] (0/22) | 90.9% [72.2%–97.5%] (20/22) |
| CONST | 245 | 0.0% [0.0%–1.5%] (0/245) | 26.9% [21.8%–32.8%] (66/245) |
| IO | 183 | 8.2% [5.0%–13.1%] (15/183) | 92.3% [87.6%–95.4%] (169/183) |
| CF | 152 | 0.0% [0.0%–2.5%] (0/152) | 100.0% [97.5%–100.0%] (152/152) |
| SIDE | 115 | 23.5% [16.7%–32.0%] (27/115) | 47.0% [38.1%–56.0%] (54/115) |
| NAME | 7 | 0.0% [0.0%–35.4%] (0/7) | 100.0% [64.6%–100.0%] (7/7) |

## RQ1 — HR_strict theo loại claim × cấu hình (so sánh công bằng khi mật độ claim khác nhau)

| Loại | plain | opt | obf |
|---|---|---|---|
| ALG | — | — | 0.0% [0.0%–14.9%] (0/22) |
| CONST | — | — | 0.0% [0.0%–1.5%] (0/245) |
| IO | — | — | 8.2% [5.0%–13.1%] (15/183) |
| CF | — | — | 0.0% [0.0%–2.5%] (0/152) |
| SIDE | — | — | 23.5% [16.7%–32.0%] (27/115) |
| NAME | — | — | 0.0% [0.0%–35.4%] (0/7) |

Claim IO có trường `io` parse được theo DSL (kiểm được bằng vector): 16.9% [12.2%–23.0%] (31/183); phần còn lại luôn unsupported.

## Kiểm soát prompt — claim chép ví dụ

Claim trùng câu ví dụ của prompt: 0.8% [0.4%–1.8%] (6/724); trong đó bị contradicted: 16.7% [3.0%–56.4%] (1/6).

- obf/fn_07: Writes the encoded data to out[0..<len>].
- obf/fn_16: Writes 0x1f9 to out[0..<len>].
- obf/fn_17: Writes *(undefined1 *)(param_4 + param_2) to out[<first>..<last>].
- obf/fn_17: The function writes to out[<first>..<last>].
- obf/fn_18: The function reads from the input buffer in[0..<len>].
- obf/fn_19: Writes a transformed value to out[<first>..<last>].

## Biến kiểm soát

| Cấu hình | Claim/item | Từ/claim | Claim bị lọc/item |
|---|---|---|---|
| obf | 7.4 | 7.6 | 0.6 |

## V1 — mã khôi phục

| Cấu hình | Compile | FEPR = 1 | FEPR trung vị |
|---|---|---|---|
| plain | — | — | — |
| opt | — | — | — |
| obf | 35.0% [26.4%–44.7%] (35/100) | 1.0% [0.2%–5.4%] (1/100) | 0.00 |

## RQ2 — bảng chéo E2 (mức hàm)

| | V1 đạt (FEPR = 1) | V1 không đạt |
|---|---|---|
| Giải thích sạch | 0 | 66 |
| Có claim contradicted | 1 | 31 |

Ô lệch đường chéo (nguồn case study):

- Giải thích sạch nhưng mã sai: obf/fn_01, obf/fn_02, obf/fn_02, obf/fn_02, obf/fn_02, obf/fn_02, obf/fn_03, obf/fn_03, obf/fn_03, obf/fn_04, obf/fn_04, obf/fn_04, obf/fn_04, obf/fn_04, obf/fn_05, obf/fn_05, obf/fn_05, obf/fn_05, obf/fn_06, obf/fn_06, obf/fn_07, obf/fn_07, obf/fn_07, obf/fn_08, obf/fn_08, obf/fn_09, obf/fn_09, obf/fn_09, obf/fn_10, obf/fn_10, obf/fn_10, obf/fn_11, obf/fn_11, obf/fn_11, obf/fn_12, obf/fn_12, obf/fn_12, obf/fn_12, obf/fn_13, obf/fn_13, obf/fn_13, obf/fn_13, obf/fn_14, obf/fn_14, obf/fn_14, obf/fn_14, obf/fn_15, obf/fn_15, obf/fn_15, obf/fn_15, obf/fn_16, obf/fn_16, obf/fn_17, obf/fn_17, obf/fn_17, obf/fn_17, obf/fn_18, obf/fn_18, obf/fn_19, obf/fn_19, obf/fn_19, obf/fn_19, obf/fn_20, obf/fn_20, obf/fn_20, obf/fn_20
- Mã đúng nhưng giải thích sai: obf/fn_19

## RQ5 — gán nhầm thuật toán (E3)

| Nhóm | Claim ALG | Gán nhầm (V1b contradicted) | Item có gọi tên thuật toán |
|---|---|---|---|
| classic | 6 | 0.0% [0.0%–39.0%] (0/6) | 18.2% [8.6%–34.4%] (6/33) |
| near_miss | 9 | 0.0% [0.0%–29.9%] (0/9) | 22.9% [12.1%–39.0%] (8/35) |
| custom | 7 | 0.0% [0.0%–35.4%] (0/7) | 20.0% [9.5%–37.3%] (6/30) |

## RQ3 — độ tự tin tự khai

AUROC của (1 − confidence) để dự báo claim contradicted: 0.71 (42 claim contradicted, 682 claim khác; 0,5 = ngẫu nhiên).

## So sánh cặp giữa cấu hình (McNemar chính xác, mức hàm)

| Cặp | Chỉ cấu hình 1 có hallucination | Chỉ cấu hình 2 | p |
|---|---|---|---|
| plain_vs_opt | 0 | 0 | 1.000 |
| opt_vs_obf | 0 | 0 | 1.000 |
| plain_vs_obf | 0 | 0 | 1.000 |
