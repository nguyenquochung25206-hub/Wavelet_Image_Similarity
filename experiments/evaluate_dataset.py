"""
evaluate_dataset.py — TV5

Đánh giá hệ thống Wavelet Hash + Hamming Distance trên TOÀN BỘ dataset
(data/input/labels.csv): so ground truth với kết quả dự đoán để tính
TP / TN / FP / FN, Accuracy, Sensitivity, Specificity, ROC và AUC.

Cách chạy (từ thư mục gốc project):

    python experiments/evaluate_dataset.py
    python experiments/evaluate_dataset.py --threshold 0.25
    python experiments/evaluate_dataset.py --wavelet haar --hash-size 16
    python experiments/evaluate_dataset.py --sweep-wavelets      # thí nghiệm 1: so sánh các loại Wavelet

Nguồn Wavelet Hash (--hash-source):
    auto     (mặc định) dùng WaveletTransform + WaveletHash của TV2/TV3 nếu đã
             cài đặt xong; nếu chưa thì tự động dùng bản tham chiếu bên dưới.
    team     bắt buộc dùng module của TV2/TV3 (báo lỗi nếu chưa có).
    builtin  bản tham chiếu của TV5: tiền xử lý TV1 -> DWT (TV2) -> LL 8x8 ->
             ngưỡng median -> chuỗi bit (giống ý tưởng whash của imagehash).

Đầu ra:
    results/tables/pair_results.csv          kết quả từng cặp ảnh
    results/tables/evaluation_metrics.csv    chỉ số tại các ngưỡng
    results/tables/roc_points.csv            các điểm của đường ROC
    results/tables/variation_breakdown.csv   độ nhạy theo loại biến thể
    results/tables/wavelet_comparison.csv    (khi dùng --sweep-wavelets)
    results/figures/roc_curve.png, distance_distribution.png, confusion_matrix.png
    results/reports/evaluation_report.md     báo cáo tự động
"""

from __future__ import annotations

import argparse
import csv
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List, Optional

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.evaluation import (  # noqa: E402
    compute_roc,
    evaluate_at_threshold,
    leave_one_out_accuracy,
    plot_confusion_matrix,
    plot_distance_distribution,
    plot_roc_curve,
    predict_by_threshold,
)
from src.preprocessing.image_preprocessor import preprocess_image  # noqa: E402

DEFAULT_LABELS = PROJECT_ROOT / "data" / "input" / "labels.csv"
DEFAULT_THRESHOLD = 0.25  # ngưỡng thử nghiệm ban đầu của TV4
SWEEP_WAVELETS = ["haar", "db2", "db4", "db8", "sym2", "sym4", "coif1"]

HashFn = Callable[[np.ndarray], str]


# --------------------------------------------------------------------------- #
# Wavelet Hash: bản của nhóm (TV2/TV3) hoặc bản tham chiếu
# --------------------------------------------------------------------------- #

def builtin_wavelet_hash(
    image: np.ndarray, wavelet: str = "db4", hash_size: int = 8
) -> str:
    """
    Bản Wavelet Hash tham chiếu của TV5 (dùng khi TV3 chưa hoàn thiện).

    Các bước:
        1. Ảnh đã tiền xử lý (256x256, xám, [0,1]) từ TV1.
        2. DWT nhiều mức bằng pywt.wavedec2 cho tới khi LL còn cỡ hash_size x hash_size.
        3. Lấy ma trận xấp xỉ LL (nếu lớn hơn hash_size thì thu nhỏ bằng
           trung bình vùng - INTER_AREA), rồi lượng tử hóa bằng ngưỡng MEDIAN:
           hệ số > median -> bit 1, ngược lại -> bit 0.
        4. Duỗi thành chuỗi hash_size^2 bit.

    Wavelet mặc định db4 theo ví dụ trong đề bài / mặc định của TV2.
    """
    import cv2
    import pywt

    from src.wavelet.wavelet_transform import wavedec2_image

    h, w = image.shape
    level = int(round(np.log2(min(h, w) / hash_size)))
    level = max(1, min(level, pywt.dwtn_max_level(image.shape, wavelet)))
    coeffs = wavedec2_image(image.astype(np.float64), wavelet=wavelet, level=level)
    ll = np.asarray(coeffs[0], dtype=np.float64)
    if ll.shape != (hash_size, hash_size):
        ll = cv2.resize(ll, (hash_size, hash_size), interpolation=cv2.INTER_AREA)
    bits = ll > np.median(ll)
    return "".join("1" if b else "0" for b in bits.ravel())


def build_hash_fn(
    source: str, wavelet: str, hash_size: int
) -> tuple[HashFn, str]:
    """Trả về (hàm ảnh-đã-tiền-xử-lý -> chuỗi bit, mô tả nguồn hash)."""
    team_error: Optional[Exception] = None
    if source in ("auto", "team"):
        try:
            from src.wavelet.wavelet_hash import WaveletHash  # type: ignore
            from src.wavelet.wavelet_transform import WaveletTransform  # type: ignore

            transform, hasher = WaveletTransform(), WaveletHash()

            def team_fn(image: np.ndarray) -> str:
                bits = hasher.generate(transform.transform(image))
                return bits if isinstance(bits, str) else "".join(str(int(b)) for b in np.ravel(bits))

            return team_fn, "WaveletTransform + WaveletHash của nhóm (TV2/TV3)"
        except (ImportError, AttributeError, TypeError) as exc:
            team_error = exc
            if source == "team":
                raise RuntimeError(
                    "Chưa dùng được module TV2/TV3 (cần class WaveletTransform và "
                    f"WaveletHash): {exc}"
                ) from exc

    if team_error is not None:
        print(
            "[Thông báo] Module WaveletHash của TV3 chưa sẵn sàng "
            f"({type(team_error).__name__}) -> dùng bản tham chiếu builtin của TV5."
        )

    def builtin_fn(image: np.ndarray) -> str:
        return builtin_wavelet_hash(image, wavelet=wavelet, hash_size=hash_size)

    return builtin_fn, (
        f"Bản tham chiếu TV5 (wavelet={wavelet}, LL {hash_size}x{hash_size}, "
        f"{hash_size * hash_size} bit, ngưỡng median)"
    )


# --------------------------------------------------------------------------- #
# Đọc dataset
# --------------------------------------------------------------------------- #

@dataclass
class PairRecord:
    pair_id: str
    label: int  # 1 = similar, 0 = dissimilar
    variation: str
    image_1: Path
    image_2: Path


def load_pairs(labels_csv: Path, input_root: Path) -> List[PairRecord]:
    """Đọc labels.csv và kiểm tra đủ file ảnh cho mọi cặp."""
    if not labels_csv.exists():
        raise FileNotFoundError(f"Không tìm thấy file nhãn: {labels_csv}")

    pairs: List[PairRecord] = []
    with open(labels_csv, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            label_text = row["label"].strip().lower()
            if label_text not in ("similar", "dissimilar"):
                raise ValueError(f"Nhãn không hợp lệ '{row['label']}' ở cặp {row['pair_id']}")
            folder = input_root / row["pair_id"].strip()
            img1, img2 = folder / "image_01.jpg", folder / "image_02.jpg"
            for img in (img1, img2):
                if not img.exists():
                    raise FileNotFoundError(f"Thiếu ảnh: {img}")
            pairs.append(
                PairRecord(
                    pair_id=row["pair_id"].strip(),
                    label=1 if label_text == "similar" else 0,
                    variation=row.get("variation", "n/a").strip(),
                    image_1=img1,
                    image_2=img2,
                )
            )
    if not pairs:
        raise ValueError("labels.csv không có cặp ảnh nào.")
    return pairs


def compute_pair_hashes(pairs: List[PairRecord], hash_fn: HashFn) -> List[Dict]:
    """Tiền xử lý (TV1) -> hash -> Hamming distance cho từng cặp."""
    rows = []
    for p in pairs:
        h1 = hash_fn(preprocess_image(p.image_1))
        h2 = hash_fn(preprocess_image(p.image_2))
        if len(h1) != len(h2):
            raise ValueError(f"Hai hash của {p.pair_id} khác độ dài.")
        dist = sum(a != b for a, b in zip(h1, h2))
        rows.append(
            {
                "pair_id": p.pair_id,
                "label": p.label,
                "variation": p.variation,
                "hash_1": h1,
                "hash_2": h2,
                "hash_length": len(h1),
                "hamming_distance": dist,
                "normalized_distance": dist / len(h1),
            }
        )
    return rows


# --------------------------------------------------------------------------- #
# Ghi kết quả
# --------------------------------------------------------------------------- #

def _write_csv(path: Path, header: List[str], rows: List[List]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


def variation_breakdown(rows: List[Dict], threshold: float) -> List[List]:
    """Tỉ lệ nhận đúng (Similar) theo từng loại biến thể của cặp similar."""
    groups: Dict[str, List[bool]] = {}
    for r in rows:
        if r["label"] != 1:
            continue
        key = "combo" if r["variation"].startswith("combo") else r["variation"]
        groups.setdefault(key, []).append(r["normalized_distance"] <= threshold)
    out = []
    for key, oks in sorted(groups.items()):
        out.append([key, len(oks), int(sum(oks)), f"{sum(oks) / len(oks):.4f}"])
    return out


def write_report(
    path: Path,
    source_desc: str,
    rows: List[Dict],
    roc,
    m_default,
    m_opt,
    loo_acc: float,
    wrong_default: List[Dict],
    wrong_opt: List[Dict],
    sweep: Optional[List[Dict]],
) -> None:
    def m_line(name, m):
        return (
            f"| {name} | {m.threshold:.4f} | {m.tp} | {m.tn} | {m.fp} | {m.fn} | "
            f"{m.accuracy:.4f} | {m.sensitivity:.4f} | {m.specificity:.4f} | "
            f"{m.precision:.4f} | {m.f1:.4f} |"
        )

    def wrong_lines(wrong):
        if not wrong:
            return ["- Không có cặp nào bị phân loại sai."]
        return [
            f"- `{r['pair_id']}` (thực tế {'Similar' if r['label'] else 'Dissimilar'}, "
            f"biến thể: {r['variation']}) — distance = {r['hamming_distance']}/"
            f"{r['hash_length']} = {r['normalized_distance']:.4f}"
            for r in wrong
        ]

    n_sim = sum(r["label"] for r in rows)
    lines = [
        "# Báo cáo đánh giá tự động (TV5)",
        "",
        f"- Nguồn hash: {source_desc}",
        f"- Số cặp: {len(rows)} ({n_sim} similar, {len(rows) - n_sim} dissimilar)",
        f"- Độ dài hash: {rows[0]['hash_length']} bit",
        f"- **AUC = {roc.auc:.4f}**",
        f"- Ngưỡng tối ưu theo Youden's J: {roc.youden_threshold:.4f} (J = {roc.youden_j:.4f})",
        f"- Accuracy leave-one-out (ước lượng công bằng): {loo_acc:.4f}",
        "",
        "## Chỉ số theo ngưỡng",
        "",
        "| Ngưỡng | Giá trị | TP | TN | FP | FN | Accuracy | Sensitivity | Specificity | Precision | F1 |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
        m_line("Mặc định (TV4)", m_default),
        m_line("Tối ưu (ROC)", m_opt),
        "",
        f"## Cặp bị phân loại sai tại ngưỡng mặc định {m_default.threshold:.2f}",
        "",
        *wrong_lines(wrong_default),
        "",
        f"## Cặp bị phân loại sai tại ngưỡng tối ưu {m_opt.threshold:.4f}",
        "",
        *wrong_lines(wrong_opt),
        "",
    ]
    if sweep:
        lines += [
            "## So sánh các loại Wavelet",
            "",
            "| Wavelet | AUC | Ngưỡng Youden | Accuracy | Sensitivity | Specificity | LOO Accuracy |",
            "|---|---|---|---|---|---|---|",
        ]
        for s in sweep:
            lines.append(
                f"| {s['wavelet']} | {s['auc']:.4f} | {s['threshold']:.4f} | "
                f"{s['accuracy']:.4f} | {s['sensitivity']:.4f} | {s['specificity']:.4f} | "
                f"{s['loo_accuracy']:.4f} |"
            )
        lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


# --------------------------------------------------------------------------- #
# Chương trình chính
# --------------------------------------------------------------------------- #

def evaluate(rows: List[Dict], threshold: float):
    y = np.array([r["label"] for r in rows])
    d = np.array([r["normalized_distance"] for r in rows])
    roc = compute_roc(y, d)
    m_default = evaluate_at_threshold(y, d, threshold)
    m_opt = evaluate_at_threshold(y, d, roc.youden_threshold)
    loo = leave_one_out_accuracy(y, d)
    return y, d, roc, m_default, m_opt, loo


def run_wavelet_sweep(pairs: List[PairRecord], hash_size: int) -> List[Dict]:
    """Thí nghiệm so sánh hiệu quả PHÂN LOẠI của nhiều loại wavelet."""
    out = []
    for wv in SWEEP_WAVELETS:
        fn = lambda img, wv=wv: builtin_wavelet_hash(img, wavelet=wv, hash_size=hash_size)  # noqa: E731
        rows = compute_pair_hashes(pairs, fn)
        _, _, roc, _, m_opt, loo = evaluate(rows, DEFAULT_THRESHOLD)
        out.append(
            {
                "wavelet": wv,
                "auc": roc.auc,
                "threshold": roc.youden_threshold,
                "accuracy": m_opt.accuracy,
                "sensitivity": m_opt.sensitivity,
                "specificity": m_opt.specificity,
                "loo_accuracy": loo,
            }
        )
    return out


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Đánh giá Wavelet Hash + Hamming Distance trên toàn bộ dataset."
    )
    p.add_argument("--labels", type=Path, default=DEFAULT_LABELS, help="File labels.csv.")
    p.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD,
                   help="Ngưỡng normalized Hamming để so sánh với ngưỡng tối ưu (mặc định 0.25).")
    p.add_argument("--hash-source", choices=["auto", "team", "builtin"], default="auto")
    p.add_argument("--wavelet", default="db4", help="Wavelet cho bản builtin (mặc định db4).")
    p.add_argument("--hash-size", type=int, default=8, help="Cạnh ma trận LL (hash = size^2 bit).")
    p.add_argument("--sweep-wavelets", action="store_true",
                   help="So sánh hiệu quả phân loại của các loại wavelet (bản builtin).")
    p.add_argument("--out-dir", type=Path, default=PROJECT_ROOT / "results",
                   help="Thư mục results/ gốc.")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    if not 0.0 <= args.threshold <= 1.0:
        raise SystemExit("--threshold phải nằm trong [0, 1].")

    pairs = load_pairs(args.labels, args.labels.parent)
    hash_fn, source_desc = build_hash_fn(args.hash_source, args.wavelet, args.hash_size)
    print(f"Nguồn hash : {source_desc}")
    print(f"Số cặp ảnh : {len(pairs)}")

    rows = compute_pair_hashes(pairs, hash_fn)
    y, d, roc, m_def, m_opt, loo = evaluate(rows, args.threshold)

    pred_def = predict_by_threshold(d, m_def.threshold)
    pred_opt = predict_by_threshold(d, m_opt.threshold)
    for r, pd_, po in zip(rows, pred_def, pred_opt):
        r["pred_default"] = int(pd_)
        r["pred_optimal"] = int(po)
    wrong_def = [r for r in rows if r["pred_default"] != r["label"]]
    wrong_opt = [r for r in rows if r["pred_optimal"] != r["label"]]

    sweep = run_wavelet_sweep(pairs, args.hash_size) if args.sweep_wavelets else None

    tables = args.out_dir / "tables"
    figures = args.out_dir / "figures"

    _write_csv(
        tables / "pair_results.csv",
        ["pair_id", "label", "variation", "hash_length", "hamming_distance",
         "normalized_distance", "similarity", "pred_default", "pred_optimal",
         "correct_default", "correct_optimal"],
        [[r["pair_id"], "similar" if r["label"] else "dissimilar", r["variation"],
          r["hash_length"], r["hamming_distance"], f"{r['normalized_distance']:.4f}",
          f"{1 - r['normalized_distance']:.4f}",
          "similar" if r["pred_default"] else "dissimilar",
          "similar" if r["pred_optimal"] else "dissimilar",
          int(r["pred_default"] == r["label"]), int(r["pred_optimal"] == r["label"])]
         for r in rows],
    )
    _write_csv(
        tables / "evaluation_metrics.csv",
        ["threshold_type", "threshold", "TP", "TN", "FP", "FN", "accuracy",
         "sensitivity", "specificity", "precision", "f1", "auc", "loo_accuracy"],
        [[name, f"{m.threshold:.4f}", m.tp, m.tn, m.fp, m.fn, f"{m.accuracy:.4f}",
          f"{m.sensitivity:.4f}", f"{m.specificity:.4f}", f"{m.precision:.4f}",
          f"{m.f1:.4f}", f"{roc.auc:.4f}", f"{loo:.4f}"]
         for name, m in (("default", m_def), ("optimal_youden", m_opt))],
    )
    _write_csv(
        tables / "roc_points.csv",
        ["threshold", "fpr", "tpr"],
        [[f"{t:.4f}", f"{f:.4f}", f"{tp:.4f}"]
         for t, f, tp in zip(roc.thresholds, roc.fpr, roc.tpr)],
    )
    _write_csv(
        tables / "variation_breakdown.csv",
        ["variation", "n_pairs", "detected_at_optimal", "sensitivity"],
        variation_breakdown(rows, m_opt.threshold),
    )
    if sweep:
        _write_csv(
            tables / "wavelet_comparison.csv",
            ["wavelet", "auc", "threshold_youden", "accuracy", "sensitivity",
             "specificity", "loo_accuracy"],
            [[s["wavelet"], f"{s['auc']:.4f}", f"{s['threshold']:.4f}",
              f"{s['accuracy']:.4f}", f"{s['sensitivity']:.4f}",
              f"{s['specificity']:.4f}", f"{s['loo_accuracy']:.4f}"] for s in sweep],
        )

    plot_roc_curve(roc, str(figures / "roc_curve.png"))
    plot_distance_distribution(y, d, m_opt.threshold, str(figures / "distance_distribution.png"))
    plot_confusion_matrix(m_opt.tp, m_opt.tn, m_opt.fp, m_opt.fn,
                          str(figures / "confusion_matrix.png"),
                          title=f"Confusion matrix (ngưỡng {m_opt.threshold:.4f})")

    write_report(args.out_dir / "reports" / "evaluation_report.md", source_desc, rows,
                 roc, m_def, m_opt, loo, wrong_def, wrong_opt, sweep)

    # ---- In kết quả ra màn hình ----
    print("\n" + "=" * 64)
    print("KẾT QUẢ ĐÁNH GIÁ TRÊN TOÀN BỘ DATASET")
    print("=" * 64)
    for name, m in (("Ngưỡng mặc định", m_def), ("Ngưỡng tối ưu (Youden)", m_opt)):
        print(f"[{name}] threshold = {m.threshold:.4f}")
        print(f"  TP={m.tp} TN={m.tn} FP={m.fp} FN={m.fn}")
        print(f"  Accuracy={m.accuracy:.4f}  Sensitivity={m.sensitivity:.4f}  "
              f"Specificity={m.specificity:.4f}  Precision={m.precision:.4f}  F1={m.f1:.4f}")
    print(f"AUC = {roc.auc:.4f}   |   Accuracy leave-one-out = {loo:.4f}")
    if wrong_opt:
        print("Cặp sai tại ngưỡng tối ưu:", ", ".join(r["pair_id"] for r in wrong_opt))
    if sweep:
        print("\nSo sánh wavelet (AUC):", ", ".join(f"{s['wavelet']}={s['auc']:.3f}" for s in sweep))
    print(f"\nĐã lưu kết quả vào: {args.out_dir}")


if __name__ == "__main__":
    main()
