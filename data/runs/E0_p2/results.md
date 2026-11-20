# Kết quả lượt chạy E0_p2

Model `qwen2.5-coder:7b` (Q4_K_M, digest `dae161e27b0e`), Ollama 0.34.3, temperature 0.0, think=None, backend ghidra 12.1.4.

15/15 item có output đúng schema. HR_strict = contradicted / tổng claim (hallucination). HR_loose = (contradicted + unsupported) / tổng claim (**không kiểm chứng được**, không phải hallucination).

## RQ1 — HR theo cấu hình

| Cấu hình | Claim | HR_strict | HR_loose |
|---|---|---|---|
| tổng | 93 | 6.5% [3.0%–13.4%] (6/93) | 58.1% [47.9%–67.6%] (54/93) |
| plain | 23 | 4.3% [0.8%–21.0%] (1/23) | 65.2% [44.9%–81.2%] (15/23) |
| opt | 25 | 12.0% [4.2%–30.0%] (3/25) | 64.0% [44.5%–79.8%] (16/25) |
| obf | 45 | 4.4% [1.2%–14.8%] (2/45) | 51.1% [37.0%–65.0%] (23/45) |

## RQ1 — HR theo nhóm hàm

| Nhóm | Claim | HR_strict | HR_loose |
|---|---|---|---|
| classic | 41 | 7.3% [2.5%–19.4%] (3/41) | 51.2% [36.5%–65.7%] (21/41) |
| near_miss | 35 | 8.6% [3.0%–22.4%] (3/35) | 62.9% [46.3%–76.8%] (22/35) |
| custom | 17 | 0.0% [0.0%–18.4%] (0/17) | 64.7% [41.3%–82.7%] (11/17) |

## RQ1 — HR theo loại claim

| Loại | Claim | HR_strict | HR_loose |
|---|---|---|---|
| ALG | 2 | 0.0% [0.0%–65.8%] (0/2) | 0.0% [0.0%–65.8%] (0/2) |
| CONST | 29 | 0.0% [0.0%–11.7%] (0/29) | 6.9% [1.9%–22.0%] (2/29) |
| IO | 20 | 5.0% [0.9%–23.6%] (1/20) | 100.0% [83.9%–100.0%] (20/20) |
| CF | 23 | 0.0% [0.0%–14.3%] (0/23) | 100.0% [85.7%–100.0%] (23/23) |
| SIDE | 17 | 29.4% [13.3%–53.1%] (5/17) | 41.2% [21.6%–64.0%] (7/17) |
| NAME | 2 | 0.0% [0.0%–65.8%] (0/2) | 100.0% [34.2%–100.0%] (2/2) |

## RQ1 — HR_strict theo loại claim × cấu hình (so sánh công bằng khi mật độ claim khác nhau)

| Loại | plain | opt | obf |
|---|---|---|---|
| ALG | 0.0% [0.0%–79.3%] (0/1) | 0.0% [0.0%–79.3%] (0/1) | — |
| CONST | 0.0% [0.0%–56.2%] (0/3) | 0.0% [0.0%–43.4%] (0/5) | 0.0% [0.0%–15.5%] (0/21) |
| IO | 0.0% [0.0%–43.4%] (0/5) | 12.5% [2.2%–47.1%] (1/8) | 0.0% [0.0%–35.4%] (0/7) |
| CF | 0.0% [0.0%–35.4%] (0/7) | 0.0% [0.0%–39.0%] (0/6) | 0.0% [0.0%–27.8%] (0/10) |
| SIDE | 20.0% [3.6%–62.4%] (1/5) | 40.0% [11.8%–76.9%] (2/5) | 28.6% [8.2%–64.1%] (2/7) |
| NAME | 0.0% [0.0%–65.8%] (0/2) | — | — |

Claim IO có trường `io` parse được theo DSL (kiểm được bằng vector): 5.0% [0.9%–23.6%] (1/20); phần còn lại luôn unsupported.

## Kiểm soát prompt — claim chép ví dụ

Claim trùng câu ví dụ của prompt: 1.1% [0.2%–5.8%] (1/93); trong đó bị contradicted: 100.0% [20.7%–100.0%] (1/1).

- obf/fn_01: Writes the hash value to out[0] and out[1] only.

## Biến kiểm soát

| Cấu hình | Claim/item | Từ/claim | Claim bị lọc/item |
|---|---|---|---|
| plain | 4.6 | 10.7 | 0.6 |
| opt | 5.0 | 10.4 | 0.6 |
| obf | 9.0 | 9.3 | 0.8 |

## V1 — mã khôi phục

| Cấu hình | Compile | FEPR = 1 | FEPR trung vị |
|---|---|---|---|
| plain | 60.0% [23.1%–88.2%] (3/5) | 40.0% [11.8%–76.9%] (2/5) | 0.32 |
| opt | 100.0% [56.6%–100.0%] (5/5) | 20.0% [3.6%–62.4%] (1/5) | 0.12 |
| obf | 40.0% [11.8%–76.9%] (2/5) | 0.0% [0.0%–43.4%] (0/5) | 0.00 |

## RQ2 — bảng chéo E2 (mức hàm)

| | V1 đạt (FEPR = 1) | V1 không đạt |
|---|---|---|
| Giải thích sạch | 1 | 8 |
| Có claim contradicted | 2 | 4 |

Ô lệch đường chéo (nguồn case study):

- Giải thích sạch nhưng mã sai: obf/fn_05, obf/fn_14, obf/fn_18, opt/fn_05, opt/fn_18, plain/fn_05, plain/fn_14, plain/fn_18
- Mã đúng nhưng giải thích sai: opt/fn_08, plain/fn_01

## RQ5 — gán nhầm thuật toán (E3)

| Nhóm | Claim ALG | Gán nhầm (V1b contradicted) | Item có gọi tên thuật toán |
|---|---|---|---|
| classic | 2 | 0.0% [0.0%–65.8%] (0/2) | 33.3% [9.7%–70.0%] (2/6) |
| near_miss | 0 | — | 0.0% [0.0%–39.0%] (0/6) |
| custom | 0 | — | 0.0% [0.0%–56.2%] (0/3) |

## RQ3 — độ tự tin tự khai

AUROC của (1 − confidence) để dự báo claim contradicted: 0.52 (6 claim contradicted, 87 claim khác; 0,5 = ngẫu nhiên).

## So sánh cặp giữa cấu hình (McNemar chính xác, mức hàm)

| Cặp | Chỉ cấu hình 1 có hallucination | Chỉ cấu hình 2 | p |
|---|---|---|---|
| plain_vs_opt | 0 | 2 | 0.500 |
| opt_vs_obf | 1 | 0 | 1.000 |
| plain_vs_obf | 0 | 1 | 1.000 |
