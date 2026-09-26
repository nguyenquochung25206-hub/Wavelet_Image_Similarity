"""
Image preprocessing module.

Pipeline:

    Load image
        ↓
    Resize
        ↓
    Grayscale
        ↓
    Normalize [0, 1]

Output:
    numpy.ndarray
    2D grayscale
    float32
    pixel values in [0, 1]
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Tuple, Union

import cv2
import numpy as np


PathLike = Union[str, Path]

DEFAULT_SIZE: Tuple[int, int] = (256, 256)


# ---------------------------------------------------------------------------
# Load image
# ---------------------------------------------------------------------------

def load_image(path: PathLike) -> np.ndarray:
    """
    Load an image as BGR uint8 numpy array.

    Uses np.fromfile + cv2.imdecode so that Windows paths containing
    Vietnamese/Unicode characters are supported correctly.
    """

    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(
            f"Không tìm thấy ảnh: {path}"
        )

    image_data = np.fromfile(
        str(path),
        dtype=np.uint8
    )

    if image_data.size == 0:
        raise ValueError(
            f"File ảnh rỗng: {path}"
        )

    image = cv2.imdecode(
        image_data,
        cv2.IMREAD_COLOR
    )

    if image is None:
        raise ValueError(
            f"Không thể đọc ảnh "
            f"(sai định dạng hoặc file hỏng): {path}"
        )

    return image


# ---------------------------------------------------------------------------
# Resize
# ---------------------------------------------------------------------------

def resize_image(
    image: np.ndarray,
    size: Tuple[int, int] = DEFAULT_SIZE
) -> np.ndarray:
    """
    Resize image to (width, height).

    INTER_AREA:
        Used when reducing image size.

    INTER_LINEAR:
        Used when enlarging image size.
    """

    if image is None or image.size == 0:
        raise ValueError(
            "Ảnh đầu vào rỗng, không thể resize."
        )

    if len(size) != 2:
        raise ValueError(
            "size phải có dạng (width, height)."
        )

    target_w, target_h = size

    if target_w <= 0 or target_h <= 0:
        raise ValueError(
            "width và height phải lớn hơn 0."
        )

    h, w = image.shape[:2]

    interpolation = (
        cv2.INTER_AREA
        if target_w < w or target_h < h
        else cv2.INTER_LINEAR
    )

    return cv2.resize(
        image,
        (target_w, target_h),
        interpolation=interpolation
    )


# ---------------------------------------------------------------------------
# Grayscale
# ---------------------------------------------------------------------------

def to_grayscale(image: np.ndarray) -> np.ndarray:
    """
    Convert BGR image to grayscale.

    If the input is already grayscale, return it unchanged.
    """

    if image is None or image.size == 0:
        raise ValueError(
            "Ảnh đầu vào rỗng, không thể chuyển grayscale."
        )

    if image.ndim == 2:
        return image

    if image.ndim != 3:
        raise ValueError(
            "Ảnh phải có 2 hoặc 3 chiều."
        )

    return cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )


# ---------------------------------------------------------------------------
# Normalize
# ---------------------------------------------------------------------------

def normalize_image(image: np.ndarray) -> np.ndarray:
    """
    Normalize pixel values to [0, 1].

    Output:
        numpy.ndarray
        dtype=float32
    """

    if image is None or image.size == 0:
        raise ValueError(
            "Ảnh đầu vào rỗng, không thể normalize."
        )

    image = np.asarray(
        image,
        dtype=np.float32
    )

    # Nếu ảnh đang ở dạng uint8 / giá trị [0, 255]
    if image.max() > 1.0:
        image = image / 255.0

    return np.clip(
        image,
        0.0,
        1.0
    ).astype(np.float32)


# ---------------------------------------------------------------------------
# Complete preprocessing pipeline
# ---------------------------------------------------------------------------

def preprocess_image(
    path: PathLike,
    size: Tuple[int, int] = DEFAULT_SIZE
) -> np.ndarray:
    """
    Complete preprocessing pipeline:

        load
          ↓
        resize
          ↓
        grayscale
          ↓
        normalize
    """

    image = load_image(path)

    resized = resize_image(
        image,
        size=size
    )

    gray = to_grayscale(
        resized
    )

    normalized = normalize_image(
        gray
    )

    return normalized


# ---------------------------------------------------------------------------
# Save preprocessed image
# ---------------------------------------------------------------------------

def save_preprocessed(
    image: np.ndarray,
    output_path: PathLike
) -> None:
    """
    Save normalized image to an image file.

    Input:
        float32 image in [0, 1]

    Output:
        uint8 image in [0, 255]
    """

    if image is None or image.size == 0:
        raise ValueError(
            "Ảnh đầu vào rỗng, không thể lưu."
        )

    output_path = Path(output_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    image_uint8 = np.clip(
        image * 255.0,
        0,
        255
    ).astype(np.uint8)

    success = cv2.imwrite(
        str(output_path),
        image_uint8
    )

    if not success:
        raise IOError(
            f"Không thể lưu ảnh: {output_path}"
        )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Tiền xử lý ảnh: "
            "resize → grayscale → normalize."
        )
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Đường dẫn ảnh đầu vào."
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Đường dẫn ảnh đầu ra."
    )

    parser.add_argument(
        "--width",
        type=int,
        default=DEFAULT_SIZE[0],
        help="Chiều rộng sau resize."
    )

    parser.add_argument(
        "--height",
        type=int,
        default=DEFAULT_SIZE[1],
        help="Chiều cao sau resize."
    )

    return parser


def main() -> None:
    parser = _build_arg_parser()

    args = parser.parse_args()

    processed = preprocess_image(
        args.input,
        size=(args.width, args.height)
    )

    save_preprocessed(
        processed,
        args.output
    )

    print(
        f"Đã tiền xử lý '{args.input}' "
        f"-> '{args.output}' "
        f"(kích thước {args.width}x{args.height})."
    )


if __name__ == "__main__":
    main()