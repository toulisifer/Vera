# Kết quả lượt chạy E1_qwen3

Model `qwen3:8b` (Q4_K_M, digest `500a1f067a9f`), Ollama 0.34.3, temperature 0.0, think=False, backend ghidra 12.1.4.

50/60 item có output đúng schema. HR_strict = contradicted / tổng claim (hallucination). HR_loose = (contradicted + unsupported) / tổng claim (**không kiểm chứng được**, không phải hallucination).

## RQ1 — HR theo cấu hình

| Cấu hình | Claim | HR_strict | HR_loose |
|---|---|---|---|
| tổng | 448 | 2.2% [1.2%–4.1%] (10/448) | 67.6% [63.2%–71.8%] (303/448) |
| plain | 154 | 0.6% [0.1%–3.6%] (1/154) | 71.4% [63.8%–78.0%] (110/154) |
| opt | 136 | 1.5% [0.4%–5.2%] (2/136) | 75.0% [67.1%–81.5%] (102/136) |
| obf | 158 | 4.4% [2.2%–8.9%] (7/158) | 57.6% [49.8%–65.0%] (91/158) |

## RQ1 — HR theo nhóm hàm

| Nhóm | Claim | HR_strict | HR_loose |
|---|---|---|---|
| classic | 174 | 2.9% [1.2%–6.5%] (5/174) | 62.6% [55.3%–69.5%] (109/174) |
| near_miss | 168 | 2.4% [0.9%–6.0%] (4/168) | 66.1% [58.6%–72.8%] (111/168) |
| custom | 106 | 0.9% [0.2%–5.2%] (1/106) | 78.3% [69.5%–85.1%] (83/106) |

## RQ1 — HR theo loại claim

| Loại | Claim | HR_strict | HR_loose |
|---|---|---|---|
| ALG | 25 | 8.0% [2.2%–25.0%] (2/25) | 88.0% [70.0%–95.8%] (22/25) |
| CONST | 129 | 0.0% [0.0%–2.9%] (0/129) | 34.1% [26.5%–42.6%] (44/129) |
| IO | 102 | 5.9% [2.7%–12.2%] (6/102) | 97.1% [91.7%–99.0%] (99/102) |
| CF | 114 | 0.0% [0.0%–3.3%] (0/114) | 100.0% [96.7%–100.0%] (114/114) |
| SIDE | 60 | 3.3% [0.9%–11.4%] (2/60) | 10.0% [4.7%–20.1%] (6/60) |
| NAME | 18 | 0.0% [0.0%–17.6%] (0/18) | 100.0% [82.4%–100.0%] (18/18) |

## RQ1 — HR_strict theo loại claim × cấu hình (so sánh công bằng khi mật độ claim khác nhau)

| Loại | plain | opt | obf |
|---|---|---|---|
| ALG | 6.7% [1.2%–29.8%] (1/15) | 14.3% [2.6%–51.3%] (1/7) | 0.0% [0.0%–56.2%] (0/3) |
| CONST | 0.0% [0.0%–10.7%] (0/32) | 0.0% [0.0%–10.4%] (0/33) | 0.0% [0.0%–5.7%] (0/64) |
| IO | 0.0% [0.0%–9.9%] (0/35) | 0.0% [0.0%–9.4%] (0/37) | 20.0% [9.5%–37.3%] (6/30) |
| CF | 0.0% [0.0%–8.0%] (0/44) | 0.0% [0.0%–9.9%] (0/35) | 0.0% [0.0%–9.9%] (0/35) |
| SIDE | 0.0% [0.0%–13.8%] (0/24) | 5.3% [0.9%–24.6%] (1/19) | 5.9% [1.0%–27.0%] (1/17) |
| NAME | 0.0% [0.0%–49.0%] (0/4) | 0.0% [0.0%–43.4%] (0/5) | 0.0% [0.0%–29.9%] (0/9) |

Claim IO có trường `io` parse được theo DSL (kiểm được bằng vector): 8.8% [4.7%–15.9%] (9/102); phần còn lại luôn unsupported.

## Kiểm soát prompt — claim chép ví dụ

Claim trùng câu ví dụ của prompt: 0.9% [0.3%–2.3%] (4/448); trong đó bị contradicted: 0.0% [0.0%–49.0%] (0/4).

- obf/fn_07: Writes 4 base64 characters for each 3-byte chunk to out[<first>..<last>].
- obf/fn_07: Writes 2 base64 characters for remaining 1-byte input to out[<first>..<last>].
- obf/fn_07: Writes 3 base64 characters for remaining 2-byte input to out[<first>..<last>].
- obf/fn_17: Writes data to out[<first>..<last>].

## Biến kiểm soát

| Cấu hình | Claim/item | Từ/claim | Claim bị lọc/item |
|---|---|---|---|
| plain | 7.7 | 9.0 | 0.3 |
| opt | 8.5 | 8.2 | 0.4 |
| obf | 11.3 | 7.5 | 0.5 |

## V1 — mã khôi phục

| Cấu hình | Compile | FEPR = 1 | FEPR trung vị |
|---|---|---|---|
| plain | 90.0% [69.9%–97.2%] (18/20) | 80.0% [58.4%–91.9%] (16/20) | 1.00 |
| opt | 75.0% [53.1%–88.8%] (15/20) | 35.0% [18.1%–56.7%] (7/20) | 0.20 |
| obf | 55.0% [34.2%–74.2%] (11/20) | 15.0% [5.2%–36.0%] (3/20) | 0.00 |

## RQ2 — bảng chéo E2 (mức hàm)

| | V1 đạt (FEPR = 1) | V1 không đạt |
|---|---|---|
| Giải thích sạch | 26 | 17 |
| Có claim contradicted | 0 | 7 |

Ô lệch đường chéo (nguồn case study):

- Giải thích sạch nhưng mã sai: obf/fn_04, obf/fn_05, obf/fn_07, obf/fn_08, obf/fn_11, obf/fn_14, obf/fn_19, opt/fn_05, opt/fn_07, opt/fn_08, opt/fn_10, opt/fn_11, opt/fn_12, opt/fn_15, plain/fn_13, plain/fn_17, plain/fn_18
- Mã đúng nhưng giải thích sai: —

## RQ5 — gán nhầm thuật toán (E3)

| Nhóm | Claim ALG | Gán nhầm (V1b contradicted) | Item có gọi tên thuật toán |
|---|---|---|---|
| classic | 15 | 6.7% [1.2%–29.8%] (1/15) | 63.2% [41.0%–80.9%] (12/19) |
| near_miss | 8 | 12.5% [2.2%–47.1%] (1/8) | 36.8% [19.1%–59.0%] (7/19) |
| custom | 2 | 0.0% [0.0%–65.8%] (0/2) | 16.7% [4.7%–44.8%] (2/12) |

## RQ3 — độ tự tin tự khai

AUROC của (1 − confidence) để dự báo claim contradicted: 0.54 (10 claim contradicted, 438 claim khác; 0,5 = ngẫu nhiên).

## So sánh cặp giữa cấu hình (McNemar chính xác, mức hàm)

| Cặp | Chỉ cấu hình 1 có hallucination | Chỉ cấu hình 2 | p |
|---|---|---|---|
| plain_vs_opt | 0 | 1 | 1.000 |
| opt_vs_obf | 2 | 4 | 0.688 |
| plain_vs_obf | 1 | 4 | 0.375 |
