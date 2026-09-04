from __future__ import annotations
import argparse
from pathlib import Path
from typing import Tuple, Union

import cv2
import numpy as np

PathLike = Union[str, Path]

DEFAULT_SIZE: Tuple[int, int] = (256, 256)


def load_image(path: PathLike) -> np.ndarray:
    """Đọc ảnh từ đường dẫn và trả về mảng numpy dạng BGR (uint8).

    Raises:
        FileNotFoundError: nếu đường dẫn không tồn tại.
        ValueError: nếu file tồn tại nhưng không đọc được thành ảnh hợp lệ
            (ví dụ sai định dạng, file hỏng).
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Không tìm thấy ảnh: {path}")

    image = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError(f"Không thể đọc ảnh (sai định dạng hoặc file hỏng): {path}")

    return image


def resize_image(image: np.ndarray, size: Tuple[int, int] = DEFAULT_SIZE) -> np.ndarray:
    """Resize ảnh về kích thước cố định `size` = (width, height).

    Dùng nội suy INTER_AREA khi thu nhỏ (chất lượng tốt hơn) và INTER_LINEAR
    khi phóng to.
    """
    if image is None or image.size == 0:
        raise ValueError("Ảnh đầu vào rỗng, không thể resize.")

    h, w = image.shape[:2]
    target_w, target_h = size
    interpolation = cv2.INTER_AREA if (target_w < w or target_h < h) else cv2.INTER_LINEAR

    return cv2.resize(image, (target_w, target_h), interpolation=interpolation)


def to_grayscale(image: np.ndarray) -> np.ndarray:
    """Chuyển ảnh màu (BGR) sang ảnh xám (grayscale).

    Nếu ảnh đầu vào đã là grayscale (2 chiều) thì trả về nguyên trạng.
    """
    if image.ndim == 2:
        return image
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def normalize_image(image: np.ndarray) -> np.ndarray:
    """Chuẩn hóa giá trị pixel về khoảng [0, 1] dạng float32.

    Đây là bước chuẩn hóa cường độ sáng — giúp Wavelet Hash ở bước sau ổn
    định hơn với các ảnh có độ sáng/độ tương phản khác nhau.
    """
    normalized = image.astype(np.float32) / 255.0
    return normalized


def preprocess_image(
    path: PathLike,
    size: Tuple[int, int] = DEFAULT_SIZE,
) -> np.ndarray:
    """Pipeline tiền xử lý đầy đủ: load → resize → grayscale → normalize.

    Trả về mảng numpy 2 chiều, kiểu float32, giá trị trong [0, 1], sẵn sàng
    làm đầu vào cho Wavelet Transform (module của TV2).
    """
    image = load_image(path)
    resized = resize_image(image, size=size)
    gray = to_grayscale(resized)
    normalized = normalize_image(gray)
    return normalized


def save_preprocessed(image: np.ndarray, output_path: PathLike) -> None:
    """Lưu ảnh đã tiền xử lý (float32 trong [0,1]) ra file, dùng để kiểm tra
    trực quan kết quả tiền xử lý.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Chuyển lại về uint8 [0, 255] để có thể lưu thành ảnh xem được.
    image_uint8 = np.clip(image * 255.0, 0, 255).astype(np.uint8)
    cv2.imwrite(str(output_path), image_uint8)


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Tiền xử lý ảnh: resize, grayscale, chuẩn hóa."
    )
    parser.add_argument("--input", required=True, help="Đường dẫn ảnh đầu vào.")
    parser.add_argument("--output", required=True, help="Đường dẫn ảnh đầu ra.")
    parser.add_argument(
        "--width", type=int, default=DEFAULT_SIZE[0], help="Chiều rộng sau resize."
    )
    parser.add_argument(
        "--height", type=int, default=DEFAULT_SIZE[1], help="Chiều cao sau resize."
    )
    return parser


def main() -> None:
    parser = _build_arg_parser()
    args = parser.parse_args()

    processed = preprocess_image(args.input, size=(args.width, args.height))
    save_preprocessed(processed, args.output)
    print(f"Đã tiền xử lý '{args.input}' -> '{args.output}' "
          f"(kích thước {args.width}x{args.height}).")


if __name__ == "__main__":
    main()
