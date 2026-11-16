# Research card

File này nằm cố định ở `report/team/research_card.md`; `python -m lab8.check_submission` đọc cột "Nhóm điền" bằng máy.

Phần này nối tiếp phần mini research ở buổi lý thuyết (slide 62–63). Chọn **một** câu R1–R4, điền 6 dòng, rồi biến nó thành **một ablation** chạy được trong lab: giữ nguyên model (MockLLM), tool, seed, corpus và giá, chỉ thay đổi một biến.

| Câu | Nguồn (thư viện tham khảo, slide 68–69) | Câu hỏi gợi ý cho lab |
| --- | --- | --- |
| R1 · Scaling | Google Research 2026, *Towards a Science of Scaling Agent Systems* | Task claims chủ yếu tuần tự hay song song được? Dự đoán thêm investigator sẽ làm pass rate và cost/success thay đổi thế nào. |
| R2 · Failure taxonomy | MAST, NeurIPS 2025, *Why Do Multi-Agent LLM Systems Fail?* | Các trial fail của swarm (seed 55) thuộc nhóm nào: lỗi giao việc, lệch mục tiêu, hay lỗi kiểm chứng? |
| R3 · Architecture choices | AgentArch, AACL 2026 | Nếu đổi topology mà giữ nguyên mọi thứ khác, biến nào phải cố định để kết luận còn đúng? |
| R4 · Evaluation confounders | EMNLP 2026, *Rethinking Evaluation of MAS Efficiency* | Làm sao chứng minh chênh lệch giữa A/B/C/D là do topology, không phải do prompt, tool hay seed? |

## Phiếu của nhóm

Điền vào cột cuối. Không xóa hai cột đầu.

| Field | Hướng dẫn | Nhóm điền |
| --- | --- | --- |
| CÂU | R1 / R2 / R3 / R4 | R4 · Evaluation confounders |
| SOURCE | Paper/blog, năm, URL, loại bằng chứng (benchmark, production report, blog kinh nghiệm) | EMNLP 2026, *Rethinking Evaluation of MAS Efficiency* (thư viện tham khảo slide 68–69); loại bằng chứng: nghiên cứu thực nghiệm về phương pháp đánh giá |
| CLAIM | Một kết luận gốc của nguồn. Không viết rộng hơn phạm vi paper | Chênh lệch hiệu quả giữa hệ multi-agent và single-agent thường bị lẫn với biến gây nhiễu (prompt, tool, ngân sách token, seed); chỉ quy chênh lệch cho topology khi các biến đó được giữ cố định |
| BOUNDARY | Model / dataset / setup giới hạn kết luận đó | Kết luận của paper dựa trên LLM thật và benchmark của họ; lab này dùng MockLLM theo seed, 14 claim public, giá mô phỏng, nên chỉ kiểm được phần phương pháp (cố định biến), không kiểm được độ lớn hiệu ứng trên model thật |
| HYPOTHESIS | Nếu đổi shape A→B (hoặc bật/tắt một thành phần), metric X sẽ đổi theo hướng nào, khoảng bao nhiêu | Đổi workflow (A) sang orchestrator (C) với cùng tool tính tiền và cùng host: pass rate không đổi (chênh 0), vì số tiền do `compute_compensation` quyết ở cả hai; cost/success tăng 50–100% vì C thêm lời gọi model lập kế hoạch và một tool đọc lịch sử refund |
| METHOD | Biến giữ cố định: model, tools, seed, corpus, giá, evaluator. Biến duy nhất được thay đổi: … | Giữ cố định: MockLLM, `compute_compensation` và host `durability.issue_refund`, seed 11,22,33,44,55, corpus `data/public_claims.jsonl`, `config/pricing.yaml`, evaluator `metrics.trial_pass`, SQLite mới cho mỗi trial. Biến duy nhất được thay đổi: topology (workflow tuần tự ↔ orchestrator + investigator chỉ đọc) |
| FAILURE / METRIC | Một lỗi dự kiến và cách đo nó: pass rate, pass^5, variance, cost/success, leak, bypass | Lỗi dự kiến: quy chênh lệch cost cho topology trong khi thật ra do số lời gọi model. Đo: pass rate, pass^5, variance, cost/success, mean_model_calls, mean_tool_calls; chạy lại cùng lệnh phải ra cùng số (nếu khác thì kết quả bị nhiễu bởi seed hoặc trạng thái DB) |

## Kết quả ablation

- Lệnh đã chạy (copy nguyên văn): `python -m lab8.benchmark --shapes workflow,orchestrator --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/ablation_r4_topology.json`
- Run id / file report: `src/reports/ablation_r4_topology.json` (140 trial, ví dụ R-workflow-C-014-s55 và R-orchestrator-C-014-s55); khớp từng số với `src/reports/benchmark.json`
- Kết quả so với hypothesis (đúng / sai / không kết luận được), kèm số liệu: Đúng. Pass rate 1.000 ở cả hai, pass^5 1.000, variance 0. Cost/success 28.48 → 47.80 VND (+68%, nằm trong khoảng dự đoán 50–100%). Chênh lệch giải thích được hoàn toàn bằng số lời gọi: model 0.64 → 2.00 mỗi trial, tool 2.79 → 4.64 mỗi trial. Chạy lại cho cùng số, nên chênh lệch không đến từ seed hay trạng thái DB. Kết luận: trên task này, topology chỉ thêm chi phí chứ không thêm độ đúng.
- Giới hạn: MockLLM không phải model sản xuất, latency là `unavailable`.

Muốn đi xa hơn một ablation để lấy điểm cộng thì xem [docs/bonus_topics.md](../../docs/bonus_topics.md).
