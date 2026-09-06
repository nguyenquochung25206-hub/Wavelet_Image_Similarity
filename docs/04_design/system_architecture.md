# KIẾN TRÚC HỆ THỐNG

## 1. Tổng quan hệ thống

Hệ thống **Wavelet Image Similarity** được xây dựng nhằm đo lường mức độ tương đồng giữa hai ảnh bằng cách sử dụng **Wavelet Transform**, **Wavelet Hash** và **Hamming Distance**.

Hệ thống được thiết kế theo dạng các module độc lập. Mỗi module đảm nhiệm một nhiệm vụ riêng và kết quả đầu ra của module trước sẽ được sử dụng làm đầu vào cho module tiếp theo.

Quy trình tổng quát của hệ thống như sau:

```text
Ảnh đầu vào
    ↓
Tiền xử lý ảnh
    ↓
Wavelet Transform
    ↓
Tạo Wavelet Hash
    ↓
Tính Hamming Distance
    ↓
Phân loại độ tương đồng
    ↓
Đánh giá hiệu năng
    ↓
Trực quan hóa và lưu kết quả
```

Thiết kế theo dạng module giúp hệ thống dễ phát triển, kiểm thử, bảo trì và mở rộng.

---

## 2. Các module của hệ thống

Hệ thống gồm sáu module chính.

### 2.1. Module tiền xử lý ảnh

Module tiền xử lý có nhiệm vụ chuẩn bị ảnh đầu vào trước khi thực hiện biến đổi Wavelet.

Các bước xử lý chính bao gồm:

* Đọc ảnh đầu vào.
* Thay đổi kích thước ảnh về kích thước cố định.
* Chuyển ảnh sang ảnh xám.
* Chuẩn hóa giá trị pixel.

Kết quả của module này là một ảnh xám đã được chuẩn hóa, phù hợp để đưa vào bước Wavelet Transform.

**Đầu vào:** Ảnh gốc.

**Đầu ra:** Ảnh đã được tiền xử lý.

---

### 2.2. Module Wavelet Transform

Module Wavelet Transform thực hiện biến đổi ảnh từ miền không gian sang các hệ số Wavelet.

Sau khi biến đổi, ảnh được phân tách thành các thành phần thông tin khác nhau, bao gồm:

* **LL:** Thành phần xấp xỉ, chứa thông tin tổng quát của ảnh.
* **LH:** Thành phần thể hiện chi tiết theo một hướng.
* **HL:** Thành phần thể hiện chi tiết theo hướng còn lại.
* **HH:** Thành phần thể hiện các chi tiết theo đường chéo.

Các hệ số Wavelet giúp biểu diễn đặc trưng cấu trúc và thông tin tần số của ảnh.

**Đầu vào:** Ảnh đã tiền xử lý.

**Đầu ra:** Các hệ số Wavelet.

---

### 2.3. Module Wavelet Hash

Module Wavelet Hash có nhiệm vụ tạo ra một mã hash dạng nhị phân đại diện cho đặc trưng của ảnh.

Quy trình tạo Wavelet Hash bao gồm:

1. Nhận ảnh đã được tiền xử lý.
2. Thực hiện Wavelet Transform.
3. Lấy các hệ số Wavelet cần thiết.
4. Lượng tử hóa các hệ số.
5. Chuyển kết quả thành chuỗi bit.
6. Tạo Wavelet Hash cuối cùng.

Các ảnh có nội dung hoặc cấu trúc tương tự được kỳ vọng sẽ tạo ra các giá trị hash tương đối giống nhau.

**Đầu vào:** Các hệ số Wavelet.

**Đầu ra:** Wavelet Hash dạng chuỗi bit.

---

### 2.4. Module đo độ tương đồng

Module này có nhiệm vụ so sánh hai Wavelet Hash được tạo ra từ hai ảnh.

Phương pháp chính được sử dụng là **Hamming Distance**.

Hamming Distance đo số lượng vị trí khác nhau giữa hai chuỗi bit có cùng độ dài.

Ví dụ:

```text
Hash 1: 10110110
Hash 2: 10100111
```

Số lượng vị trí bit khác nhau chính là Hamming Distance.

Khoảng cách Hamming càng nhỏ thì hai ảnh càng có xu hướng tương đồng.

Dựa trên giá trị khoảng cách và ngưỡng được lựa chọn, hệ thống sẽ phân loại cặp ảnh thành:

* Similar.
* Dissimilar.

**Đầu vào:** Hai Wavelet Hash.

**Đầu ra:** Hamming Distance và kết quả phân loại.

---

### 2.5. Module đánh giá hiệu năng

Module đánh giá hiệu năng được sử dụng để đo lường mức độ hoạt động của hệ thống trên toàn bộ dataset.

Kết quả dự đoán của hệ thống được so sánh với nhãn thực tế của dữ liệu.

Các chỉ số được sử dụng bao gồm:

* True Positive (TP).
* True Negative (TN).
* False Positive (FP).
* False Negative (FN).
* Accuracy.
* Sensitivity.
* Specificity.
* ROC Curve.
* AUC.

**Đầu vào:** Nhãn thực tế và kết quả dự đoán.

**Đầu ra:** Các chỉ số đánh giá hiệu năng của hệ thống.

---

### 2.6. Module trực quan hóa và lưu kết quả

Module trực quan hóa có nhiệm vụ hiển thị kết quả của quá trình so sánh ảnh theo cách rõ ràng và dễ hiểu.

Module này có thể thực hiện các chức năng:

* Hiển thị hai ảnh được so sánh.
* Hiển thị Wavelet Hash của từng ảnh.
* Hiển thị Hamming Distance.
* Hiển thị độ tương đồng giữa hai ảnh.
* Hiển thị kết quả phân loại Similar hoặc Dissimilar.
* Vẽ biểu đồ liên quan đến độ tương đồng.
* Lưu kết quả để phục vụ phân tích và báo cáo.

Các kết quả trực quan có thể được sử dụng trong:

* Phân tích thí nghiệm.
* Báo cáo project.
* Demo chương trình.
* Thuyết trình.

**Đầu vào:** Kết quả so sánh và kết quả đánh giá.

**Đầu ra:** Hình ảnh trực quan, biểu đồ và các file kết quả.

---

## 3. Sự tương tác giữa các module

Các module của hệ thống hoạt động theo một quy trình xử lý tuần tự.

```text
Ảnh 1 ──┐
        │
        ▼
  Tiền xử lý ảnh
        │
        ▼
 Wavelet Transform
        │
        ▼
 Tạo Wavelet Hash
        │
        ▼
 Hash của ảnh 1 và ảnh 2
        │
        ▼
 Tính Hamming Distance
        │
        ▼
 Phân loại độ tương đồng
        │
        ▼
 Đánh giá hiệu năng
        │
        ▼
Trực quan hóa và lưu kết quả
```

Mỗi module đảm nhiệm một nhiệm vụ riêng biệt. Thiết kế này giúp giảm sự phụ thuộc giữa các thành phần và giúp việc kiểm thử, bảo trì hoặc nâng cấp hệ thống trở nên thuận tiện hơn.

---

## 4. Luồng dữ liệu trong hệ thống

Luồng dữ liệu chính của hệ thống được mô tả như sau:

```text
Ảnh gốc
    ↓
Ảnh đã tiền xử lý
    ↓
Hệ số Wavelet
    ↓
Wavelet Hash
    ↓
Hamming Distance
    ↓
Độ tương đồng
    ↓
Similar / Dissimilar
    ↓
Các chỉ số đánh giá
    ↓
Biểu đồ và kết quả trực quan
```

---

## 5. Ưu điểm của kiến trúc hệ thống

Kiến trúc được thiết kế theo các module riêng biệt mang lại một số ưu điểm:

* Mỗi module có nhiệm vụ rõ ràng.
* Các module có thể được kiểm thử độc lập.
* Có thể thay đổi hoặc cải tiến một module mà ít ảnh hưởng đến các module khác.
* Có thể thử nghiệm và so sánh nhiều loại Wavelet khác nhau.
* Phần trực quan hóa có thể được phát triển độc lập với thuật toán chính.
* Hệ thống có thể mở rộng thêm các chức năng trong tương lai, chẳng hạn như tìm kiếm ảnh tương tự.

---

## 6. Tổng kết

Hệ thống Wavelet Image Similarity được xây dựng theo kiến trúc xử lý theo từng module.

Hệ thống bắt đầu từ việc tiền xử lý ảnh, sau đó sử dụng Wavelet Transform để trích xuất đặc trưng. Các đặc trưng này được sử dụng để tạo Wavelet Hash và so sánh bằng Hamming Distance.

Kết quả cuối cùng được phân loại thành ảnh tương đồng hoặc không tương đồng, sau đó được đánh giá bằng các chỉ số hiệu năng và trực quan hóa để phục vụ việc phân tích, báo cáo và trình bày project.
