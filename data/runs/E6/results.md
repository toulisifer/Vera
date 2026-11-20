# Kết quả lượt chạy E6

Model `qwen2.5-coder:7b` (Q4_K_M, digest `dae161e27b0e`), Ollama 0.34.3, temperature 0.0, think=None, backend ghidra 12.1.4.

88/90 item có output đúng schema. HR_strict = contradicted / tổng claim (hallucination). HR_loose = (contradicted + unsupported) / tổng claim (**không kiểm chứng được**, không phải hallucination).

## RQ1 — HR theo cấu hình

| Cấu hình | Claim | HR_strict | HR_loose |
|---|---|---|---|
| tổng | 615 | 7.6% [5.8%–10.0%] (47/615) | 61.3% [57.4%–65.1%] (377/615) |
| plain | 182 | 4.4% [2.2%–8.4%] (8/182) | 68.7% [61.6%–75.0%] (125/182) |
| opt | 157 | 7.6% [4.4%–12.9%] (12/157) | 66.2% [58.5%–73.2%] (104/157) |
| obf | 276 | 9.8% [6.8%–13.9%] (27/276) | 53.6% [47.7%–59.4%] (148/276) |

## RQ1 — HR theo nhóm hàm

| Nhóm | Claim | HR_strict | HR_loose |
|---|---|---|---|
| classic | 249 | 6.0% [3.7%–9.7%] (15/249) | 55.8% [49.6%–61.9%] (139/249) |
| near_miss | 248 | 10.9% [7.6%–15.4%] (27/248) | 60.5% [54.3%–66.4%] (150/248) |
| custom | 118 | 4.2% [1.8%–9.5%] (5/118) | 74.6% [66.0%–81.6%] (88/118) |

## RQ1 — HR theo loại claim

| Loại | Claim | HR_strict | HR_loose |
|---|---|---|---|
| ALG | 30 | 23.3% [11.8%–40.9%] (7/30) | 70.0% [52.1%–83.3%] (21/30) |
| CONST | 195 | 0.0% [0.0%–1.9%] (0/195) | 21.0% [15.9%–27.3%] (41/195) |
| IO | 161 | 12.4% [8.2%–18.4%] (20/161) | 87.0% [80.9%–91.3%] (140/161) |
| CF | 133 | 0.0% [0.0%–2.8%] (0/133) | 100.0% [97.2%–100.0%] (133/133) |
| SIDE | 82 | 24.4% [16.4%–34.7%] (20/82) | 34.1% [24.8%–44.9%] (28/82) |
| NAME | 14 | 0.0% [0.0%–21.5%] (0/14) | 100.0% [78.5%–100.0%] (14/14) |

## RQ1 — HR_strict theo loại claim × cấu hình (so sánh công bằng khi mật độ claim khác nhau)

| Loại | plain | opt | obf |
|---|---|---|---|
| ALG | 15.0% [5.2%–36.0%] (3/20) | 40.0% [16.8%–68.7%] (4/10) | — |
| CONST | 0.0% [0.0%–12.1%] (0/28) | 0.0% [0.0%–9.0%] (0/39) | 0.0% [0.0%–2.9%] (0/128) |
| IO | 9.8% [4.3%–21.0%] (5/51) | 4.0% [1.1%–13.5%] (2/50) | 21.7% [13.1%–33.6%] (13/60) |
| CF | 0.0% [0.0%–8.4%] (0/42) | 0.0% [0.0%–11.7%] (0/29) | 0.0% [0.0%–5.8%] (0/62) |
| SIDE | 0.0% [0.0%–9.4%] (0/37) | 24.0% [11.5%–43.4%] (6/25) | 70.0% [48.1%–85.5%] (14/20) |
| NAME | 0.0% [0.0%–49.0%] (0/4) | 0.0% [0.0%–49.0%] (0/4) | 0.0% [0.0%–39.0%] (0/6) |

Claim IO có trường `io` parse được theo DSL (kiểm được bằng vector): 25.5% [19.4%–32.7%] (41/161); phần còn lại luôn unsupported.

## Kiểm soát prompt — claim chép ví dụ

Claim trùng câu ví dụ của prompt: 0.0% [0.0%–0.6%] (0/615); trong đó bị contradicted: —.


## Biến kiểm soát

| Cấu hình | Claim/item | Từ/claim | Claim bị lọc/item |
|---|---|---|---|
| plain | 6.1 | 8.5 | 0.3 |
| opt | 5.6 | 7.6 | 0.5 |
| obf | 9.2 | 7.6 | 0.5 |

## V1 — mã khôi phục

| Cấu hình | Compile | FEPR = 1 | FEPR trung vị |
|---|---|---|---|
| plain | 66.7% [48.8%–80.8%] (20/30) | 30.0% [16.7%–47.9%] (9/30) | 0.98 |
| opt | 83.3% [66.4%–92.7%] (25/30) | 23.3% [11.8%–40.9%] (7/30) | 0.20 |
| obf | 10.0% [3.5%–25.6%] (3/30) | 0.0% [0.0%–11.4%] (0/30) | 0.00 |

## RQ2 — bảng chéo E2 (mức hàm)

| | V1 đạt (FEPR = 1) | V1 không đạt |
|---|---|---|
| Giải thích sạch | 10 | 37 |
| Có claim contradicted | 6 | 35 |

Ô lệch đường chéo (nguồn case study):

- Giải thích sạch nhưng mã sai: obf/fn_05, obf/fn_05, obf/fn_05, obf/fn_08, obf/fn_18, obf/fn_18, obf/fn_18, opt/fn_05, opt/fn_05, opt/fn_05, opt/fn_07, opt/fn_07, opt/fn_07, opt/fn_12, opt/fn_12, opt/fn_12, opt/fn_14, opt/fn_14, opt/fn_14, opt/fn_18, plain/fn_01, plain/fn_03, plain/fn_03, plain/fn_05, plain/fn_07, plain/fn_07, plain/fn_07, plain/fn_08, plain/fn_08, plain/fn_10, plain/fn_10, plain/fn_16, plain/fn_16, plain/fn_16, plain/fn_18, plain/fn_18, plain/fn_18
- Mã đúng nhưng giải thích sai: opt/fn_08, opt/fn_08, plain/fn_01, plain/fn_01, plain/fn_03, plain/fn_08

## RQ5 — gán nhầm thuật toán (E3)

| Nhóm | Claim ALG | Gán nhầm (V1b contradicted) | Item có gọi tên thuật toán |
|---|---|---|---|
| classic | 15 | 0.0% [0.0%–20.4%] (0/15) | 41.7% [27.1%–57.8%] (15/36) |
| near_miss | 14 | 42.9% [21.4%–67.4%] (6/14) | 33.3% [20.2%–49.7%] (12/36) |
| custom | 1 | 100.0% [20.7%–100.0%] (1/1) | 6.2% [1.1%–28.3%] (1/16) |

## RQ3 — độ tự tin tự khai

AUROC của (1 − confidence) để dự báo claim contradicted: 0.59 (47 claim contradicted, 568 claim khác; 0,5 = ngẫu nhiên).

## So sánh cặp giữa cấu hình (McNemar chính xác, mức hàm)

| Cặp | Chỉ cấu hình 1 có hallucination | Chỉ cấu hình 2 | p |
|---|---|---|---|
| plain_vs_opt | 2 | 4 | 0.688 |
| opt_vs_obf | 0 | 4 | 0.125 |
| plain_vs_obf | 0 | 6 | 0.031 |
