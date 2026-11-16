# Báo cáo cá nhân — 2A202603698_NguyenThiDuyen

## 1. Thông tin thành viên

- Họ tên: Nguyễn Thị Duyên
- MSSV: 2A202603698
- Email: [nguyenduyen.260903@gmail.com](mailto:nguyenduyen.260903@gmail.com)
- GitHub: duyen26912

## 2. Phần việc phụ trách

Shape B — single (ReAct). Viết `src/lab8/shapes/single.py` và test `src/tests/test_team_single.py`, làm trên nhánh `feat/single-agent`.

## 3. Đóng góp cụ thể

- Commit chính: `fe9de32` (viết shape single và test), `9389e29` (bổ sung test, ghi lịch sử hoàn tiền vào trace), trên nhánh `feat/single-agent`.
- Test đã thêm: `src/tests/test_team_single.py` (43 test), gồm:
  - `test_single_matches_expected_labels`: 14 claim public khớp nhãn `expected`, trace không lộ secret.
  - `test_single_decide_never_returns_write_tool`: `decide` không bao giờ trả tool ghi.
  - `test_single_stops_within_8_steps`: truyền `max_steps=8`, dừng trong tối đa 8 bước.
  - `test_single_early_returns_skip_loop_and_write_trace`: `needs_info` và claim không tồn tại không chạy vòng ReAct, vẫn ghi trace.
  - `test_single_crash_reraises_then_resume_pays_once`: crash rồi chạy lại vẫn 1 refund, 1 audit.
- Quyết định kỹ thuật:
  - Dùng `run_react` với `max_steps=8`. `decide` chỉ chọn tool đọc (`lookup_order` → `lookup_refund_history` → `compute_compensation`), không bao giờ trả `issue_refund`.
  - Sau vòng lặp, code của shape quyết định trạng thái và gọi `issue_refund`, model không chọn số tiền.
  - Tiền do `compute_compensation` tính từ order row, bỏ qua mọi con số trong ticket.
  - Truyền quote đầy đủ, không tự trừ phần đã hoàn. `lookup_refund_history` chỉ để ghi trace.
  - `decide` giữ state riêng, vì `run_react` chỉ trả kết quả tool cuối.
  - Truyền `crash_at`, ghi trace rồi raise lại `InjectedCrash`. Mọi nhánh trả kết quả đều qua `finish()`.

## 4. Bằng chứng

- Commit `fe9de32`, `9389e29` trên nhánh `feat/single-agent`.
- `python -m pytest -q -m student -o addopts= -k "single]"`: 62 passed.
- `python -m pytest -q`: 99 passed.
- Run id: `R-single-C-001-s11` (`resolved`, 35.000), `R-single-C-002-s11` (T02, `denied`), `R-single-C-014-s11` (T14, quote 150.000, thực hoàn 120.000).

## 5. Công cụ AI đã dùng

 Hỗ trợ viết `single.py` và test theo khung của `workflow.py`, code review bằng skill `/code-review`. Tự kiểm tra bằng cách chạy ma trận student và cổng host, đọc lại code để chắc `decide` không gọi tool ghi, không tự trừ tiền đã hoàn, không nuốt `InjectedCrash`, không ghi ticket vào trace.

## 6. Tự đánh giá

- Single đạt 62/62 ở ma trận student, có 43 test, cổng host xanh. 
- Khó khăn: lỗi cài đặt Python, thao tác git, và lý thuyết về ReAct, idempotency, crash/resume chưa nắm chắc. 
- Cần học thêm lý thuyết phần này để tự viết và giải thích code mà không phụ thuộc vào AI.
