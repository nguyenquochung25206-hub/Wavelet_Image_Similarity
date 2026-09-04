# Yêu cầu về thí nghiệm

## 1. Dữ liệu thí nghiệm

- Tối thiểu N cặp ảnh **similar** và N cặp ảnh **dissimilar** (N do nhóm tự
  quyết định, khuyến nghị ≥ 10 cặp mỗi loại để kết quả đánh giá có ý nghĩa
  thống kê).
- Mỗi cặp similar nên có ít nhất một biến thể: khác góc chụp, độ sáng, kích
  thước, độ nhiễu, hoặc độ tương phản, nhằm kiểm tra tính bền vững (độ chắc)
  của Wavelet Hash.
- Mỗi cặp dissimilar là hai ảnh không liên quan về nội dung.

## 2. Các thí nghiệm cần thực hiện

1. **So sánh các loại Wavelet** (TV2): thử Haar, db2, db4, db8, sym2, sym4,
   coif1,... và so sánh hiệu quả phân loại.
2. **So sánh từng cặp ảnh** (TV4): với mỗi cặp, tính Hash 1, Hash 2, Hamming
   Distance, độ tương đồng (similarity), và kết luận Similar/Dissimilar.
3. **Đánh giá trên toàn bộ dataset** (TV5): so ground truth với kết quả dự
   đoán để tính TP/TN/FP/FN, từ đó suy ra Accuracy, Sensitivity, Specificity,
   ROC, AUC.
4. **Kiểm thử độ bền vững**: kiểm tra Hash có ổn định khi ảnh bị thay đổi
   brightness, resize, hay không (theo test case của TV7).

## 3. Tiêu chí đánh giá kết quả

- Ngưỡng (threshold) Hamming Distance được chọn dựa trên đường ROC (điểm cân
  bằng giữa Sensitivity và Specificity, hoặc theo yêu cầu cụ thể của đề bài).
- Ghi nhận và giải thích rõ các trường hợp phân loại sai (false
  positive/false negative).

## 4. Đầu ra của thí nghiệm

- Bảng kết quả (`results/tables/`).
- Biểu đồ (`results/figures/`): Hamming Distance distribution, ROC curve,...
- Báo cáo tổng hợp (`docs/06_results/`).
