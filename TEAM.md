# Team D2HL

## Thông tin nhóm

- Tên nhóm: D2HL
- Lớp: L3A
- Repo nhóm: K5-L3A-DAY08-NhomD2HL-FromWorkflowsToAgents
  (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt:

## Thành viên

| STT | Họ tên           | MSSV        | Email                                                               | GitHub          | Vai trò                |
| --: | ---------------- | ----------- | ------------------------------------------------------------------- | --------------- | ---------------------- |
|   1 | Vũ Gia Linh      | 2A202603677 | [vugialinh905@gmail.com](mailto:vugialinh905@gmail.com)             | vugialinh905-wq | workflow + integration |
|   2 | Nguyễn Thị Duyên | 2A202603698 | [nguyenduyen.260903@gmail.com](mailto:nguyenduyen.260903@gmail.com) | duyen26912      | Single agent (ReAct)   |
|   3 | Nguyễn Đức Huân  | 2A202603690 | [huanducj@gmail.com](mailto:huanducj@gmail.com)                     | NgHuanLHd       | Orchestrator + Handoff |
|   4 | Võ Thị Kim Huyền | 2A202603679 | vothikimhuyenvta@gmail.com                                          | copengoknghek   | ledger + evaluation    |

Gợi ý chia vai:

- Nhóm 6 người: integration; workflow; single agent; orchestrator; ledger/policy/crash; eval/report.
- Nhóm 4 người: workflow + integration; single; orchestrator + handoff; ledger + evaluation.

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người            | Vai                    | Commit  | Test đã thêm hoặc sửa                                                                      |
| ---------------- | ---------------------- | ------- | ------------------------------------------------------------------------------------------ |
| Vũ Gia Linh      | workflow + integration |         |                                                                                            |
| Nguyễn Thị Duyên | Single agent (ReAct)   |         |                                                                                            |
| Nguyễn Đức Huân  | Orchestrator + Handoff |         |                                                                                            |
| Võ Thị Kim Huyền | ledger + evaluation    | 133d97f | `tests/test_team_ledger.py` (12 test: crash-resume 3 điểm × 3 shape, retry thiếu approval) |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.

# Mng làm theo mẫu sau nhe:

## MSSV_HovaTen

### Phần việc phụ trách

- Shape A `src/lab8/shapes/workflow.py`; ghép code các nhánh vào `main`, giữ `python -m pytest -q` xanh.

### Đóng góp cụ thể

- Cài 8 bước workflow: đọc claim qua `get_claim_view`, xử lý `needs_info` / `escalated`, tính tiền bằng `compute_compensation`, gọi `durability.issue_refund` với quote đầy đủ, ghi trace ở mọi nhánh return.
- Merge các nhánh, xử lý conflict.

### Bằng chứng

- Commit `<hash>`; `pytest -m student -k workflow`: 62 passed.

## 2A202603677_Vũ Gia Linh

### Phần việc phụ trách

-

### Đóng góp cụ thể

-

### Bằng chứng

-

## 2A202603698_Nguyễn Thị Duyên

### Phần việc phụ trách

-

### Đóng góp cụ thể

-

### Bằng chứng

-

## 2A202603690_Nguyễn Đức Huân

### Phần việc phụ trách

-

### Đóng góp cụ thể

-

### Bằng chứng

-

## 2A202603679_Võ Thị Kim Huyền

### Phần việc phụ trách

- Ledger + evaluation: crash/idempotency trên 3 shape nhóm viết, crash suite, benchmark, ADR và research card.

### Đóng góp cụ thể

- Thêm `src/tests/test_team_ledger.py`: crash ở cả 3 điểm rồi resume trên workflow, single, orchestrator (còn đúng 1 refund, 1 audit `refund_committed`); retry khi thiếu approval không tạo refund và không lộ secret.
- Chạy và commit `reports/benchmark.json`, `reports/crash.json`; ablation R4 `reports/ablation_r4_topology.json`.
- Điền `report/team/decision_adr.md` (đề xuất chọn workflow) và `report/team/research_card.md` (R4).

### Bằng chứng

- Commit `133d97f`; `pytest -q`: 129 passed; `pytest -m student`: 248 passed; `crash_safety 20/20`; workflow pass 1.000, cost/success 28.48 VND.
