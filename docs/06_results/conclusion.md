# Kết luận

> Phụ trách: TV5. Dựa trên số liệu ở `evaluation_results.md` và `experiment_results.md`.

> **Điều kiện:** các kết luận dưới đây áp dụng cho **hash tham chiếu của TV5** (db4, LL 8×8, median, 64 bit) vì
> module Wavelet Hash của TV3 chưa hoàn thiện lúc viết. Khi TV3 xong, chạy lại
> `python experiments/evaluate_dataset.py --sweep-wavelets` và cập nhật các con số trong mục 1.

## 1. Kết quả chính

Trên 20 cặp ảnh (10 similar + 10 dissimilar):

| Chỉ số | Giá trị |
|---|---|
| Ngưỡng chọn theo ROC (Youden) | 0.1562 (≈ 10/64 bit khác nhau) |
| Accuracy | 0.75 (leave-one-out: 0.65) |
| Sensitivity | 0.50 |
| Specificity | 1.00 |
| AUC | 0.825 |

## 2. Kết luận

1. **Hệ thống tách được hai nhóm ở mức khá** (AUC 0.825, không có cặp Dissimilar nào bị nhận nhầm), nhưng
   **bỏ sót một nửa số cặp Similar**.
2. **Hash bền vững với** thay đổi độ sáng, độ tương phản và kích thước (nhận đúng 5/5 cặp), vì Wavelet Hash dựa
   trên LL và ngưỡng median nên ít bị ảnh hưởng bởi thay đổi cường độ chung và thu phóng.
3. **Hash yếu với** xoay góc và nhiễu (0/5 cặp gồm cả cặp tổ hợp): các cặp này có distance 0.28–0.44, lẫn vào vùng
   của cặp Dissimilar (0.28–0.47) nên không ngưỡng nào tách được. Muốn cải thiện phải đổi **cách tạo hash**,
   không phải đổi ngưỡng.
4. **Ngưỡng 0.25 mặc định của TV4 cho kết quả trùng ngưỡng tối ưu từ ROC** trên dataset này, vì hai nhóm cách nhau
   một khoảng trống lớn (distance từ 0.03 đến 0.28). Tuy vậy, dùng ROC vẫn là cách có căn cứ hơn; nên chọn lại
   ngưỡng khi hash của TV3 thay đổi.
5. **Loại wavelet ảnh hưởng đáng kể**: Haar (AUC 0.31) kém hơn nhiều so với db2/db4/db8/sym2/coif1 (AUC 0.82–0.84)
   với cùng cách lượng tử hóa. Sự khác nhau giữa các wavelet dài hơn thì nhỏ so với sai số của 20 cặp nên chưa thể
   khẳng định loại nào tốt nhất.

## 3. Hạn chế

- Chỉ 20 cặp ảnh tổng hợp → kết quả dao động mạnh, chưa đủ để kết luận có ý nghĩa thống kê.
- Ngưỡng chọn và đánh giá trên cùng dữ liệu; LOO Accuracy (0.65) thấp hơn Accuracy (0.75) cho thấy sự lạc quan này.
- Tất cả ảnh đều là một hình đơn sắc ở giữa nền phẳng; cặp Dissimilar cùng bố cục nên là bài toán khó đặc thù cho
  hash dựa trên LL. Chưa kiểm tra trên ảnh tự nhiên.
- Kết quả gắn với hash tham chiếu, không phải hash cuối cùng của TV3.

## 4. Đề xuất

- **TV3:** thử thêm các hệ số chi tiết (LH/HL/HH) vào hash thay vì chỉ LL để bắt cạnh/hình dạng, và thử cách lượng
  tử hóa khác median. Chạy lại `evaluate_dataset.py` để so sánh AUC trước/sau.
- **TV1:** bổ sung thêm cặp ảnh (đặc biệt Dissimilar có bố cục khác nhau, và ảnh thật) để kết quả đáng tin cậy hơn.
- **TV4/TV7:** cập nhật ngưỡng mặc định theo ROC sau khi hash cuối cùng được chốt.
- **Nhóm:** sau khi chốt hash, chạy lại đánh giá và chép lại số liệu vào ba file trong `docs/06_results/`.
