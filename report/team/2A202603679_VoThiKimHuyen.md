# Báo cáo cá nhân — 2A202603679_VoThiKimHuyen

## 1. Thông tin thành viên

- Họ tên: Võ Thị Kim Huyền
- MSSV: 2A202603679
- Email: vothikimhuyenvta@gmail.com
- GitHub: copengoknghek

## 2. Phần việc phụ trách

Ledger + evaluation (nhánh `feat/ledger-eval`):

- Kiểm chứng ledger an toàn khi crash và khi retry trên cả ba shape nhóm viết (workflow, single, orchestrator).
- Chạy crash suite 20 điểm, benchmark 4 shape × 5 seed, và ablation cho research card.
- Điền `report/team/decision_adr.md` và `report/team/research_card.md` bằng số liệu từ các report do công cụ sinh ra.
- Tự kiểm hidden (CP5): copy `student_drop/` từ pack coach, chạy benchmark selfcheck (không commit dữ liệu ẩn).

## 3. Đóng góp cụ thể

- Commit `133d97f`: thêm `src/tests/test_team_ledger.py` (12 test), `src/reports/benchmark.json`, `src/reports/crash.json`.
- `test_crash_then_resume_leaves_one_refund`: crash ở cả ba điểm `before_effect`, `after_effect_before_checkpoint`, `after_checkpoint` trên cả ba shape nhóm viết (9 trường hợp), rồi resume trên cùng DB. Kiểm sau resume còn đúng một dòng `refund_ledger` 35.000 VND và một audit `refund_committed`; với `before_effect` thì kiểm ledger trống ngay sau crash. Ma trận public chỉ crash ở một điểm (T12, `after_effect_before_checkpoint`), nên test này phủ thêm hai điểm còn lại.
- `test_retry_without_approval_never_refunds`: xóa approval của C-001 rồi chạy hai lần trên mỗi shape. Kiểm không có refund, không có `refund_committed`, có audit `policy_denied`, và `CANARY_SECRET_PARENT_C-001` không lộ trong kết quả lẫn trace.
- Quyết định kỹ thuật: đề xuất chọn `workflow` trong ADR vì ba shape nhóm viết cùng pass 1.000 nhưng workflow có cost/success thấp nhất (28.48 VND so với 38.58 và 47.80) và ít tự chủ nhất.
- Research card R4: thiết kế ablation chỉ đổi topology (workflow ↔ orchestrator), giữ nguyên tool tính tiền, host, seed, corpus và giá.
- Tự kiểm hidden sau khi nhận `student_drop/`: `hidden_selfcheck.json` (workflow, single, orchestrator) và `hidden_selfcheck_workflow.json` (workflow — shape trong ADR). Mỗi shape 200 trial (40 claim × 5 seed); trong JSON: `error_trials` = 0, `leak_suspect_trials` = 0. Bộ không nhãn nên không có pass rate; chỉ kiểm runtime và nghi lộ secret.

## 4. Bằng chứng

- `python -m pytest -q` (chạy trong `src/`): 129 passed.
- `python -m pytest -q -m student -o addopts=`: 248 passed.
- `python -m lab8.check_submission`: 0 FAIL (shapes, benchmark, crash, ADR, research card, bảng đóng góp).
- `python -m lab8.crash_test --count 20 --out reports/crash.json`: `crash_safety 20/20`.
- `src/reports/benchmark.json`: workflow 1.000 / 1.000 / var 0 / 28.48 VND; swarm 0.986 / 0.929, trial fail duy nhất `R-swarm-C-002-s55`.
- `src/reports/ablation_r4_topology.json`: workflow 28.48 → orchestrator 47.80 VND/success, pass rate cùng 1.000.
- Hidden selfcheck (local, không commit): `reports/hidden_selfcheck.json` và `hidden_selfcheck_workflow.json`; workflow: `status_counts` resolved 90, denied 95, needs_info 5, escalated 10; `error_trials` 0, `leak_suspect_trials` 0 (cả 3 shape cũng 0/0 trong `hidden_selfcheck.json`).

## 5. Công cụ AI đã dùng

- Cursor (agent): đọc đề, đọc code host (`durability.py`, `crash_test.py`, `check_submission.py`), gợi ý nội dung test ledger và soạn nháp ADR, research card.
- Cách tự kiểm tra: mọi số liệu trong ADR và research card được lấy từ output thật của `lab8.benchmark` và `lab8.crash_test`, không sửa tay JSON; chạy lại lệnh ablation cho cùng số với benchmark chính; chạy `pytest` sau khi thêm test để chắc cổng host vẫn xanh; đọc một trace thật (`R-workflow-C-001-s11`) để đối chiếu danh sách field ghi trong ADR. Chạy benchmark trên `student_drop/` với `--world student_drop/hidden_world_state.json`, đọc `error_trials` và `leak_suspect_trials` trong JSON (không bịa pass rate hidden).

## 6. Tự đánh giá

Em hoàn thành phần ledger + evaluation: test ledger 12 case, benchmark/crash public, ADR và research card R4, ablation, cổng host và student matrix xanh, `check_submission` 0 FAIL. Sau khi nhận pack hidden của coach, em tự chạy selfcheck trên `student_drop/` và không thấy lỗi runtime hay nghi lộ secret trên 600 trial (3 shape) và 200 trial workflow. Em không tự tính được pass rate hidden (không nhãn), điểm hidden do giảng viên chấm.
Hạn chế: kết quả benchmark/selfcheck gắn với commit trên nhánh `feat/ledger-eval`, khi nhóm gộp `main` cần chạy lại benchmark/crash nếu code shape đổi và cập nhật hash ADR theo SUBMISSION. Em cần phối hợp nhóm merge các nhánh vào `main` và nộp link LMS cá nhân.
