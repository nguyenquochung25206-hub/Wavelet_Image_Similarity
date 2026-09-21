"""
compare_wavelets.py — TV2

Thử nghiệm và so sánh hiệu quả của các loại Wavelet khác nhau:
    Haar, db2, db4, db8, sym2, sym4, coif1

Với mỗi loại wavelet, script đo:
    - Thời gian thực hiện DWT (giây)
    - Tỉ lệ năng lượng tập trung ở thành phần xấp xỉ LL (energy compaction)
    - Sai số tái tạo (Reconstruction MSE) khi biến đổi rồi biến đổi ngược
    - Số lượng hệ số ở mỗi sub-band

Cách chạy:
    python experiments/compare_wavelets.py
    python experiments/compare_wavelets.py --image path/to/anh.jpg --level 2

Nếu không truyền --image, script mặc định dùng ảnh thật trong dataset của
nhóm: data/input/similar/pair_01/image_01.jpg. Nếu chưa có dataset (ví dụ
clone repo ở máy khác chưa kéo data/), script tự động dự phòng bằng ảnh mẫu
skimage.data.camera() và in cảnh báo.

Kết quả được lưu vào results/tables/compare_wavelets_results.csv và
results/figures/ll_comparison.png (đúng cấu trúc project ở bai4.txt).

Yêu cầu: pip install PyWavelets numpy pillow matplotlib
(scikit-image chỉ cần khi dùng chế độ dự phòng ở trên)
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from dataclasses import dataclass, field
from typing import List

import numpy as np

# Cho phép chạy script trực tiếp mà không cần cài đặt package
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

from src.wavelet.wavelet_transform import (  # noqa: E402
    SUPPORTED_WAVELETS,
    energy_compaction,
    get_subbands,
    load_image_grayscale,
    normalize_for_display,
    reconstruct_image,
    wavedec2_image,
)

# Ảnh mặc định lấy từ dataset thật của project (data/input/similar/pair_01),
# thay vì ảnh mẫu skimage.data.camera() không liên quan đến đề tài.
DEFAULT_IMAGE = os.path.join(
    PROJECT_ROOT, "data", "input", "similar", "pair_01", "image_01.jpg"
)


@dataclass
class WaveletResult:
    wavelet: str
    level: int
    time_seconds: float
    energy_compaction_ratio: float
    reconstruction_mse: float
    ll_shape: tuple
    total_coeffs: int
    ll_coeffs: int

    @property
    def compression_ratio(self) -> float:
        """Tỉ lệ số hệ số LL so với tổng số hệ số (càng nhỏ càng gọn)."""
        return self.ll_coeffs / self.total_coeffs if self.total_coeffs else 0.0


def _count_coeffs(coeffs) -> int:
    total = int(np.size(coeffs[0]))
    for detail in coeffs[1:]:
        for band in detail:
            total += int(np.size(band))
    return total


def load_sample_image(image_path: str | None) -> np.ndarray:
    """
    Đọc ảnh từ đường dẫn được truyền vào.

    Nếu không truyền --image, mặc định dùng ảnh thật trong dataset của nhóm
    (data/input/similar/pair_01/image_01.jpg). Chỉ khi ảnh đó không tồn tại
    (ví dụ chạy ở máy khác chưa có dataset) mới dự phòng bằng ảnh mẫu
    skimage.data.camera() để script vẫn chạy được.
    """
    path = image_path or DEFAULT_IMAGE
    if os.path.exists(path):
        return load_image_grayscale(path)

    if image_path:
        raise FileNotFoundError(f"Không tìm thấy ảnh: {image_path}")

    print(
        f"[Cảnh báo] Không tìm thấy {DEFAULT_IMAGE}, "
        "dùng tạm ảnh mẫu skimage.data.camera()."
    )
    from skimage import data, img_as_float

    return img_as_float(data.camera())


def evaluate_wavelet(image: np.ndarray, wavelet: str, level: int) -> WaveletResult:
    start = time.perf_counter()
    coeffs = wavedec2_image(image, wavelet=wavelet, level=level)
    elapsed = time.perf_counter() - start

    reconstructed = reconstruct_image(coeffs, wavelet=wavelet)
    reconstructed = reconstructed[: image.shape[0], : image.shape[1]]
    mse = float(np.mean((image - reconstructed) ** 2))

    ll = coeffs[0]
    total_coeffs = _count_coeffs(coeffs)

    return WaveletResult(
        wavelet=wavelet,
        level=level,
        time_seconds=elapsed,
        energy_compaction_ratio=energy_compaction(coeffs),
        reconstruction_mse=mse,
        ll_shape=tuple(ll.shape),
        total_coeffs=total_coeffs,
        ll_coeffs=int(np.size(ll)),
    )


def print_results_table(results: List[WaveletResult]) -> None:
    header = (
        f"{'Wavelet':<8} | {'Level':<5} | {'LL shape':<12} | "
        f"{'Energy@LL':<10} | {'Recon MSE':<12} | {'Time (s)':<10} | {'LL/Total':<8}"
    )
    print(header)
    print("-" * len(header))
    for r in results:
        print(
            f"{r.wavelet:<8} | {r.level:<5} | {str(r.ll_shape):<12} | "
            f"{r.energy_compaction_ratio:<10.4f} | {r.reconstruction_mse:<12.2e} | "
            f"{r.time_seconds:<10.5f} | {r.compression_ratio:<8.4f}"
        )


def save_results_csv(results: List[WaveletResult], out_path: str) -> None:
    import csv

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "wavelet",
                "level",
                "ll_shape",
                "energy_compaction_ratio",
                "reconstruction_mse",
                "time_seconds",
                "ll_over_total_coeffs",
            ]
        )
        for r in results:
            writer.writerow(
                [
                    r.wavelet,
                    r.level,
                    r.ll_shape,
                    r.energy_compaction_ratio,
                    r.reconstruction_mse,
                    r.time_seconds,
                    r.compression_ratio,
                ]
            )
    print(f"\nĐã lưu bảng kết quả: {out_path}")


def save_ll_comparison_figure(
    image: np.ndarray, wavelets: List[str], level: int, out_path: str
) -> None:
    """Lưu hình so sánh trực quan ảnh xấp xỉ (LL) của từng loại wavelet."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    n = len(wavelets) + 1
    cols = min(4, n)
    rows = (n + cols - 1) // cols

    fig, axes = plt.subplots(rows, cols, figsize=(4 * cols, 4 * rows))
    axes = np.atleast_1d(axes).ravel()

    axes[0].imshow(image, cmap="gray")
    axes[0].set_title("Ảnh gốc")
    axes[0].axis("off")

    for i, wavelet in enumerate(wavelets, start=1):
        coeffs = wavedec2_image(image, wavelet=wavelet, level=level)
        bands = get_subbands(coeffs, level=level)
        ll_display = normalize_for_display(bands["LL"])
        axes[i].imshow(ll_display, cmap="gray")
        axes[i].set_title(f"LL — {wavelet} (level {level})")
        axes[i].axis("off")

    for j in range(n, len(axes)):
        axes[j].axis("off")

    fig.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"Đã lưu hình so sánh LL: {out_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="So sánh các loại Wavelet trên một ảnh.")
    parser.add_argument("--image", type=str, default=None, help="Đường dẫn ảnh đầu vào (tùy chọn).")
    parser.add_argument("--level", type=int, default=1, help="Số level DWT (mặc định: 1).")
    parser.add_argument(
        "--wavelets",
        type=str,
        nargs="+",
        default=SUPPORTED_WAVELETS,
        help=f"Danh sách wavelet cần thử (mặc định: {SUPPORTED_WAVELETS}).",
    )
    parser.add_argument(
        "--out-dir",
        type=str,
        default=os.path.join(PROJECT_ROOT, "results"),
        help=(
            "Thư mục results/ gốc của project (mặc định). CSV được lưu vào "
            "<out-dir>/tables/, hình so sánh lưu vào <out-dir>/figures/, "
            "đúng theo cấu trúc results/tables [TV5] và results/figures [TV6]."
        ),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    image = load_sample_image(args.image)
    print(f"Ảnh đầu vào: shape={image.shape}, level={args.level}")
    print(f"Danh sách wavelet thử nghiệm: {args.wavelets}\n")

    results = [evaluate_wavelet(image, w, args.level) for w in args.wavelets]
    print_results_table(results)

    best_compaction = max(results, key=lambda r: r.energy_compaction_ratio)
    fastest = min(results, key=lambda r: r.time_seconds)
    print(
        f"\n=> Nén năng lượng tốt nhất (LL giữ nhiều năng lượng nhất): "
        f"{best_compaction.wavelet} ({best_compaction.energy_compaction_ratio:.4f})"
    )
    print(f"=> Nhanh nhất: {fastest.wavelet} ({fastest.time_seconds:.5f}s)")

    save_results_csv(
        results, os.path.join(args.out_dir, "tables", "compare_wavelets_results.csv")
    )
    save_ll_comparison_figure(
        image,
        args.wavelets,
        args.level,
        os.path.join(args.out_dir, "figures", "ll_comparison.png"),
    )


if __name__ == "__main__":
    main()
