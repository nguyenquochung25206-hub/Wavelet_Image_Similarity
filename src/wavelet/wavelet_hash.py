"""
wavelet_hash.py - TV3

Tao Wavelet Hash tu anh xam bang Discrete Wavelet Transform (DWT).

Quy trinh:
    Image
      ↓
    Grayscale
      ↓
    DWT 2D
      ↓
    Lay LL (approximation)
      ↓
    Resize ve kich thuoc hash
      ↓
    Tinh gia tri trung binh
      ↓
    Chuyen thanh chuoi bit 0/1

Wavelet Hash mac dinh:
    - wavelet = "haar"
    - hash_size = (8, 8)
    - do dai hash = 64 bit
"""

from __future__ import annotations

from typing import Tuple

import numpy as np
import pywt
from PIL import Image


def _validate_hash_size(
    hash_size: Tuple[int, int]
) -> Tuple[int, int]:
    """
    Kiem tra kich thuoc Wavelet Hash.

    Parameters
    ----------
    hash_size:
        Tuple (width, height).

    Returns
    -------
    Tuple[int, int]
        Kich thuoc hop le.

    Raises
    ------
    ValueError
        Neu kich thuoc khong hop le.
    """

    if not isinstance(hash_size, tuple):
        raise ValueError(
            "hash_size phai la tuple, vi du (8, 8)."
        )

    if len(hash_size) != 2:
        raise ValueError(
            "hash_size phai co dang (width, height)."
        )

    width, height = hash_size

    if not isinstance(width, int) or not isinstance(height, int):
        raise ValueError(
            "width va height phai la so nguyen."
        )

    if width <= 0 or height <= 0:
        raise ValueError(
            "width va height phai lon hon 0."
        )

    return width, height


def _to_grayscale_array(
    image: np.ndarray
) -> np.ndarray:
    """
    Chuyen anh dau vao ve anh grayscale float32.

    Ho tro:
    - Anh grayscale 2 chieu.
    - Anh mau BGR/RGB 3 chieu.

    Gia tri pixel duoc dua ve khoang [0, 1].
    """

    if image is None:
        raise ValueError(
            "Anh dau vao khong duoc la None."
        )

    image = np.asarray(image)

    if image.size == 0:
        raise ValueError(
            "Anh dau vao rong."
        )

    # Anh grayscale
    if image.ndim == 2:
        gray = image.astype(np.float32)

    # Anh mau
    elif image.ndim == 3:
        if image.shape[2] == 3:
            # OpenCV thuong dung BGR.
            # Cong thuc grayscale theo OpenCV.
            gray = (
                0.1140 * image[:, :, 0]
                + 0.5870 * image[:, :, 1]
                + 0.2990 * image[:, :, 2]
            ).astype(np.float32)
        else:
            raise ValueError(
                "Anh mau phai co 3 kenh."
            )

    else:
        raise ValueError(
            "Anh phai la mang 2 chieu hoac 3 chieu."
        )

    # Dua pixel ve [0, 1]
    if np.issubdtype(gray.dtype, np.integer):
        max_value = np.iinfo(gray.dtype).max

        if max_value > 0:
            gray = gray / float(max_value)

    else:
        gray = gray.astype(np.float32)

        # Neu gia tri dang o [0,255]
        if gray.max() > 1.0:
            gray = gray / 255.0

    gray = np.clip(
        gray,
        0.0,
        1.0
    )

    return gray.astype(np.float32)


def wavelet_hash(
    image: np.ndarray,
    wavelet: str = "haar",
    hash_size: Tuple[int, int] = (8, 8)
) -> str:
    """
    Tao Wavelet Hash nhi phan.

    Parameters
    ----------
    image:
        Anh dau vao dang numpy array.

    wavelet:
        Ten wavelet duoc PyWavelets ho tro.
        Mac dinh: "haar".

    hash_size:
        Kich thuoc ma tran hash.
        Mac dinh: (8, 8) -> 64 bit.

    Returns
    -------
    str
        Chuoi hash chi gom ky tu '0' va '1'.

    Example
    -------
    >>> hash_value = wavelet_hash(image)
    >>> len(hash_value)
    64
    """

    # ---------------------------------------------------------
    # 1. Kiem tra hash size
    # ---------------------------------------------------------

    width, height = _validate_hash_size(
        hash_size
    )

    # ---------------------------------------------------------
    # 2. Kiem tra wavelet
    # ---------------------------------------------------------

    try:
        pywt.Wavelet(wavelet)

    except Exception as exc:
        raise ValueError(
            f"Wavelet khong hop le: {wavelet}"
        ) from exc

    # ---------------------------------------------------------
    # 3. Chuyen anh ve grayscale
    # ---------------------------------------------------------

    gray = _to_grayscale_array(
        image
    )

    # ---------------------------------------------------------
    # 4. DWT 2D
    # ---------------------------------------------------------
    #
    # pywt.dwt2() tra ve:
    #
    # (
    #     cA,
    #     (cH, cV, cD)
    # )
    #
    # Trong do:
    # cA = LL
    # cH = LH
    # cV = HL
    # cD = HH
    #
    # KHONG duoc viet:
    #
    # ll, _, _, _ = pywt.dwt2(...)
    #
    # vi dwt2 chi tra ve 2 phan tu.
    # ---------------------------------------------------------

    ll, (
        lh,
        hl,
        hh
    ) = pywt.dwt2(
        gray,
        wavelet=wavelet
    )

    # ---------------------------------------------------------
    # 5. Chuyen LL thanh PIL Image
    # ---------------------------------------------------------

    ll_image = Image.fromarray(
        ll.astype(np.float32)
    )

    # ---------------------------------------------------------
    # 6. Resize LL
    # ---------------------------------------------------------

    ll_image = ll_image.resize(
        (width, height),
        Image.Resampling.BILINEAR
    )

    # ---------------------------------------------------------
    # 7. Chuyen lai ve numpy
    # ---------------------------------------------------------

    ll_resized = np.asarray(
        ll_image,
        dtype=np.float32
    )

    # ---------------------------------------------------------
    # 8. Tinh gia tri trung binh
    # ---------------------------------------------------------

    reference = float(
        np.mean(ll_resized)
    )

    # ---------------------------------------------------------
    # 9. So sanh tung pixel voi gia tri trung binh
    # ---------------------------------------------------------

    bits = (
        ll_resized >= reference
    ).astype(np.uint8)

    # ---------------------------------------------------------
    # 10. Chuyen ma tran bit thanh chuoi
    # ---------------------------------------------------------

    hash_value = "".join(
        str(int(bit))
        for bit in bits.flatten()
    )

    return hash_value


def hash_to_matrix(
    hash_value: str,
    hash_size: Tuple[int, int] = (8, 8)
) -> np.ndarray:
    """
    Chuyen chuoi hash ve ma tran 0/1.

    Vi du:
        hash_size = (8, 8)
        hash co 64 bit

    Returns
    -------
    np.ndarray
        Ma tran numpy co kich thuoc (height, width).
    """

    width, height = _validate_hash_size(
        hash_size
    )

    if not isinstance(hash_value, str):
        raise TypeError(
            "hash_value phai la chuoi."
        )

    if len(hash_value) != width * height:
        raise ValueError(
            "Do dai hash khong phu hop voi hash_size."
        )

    if any(
        bit not in {"0", "1"}
        for bit in hash_value
    ):
        raise ValueError(
            "Hash chi duoc chua 0 va 1."
        )

    bits = np.array(
        [int(bit) for bit in hash_value],
        dtype=np.uint8
    )

    return bits.reshape(
        height,
        width
    )


if __name__ == "__main__":
    # Demo nhanh
    image = np.random.default_rng(0).random(
        (256, 256)
    ).astype(np.float32)

    hash_value = wavelet_hash(
        image,
        wavelet="haar",
        hash_size=(8, 8)
    )

    print("Wavelet Hash:")
    print(hash_value)

    print("Do dai hash:", len(hash_value))

    matrix = hash_to_matrix(
        hash_value
    )

    print("Kich thuoc ma tran:", matrix.shape)