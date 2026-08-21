# Hướng dẫn chụp screenshot nộp bài

Chụp ảnh theo đúng thứ tự dưới đây. Mỗi ảnh nên thấy thanh địa chỉ hoặc tiêu đề
cửa sổ, nội dung chính và không để lộ token/private key.

## 1. MLflow UI — ít nhất ba thí nghiệm

Tại thư mục repo, chạy:

```powershell
.venv\Scripts\mlflow.exe ui --backend-store-uri sqlite:///mlflow.db --port 5000
```

Mở `http://localhost:5000`, mở experiment `Default`, sắp xếp theo Accuracy giảm
dần. Chụp bảng có tối thiểu ba run với cột model type/params, Accuracy và F1.
Ưu tiên để cùng ảnh thấy Random Forest, Gradient Boosting và Logistic
Regression nhằm làm bằng chứng Bonus 2.

## 2. GitHub Actions — pipeline dữ liệu chạy xanh

Mở run sau và chụp toàn bộ sơ đồ bốn jobs xanh cùng commit dữ liệu:

`https://github.com/duckymoimoi/K3-Track2-Day21-CI-CD-for-AI-Systems/actions/runs/32443554519`

Ảnh phải thấy tên commit `data: bổ sung 2998 mẫu dữ liệu mới (train_phase2)` và
bốn jobs Unit Test, Train, Eval, Deploy màu xanh.

Run xanh thứ hai sau khi khôi phục bộ siêu tham số production:

`https://github.com/duckymoimoi/K3-Track2-Day21-CI-CD-for-AI-Systems/actions/runs/32444071837`

## 3. Eval gate chặn model yếu

Ngưỡng tối thiểu 0.70:

`https://github.com/duckymoimoi/K3-Track2-Day21-CI-CD-for-AI-Systems/actions/runs/32443334169`

Mở job Eval → bước `Check quality gate...`, chụp dòng:
`FAILED: accuracy 0.6820 < 0.70. Deploy blocked.`

Bonus rollback production:

`https://github.com/duckymoimoi/K3-Track2-Day21-CI-CD-for-AI-Systems/actions/runs/32443887907`

Chụp ba dòng candidate 0.734, production 0.744 và thông báo `REGRESSION`.

## 4. Serving — health và predict

Mở PowerShell, tăng chiều rộng cửa sổ rồi chạy:

```powershell
curl.exe -sS http://34.135.190.153:8000/health
$body = @{features=@(7.4,0.70,0.00,1.9,0.076,11.0,34.0,0.9978,3.51,0.56,9.4,0)} | ConvertTo-Json -Compress
$curlBody = $body.Replace('"','\"')
curl.exe -sS -X POST http://34.135.190.153:8000/predict -H "Content-Type: application/json" --data-raw $curlBody
```

Chụp cùng một ảnh có cả hai kết quả:

```json
{"status":"ok"}
{"prediction":0,"label":"thap"}
```

## 5. Google Cloud Storage — DVC và production model

Mở:

`https://console.cloud.google.com/storage/browser/vinuni-mlops-day21-79888249254?project=project-c2976661-717f-46ca-9ce`

Chụp một ảnh ở prefix `dvc/files/md5/` để thấy các object dữ liệu. Sau đó mở
`models/latest/` và chụp ảnh thấy đủ `model.pkl`, `metrics.json`, `report.txt`.

## 6. DagsHub MLflow — Bonus 1

Sau khi cấu hình DagsHub, mở:

`https://dagshub.com/<DAGSHUB_USER>/K3-Track2-Day21-CI-CD-for-AI-Systems.mlflow`

Chụp bảng run được tạo bởi GitHub Actions, có params và metrics. Không chụp
trang token/settings.

## 7. Repo và gói nộp

Repo public:

`https://github.com/duckymoimoi/K3-Track2-Day21-CI-CD-for-AI-Systems`

Nộp URL repo, chuỗi ảnh theo thứ tự trên, và file
`docs/SUBMISSION_REPORT.md` (xuất PDF nếu LMS yêu cầu file thay vì Markdown).
