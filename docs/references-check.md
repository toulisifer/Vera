# Kiểm tra tài liệu tham khảo (02/10/2026)

Kết quả tra bản gốc, dùng khi viết báo cáo / proposal mục 2.

| # | Tài liệu | Kết quả |
|---|---|---|
| [1] | Nishizaka, Fujiwara, Shimizu, Kato, Sugiyama, "Towards LLM-Resistant Software Protection: Agent Failure Patterns in CTF Reverse Engineering", NDSS BAR 2026 (San Diego, 02/2026) | Có thật. Tên đầy đủ: Ryutaro, Yudai, Takuya, Kazushi, Yuichi. 3 agent, 24 bài CTF RE; 4 điểm yếu: training bias, over-trust in observations, context limitation, plan persistence. https://www.ndss-symposium.org/wp-content/uploads/bar2026-58.pdf |
| [2] | Elastic Security Labs — C. François, D. Stepanic, J. Y. Chan, "The Cost of Understanding: LLM-Driven Reverse Engineering vs Iterative LLM Obfuscation", 21/04/2026 | Có thật. **"40%" là tỉ lệ GIẢI ĐƯỢC (success), không phải failure**: Claude Opus 4.6 giải 40% trong 20 task đánh giá được (22 crackme Tigress, 2 bị treo). Theo pha: 12,5% / 50% / 38,5% / 0%. Proposal ghi "40% task-level failure" → **phải sửa** thành "solved 40% of tasks (task-level success), i.e. failed on ~60%". Đo theo nhiệm vụ, không theo claim. |
| [4] | Hu, Shang, Shi, Cheng, Zhang, Li, Yang, Zhang, Lo, "Can LLMs Deobfuscate Binary Code? ...", arXiv:2604.08083 (09/04/2026) | Có thật, khớp. Benchmark BinDeObfBench. |
| mới | Xie, Zhang, Jiang, Xu, Tan, Zhang, "ReSym: Harnessing LLMs to Recover Variable and Data Structure Symbols from Stripped Binaries", ACM CCS 2024, pp. 4554–4568, doi:10.1145/3658644.3670340 | Distinguished Paper. Fine-tune 2 LLM + Prolog cross-check. Khác VeRA: kiểm chéo dự đoán tên/kiểu giữa các hàm, không kiểm claim ngôn ngữ tự nhiên bằng thực thi. |
| mới | Min et al., "FActScore", EMNLP 2023 | Cần chép trích dẫn chuẩn khi viết. |
| mới | Collberg, Thomborson, Low, "A Taxonomy of Obfuscating Transformations", TR #148, Univ. Auckland, 1997 | Nguồn chuẩn cho opaque predicate. Cần xác nhận khi viết. |

Công trình gần cần đọc thêm cho research gap (tìm thấy khi tra):
- "Reveree: Diagnosing LLM Reverse-Engineering Agents", arXiv:2609.01185
- "SoK: AI-Augmented Binary Reversing", arXiv:2606.17398
- "When LLM Decompilers Recompile More and Preserve Less", arXiv:2609.05370 (gần với E2/V1)
