# Yêu cầu chính thức của đề bài

## 1. Bài toán

Xây dựng chương trình so sánh độ tương đồng giữa hai ảnh sử dụng phương pháp
**Wavelet Hash** kết hợp **Hamming Distance**.

## 2. Yêu cầu chức năng

1. Đọc và tiền xử lý ảnh đầu vào (resize, chuyển grayscale, chuẩn hóa).
2. Thực hiện Wavelet Transform trên ảnh đã tiền xử lý để lấy các hệ số
   Wavelet (LL, LH, HL, HH).
3. Lượng tử hóa các hệ số Wavelet và sinh ra mã băm (Wavelet Hash) dạng
   chuỗi bit.
4. Tính Hamming Distance giữa hai mã băm để đo độ khác biệt.
5. Phân loại hai ảnh là **Similar** hoặc **Dissimilar** dựa trên một ngưỡng
   (threshold) xác định.
6. Đánh giá hiệu năng hệ thống trên một tập dữ liệu gồm các cặp ảnh
   similar/dissimilar đã được gán nhãn (ground truth), bằng các chỉ số:
   - Accuracy
   - Sensitivity (True Positive Rate)
   - Specificity (True Negative Rate)
   - Đường cong ROC và AUC

## 3. Yêu cầu phi chức năng

- Chương trình cần chạy được với các ảnh có khác biệt về góc chụp, độ sáng,
  kích thước, độ nhiễu, độ tương phản (đối với cặp similar), và vẫn cho kết
  quả hợp lý.
- Có tài liệu mô tả lý thuyết, thiết kế hệ thống, kế hoạch/kết quả kiểm thử.
- Có báo cáo tổng hợp kết quả thí nghiệm và kết luận.

## 4. Sản phẩm bàn giao

- Source code đầy đủ (`src/`, `experiments/`).
- Bộ test (`tests/`).
- Dataset mẫu (`data/`).
- Tài liệu (`docs/`) và kết quả (`results/`).
