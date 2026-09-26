"""
Unit tests for Wavelet Hash.

Module under test:
    src/wavelet/wavelet_hash.py

Run:
    pytest tests/test_wavelet_hash.py -v
"""

import numpy as np
import pytest

from src.wavelet.wavelet_hash import wavelet_hash


def make_gradient_image(size=(64, 64)):
    """Create a deterministic grayscale gradient image."""
    height, width = size

    row = np.linspace(
        0,
        255,
        width,
        dtype=np.float32
    )

    return np.tile(row, (height, 1))


def make_checkerboard(size=(64, 64), block_size=8):
    """Create a deterministic checkerboard image."""
    height, width = size

    y, x = np.indices((height, width))

    board = (
        (x // block_size + y // block_size) % 2
    ) * 255

    return board.astype(np.float32)


def test_wavelet_hash_returns_string():
    """Wavelet Hash should return a string."""
    image = make_gradient_image()

    result = wavelet_hash(image)

    assert isinstance(result, str)


def test_wavelet_hash_default_length():
    """
    Default hash size is 8x8,
    therefore the hash should contain 64 bits.
    """
    image = make_gradient_image()

    result = wavelet_hash(image)

    assert len(result) == 64


def test_wavelet_hash_contains_only_binary_values():
    """Hash must contain only 0 and 1."""
    image = make_gradient_image()

    result = wavelet_hash(image)

    assert set(result).issubset({"0", "1"})


def test_wavelet_hash_is_deterministic():
    """
    The same image should always produce
    the same Wavelet Hash.
    """
    image = make_gradient_image()

    hash_1 = wavelet_hash(image)
    hash_2 = wavelet_hash(image.copy())

    assert hash_1 == hash_2


def test_wavelet_hash_supports_custom_hash_size():
    """Test a custom 4x4 hash."""
    image = make_gradient_image()

    result = wavelet_hash(
        image,
        hash_size=(4, 4)
    )

    assert len(result) == 16
    assert set(result).issubset({"0", "1"})


def test_wavelet_hash_supports_wavelet_parameter():
    """Test a valid wavelet parameter."""
    image = make_gradient_image()

    result = wavelet_hash(
        image,
        wavelet="haar"
    )

    assert len(result) == 64
    assert set(result).issubset({"0", "1"})


def test_different_images_can_produce_different_hashes():
    """
    Different image structures should be able
    to produce different hashes.
    """
    gradient = make_gradient_image()
    checkerboard = make_checkerboard()

    gradient_hash = wavelet_hash(gradient)
    checkerboard_hash = wavelet_hash(checkerboard)

    assert gradient_hash != checkerboard_hash


def test_small_image_is_processed():
    """Test Wavelet Hash with a smaller image."""
    image = make_gradient_image(
        size=(16, 16)
    )

    result = wavelet_hash(image)

    assert len(result) == 64
    assert set(result).issubset({"0", "1"})


@pytest.mark.parametrize(
    "invalid_hash_size",
    [
        (0, 8),
        (8, 0),
        (4,),
        (4, 4, 4),
    ],
)
def test_invalid_hash_size_is_rejected(
    invalid_hash_size
):
    """Invalid hash sizes should raise an exception."""
    image = make_gradient_image()

    with pytest.raises(
        (ValueError, TypeError, IndexError)
    ):
        wavelet_hash(
            image,
            hash_size=invalid_hash_size
        )


def test_invalid_wavelet_is_rejected():
    """An invalid wavelet name should raise an exception."""
    image = make_gradient_image()

    with pytest.raises(
        (ValueError, KeyError, TypeError)
    ):
        wavelet_hash(
            image,
            wavelet="not_a_real_wavelet"
        )


def test_hash_is_binary_for_constant_image():
    """
    A constant image is still a valid input.

    The exact bit pattern depends on the implementation,
    but the result must have the requested length
    and contain only binary values.
    """
    image = np.full(
        (64, 64),
        128,
        dtype=np.float32
    )

    result = wavelet_hash(image)

    assert len(result) == 64
    assert set(result).issubset({"0", "1"})