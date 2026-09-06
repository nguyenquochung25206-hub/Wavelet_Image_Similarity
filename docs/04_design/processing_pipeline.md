# QUY TRÌNH XỬ LÝ HỆ THỐNG

## 1. Tổng quan quy trình

Hệ thống **Wavelet Image Similarity** được xây dựng nhằm xác định mức độ tương đồng giữa hai ảnh dựa trên đặc trưng được trích xuất bằng Wavelet Transform.

Quy trình xử lý của hệ thống bắt đầu từ hai ảnh đầu vào. Các ảnh được tiền xử lý để đưa về cùng định dạng, sau đó thực hiện Wavelet Transform để trích xuất đặc trưng. Các đặc trưng Wavelet được sử dụng để tạo Wavelet Hash cho từng ảnh.

Hai giá trị hash sau đó được so sánh bằng Hamming Distance để xác định mức độ khác biệt giữa hai ảnh. Dựa trên một ngưỡng xác định, hệ thống sẽ phân loại cặp ảnh thành **Similar** hoặc **Dissimilar**.

Cuối cùng, kết quả được đánh giá bằng các chỉ số hiệu năng và được trực quan hóa để phục vụ việc phân tích và báo cáo.

Quy trình tổng quát:

```text
Ảnh 1                  Ảnh 2
  │                      │
  ▼                      ▼
Tiền xử lý ảnh      Tiền xử lý ảnh
  │                      │
  ▼                      ▼
Wavelet Transform    Wavelet Transform
  │                      │
  ▼                      ▼
Wavelet Hash         Wavelet Hash
        │
        ▼
  Hamming Distance
        │
        ▼
Tính độ tương đồng
        │
        ▼
So sánh với ngưỡng
        │
        ▼
Similar / Dissimilar
        │
        ▼
Đánh giá và trực quan hóa
```

---

## 2. Bước 1: Nhận ảnh đầu vào

Hệ thống nhận hai ảnh cần được so sánh.

Hai ảnh có thể thuộc một trong hai nhóm:

* **Similar:** Hai ảnh có nội dung hoặc đối tượng tương tự nhau.
* **Dissimilar:** Hai ảnh có nội dung hoặc đối tượng khác nhau.

Hai ảnh tương tự có thể có sự khác biệt về:

* Kích thước.
* Độ sáng.
* Độ tương phản.
* Góc chụp.
* Nhiễu.

Việc xử lý các ảnh có những thay đổi này giúp đánh giá khả năng nhận diện sự tương đồng của thuật toán.

**Đầu vào:**

```text
Image 1
Image 2
```

**Đầu ra:**

```text
Hai ảnh gốc cần được so sánh
```

---

## 3. Bước 2: Tiền xử lý ảnh

Hai ảnh đầu vào được đưa qua module tiền xử lý.

Mục tiêu của bước này là đưa các ảnh về một định dạng thống nhất trước khi thực hiện Wavelet Transform.

Các thao tác chính bao gồm:

### 3.1. Đọc ảnh

Ảnh được đọc từ đường dẫn đầu vào.

### 3.2. Resize

Ảnh được thay đổi về cùng một kích thước.

Việc sử dụng kích thước thống nhất giúp các ảnh có cùng kích thước đầu vào trước khi thực hiện biến đổi Wavelet.

### 3.3. Chuyển sang ảnh xám

Ảnh màu được chuyển thành ảnh grayscale.

Việc chuyển sang ảnh xám giúp giảm số lượng thông tin cần xử lý và tập trung vào đặc trưng cấu trúc, hình dạng và cường độ của ảnh.

### 3.4. Chuẩn hóa giá trị pixel

Giá trị pixel được chuẩn hóa về cùng một khoảng giá trị.

Sau bước tiền xử lý, ảnh có định dạng phù hợp để đưa vào Wavelet Transform.

Quy trình:

```text
Ảnh gốc
   ↓
Đọc ảnh
   ↓
Resize
   ↓
Grayscale
   ↓
Normalize
   ↓
Ảnh đã tiền xử lý
```

**Đầu ra:**

```text
Preprocessed Image 1
Preprocessed Image 2
```

---

## 4. Bước 3: Wavelet Transform

Ảnh đã tiền xử lý được đưa vào module Wavelet Transform.

Mục tiêu của bước này là phân tích ảnh thành các thành phần có đặc trưng khác nhau.

Sau khi thực hiện Discrete Wavelet Transform, ảnh được phân tách thành các hệ số Wavelet.

Ở một mức biến đổi, ảnh có thể được biểu diễn thành:

```text
┌─────────────┬─────────────┐
│             │             │
│     LL      │     LH      │
│             │             │
├─────────────┼─────────────┤
│             │             │
│     HL      │     HH      │
│             │             │
└─────────────┴─────────────┘
```

Trong đó:

* **LL:** Thành phần xấp xỉ, chứa thông tin tổng quát của ảnh.
* **LH:** Thành phần chứa một dạng thông tin chi tiết.
* **HL:** Thành phần chứa thông tin chi tiết theo hướng khác.
* **HH:** Thành phần chứa thông tin chi tiết theo đường chéo.

Các hệ số Wavelet được sử dụng làm đặc trưng cho ảnh.

Quy trình:

```text
Ảnh đã tiền xử lý
        ↓
Discrete Wavelet Transform
        ↓
Wavelet Coefficients
        ↓
LL + LH + HL + HH
```

**Đầu ra:**

```text
Wavelet Coefficients của Image 1
Wavelet Coefficients của Image 2
```

---

## 5. Bước 4: Tạo Wavelet Hash

Các hệ số Wavelet được sử dụng để tạo một mã hash đại diện cho đặc trưng của ảnh.

Quy trình tạo Wavelet Hash bao gồm:

```text
Wavelet Coefficients
        ↓
Chọn đặc trưng phù hợp
        ↓
Quantization
        ↓
Chuyển thành chuỗi bit
        ↓
Wavelet Hash
```

Trong bước lượng tử hóa, các hệ số Wavelet được chuyển thành các giá trị rời rạc.

Sau đó, các giá trị này được biểu diễn dưới dạng nhị phân.

Ví dụ:

```text
Wavelet Coefficients
        ↓
Quantization
        ↓
0 1 1 0 1 0 0 1
        ↓
Wavelet Hash
```

Mỗi ảnh sẽ tạo ra một Wavelet Hash riêng.

**Đầu ra:**

```text
Hash 1: 011010010...
Hash 2: 011011010...
```

---

## 6. Bước 5: Tính Hamming Distance

Hai Wavelet Hash được đưa vào module tính Hamming Distance.

Hamming Distance là số lượng vị trí bit khác nhau giữa hai chuỗi hash có cùng độ dài.

Ví dụ:

```text
Hash 1: 10110110
Hash 2: 10100111
```

Mỗi vị trí có giá trị khác nhau sẽ được tính vào khoảng cách Hamming.

Quy trình:

```text
Wavelet Hash 1
        │
        ├──────► So sánh từng bit ──────► Hamming Distance
        │
Wavelet Hash 2
```

Giá trị Hamming Distance càng nhỏ cho thấy hai hash càng giống nhau.

Do đó, hai ảnh có khả năng có mức độ tương đồng cao hơn.

**Đầu ra:**

```text
Hamming Distance = D
```

---

## 7. Bước 6: Tính độ tương đồng và phân loại

Giá trị Hamming Distance được sử dụng để xác định mức độ tương đồng giữa hai ảnh.

Khoảng cách Hamming nhỏ cho thấy hai hash có ít sự khác biệt.

Ngược lại, khoảng cách Hamming lớn cho thấy hai hash có nhiều sự khác biệt.

Kết quả được so sánh với một giá trị ngưỡng.

```text
Hamming Distance
        ↓
So sánh với Threshold
        ↓
┌─────────────────────────┐
│ Distance ≤ Threshold    │
│        ↓                │
│      Similar            │
└─────────────────────────┘

┌─────────────────────────┐
│ Distance > Threshold    │
│        ↓                │
│     Dissimilar          │
└─────────────────────────┘
```

Ngưỡng phân loại sẽ được lựa chọn và đánh giá dựa trên kết quả thực nghiệm trên dataset.

**Đầu ra:**

```text
Similarity Result

Similar
hoặc
Dissimilar
```

---

## 8. Bước 7: Đánh giá hiệu năng

Kết quả dự đoán của hệ thống được so sánh với nhãn thực tế của dataset.

Quá trình này tạo ra các giá trị:

* **TP (True Positive):** Ảnh tương tự được dự đoán đúng là tương tự.
* **TN (True Negative):** Ảnh không tương tự được dự đoán đúng là không tương tự.
* **FP (False Positive):** Ảnh không tương tự nhưng được dự đoán là tương tự.
* **FN (False Negative):** Ảnh tương tự nhưng được dự đoán là không tương tự.

Từ đó, hệ thống tính các chỉ số:

* Accuracy.
* Sensitivity.
* Specificity.
* ROC Curve.
* AUC.

Quy trình:

```text
Ground Truth
       │
       ▼
Kết quả dự đoán
       │
       ▼
TP / TN / FP / FN
       │
       ▼
Accuracy
Sensitivity
Specificity
       │
       ▼
ROC Curve và AUC
```

**Đầu ra:**

```text
Các chỉ số đánh giá hiệu năng
```

---

## 9. Bước 8: Trực quan hóa và lưu kết quả

Kết quả từ quá trình so sánh và đánh giá được đưa vào module trực quan hóa.

Module này có nhiệm vụ hiển thị kết quả một cách rõ ràng và dễ theo dõi.

Các thông tin có thể được hiển thị bao gồm:

* Ảnh thứ nhất.
* Ảnh thứ hai.
* Wavelet Hash của từng ảnh.
* Hamming Distance.
* Giá trị hoặc mức độ tương đồng.
* Kết quả phân loại Similar/Dissimilar.

Ví dụ:

```text
┌──────────────────────────────────────┐
│             IMAGE COMPARISON         │
├──────────────────────────────────────┤
│ Image 1: image_01.jpg                │
│ Image 2: image_02.jpg                │
├──────────────────────────────────────┤
│ Hamming Distance: 8                  │
│ Similarity: High                     │
│ Result: Similar                      │
└──────────────────────────────────────┘
```

Ngoài ra, hệ thống có thể vẽ:

* Biểu đồ Hamming Distance.
* Biểu đồ độ tương đồng.
* Các hình minh họa kết quả so sánh.
* ROC Curve.

Kết quả được lưu để phục vụ:

* Phân tích thí nghiệm.
* Viết báo cáo.
* Thuyết trình.
* Demo hệ thống.

---

## 10. Tổng hợp quy trình xử lý

Toàn bộ pipeline của hệ thống được tóm tắt như sau:

```text
                 IMAGE 1          IMAGE 2
                    │                │
                    ▼                ▼
              Tiền xử lý       Tiền xử lý
                    │                │
                    ▼                ▼
            Wavelet Transform  Wavelet Transform
                    │                │
                    ▼                ▼
              Wavelet Hash     Wavelet Hash
                    │                │
                    └───────┬────────┘
                            ▼
                    Hamming Distance
                            │
                            ▼
                  Tính độ tương đồng
                            │
                            ▼
                   So sánh với ngưỡng
                            │
                 ┌──────────┴──────────┐
                 ▼                     ▼
              Similar              Dissimilar
                 │                     │
                 └──────────┬──────────┘
                            ▼
                   Đánh giá hiệu năng
                            │
                            ▼
              Trực quan hóa và lưu kết quả
```

---

## 11. Tổng kết

Quy trình xử lý của hệ thống được xây dựng theo dạng pipeline tuần tự, trong đó mỗi bước đảm nhiệm một nhiệm vụ cụ thể.

Hai ảnh đầu vào được tiền xử lý để đưa về cùng định dạng. Sau đó, Wavelet Transform được sử dụng để trích xuất các đặc trưng của ảnh. Các đặc trưng này được chuyển thành Wavelet Hash để tạo một biểu diễn ngắn gọn cho mỗi ảnh.

Hai Wavelet Hash được so sánh bằng Hamming Distance để xác định mức độ khác biệt. Dựa trên giá trị khoảng cách và ngưỡng phân loại, hệ thống đưa ra kết quả Similar hoặc Dissimilar.

Cuối cùng, kết quả được đánh giá bằng các chỉ số hiệu năng và trực quan hóa để hỗ trợ quá trình phân tích, báo cáo và trình bày hệ thống.
