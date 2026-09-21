Wavelet Hash – TV3

1. Mục đích

Module Wavelet Hash là phần việc của TV3 trong project
Wavelet Image Similarity.

Nhiệm vụ của TV3 là nhận kết quả Wavelet Transform từ TV2 và chuyển các
hệ số Wavelet thành một chuỗi bit có độ dài cố định. Chuỗi bit này được đưa
sang TV4 để tính Hamming Distance.

TV3 không chịu trách nhiệm:

Đọc file ảnh.

Resize/grayscale/normalize ảnh.

Thực hiện Wavelet Transform.

Tính Hamming Distance.

Quyết định threshold Similar/Dissimilar.

Pipeline được giữ tách biệt:

Image
  ↓
TV1 – Preprocessing
  ↓
TV2 – Wavelet Transform
  ↓
TV3 – Wavelet Hash
  ↓
TV4 – Hamming Distance
  ↓
TV5 – Evaluation

2. File triển khai

Source code:

src/wavelet/wavelet_hash.py

Unit test:

tests/test_wavelet_hash.py

Tài liệu:

docs/03_research/wavelet_hash.md

3. Ý tưởng của Wavelet Hash

Sau Wavelet Transform, ảnh được biểu diễn bởi các hệ số Wavelet.

Với DWT 2-D ở một mức, ta thường có bốn nhóm hệ số:

┌──────────────┬──────────────┐
│      LL      │      LH      │
├──────────────┼──────────────┤
│      HL      │      HH      │
└──────────────┴──────────────┘

Trong đó:

LL là thành phần xấp xỉ, chứa thông tin cấu trúc tổng quát/độ thấp tần.

LH, HL, HH chứa các thành phần chi tiết theo các hướng.

TV3 sử dụng LL làm đầu vào chính cho hash. Lý do là LL giữ lại cấu trúc
thô của ảnh và ít phụ thuộc hơn vào các thay đổi chi tiết nhỏ so với việc
dùng trực tiếp các hệ số tần số cao.

Đây là lựa chọn thiết kế của project. Nếu thí nghiệm của nhóm cần so sánh
các biến thể Wavelet Hash khác, có thể bổ sung implementation sau mà không
thay đổi API WaveletHash.generate().

4. Thuật toán

Bước 1 – Nhận Wavelet coefficients

WaveletHash.generate() nhận output của TV2.

Implementation hỗ trợ các dạng phổ biến:

Dạng NumPy array

hash_value = WaveletHash().generate(ll)

Trong trường hợp này, array được hiểu là LL/approximation coefficients.

Dạng PyWavelets dwt2

coefficients = (LL, (LH, HL, HH))

hash_value = WaveletHash().generate(coefficients)

Dạng mapping

coefficients = {
    "LL": LL,
    "LH": LH,
    "HL": HL,
    "HH": HH,
}

hash_value = WaveletHash().generate(coefficients)

Việc hỗ trợ nhiều representation giúp TV3 ít phụ thuộc vào cách TV2 đóng gói
kết quả Wavelet.

5. Chuẩn hóa kích thước hash

LL có thể có kích thước khác nhau tùy ảnh đầu vào hoặc cấu hình Wavelet.

Để TV4 luôn nhận được hai hash có cùng độ dài, LL được resize về kích thước
mặc định:

8 × 8

Do đó:

8 × 8 = 64 bits

API cho phép thay đổi kích thước:

hasher = WaveletHash(hash_size=(16, 16))

Khi đó hash có:

16 × 16 = 256 bits

Không nên thay đổi hash_size giữa hai ảnh đang được so sánh.

6. Lượng tử hóa bằng median

Sau khi resize LL về kích thước hash, TV3 tính median của toàn bộ hệ số:

median = median(LL)

Mỗi coefficient được chuyển thành một bit theo quy tắc:

coefficient > median → 1
coefficient ≤ median → 0

Ví dụ:

LL:

1  2
3  4

median = 2.5

Lượng tử hóa:

0  0
1  1

Sau khi flatten:

0011

Đây chính là Wavelet Hash dạng chuỗi bit.

Tại sao dùng median?

Median tạo ra một ngưỡng tương đối với chính ảnh đang xét. Vì vậy thuật toán
không phụ thuộc trực tiếp vào một giá trị pixel/coefficient tuyệt đối cố định.

Quy tắc > được dùng thay vì >= để các giá trị đúng bằng median luôn được
xử lý nhất quán.

7. Độ dài và định dạng hash

Hash mặc định:

hash_size = (8, 8)

nên:

len(hash) = 64

Kiểu dữ liệu trả về:

str

và chỉ chứa hai ký tự:

0
1

Ví dụ:

0110010101110010...

Điều này phù hợp với module Hamming Distance của TV4 vì hai hash có thể được
so sánh theo từng vị trí bit.

8. API chính

8.1. WaveletHash

from src.wavelet.wavelet_hash import WaveletHash

hasher = WaveletHash()

hash_value = hasher.generate(coefficients)

8.2. Custom hash size

hasher = WaveletHash(hash_size=(16, 16))

hash_value = hasher.generate(coefficients)

8.3. Lấy ma trận bit

Ngoài API chính trả về chuỗi, module có:

bits = hasher.generate_bits(coefficients)

Kết quả là NumPy array:

shape = (8, 8)
dtype = uint8

API này phù hợp cho debug hoặc visualization. TV4 nên sử dụng
generate() để nhận chuỗi hash.

8.4. Functional API

Có thể sử dụng:

from src.wavelet.wavelet_hash import generate_wavelet_hash

hash_value = generate_wavelet_hash(coefficients)

API này chỉ là convenience wrapper; thuật toán vẫn được thực hiện bởi
WaveletHash.

9. Hợp đồng dữ liệu giữa TV2 và TV3

TV2 phải cung cấp cho TV3 một trong các dạng sau:

np.ndarray                  # LL

hoặc:

(LL, (LH, HL, HH))          # PyWavelets dwt2

hoặc:

{
    "LL": LL,
    "LH": LH,
    "HL": HL,
    "HH": HH,
}

Trong đó LL phải là ma trận số 2 chiều, không rỗng và không chứa NaN hoặc
inf.

TV3 không yêu cầu TV2 phải sử dụng một class hay một implementation cụ thể.
Đây là điểm giúp hai module có thể phát triển độc lập.

10. Hợp đồng dữ liệu giữa TV3 và TV4

TV3 trả về:

str

Ví dụ:

hash_01 = "001101..."
hash_02 = "001001..."

TV4 nhận hai chuỗi này và tính:

Hamming Distance

Hai hash dùng để so sánh phải có cùng độ dài.

Với cấu hình mặc định:

Hash 1: 64 bits
Hash 2: 64 bits

TV3 đảm bảo cùng hash_size sẽ tạo ra cùng độ dài hash.

11. Kiểm tra input

Implementation không âm thầm xử lý dữ liệu sai.

Các trường hợp bị từ chối gồm:

hash_size không có dạng (width, height).

Kích thước hash bằng 0 hoặc âm.

coefficients rỗng.

coefficients không phải dữ liệu số.

coefficients không phải ma trận 2 chiều sau khi lấy LL.

coefficients chứa NaN.

coefficients chứa inf.

mapping không có LL/approximation hợp lệ.

tuple/list không có cấu trúc Wavelet được hỗ trợ.

Các lỗi được báo bằng:

ValueError

Điều này giúp phát hiện lỗi ở ranh giới giữa TV2 và TV3 sớm hơn thay vì tạo ra
một hash sai mà không báo lỗi.

12. Tính deterministic

Cùng một input và cùng một cấu hình:

WaveletHash(hash_size=(8, 8))

phải luôn tạo cùng một hash.

Ví dụ:

hash_1 = hasher.generate(coefficients)
hash_2 = hasher.generate(coefficients)

assert hash_1 == hash_2

Tính deterministic là yêu cầu quan trọng vì kết quả TV3 sẽ được sử dụng trực
tiếp trong Hamming Distance và các thí nghiệm của TV5.

13. Ví dụ tích hợp với TV2

Nếu TV2 sử dụng PyWavelets và trả về dạng:

coefficients = pywt.dwt2(image, "haar")

thì TV3 có thể dùng trực tiếp:

from src.wavelet.wavelet_hash import WaveletHash

wavelet_hash = WaveletHash()

hash_value = wavelet_hash.generate(coefficients)

Nếu TV2 chỉ trả về LL:

ll = coefficients[0]

hash_value = wavelet_hash.generate(ll)

Không cần chuyển đổi sang một class trung gian.

14. Ví dụ tích hợp với pipeline

Luồng sử dụng dự kiến:

from src.wavelet.wavelet_transform import WaveletTransform
from src.wavelet.wavelet_hash import WaveletHash
from src.similarity.hamming_distance import HammingDistance

transform = WaveletTransform()
hasher = WaveletHash()
hamming = HammingDistance()

transformed_01 = transform.transform(processed_01)
transformed_02 = transform.transform(processed_02)

hash_01 = hasher.generate(transformed_01)
hash_02 = hasher.generate(transformed_02)

distance = hamming.calculate(hash_01, hash_02)

Đây cũng chính là API mà integration test hiện tại của project đang hướng tới:

WaveletTransform()
      ↓
transform(...)
      ↓
WaveletHash()
      ↓
generate(...)
      ↓
HammingDistance()
      ↓
calculate(...)

15. Unit Test

File:

tests/test_wavelet_hash.py

Các nhóm kiểm thử chính:

Test

Mục tiêu

Default hash length

Kiểm tra hash mặc định có 64 bit

Deterministic

Cùng input tạo cùng hash

Custom hash size

Kiểm tra kích thước hash tùy chỉnh

PyWavelets output

Kiểm tra (LL, (LH, HL, HH))

Mapping output

Kiểm tra dạng LL/LH/HL/HH

Median quantization

Kiểm tra quy tắc lượng tử hóa

generate_bits()

Kiểm tra ma trận bit

Functional API

Kiểm tra wrapper

Invalid hash size

Kiểm tra validation

Invalid coefficients

Kiểm tra validation

Chạy riêng test TV3:

pytest tests/test_wavelet_hash.py -v

Chạy toàn bộ test:

pytest tests/ -v

16. Giới hạn của implementation

Wavelet Hash không phải là một cryptographic hash như SHA-256.

Mục tiêu của nó là tạo perceptual hash:

ảnh
 ↓
đặc trưng Wavelet
 ↓
bit representation

Do đó hai ảnh có nội dung tương đồng có thể có hash gần nhau, trong khi hai
ảnh khác nhau có xu hướng có hash khác nhau. Việc xác định chính xác
threshold để phân loại Similar/Dissimilar không thuộc TV3 mà thuộc bước
thực nghiệm/evaluation.

Đặc biệt, không nên ghi cố định một threshold vào tài liệu TV3 nếu threshold
chưa được xác định từ dataset thực tế.

17. Kết luận

TV3 cung cấp một module độc lập, deterministic và có API rõ ràng:

WaveletHash().generate(coefficients)

Module lấy LL/approximation coefficients từ Wavelet Transform, resize về kích
thước hash cố định, lượng tử hóa theo median và trả về chuỗi bit.

Thiết kế này đảm bảo:

TV2
 ↓
Wavelet coefficients
 ↓
TV3
 ↓
64-bit Wavelet Hash
 ↓
TV4
 ↓
Hamming Distance

đồng thời giữ cho TV3 không phụ thuộc chặt vào cách TV2 triển khai nội bộ.
