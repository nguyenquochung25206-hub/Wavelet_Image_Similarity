"""
metrics.py — TV5

Tính các chỉ số đánh giá hiệu năng của hệ thống so sánh ảnh:
    Confusion matrix (TP / TN / FP / FN), Accuracy, Sensitivity (TPR),
    Specificity (TNR), Precision, F1-score.

Quy ước (dùng xuyên suốt project):
    - Lớp dương (positive, nhãn 1)  = cặp ảnh SIMILAR
    - Lớp âm   (negative, nhãn 0)   = cặp ảnh DISSIMILAR
    - Quy tắc phân loại: normalized Hamming distance <= threshold  ->  Similar

Lý thuyết: xem docs/03_research/evaluation_methods.md
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Dict, Sequence

import numpy as np

ArrayLike = Sequence[int]


# --------------------------------------------------------------------------- #
# Kiểm tra đầu vào
# --------------------------------------------------------------------------- #

def _as_binary_array(values: ArrayLike, name: str) -> np.ndarray:
    """Chuyển về mảng 1 chiều gồm 0/1; báo lỗi nếu có giá trị khác."""
    arr = np.asarray(values).reshape(-1)
    if arr.size == 0:
        raise ValueError(f"{name} không được rỗng.")
    if arr.dtype == bool:
        return arr.astype(int)
    if not np.all(np.isin(arr, (0, 1))):
        raise ValueError(f"{name} chỉ được chứa các giá trị 0 hoặc 1.")
    return arr.astype(int)


def _check_same_length(y_true: np.ndarray, y_pred: np.ndarray) -> None:
    if y_true.shape != y_pred.shape:
        raise ValueError(
            "y_true và y_pred phải có cùng số phần tử "
            f"(nhận {y_true.size} và {y_pred.size})."
        )


def _safe_div(numerator: float, denominator: float) -> float:
    """Chia an toàn: trả về 0.0 khi mẫu số bằng 0 (ví dụ không có lớp dương)."""
    return float(numerator) / float(denominator) if denominator else 0.0


# --------------------------------------------------------------------------- #
# Confusion matrix
# --------------------------------------------------------------------------- #

def confusion_matrix(y_true: ArrayLike, y_pred: ArrayLike) -> Dict[str, int]:
    """
    Trả về dict {"TP", "TN", "FP", "FN"}.

        TP: thực tế Similar,    dự đoán Similar
        TN: thực tế Dissimilar, dự đoán Dissimilar
        FP: thực tế Dissimilar, dự đoán Similar     (báo nhầm)
        FN: thực tế Similar,    dự đoán Dissimilar  (bỏ sót)
    """
    t = _as_binary_array(y_true, "y_true")
    p = _as_binary_array(y_pred, "y_pred")
    _check_same_length(t, p)
    return {
        "TP": int(np.sum((t == 1) & (p == 1))),
        "TN": int(np.sum((t == 0) & (p == 0))),
        "FP": int(np.sum((t == 0) & (p == 1))),
        "FN": int(np.sum((t == 1) & (p == 0))),
    }


# --------------------------------------------------------------------------- #
# Các chỉ số từ TP / TN / FP / FN
# --------------------------------------------------------------------------- #

def accuracy(tp: int, tn: int, fp: int, fn: int) -> float:
    """Accuracy = (TP + TN) / (TP + TN + FP + FN)."""
    return _safe_div(tp + tn, tp + tn + fp + fn)


def sensitivity(tp: int, fn: int) -> float:
    """Sensitivity (Recall, TPR) = TP / (TP + FN)."""
    return _safe_div(tp, tp + fn)


def specificity(tn: int, fp: int) -> float:
    """Specificity (TNR) = TN / (TN + FP)."""
    return _safe_div(tn, tn + fp)


def precision(tp: int, fp: int) -> float:
    """Precision (PPV) = TP / (TP + FP)."""
    return _safe_div(tp, tp + fp)


def f1_score(tp: int, fp: int, fn: int) -> float:
    """F1 = 2TP / (2TP + FP + FN)."""
    return _safe_div(2 * tp, 2 * tp + fp + fn)


@dataclass(frozen=True)
class MetricsResult:
    """Toàn bộ chỉ số đánh giá tại một ngưỡng phân loại."""

    threshold: float
    tp: int
    tn: int
    fp: int
    fn: int
    accuracy: float
    sensitivity: float
    specificity: float
    precision: float
    f1: float

    @property
    def total(self) -> int:
        return self.tp + self.tn + self.fp + self.fn

    @property
    def balanced_accuracy(self) -> float:
        """Trung bình Sensitivity và Specificity (ổn khi dữ liệu lệch lớp)."""
        return (self.sensitivity + self.specificity) / 2.0

    def to_dict(self) -> Dict[str, float]:
        data = asdict(self)
        data["balanced_accuracy"] = self.balanced_accuracy
        return data


def compute_metrics(
    y_true: ArrayLike, y_pred: ArrayLike, threshold: float = float("nan")
) -> MetricsResult:
    """Tính toàn bộ chỉ số từ nhãn thật và nhãn dự đoán (1 = Similar, 0 = Dissimilar)."""
    cm = confusion_matrix(y_true, y_pred)
    tp, tn, fp, fn = cm["TP"], cm["TN"], cm["FP"], cm["FN"]
    return MetricsResult(
        threshold=float(threshold),
        tp=tp,
        tn=tn,
        fp=fp,
        fn=fn,
        accuracy=accuracy(tp, tn, fp, fn),
        sensitivity=sensitivity(tp, fn),
        specificity=specificity(tn, fp),
        precision=precision(tp, fp),
        f1=f1_score(tp, fp, fn),
    )


# --------------------------------------------------------------------------- #
# Phân loại theo ngưỡng khoảng cách
# --------------------------------------------------------------------------- #

def predict_by_threshold(distances: Sequence[float], threshold: float) -> np.ndarray:
    """
    Phân loại theo quy tắc của project: distance <= threshold -> Similar (1).

    `distances` là normalized Hamming distance trong [0, 1]
    (cùng thang đo với HammingDistance.threshold của TV4).
    """
    d = np.asarray(distances, dtype=float).reshape(-1)
    if d.size == 0:
        raise ValueError("distances không được rỗng.")
    return (d <= float(threshold)).astype(int)


def evaluate_at_threshold(
    y_true: ArrayLike, distances: Sequence[float], threshold: float
) -> MetricsResult:
    """Phân loại theo ngưỡng rồi tính toàn bộ chỉ số."""
    y_pred = predict_by_threshold(distances, threshold)
    return compute_metrics(y_true, y_pred, threshold=threshold)


def threshold_sweep(
    y_true: ArrayLike, distances: Sequence[float], thresholds: Sequence[float]
) -> list[MetricsResult]:
    """Tính chỉ số tại nhiều ngưỡng khác nhau (dùng để vẽ/so sánh)."""
    return [evaluate_at_threshold(y_true, distances, t) for t in thresholds]
