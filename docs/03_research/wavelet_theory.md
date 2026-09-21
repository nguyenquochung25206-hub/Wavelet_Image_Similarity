# Wavelet — Lý thuyết cơ bản

## 1. Wavelet là gì?

**Wavelet** (tạm dịch: "sóng con") là một hàm toán học dùng để phân tích tín hiệu (âm thanh, hình ảnh, chuỗi thời gian...) theo cả **miền tần số** lẫn **miền không gian/thời gian** cùng lúc.

Một wavelet có hai đặc điểm quan trọng:

- **Dao động** (giống sóng — "wave"): có giá trị dương và âm xen kẽ, trung bình bằng 0.
- **Cục bộ hóa** (nhỏ — "let"): chỉ tồn tại trong một khoảng hữu hạn rồi tắt dần về 0, khác với sóng sin/cosin kéo dài vô hạn.

Nhờ tính chất "cục bộ" này, wavelet có thể "quét" qua tín hiệu và phát hiện các đặc điểm xảy ra tại một vị trí cụ thể (ví dụ một cạnh, một điểm nhiễu, một chi tiết nhỏ trong ảnh) — điều mà phép biến đổi Fourier (chỉ cho biết tần số nào tồn tại, không biết tồn tại ở đâu) không làm được.

Một wavelet cơ bản gọi là **wavelet mẹ** (mother wavelet), ký hiệu ψ(t). Các wavelet khác được tạo ra bằng cách **co giãn** (scale) và **dịch chuyển** (translate) wavelet mẹ:

```
ψ_{a,b}(t) = (1/√a) · ψ((t - b) / a)
```

- `a`: hệ số tỉ lệ (scale) — a lớn → wavelet "giãn ra" → bắt được đặc trưng tần số thấp (thay đổi chậm, vùng lớn).
- `b`: hệ số dịch (translation) — dịch wavelet đến vị trí cần phân tích.

## 2. Vì sao dùng Wavelet để so sánh ảnh?

Khi so sánh độ giống nhau giữa hai ảnh (image similarity), có nhiều cách tiếp cận: so sánh pixel trực tiếp, histogram màu, đặc trưng học sâu (deep features)... Wavelet là một lựa chọn hiệu quả vì các lý do sau:

- **Biểu diễn đa phân giải (multi-resolution):** Wavelet phân tách ảnh thành nhiều "mức chi tiết" khác nhau — từ thông tin tổng quát (bố cục, màu nền) đến thông tin chi tiết (cạnh, kết cấu, nhiễu). Nhờ đó có thể so sánh ảnh ở nhiều cấp độ: tổng thể trước, chi tiết sau.

- **Tách biệt thông tin cấu trúc và chi tiết:** Wavelet Transform tách ảnh thành thành phần "xấp xỉ" (approximation — giữ nội dung chính) và thành phần "chi tiết" (detail — cạnh, biên, kết cấu). Điều này giúp so sánh ảnh bền vững hơn với nhiễu nhỏ, vì có thể ưu tiên so sánh phần xấp xỉ thay vì từng pixel.

- **Giảm chiều dữ liệu (dimensionality reduction):** Sau biến đổi wavelet, phần lớn năng lượng của ảnh tập trung vào một số hệ số lớn (đặc biệt ở thành phần xấp xỉ). Có thể dùng một tập hệ số nhỏ hơn nhiều so với ảnh gốc để đại diện cho ảnh, giúp so sánh nhanh hơn.

- **Bền vững với biến đổi nhẹ:** So với so sánh pixel-by-pixel (rất nhạy với dịch chuyển, nhiễu, thay đổi độ sáng nhỏ), các hệ số wavelet ở mức xấp xỉ thấp ít bị ảnh hưởng bởi các biến đổi nhỏ này hơn, giúp phép so sánh ổn định hơn.

- **Nắm bắt cả không gian lẫn tần số:** Không giống Fourier Transform (chỉ cho biết ảnh có những tần số nào, mất thông tin vị trí), Wavelet Transform giữ được thông tin **vị trí xuất hiện** của từng đặc trưng tần số — rất quan trọng khi so sánh cấu trúc/kết cấu cục bộ giữa hai ảnh.

- **Chi phí tính toán thấp:** Discrete Wavelet Transform (DWT) có độ phức tạp tuyến tính O(n), nhanh hơn nhiều so với các phép biến đổi tần số khác, phù hợp để triển khai trong hệ thống so sánh ảnh cần tốc độ.

**Tóm lại:** Wavelet cho phép biểu diễn ảnh một cách "phân tầng" theo mức độ chi tiết, tách cấu trúc chính khỏi nhiễu/chi tiết nhỏ, và giữ cả thông tin không gian lẫn tần số — nên rất phù hợp làm đặc trưng (feature) để đo độ giống nhau giữa hai ảnh.

## 3. Các loại Wavelet có thể sử dụng

Có nhiều họ wavelet (wavelet family) khác nhau, mỗi loại có hình dạng và tính chất riêng, phù hợp với từng loại tín hiệu/ảnh khác nhau. Một số loại phổ biến (cũng là các loại nằm trong kế hoạch thử nghiệm của đề tài):

| Wavelet | Đặc điểm chính | Ưu điểm | Nhược điểm |
|---|---|---|---|
| **Haar** | Wavelet đơn giản nhất, dạng bậc thang (step function) | Tính toán cực nhanh, dễ cài đặt, tốt cho phát hiện cạnh sắc nét | Không mượt, dễ gây hiện tượng "khối" (blocking artifact) |
| **Daubechies (db2, db4, db8...)** | Họ wavelet trực giao (orthogonal), số càng lớn thì bộ lọc càng dài, càng mượt | Cân bằng tốt giữa độ mượt và khả năng cục bộ hóa; phổ biến trong nén ảnh, xử lý ảnh | Bộ lọc dài hơn → tính toán chậm hơn Haar |
| **Symlets (sym2, sym4...)** | Biến thể gần đối xứng của Daubechies | Giảm méo pha (phase distortion) so với Daubechies, phù hợp khi cần bảo toàn hình dạng đặc trưng | Tính toán phức tạp hơn Haar |
| **Coiflets (coif1...)** | Có cả wavelet và hàm scaling gần đối xứng, có nhiều moment triệt tiêu | Xấp xỉ tốt các tín hiệu đa thức bậc thấp, giữ cấu trúc tốt | Bộ lọc dài, chi phí tính toán cao hơn |

**Tiêu chí lựa chọn wavelet cho bài toán so sánh ảnh:**

- Cần **tốc độ** → ưu tiên Haar.
- Cần **giữ chi tiết mượt, ít nhiễu khối** → Daubechies hoặc Symlets bậc cao hơn.
- Cần **đối xứng, ít méo pha** khi so sánh cấu trúc/kết cấu → Symlets.
- Cần **xấp xỉ tốt vùng phẳng** (ảnh có nhiều vùng màu đồng nhất) → Coiflets.

Đề tài này sẽ thử nghiệm và so sánh thực nghiệm các loại: **Haar, db2, db4, db8, sym2, sym4, coif1** để chọn ra loại phù hợp nhất cho bài toán so sánh độ giống nhau giữa các ảnh (xem `experiments/compare_wavelets.py`).
