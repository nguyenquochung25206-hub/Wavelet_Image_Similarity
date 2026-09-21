# Kết quả các thí nghiệm

> Phụ trách: TV5. Số liệu sinh bằng `python experiments/evaluate_dataset.py --sweep-wavelets`.
> Kết quả đánh giá tổng hợp (Accuracy, ROC...) xem `evaluation_results.md`.

> **Lưu ý:** module Wavelet Hash của TV3 chưa được cài đặt (`src/wavelet/wavelet_hash.py` đang trống), nên
> các thí nghiệm dưới đây dùng **hash tham chiếu của TV5** (db4, LL 8×8, ngưỡng median, 64 bit). Khi TV3 xong,
> chạy lại lệnh trên để cập nhật.

## 1. Dữ liệu thí nghiệm

- 20 cặp ảnh (kích thước gốc 400×300, 640×480 hoặc 720×540 px; TV1 resize về 256×256), gồm **10 cặp Similar** và **10 cặp Dissimilar** — đạt mức khuyến nghị ≥ 10 cặp mỗi loại
  trong `docs/02_requirements/experiment_requirements.md`.
- Ảnh là hình học đơn sắc (tròn, vuông, thoi, tam giác, sao, chữ thập) đặt giữa nền có màu pastel và vài đốm mờ.
- Cặp **Similar**: cùng hình, thay đổi một biến thể. Cặp **Dissimilar**: hai hình khác nhau, màu khác nhau.

| Biến thể của cặp Similar | Số cặp |
|---|---|
| angle (góc chụp) | 2 (pair_01, pair_07) |
| brightness (độ sáng) | 2 (pair_02, pair_08) |
| size (kích thước) | 2 (pair_03, pair_09) |
| noise (nhiễu) | 2 (pair_04, pair_10) |
| contrast (tương phản) | 1 (pair_05) |
| combo (góc + sáng + nhiễu) | 1 (pair_06) |

## 2. Thí nghiệm: đánh giá trên toàn bộ dataset (yêu cầu mục 3 của đề)

So ground truth với dự đoán để tính TP/TN/FP/FN và các chỉ số. Kết quả (ngưỡng tối ưu 0.1562):

| TP | TN | FP | FN | Accuracy | Sensitivity | Specificity | AUC |
|---|---|---|---|---|---|---|---|
| 5 | 10 | 0 | 5 | 0.75 | 0.50 | 1.00 | 0.825 |

Chi tiết và phân tích: `evaluation_results.md`.

## 3. Thí nghiệm: kết quả từng cặp ảnh (`results/tables/pair_results.csv`)

| Cặp | Nhãn | Biến thể | Hamming | Norm. | Similarity | Dự đoán (ngưỡng 0.1562) | Đúng? |
|---|---|---|---|---|---|---|---|
| similar/pair_01 | Similar | angle | 22 | 0.3438 | 65.6% | Dissimilar | ✗ (FN) |
| similar/pair_02 | Similar | brightness | 0 | 0.0000 | 100.0% | Similar | ✓ |
| similar/pair_03 | Similar | size | 1 | 0.0156 | 98.4% | Similar | ✓ |
| similar/pair_04 | Similar | noise | 20 | 0.3125 | 68.8% | Dissimilar | ✗ (FN) |
| similar/pair_05 | Similar | contrast | 2 | 0.0312 | 96.9% | Similar | ✓ |
| similar/pair_06 | Similar | combo | 24 | 0.3750 | 62.5% | Dissimilar | ✗ (FN) |
| similar/pair_07 | Similar | angle | 28 | 0.4375 | 56.3% | Dissimilar | ✗ (FN) |
| similar/pair_08 | Similar | brightness | 2 | 0.0312 | 96.9% | Similar | ✓ |
| similar/pair_09 | Similar | size | 0 | 0.0000 | 100.0% | Similar | ✓ |
| similar/pair_10 | Similar | noise | 18 | 0.2812 | 71.9% | Dissimilar | ✗ (FN) |
| dissimilar/pair_01 | Dissimilar | — | 26 | 0.4062 | 59.4% | Dissimilar | ✓ |
| dissimilar/pair_02 | Dissimilar | — | 24 | 0.3750 | 62.5% | Dissimilar | ✓ |
| dissimilar/pair_03 | Dissimilar | — | 22 | 0.3438 | 65.6% | Dissimilar | ✓ |
| dissimilar/pair_04 | Dissimilar | — | 22 | 0.3438 | 65.6% | Dissimilar | ✓ |
| dissimilar/pair_05 | Dissimilar | — | 30 | 0.4688 | 53.1% | Dissimilar | ✓ |
| dissimilar/pair_06 | Dissimilar | — | 30 | 0.4688 | 53.1% | Dissimilar | ✓ |
| dissimilar/pair_07 | Dissimilar | — | 18 | 0.2812 | 71.9% | Dissimilar | ✓ |
| dissimilar/pair_08 | Dissimilar | — | 26 | 0.4062 | 59.4% | Dissimilar | ✓ |
| dissimilar/pair_09 | Dissimilar | — | 30 | 0.4688 | 53.1% | Dissimilar | ✓ |
| dissimilar/pair_10 | Dissimilar | — | 18 | 0.2812 | 71.9% | Dissimilar | ✓ |

Thống kê: distance trung bình của cặp Similar là 0.1828, của cặp Dissimilar là 0.3844 (Dissimilar lớn hơn, đúng kỳ vọng).

## 4. Thí nghiệm: độ bền vững với từng loại biến thể

Xem bảng ở `evaluation_results.md` mục 4. Tóm tắt: nhận đúng 100% cặp đổi độ sáng, tương phản, kích thước;
0% cặp xoay góc, nhiễu, và tổ hợp.

## 5. Thí nghiệm: so sánh các loại Wavelet

Xem bảng ở `evaluation_results.md` mục 6 (`results/tables/wavelet_comparison.csv`). Phần đo thời gian DWT,
energy compaction và sai số tái tạo do TV2 thực hiện trong `experiments/compare_wavelets.py`
(`results/tables/compare_wavelets_results.csv`); phần TV5 bổ sung so sánh theo **hiệu quả phân loại** (AUC, Accuracy).

## 6. Hạn chế của thí nghiệm

- Chỉ **20 cặp**: một cặp sai làm Accuracy đổi 5%; AUC và LOO Accuracy dao động lớn nếu thêm/bớt vài cặp.
- Dataset dạng tổng hợp (hình học đơn sắc trên nền phẳng, cùng bố cục ở giữa) nên chưa đại diện cho ảnh tự nhiên.
- Các cặp Dissimilar đều có vật thể ở chính giữa; hash chỉ ghi lại bố cục thô nên loại ảnh này khó với mọi
  hash dựa trên LL (xem nhận xét về Haar ở `evaluation_results.md`).
- Ngưỡng chọn và đánh giá trên cùng tập dữ liệu (đã bổ sung LOO Accuracy để giảm lạc quan).
- Chưa có tập kiểm tra độc lập (validation/test). Nên bổ sung thêm cặp ảnh nếu còn thời gian.
