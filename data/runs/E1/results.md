# Kết quả lượt chạy E1

Model `qwen2.5-coder:7b` (Q4_K_M, digest `dae161e27b0e`), Ollama 0.34.3, temperature 0.0, think=None, backend ghidra 12.1.4.

58/60 item có output đúng schema. HR_strict = contradicted / tổng claim (hallucination). HR_loose = (contradicted + unsupported) / tổng claim (**không kiểm chứng được**, không phải hallucination).

## RQ1 — HR theo cấu hình

| Cấu hình | Claim | HR_strict | HR_loose |
|---|---|---|---|
| tổng | 389 | 6.4% [4.4%–9.3%] (25/389) | 65.6% [60.7%–70.1%] (255/389) |
| plain | 117 | 7.7% [4.1%–14.0%] (9/117) | 66.7% [57.7%–74.6%] (78/117) |
| opt | 118 | 5.1% [2.4%–10.7%] (6/118) | 72.0% [63.3%–79.3%] (85/118) |
| obf | 154 | 6.5% [3.6%–11.5%] (10/154) | 59.7% [51.8%–67.2%] (92/154) |

## RQ1 — HR theo nhóm hàm

| Nhóm | Claim | HR_strict | HR_loose |
|---|---|---|---|
| classic | 136 | 5.9% [3.0%–11.2%] (8/136) | 61.8% [53.4%–69.5%] (84/136) |
| near_miss | 125 | 11.2% [6.8%–17.9%] (14/125) | 63.2% [54.5%–71.1%] (79/125) |
| custom | 128 | 2.3% [0.8%–6.7%] (3/128) | 71.9% [63.5%–78.9%] (92/128) |

## RQ1 — HR theo loại claim

| Loại | Claim | HR_strict | HR_loose |
|---|---|---|---|
| ALG | 18 | 38.9% [20.3%–61.4%] (7/18) | 83.3% [60.8%–94.2%] (15/18) |
| CONST | 110 | 0.0% [0.0%–3.4%] (0/110) | 26.4% [19.0%–35.3%] (29/110) |
| IO | 102 | 10.8% [6.1%–18.3%] (11/102) | 87.3% [79.4%–92.4%] (89/102) |
| CF | 103 | 0.0% [0.0%–3.6%] (0/103) | 100.0% [96.4%–100.0%] (103/103) |
| SIDE | 49 | 14.3% [7.1%–26.7%] (7/49) | 24.5% [14.6%–38.1%] (12/49) |
| NAME | 7 | 0.0% [0.0%–35.4%] (0/7) | 100.0% [64.6%–100.0%] (7/7) |

## RQ1 — HR_strict theo loại claim × cấu hình (so sánh công bằng khi mật độ claim khác nhau)

| Loại | plain | opt | obf |
|---|---|---|---|
| ALG | 36.4% [15.2%–64.6%] (4/11) | 42.9% [15.8%–75.0%] (3/7) | — |
| CONST | 0.0% [0.0%–19.4%] (0/16) | 0.0% [0.0%–11.4%] (0/30) | 0.0% [0.0%–5.7%] (0/64) |
| IO | 15.6% [6.9%–31.8%] (5/32) | 0.0% [0.0%–9.2%] (0/38) | 18.8% [8.9%–35.3%] (6/32) |
| CF | 0.0% [0.0%–10.2%] (0/34) | 0.0% [0.0%–14.3%] (0/23) | 0.0% [0.0%–7.7%] (0/46) |
| SIDE | 0.0% [0.0%–14.3%] (0/23) | 17.6% [6.2%–41.0%] (3/17) | 44.4% [18.9%–73.3%] (4/9) |
| NAME | 0.0% [0.0%–79.3%] (0/1) | 0.0% [0.0%–56.2%] (0/3) | 0.0% [0.0%–56.2%] (0/3) |

Claim IO có trường `io` parse được theo DSL (kiểm được bằng vector): 23.5% [16.4%–32.6%] (24/102); phần còn lại luôn unsupported.

## Kiểm soát prompt — claim chép ví dụ

Claim trùng câu ví dụ của prompt: 0.8% [0.3%–2.2%] (3/389); trong đó bị contradicted: 0.0% [0.0%–56.2%] (0/3).

- opt/fn_15: Writes the encoded result to out[0..<len>].
- plain/fn_06: Writes the encrypted data to out[0..<len>].
- plain/fn_19: Writes transformed data to out[0..<len>].

## Biến kiểm soát

| Cấu hình | Claim/item | Từ/claim | Claim bị lọc/item |
|---|---|---|---|
| plain | 5.8 | 9.1 | 0.6 |
| opt | 6.2 | 7.6 | 0.6 |
| obf | 8.1 | 7.9 | 1.4 |

## V1 — mã khôi phục

| Cấu hình | Compile | FEPR = 1 | FEPR trung vị |
|---|---|---|---|
| plain | 80.0% [58.4%–91.9%] (16/20) | 45.0% [25.8%–65.8%] (9/20) | 0.98 |
| opt | 80.0% [58.4%–91.9%] (16/20) | 25.0% [11.2%–46.9%] (5/20) | 0.08 |
| obf | 15.0% [5.2%–36.0%] (3/20) | 0.0% [0.0%–16.1%] (0/20) | 0.00 |

## RQ2 — bảng chéo E2 (mức hàm)

| | V1 đạt (FEPR = 1) | V1 không đạt |
|---|---|---|
| Giải thích sạch | 6 | 29 |
| Có claim contradicted | 8 | 15 |

Ô lệch đường chéo (nguồn case study):

- Giải thích sạch nhưng mã sai: obf/fn_02, obf/fn_04, obf/fn_05, obf/fn_06, obf/fn_08, obf/fn_09, obf/fn_11, obf/fn_17, obf/fn_18, obf/fn_19, obf/fn_20, opt/fn_04, opt/fn_05, opt/fn_06, opt/fn_07, opt/fn_11, opt/fn_12, opt/fn_14, opt/fn_15, opt/fn_17, opt/fn_18, plain/fn_01, plain/fn_06, plain/fn_07, plain/fn_15, plain/fn_16, plain/fn_18, plain/fn_19, plain/fn_20
- Mã đúng nhưng giải thích sai: opt/fn_02, opt/fn_08, plain/fn_02, plain/fn_03, plain/fn_04, plain/fn_08, plain/fn_09, plain/fn_13

## RQ5 — gán nhầm thuật toán (E3)

| Nhóm | Claim ALG | Gán nhầm (V1b contradicted) | Item có gọi tên thuật toán |
|---|---|---|---|
| classic | 9 | 22.2% [6.3%–54.7%] (2/9) | 42.9% [24.5%–63.5%] (9/21) |
| near_miss | 9 | 55.6% [26.7%–81.1%] (5/9) | 47.4% [27.3%–68.3%] (9/19) |
| custom | 0 | — | 0.0% [0.0%–17.6%] (0/18) |

## RQ3 — độ tự tin tự khai

AUROC của (1 − confidence) để dự báo claim contradicted: 0.53 (25 claim contradicted, 364 claim khác; 0,5 = ngẫu nhiên).

## So sánh cặp giữa cấu hình (McNemar chính xác, mức hàm)

| Cặp | Chỉ cấu hình 1 có hallucination | Chỉ cấu hình 2 | p |
|---|---|---|---|
| plain_vs_opt | 3 | 1 | 0.625 |
| opt_vs_obf | 4 | 6 | 0.754 |
| plain_vs_obf | 5 | 5 | 1.000 |
