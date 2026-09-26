"""
Wavelet Hash implementation.

Module:
    src/wavelet/wavelet_hash.py

Description:
    Generate a binary hash from an image using
    the Discrete Wavelet Transform (DWT).

Pipeline:

    Image
      ↓
    DWT
      ↓
    Approximation coefficients (LL)
      ↓
    Resize
      ↓
    Mean threshold
      ↓
    Binary hash
"""


import numpy as np
import pywt
from PIL import Image


def wavelet_hash(
    image,
    wavelet="haar",
    hash_size=(8, 8)
):
    """
    Generate a binary Wavelet Hash for an image.

    Parameters
    ----------
    image : numpy.ndarray
        Input grayscale image.

    wavelet : str
        Wavelet type used for DWT.
        Default is "haar".

    hash_size : tuple
        Size of the generated hash.
        Default is (8, 8), producing 64 bits.

    Returns
    -------
    str
        Binary hash represented as a string of 0 and 1.

    Raises
    ------
    ValueError
        If hash_size is invalid or the image is invalid.

    TypeError
        If hash_size has an invalid type.

    """

    # ---------------------------------------------------------------
    # Validate image
    # ---------------------------------------------------------------

    if not isinstance(image, np.ndarray):
        raise TypeError("image must be a numpy.ndarray")

    if image.size == 0:
        raise ValueError("image must not be empty")

    if image.ndim != 2:
        raise ValueError(
            "image must be a 2D grayscale image"
        )

    # ---------------------------------------------------------------
    # Validate hash_size
    # ---------------------------------------------------------------

    if not isinstance(hash_size, tuple):
        raise TypeError(
            "hash_size must be a tuple"
        )

    if len(hash_size) != 2:
        raise ValueError(
            "hash_size must contain exactly two values"
        )

    height, width = hash_size

    if height <= 0 or width <= 0:
        raise ValueError(
            "hash_size values must be greater than zero"
        )

    # ---------------------------------------------------------------
    # Validate wavelet
    # ---------------------------------------------------------------

    try:
        pywt.Wavelet(wavelet)
    except Exception as exc:
        raise ValueError(
            f"Invalid wavelet: {wavelet}"
        ) from exc

    # ---------------------------------------------------------------
    # Convert image to float32
    # ---------------------------------------------------------------

    image = image.astype(np.float32)

    # ---------------------------------------------------------------
    # Discrete Wavelet Transform
    # ---------------------------------------------------------------

    coefficients = pywt.dwt2(
        image,
        wavelet
    )

    # Approximation coefficients (LL)
    ll, _, _, _ = coefficients

    # ---------------------------------------------------------------
    # Resize LL coefficients
    # ---------------------------------------------------------------

    ll_image = Image.fromarray(
        ll.astype(np.float32)
    )

    ll_image = ll_image.resize(
        (width, height),
        Image.Resampling.BILINEAR
    )

    ll_resized = np.asarray(
        ll_image,
        dtype=np.float32
    )

    # ---------------------------------------------------------------
    # Calculate mean threshold
    # ---------------------------------------------------------------

    mean_value = np.mean(ll_resized)

    # ---------------------------------------------------------------
    # Generate binary hash
    # ---------------------------------------------------------------

    binary_hash = (
        ll_resized >= mean_value
    ).astype(np.uint8)

    # ---------------------------------------------------------------
    # Convert matrix to binary string
    # ---------------------------------------------------------------

    return "".join(
        str(int(bit))
        for bit in binary_hash.flatten()
    )