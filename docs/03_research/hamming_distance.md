<<<<<<< HEAD
Hamming Distance trong bài toán so sánh ảnh

1. Vai trò trong hệ thống

Sau khi hai ảnh được tiền xử lý, biến đổi Wavelet và tạo Wavelet Hash, phần của TV4 nhận hai chuỗi hash này để đo mức độ khác nhau. Phương pháp sử dụng là Hamming Distance.

Pipeline liên quan trực tiếp đến TV4:

Wavelet Hash 1 ─┐
                ├─> Hamming Distance ─> Similarity ─> Threshold ─> Similar / Dissimilar
Wavelet Hash 2 ─┘

TV4 không tạo hash. Hash được nhận từ module src/wavelet/wavelet_hash.py của TV3.

2. Khái niệm Hamming Distance

Hamming Distance là số vị trí có giá trị khác nhau giữa hai chuỗi bit cùng độ dài.

Với hai hash:

Hash 1: 1 0 1 1 0 1 1 0
Hash 2: 1 0 1 0 0 1 1 1
               ↑       ↑

Có 2 vị trí khác nhau nên:

Hamming Distance = 2

Nếu hai hash giống hệt nhau thì khoảng cách bằng 0. Khoảng cách càng nhỏ thì hai hash càng giống nhau, do đó hai ảnh có xu hướng tương đồng hơn.

Công thức:

D(H1, H2) = số vị trí i sao cho H1[i] ≠ H2[i]

3. Hamming Distance chuẩn hóa

Khoảng cách thô phụ thuộc vào độ dài hash. Ví dụ khoảng cách 8 trên hash 64 bit và khoảng cách 8 trên hash 256 bit không thể hiểu giống nhau. Vì vậy module có thêm khoảng cách chuẩn hóa:

Normalized Distance = Hamming Distance / Hash Length

Giá trị nằm trong khoảng từ 0 đến 1:

0: hai hash hoàn toàn giống nhau.

Giá trị càng gần 1: hai hash càng khác nhau.

Ví dụ hash dài 64 bit, có 8 bit khác nhau:

Normalized Distance = 8 / 64 = 0.125

4. Tính độ tương đồng

Độ tương đồng được tính từ khoảng cách chuẩn hóa:

Similarity = 1 - Normalized Distance

Với ví dụ trên:

Similarity = 1 - 0.125 = 0.875 = 87.5%

Similarity càng lớn thì hai ảnh càng giống nhau theo biểu diễn Wavelet Hash.

5. Phân loại Similar / Dissimilar

Kết quả được quyết định bằng một ngưỡng threshold:

Nếu Normalized Distance <= Threshold  → Similar
Nếu Normalized Distance >  Threshold  → Dissimilar

Trong code TV4 sử dụng ngưỡng thử nghiệm mặc định 0.25. Đây không phải ngưỡng kết luận cuối cùng. Theo yêu cầu của project, threshold chính thức nên được lựa chọn sau khi TV5 đánh giá trên dataset và phân tích ROC để cân bằng Sensitivity và Specificity.

Việc dùng ngưỡng chuẩn hóa giúp chương trình vẫn hoạt động hợp lý khi nhóm thay đổi độ dài Wavelet Hash.

6. Cài đặt trong src/similarity/hamming_distance.py

Class chính:

hamming = HammingDistance(threshold=0.25)

Tính khoảng cách thô

distance = hamming.calculate(hash_1, hash_2)

Ví dụ:

hash_1 = "10110110"
hash_2 = "10100111"

distance = hamming.calculate(hash_1, hash_2)
print(distance)

Kết quả:

2

Tính khoảng cách chuẩn hóa

normalized = hamming.normalized(hash_1, hash_2)

Tính độ tương đồng

similarity = hamming.similarity(hash_1, hash_2)

Lấy toàn bộ kết quả trong một lần

result = hamming.compare(hash_1, hash_2)

print(result.distance)
print(result.normalized_distance)
print(result.similarity)
print(result.label)

Kết quả trả về gồm:

distance             : số bit khác nhau
normalized_distance  : khoảng cách chuẩn hóa [0, 1]
similarity            : độ tương đồng [0, 1]
label                 : Similar hoặc Dissimilar

7. Kiểm tra dữ liệu đầu vào

Để tránh kết quả sai, module kiểm tra:

Hai hash không được rỗng.

Hash chỉ được chứa giá trị nhị phân 0 và 1.

Hai hash phải có cùng độ dài.

Threshold phải nằm trong khoảng [0, 1].

Nếu hai hash khác độ dài, chương trình báo lỗi thay vì cố tính khoảng cách.

8. Ý nghĩa đối với bài toán ảnh

Hamming Distance không so sánh trực tiếp từng pixel của hai ảnh. Nó so sánh hai mã Wavelet Hash đại diện cho đặc trưng của ảnh. Nhờ vậy bước so sánh nhanh hơn rất nhiều so với việc đối chiếu toàn bộ ma trận pixel.

Tuy nhiên, chất lượng kết quả còn phụ thuộc vào các bước trước đó: preprocessing, loại Wavelet, cách chọn hệ số và cách tạo hash. Vì vậy Hamming Distance chỉ là bước đo sự khác nhau giữa hai biểu diễn đã được tạo ra.

9. Tóm tắt phần TV4

TV4 thực hiện ba nhiệm vụ chính:

1. Nhận Hash 1 và Hash 2 từ TV3
2. Tính Hamming Distance + Similarity
3. So sánh với threshold để kết luận Similar / Dissimilar

Đầu ra của TV4 được chuyển cho TV5 để đánh giá Accuracy, Sensitivity, Specificity và ROC/AUC trên toàn bộ dataset.
=======
Hamming Distance trong bài toán so sánh ảnh

1. Vai trò trong hệ thống

Sau khi hai ảnh được tiền xử lý, biến đổi Wavelet và tạo Wavelet Hash, phần của TV4 nhận hai chuỗi hash này để đo mức độ khác nhau. Phương pháp sử dụng là Hamming Distance.

Pipeline liên quan trực tiếp đến TV4:

Wavelet Hash 1 ─┐
                ├─> Hamming Distance ─> Similarity ─> Threshold ─> Similar / Dissimilar
Wavelet Hash 2 ─┘

TV4 không tạo hash. Hash được nhận từ module src/wavelet/wavelet_hash.py của TV3.

2. Khái niệm Hamming Distance

Hamming Distance là số vị trí có giá trị khác nhau giữa hai chuỗi bit cùng độ dài.

Với hai hash:

Hash 1: 1 0 1 1 0 1 1 0
Hash 2: 1 0 1 0 0 1 1 1
               ↑       ↑

Có 2 vị trí khác nhau nên:

Hamming Distance = 2

Nếu hai hash giống hệt nhau thì khoảng cách bằng 0. Khoảng cách càng nhỏ thì hai hash càng giống nhau, do đó hai ảnh có xu hướng tương đồng hơn.

Công thức:

D(H1, H2) = số vị trí i sao cho H1[i] ≠ H2[i]

3. Hamming Distance chuẩn hóa

Khoảng cách thô phụ thuộc vào độ dài hash. Ví dụ khoảng cách 8 trên hash 64 bit và khoảng cách 8 trên hash 256 bit không thể hiểu giống nhau. Vì vậy module có thêm khoảng cách chuẩn hóa:

Normalized Distance = Hamming Distance / Hash Length

Giá trị nằm trong khoảng từ 0 đến 1:

0: hai hash hoàn toàn giống nhau.

Giá trị càng gần 1: hai hash càng khác nhau.

Ví dụ hash dài 64 bit, có 8 bit khác nhau:

Normalized Distance = 8 / 64 = 0.125

4. Tính độ tương đồng

Độ tương đồng được tính từ khoảng cách chuẩn hóa:

Similarity = 1 - Normalized Distance

Với ví dụ trên:

Similarity = 1 - 0.125 = 0.875 = 87.5%

Similarity càng lớn thì hai ảnh càng giống nhau theo biểu diễn Wavelet Hash.

5. Phân loại Similar / Dissimilar

Kết quả được quyết định bằng một ngưỡng threshold:

Nếu Normalized Distance <= Threshold  → Similar
Nếu Normalized Distance >  Threshold  → Dissimilar

Trong code TV4 sử dụng ngưỡng thử nghiệm mặc định 0.25. Đây không phải ngưỡng kết luận cuối cùng. Theo yêu cầu của project, threshold chính thức nên được lựa chọn sau khi TV5 đánh giá trên dataset và phân tích ROC để cân bằng Sensitivity và Specificity.

Việc dùng ngưỡng chuẩn hóa giúp chương trình vẫn hoạt động hợp lý khi nhóm thay đổi độ dài Wavelet Hash.

6. Cài đặt trong src/similarity/hamming_distance.py

Class chính:

hamming = HammingDistance(threshold=0.25)

Tính khoảng cách thô

distance = hamming.calculate(hash_1, hash_2)

Ví dụ:

hash_1 = "10110110"
hash_2 = "10100111"

distance = hamming.calculate(hash_1, hash_2)
print(distance)

Kết quả:

2

Tính khoảng cách chuẩn hóa

normalized = hamming.normalized(hash_1, hash_2)

Tính độ tương đồng

similarity = hamming.similarity(hash_1, hash_2)

Lấy toàn bộ kết quả trong một lần

result = hamming.compare(hash_1, hash_2)

print(result.distance)
print(result.normalized_distance)
print(result.similarity)
print(result.label)

Kết quả trả về gồm:

distance             : số bit khác nhau
normalized_distance  : khoảng cách chuẩn hóa [0, 1]
similarity            : độ tương đồng [0, 1]
label                 : Similar hoặc Dissimilar

7. Kiểm tra dữ liệu đầu vào

Để tránh kết quả sai, module kiểm tra:

Hai hash không được rỗng.

Hash chỉ được chứa giá trị nhị phân 0 và 1.

Hai hash phải có cùng độ dài.

Threshold phải nằm trong khoảng [0, 1].

Nếu hai hash khác độ dài, chương trình báo lỗi thay vì cố tính khoảng cách.

8. Ý nghĩa đối với bài toán ảnh

Hamming Distance không so sánh trực tiếp từng pixel của hai ảnh. Nó so sánh hai mã Wavelet Hash đại diện cho đặc trưng của ảnh. Nhờ vậy bước so sánh nhanh hơn rất nhiều so với việc đối chiếu toàn bộ ma trận pixel.

Tuy nhiên, chất lượng kết quả còn phụ thuộc vào các bước trước đó: preprocessing, loại Wavelet, cách chọn hệ số và cách tạo hash. Vì vậy Hamming Distance chỉ là bước đo sự khác nhau giữa hai biểu diễn đã được tạo ra.

9. Tóm tắt phần TV4

TV4 thực hiện ba nhiệm vụ chính:

1. Nhận Hash 1 và Hash 2 từ TV3
2. Tính Hamming Distance + Similarity
3. So sánh với threshold để kết luận Similar / Dissimilar

Đầu ra của TV4 được chuyển cho TV5 để đánh giá Accuracy, Sensitivity, Specificity và ROC/AUC trên toàn bộ dataset.
>>>>>>> f28b4cd ( cap nhat)
