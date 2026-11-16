# Báo cáo nhóm — Lab 8 LogiX-VN

Tối đa 5 trang ngoài phụ lục. Số liệu lấy từ file trong `src/reports/`, không chép tay từ terminal.

## 1. Thông tin nhóm

- Tên nhóm: D2HL (lớp L3A)
- Thành viên: xem `TEAM.md` (Vũ Gia Linh, Nguyễn Thị Duyên, Nguyễn Đức Huân, Võ Thị Kim Huyền)
- Repo: https://github.com/NgHuanLHd/K5-L3A-DAY08-NhomD2HL-FromWorkflowsToAgents, nhánh `main`
- Commit chốt (trùng `report/team/decision_adr.md`): `0bff6f0`

## 2. Mục tiêu và cách tiếp cận

Bài toán: xử lý claim hoàn phí vận chuyển của LogiX-VN bằng bốn kiến trúc có cùng chữ ký `run_claim`, rồi chọn kiến trúc **ít tự chủ nhất mà vẫn làm được việc** dựa trên số đo. Nhóm thống nhất từ đầu một nguyên tắc chung cho cả ba shape tự viết: số tiền, approval và chống ghi trùng do **code** quyết; model (MockLLM) chỉ đọc và soạn chữ; chữ trong ticket là dữ liệu người dùng, không phải lệnh và không phải nguồn sự thật.

Chia việc theo gợi ý nhóm 4 người trong `TEAM.md`, mỗi người một nhánh và một file shape riêng để tránh xung đột:

| Thành viên | Vai | Nhánh |
| --- | --- | --- |
| Vũ Gia Linh | Workflow (A) + integration | `feat/workflow` |
| Nguyễn Thị Duyên | Single agent ReAct (B) | `feat/single-agent` |
| Nguyễn Đức Huân | Orchestrator + handoff (C) | `feat/orchestrator` |
| Võ Thị Kim Huyền | Ledger + evaluation | `feat/ledger-eval` |

Thứ tự làm: workflow trước (khung đơn giản nhất: đọc claim, `needs_info`, `escalated`, gọi host), single và orchestrator làm song song, dùng `swarm_reference.py` làm mẫu cho cách gọi `finish()` và trace. Ledger/eval viết test crash và retry khi đã có shape, rồi chạy crash suite, benchmark 4 shape × 5 seed và ablation. Mỗi nhánh được review code trước khi gộp; `feat/orchestrator` được dùng làm nhánh đệm để gộp các nhánh, chạy lại toàn bộ kiểm tra rồi mới đưa lên `main` qua PR (#1, #2, #3).

## 3. Giải pháp

### Phần chung của ba shape

- Đọc claim bằng `get_claim_view` (không `SELECT *`), nên `parent_secret` và header không vào bộ nhớ của shape. Thiếu `order_id` → `needs_info`, không lấy mã đơn từ chữ trong ticket.
- Đơn đọc qua `lookup_order` trong phạm vi principal; không thấy đơn hoặc khác principal → `escalated`.
- Tiền do `compute_compensation` tính từ order row và policy hiện hành. Quote 0 → `denied`, không gọi host.
- Quote > 0 → `durability.issue_refund(conn, claim_id, <quote đầy đủ>, crash_at=crash_at)`. Không tự trừ phần đã hoàn: host tự trừ theo trần đơn (T13 `denied` + `policy_denied`; T14 quote 150.000, ledger 120.000). Host từ chối → `denied` với `proposal_amount` là quote; `amount_conflict` → `failed`.
- `InjectedCrash` không bị nuốt: ghi event `crash` vào trace rồi ném tiếp, để lần chạy lại dựa vào ledger và khóa `refund:{claim_id}` mà không tạo refund thứ hai.
- Mọi nhánh return đều đi qua `finish()`, nên trace luôn được ghi trong chính lần chạy với `run_id` đúng.

### Ranh giới code / model theo từng shape

| Shape | Đọc gì | Model làm gì | Ai quyết tiền và gọi host |
| --- | --- | --- | --- |
| A `workflow` | claim view → order → quote, các bước cố định | Chỉ soạn câu trả lời sau khi host trả kết quả | Code của shape |
| B `single` | Vòng `run_react` tối đa 8 bước; `decide` chỉ chọn tool đọc: `lookup_order` → `lookup_refund_history` → `compute_compensation` | Một lời gọi "react" mỗi bước, chỉ nhận tên tool vừa chạy (không thấy ticket); không bao giờ trả `issue_refund` | Code của shape, **sau** vòng lặp |
| C `orchestrator` | Orchestrator đọc claim view; investigator đọc đơn, lịch sử refund, quote | Một lời gọi lập kế hoạch với prompt cố định (không có ticket) và một lời soạn câu trả lời | Orchestrator; investigator không có tool ghi |

### Handoff của orchestrator

Handoff dựng bằng `make_handoff` và đi qua `sanitize`: chỉ còn các field allowlist `handoff.v1` (`contract_version`, `request_id`, `claim_id`, `principal_scope`, `task`, `facts`, `allowed_tools`, `max_output_tokens`). `allowed_tools` chỉ gồm 3 tool đọc. `facts` cố ý để rỗng: trước khi investigator đọc order row, orchestrator chưa có dữ kiện đã kiểm chứng, còn số ngày trễ trong ticket không phải dữ kiện. Nhóm không dùng tóm tắt bằng LLM để thay redaction.

### Trace

Trace ghi: `claim` (chỉ `claim_id` và cờ có `order_id`), handoff đã sanitize (C), order đã lọc theo `ORDER_FIELDS` (mã đơn, trạng thái, số ngày trễ, phí ship, số tiền đã trả, hư hỏng đã xác minh, hãng vận chuyển), tổng tiền đã hoàn (B, C), `quote`, `host` (`ok`, `reason`), `crash` nếu có, `decision`. Cố ý **không** ghi: ticket thô (có thể chứa injection như "ignore policy"), claim row và order row thô, `parent_secret`, header, số điện thoại, địa chỉ, tên hàng, ghi chú nội bộ.

## 4. Kết quả

### Bộ public (`src/reports/benchmark.json`, 14 claim × 5 seed `11,22,33,44,55`, mỗi trial một SQLite mới)

| Shape | Pass rate | Pass^5 | Seed min–max | Variance | Cost/success (VND mô phỏng) | Mean / p95 steps | Model / tool calls mỗi trial |
| --- | ---: | ---: | --- | ---: | ---: | --- | --- |
| A workflow | 1.000 | 1.000 | 1.000–1.000 | 0 | 28.48 | 4.36 / 5 | 0.64 / 2.79 |
| B single | 1.000 | 1.000 | 1.000–1.000 | 0 | 38.58 | 6.14 / 7 | 4.21 / 3.64 |
| C orchestrator | 1.000 | 1.000 | 1.000–1.000 | 0 | 47.80 | 5.36 / 6 | 2.00 / 4.64 |
| D swarm (có sẵn) | 0.986 | 0.929 | 0.929–1.000 | 0.000816 | 49.57 | 2.80 / 3 | 3.00 / 4.66 |

Trial fail duy nhất là `R-swarm-C-002-s55`: ở seed 55 swarm tin số ngày trễ trong ticket (5 ngày) thay vì order row (2 ngày) và trả 20.000 cho một claim lẽ ra `denied`. Ba shape nhóm viết từ chối đúng T02 ở mọi seed vì không đọc số trong ticket.

### Durability, policy và bảo mật

- Crash suite (`src/reports/crash.json`): `crash_safety` **20/20**.
- Ma trận student T01–T14: 248/248 passed (62 cho mỗi shape). Cổng host và test nhóm `python -m pytest -q`: 129 passed.
- Test nhóm bổ sung: crash ở cả 3 điểm (`before_effect`, `after_effect_before_checkpoint`, `after_checkpoint`) rồi resume trên cả ba shape vẫn đúng 1 refund và 1 audit `refund_committed`; retry khi thiếu approval không tạo refund và có `policy_denied`; trace của 14 claim không chứa `forbid_substrings`, `CANARY_SECRET_` hay ticket thô.
- Tái lập: chạy lại hai lệnh crash và benchmark trên commit chốt cho cùng mọi trial và chỉ số (chỉ khác ở chữ số thập phân thứ 13 trở đi của tổng cost do cộng số thực).

### Tự kiểm trên `student_drop/`

Mỗi shape 200 trial (40 claim × 5 seed): `error_trials` = 0, `leak_suspect_trials` = 0 cho cả ba shape nhóm viết; workflow ra resolved 90, denied 95, needs_info 5, escalated 10. Bộ này không có nhãn nên nhóm **không** tính pass rate hidden; điểm hidden do grader của giảng viên chấm. File selfcheck để ở máy, không commit.

Quyết định kiến trúc và lý do: xem `report/team/decision_adr.md` (chọn **workflow**: cùng độ đúng, rẻ nhất, ít tự chủ nhất). Phiếu nghiên cứu và ablation: xem `report/team/research_card.md` (R4, ablation workflow ↔ orchestrator).

## 5. Khó khăn và cách xử lý

| Khó khăn | Biểu hiện | Cách xử lý |
| --- | --- | --- |
| Xung đột `TEAM.md` khi gộp nhánh | Mỗi người điền dòng của mình trên một bản `TEAM.md` khác nhau; 4 lần gộp đều báo `CONFLICT (content): Merge conflict in TEAM.md` | Dùng `feat/orchestrator` làm nhánh đệm, giữ bảng thành viên đầy đủ và gộp từng dòng đóng góp; chạy lại test và `check_submission` trước khi mở PR vào `main` |
| Force-push lên nhánh đã chia sẻ | `feat/workflow` và `feat/ledger-eval` bị force-push, hash commit đổi (`b335c50` → `204619f`) dù nội dung như cũ | So nội dung bằng `git diff` trước khi gộp; merge PR bằng merge commit (không squash) và kiểm cả 4 hash trong bảng đóng góp đều nằm trên `main` |
| Hash trong ADR | Hash ban đầu (`133d97f`) là commit trước khi điền ADR, nằm trên nhánh riêng | Sau khi mọi thứ lên `main`, cập nhật thành commit chốt `0bff6f0` theo thứ tự trong `SUBMISSION.md` |
| Lỗi in tiếng Việt trên Windows | Đọc file claim bằng Python trên PowerShell báo `UnicodeEncodeError: 'charmap' codec can't encode characters` (console cp1252) | Chạy với `PYTHONIOENCODING=utf-8` |
| Cài đặt môi trường và git | Thành viên gặp lỗi cài Python và thao tác git (theo báo cáo cá nhân) | Làm theo `src/README.md` và `docs/troubleshooting.md`; mỗi người làm trên nhánh riêng, chỉ sửa file shape của mình |
| Review code | Review bằng skill `code-review` tìm ra: thiếu lớp bắt lỗi chung trong `run_claim`, gửi ticket thô vào model, test chưa quét `forbid_substrings` | Orchestrator đã sửa trước khi merge; các finding còn lại của workflow và single được ghi ở mục 7 |

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong `TEAM.md` (bảng đóng góp) và báo cáo cá nhân trong `report/team/`:

| Thành viên | Commit chính | Test |
| --- | --- | --- |
| Vũ Gia Linh | `204619f` (workflow) | `tests/test_team_workflow.py` |
| Nguyễn Thị Duyên | `fe9de32`, `9389e29` (single) | `tests/test_team_single.py` |
| Nguyễn Đức Huân | `3e8dd90` (orchestrator), gộp nhánh qua PR #1–#3 | `tests/test_team_handoff.py` |
| Võ Thị Kim Huyền | `133d97f` (test ledger, benchmark, crash), ADR, research card | `tests/test_team_ledger.py` |

## 7. Hạn chế và hướng cải thiện

- **MockLLM không phải model sản xuất**, latency là `unavailable`, cost là giá mô phỏng trong `config/pricing.yaml`, không phải hóa đơn API. Pass rate 1.000 chỉ đo trên 14 claim public; pass rate hidden do giảng viên chấm.
- **Shape B chưa thật sự tự chủ:** `decide` của single là một kịch bản cố định, model không chọn tool. Vì vậy so sánh A với B ở đây chủ yếu đo chi phí của các lời gọi model thêm vào, chưa đo được giá trị của ReAct.
- **Ablation chưa tách được một biến:** đổi workflow sang orchestrator đồng thời thêm lời gọi lập kế hoạch và một tool đọc, nên phần cost tăng thêm (+68%) gắn với thiết kế orchestrator này, không thể quy hoàn toàn cho topology.
- **Finding review chưa sửa ở workflow và single:** chưa có lớp bắt lỗi chung trong `run_claim` (lỗi SQLite hay ghi trace có thể làm hàm ném exception), single chưa bật `worker=True` cho `run_react`, model draft chỉ được gọi ở nhánh có gọi host, trace ghi nguyên payload quote. Nếu sửa, phải chạy lại benchmark và crash rồi cập nhật số và hash trong ADR.
- **Điều kiện làm kết luận thay đổi:** bộ hidden có loại claim mà luật cố định không mã hóa được (workflow tụt dưới 0.75 trong khi single hoặc orchestrator giữ được); cần nhiều investigator song song trên nhiều nguồn dữ liệu, khi latency trở thành tiêu chí; hoặc giá model giảm đến mức chênh 19 VND/success không còn đáng kể so với lợi ích tách quyền.

## 8. Tài liệu tham khảo

- Đề bài và tài liệu của lab: `README.md`, `RUBRIC.md`, `SUBMISSION.md`, `docs/business_rules.md`, `docs/contracts.md`, `docs/architecture.md`, `docs/metrics.md`.
- Shape tham chiếu: `src/lab8/shapes/swarm_reference.py`.
- Nguồn của research card (R4): *Rethinking Evaluation of MAS Efficiency*, EMNLP 2026, trong thư viện tham khảo của buổi lý thuyết (slide 68–69).
- Công cụ AI các thành viên đã dùng (Claude Code, Cursor) và cách tự kiểm tra: ghi trong từng báo cáo cá nhân.
