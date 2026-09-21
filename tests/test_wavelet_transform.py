"""
test_wavelet_transform.py — TV2

Bộ test cho module src/wavelet/wavelet_transform.py:
    - DWT hoạt động đúng (kích thước sub-band hợp lý).
    - Tái tạo (reconstruction) lại được ảnh gần như nguyên vẹn.
    - Các hệ số (coefficients) hợp lệ (không NaN/Inf, đúng kiểu dữ liệu).
    - Chạy được với nhiều loại Wavelet: Haar, db2, db4, db8, sym2, sym4, coif1.

Chạy test:
    pytest tests/test_wavelet_transform.py -v

Nếu chưa cài PyWavelets, các test liên quan sẽ tự động bị skip
(pytest.importorskip) thay vì báo lỗi.
"""

from __future__ import annotations

import os
import sys

import numpy as np
import pytest

# Cho phép chạy test trực tiếp mà không cần cài đặt package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

pywt = pytest.importorskip("pywt", reason="Cần cài PyWavelets: pip install PyWavelets")

from src.wavelet.wavelet_transform import (  # noqa: E402
    SUPPORTED_WAVELETS,
    dwt2_image,
    energy,
    energy_compaction,
    get_subbands,
    max_dwt_level,
    normalize_for_display,
    reconstruct_image,
    wavedec2_image,
    wavelet_similarity,
)


@pytest.fixture
def sample_image() -> np.ndarray:
    """Ảnh 64x64 có cấu trúc (không phải nhiễu thuần) để DWT có ý nghĩa kiểm thử."""
    x = np.linspace(0, 4 * np.pi, 64)
    y = np.linspace(0, 4 * np.pi, 64)
    xx, yy = np.meshgrid(x, y)
    base = (np.sin(xx) + np.cos(yy)) / 2 + 0.5
    rng = np.random.default_rng(42)
    noise = rng.normal(0, 0.01, size=base.shape)
    return np.clip(base + noise, 0.0, 1.0)


# --------------------------------------------------------------------------- #
# 1) DWT hoạt động đúng
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("wavelet", SUPPORTED_WAVELETS)
def test_dwt2_subband_shapes_are_consistent(sample_image, wavelet):
    LL, (LH, HL, HH) = dwt2_image(sample_image, wavelet=wavelet)
    shapes = {LL.shape, LH.shape, HL.shape, HH.shape}
    assert len(shapes) == 1, "LL, LH, HL, HH phải có cùng kích thước"

    h, w = LL.shape
    # Với ảnh 64x64, sub-band phải xấp xỉ bằng một nửa mỗi chiều
    assert 30 <= h <= 40
    assert 30 <= w <= 40


@pytest.mark.parametrize("wavelet", SUPPORTED_WAVELETS)
def test_dwt2_coefficients_are_finite(sample_image, wavelet):
    LL, (LH, HL, HH) = dwt2_image(sample_image, wavelet=wavelet)
    for band in (LL, LH, HL, HH):
        assert np.all(np.isfinite(band)), f"Hệ số không hợp lệ (NaN/Inf) với wavelet={wavelet}"


def test_multi_level_decomposition_structure(sample_image):
    max_level = max_dwt_level(sample_image, wavelet="db4")
    assert max_level >= 2, "Ảnh mẫu 64x64 phải cho phép phân rã ít nhất 2 mức với db4"

    coeffs = wavedec2_image(sample_image, wavelet="db4", level=2)
    # coeffs = [cA2, (cH2,cV2,cD2), (cH1,cV1,cD1)] -> 3 phần tử cho level=2
    assert len(coeffs) == 3
    assert isinstance(coeffs[0], np.ndarray)
    for detail in coeffs[1:]:
        assert len(detail) == 3


# --------------------------------------------------------------------------- #
# 2) Tái tạo ảnh (reconstruction)
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("wavelet", SUPPORTED_WAVELETS)
def test_reconstruction_close_to_original(sample_image, wavelet):
    coeffs = wavedec2_image(sample_image, wavelet=wavelet, level=1)
    reconstructed = reconstruct_image(coeffs, wavelet=wavelet)
    reconstructed = reconstructed[: sample_image.shape[0], : sample_image.shape[1]]

    mse = np.mean((sample_image - reconstructed) ** 2)
    assert mse < 1e-6, f"MSE tái tạo quá lớn với wavelet={wavelet}: {mse}"


def test_reconstruction_multi_level(sample_image):
    coeffs = wavedec2_image(sample_image, wavelet="db2", level=3)
    reconstructed = reconstruct_image(coeffs, wavelet="db2")
    reconstructed = reconstructed[: sample_image.shape[0], : sample_image.shape[1]]

    mse = np.mean((sample_image - reconstructed) ** 2)
    assert mse < 1e-6


# --------------------------------------------------------------------------- #
# 3) Kiểm tra các coefficients / sub-band LL, LH, HL, HH
# --------------------------------------------------------------------------- #

def test_get_subbands_finest_level_has_no_ll(sample_image):
    coeffs = wavedec2_image(sample_image, wavelet="db4", level=2)
    finest = get_subbands(coeffs, level=1)

    assert finest["LL"] is None
    assert set(finest.keys()) == {"LL", "LH", "HL", "HH"}
    assert finest["LH"] is not None
    assert finest["HL"] is not None
    assert finest["HH"] is not None


def test_get_subbands_coarsest_level_has_ll(sample_image):
    coeffs = wavedec2_image(sample_image, wavelet="db4", level=2)
    coarsest = get_subbands(coeffs, level=2)

    assert coarsest["LL"] is not None
    assert coarsest["LL"].shape == coeffs[0].shape
    np.testing.assert_array_equal(coarsest["LL"], coeffs[0])


def test_get_subbands_single_level_matches_dwt2(sample_image):
    coeffs = wavedec2_image(sample_image, wavelet="db4", level=1)
    bands = get_subbands(coeffs, level=1)

    LL, (LH, HL, HH) = dwt2_image(sample_image, wavelet="db4")
    np.testing.assert_array_almost_equal(bands["LL"], LL)
    np.testing.assert_array_almost_equal(bands["LH"], LH)
    np.testing.assert_array_almost_equal(bands["HL"], HL)
    np.testing.assert_array_almost_equal(bands["HH"], HH)


def test_get_subbands_invalid_level_raises(sample_image):
    coeffs = wavedec2_image(sample_image, wavelet="db4", level=1)
    with pytest.raises(ValueError):
        get_subbands(coeffs, level=0)
    with pytest.raises(ValueError):
        get_subbands(coeffs, level=5)


def test_energy_compaction_between_zero_and_one(sample_image):
    coeffs = wavedec2_image(sample_image, wavelet="db4", level=2)
    ratio = energy_compaction(coeffs)
    assert 0.0 <= ratio <= 1.0
    # Với ảnh có cấu trúc mượt (sin/cos), phần lớn năng lượng nên tập trung ở LL
    assert ratio > 0.8


def test_normalize_for_display_range(sample_image):
    _, (_, _, HH) = dwt2_image(sample_image, wavelet="db4")
    normed = normalize_for_display(HH)
    assert normed.dtype == np.uint8
    assert normed.min() >= 0
    assert normed.max() <= 255


def test_energy_is_non_negative(sample_image):
    LL, (LH, HL, HH) = dwt2_image(sample_image, wavelet="haar")
    for band in (LL, LH, HL, HH):
        assert energy(band) >= 0.0


# --------------------------------------------------------------------------- #
# 4) Chạy được với nhiều loại Wavelet
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("wavelet", SUPPORTED_WAVELETS)
def test_all_target_wavelets_are_valid_pywt_names(wavelet):
    assert wavelet in pywt.wavelist(kind="discrete")


@pytest.mark.parametrize("wavelet", SUPPORTED_WAVELETS)
def test_pipeline_runs_end_to_end_for_every_wavelet(sample_image, wavelet):
    coeffs = wavedec2_image(sample_image, wavelet=wavelet, level=1)
    bands = get_subbands(coeffs, level=1)
    assert bands["LL"] is not None

    reconstructed = reconstruct_image(coeffs, wavelet=wavelet)
    reconstructed = reconstructed[: sample_image.shape[0], : sample_image.shape[1]]
    assert reconstructed.shape == sample_image.shape


# --------------------------------------------------------------------------- #
# 5) Độ tương đồng ảnh (wavelet_similarity)
# --------------------------------------------------------------------------- #

def test_wavelet_similarity_identical_image_is_one(sample_image):
    sim = wavelet_similarity(sample_image, sample_image, wavelet="db4", level=1)
    assert sim == pytest.approx(1.0, abs=1e-9)


def test_wavelet_similarity_different_images_is_lower(sample_image):
    rng = np.random.default_rng(7)
    other = rng.random(sample_image.shape)

    sim_same = wavelet_similarity(sample_image, sample_image, wavelet="db4")
    sim_diff = wavelet_similarity(sample_image, other, wavelet="db4")
    assert sim_diff < sim_same


def test_wavelet_similarity_use_only_ll_option(sample_image):
    rng = np.random.default_rng(7)
    other = rng.random(sample_image.shape)

    sim_full = wavelet_similarity(sample_image, other, wavelet="db4", use_only_ll=False)
    sim_ll_only = wavelet_similarity(sample_image, other, wavelet="db4", use_only_ll=True)
    # Hai cách tính có thể khác nhau về giá trị, nhưng đều phải hợp lệ trong [-1, 1]
    for sim in (sim_full, sim_ll_only):
        assert -1.0 <= sim <= 1.0


def test_wavelet_similarity_shape_mismatch_raises(sample_image):
    other = sample_image[:32, :32]
    with pytest.raises(ValueError):
        wavelet_similarity(sample_image, other, wavelet="db4")
