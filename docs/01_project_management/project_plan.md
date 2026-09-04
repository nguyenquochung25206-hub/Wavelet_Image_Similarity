# Kế hoạch tổng thể project — Wavelet Image Similarity

## 1. Mục tiêu

Xây dựng một hệ thống so sánh độ tương đồng giữa hai ảnh dựa trên **Wavelet
Hash** và **Hamming Distance**, sau đó đánh giá hiệu năng của hệ thống bằng
các chỉ số Accuracy, Sensitivity, Specificity và đường cong ROC.

## 2. Phạm vi công việc

1. Tiền xử lý ảnh (resize, grayscale, chuẩn hóa).
2. Biến đổi Wavelet (Wavelet Transform) trên ảnh đã tiền xử lý.
3. Sinh mã băm (Wavelet Hash) từ các hệ số Wavelet.
4. So sánh hai mã băm bằng Hamming Distance để phân loại Similar/Dissimilar.
5. Đánh giá hiệu năng hệ thống trên toàn bộ dataset (Accuracy, Sensitivity,
   Specificity, ROC/AUC).
6. Thiết kế kiến trúc hệ thống và trực quan hóa kết quả.
7. Kiểm thử toàn bộ pipeline trước khi nộp báo cáo.

## 3. Quy trình xử lý tổng quát

```
Ảnh gốc
  ↓ (TV1) Tiền xử lý
  ↓ (TV2) Wavelet Transform
  ↓ (TV3) Wavelet Hash
  ↓ (TV4) Hamming Distance
  ↓ (TV4) So sánh ngưỡng → Similar / Dissimilar
  ↓ (TV5) Đánh giá kết quả
  ↓ (TV6) Trực quan hóa
  ↓ (TV7) Kiểm thử & tổng hợp
```

## 4. Phân công nhân sự

Xem chi tiết tại [`task_list.md`](task_list.md).

## 5. Mốc thời gian

Xem chi tiết tại [`timeline.md`](timeline.md).

## 6. Tiêu chí nghiệm thu

- Toàn bộ pipeline chạy được từ đầu đến cuối trên dataset mẫu.
- Có đầy đủ tài liệu nghiên cứu, thiết kế, kiểm thử, kết quả trong `docs/`.
- Có test cho từng module chính trong `tests/`.
- Có báo cáo đánh giá hiệu năng (Accuracy, Sensitivity, Specificity, ROC).
- Có sơ đồ hệ thống và biểu đồ kết quả phục vụ báo cáo/thuyết trình.
