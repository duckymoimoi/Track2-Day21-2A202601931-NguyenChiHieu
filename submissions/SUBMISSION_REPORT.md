# Báo cáo Lab Day 21 — CI/CD cho AI Systems

## Kết quả

Pipeline gồm bốn job `Unit Test → Train → Eval → Deploy`. MLflow lưu thí nghiệm trên DagsHub, DVC lưu dữ liệu trên Google Cloud Storage và FastAPI phục vụ mô hình trên Compute Engine. GitHub Actions truy cập GCP bằng Workload Identity Federation, không dùng service-account key dài hạn.

## So sánh thí nghiệm và chọn siêu tham số

Các run trên MLflow dùng cùng tập đánh giá 500 mẫu của phase 1 và cho kết quả sau:

| Mô hình | Siêu tham số | `accuracy` | `f1_score` (weighted) |
|---|---|---:|---:|
| Random Forest | `n_estimators=400`, `max_depth=None`, `min_samples_split=2`, `min_samples_leaf=2` | 0.682 | 0.6809 |
| Random Forest | `n_estimators=200`, `max_depth=10`, `min_samples_split=5` | 0.644 | 0.6417 |
| Gradient Boosting | `n_estimators=150`, `learning_rate=0.05`, `max_depth=3` | 0.604 | 0.6006 |
| Logistic Regression | `C=1.0`, `max_iter=2000` | 0.568 | 0.5632 |
| Random Forest | `n_estimators=100`, `max_depth=5`, `min_samples_split=2` | 0.564 | 0.5534 |
| Random Forest | `n_estimators=50`, `max_depth=3`, `min_samples_split=2` | 0.558 | 0.5185 |

Random Forest với 400 cây cho cả accuracy và weighted F1 cao nhất nên được chọn. `max_depth=None` giữ đủ năng lực học, còn `min_samples_leaf=2` hạn chế các lá chỉ chứa một mẫu. Đây cũng là cấu hình dùng cho model production.

## So sánh hai giai đoạn dữ liệu

| Dữ liệu huấn luyện | `accuracy` | `f1_score` (weighted) |
|---:|---:|---:|
| 2.998 mẫu | 0.682 | 0.6809 |
| 5.996 mẫu | 0.744 | 0.7430 |

Thêm 2.998 mẫu phase 2 giúp accuracy tăng 0.062 và weighted F1 tăng 0.0621. Model mới vượt ngưỡng 0.70 và được triển khai. API production trả `{"status":"ok"}` tại `/health` và trả dự đoán hợp lệ tại `/predict`.

## Kiểm soát chất lượng và bonus

- Eval gate chặn model phase 1 vì accuracy 0.682 thấp hơn 0.70.
- Regression gate chặn model 0.734 vì thấp hơn model production 0.744.
- Model chỉ được chuyển từ vùng candidate sang `models/latest` sau khi vượt cả hai gate.
- Báo cáo huấn luyện có confusion matrix, precision, recall, F1 theo từng lớp và phân phối nhãn.
- MLflow lưu tham số và metrics của Random Forest, Gradient Boosting và Logistic Regression trên DagsHub.
- DagsHub token được lưu trong GitHub Secret `DAY21`, không xuất hiện trong code hoặc log.

## Khó khăn và cách xử lý

`mlflow==2.13.0` không tương thích với setuptools mới nên dự án khóa `setuptools<81`. Chính sách GCP không cho tạo service-account JSON key nên GitHub Actions dùng Workload Identity Federation và VM dùng attached service account. Dữ liệu phase 1 không đạt ngưỡng 0.70 dù đã thử nhiều cấu hình, vì vậy pipeline giữ nguyên gate, dùng lần thất bại để chứng minh cơ chế chặn và chỉ triển khai sau khi bổ sung phase 2.
