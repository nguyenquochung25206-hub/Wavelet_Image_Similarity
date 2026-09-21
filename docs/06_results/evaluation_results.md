# Kết quả đánh giá (Accuracy, Sensitivity, Specificity, ROC)

> Phụ trách: TV5. Số liệu sinh tự động bằng `python experiments/evaluate_dataset.py --sweep-wavelets`.
> Bảng chi tiết: `results/tables/`; hình: `results/figures/`; báo cáo tự động: `results/reports/evaluation_report.md`.

## 1. Cấu hình đánh giá

| Mục | Giá trị |
|---|---|
| Dataset | 20 cặp: 10 similar + 10 dissimilar (`data/input/labels.csv`) |
| Tiền xử lý | TV1: resize 256×256 → grayscale → chuẩn hóa [0, 1] |
| Wavelet Hash | Bản tham chiếu TV5: DWT `db4`, LL thu về 8×8, lượng tử hóa bằng median → **64 bit** |
| Khoảng cách | Normalized Hamming distance (Hamming / 64) |
| Lớp dương | Similar |
| Quy tắc dự đoán | distance ≤ ngưỡng → Similar |

> **Lưu ý quan trọng:** `src/wavelet/wavelet_hash.py` (TV3) hiện còn trống nên các số liệu dưới đây dùng
> **bản hash tham chiếu của TV5**, không phải hash cuối cùng của nhóm. Khi TV3 hoàn thiện (class
> `WaveletTransform` + `WaveletHash`), chạy lại lệnh trên — script tự dùng hash của nhóm — rồi cập nhật các bảng bên dưới.

## 2. Kết quả tại hai ngưỡng

| Ngưỡng | Giá trị | TP | TN | FP | FN | Accuracy | Sensitivity | Specificity | Precision | F1 |
|---|---|---|---|---|---|---|---|---|---|---|
| Mặc định của TV4 | 0.2500 | 5 | 10 | 0 | 5 | 0.7500 | 0.5000 | 1.0000 | 1.0000 | 0.6667 |
| Tối ưu (Youden) | 0.1562 | 5 | 10 | 0 | 5 | 0.7500 | 0.5000 | 1.0000 | 1.0000 | 0.6667 |

- Hai ngưỡng cho **cùng kết quả** vì khoảng cách của hai nhóm nằm rất xa nhau trong đoạn (0.03; 0.28): mọi
  ngưỡng trong khoảng này đều phân loại giống hệt nhau.
- **AUC = 0.825.**
- **Accuracy leave-one-out = 0.65** (thấp hơn 0.75 — cho thấy kết quả 0.75 hơi lạc quan như đã giải thích ở
  `docs/03_research/evaluation_methods.md`, mục 6).

![ROC](../../results/figures/roc_curve.png)

![Phân bố distance](../../results/figures/distance_distribution.png)

![Confusion matrix](../../results/figures/confusion_matrix.png)

## 3. Đường ROC

Các điểm chính (`results/tables/roc_points.csv`):

| Ngưỡng distance | FPR | TPR |
|---|---|---|
| 0.0312 | 0.0 | 0.5 |
| 0.2812 | 0.2 | 0.6 |
| 0.3438 | 0.4 | 0.8 |
| 0.4062 | 0.7 | 0.9 |
| 0.4688 | 1.0 | 1.0 |

Đường ROC có hình "bậc thang" rõ rệt: từ ngưỡng 0 đến 0.03, TPR lên 0.5 mà FPR vẫn = 0; sau đó muốn tăng
thêm TPR bắt buộc chấp nhận FPR tăng gần như tương ứng (đi sát đường chéo). Nghĩa là hash **tách rất tốt
một nửa số cặp Similar** và **gần như không tách được nửa còn lại**.

## 4. Phân tích theo loại biến thể (cặp Similar)

Tại ngưỡng tối ưu (`results/tables/variation_breakdown.csv`):

| Biến thể | Số cặp | Nhận đúng | Sensitivity |
|---|---|---|---|
| brightness (độ sáng) | 2 | 2 | 1.00 |
| contrast (tương phản) | 1 | 1 | 1.00 |
| size (kích thước) | 2 | 2 | 1.00 |
| angle (góc chụp) | 2 | 0 | 0.00 |
| noise (nhiễu) | 2 | 0 | 0.00 |
| combo (góc + sáng + nhiễu) | 1 | 0 | 0.00 |

Hash **bền vững** với thay đổi độ sáng, độ tương phản, kích thước, nhưng **không bền** với xoay góc và nhiễu.

## 5. Các cặp bị phân loại sai

Không có FP. Có 5 FN (hai ngưỡng 0.1562 và 0.25 cho cùng danh sách):

| Cặp | Biến thể | Distance | Similarity |
|---|---|---|---|
| similar/pair_01 | angle | 22/64 = 0.3438 | 65.6% |
| similar/pair_04 | noise | 20/64 = 0.3125 | 68.8% |
| similar/pair_06 | combo | 24/64 = 0.3750 | 62.5% |
| similar/pair_07 | angle | 28/64 = 0.4375 | 56.3% |
| similar/pair_10 | noise | 18/64 = 0.2812 | 71.9% |

Giải thích (nhận định dựa trên quan sát ảnh và số liệu, chưa kiểm chứng riêng từng giả thuyết):

- **Xoay góc** (pair_01, pair_07, và pair_06 có xoay): ảnh sau xoay có viền xám ở góc và vật thể dịch chuyển
  nên nhiều ô LL đổi giá trị so với median → nhiều bit đảo.
- **Nhiễu** (pair_04, pair_10): nền ảnh gần phẳng nên các hệ số LL ở vùng nền rất gần nhau; nhiễu nhỏ cũng có
  thể đẩy chúng qua lại phía median → bit đảo gần như ngẫu nhiên (khoảng cách 0.28–0.31).
- Khoảng cách của các cặp Similar này (0.28–0.44) **nằm lẫn** trong vùng của cặp Dissimilar (0.28–0.47), nên
  **không có ngưỡng nào** tách được chúng mà không sinh thêm FP. Đây là giới hạn của hash, không phải của ngưỡng.

## 6. So sánh các loại Wavelet (hiệu quả phân loại)

Cùng cấu hình hash (LL 8×8, median), chỉ đổi loại wavelet (`results/tables/wavelet_comparison.csv`):

| Wavelet | AUC | Ngưỡng Youden | Accuracy | Sensitivity | Specificity | LOO Accuracy |
|---|---|---|---|---|---|---|
| haar | 0.310 | 0.0156 | 0.50 | 0.00 | 1.00 | 0.40 |
| db2 | 0.815 | 0.2812 | 0.85 | 0.80 | 0.90 | 0.85 |
| db4 | 0.825 | 0.1562 | 0.75 | 0.50 | 1.00 | 0.65 |
| db8 | 0.840 | 0.1406 | 0.75 | 0.50 | 1.00 | 0.65 |
| sym2 | 0.815 | 0.2812 | 0.85 | 0.80 | 0.90 | 0.85 |
| sym4 | 0.735 | 0.0781 | 0.75 | 0.50 | 1.00 | 0.70 |
| coif1 | 0.830 | 0.4297 | 0.80 | 0.90 | 0.70 | 0.65 |

Nhận xét:

- Các wavelet db2/db4/db8/sym2/coif1 có AUC gần nhau (0.82–0.84); chênh lệch này **nhỏ so với sai số** của
  tập 20 cặp nên **không đủ căn cứ** để nói wavelet nào tốt hơn hẳn.
- **Haar cho AUC 0.31 (< 0.5)**: distance trung bình của cặp Dissimilar chỉ 0.039 trong khi của cặp Similar là
  0.216, tức là distance đang *đảo chiều* (cặp khác nhau lại có hash gần nhau hơn cặp giống nhau). Nhiều khả
  năng vì các ảnh trong dataset đều là một hình đơn sắc ở giữa nền phẳng: ở mức 8×8, LL của Haar chỉ ghi lại
  "có một khối ở giữa" nên hai hình khác nhau cho hash gần như trùng, còn xoay/nhiễu lại làm hash Similar lệch
  nhiều. Đây là giả thuyết, cần TV3 kiểm tra khi thiết kế hash.
- Wavelet đứng đầu về AUC không nhất thiết đứng đầu về Accuracy/LOO: db2/sym2 có LOO cao nhất (0.85) nhưng AUC
  thấp hơn db8.
