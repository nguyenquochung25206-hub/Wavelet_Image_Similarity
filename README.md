# Wavelet Image Similarity

So sánh độ tương đồng giữa hai ảnh bằng phương pháp **Wavelet Hash** kết hợp
**Hamming Distance**, có đánh giá hiệu năng bằng Accuracy, Sensitivity,
Specificity và đường cong ROC.

## 1. Giới thiệu

Project mô phỏng một pipeline hoàn chỉnh để xác định hai ảnh có "giống nhau"
hay không, ngay cả khi chúng khác nhau về góc chụp, độ sáng, kích thước, độ
nhiễu hoặc độ tương phản. Quy trình tổng quát:

```
Ảnh gốc
  ↓
Tiền xử lý (resize, grayscale, chuẩn hóa)
  ↓
Wavelet Transform
  ↓
Wavelet coefficients → Quantization
  ↓
Wavelet Hash
  ↓
Hamming Distance
  ↓
Similar / Dissimilar
  ↓
Đánh giá kết quả (Accuracy, Sensitivity, Specificity, ROC)
```

## 2. Cấu trúc thư mục

```
Wavelet_Image_Similarity/
├── docs/           # Tài liệu quản lý, nghiên cứu, thiết kế, kiểm thử, kết quả
├── data/           # Ảnh đầu vào (similar/dissimilar) và kết quả đầu ra
├── src/            # Source code chính (preprocessing, wavelet, similarity, evaluation, visualization)
├── experiments/    # Script chạy thí nghiệm
├── tests/          # Unit test cho từng module
├── notebooks/      # Jupyter notebook nghiên cứu/thử nghiệm
└── results/        # Bảng, biểu đồ, báo cáo cuối cùng
```

Chi tiết phân công từng thành viên: xem
[`docs/01_project_management/task_list.md`](docs/01_project_management/task_list.md).

## 3. Cài đặt

Yêu cầu Python 3.9+.

```bash
# 1. Tạo virtual environment (khuyến nghị)
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Cài thư viện
pip install -r requirements.txt
```

## 4. Chuẩn bị dữ liệu

Đặt các cặp ảnh vào:

```
data/input/similar/pair_XX/image_01.jpg
data/input/similar/pair_XX/image_02.jpg

data/input/dissimilar/pair_XX/image_01.jpg
data/input/dissimilar/pair_XX/image_02.jpg
```

- **similar**: hai ảnh cùng đối tượng/nội dung, có thể khác góc chụp, độ
  sáng, kích thước, độ nhiễu, độ tương phản.
- **dissimilar**: hai ảnh không có nội dung tương đồng.

## 5. Chạy tiền xử lý (module của TV1)

```bash
python -m src.preprocessing.image_preprocessor \
    --input data/input/similar/pair_01/image_01.jpg \
    --output data/output/preprocessed/pair_01_image_01.png
```

Hoặc dùng trực tiếp trong Python:

```python
from src.preprocessing.image_preprocessor import preprocess_image

processed = preprocess_image("data/input/similar/pair_01/image_01.jpg")
```

## 6. Chạy test

```bash
pytest tests/ -v
```

## 7. Các bước tiếp theo trong pipeline

Sau khi ảnh được tiền xử lý bởi module của TV1, các thành viên khác sẽ tiếp
tục: TV2 (Wavelet Transform) → TV3 (Wavelet Hash) → TV4 (Hamming Distance) →
TV5 (Evaluation) → TV6 (Visualization) → TV7 (Testing/Integration).

## 8. Giấy phép

Xem [LICENSE](LICENSE).
