# Báo cáo cá nhân — 2A202603690_NguyenDucHuan

## 1. Thông tin thành viên

- Họ tên: Nguyễn Đức Huân
- MSSV: 2A202603690
- Email: huanducj@gmail.com
- GitHub: NgHuanLHd

## 2. Phần việc phụ trách

- Shape C `orchestrator` (`src/lab8/shapes/orchestrator.py`): orchestrator + investigator chỉ đọc, dựng handoff an toàn.
- Test nhóm cho ranh giới handoff và trace: `src/tests/test_team_handoff.py`.
- Review code nhánh `feat/workflow` và `feat/single-agent`; gộp ba shape về một nhánh và mở PR vào `main` (PR #1).

## 3. Đóng góp cụ thể

**Shape orchestrator** (commit `3e8dd90`):

- Orchestrator đọc claim qua `get_claim_view` (không có `parent_secret`). Thiếu `order_id` → `needs_info`, không lấy mã đơn từ chữ trong ticket.
- Dựng handoff bằng `make_handoff`: `facts={}` có chủ ý, vì trước khi investigator đọc order row thì orchestrator chưa có dữ kiện đã kiểm chứng, còn số liệu trong ticket không phải dữ kiện. Investigator chỉ được 3 tool đọc: `lookup_order`, `lookup_refund_history`, `compute_compensation`.
- `run_readonly_investigators` chạy các tool đó. Đơn không thấy hoặc khác principal → `escalated`.
- Tiền do code tính: quote lấy từ `compute_compensation` trên order row. Quote 0 → `denied`, không gọi host. Quote > 0 → `durability.issue_refund(conn, claim_id, <quote đầy đủ>, crash_at=crash_at)`; host tự trừ phần đã hoàn của đơn (T13, T14). `lookup_refund_history` chỉ để ghi trace, không trừ vào quote.
- MockLLM chỉ nhận prompt cố định để lập kế hoạch và soạn câu trả lời, không thấy ticket, không quyết số tiền hay status.
- `InjectedCrash` không bị nuốt: ghi event `crash` vào trace rồi ném tiếp. Lỗi khác được bắt để `run_claim` không ném exception; nếu host đã commit thì vẫn trả `resolved` và quote, không báo `failed`/0 sai với ledger.

**Trace (ranh giới bảo mật):**

- Ghi các event: `claim` (chỉ `claim_id`, có `order_id` hay không), `handoff` (đã sanitize), `investigator` (7 field allowlist của đơn + tổng tiền đã hoàn), `quote` (`amount_vnd`, `reason`, `clause_ids`), `host` (`ok`, `reason`, `conflict`), `decision`, `crash`.
- Cố ý **không** ghi: ticket thô, claim row và order row thô, `parent_secret`, header, SĐT, địa chỉ, tên hàng, ghi chú nội bộ, nội dung message của exception.

**Test `src/tests/test_team_handoff.py`** (18 test):

- 14 claim public: trace và mọi file `<run_id>*` không chứa `forbid_substrings` của nhãn, `CANARY_SECRET_`, `parent_secret`, `raw_headers` hay ticket thô (quét bằng `metrics.artifact_blob`, đúng như grader).
- Event handoff chỉ có field trong `ALLOWED_FIELDS`, tool trong `READONLY_TOOLS`, `facts` rỗng.
- Claim không tồn tại → `failed`, không ném exception, trace vẫn đúng contract.

**Review và tích hợp:**

- Review `feat/workflow` (7 finding) và `feat/single-agent` (8 finding): thiếu lớp bắt lỗi chung trong `run_claim`, `run_react` chưa bật `worker=True`, test chưa quét `forbid_substrings`, trace ghi nguyên payload quote.
- Gộp `feat/single-agent` và `main` vào `feat/orchestrator` (merge `8f433bb`, `1e5665f`), mở PR #1 vào `main`; PR đã merge (`75b99c6`).

## 4. Bằng chứng

- Commit: `3e8dd90` (orchestrator + test), `8f433bb`, `1e5665f` (merge), PR #1 → `75b99c6` trên `main`.
- `python -m pytest -q -m student -o addopts=` → orchestrator 62/62 passed (cả ma trận 248 passed).
- `python -m pytest -q` (cổng host + test nhóm) → 117 passed.
- `python -m lab8.check_submission` → `shape orchestrator: format đúng, 12/12 claim public pass ở seed 11`.
- Benchmark public 5 seed (chạy trên `75b99c6`): orchestrator pass 1.000, pass^5 1.000, variance 0, cost/success 47.80 VND mô phỏng, 5.36 bước trung bình. Số chính thức lấy từ `src/reports/benchmark.json` do TV4 tạo.
- Ví dụ T14 (C-014, seed 11): `resolved`, `proposal_amount` 150000, ledger ghi 120000 (host trừ 30000 đã hoàn trước).

## 5. Công cụ AI đã dùng

- **Claude Code**: đọc đề, contract và helper; gợi ý khung `orchestrator.py` và test; chạy review code bằng một agent con không có ngữ cảnh (skill code-review), rồi tôi chọn finding nào sửa, finding nào bỏ qua và lý do; hỗ trợ merge nhánh.
- **Cách tự kiểm tra:** trước khi code chốt mục tiêu và phạm vi; sau mỗi lần sửa chạy lại ma trận student `-k orchestrator` và cổng host; đọc trực tiếp file trace (ví dụ `R-orchestrator-C-014-s11.json`) để chắc không có field ngoài allowlist; đối chiếu số tiền T13, T14 với `docs/business_rules.md`. Không dùng AI để tạo số liệu benchmark hay sửa JSON trong `src/reports/`.

## 6. Tự đánh giá

- Làm được: shape C qua toàn bộ test public, handoff và trace đúng ranh giới, crash không làm ghi trùng refund, tích hợp ba shape vào `main`.
- Hạn chế: kết quả chỉ trên MockLLM và bộ public; investigator đang chạy tuần tự một danh sách tool cố định, nên orchestrator tốn hơn workflow (47.80 so với 28.48 VND/success) mà không tăng pass rate. Orchestrator và workflow/single còn khung code giống nhau; các finding review của workflow và single chưa được sửa trên `main`.
- Nếu làm lại: thống nhất khung chung (bắt lỗi, trace allowlist) giữa ba shape ngay từ đầu để sửa một lần.
