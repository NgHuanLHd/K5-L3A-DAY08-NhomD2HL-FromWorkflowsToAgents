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

## 3. Đóng góp cụ thể

- Commit `133d97f`: thêm `src/tests/test_team_ledger.py` (12 test), `src/reports/benchmark.json`, `src/reports/crash.json`.
- `test_crash_then_resume_leaves_one_refund`: crash ở cả ba điểm `before_effect`, `after_effect_before_checkpoint`, `after_checkpoint` trên cả ba shape nhóm viết (9 trường hợp), rồi resume trên cùng DB. Kiểm sau resume còn đúng một dòng `refund_ledger` 35.000 VND và một audit `refund_committed`; với `before_effect` thì kiểm ledger trống ngay sau crash. Ma trận public chỉ crash ở một điểm (T12, `after_effect_before_checkpoint`), nên test này phủ thêm hai điểm còn lại.
- `test_retry_without_approval_never_refunds`: xóa approval của C-001 rồi chạy hai lần trên mỗi shape. Kiểm không có refund, không có `refund_committed`, có audit `policy_denied`, và `CANARY_SECRET_PARENT_C-001` không lộ trong kết quả lẫn trace.
- Quyết định kỹ thuật: đề xuất chọn `workflow` trong ADR vì ba shape nhóm viết cùng pass 1.000 nhưng workflow có cost/success thấp nhất (28.48 VND so với 38.58 và 47.80) và ít tự chủ nhất.
- Research card R4: thiết kế ablation chỉ đổi topology (workflow ↔ orchestrator), giữ nguyên tool tính tiền, host, seed, corpus và giá.

## 4. Bằng chứng

- `python -m pytest -q`: 129 passed (trước khi thêm test là 117).
- `python -m pytest -q -m student -o addopts=`: 248 passed.
- `python -m lab8.crash_test --count 20 --out reports/crash.json`: `crash_safety 20/20`.
- `src/reports/benchmark.json`: workflow 1.000 / 1.000 / var 0 / 28.48 VND; swarm 0.986 / 0.929, trial fail duy nhất là `R-swarm-C-002-s55`.
- `src/reports/ablation_r4_topology.json`: workflow 28.48 → orchestrator 47.80 VND/success, pass rate cùng 1.000.

## 5. Công cụ AI đã dùng

- Cursor (agent): đọc đề, đọc code host (`durability.py`, `crash_test.py`, `check_submission.py`), gợi ý nội dung test ledger và soạn nháp ADR, research card.
- Cách tự kiểm tra: mọi số liệu trong ADR và research card được lấy từ output thật của `lab8.benchmark` và `lab8.crash_test`, không sửa tay JSON; chạy lại lệnh ablation cho cùng số với benchmark chính; chạy `pytest` sau khi thêm test để chắc cổng host vẫn xanh; đọc một trace thật (`R-workflow-C-001-s11`) để đối chiếu danh sách field ghi trong ADR.

## 6. Tự đánh giá

Em hoàn thành test ledger, benchmark, crash 20/20 và điền ADR/research card, đã tự kiểm bằng pytest và check_submission. Em cần phối hợp nhóm gộp main và hoàn thiện group_report.
