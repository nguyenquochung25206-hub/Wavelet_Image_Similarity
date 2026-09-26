# Wavelet Transform

## 1. Wavelet Transform là gì?

**Wavelet Transform (Biến đổi Wavelet)** là phép biến đổi một tín hiệu (ví dụ ảnh) từ miền không gian sang một biểu diễn dựa trên các wavelet đã co giãn và dịch chuyển (xem `wavelet_theory.md`). Kết quả của phép biến đổi là một tập **hệ số wavelet (wavelet coefficients)**, cho biết "mức độ giống" giữa tín hiệu gốc và wavelet tại từng vị trí, từng tỉ lệ.

Có hai dạng chính:

- **Continuous Wavelet Transform (CWT):** co giãn (a) và dịch (b) biến thiên liên tục → cho biểu diễn rất chi tiết nhưng dư thừa thông tin, chi phí tính toán cao.
- **Discrete Wavelet Transform (DWT):** chỉ lấy mẫu a, b tại các giá trị rời rạc (thường theo lũy thừa của 2) → giảm dư thừa, tính toán nhanh, phù hợp để xử lý ảnh và nén dữ liệu (JPEG2000 dùng DWT).

Trong đề tài này, ta tập trung vào **DWT** vì tính hiệu quả và khả năng ứng dụng thực tế cho bài toán so sánh ảnh.

## 2. Discrete Wavelet Transform (DWT)

DWT thực hiện bằng cách cho tín hiệu đi qua một cặp **bộ lọc số (digital filter)**:

- **Bộ lọc thông thấp (Low-pass filter, L):** giữ lại thành phần biến đổi chậm — thông tin tổng quát, "xấp xỉ" của tín hiệu.
- **Bộ lọc thông cao (High-pass filter, H):** giữ lại thành phần biến đổi nhanh — chi tiết, cạnh, nhiễu.

Sau khi lọc, tín hiệu được **lấy mẫu xuống (downsampling)** hệ số 2 (chỉ giữ lại một nửa số mẫu), vì thông tin đã được nén gọn lại sau lọc.

**Với ảnh (tín hiệu 2 chiều):** DWT được áp dụng lần lượt theo hai chiều — hàng rồi đến cột (hoặc ngược lại):

1. Áp dụng bộ lọc L và H theo **chiều ngang** (theo hàng) cho toàn ảnh, downsample theo chiều ngang → được 2 ảnh con: một ảnh thông thấp (L), một ảnh thông cao (H), mỗi ảnh có chiều rộng giảm còn một nửa.
2. Với mỗi ảnh con đó, tiếp tục áp dụng bộ lọc L và H theo **chiều dọc** (theo cột), downsample theo chiều dọc.

Kết quả: từ 1 ảnh gốc, ta thu được **4 ảnh con** (sub-band), mỗi ảnh có kích thước bằng 1/4 ảnh gốc (giảm một nửa mỗi chiều) — chính là 4 thành phần **LL, LH, HL, HH** (xem mục 4).

Đây là bản chất của thuật toán **Fast Wavelet Transform / Mallat algorithm** — cách cài đặt DWT phổ biến và hiệu quả nhất, được dùng trong hầu hết các thư viện (ví dụ `PyWavelets`).

## 3. Các hệ số Wavelet (Wavelet Coefficients)

Sau khi thực hiện DWT, tín hiệu/ảnh gốc được biểu diễn lại bằng một tập **hệ số wavelet** thay vì giá trị pixel gốc. Hai loại hệ số chính:

- **Hệ số xấp xỉ (Approximation coefficients):** kết quả của việc lọc thông thấp theo cả hai chiều → phản ánh nội dung tổng quát, "phiên bản thu nhỏ mờ" của ảnh gốc.
- **Hệ số chi tiết (Detail coefficients):** kết quả có liên quan đến bộ lọc thông cao → phản ánh cạnh, biên, kết cấu, nhiễu theo từng hướng (ngang, dọc, chéo).

Đặc điểm quan trọng của hệ số wavelet trong bài toán so sánh ảnh:

- Phần lớn **năng lượng (information)** của ảnh tập trung ở hệ số xấp xỉ và một số ít hệ số chi tiết có giá trị lớn — các hệ số còn lại thường nhỏ hoặc gần 0. Đây là cơ sở để **nén** và **rút gọn đặc trưng (feature)** khi so sánh ảnh.
- Có thể so sánh hai ảnh bằng cách so sánh trực tiếp các hệ số wavelet (ví dụ bằng khoảng cách Euclidean, cosine similarity) thay vì so sánh toàn bộ pixel — nhanh hơn và bền vững hơn với nhiễu.

## 4. LL, LH, HL, HH

Sau một lần biến đổi DWT 2 chiều, ảnh được chia thành 4 vùng (sub-band), thường minh họa như sau:

```
Ảnh
 ↓
Wavelet Transform
 ↓
┌────┬────┐
│ LL │ LH │
├────┼────┤
│ HL │ HH │
└────┴────┘
```

Ý nghĩa từng thành phần (chữ đầu = lọc theo chiều ngang, chữ sau = lọc theo chiều dọc):

- **LL (Low-Low):** lọc thông thấp theo cả hai chiều → là **ảnh xấp xỉ**, trông giống ảnh gốc nhưng độ phân giải giảm một nửa mỗi chiều (kích thước = 1/4 ảnh gốc). Đây là thành phần mang nhiều thông tin nhất, dùng làm đầu vào để tiếp tục phân tách ở mức (level) cao hơn.
- **LH (Low-High):** lọc thông thấp theo hàng, thông cao theo cột → làm nổi bật các **cạnh ngang** (thay đổi cường độ theo chiều dọc).
- **HL (High-Low):** lọc thông cao theo hàng, thông thấp theo cột → làm nổi bật các **cạnh dọc** (thay đổi cường độ theo chiều ngang).
- **HH (High-High):** lọc thông cao theo cả hai chiều → làm nổi bật các **cạnh chéo** và **chi tiết/nhiễu** mịn nhất trong ảnh.

**Ứng dụng trong so sánh ảnh:**
- So sánh **LL** giữa hai ảnh → so sánh bố cục/nội dung tổng thể, ít nhạy với nhiễu.
- So sánh **LH, HL, HH** → so sánh về kết cấu, cạnh, chi tiết — hữu ích khi cần phát hiện khác biệt nhỏ (ví dụ ảnh giả mạo, chỉnh sửa cục bộ).

## 5. Level của Wavelet

**Level** (mức phân giải) là số lần áp dụng DWT lặp lại liên tiếp lên thành phần **LL** của bước trước đó.

- **Level 1:** áp dụng DWT một lần trên ảnh gốc → thu được LL1, LH1, HL1, HH1 (kích thước mỗi ảnh = 1/4 ảnh gốc).
- **Level 2:** tiếp tục áp dụng DWT lên **LL1** (chứ không áp dụng lại toàn bộ ảnh gốc) → thu được LL2, LH2, HL2, HH2 (kích thước = 1/16 ảnh gốc).
- Quá trình lặp lại tương tự cho **level 3, 4,...** — mỗi lần kích thước ảnh xấp xỉ giảm tiếp một nửa mỗi chiều.

Minh họa cấu trúc phân rã 2 mức (2-level decomposition):

```
Ảnh gốc
   ↓ DWT level 1
┌──────┬──────┐
│ LL1  │ LH1  │
├──────┼──────┤
│ HL1  │ HH1  │
└──────┴──────┘
   ↓ DWT level 2 (áp dụng tiếp lên LL1)
┌────┬────┬──────┐
│LL2 │LH2 │      │
├────┼────┤ LH1  │
│HL2 │HH2 │      │
├──────────┼──────┤
│   HL1    │ HH1  │
└──────────┴──────┘
```

**Ý nghĩa của việc chọn level:**

- **Level thấp (1-2):** giữ nhiều chi tiết, phù hợp khi cần so sánh cả cấu trúc lớn lẫn chi tiết nhỏ.
- **Level cao (3+):** ảnh xấp xỉ (LL) càng thu nhỏ, càng mang tính "tổng quan cấp cao" (high-level structure), lược bỏ nhiều chi tiết/nhiễu → phù hợp khi chỉ cần so sánh bố cục tổng thể, hoặc muốn giảm chiều dữ liệu mạnh hơn.
- Số level tối đa phụ thuộc vào kích thước ảnh (ảnh càng nhỏ thì càng ít lần chia đôi được).

<<<<<<< HEAD
Việc chọn level phù hợp là một tham số quan trọng cần thử nghiệm trong `compare_wavelets.py`, cùng với việc chọn loại wavelet (Haar, db2, db4, db8, sym2, sym4, coif1).
=======
Việc chọn level phù hợp là một tham số quan trọng cần thử nghiệm trong `compare_wavelets.py`, cùng với việc chọn loại wavelet (Haar, db2, db4, db8, sym2, sym4, coif1).
>>>>>>> f28b4cd ( cap nhat)
