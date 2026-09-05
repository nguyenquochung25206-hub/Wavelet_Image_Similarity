# data/input/dissimilar/

Mỗi thư mục `pair_XX/` chứa 2 ảnh không có nội dung tương đồng.

```
pair_01/
├── image_01.jpg
└── image_02.jpg
```

## Dataset mẫu hiện tại

10 cặp ảnh trong thư mục này là ảnh tổng hợp do
[`scripts/prepare_dataset.py`](../../../scripts/prepare_dataset.py) sinh ra
(TV1), mỗi cặp gồm hai "vật thể" khác loại, khác màu, khác nền — đảm bảo
không có nội dung tương đồng. Ground truth nằm ở
[`data/input/labels.csv`](../labels.csv).

**Khi có ảnh thật**: thay nội dung từng `pair_XX/` bằng hai ảnh không liên
quan và cập nhật lại `labels.csv`.
