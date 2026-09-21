"""
roc_curve.py — TV5

Tạo và vẽ đường cong ROC, tính AUC, chọn ngưỡng (threshold) tối ưu cho
Hamming Distance, cùng các biểu đồ đánh giá đi kèm.

Cách hiểu:
    - Điểm càng NHỎ (distance nhỏ) càng giống nhau -> dự đoán Similar.
    - Mỗi ngưỡng t cho một điểm ROC: (FPR, TPR) với quy tắc distance <= t.
    - Quét t qua mọi giá trị distance thực tế -> đường cong ROC.

Không phụ thuộc scikit-learn (tự cài đặt bằng numpy) để dễ giải thích trong
báo cáo; tests/test_evaluation.py đối chiếu kết quả với sklearn.

Lý thuyết: xem docs/03_research/evaluation_methods.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Sequence

import numpy as np


@dataclass(frozen=True)
class RocResult:
    """Kết quả phân tích ROC.

    fpr, tpr, thresholds có cùng độ dài; thresholds[i] là ngưỡng distance tạo
    ra điểm (fpr[i], tpr[i]). Điểm đầu tiên là (0, 0) với ngưỡng nhỏ hơn mọi
    distance (không dự đoán Similar nào).
    """

    fpr: np.ndarray
    tpr: np.ndarray
    thresholds: np.ndarray
    auc: float
    youden_threshold: float
    youden_j: float
    topleft_threshold: float
    youden_index: int  # chỉ số điểm ROC đạt Youden's J lớn nhất


def _validate(y_true: Sequence[int], distances: Sequence[float]):
    t = np.asarray(y_true).reshape(-1)
    d = np.asarray(distances, dtype=float).reshape(-1)
    if t.size == 0 or d.size == 0:
        raise ValueError("y_true và distances không được rỗng.")
    if t.shape != d.shape:
        raise ValueError(
            f"y_true và distances phải cùng độ dài (nhận {t.size} và {d.size})."
        )
    if not np.all(np.isin(t, (0, 1))):
        raise ValueError("y_true chỉ được chứa 0 hoặc 1.")
    if np.any(~np.isfinite(d)):
        raise ValueError("distances chứa giá trị không hợp lệ (NaN/inf).")
    n_pos = int(np.sum(t == 1))
    n_neg = int(np.sum(t == 0))
    if n_pos == 0 or n_neg == 0:
        raise ValueError("Cần có cả cặp Similar và Dissimilar để vẽ ROC.")
    return t.astype(int), d, n_pos, n_neg


def auc_score(fpr: Sequence[float], tpr: Sequence[float]) -> float:
    """Diện tích dưới đường cong (quy tắc hình thang)."""
    x = np.asarray(fpr, dtype=float)
    y = np.asarray(tpr, dtype=float)
    return float(np.sum((x[1:] - x[:-1]) * (y[1:] + y[:-1]) / 2.0))


def _with_margin(thresholds: np.ndarray, idx: int) -> float:
    """
    Ngưỡng tại điểm ROC thứ idx cho cùng kết quả phân loại với mọi ngưỡng nằm
    trong [thresholds[idx], thresholds[idx + 1]). Lấy điểm giữa khoảng đó để
    ngưỡng cách đều hai cặp distance lân cận (ổn định hơn với dữ liệu mới)
    thay vì đặt sát đúng một giá trị distance của tập dữ liệu.
    """
    if idx + 1 < len(thresholds):
        return float((thresholds[idx] + thresholds[idx + 1]) / 2.0)
    return float(thresholds[idx])


def compute_roc(y_true: Sequence[int], distances: Sequence[float]) -> RocResult:
    """
    Tính đường cong ROC từ nhãn thật (1 = Similar) và normalized Hamming distance.

    Xử lý đúng trường hợp nhiều cặp có cùng distance (ties): chỉ tạo một điểm
    ROC cho mỗi giá trị distance duy nhất.
    """
    t, d, n_pos, n_neg = _validate(y_true, distances)

    unique_d = np.unique(d)  # đã sắp xếp tăng dần
    fpr = [0.0]
    tpr = [0.0]
    thresholds = [unique_d[0] - 1e-9]  # nhỏ hơn mọi distance: không ai là Similar
    for thr in unique_d:
        pred_sim = d <= thr
        tpr.append(float(np.sum(pred_sim & (t == 1))) / n_pos)
        fpr.append(float(np.sum(pred_sim & (t == 0))) / n_neg)
        thresholds.append(float(thr))

    fpr_a, tpr_a, thr_a = np.array(fpr), np.array(tpr), np.array(thresholds)
    auc = auc_score(fpr_a, tpr_a)

    # Ngưỡng tối ưu 1: Youden's J = TPR - FPR = Sensitivity + Specificity - 1
    j = tpr_a - fpr_a
    best = int(np.argmax(j))  # nếu nhiều điểm cùng J, lấy điểm đầu tiên (ngưỡng nhỏ nhất)
    # Ngưỡng tối ưu 2: gần góc trên-trái (0, 1) nhất
    topleft = int(np.argmin(np.hypot(fpr_a, 1.0 - tpr_a)))

    return RocResult(
        fpr=fpr_a,
        tpr=tpr_a,
        thresholds=thr_a,
        auc=auc,
        youden_threshold=_with_margin(thr_a, best),
        youden_j=float(j[best]),
        topleft_threshold=_with_margin(thr_a, topleft),
        youden_index=best,
    )


def select_threshold(
    y_true: Sequence[int], distances: Sequence[float], method: str = "youden"
) -> float:
    """Chọn ngưỡng distance tối ưu: method = "youden" hoặc "topleft"."""
    roc = compute_roc(y_true, distances)
    if method == "youden":
        return roc.youden_threshold
    if method == "topleft":
        return roc.topleft_threshold
    raise ValueError("method phải là 'youden' hoặc 'topleft'.")


def leave_one_out_accuracy(
    y_true: Sequence[int], distances: Sequence[float], method: str = "youden"
) -> float:
    """
    Accuracy ước lượng công bằng hơn: với mỗi cặp i, chọn ngưỡng bằng ROC trên
    các cặp CÒN LẠI rồi dự đoán cặp i (leave-one-out).

    Cần thiết vì chọn ngưỡng và đánh giá trên cùng một tập nhỏ sẽ cho kết quả
    lạc quan.
    """
    t = np.asarray(y_true).reshape(-1).astype(int)
    d = np.asarray(distances, dtype=float).reshape(-1)
    correct = 0
    for i in range(t.size):
        mask = np.arange(t.size) != i
        try:
            thr = select_threshold(t[mask], d[mask], method)
        except ValueError:  # phần còn lại chỉ còn một lớp
            return float("nan")
        pred = int(d[i] <= thr)
        correct += int(pred == t[i])
    return correct / t.size


# --------------------------------------------------------------------------- #
# Vẽ biểu đồ
# --------------------------------------------------------------------------- #

def _get_pyplot():
    import matplotlib

    matplotlib.use("Agg")  # chạy được cả khi không có màn hình
    import matplotlib.pyplot as plt

    return plt


def plot_roc_curve(
    roc: RocResult,
    out_path: Optional[str] = None,
    title: str = "ROC curve — Wavelet Hash + Hamming Distance",
):
    """Vẽ đường ROC, đường chéo ngẫu nhiên và điểm ngưỡng Youden."""
    plt = _get_pyplot()
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.plot(roc.fpr, roc.tpr, marker="o", ms=3, lw=2, label=f"ROC (AUC = {roc.auc:.3f})")
    ax.plot([0, 1], [0, 1], "--", color="gray", label="Ngẫu nhiên (AUC = 0.5)")
    k = roc.youden_index
    ax.scatter(
        [roc.fpr[k]], [roc.tpr[k]], s=90, color="red", zorder=5,
        label=f"Ngưỡng Youden = {roc.youden_threshold:.4f}",
    )
    ax.set_xlim(-0.02, 1.02)
    ax.set_ylim(-0.02, 1.02)
    ax.set_xlabel("False Positive Rate (1 − Specificity)")
    ax.set_ylabel("True Positive Rate (Sensitivity)")
    ax.set_title(title)
    ax.grid(alpha=0.3)
    ax.legend(loc="lower right")
    fig.tight_layout()
    if out_path:
        _save(fig, out_path)
    return fig


def plot_distance_distribution(
    y_true: Sequence[int],
    distances: Sequence[float],
    threshold: Optional[float] = None,
    out_path: Optional[str] = None,
):
    """Histogram normalized Hamming distance của cặp Similar và Dissimilar."""
    plt = _get_pyplot()
    t = np.asarray(y_true).astype(int)
    d = np.asarray(distances, dtype=float)
    bins = np.linspace(0, max(0.6, float(d.max()) + 0.02), 25)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.hist(d[t == 1], bins=bins, alpha=0.7, label="Similar", color="tab:green")
    ax.hist(d[t == 0], bins=bins, alpha=0.7, label="Dissimilar", color="tab:red")
    if threshold is not None:
        ax.axvline(threshold, color="black", ls="--", label=f"Ngưỡng = {threshold:.4f}")
    ax.set_xlabel("Normalized Hamming distance")
    ax.set_ylabel("Số cặp ảnh")
    ax.set_title("Phân bố Hamming distance theo nhóm")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    if out_path:
        _save(fig, out_path)
    return fig


def plot_confusion_matrix(
    tp: int, tn: int, fp: int, fn: int,
    out_path: Optional[str] = None,
    title: str = "Confusion matrix",
):
    """Vẽ confusion matrix 2x2 (hàng = thực tế, cột = dự đoán)."""
    plt = _get_pyplot()
    mat = np.array([[tp, fn], [fp, tn]])
    fig, ax = plt.subplots(figsize=(4.6, 4.2))
    ax.imshow(mat, cmap="Blues")
    labels = [["TP", "FN"], ["FP", "TN"]]
    for i in range(2):
        for j in range(2):
            ax.text(
                j, i, f"{labels[i][j]}\n{mat[i, j]}", ha="center", va="center",
                color="white" if mat[i, j] > mat.max() / 2 else "black", fontsize=13,
            )
    ax.set_xticks([0, 1], ["Similar", "Dissimilar"])
    ax.set_yticks([0, 1], ["Similar", "Dissimilar"])
    ax.set_xlabel("Dự đoán")
    ax.set_ylabel("Thực tế")
    ax.set_title(title)
    fig.tight_layout()
    if out_path:
        _save(fig, out_path)
    return fig


def _save(fig, out_path: str) -> None:
    import os

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    fig.savefig(out_path, dpi=150)
    _get_pyplot().close(fig)
