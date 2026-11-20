# Nhật ký thay đổi ground truth

Ground truth (manifest, mã nguồn corpus, vector I/O, binary) được chốt bằng tag git `ground-truth-v1`
ngày 2026-09-24, TRƯỚC lượt chạy chính E1. Kiểm tra trước khi chốt: `python tools/check_manifests.py`,
`python -m vera.corpus.check`.

Mọi thay đổi sau tag phải ghi vào đây: ngày, file, lý do, và đã thấy output LLM hay chưa.

| Ngày | Thay đổi | Lý do | Đã thấy output E1? |
|---|---|---|---|
| 2026-09-24 | Chốt `ground-truth-v1` | — | Chưa (chỉ mới có E0 trên 5 hàm) |
| 2026-10-02 | `fn_19`: mô tả tham chiếu thêm 2 câu (độ dài đầu ra, không có hằng đặc trưng, tính tự đảo) — chỉ trường `description` | Đủ 3–5 câu theo hướng dẫn của thầy; phát hiện khi rà soát tiêu chí. Không đổi mã nguồn, vector, binary, nhãn hay metric | Có (sau E1); thay đổi không chạm tới phần được chấm |
