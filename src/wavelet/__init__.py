"""
Wavelet module — TV2 deliverable cho đề tài Wavelet Image Similarity.

Cung cấp các hàm để đọc ảnh, thực hiện Discrete Wavelet Transform (DWT),
trích xuất các thành phần LL/LH/HL/HH, tái tạo ảnh, và tính độ tương đồng
giữa hai ảnh dựa trên hệ số wavelet.

Ví dụ nhanh:
    >>> from src.wavelet import wavedec2_image, get_subbands
    >>> coeffs = wavedec2_image(image, wavelet="db4", level=1)
    >>> bands = get_subbands(coeffs, level=1)
    >>> bands["LL"], bands["LH"], bands["HL"], bands["HH"]

Xem thêm lý thuyết tại:
    docs/03_research/wavelet_theory.md
    docs/03_research/wavelet_transform.md
"""

from .wavelet_transform import (
    dwt2_image,
    energy,
    get_subbands,
    load_image_grayscale,
    max_dwt_level,
    normalize_for_display,
    reconstruct_image,
    wavedec2_image,
    wavelet_similarity,
)

__all__ = [
    "dwt2_image",
    "energy",
    "get_subbands",
    "load_image_grayscale",
    "max_dwt_level",
    "normalize_for_display",
    "reconstruct_image",
    "wavedec2_image",
    "wavelet_similarity",
]

__version__ = "0.1.0"
