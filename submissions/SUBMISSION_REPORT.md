# Báo cáo Lab Day 21 — CI/CD cho AI Systems

## Kết quả

Pipeline gồm bốn job `Unit Test → Train → Eval → Deploy`. MLflow lưu thí nghiệm trên DagsHub, DVC lưu dữ liệu trên Google Cloud Storage và FastAPI phục vụ mô hình trên Compute Engine. GitHub Actions truy cập GCP bằng Workload Identity Federation, không dùng service-account key dài hạn.

Mô hình production là Random Forest với `n_estimators=400`, `max_depth=None`, `min_samples_split=2` và `min_samples_leaf=2`. Cấu hình này cho kết quả tốt nhất trong các thử nghiệm đã chạy. Gradient Boosting và Logistic Regression cũng được thử và lưu trên MLflow để so sánh.

| Dữ liệu huấn luyện | Accuracy | Weighted F1 |
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
