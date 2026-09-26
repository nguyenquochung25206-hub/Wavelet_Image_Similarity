<<<<<<< HEAD

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

These tests focus on the integration between modules rather than testing
every internal implementation detail of each module.
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
    Return image_01.jpg and image_02.jpg from a pair directory.

    Parameters
    ----------
    pair_dir : Path
        Directory containing image_01.jpg and image_02.jpg.

    Returns
    -------
    tuple[Path, Path]
        Paths to the two images.
    """

    image_01 = pair_dir / "image_01.jpg"
    image_02 = pair_dir / "image_02.jpg"

    return image_01, image_02


def load_image(path: Path):
    """
    Load an image using OpenCV.

    Raises
    ------
    AssertionError
        If the image cannot be loaded.
    """

    assert path.exists(), f"Image does not exist: {path}"

    image = cv2.imread(str(path))

    assert image is not None, f"Could not load image: {path}"

    return image


# ---------------------------------------------------------------------------
# Dataset tests
# ---------------------------------------------------------------------------

def test_similar_dataset_exists():
    """Check that the Similar dataset exists."""

    assert SIMILAR_DIR.exists(), (
        f"Similar dataset does not exist: {SIMILAR_DIR}"
    )


def test_dissimilar_dataset_exists():
    """Check that the Dissimilar dataset exists."""

    assert DISSIMILAR_DIR.exists(), (
        f"Dissimilar dataset does not exist: {DISSIMILAR_DIR}"
    )


def test_similar_pair_can_be_loaded():
    """
    Check that a Similar image pair can be loaded successfully.
    """

    pair_dir = SIMILAR_DIR / "pair_01"

    image_01_path, image_02_path = get_image_pair(pair_dir)

    image_01 = load_image(image_01_path)
    image_02 = load_image(image_02_path)

    assert image_01.size > 0
    assert image_02.size > 0


def test_dissimilar_pair_can_be_loaded():
    """
    Check that a Dissimilar image pair can be loaded successfully.
    """

    pair_dir = DISSIMILAR_DIR / "pair_01"

    image_01_path, image_02_path = get_image_pair(pair_dir)

    image_01 = load_image(image_01_path)
    image_02 = load_image(image_02_path)

    assert image_01.size > 0
    assert image_02.size > 0


# ---------------------------------------------------------------------------
# Preprocessing integration
# ---------------------------------------------------------------------------

def test_preprocessing_output():
    """
    Check that preprocessing can process a real dataset image.
    """

    from src.preprocessing.image_preprocessor import ImagePreprocessor

    image_path = SIMILAR_DIR / "pair_01" / "image_01.jpg"

    image = load_image(image_path)

    preprocessor = ImagePreprocessor()

    result = preprocessor.preprocess(image)

    assert result is not None
    assert isinstance(result, np.ndarray)
    assert result.size > 0


# ---------------------------------------------------------------------------
# Wavelet pipeline integration
# ---------------------------------------------------------------------------

def _import_wavelet_modules():
    """
    Import Wavelet modules.

    The project currently contains placeholder files for some Wavelet
    modules. If the required implementation is not available, the
    integration test is skipped instead of failing because of an
    unfinished module.
    """

    try:
        from src.wavelet.wavelet_transform import WaveletTransform
        from src.wavelet.wavelet_hash import WaveletHash
        from src.similarity.hamming_distance import HammingDistance

        return WaveletTransform, WaveletHash, HammingDistance

    except (ImportError, AttributeError):
        pytest.skip(
            "Wavelet Transform / Wavelet Hash / Hamming Distance "
            "implementation is not available yet."
        )


def test_wavelet_pipeline_single_pair():
    """
    Test the complete processing flow for one Similar image pair.

    This test verifies that:

        image
          ↓
        preprocessing
          ↓
        wavelet transform
          ↓
        wavelet hash
          ↓
        hamming distance

    can be connected successfully.
    """

    WaveletTransform, WaveletHash, HammingDistance = _import_wavelet_modules()

    image_01_path = SIMILAR_DIR / "pair_01" / "image_01.jpg"
    image_02_path = SIMILAR_DIR / "pair_01" / "image_02.jpg"

    image_01 = load_image(image_01_path)
    image_02 = load_image(image_02_path)

    # ---------------------------------------------------------------
    # Step 1: Preprocessing
    # ---------------------------------------------------------------

    from src.preprocessing.image_preprocessor import ImagePreprocessor

    preprocessor = ImagePreprocessor()

    processed_01 = preprocessor.preprocess(image_01)
    processed_02 = preprocessor.preprocess(image_02)

    assert processed_01 is not None
    assert processed_02 is not None

    # ---------------------------------------------------------------
    # Step 2: Wavelet Transform
    # ---------------------------------------------------------------

    wavelet_transform = WaveletTransform()

    transformed_01 = wavelet_transform.transform(processed_01)
    transformed_02 = wavelet_transform.transform(processed_02)

    assert transformed_01 is not None
    assert transformed_02 is not None

    # ---------------------------------------------------------------
    # Step 3: Wavelet Hash
    # ---------------------------------------------------------------

    wavelet_hash = WaveletHash()

    hash_01 = wavelet_hash.generate(transformed_01)
    hash_02 = wavelet_hash.generate(transformed_02)

    assert hash_01 is not None
    assert hash_02 is not None

    assert len(hash_01) == len(hash_02)

    # ---------------------------------------------------------------
    # Step 4: Hamming Distance
    # ---------------------------------------------------------------

    hamming = HammingDistance()

    distance = hamming.calculate(hash_01, hash_02)

    assert distance is not None
    assert isinstance(distance, (int, float))
    assert distance >= 0


# ---------------------------------------------------------------------------
# Reproducibility test
# ---------------------------------------------------------------------------

def test_pipeline_is_deterministic():
    """
    Processing the same image twice should produce the same hash.

    This test is important because Wavelet Hash should be deterministic
    for the same input and the same configuration.
    """

    WaveletTransform, WaveletHash, _ = _import_wavelet_modules()

    image_path = SIMILAR_DIR / "pair_01" / "image_01.jpg"

    image = load_image(image_path)

    from src.preprocessing.image_preprocessor import ImagePreprocessor

    preprocessor = ImagePreprocessor()

    processed_01 = preprocessor.preprocess(image)
    processed_02 = preprocessor.preprocess(image.copy())

    wavelet_transform = WaveletTransform()

    transformed_01 = wavelet_transform.transform(processed_01)
    transformed_02 = wavelet_transform.transform(processed_02)

    wavelet_hash = WaveletHash()

    hash_01 = wavelet_hash.generate(transformed_01)
    hash_02 = wavelet_hash.generate(transformed_02)

    assert hash_01 == hash_02


# ---------------------------------------------------------------------------
# Similar and Dissimilar integration tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "dataset_dir",
    [
        SIMILAR_DIR,
        DISSIMILAR_DIR,
    ],
)
def test_dataset_pairs_have_two_images(dataset_dir):
    """
    Check that every dataset pair contains exactly the required two images.
    """

    pair_dirs = sorted(
        path for path in dataset_dir.iterdir()
        if path.is_dir()
    )

    assert pair_dirs, f"No pair directories found in {dataset_dir}"

    for pair_dir in pair_dirs:

        image_01, image_02 = get_image_pair(pair_dir)

        assert image_01.exists(), (
            f"Missing image_01.jpg in {pair_dir}"
        )

        assert image_02.exists(), (
            f"Missing image_02.jpg in {pair_dir}"
        )


@pytest.mark.parametrize(
    "dataset_dir",
    [
        SIMILAR_DIR,
        DISSIMILAR_DIR,
    ],
)
def test_all_dataset_images_are_readable(dataset_dir):
    """
    Check that all images in the dataset can be opened by OpenCV.
    """

    pair_dirs = sorted(
        path for path in dataset_dir.iterdir()
        if path.is_dir()
    )

    for pair_dir in pair_dirs:

        image_01_path, image_02_path = get_image_pair(pair_dir)

        image_01 = load_image(image_01_path)
        image_02 = load_image(image_02_path)

        assert image_01.ndim in (2, 3)
        assert image_02.ndim in (2, 3)

        assert image_01.size > 0
        assert image_02.size > 0

=======

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

These tests focus on the integration between modules rather than testing
every internal implementation detail of each module.
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
    Return image_01.jpg and image_02.jpg from a pair directory.

    Parameters
    ----------
    pair_dir : Path
        Directory containing image_01.jpg and image_02.jpg.

    Returns
    -------
    tuple[Path, Path]
        Paths to the two images.
    """

    image_01 = pair_dir / "image_01.jpg"
    image_02 = pair_dir / "image_02.jpg"

    return image_01, image_02


def load_image(path: Path):
    """
    Load an image using OpenCV.

    Raises
    ------
    AssertionError
        If the image cannot be loaded.
    """

    assert path.exists(), f"Image does not exist: {path}"

    image = cv2.imread(str(path))

    assert image is not None, f"Could not load image: {path}"

    return image


# ---------------------------------------------------------------------------
# Dataset tests
# ---------------------------------------------------------------------------

def test_similar_dataset_exists():
    """Check that the Similar dataset exists."""

    assert SIMILAR_DIR.exists(), (
        f"Similar dataset does not exist: {SIMILAR_DIR}"
    )


def test_dissimilar_dataset_exists():
    """Check that the Dissimilar dataset exists."""

    assert DISSIMILAR_DIR.exists(), (
        f"Dissimilar dataset does not exist: {DISSIMILAR_DIR}"
    )


def test_similar_pair_can_be_loaded():
    """
    Check that a Similar image pair can be loaded successfully.
    """

    pair_dir = SIMILAR_DIR / "pair_01"

    image_01_path, image_02_path = get_image_pair(pair_dir)

    image_01 = load_image(image_01_path)
    image_02 = load_image(image_02_path)

    assert image_01.size > 0
    assert image_02.size > 0


def test_dissimilar_pair_can_be_loaded():
    """
    Check that a Dissimilar image pair can be loaded successfully.
    """

    pair_dir = DISSIMILAR_DIR / "pair_01"

    image_01_path, image_02_path = get_image_pair(pair_dir)

    image_01 = load_image(image_01_path)
    image_02 = load_image(image_02_path)

    assert image_01.size > 0
    assert image_02.size > 0


# ---------------------------------------------------------------------------
# Preprocessing integration
# ---------------------------------------------------------------------------

def test_preprocessing_output():
    """
    Check that preprocessing can process a real dataset image.
    """

    from src.preprocessing.image_preprocessor import ImagePreprocessor

    image_path = SIMILAR_DIR / "pair_01" / "image_01.jpg"

    image = load_image(image_path)

    preprocessor = ImagePreprocessor()

    result = preprocessor.preprocess(image)

    assert result is not None
    assert isinstance(result, np.ndarray)
    assert result.size > 0


# ---------------------------------------------------------------------------
# Wavelet pipeline integration
# ---------------------------------------------------------------------------

def _import_wavelet_modules():
    """
    Import Wavelet modules.

    The project currently contains placeholder files for some Wavelet
    modules. If the required implementation is not available, the
    integration test is skipped instead of failing because of an
    unfinished module.
    """

    try:
        from src.wavelet.wavelet_transform import WaveletTransform
        from src.wavelet.wavelet_hash import WaveletHash
        from src.similarity.hamming_distance import HammingDistance

        return WaveletTransform, WaveletHash, HammingDistance

    except (ImportError, AttributeError):
        pytest.skip(
            "Wavelet Transform / Wavelet Hash / Hamming Distance "
            "implementation is not available yet."
        )


def test_wavelet_pipeline_single_pair():
    """
    Test the complete processing flow for one Similar image pair.

    This test verifies that:

        image
          ↓
        preprocessing
          ↓
        wavelet transform
          ↓
        wavelet hash
          ↓
        hamming distance

    can be connected successfully.
    """

    WaveletTransform, WaveletHash, HammingDistance = _import_wavelet_modules()

    image_01_path = SIMILAR_DIR / "pair_01" / "image_01.jpg"
    image_02_path = SIMILAR_DIR / "pair_01" / "image_02.jpg"

    image_01 = load_image(image_01_path)
    image_02 = load_image(image_02_path)

    # ---------------------------------------------------------------
    # Step 1: Preprocessing
    # ---------------------------------------------------------------

    from src.preprocessing.image_preprocessor import ImagePreprocessor

    preprocessor = ImagePreprocessor()

    processed_01 = preprocessor.preprocess(image_01)
    processed_02 = preprocessor.preprocess(image_02)

    assert processed_01 is not None
    assert processed_02 is not None

    # ---------------------------------------------------------------
    # Step 2: Wavelet Transform
    # ---------------------------------------------------------------

    wavelet_transform = WaveletTransform()

    transformed_01 = wavelet_transform.transform(processed_01)
    transformed_02 = wavelet_transform.transform(processed_02)

    assert transformed_01 is not None
    assert transformed_02 is not None

    # ---------------------------------------------------------------
    # Step 3: Wavelet Hash
    # ---------------------------------------------------------------

    wavelet_hash = WaveletHash()

    hash_01 = wavelet_hash.generate(transformed_01)
    hash_02 = wavelet_hash.generate(transformed_02)

    assert hash_01 is not None
    assert hash_02 is not None

    assert len(hash_01) == len(hash_02)

    # ---------------------------------------------------------------
    # Step 4: Hamming Distance
    # ---------------------------------------------------------------

    hamming = HammingDistance()

    distance = hamming.calculate(hash_01, hash_02)

    assert distance is not None
    assert isinstance(distance, (int, float))
    assert distance >= 0


# ---------------------------------------------------------------------------
# Reproducibility test
# ---------------------------------------------------------------------------

def test_pipeline_is_deterministic():
    """
    Processing the same image twice should produce the same hash.

    This test is important because Wavelet Hash should be deterministic
    for the same input and the same configuration.
    """

    WaveletTransform, WaveletHash, _ = _import_wavelet_modules()

    image_path = SIMILAR_DIR / "pair_01" / "image_01.jpg"

    image = load_image(image_path)

    from src.preprocessing.image_preprocessor import ImagePreprocessor

    preprocessor = ImagePreprocessor()

    processed_01 = preprocessor.preprocess(image)
    processed_02 = preprocessor.preprocess(image.copy())

    wavelet_transform = WaveletTransform()

    transformed_01 = wavelet_transform.transform(processed_01)
    transformed_02 = wavelet_transform.transform(processed_02)

    wavelet_hash = WaveletHash()

    hash_01 = wavelet_hash.generate(transformed_01)
    hash_02 = wavelet_hash.generate(transformed_02)

    assert hash_01 == hash_02


# ---------------------------------------------------------------------------
# Similar and Dissimilar integration tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "dataset_dir",
    [
        SIMILAR_DIR,
        DISSIMILAR_DIR,
    ],
)
def test_dataset_pairs_have_two_images(dataset_dir):
    """
    Check that every dataset pair contains exactly the required two images.
    """

    pair_dirs = sorted(
        path for path in dataset_dir.iterdir()
        if path.is_dir()
    )

    assert pair_dirs, f"No pair directories found in {dataset_dir}"

    for pair_dir in pair_dirs:

        image_01, image_02 = get_image_pair(pair_dir)

        assert image_01.exists(), (
            f"Missing image_01.jpg in {pair_dir}"
        )

        assert image_02.exists(), (
            f"Missing image_02.jpg in {pair_dir}"
        )


@pytest.mark.parametrize(
    "dataset_dir",
    [
        SIMILAR_DIR,
        DISSIMILAR_DIR,
    ],
)
def test_all_dataset_images_are_readable(dataset_dir):
    """
    Check that all images in the dataset can be opened by OpenCV.
    """

    pair_dirs = sorted(
        path for path in dataset_dir.iterdir()
        if path.is_dir()
    )

    for pair_dir in pair_dirs:

        image_01_path, image_02_path = get_image_pair(pair_dir)

        image_01 = load_image(image_01_path)
        image_02 = load_image(image_02_path)

        assert image_01.ndim in (2, 3)
        assert image_02.ndim in (2, 3)

        assert image_01.size > 0
        assert image_02.size > 0

>>>>>>> f28b4cd ( cap nhat)
