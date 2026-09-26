"""
Integration tests for the Wavelet Image Similarity pipeline.

Pipeline:

    Image
      ↓
    Preprocessing
      ↓
    Wavelet Transform
      ↓
    Wavelet Hash
      ↓
    Hamming Distance
      ↓
    Similarity
"""

from pathlib import Path

import cv2
import numpy as np
import pytest


# ---------------------------------------------------------------------------
# Project paths
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_ROOT / "data" / "input"

SIMILAR_DIR = DATA_DIR / "similar"
DISSIMILAR_DIR = DATA_DIR / "dissimilar"


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def get_image_pair(pair_dir: Path):
    """
    Return image_01.jpg and image_02.jpg.
    """

    image_01 = pair_dir / "image_01.jpg"
    image_02 = pair_dir / "image_02.jpg"

    return image_01, image_02


def load_image(path: Path):
    """
    Load image using the project's preprocessing loader.

    This avoids cv2.imread() Unicode path problems on Windows.
    """

    from src.preprocessing.image_preprocessor import (
        load_image as project_load_image
    )

    return project_load_image(path)


# ---------------------------------------------------------------------------
# Dataset existence
# ---------------------------------------------------------------------------

def test_similar_dataset_exists():
    """Check that Similar dataset exists."""

    assert SIMILAR_DIR.exists(), (
        f"Similar dataset does not exist: {SIMILAR_DIR}"
    )


def test_dissimilar_dataset_exists():
    """Check that Dissimilar dataset exists."""

    assert DISSIMILAR_DIR.exists(), (
        f"Dissimilar dataset does not exist: {DISSIMILAR_DIR}"
    )


# ---------------------------------------------------------------------------
# Dataset pair loading
# ---------------------------------------------------------------------------

def test_similar_pair_can_be_loaded():
    """Check that a Similar image pair can be loaded."""

    pair_dir = SIMILAR_DIR / "pair_01"

    image_01_path, image_02_path = get_image_pair(
        pair_dir
    )

    image_01 = load_image(
        image_01_path
    )

    image_02 = load_image(
        image_02_path
    )

    assert image_01.size > 0
    assert image_02.size > 0


def test_dissimilar_pair_can_be_loaded():
    """Check that a Dissimilar image pair can be loaded."""

    pair_dir = DISSIMILAR_DIR / "pair_01"

    image_01_path, image_02_path = get_image_pair(
        pair_dir
    )

    image_01 = load_image(
        image_01_path
    )

    image_02 = load_image(
        image_02_path
    )

    assert image_01.size > 0
    assert image_02.size > 0


# ---------------------------------------------------------------------------
# Preprocessing integration
# ---------------------------------------------------------------------------

def test_preprocessing_output():
    """
    Check complete preprocessing pipeline.
    """

    from src.preprocessing.image_preprocessor import (
        preprocess_image
    )

    image_path = (
        SIMILAR_DIR
        / "pair_01"
        / "image_01.jpg"
    )

    result = preprocess_image(
        image_path,
        size=(256, 256)
    )

    assert result is not None
    assert isinstance(result, np.ndarray)

    assert result.size > 0

    # Must be grayscale.
    assert result.ndim == 2

    # Must be float32.
    assert result.dtype == np.float32

    # Must be normalized.
    assert result.min() >= 0.0
    assert result.max() <= 1.0

    # Expected size.
    assert result.shape == (256, 256)


# ---------------------------------------------------------------------------
# Complete Wavelet pipeline
# ---------------------------------------------------------------------------

def _run_pipeline(image_path: Path):
    """
    Run the actual project pipeline using function-based APIs.
    """

    from src.preprocessing.image_preprocessor import (
        preprocess_image
    )

    from src.wavelet.wavelet_transform import (
        dwt2_image
    )

    from src.wavelet.wavelet_hash import (
        wavelet_hash
    )

    from src.similarity.hamming_distance import (
        HammingDistance
    )

    # ---------------------------------------------------------------
    # Step 1: Preprocessing
    # ---------------------------------------------------------------

    processed = preprocess_image(
        image_path,
        size=(256, 256)
    )

    assert processed is not None
    assert processed.ndim == 2

    # ---------------------------------------------------------------
    # Step 2: Wavelet Transform
    # ---------------------------------------------------------------

    ll, details = dwt2_image(
        processed,
        wavelet="haar"
    )

    assert ll is not None
    assert isinstance(ll, np.ndarray)

    assert len(details) == 3

    # ---------------------------------------------------------------
    # Step 3: Wavelet Hash
    #
    # The hash function accepts an image.
    # Use the LL approximation generated by DWT.
    # ---------------------------------------------------------------

    hash_value = wavelet_hash(
        processed,
        wavelet="haar",
        hash_size=(8, 8)
    )

    assert hash_value is not None
    assert isinstance(hash_value, str)

    assert len(hash_value) == 64

    assert set(hash_value).issubset(
        {"0", "1"}
    )

    return hash_value


def test_wavelet_pipeline_single_pair():
    """
    Test complete processing flow for one Similar pair.
    """

    image_01_path = (
        SIMILAR_DIR
        / "pair_01"
        / "image_01.jpg"
    )

    image_02_path = (
        SIMILAR_DIR
        / "pair_01"
        / "image_02.jpg"
    )

    hash_01 = _run_pipeline(
        image_01_path
    )

    hash_02 = _run_pipeline(
        image_02_path
    )

    # ---------------------------------------------------------------
    # Step 4: Hamming Distance
    # ---------------------------------------------------------------

    from src.similarity.hamming_distance import (
        HammingDistance
    )

    hamming = HammingDistance()

    distance = hamming.calculate(
        hash_01,
        hash_02
    )

    assert distance is not None
    assert isinstance(
        distance,
        int
    )

    assert distance >= 0
    assert distance <= 64


# ---------------------------------------------------------------------------
# Deterministic pipeline
# ---------------------------------------------------------------------------

def test_pipeline_is_deterministic():
    """
    Processing the same image twice must produce the same hash.
    """

    image_path = (
        SIMILAR_DIR
        / "pair_01"
        / "image_01.jpg"
    )

    hash_01 = _run_pipeline(
        image_path
    )

    hash_02 = _run_pipeline(
        image_path
    )

    assert hash_01 == hash_02


# ---------------------------------------------------------------------------
# Dataset pair structure
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "dataset_dir",
    [
        SIMILAR_DIR,
        DISSIMILAR_DIR,
    ],
)
def test_dataset_pairs_have_two_images(
    dataset_dir
):
    """
    Check that every dataset pair contains two images.
    """

    assert dataset_dir.exists(), (
        f"Dataset directory does not exist: {dataset_dir}"
    )

    pair_dirs = sorted(
        path
        for path in dataset_dir.iterdir()
        if path.is_dir()
    )

    assert pair_dirs, (
        f"No pair directories found in {dataset_dir}"
    )

    for pair_dir in pair_dirs:

        image_01, image_02 = get_image_pair(
            pair_dir
        )

        assert image_01.exists(), (
            f"Missing image_01.jpg in {pair_dir}"
        )

        assert image_02.exists(), (
            f"Missing image_02.jpg in {pair_dir}"
        )


# ---------------------------------------------------------------------------
# Dataset image readability
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "dataset_dir",
    [
        SIMILAR_DIR,
        DISSIMILAR_DIR,
    ],
)
def test_all_dataset_images_are_readable(
    dataset_dir
):
    """
    Check that all dataset images can be opened.
    """

    assert dataset_dir.exists(), (
        f"Dataset directory does not exist: {dataset_dir}"
    )

    pair_dirs = sorted(
        path
        for path in dataset_dir.iterdir()
        if path.is_dir()
    )

    assert pair_dirs, (
        f"No pair directories found in {dataset_dir}"
    )

    for pair_dir in pair_dirs:

        image_01_path, image_02_path = (
            get_image_pair(pair_dir)
        )

        image_01 = load_image(
            image_01_path
        )

        image_02 = load_image(
            image_02_path
        )

        assert image_01.ndim in (2, 3)
        assert image_02.ndim in (2, 3)

        assert image_01.size > 0
        assert image_02.size > 0