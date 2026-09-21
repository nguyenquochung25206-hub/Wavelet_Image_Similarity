"""
wavelet_transform.py — TV2

Thực hiện Discrete Wavelet Transform (DWT) trên ảnh bằng thư viện PyWavelets
(pywt), trích xuất các thành phần LL / LH / HL / HH, tái tạo lại ảnh, và
tính độ tương đồng giữa hai ảnh dựa trên hệ số wavelet.

Lý thuyết liên quan: xem docs/03_research/wavelet_transform.md

Yêu cầu cài đặt:
    pip install PyWavelets numpy pillow

Ví dụ cơ bản (đúng như đề bài):
    >>> import pywt
    >>> coeffs = pywt.wavedec2(image, wavelet="db4", level=1)
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple, Union

import numpy as np

try:
    import pywt
except ImportError as _exc:  # pragma: no cover - chỉ xảy ra khi chưa cài pywt
    pywt = None
    _PYWT_IMPORT_ERROR: Optional[ImportError] = _exc
else:
    _PYWT_IMPORT_ERROR = None


# Danh sách wavelet dùng để thử nghiệm trong experiments/compare_wavelets.py
SUPPORTED_WAVELETS = ["haar", "db2", "db4", "db8", "sym2", "sym4", "coif1"]

DetailTuple = Tuple[np.ndarray, np.ndarray, np.ndarray]
WaveDecCoeffs = List[Union[np.ndarray, DetailTuple]]
Subbands = Dict[str, Optional[np.ndarray]]


def _require_pywt() -> None:
    """Báo lỗi rõ ràng nếu PyWavelets chưa được cài đặt."""
    if pywt is None:  # pragma: no cover
        raise ImportError(
            "Cần cài đặt PyWavelets để dùng wavelet_transform.py: "
            "pip install PyWavelets"
        ) from _PYWT_IMPORT_ERROR


# --------------------------------------------------------------------------- #
# Đọc / tiền xử lý ảnh
# --------------------------------------------------------------------------- #

def load_image_grayscale(path: str) -> np.ndarray:
    """
    Đọc ảnh từ đường dẫn và chuyển sang ảnh xám (grayscale).

    Trả về mảng numpy float64, giá trị chuẩn hóa trong khoảng [0, 1].
    """
    from PIL import Image

    with Image.open(path) as im:
        gray = im.convert("L")
        arr = np.asarray(gray, dtype=np.float64) / 255.0
    return arr


def max_dwt_level(image: np.ndarray, wavelet: str = "db4") -> int:
    """Trả về số level (mức) phân rã DWT tối đa hợp lệ cho ảnh và wavelet đã cho."""
    _require_pywt()
    return pywt.dwtn_max_level(image.shape, wavelet)


# --------------------------------------------------------------------------- #
# Biến đổi Wavelet (DWT)
# --------------------------------------------------------------------------- #

def dwt2_image(
    image: np.ndarray, wavelet: str = "db4", mode: str = "symmetric"
) -> Tuple[np.ndarray, DetailTuple]:
    """
    Thực hiện DWT 2D một mức (level 1) trên ảnh.

    Trả về (LL, (LH, HL, HH)):
        - LL: ảnh xấp xỉ (approximation) — tương ứng cA của pywt.dwt2
        - LH: chi tiết ngang / horizontal edges — tương ứng cH
        - HL: chi tiết dọc / vertical edges     — tương ứng cV
        - HH: chi tiết chéo / diagonal edges    — tương ứng cD
    """
    _require_pywt()
    cA, (cH, cV, cD) = pywt.dwt2(image, wavelet=wavelet, mode=mode)
    return cA, (cH, cV, cD)


def wavedec2_image(
    image: np.ndarray,
    wavelet: str = "db4",
    level: int = 1,
    mode: str = "symmetric",
) -> WaveDecCoeffs:
    """
    Thực hiện DWT 2D nhiều mức (multi-level) trên ảnh.

        coeffs = pywt.wavedec2(image, wavelet='db4', level=1)

    coeffs có dạng:
        [cA_n, (cH_n, cV_n, cD_n), ..., (cH_1, cV_1, cD_1)]
    với n = level. cA_n (coeffs[0]) là ảnh xấp xỉ (LL) ở mức sâu nhất.
    coeffs[1] là chi tiết ở mức sâu nhất (thô nhất), coeffs[-1] là chi tiết
    ở mức 1 (mịn nhất, gần độ phân giải ảnh gốc nhất).
    """
    _require_pywt()
    return pywt.wavedec2(image, wavelet=wavelet, level=level, mode=mode)


def get_subbands(coeffs: WaveDecCoeffs, level: int = 1) -> Subbands:
    """
    Trích các thành phần LL, LH, HL, HH tại một mức (level) cụ thể từ kết
    quả của wavedec2_image.

    Quy ước đánh số: level=1 là mức mịn nhất (gần độ phân giải gốc nhất,
    tương ứng với lần DWT đầu tiên), level=n_levels là mức thô nhất
    (sâu nhất, tương ứng lần DWT cuối cùng).

    Lưu ý: LL (ảnh xấp xỉ) chỉ thật sự tồn tại ở mức sâu nhất
    (level == n_levels), vì pywt.wavedec2 tiếp tục phân rã LL của các
    mức trung gian thành mức sâu hơn chứ không giữ lại. Ở các mức khác,
    khóa "LL" trả về None.
    """
    n_levels = len(coeffs) - 1
    if not (1 <= level <= n_levels):
        raise ValueError(f"level phải nằm trong khoảng [1, {n_levels}], nhận {level}")

    idx = n_levels - level + 1  # coeffs[1] la muc tho nhat (level = n_levels)
    cH, cV, cD = coeffs[idx]

    subbands: Subbands = {"LH": cH, "HL": cV, "HH": cD}
    subbands["LL"] = coeffs[0] if level == n_levels else None
    return subbands


def reconstruct_image(
    coeffs: WaveDecCoeffs, wavelet: str = "db4", mode: str = "symmetric"
) -> np.ndarray:
    """Tái tạo lại ảnh từ hệ số wavelet (phép biến đổi nghịch đảo của wavedec2)."""
    _require_pywt()
    return pywt.waverec2(coeffs, wavelet=wavelet, mode=mode)


# --------------------------------------------------------------------------- #
# Tiện ích hiển thị / phân tích
# --------------------------------------------------------------------------- #

def normalize_for_display(band: np.ndarray) -> np.ndarray:
    """Chuẩn hóa một sub-band (có thể chứa giá trị âm) về [0, 255] (uint8) để hiển thị."""
    band = np.asarray(band, dtype=np.float64)
    b_min, b_max = band.min(), band.max()
    if b_max - b_min < 1e-12:
        return np.zeros_like(band, dtype=np.uint8)
    normed = (band - b_min) / (b_max - b_min)
    return (normed * 255).astype(np.uint8)


def energy(band: np.ndarray) -> float:
    """Năng lượng của một sub-band (tổng bình phương các hệ số)."""
    return float(np.sum(np.square(band, dtype=np.float64)))


def energy_compaction(coeffs: WaveDecCoeffs) -> float:
    """
    Tỉ lệ năng lượng tập trung ở thành phần xấp xỉ (LL) so với tổng năng
    lượng toàn bộ hệ số wavelet — dùng để so sánh hiệu quả nén giữa các
    loại wavelet trong experiments/compare_wavelets.py.
    """
    ll_energy = energy(coeffs[0])
    total_energy = ll_energy
    for detail in coeffs[1:]:
        for band in detail:
            total_energy += energy(band)
    if total_energy < 1e-12:
        return 0.0
    return ll_energy / total_energy


# --------------------------------------------------------------------------- #
# So sánh ảnh bằng hệ số wavelet
# --------------------------------------------------------------------------- #

def _flatten_features(coeffs: WaveDecCoeffs) -> np.ndarray:
    """Ghép toàn bộ hệ số wavelet (mọi mức) thành một vector đặc trưng 1 chiều."""
    parts = [np.ravel(coeffs[0])]
    for detail in coeffs[1:]:
        for band in detail:
            parts.append(np.ravel(band))
    return np.concatenate(parts)


def wavelet_similarity(
    image_a: np.ndarray,
    image_b: np.ndarray,
    wavelet: str = "db4",
    level: int = 1,
    mode: str = "symmetric",
    use_only_ll: bool = False,
) -> float:
    """
    Tính độ tương đồng cosine giữa hai ảnh dựa trên hệ số wavelet.

    - use_only_ll=True: chỉ so sánh thành phần xấp xỉ (LL) — nhanh và bền
      với nhiễu, phù hợp so sánh bố cục / nội dung tổng thể.
    - use_only_ll=False (mặc định): so sánh toàn bộ hệ số (LL + LH + HL + HH
      ở mọi mức) — nhạy hơn với chi tiết / kết cấu.

    Trả về giá trị trong [-1, 1]; càng gần 1 thì hai ảnh càng giống nhau.
    Yêu cầu image_a và image_b có cùng kích thước.
    """
    if image_a.shape != image_b.shape:
        raise ValueError("Hai ảnh phải có cùng kích thước để so sánh hệ số wavelet.")

    coeffs_a = wavedec2_image(image_a, wavelet=wavelet, level=level, mode=mode)
    coeffs_b = wavedec2_image(image_b, wavelet=wavelet, level=level, mode=mode)

    if use_only_ll:
        vec_a = np.ravel(coeffs_a[0]).astype(np.float64)
        vec_b = np.ravel(coeffs_b[0]).astype(np.float64)
    else:
        vec_a = _flatten_features(coeffs_a).astype(np.float64)
        vec_b = _flatten_features(coeffs_b).astype(np.float64)

    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)
    if norm_a < 1e-12 or norm_b < 1e-12:
        return 0.0
    return float(np.dot(vec_a, vec_b) / (norm_a * norm_b))


if __name__ == "__main__":  # pragma: no cover
    # Demo nhanh khi chạy trực tiếp file này: python -m src.wavelet.wavelet_transform
    _require_pywt()
    rng = np.random.default_rng(0)
    demo_image = rng.random((256, 256))

    coeffs = wavedec2_image(demo_image, wavelet="db4", level=1)
    bands = get_subbands(coeffs, level=1)
    print("Kich thuoc anh goc:", demo_image.shape)
    for name in ("LL", "LH", "HL", "HH"):
        band = bands[name]
        print(f"  {name}: shape={band.shape}")

    reconstructed = reconstruct_image(coeffs, wavelet="db4")
    mse = np.mean((demo_image - reconstructed[: demo_image.shape[0], : demo_image.shape[1]]) ** 2)
    print("MSE sau khi tai tao lai anh:", mse)

    sim = wavelet_similarity(demo_image, demo_image, wavelet="db4")
    print("Do tuong dong voi chinh no (phai = 1.0):", sim)
