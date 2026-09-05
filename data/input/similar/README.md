# data/input/similar/

Mỗi thư mục `pair_XX/` chứa 2 ảnh cùng đối tượng/nội dung, có thể khác nhau
về góc chụp, độ sáng, kích thước, độ nhiễu, độ tương phản.

```
pair_01/
├── image_01.jpg
└── image_02.jpg
```

## Dataset mẫu hiện tại

10 cặp ảnh hiện có trong thư mục này là ảnh **tổng hợp (synthetic)** do TV1
sinh bằng script [`scripts/prepare_dataset.py`](../../../scripts/prepare_dataset.py),
dùng để cả nhóm chạy thử pipeline trong lúc chưa có ảnh chụp thật. Mỗi cặp
minh họa đúng một (hoặc kết hợp) loại biến thể theo yêu cầu đề bài:

| Pair | Biến thể |
|---|---|
| pair_01 | góc chụp (rotate) |
| pair_02 | độ sáng |
| pair_03 | kích thước ảnh |
| pair_04 | độ nhiễu |
| pair_05 | độ tương phản |
| pair_06 | kết hợp: góc chụp + độ sáng + nhiễu |
| pair_07 | góc chụp (rotate) |
| pair_08 | độ sáng |
| pair_09 | kích thước ảnh |
| pair_10 | độ nhiễu |

Nhãn đầy đủ (ground truth) cho toàn bộ dataset — dùng cho TV5 khi tính
Accuracy/Sensitivity/Specificity/ROC — nằm ở
[`data/input/labels.csv`](../labels.csv).

**Khi có ảnh thật**: chỉ cần thay nội dung các thư mục `pair_XX/` (giữ đúng
tên file `image_01.jpg` / `image_02.jpg`) và cập nhật lại `labels.csv` —
không cần đổi code của các module khác.
