# Wavelet Hash

## 1. Tổng quan

Wavelet Hash (WHash) là một phương pháp **perceptual image hashing** được sử dụng để tạo ra một mã Hash đại diện cho đặc trưng trực quan của ảnh.

Khác với các hàm băm mật mã như MD5 hoặc SHA-1, perceptual hashing được thiết kế để các ảnh có nội dung hoặc cấu trúc trực quan tương tự tạo ra các Hash tương tự nhau. Vì vậy, Wavelet Hash phù hợp với các bài toán phát hiện ảnh tương đồng, tìm ảnh trùng lặp và so sánh ảnh.

Wavelet Hash sử dụng **Discrete Wavelet Transform (DWT)** để phân tích ảnh ở miền Wavelet. Một biến thể phổ biến sử dụng Haar Wavelet và các hệ số xấp xỉ (LL) để tạo ra biểu diễn Hash.

Trong project này, Wavelet Hash đóng vai trò là bước chuyển đổi từ ảnh đã tiền xử lý thành một mã nhị phân nhỏ gọn. Mã Hash sau đó được sử dụng ở bước tiếp theo để tính Hamming Distance giữa hai ảnh.

---

## 2. Mục đích của Wavelet Hash

Mục tiêu của Wavelet Hash là:

- Biểu diễn đặc trưng chính của ảnh bằng một mã Hash ngắn.
- Giảm lượng dữ liệu cần sử dụng khi so sánh ảnh.
- Giữ lại các đặc trưng cấu trúc quan trọng của ảnh.
- Giảm ảnh hưởng của một số thay đổi nhỏ như thay đổi kích thước, nén hoặc biến đổi nhẹ.
- Tạo ra một biểu diễn thuận tiện cho việc so sánh bằng Hamming Distance.

Các thuật toán perceptual hashing thường chuyển ảnh thành một biểu diễn nhỏ gọn sao cho ảnh tương đồng có Hash gần nhau, thay vì yêu cầu hai ảnh phải có từng pixel giống hệt nhau.

---

## 3. Phân biệt Perceptual Hash và Cryptographic Hash

Wavelet Hash không phải là cryptographic hash.

### Cryptographic Hash

Ví dụ:

- MD5
- SHA-1
- SHA-256

Mục đích chính của các hàm này là tạo ra một giá trị băm phục vụ kiểm tra dữ liệu và các ứng dụng mật mã.

Chỉ cần thay đổi rất nhỏ trong dữ liệu đầu vào cũng có thể làm giá trị Hash thay đổi rất lớn.

### Perceptual Hash

Perceptual Hash tập trung vào đặc trưng trực quan của dữ liệu.

Ví dụ:

```text
Ảnh A
   ↓
Wavelet Hash
   ↓
101100101010...
```

Một ảnh B có nội dung tương tự A có thể tạo ra:

```text
Ảnh B
   ↓
Wavelet Hash
   ↓
101100101110...
```

Hai Hash có một số bit khác nhau nhưng vẫn có thể được xác định là gần nhau thông qua Hamming Distance.

ImageHash là một thư viện phổ biến hỗ trợ nhiều phương pháp perceptual hashing, trong đó có Wavelet Hash.

---

## 4. Ý tưởng của Wavelet Hash

Wavelet Hash dựa trên ý tưởng phân tích ảnh thành các thành phần tần số bằng Wavelet Transform.

Ảnh sau khi được tiền xử lý được đưa vào DWT. Với biến đổi Wavelet 2D, ảnh được phân tách thành các vùng hệ số thể hiện thông tin ở các mức và hướng khác nhau.

Đối với Haar Wavelet, kết quả phân rã thường được biểu diễn thành bốn vùng:

```text
+-------------+-------------+
|     LL      |     LH      |
|             |             |
+-------------+-------------+
|     HL      |     HH      |
|             |             |
+-------------+-------------+
```

Trong đó:

- **LL**: thành phần xấp xỉ, chứa thông tin tần số thấp.
- **LH**: thành phần chi tiết theo một hướng.
- **HL**: thành phần chi tiết theo hướng còn lại.
- **HH**: thành phần chi tiết tần số cao.

Thành phần LL chứa thông tin tổng quát của ảnh ở độ phân giải thấp và thường được sử dụng trong các biến thể Wavelet Hash.

---

## 5. Quy trình tạo Wavelet Hash

Quy trình tổng quát:

```text
Ảnh đầu vào
    ↓
Resize
    ↓
Grayscale
    ↓
Wavelet Transform
    ↓
Lấy các hệ số Wavelet phù hợp
    ↓
Tính giá trị tham chiếu
    ↓
So sánh các hệ số
    ↓
Chuyển thành 0 / 1
    ↓
Wavelet Hash
```

Mỗi bước có vai trò riêng trong việc tạo ra biểu diễn Hash.

---

## 6. Bước 1 – Resize ảnh

Các ảnh đầu vào có thể có kích thước khác nhau.

Để đảm bảo quá trình Wavelet Transform được thực hiện trên dữ liệu có kích thước thống nhất, ảnh cần được đưa về một kích thước cố định.

Ví dụ:

```text
Ảnh A: 1920 × 1080
Ảnh B: 800 × 600
Ảnh C: 500 × 500

        ↓ Resize

Các ảnh có cùng kích thước xử lý
```

Một số triển khai Wavelet Hash sử dụng kích thước ảnh chuẩn như 64×64 trước khi thực hiện Wavelet Transform. Kích thước cụ thể phụ thuộc vào biến thể thuật toán được sử dụng.

Việc chuẩn hóa kích thước giúp giảm ảnh hưởng của sự khác biệt về kích thước ban đầu.

---

## 7. Bước 2 – Chuyển ảnh sang Grayscale

Wavelet Hash thường hoạt động trên thông tin độ sáng thay vì trực tiếp sử dụng ba kênh màu RGB.

Ảnh màu được chuyển thành ảnh grayscale:

```text
RGB Image
   ↓
Grayscale
   ↓
Intensity Matrix
```

Mỗi pixel lúc này được biểu diễn bằng một giá trị cường độ sáng.

Ví dụ:

```text
[
 [120, 125, 130, ...],
 [118, 123, 128, ...],
 [100, 110, 115, ...],
 ...
]
```

Việc chuyển sang grayscale làm giảm dữ liệu cần xử lý nhưng vẫn giữ lại nhiều thông tin về cấu trúc và độ sáng của ảnh. Các thư viện perceptual hashing phổ biến cũng sử dụng thông tin luminance/grayscale cho các phương pháp như average hash, perceptual hash, difference hash và wavelet hash.

---

## 8. Bước 3 – Wavelet Transform

Sau khi chuẩn hóa ảnh, DWT được áp dụng.

Trong project, Wavelet Transform có nhiệm vụ phân tích ảnh thành các thành phần có tần số khác nhau.

Với Haar Wavelet, quá trình cơ bản dựa trên phép tính trung bình và sai khác giữa các giá trị lân cận.

Một cách biểu diễn đơn giản:

\[
A = \frac{x_1+x_2}{2}
\]

\[
D = \frac{x_1-x_2}{2}
\]

Trong đó:

- `A`: thành phần xấp xỉ.
- `D`: thành phần chi tiết.

Quá trình được thực hiện theo hàng và cột để tạo thành phân rã Wavelet 2D.

---

## 9. Các Sub-band của Wavelet

Sau một mức phân rã Wavelet 2D, ảnh được chia thành bốn sub-band:

### LL

Chứa thông tin xấp xỉ và tần số thấp của ảnh.

LL thể hiện những đặc trưng tổng quát như cấu trúc lớn, bố cục và sự phân bố độ sáng.

### LH

Chứa thông tin chi tiết theo một hướng của ảnh.

### HL

Chứa thông tin chi tiết theo hướng còn lại.

### HH

Chứa thông tin chi tiết tần số cao và thường liên quan đến các thành phần thay đổi nhanh như cạnh và chi tiết nhỏ.

Trong nhiều biến thể Wavelet Hash, các hệ số xấp xỉ được sử dụng để tạo biểu diễn Hash vì chúng đại diện cho cấu trúc tổng quát của ảnh.

---

## 10. Bước 4 – Lựa chọn hệ số Wavelet

Sau khi thực hiện Wavelet Transform, hệ thống cần lựa chọn tập hệ số dùng để tạo Hash.

Một phương pháp phổ biến là sử dụng các hệ số thuộc vùng LL.

Ví dụ:

```text
Wavelet coefficients

+-------------------+
|                   |
|       LL          |
|                   |
+-------------------+
|       Detail      |
|                   |
+-------------------+
```

Các hệ số LL đại diện cho thông tin tần số thấp của ảnh và do đó cung cấp một biểu diễn cô đọng về cấu trúc tổng thể.

Một số triển khai wHash sử dụng vùng LL sau nhiều mức phân rã và sau đó lấy một vùng nhỏ, chẳng hạn 8×8 hệ số, để tạo Hash 64 bit. Đây là một biến thể triển khai; kích thước chính xác cần thống nhất với code của project.

---

## 11. Bước 5 – Tính giá trị tham chiếu

Sau khi lấy các hệ số cần thiết, hệ thống cần một giá trị tham chiếu để chuyển các hệ số liên tục thành bit.

Một cách phổ biến là tính:

- Mean (giá trị trung bình), hoặc
- Median (trung vị).

Sau đó mỗi hệ số được so sánh với giá trị tham chiếu.

Ví dụ sử dụng mean:

\[
mean = \frac{1}{N}\sum_{i=1}^{N}c_i
\]

Trong đó:

- `c_i`: hệ số Wavelet thứ `i`.
- `N`: số lượng hệ số được sử dụng.

---

## 12. Bước 6 – Chuyển hệ số thành bit

Mỗi hệ số được chuyển thành một bit.

Ví dụ sử dụng giá trị trung bình:

\[
h_i =
\begin{cases}
1 & \text{nếu } c_i \geq mean\\
0 & \text{nếu } c_i < mean
\end{cases}
\]

Kết quả là một chuỗi nhị phân:

```text
1011010010110010...
```

Nếu sử dụng 64 hệ số thì kết quả có thể là một Hash gồm 64 bit.

Một số triển khai Wavelet Hash sử dụng median thay vì mean làm ngưỡng lượng tử hóa. Vì vậy, cách lựa chọn mean hay median phải được thống nhất với implementation cụ thể của project.

---

## 13. Ví dụ minh họa

Giả sử sau Wavelet Transform ta thu được 8 hệ số:

```text
[10, 20, 30, 40, 50, 60, 70, 80]
```

Giá trị trung bình:

\[
mean = 45
\]

So sánh từng hệ số với mean:

```text
10 < 45 → 0
20 < 45 → 0
30 < 45 → 0
40 < 45 → 0
50 ≥ 45 → 1
60 ≥ 45 → 1
70 ≥ 45 → 1
80 ≥ 45 → 1
```

Hash thu được:

```text
00001111
```

Đây chỉ là ví dụ minh họa nguyên lý lượng tử hóa hệ số thành bit; Hash thực tế của project có thể có kích thước lớn hơn.

---

## 14. Wavelet Hash và Hamming Distance

Sau khi tạo Hash cho hai ảnh, hệ thống có thể so sánh hai Hash bằng Hamming Distance.

Ví dụ:

```text
Hash A: 10110010
Hash B: 10100011
```

So sánh từng bit:

```text
1 = 1  → giống
0 = 0  → giống
1 = 1  → giống
1 ≠ 0  → khác
0 = 0  → giống
0 = 0  → giống
1 ≠ 1  → giống
0 ≠ 1  → khác
```

Số vị trí khác nhau chính là Hamming Distance.

Do đó:

```text
Wavelet Hash
      ↓
Binary Hash
      ↓
Hamming Distance
      ↓
Đánh giá độ tương đồng
```

Hamming Distance càng nhỏ thì hai Hash càng gần nhau về mặt bit. Trong các hệ thống perceptual hashing, đây là cách phổ biến để so sánh hai mã Hash.

---

## 15. Tại sao sử dụng Wavelet?

Wavelet cho phép phân tích ảnh ở nhiều mức độ phân giải và tách thông tin thành các thành phần tần số khác nhau.

Đối với Wavelet Hash, việc sử dụng các thành phần xấp xỉ giúp tạo một biểu diễn cô đọng hơn của cấu trúc ảnh.

Các phương pháp dựa trên Wavelet cũng đã được nghiên cứu trong các bài toán đánh giá và so sánh ảnh. Ví dụ, HaarPSI sử dụng các hệ số Haar Wavelet để xây dựng các đặc trưng phục vụ đánh giá độ tương đồng ảnh.

---

## 16. Đặc điểm của Wavelet Hash

### Ưu điểm

- Biểu diễn ảnh bằng Hash có kích thước nhỏ.
- Dễ dàng so sánh bằng Hamming Distance.
- Tập trung vào cấu trúc tổng quát của ảnh.
- Có thể giảm ảnh hưởng của một số thay đổi nhỏ so với việc so sánh trực tiếp từng pixel.
- Có thể sử dụng nhiều loại Wavelet khác nhau để thực nghiệm.

### Hạn chế

Wavelet Hash không đảm bảo hai ảnh có nội dung tương đồng luôn tạo ra Hash giống nhau.

Kết quả phụ thuộc vào:

- Phương pháp tiền xử lý.
- Kích thước ảnh sau resize.
- Loại Wavelet.
- Số mức phân rã.
- Số lượng hệ số được sử dụng.
- Cách lựa chọn threshold/giá trị tham chiếu.
- Kích thước Hash.

Do đó, các tham số cần được đánh giá thực nghiệm trên dataset của project.

---

## 17. Các loại Wavelet có thể thử nghiệm

Project có thể thực nghiệm với nhiều Wavelet khác nhau để đánh giá ảnh hưởng của Wavelet đến kết quả.

Một số Wavelet thường gặp:

```text
Haar
db2
db4
db8
sym2
sym4
coif1
```

Các Wavelet khác nhau có đặc điểm về hàm cơ sở và cách biểu diễn tín hiệu khác nhau. Vì vậy, khi thay đổi Wavelet, các hệ số thu được và Hash cuối cùng cũng có thể thay đổi.

Việc so sánh các Wavelet cần được thực hiện trên cùng dataset và cùng quy trình đánh giá để kết quả có thể đối chiếu.

---

## 18. Quy trình Wavelet Hash trong project

Quy trình tổng thể được mô tả như sau:

```text
Input Image
     ↓
Image Preprocessing
     ↓
Resize
     ↓
Grayscale
     ↓
Wavelet Transform
     ↓
Extract Wavelet Coefficients
     ↓
Calculate Reference Value
     ↓
Compare Coefficients
     ↓
Binary Hash
     ↓
Wavelet Hash
```

Sau khi tạo Hash:

```text
Wavelet Hash A ─┐
                ├──→ Hamming Distance
Wavelet Hash B ─┘
                       ↓
                 Similar / Dissimilar
```

---

## 19. Vai trò của Wavelet Hash trong hệ thống

Wavelet Hash là thành phần trung tâm kết nối giữa quá trình xử lý ảnh và quá trình đánh giá độ tương đồng.

Pipeline của hệ thống:

```text
Ảnh đầu vào
    ↓
Preprocessing
    ↓
Wavelet Transform
    ↓
Wavelet Hash
    ↓
Hamming Distance
    ↓
Similarity Decision
    ↓
Evaluation
```

Trong đó:

- `Preprocessing` chuẩn hóa ảnh.
- `Wavelet Transform` phân tích ảnh trong miền Wavelet.
- `Wavelet Hash` tạo biểu diễn nhị phân.
- `Hamming Distance` đo sự khác biệt giữa hai Hash.
- `Evaluation` đánh giá kết quả phân loại trên dataset.

---

## 20. Kết luận

Wavelet Hash là phương pháp perceptual hashing sử dụng Wavelet Transform để tạo một biểu diễn nhỏ gọn của ảnh.

Quá trình cơ bản gồm:

1. Chuẩn hóa kích thước ảnh.
2. Chuyển ảnh sang grayscale.
3. Thực hiện Wavelet Transform.
4. Lựa chọn các hệ số Wavelet.
5. Tính giá trị tham chiếu.
6. Lượng tử hóa các hệ số thành `0` hoặc `1`.
7. Tạo chuỗi Hash.
8. Sử dụng Hamming Distance để so sánh các Hash.

Trong project **Wavelet_Image_Similarity**, Wavelet Hash là bước quan trọng để chuyển đặc trưng của ảnh thành dạng nhị phân, từ đó phục vụ bài toán xác định hai ảnh có tương đồng hay không.