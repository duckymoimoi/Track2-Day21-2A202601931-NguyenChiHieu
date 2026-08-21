# Báo cáo Lab Day 21 — CI/CD cho AI Systems

## Kiến trúc và kết quả

Hệ thống dùng MLflow để theo dõi thí nghiệm, DVC với Google Cloud Storage để
phiên bản hóa dữ liệu, GitHub Actions để chạy chuỗi Unit Test → Train → Eval →
Deploy, và FastAPI trên Compute Engine để phục vụ mô hình. GitHub xác thực GCP
bằng Workload Identity Federation thay cho service-account key dài hạn.

Mô hình production là Random Forest với `n_estimators=400`, `max_depth=None`,
`min_samples_split=2`, `min_samples_leaf=2`. Đây là cấu hình Random Forest tốt
nhất trong các thí nghiệm: nó đạt 0.682 trên phase 1 và 0.744 sau khi thêm phase
2. Gradient Boosting và Logistic Regression cũng được thử nghiệm và ghi nhận
trong MLflow để đáp ứng phần so sánh nhiều thuật toán.

| Dữ liệu huấn luyện | Accuracy | Weighted F1 |
|---:|---:|---:|
| 2.998 mẫu | 0.682 | 0.6809 |
| 5.996 mẫu | 0.744 | 0.7430 |

Lần chạy phase 1 bị eval gate chặn vì 0.682 < 0.70. Commit dữ liệu phase 2 tự
kích hoạt lại pipeline; cả bốn jobs hoàn tất và model mới được triển khai. API
production trả `{"status":"ok"}` tại `/health` và dự đoán hợp lệ tại
`/predict`.

## Bonus và kiểm soát an toàn

- Hỗ trợ Random Forest, Gradient Boosting và Logistic Regression.
- Tự sinh confusion matrix, precision/recall từng lớp và `report.txt`.
- Ghi phân phối nhãn vào metrics; cảnh báo nếu lớp nào dưới 10%.
- Model được upload vào vùng candidate; chỉ promote sang `models/latest` sau
  khi qua ngưỡng 0.70 và không kém model production. Thử nghiệm rollback đã
  chặn model 0.734 vì thấp hơn production 0.744.
- Workflow hỗ trợ MLflow tracking từ xa qua ba GitHub secrets DagsHub.

## Khó khăn và cách xử lý

`mlflow==2.13.0` không tương thích setuptools mới, nên requirements được khóa
`setuptools<81`. Chính sách GCP cấm tạo service-account JSON key; hệ thống được
chuyển sang WIF cho GitHub và attached service account cho VM. Trên Windows,
PSCP không mở rộng `~`, nên quá trình cấu hình VM dùng đường dẫn tuyệt đối.
Cuối cùng, siêu tham số gợi ý của đề không đạt gate với 2.998 mẫu; pipeline giữ
nguyên ngưỡng 0.70 và dùng run thất bại làm bằng chứng gate hoạt động đúng.
