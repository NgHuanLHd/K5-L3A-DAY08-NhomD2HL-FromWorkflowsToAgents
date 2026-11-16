# Decision record

Điền sau dấu `:` trên cùng dòng, không xóa nhãn. Giảng viên và `python -m lab8.check_submission` (chạy trong `src/`) đọc các dòng này bằng máy. Không đổi tên hay dời file này khỏi `report/team/`.
`Shape chọn` phải là đúng một trong: `workflow`, `single`, `orchestrator`, `swarm`. Đây là shape được chấm cổng hidden.

- Shape chọn: workflow
- Commit hash: 0bff6f0
- Run id dẫn chứng: R-workflow-C-002-s55 (workflow từ chối đúng T02 ở seed 55), đối chứng R-swarm-C-002-s55 (swarm trả 20.000 VND sai); nguồn src/reports/benchmark.json
- Pass rate / pass^5 / seed min-max / variance: 1.000 / 1.000 / 1.000–1.000 / 0.000000 (70 trial = 14 claim public × 5 seed 11,22,33,44,55)
- Cost per success (mô phỏng, VND): 28.48 (single 38.58, orchestrator 47.80, swarm 49.57)
- Crash safety: 20/20 (src/reports/crash.json)
- Secret leak / approval bypass: 0 / 0 (benchmark không có trial nào fail vì chuỗi cấm hay ledger thừa; test_team_ledger.py kiểm retry thiếu approval trên cả 3 shape nhóm viết)

Ví dụ một dòng đã điền: `- Shape chọn: workflow`, `- Crash safety: 20/20 (src/reports/crash.json)`.

## Vì sao shape này

Trên cùng corpus (14 claim public), cùng 5 seed, cùng bảng giá `config/pricing.yaml` và cùng MockLLM, ba shape nhóm viết đều đạt pass rate 1.000, pass^5 1.000, variance 0. Khi độ đúng ngang nhau, quyết định nằm ở chi phí và mức tự chủ. Workflow rẻ nhất: 28.48 VND mỗi lần thành công, so với 38.58 của single (+35%) và 47.80 của orchestrator (+68%). Workflow cũng ít bước nhất trong ba shape nhóm viết (trung bình 4.36 event, p95 là 5) và trung bình chỉ 0.64 lời gọi model mỗi trial, vì model chỉ soạn chữ trả lời. Swarm có ít event trace nhất (2.8) nhưng đắt nhất (49.57 VND/success) và là shape duy nhất có variance khác 0: ở seed 55 nó tin số ngày trễ trong ticket và trả tiền cho T02 (pass rate 0.986, pass^5 0.929). Theo nguyên tắc chọn kiến trúc ít tự chủ nhất mà vẫn làm được việc, nhóm chọn workflow.

## Có đáng đổi lấy multi-agent không

Không, trên số đo hiện tại. Orchestrator không nhỉnh hơn về pass rate (cùng 1.000) mà tốn thêm 68% chi phí, do có lời gọi model để lập kế hoạch và một tool đọc lịch sử refund. Lợi ích duy nhất là tách quyền: investigator chỉ có tool đọc. Nhưng ở workflow, quyền ghi đã nằm trong code và host (`durability.issue_refund` kiểm approval, trần theo đơn, idempotency), nên lợi ích đó không làm tăng độ an toàn đo được. Quyết định sẽ đảo lại nếu: (1) bộ hidden có loại claim cần đọc chứng từ tự do mà luật cố định không mã hóa được, khiến workflow tụt dưới 0.75 trong khi single hoặc orchestrator giữ được; (2) cần chạy nhiều investigator song song trên nhiều nguồn dữ liệu, khi đó độ trễ (hiện là `unavailable`) mới trở thành tiêu chí; (3) giá model giảm đến mức chênh 19 VND/success không còn ý nghĩa so với lợi ích tách quyền.

## Trace và bằng chứng

Trace workflow (ví dụ `R-workflow-C-001-s11`) ghi các event theo thứ tự: `claim` (chỉ `claim_id` và cờ `has_order_id`), `order` (đúng các field allowlist `ORDER_FIELDS` do `lookup_order` trả về: mã đơn, trạng thái, số ngày trễ, phí ship, số tiền đã trả, hư hỏng đã xác minh, hãng vận chuyển), `quote` (số tiền, lý do, clause), `host` (`ok`, `reason`), `crash` nếu có, và `decision`. Trace cố ý **không** ghi: nội dung ticket (dữ liệu người dùng, có thể chứa injection), `parent_secret` và `raw_headers` (chứa `CANARY_SECRET_*`), số điện thoại, địa chỉ, ghi chú nội bộ và tên hàng. Claim được đọc qua `get_claim_view` chứ không `SELECT *`, nên các field nhạy cảm không vào bộ nhớ của shape từ đầu. Nếu trace nằm ngoài chỗ scanner quét, đội security vẫn kiểm được qua hai lớp: (a) các field cấm không bao giờ được đọc vào shape, kiểm được bằng cách đọc code; (b) `metrics.trial_pass` quét cả kết quả JSON lẫn mọi file `<run_id>*`, và `test_team_ledger.py` kiểm trực tiếp rằng `CANARY_SECRET_PARENT_C-001` không xuất hiện trong kết quả hay trace.

## Giới hạn

MockLLM không phải model sản xuất. Latency để `unavailable`. Không sửa JSON cho đủ 0.75. Pass rate 1.000 chỉ đo trên 14 claim public, chưa phải bộ hidden 40 claim; chi phí là giá mô phỏng, không phải hóa đơn API.
