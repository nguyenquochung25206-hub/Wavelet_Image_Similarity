
import sys
from pathlib import Path

import cv2
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.preprocessing.image_preprocessor import (  # noqa: E402
    load_image,
    resize_image,
    to_grayscale,
    normalize_image,
    preprocess_image,
    save_preprocessed,)

@pytest.fixture
def sample_image_path(tmp_path) -> Path:
    """Tạo một ảnh màu ngẫu nhiên nhỏ để test, không phụ thuộc dataset thật."""
    rng = np.random.default_rng(seed=42)
    image = rng.integers(0, 255, size=(120, 180, 3), dtype=np.uint8)
    path = tmp_path / "sample.png"
    cv2.imwrite(str(path), image)
    return path


@pytest.fixture
def sample_image_array() -> np.ndarray:
    rng = np.random.default_rng(seed=7)
    return rng.integers(0, 255, size=(100, 100, 3), dtype=np.uint8)


class TestLoadImage:
    def test_load_valid_image_returns_array(self, sample_image_path):
        image = load_image(sample_image_path)
        assert isinstance(image, np.ndarray)
        assert image.ndim == 3  # ảnh màu BGR

    def test_load_missing_file_raises(self, tmp_path):
        missing_path = tmp_path / "khong_ton_tai.jpg"
        with pytest.raises(FileNotFoundError):
            load_image(missing_path)

    def test_load_invalid_format_raises(self, tmp_path):
        bad_file = tmp_path / "not_an_image.jpg"
        bad_file.write_text("day khong phai la anh")
        with pytest.raises(ValueError):
            load_image(bad_file)


class TestResizeImage:
    def test_resize_changes_dimensions(self, sample_image_array):
        resized = resize_image(sample_image_array, size=(64, 32))
        assert resized.shape[1] == 64  # width
        assert resized.shape[0] == 32  # height

    def test_resize_default_size(self, sample_image_array):
        resized = resize_image(sample_image_array)
        assert resized.shape[:2] == (256, 256)

    def test_resize_empty_image_raises(self):
        empty = np.array([])
        with pytest.raises(ValueError):
            resize_image(empty)


class TestToGrayscale:
    def test_color_image_converted_to_2d(self, sample_image_array):
        gray = to_grayscale(sample_image_array)
        assert gray.ndim == 2
        assert gray.shape == sample_image_array.shape[:2]

    def test_already_grayscale_unchanged(self):
        gray_input = np.zeros((50, 50), dtype=np.uint8)
        result = to_grayscale(gray_input)
        assert result.ndim == 2
        np.testing.assert_array_equal(result, gray_input)


class TestNormalizeImage:
    def test_values_in_zero_one_range(self, sample_image_array):
        gray = to_grayscale(sample_image_array)
        normalized = normalize_image(gray)
        assert normalized.dtype == np.float32
        assert normalized.min() >= 0.0
        assert normalized.max() <= 1.0

    def test_max_pixel_maps_close_to_one(self):
        image = np.full((10, 10), 255, dtype=np.uint8)
        normalized = normalize_image(image)
        assert np.allclose(normalized, 1.0)

    def test_min_pixel_maps_to_zero(self):
        image = np.zeros((10, 10), dtype=np.uint8)
        normalized = normalize_image(image)
        assert np.allclose(normalized, 0.0)


class TestPreprocessPipeline:
    def test_full_pipeline_output_shape_and_range(self, sample_image_path):
        result = preprocess_image(sample_image_path, size=(256, 256))
        assert result.shape == (256, 256)
        assert result.dtype == np.float32
        assert result.min() >= 0.0
        assert result.max() <= 1.0

    def test_pipeline_with_custom_size(self, sample_image_path):
        result = preprocess_image(sample_image_path, size=(128, 64))
        assert result.shape == (64, 128)  # (height, width)

    def test_pipeline_missing_file_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            preprocess_image(tmp_path / "khong_co.jpg")


class TestSavePreprocessed:
    def test_save_creates_readable_file(self, sample_image_path, tmp_path):
        processed = preprocess_image(sample_image_path)
        output_path = tmp_path / "output" / "result.png"
        save_preprocessed(processed, output_path)

        assert output_path.exists()
        # File lưu ra phải đọc lại được bằng OpenCV.
        reloaded = cv2.imread(str(output_path))
        assert reloaded is not None
