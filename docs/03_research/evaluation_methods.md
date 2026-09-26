# Phương pháp đánh giá hệ thống

## 1. Mục đích đánh giá

Project xây dựng hệ thống so sánh độ tương đồng giữa hai ảnh dựa trên **Wavelet Hash** và **Hamming Distance**.

Sau khi hai ảnh được tiền xử lý, biến đổi Wavelet và tạo thành hai mã Hash, hệ thống tính Hamming Distance giữa hai Hash. Dựa trên một ngưỡng (threshold), hệ thống phân loại cặp ảnh thành:

- **Similar**: hai ảnh được xem là tương đồng.
- **Dissimilar**: hai ảnh được xem là không tương đồng.

Mục đích của quá trình đánh giá là xác định khả năng phân loại đúng của hệ thống trên tập dữ liệu gồm các cặp ảnh đã được gán nhãn Ground Truth.

Theo yêu cầu của project, các chỉ số chính được sử dụng gồm **Accuracy, Sensitivity, Specificity, ROC và AUC**.

---

## 2. Ground Truth và kết quả dự đoán

Mỗi cặp ảnh trong dataset được gán một nhãn Ground Truth:

- `Similar`: hai ảnh có nội dung tương đồng.
- `Dissimilar`: hai ảnh không tương đồng.

Sau khi hệ thống xử lý cặp ảnh, kết quả dự đoán được xác định dựa trên Hamming Distance và threshold.

Quy tắc phân loại:

- Nếu `Hamming Distance <= threshold` → dự đoán **Similar**.
- Nếu `Hamming Distance > threshold` → dự đoán **Dissimilar**.

Việc thay đổi threshold sẽ làm thay đổi số lượng mẫu được phân loại là Similar hoặc Dissimilar. Vì vậy, threshold có ảnh hưởng trực tiếp đến Accuracy, Sensitivity, Specificity và ROC.

---

## 3. Ma trận nhầm lẫn

Để đánh giá kết quả phân loại, sử dụng Confusion Matrix gồm bốn trường hợp:

| | Dự đoán Similar | Dự đoán Dissimilar |
|---|---:|---:|
| **Thực tế Similar** | TP | FN |
| **Thực tế Dissimilar** | FP | TN |

Trong đó:

### 3.1. True Positive (TP)

TP là số cặp ảnh thực tế là **Similar** và hệ thống cũng dự đoán **Similar**.

### 3.2. True Negative (TN)

TN là số cặp ảnh thực tế là **Dissimilar** và hệ thống cũng dự đoán **Dissimilar**.

### 3.3. False Positive (FP)

FP là số cặp ảnh thực tế là **Dissimilar** nhưng hệ thống dự đoán **Similar**.

Đây là trường hợp hệ thống nhận nhầm hai ảnh không tương đồng thành tương đồng.

### 3.4. False Negative (FN)

FN là số cặp ảnh thực tế là **Similar** nhưng hệ thống dự đoán **Dissimilar**.

Đây là trường hợp hệ thống bỏ sót một cặp ảnh tương đồng.

---

## 4. Accuracy

Accuracy biểu thị tỷ lệ số mẫu được hệ thống phân loại đúng trên tổng số mẫu.

Công thức:

\[
Accuracy = \frac{TP + TN}{TP + TN + FP + FN}
\]

Trong đó:

- `TP + TN`: tổng số mẫu được phân loại đúng.
- `FP + FN`: tổng số mẫu được phân loại sai.

Accuracy càng cao thì tỷ lệ dự đoán đúng trên toàn bộ dataset càng lớn.

Tuy nhiên, Accuracy cần được xem xét cùng với Sensitivity và Specificity, đặc biệt khi số lượng mẫu Similar và Dissimilar không cân bằng.

---

## 5. Sensitivity

Sensitivity còn được gọi là **True Positive Rate (TPR)**.

Chỉ số này cho biết khả năng hệ thống phát hiện đúng các cặp ảnh thực sự Similar.

Công thức:

\[
Sensitivity = TPR = \frac{TP}{TP + FN}
\]

Trong đó:

- `TP`: số cặp Similar được nhận diện đúng.
- `FN`: số cặp Similar bị nhận diện sai thành Dissimilar.

Sensitivity cao có nghĩa là hệ thống ít bỏ sót các cặp ảnh Similar.

---

## 6. Specificity

Specificity còn được gọi là **True Negative Rate (TNR)**.

Chỉ số này cho biết khả năng hệ thống nhận diện đúng các cặp ảnh thực sự Dissimilar.

Công thức:

\[
Specificity = \frac{TN}{TN + FP}
\]

Trong đó:

- `TN`: số cặp Dissimilar được nhận diện đúng.
- `FP`: số cặp Dissimilar bị nhận nhầm thành Similar.

Specificity cao cho thấy hệ thống có khả năng phân biệt tốt các ảnh không tương đồng.

---

## 7. False Positive Rate

False Positive Rate (FPR) biểu thị tỷ lệ các mẫu Dissimilar bị hệ thống nhận nhầm thành Similar.

Công thức:

\[
FPR = \frac{FP}{FP + TN}
\]

FPR có quan hệ với Specificity:

\[
FPR = 1 - Specificity
\]

FPR được sử dụng làm trục X khi xây dựng đường cong ROC.

---

## 8. True Positive Rate

True Positive Rate (TPR) chính là Sensitivity:

\[
TPR = \frac{TP}{TP + FN}
\]

TPR được sử dụng làm trục Y của đường cong ROC.

Khi threshold Hamming Distance thay đổi, TPR và FPR cũng thay đổi. Tập hợp các cặp giá trị `(FPR, TPR)` tương ứng với nhiều threshold tạo thành đường cong ROC.

---

## 9. ROC Curve

ROC (Receiver Operating Characteristic) là đường cong biểu diễn mối quan hệ giữa:

- Trục X: **False Positive Rate (FPR)**.
- Trục Y: **True Positive Rate (TPR)**.

Trong project, ROC được sử dụng để đánh giá khả năng phân loại Similar và Dissimilar của Wavelet Hash khi thay đổi threshold Hamming Distance.

Quy trình xây dựng ROC:

1. Tính Hamming Distance cho toàn bộ các cặp ảnh.
2. Chọn nhiều giá trị threshold khác nhau.
3. Với mỗi threshold, xác định kết quả Similar/Dissimilar.
4. Tính TP, TN, FP và FN.
5. Tính TPR và FPR.
6. Biểu diễn các điểm `(FPR, TPR)` trên đồ thị.
7. Nối các điểm để tạo ROC Curve.

ROC cho phép quan sát sự đánh đổi giữa khả năng phát hiện đúng ảnh Similar và tỷ lệ nhận nhầm ảnh Dissimilar.

Trong các nghiên cứu về perceptual image hashing, ROC cũng được sử dụng để đánh giá khả năng phân loại thông qua TPR và FPR khi thay đổi threshold.

---

## 10. AUC

AUC (Area Under the Curve) là diện tích nằm dưới đường cong ROC.

AUC được sử dụng để tổng hợp khả năng phân loại của hệ thống trên toàn bộ các threshold.

Giá trị AUC thường nằm trong khoảng:

\[
0 \leq AUC \leq 1
\]

Giá trị AUC càng gần 1 thì đường ROC càng gần khu vực phía trên bên trái của đồ thị.

AUC = 1 tương ứng với khả năng phân loại hoàn hảo trên tập dữ liệu đánh giá.

Trong đánh giá các phương pháp image similarity và image hashing, ROC/AUC là những cách phổ biến để phân tích khả năng phân biệt giữa các nhóm ảnh tương đồng và không tương đồng.

---

## 11. Lựa chọn Hamming Distance Threshold

Threshold là giá trị dùng để quyết định một cặp ảnh được xem là Similar hay Dissimilar.

Quy tắc:

\[
D \leq T \Rightarrow Similar
\]

\[
D > T \Rightarrow Dissimilar
\]

Trong đó:

- `D`: Hamming Distance giữa hai Hash.
- `T`: threshold.

Theo yêu cầu thí nghiệm của project, threshold cần được lựa chọn dựa trên kết quả ROC, có thể xem xét điểm cân bằng giữa Sensitivity và Specificity.

Không nên cố định threshold một cách tùy ý trước khi thực hiện đánh giá. Threshold cần được xác định dựa trên kết quả thực nghiệm của dataset.

---

## 12. Đánh giá trên Dataset

Dataset của project gồm hai nhóm:

### Nhóm Similar

Các cặp ảnh có nội dung tương đồng nhưng có thể có một số thay đổi như:

- Khác góc chụp.
- Thay đổi độ sáng.
- Thay đổi kích thước.
- Thêm nhiễu.
- Thay đổi độ tương phản.

Nhóm này được sử dụng để kiểm tra khả năng duy trì tính ổn định của Wavelet Hash trước các biến đổi của ảnh.

### Nhóm Dissimilar

Các cặp ảnh không liên quan về nội dung.

Nhóm này được sử dụng để kiểm tra khả năng phân biệt giữa các ảnh khác nhau.

Theo yêu cầu thí nghiệm của project, nên có tối thiểu `N` cặp Similar và `N` cặp Dissimilar, trong đó khuyến nghị `N >= 10` cho mỗi loại để kết quả đánh giá có ý nghĩa hơn.

---

## 13. Quy trình đánh giá tổng thể

Quy trình đánh giá của project được thực hiện theo các bước:

```text
Dataset
   ↓
Preprocessing
   ↓
Wavelet Transform
   ↓
Wavelet Hash
   ↓
Hamming Distance
   ↓
Thay đổi Threshold
   ↓
Similar / Dissimilar
   ↓
Confusion Matrix
   ↓
TP / TN / FP / FN
   ↓
Accuracy
Sensitivity
Specificity
FPR / TPR
   ↓
ROC Curve
   ↓
AUC
```

Quy trình này giúp đánh giá hệ thống từ bước tạo Hash đến khả năng phân loại cuối cùng.

---

## 14. Phân tích lỗi

Ngoài các chỉ số tổng hợp, cần ghi nhận các trường hợp phân loại sai:

### False Positive

Ảnh thực tế Dissimilar nhưng hệ thống dự đoán Similar.

Nguyên nhân có thể liên quan đến việc hai ảnh khác nội dung nhưng có đặc trưng sau Wavelet tương đối giống nhau hoặc threshold được chọn chưa phù hợp.

### False Negative

Ảnh thực tế Similar nhưng hệ thống dự đoán Dissimilar.

Trường hợp này có thể xảy ra khi ảnh Similar có biến đổi lớn về góc chụp, kích thước, độ sáng, nhiễu hoặc độ tương phản khiến Hash thay đổi nhiều.

Các trường hợp FP và FN cần được ghi nhận trong báo cáo thực nghiệm để phân tích nguyên nhân và đánh giá giới hạn của phương pháp.

---

## 15. So sánh các cấu hình Wavelet

Theo yêu cầu thí nghiệm, project cần thử nghiệm nhiều loại Wavelet như:

- Haar
- db2
- db4
- db8
- sym2
- sym4
- coif1
- ...

Với mỗi loại Wavelet, có thể thực hiện cùng một quy trình:

1. Tạo Wavelet Hash cho dataset.
2. Tính Hamming Distance.
3. Thay đổi threshold.
4. Tính TPR và FPR.
5. Xây dựng ROC Curve.
6. Tính AUC.
7. Ghi nhận kết quả vào bảng thực nghiệm.

Việc sử dụng cùng dataset và quy trình đánh giá giúp so sánh khả năng phân loại của các cấu hình Wavelet một cách nhất quán.

---

## 16. Các kết quả cần lưu lại

Kết quả đánh giá nên được lưu trong thư mục:

```text
results/
├── figures/
│   └── ROC Curve, biểu đồ phân bố Hamming Distance,...
│
├── tables/
│   └── Bảng Accuracy, Sensitivity, Specificity, AUC,...
│
└── reports/
    └── Báo cáo tổng hợp kết quả
```

Ngoài ra, các kết quả tổng hợp được trình bày trong:

```text
docs/06_results/
├── experiment_results.md
├── evaluation_results.md
└── conclusion.md
```

---

## 17. Kết luận về phương pháp đánh giá

Hệ thống được đánh giá dựa trên Ground Truth của dataset và kết quả dự đoán từ Hamming Distance.

Các chỉ số chính gồm:

- **Accuracy**: tỷ lệ phân loại đúng trên toàn bộ dataset.
- **Sensitivity (TPR)**: khả năng phát hiện đúng các cặp Similar.
- **Specificity (TNR)**: khả năng nhận diện đúng các cặp Dissimilar.
- **FPR**: tỷ lệ nhận nhầm Dissimilar thành Similar.
- **ROC Curve**: thể hiện sự thay đổi giữa TPR và FPR khi threshold thay đổi.
- **AUC**: tổng hợp khả năng phân biệt của hệ thống trên các threshold.

Phương pháp đánh giá này được sử dụng để xác định khả năng phân loại Similar/Dissimilar của hệ thống Wavelet Hash + Hamming Distance và làm cơ sở lựa chọn threshold cũng như phân tích các trường hợp phân loại sai.