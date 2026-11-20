# Tổng hợp kết quả

Sinh bởi `python -m vera.report.summary`. Chi tiết từng lượt: `data/runs/<lượt>/results.md`. Mọi tỉ lệ kèm khoảng tin cậy Wilson 95%.

## Các lượt chạy

| Lượt | Mô tả | Item đúng schema |
|---|---|---|
| E1 | Lượt chính — qwen2.5-coder:7b, prompt p3 | 58/60 |
| E1_p2 | Ablation prompt p2 (có câu ví dụ) — qwen2.5-coder:7b | 60/60 |
| E1_qwen3 | Model thứ hai — qwen3:8b, tắt thinking, prompt p3 | 50/60 |
| E1_llm4decompile | Baseline V1 — LLM4Decompile-Ref v2 6.7B (chỉ sinh mã) | 60/60 |

## RQ1 — HR_strict (hallucination) theo cấu hình

| Lượt | Tổng | plain | opt | obf |
|---|---|---|---|---|
| E1 | 6.4% [4.4%–9.3%] (25/389) | 7.7% [4.1%–14.0%] (9/117) | 5.1% [2.4%–10.7%] (6/118) | 6.5% [3.6%–11.5%] (10/154) |
| E1_p2 | 5.0% [3.2%–7.7%] (19/378) | 3.6% [1.4%–9.0%] (4/110) | 8.0% [4.3%–14.6%] (9/112) | 3.8% [1.8%–8.1%] (6/156) |
| E1_qwen3 | 2.2% [1.2%–4.1%] (10/448) | 0.6% [0.1%–3.6%] (1/154) | 1.5% [0.4%–5.2%] (2/136) | 4.4% [2.2%–8.9%] (7/158) |

## RQ1 — HR_strict theo nhóm hàm

| Lượt | classic | near_miss | custom |
|---|---|---|---|
| E1 | 5.9% [3.0%–11.2%] (8/136) | 11.2% [6.8%–17.9%] (14/125) | 2.3% [0.8%–6.7%] (3/128) |
| E1_p2 | 7.8% [4.3%–13.7%] (10/129) | 4.5% [2.1%–9.6%] (6/132) | 2.6% [0.9%–7.3%] (3/117) |
| E1_qwen3 | 2.9% [1.2%–6.5%] (5/174) | 2.4% [0.9%–6.0%] (4/168) | 0.9% [0.2%–5.2%] (1/106) |

## V1 — FEPR = 1 (mã khôi phục khớp 50/50 vector)

| Lượt | plain | opt | obf |
|---|---|---|---|
| E1 | 45.0% [25.8%–65.8%] (9/20) | 25.0% [11.2%–46.9%] (5/20) | 0.0% [0.0%–16.1%] (0/20) |
| E1_p2 | 60.0% [38.7%–78.1%] (12/20) | 30.0% [14.5%–51.9%] (6/20) | 0.0% [0.0%–16.1%] (0/20) |
| E1_qwen3 | 80.0% [58.4%–91.9%] (16/20) | 35.0% [18.1%–56.7%] (7/20) | 15.0% [5.2%–36.0%] (3/20) |
| E1_llm4decompile | 45.0% [25.8%–65.8%] (9/20) | 15.0% [5.2%–36.0%] (3/20) | 0.0% [0.0%–16.1%] (0/20) |

## RQ2 — bảng chéo E2 (mức hàm)

| Lượt | sạch & V1 đạt | sạch & V1 hỏng | sai & V1 đạt | sai & V1 hỏng |
|---|---|---|---|---|
| E1 | 6 | 29 | 8 | 15 |
| E1_p2 | 9 | 32 | 9 | 10 |
| E1_qwen3 | 26 | 17 | 0 | 7 |

## RQ5 — gán nhầm thuật toán (claim ALG bị V1b bác bỏ)

| Lượt | classic | near_miss |
|---|---|---|
| E1 | 22.2% [6.3%–54.7%] (2/9) | 55.6% [26.7%–81.1%] (5/9) |
| E1_p2 | 0.0% [0.0%–65.8%] (0/2) | — |
| E1_qwen3 | 6.7% [1.2%–29.8%] (1/15) | 12.5% [2.2%–47.1%] (1/8) |

## RQ3 — dự báo claim sai

- E1 (temperature 0): AUROC của 1 − confidence = 0.53
- E4 (temperature 0,7, 5 lần, cấu hình obf):

| Tín hiệu dự báo claim contradicted | AUROC [95% bootstrap] |
|---|---|
| 1 − self-consistency | 0.63 [0.55–0.70] |
| 1 − confidence tự khai | 0.71 [0.63–0.79] |
Độ nhất quán trung bình: claim contradicted 0.17, claim khác 0.33. AUROC 0,5 = ngẫu nhiên.

## E6 — độ ổn định (temperature 0, 3 lần)

| Lần lặp | HR_strict |
|---|---|
| 0 | 0.07 |
| 1 | 0.07 |
| 2 | 0.09 |
Phương sai HR_strict giữa các lần: 4.3103650627258155e-05; khoảng [0.07179487179487179, 0.08585858585858586]. 21/30 hàm có HR giống hệt ở mọi lần.

## Kiểm soát prompt

- E1_p2: claim chép ví dụ 1.3% [0.6%–3.1%] (5/378), trong đó bị bác bỏ 80.0% [37.6%–96.4%] (4/5)
- E1: claim chép ví dụ 0.8% [0.3%–2.2%] (3/389), trong đó bị bác bỏ 0.0% [0.0%–56.2%] (0/3)

## RQ4 — độ chính xác bộ kiểm chứng (gold set 120 claim, E1)

- Cohen's kappa giữa 2 người gán nhãn: 0.93 (4 bất đồng / 120)
- Precision nhãn contradicted: 88% [75%–100%]
- Recall nhãn contradicted: 52% [37%–67%] tính thẳng trên mẫu; có trọng số tầng 21,5% [15,7%–31,3%] (`data/revision_g1.json`, góp ý G1)
- Precision nhãn supported + verified: 83% [72%–93%]
- HR_strict thô 6.4% → HR hiệu chỉnh 26.2% [18.3%–34.7%]
- Phân tích lỗi: `data/gold/E1/analysis.md`

## Cổng V3 (self-test)

- Bỏ sót hằng: -O0 5%, -O2 5% (ngưỡng ≤ 5%)
- Ủng hộ nhầm thuật toán: 0/1290
