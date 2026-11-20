# Kết quả lượt chạy E0

Model `qwen2.5-coder:7b` (Q4_K_M, digest `dae161e27b0e`), Ollama 0.34.3, temperature 0.0, think=None, backend ghidra 12.1.4.

15/15 item có output đúng schema. HR_strict = contradicted / tổng claim (hallucination). HR_loose = (contradicted + unsupported) / tổng claim (**không kiểm chứng được**, không phải hallucination).

## RQ1 — HR theo cấu hình

| Cấu hình | Claim | HR_strict | HR_loose |
|---|---|---|---|
| tổng | 123 | 5.7% [2.8%–11.3%] (7/123) | 65.9% [57.1%–73.6%] (81/123) |
| plain | 31 | 6.5% [1.8%–20.7%] (2/31) | 74.2% [56.8%–86.3%] (23/31) |
| opt | 37 | 2.7% [0.5%–13.8%] (1/37) | 75.7% [59.9%–86.6%] (28/37) |
| obf | 55 | 7.3% [2.9%–17.3%] (4/55) | 54.5% [41.5%–67.0%] (30/55) |

## RQ1 — HR theo nhóm hàm

| Nhóm | Claim | HR_strict | HR_loose |
|---|---|---|---|
| classic | 44 | 2.3% [0.4%–11.8%] (1/44) | 54.5% [40.1%–68.3%] (24/44) |
| near_miss | 45 | 13.3% [6.3%–26.2%] (6/45) | 64.4% [49.8%–76.8%] (29/45) |
| custom | 34 | 0.0% [0.0%–10.2%] (0/34) | 82.4% [66.5%–91.7%] (28/34) |

## RQ1 — HR theo loại claim

| Loại | Claim | HR_strict | HR_loose |
|---|---|---|---|
| ALG | 5 | 40.0% [11.8%–76.9%] (2/5) | 60.0% [23.1%–88.2%] (3/5) |
| CONST | 40 | 0.0% [0.0%–8.8%] (0/40) | 32.5% [20.1%–48.0%] (13/40) |
| IO | 31 | 12.9% [5.1%–28.9%] (4/31) | 87.1% [71.1%–94.9%] (27/31) |
| CF | 34 | 0.0% [0.0%–10.2%] (0/34) | 100.0% [89.8%–100.0%] (34/34) |
| SIDE | 12 | 8.3% [1.5%–35.4%] (1/12) | 25.0% [8.9%–53.2%] (3/12) |
| NAME | 1 | 0.0% [0.0%–79.3%] (0/1) | 100.0% [20.7%–100.0%] (1/1) |

## RQ1 — HR_strict theo loại claim × cấu hình (so sánh công bằng khi mật độ claim khác nhau)

| Loại | plain | opt | obf |
|---|---|---|---|
| ALG | 33.3% [6.1%–79.2%] (1/3) | 50.0% [9.5%–90.5%] (1/2) | — |
| CONST | 0.0% [0.0%–65.8%] (0/2) | 0.0% [0.0%–22.8%] (0/13) | 0.0% [0.0%–13.3%] (0/25) |
| IO | 11.1% [2.0%–43.5%] (1/9) | 0.0% [0.0%–24.3%] (0/12) | 30.0% [10.8%–60.3%] (3/10) |
| CF | 0.0% [0.0%–25.9%] (0/11) | 0.0% [0.0%–39.0%] (0/6) | 0.0% [0.0%–18.4%] (0/17) |
| SIDE | 0.0% [0.0%–39.0%] (0/6) | 0.0% [0.0%–49.0%] (0/4) | 50.0% [9.5%–90.5%] (1/2) |
| NAME | — | — | 0.0% [0.0%–79.3%] (0/1) |

Claim IO có trường `io` parse được theo DSL (kiểm được bằng vector): 25.8% [13.7%–43.2%] (8/31); phần còn lại luôn unsupported.

## Kiểm soát prompt — claim chép ví dụ

Claim trùng câu ví dụ của prompt: 0.0% [0.0%–3.0%] (0/123); trong đó bị contradicted: —.


## Biến kiểm soát

| Cấu hình | Claim/item | Từ/claim | Claim bị lọc/item |
|---|---|---|---|
| plain | 6.2 | 9.8 | 0.6 |
| opt | 7.4 | 7.3 | 1.2 |
| obf | 11.0 | 8.1 | 0.8 |

## V1 — mã khôi phục

| Cấu hình | Compile | FEPR = 1 | FEPR trung vị |
|---|---|---|---|
| plain | 60.0% [23.1%–88.2%] (3/5) | 40.0% [11.8%–76.9%] (2/5) | 0.98 |
| opt | 80.0% [37.6%–96.4%] (4/5) | 40.0% [11.8%–76.9%] (2/5) | 0.32 |
| obf | 20.0% [3.6%–62.4%] (1/5) | 0.0% [0.0%–43.4%] (0/5) | 0.00 |

## RQ2 — bảng chéo E2 (mức hàm)

| | V1 đạt (FEPR = 1) | V1 không đạt |
|---|---|---|
| Giải thích sạch | 2 | 8 |
| Có claim contradicted | 2 | 3 |

Ô lệch đường chéo (nguồn case study):

- Giải thích sạch nhưng mã sai: obf/fn_05, obf/fn_08, obf/fn_18, opt/fn_05, opt/fn_14, opt/fn_18, plain/fn_01, plain/fn_18
- Mã đúng nhưng giải thích sai: opt/fn_08, plain/fn_08

## RQ5 — gán nhầm thuật toán (E3)

| Nhóm | Claim ALG | Gán nhầm (V1b contradicted) | Item có gọi tên thuật toán |
|---|---|---|---|
| classic | 2 | 0.0% [0.0%–65.8%] (0/2) | 33.3% [9.7%–70.0%] (2/6) |
| near_miss | 3 | 66.7% [20.8%–93.9%] (2/3) | 50.0% [18.8%–81.2%] (3/6) |
| custom | 0 | — | 0.0% [0.0%–56.2%] (0/3) |

## RQ3 — độ tự tin tự khai

AUROC của (1 − confidence) để dự báo claim contradicted: 0.49 (7 claim contradicted, 116 claim khác; 0,5 = ngẫu nhiên).

## So sánh cặp giữa cấu hình (McNemar chính xác, mức hàm)

| Cặp | Chỉ cấu hình 1 có hallucination | Chỉ cấu hình 2 | p |
|---|---|---|---|
| plain_vs_opt | 1 | 0 | 1.000 |
| opt_vs_obf | 1 | 2 | 1.000 |
| plain_vs_obf | 1 | 1 | 1.000 |
