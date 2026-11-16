# Bonus report: B4

- Topic + nguồn (tên, năm, slide): B4 · EMNLP 2026, _Rethinking Evaluation of MAS Efficiency_ (slide 44, 59), AgentArch, AACL 2026 (slide 43).
- CLAIM của nguồn (1 câu): Chênh lệch "hiệu quả" của hệ multi-agent có thể đến từ cách dựng benchmark (lời gọi thừa, cách chia chi phí), và random pruning đôi khi giữ nguyên hiệu năng, nên phải so với single-agent và baseline đơn giản khi giữ cố định runtime, model và tool.
- BOUNDARY (model / dataset / setup): Paper đo LLM thật trên benchmark của họ. Lab này chỉ kiểm được phần phương pháp: MockLLM theo seed, 14 claim public, 5 seed `11,22,33,44,55`, giá mô phỏng, evaluator `lab8.metrics.trial_pass`.
- HYPOTHESIS trên LogiX: Trên cùng corpus, bỏ lời gọi draft của workflow không đổi pass rate; cắt ngẫu nhiên peer/parse của swarm không đổi pass rate; bỏ bước đọc đơn hoặc bước quote thì pass rate giảm có ý nghĩa. Chênh pass rate workflow so với swarm (một trial) chưa đủ để bác bỏ giả thuyết "hai shape đúng như nhau"; chênh chi phí thì đủ.
- Biến cố định / biến thay đổi: Cố định MockLLM, `compute_compensation`, host `durability.issue_refund`, seed, `data/public_claims.jsonl`, `config/pricing.yaml`, evaluator, SQLite mới mỗi trial. Biến thay đổi: có/không lời gọi model draft; có/không `lookup_order`; có/không `compute_compensation`; có/không lời gọi peer và parse theo seed.
- Lệnh tái lập (copy-paste được), chạy trong `src/`:

```bash
python -m bonus.ablation --shapes workflow,single,swarm --extra-shape rules_only=bonus.variants:run_rules_only --extra-shape swarm_pruned=bonus.variants:run_swarm_pruned --extra-shape workflow_no_draft=bonus.variants:run_no_draft --extra-shape workflow_no_investigator=bonus.variants:run_no_investigator --extra-shape workflow_no_check=bonus.variants:run_no_check --seeds 11,22,33,44,55 --out reports/bonus_ablation.json
```

- File report + run id: `src/reports/bonus_ablation.json`. Trial lệch duy nhất của swarm và swarm_pruned: `R-swarm-C-002-s55` / `R-swarm_pruned-C-002-s55` (status `resolved` trong khi nhãn là `denied`).

## Kết quả

70 trial mỗi shape (14 claim × 5 seed). CI 95% là percentile bootstrap, resample theo claim, 4000 lần, seed `20261115`. Chi phí là VND mô phỏng. `leak` = `CANARY_SECRET_` trong kết quả hoặc trace. `bypass` = có dòng ledger khi `approval_ok` là false.

| Shape                    |  Pass | CI 95%      | Pass^5 |      Var | Cost/success | Tổng cost | Model/trial | Leak | Bypass |
| ------------------------ | ----: | ----------- | -----: | -------: | -----------: | --------: | ----------: | ---: | -----: |
| workflow                 | 1.000 | 1.000–1.000 |  1.000 |        0 |        28.48 |   1993.70 |       0.643 |    0 |      0 |
| single                   | 1.000 | 1.000–1.000 |  1.000 |        0 |        38.58 |   2700.90 |       4.214 |    0 |      0 |
| rules_only               | 1.000 | 1.000–1.000 |  1.000 |        0 |        27.86 |   1950.00 |           0 |    0 |      0 |
| workflow_no_draft        | 1.000 | 1.000–1.000 |  1.000 |        0 |        27.86 |   1950.00 |           0 |    0 |      0 |
| swarm                    | 0.986 | 0.957–1.000 |  0.929 | 0.000816 |        49.57 |   3420.12 |       3.000 |    0 |      0 |
| swarm_pruned             | 0.986 | 0.957–1.000 |  0.929 | 0.000816 |        48.94 |   3377.00 |       2.200 |    0 |      0 |
| workflow_no_investigator | 0.143 | 0.000–0.357 |  0.143 |        0 |        70.00 |    700.00 |           0 |    0 |      0 |
| workflow_no_check        | 0.357 | 0.143–0.643 |  0.357 |        0 |        54.00 |   1350.00 |           0 |    0 |      0 |

Kiểm định cặp trên cùng `(claim, seed)`. McNemar exact cho pass/fail. Sign test exact cho `cost_estimate` (positive = vế trái đắt hơn).

| Cặp                                  | McNemar (b, c, p) | Sign test chi phí (rẻ hơn / hòa / p) |
| ------------------------------------ | ----------------- | ------------------------------------ |
| workflow vs swarm                    | 0, 1, 1.0         | 70 / 0 / 1.694e-21                   |
| workflow vs single                   | 0, 0, 1.0         | 65 / 5 / 5.421e-20                   |
| rules_only vs workflow               | 0, 0, 1.0         | 45 / 25 / 5.684e-14                  |
| workflow_no_draft vs workflow        | 0, 0, 1.0         | 45 / 25 / 5.684e-14                  |
| swarm_pruned vs swarm                | 0, 0, 1.0         | 56 / 14 / 2.776e-17                  |
| workflow_no_investigator vs workflow | 60, 0, 1.735e-18  | 65 / 5 / 5.421e-20                   |
| workflow_no_check vs workflow        | 45, 0, 5.684e-14  | 60 / 10 / 1.735e-18                  |

`b` = vế trái sai và vế phải đúng; `c` = ngược lại. Seed bị cắt lời gọi (`true` = bỏ): 11 bỏ peer, 22 bỏ parse, 33 không bỏ, 44 bỏ peer, 55 bỏ peer. 14 trial hòa chi phí của swarm_pruned đúng bằng 14 claim ở seed 33.

## Kết luận

Ủng hộ một phần, không ủng hộ câu "swarm kém chính xác hơn".

Pass rate workflow và swarm chỉ lệch một cặp (C-002, seed 55). McNemar p = 1.0, CI của swarm chứa 1.0. Trên bộ public này chưa kết luận được rằng topology làm swarm sai hơn. Chi phí thì kết luận được: workflow rẻ hơn swarm trên cả 70 cặp.

Bỏ draft không đổi pass rate, pass^5, variance hay số event trace (mean steps vẫn 4.36). `workflow_no_draft` trùng `rules_only` vì draft là lời gọi model duy nhất của workflow, và lời đó không vào số tiền. 45 trial rẻ hơn, 25 trial hòa (những claim không đi tới draft). Thành phần bỏ đi mà độ đúng không đổi là lời gọi draft.

Cắt peer/parse theo seed cũng không đổi độ đúng của swarm, kể cả lỗi seed 55, vì override lấy `parse_delay_days(ticket)` chứ không lấy chữ model trả về. Mean model calls 3.0 → 2.2, cost/success 49.57 → 48.94. Random pruning giữ hiệu năng, đúng claim của nguồn, trong giới hạn MockLLM.

Bỏ `lookup_order` (bước đóng vai investigator) hạ pass rate xuống 0.143 (p = 1.735e-18). Bỏ `compute_compensation` và fail-closed, không bịa số tiền, hạ pass rate xuống 0.357 (p = 5.684e-14). Hai thành phần này không phải trang trí. Cost/success của bản không investigator là 70 VND trong khi tổng cost chỉ 700 so với 1993.70 của workflow: mẫu số success giảm nên cost/success tăng dù tổng việc giảm. Đọc mỗi cost/success sẽ đảo chiều kết luận.

Kết luận đảo ngược nếu: (1) chữ peer/parse của model thật được đưa vào quote — khi đó cắt lời gọi sẽ đổi pass rate; (2) bộ hidden có nhiều claim lệch ticket/order ở seed chia hết cho 5, đủ để McNemar p < 0.05; (3) ablation của bước kiểm không fail-closed mà tự đề xuất số tiền.

## Giới hạn

MockLLM không phải model sản xuất. Latency là `unavailable`, nên topic này không nói về độ trễ. 14 claim public, một cặp lệch, nên kiểm định độ đúng workflow–swarm gần như không có sức mạnh. Giá là mô phỏng. Nhãn lấy từ `expected` viết sẵn, không sinh bằng `compensation.quote`.
