- **Python:** 3.11.9
- **Pytest:** 8.4.2
- **Hệ điều hành:** Windows
- **Ngày kiểm thử:** 26/09/2026

---

## 2. Mục tiêu kiểm thử

Mục tiêu của quá trình kiểm thử là kiểm tra tính đúng đắn và ổn định của các thành phần chính trong hệ thống Wavelet Image Similarity, bao gồm:

- Tiền xử lý ảnh.
- Biến đổi Wavelet.
- Tính toán Wavelet Hash.
- Tính khoảng cách Hamming.
- Kiểm tra pipeline xử lý ảnh.
- Kiểm tra dữ liệu ảnh Similar và Dissimilar.
- Kiểm tra tính deterministic của pipeline.
- Kiểm tra các trường hợp đầu vào không hợp lệ.

---

## 3. Môi trường kiểm thử

| Thành phần | Thông tin |
|---|---|
| Operating System | Windows |
| Python | 3.11.9 |
| Pytest | 8.4.2 |
| Pluggy | 1.6.0 |
| Python executable | PythonSoftwareFoundation.Python.3.11 |
| Test framework | Pytest |

---

## 4. Phạm vi kiểm thử

Các module chính được kiểm thử:

```text
tests/
├── test_hamming_distance.py
├── test_pipeline.py
├── test_preprocessing.py
└── test_wavelet_transform.py

Ngoài ra dự án có:
tests/test_wavelet_hash.py

File này cần được kiểm tra riêng vì khi chạy trực tiếp Pytest báo:
collected 0 items
no tests ran

5. Kết quả kiểm thử
5.1. Hamming Distance
File:
tests/test_hamming_distance.py

Kết quả trong lần chạy toàn bộ test:
PASS

Các nội dung được kiểm tra:
- Hai hash giống nhau có khoảng cách bằng 0.
- Tính khoảng cách giữa hai hash.
- Hai hash hoàn toàn khác nhau.
- Hỗ trợ list.
- Hỗ trợ NumPy array.
- Hỗ trợ Boolean NumPy array.
- Khoảng cách Hamming chuẩn hóa.
- Similarity score.
- So sánh theo threshold.
- Override threshold khi compare.
- Kiểm tra hash có độ dài khác nhau.
- Kiểm tra hash rỗng.
- Kiểm tra hash không phải binary.
- Kiểm tra kiểu dữ liệu không hợp lệ.
- Kiểm tra threshold không hợp lệ.
Kết quả: Tất cả test được thu thập đều PASS.
5.2. Image Preprocessing
File:
tests/test_preprocessing.py

Kết quả:
15 passed

Các nội dung được kiểm tra:
- Load ảnh hợp lệ.
- Xử lý file không tồn tại.
- Xử lý định dạng ảnh không hợp lệ.
- Resize ảnh.
- Resize với kích thước mặc định.
- Xử lý ảnh rỗng.
- Chuyển ảnh màu sang grayscale.
- Xử lý ảnh đã ở dạng grayscale.
- Chuẩn hóa giá trị pixel về khoảng [0, 1].
- Kiểm tra giá trị pixel lớn nhất.
- Kiểm tra giá trị pixel nhỏ nhất.
- Kiểm tra toàn bộ preprocessing pipeline.
- Kiểm tra kích thước tùy chỉnh.
- Kiểm tra pipeline với file không tồn tại.
- Lưu ảnh sau preprocessing.
Kết quả: 15/15 PASS
5.3. Wavelet Transform
File:
tests/test_wavelet_transform.py

Các nội dung được kiểm tra:
- DWT 2D.
- Kích thước các subband.
- Hệ số Wavelet hợp lệ.
- Decomposition nhiều mức.
- Reconstruction ảnh.
- Reconstruction nhiều mức.
- Lấy các subband.
- Kiểm tra level không hợp lệ.
- Energy.
- Energy compaction.
- Normalize ảnh để hiển thị.
- Kiểm tra các Wavelet:
haar
db2
db4
db8
sym2
sym4
coif1

- Kiểm tra pipeline với từng Wavelet.
- Kiểm tra Wavelet similarity.
- Kiểm tra trường hợp hai ảnh giống nhau.
- Kiểm tra trường hợp hai ảnh khác nhau.
- Kiểm tra shape không tương thích.
Kết quả: Tất cả test được thu thập đều PASS.
5.4. Pipeline
File:
tests/test_pipeline.py

Kết quả:
11 passed in 0.34s

Các test được thực hiện:
Test	Kết quả
Similar dataset tồn tại	PASS
Dissimilar dataset tồn tại	PASS
Similar pair có thể load	PASS
Dissimilar pair có thể load	PASS
Preprocessing output	PASS
Wavelet pipeline trên một pair	PASS
Pipeline deterministic	PASS
Similar pair có đủ 2 ảnh	PASS
Dissimilar pair có đủ 2 ảnh	PASS
Toàn bộ ảnh Similar đọc được	PASS
Toàn bộ ảnh Dissimilar đọc được	PASS


Kết quả: 11/11 PASS
6. Kiểm thử toàn bộ hệ thống
Lệnh được sử dụng:
python -m pytest tests/ -v

Kết quả:
==============================================
99 passed in 0.56s
==============================================

Tổng hợp:
Trạng thái	Số lượng
Passed	99
Failed	0
Error	0


Tỷ lệ PASS của các test được Pytest thu thập: 100%.
7. Lỗi phát hiện và đã sửa
Trong quá trình kiểm thử pipeline, phát hiện lỗi trong:
src/wavelet/wavelet_hash.py

Code cũ sử dụng:
ll, _, _, _ = pywt.dwt2(    gray,    wavelet=wavelet)


Tuy nhiên pywt.dwt2() trả về hai phần:
(cA, (cH, cV, cD))


Do đó code cũ gây lỗi:
ValueError:
not enough values to unpack
(expected 4, got 2)

Code được sửa thành cách lấy đúng kết quả của pywt.dwt2().
Sau khi sửa, các test pipeline:
test_wavelet_pipeline_single_pair
test_pipeline_is_deterministic

đều PASS.
8. Kiểm tra tính Deterministic
Test:
test_pipeline_is_deterministic

được sử dụng để kiểm tra việc chạy pipeline nhiều lần trên cùng một ảnh có tạo ra kết quả ổn định hay không.
Kết quả:
PASSED

Điều này cho thấy pipeline hiện tại cho kết quả nhất quán khi cùng một dữ liệu đầu vào được xử lý nhiều lần trong phạm vi test.
9. Kiểm tra Dataset
Pipeline kiểm tra hai nhóm dữ liệu:
Similar
Dissimilar

Các test xác nhận:
- Dataset tồn tại.
- Pair ảnh tồn tại.
- Mỗi pair có hai ảnh.
- Ảnh có thể được đọc thành công.
- Pipeline có thể xử lý ảnh trong dataset.
Tất cả các test liên quan đến dataset đều PASS.
10. Vấn đề còn tồn tại
File:
tests/test_wavelet_hash.py

khi chạy trực tiếp:
python -m pytest tests/test_wavelet_hash.py -v

cho kết quả:
collected 0 items

no tests ran

Điều này có nghĩa Pytest hiện chưa thu thập được test từ file này.
Tuy nhiên, khi chạy:
python -m pytest tests/ -v

Pytest vẫn thu thập và PASS 99 test từ các test file còn lại.
Vì vậy, cần kiểm tra lại tests/test_wavelet_hash.py trước khi hoàn thiện test suite chính thức để bảo đảm các test dành riêng cho Wavelet Hash thực sự được thực thi.
11. Tổng kết
Kết quả kiểm thử hiện tại:
99 PASSED
0 FAILED
0 ERROR

Các thành phần chính đã được kiểm tra gồm:
Image
  │
  ▼
Preprocessing
  │
  ▼
Wavelet Transform
  │
  ▼
Wavelet Hash
  │
  ▼
Hamming Distance
  │
  ▼
Similarity

Các module:
- Image Preprocessing
- Wavelet Transform
- Hamming Distance
- Pipeline
đều vượt qua các test hiện có.
Pipeline cũng đã được kiểm tra với dataset Similar và Dissimilar và có tính deterministic.
12. Kết luận
Dựa trên kết quả kiểm thử ngày 26/09/2026, hệ thống hiện đạt:
99 passed
0 failed
0 error

Kết quả cho thấy các chức năng chính của dự án hoạt động đúng theo các test case hiện có.
Tuy nhiên, tests/test_wavelet_hash.py hiện chưa được Pytest thu thập khi chạy trực tiếp. Vì vậy cần hoàn thiện file test này để việc kiểm thử Wavelet Hash được thực hiện đầy đủ trước khi đóng gói phiên bản cuối cùng của dự án.