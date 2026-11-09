#!/usr/bin/env python3
"""Pre-annotate 50 train images using YOLO26 / YOLO11 for initial labels."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path
from ultralytics import YOLO


# COCO class mapping to ADAS 4-class schema:
# COCO: 2 (car) -> 0 (car), 7 (truck) -> 1 (truck), 5 (bus) -> 2 (bus)
COCO_TO_ADAS = {
    2: 0,  # car -> car
    7: 1,  # truck -> truck
    5: 2,  # bus -> bus
}


def main():
    parser = argparse.ArgumentParser(description="Tự động pre-annotate 50 ảnh train bằng YOLO.")
    parser.add_argument("--images", type=Path, default=Path("dataset/images/train"))
    parser.add_argument("--labels", type=Path, default=Path("dataset/labels/train"))
    parser.add_argument("--model", type=str, default="yolo26n.pt")
    parser.add_argument("--conf", type=float, default=0.25)
    parser.add_argument("--iou", type=float, default=0.45)
    args = parser.parse_args()

    args.labels.mkdir(parents=True, exist_ok=True)

    # Ensure model file exists; if yolo26n.pt not found, fall back to yolo11n.pt
    model_path = Path(args.model)
    if not model_path.exists():
        if Path("yolo11n.pt").exists():
            shutil.copy("yolo11n.pt", str(model_path))
            print(f"Đã sao chép yolo11n.pt -> {model_path}")
        else:
            print(f"Tải checkpoint {args.model}...")

    model = YOLO(str(model_path))
    image_paths = sorted(args.images.glob("*.jpg"))
    print(f"Bắt đầu pre-annotate {len(image_paths)} ảnh từ {args.images}...")

    total_boxes = 0
    for img_path in image_paths:
        results = model.predict(
            str(img_path),
            conf=args.conf,
            iou=args.iou,
            classes=list(COCO_TO_ADAS.keys()),
            verbose=False,
        )[0]

        lines = []
        for box in results.boxes:
            coco_cls = int(box.cls[0])
            if coco_cls not in COCO_TO_ADAS:
                continue
            adas_cls = COCO_TO_ADAS[coco_cls]

            xc, yc, w, h = box.xywhn[0].tolist()

            # Ensure box strictly stays within [0, 1] for check_yolo_labels.py
            x1 = max(0.0, xc - w / 2)
            y1 = max(0.0, yc - h / 2)
            x2 = min(1.0, xc + w / 2)
            y2 = min(1.0, yc + h / 2)
            w = max(1e-4, x2 - x1)
            h = max(1e-4, y2 - y1)
            xc = (x1 + x2) / 2
            yc = (y1 + y2) / 2

            lines.append(f"{adas_cls} {xc:.6f} {yc:.6f} {w:.6f} {h:.6f}")

        label_path = args.labels / f"{img_path.stem}.txt"
        label_path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
        total_boxes += len(lines)

    print(f"Hoàn thành! Đã tạo {len(image_paths)} file nhãn trong {args.labels}")
    print(f"Tổng số bounding box phát hiện: {total_boxes} (trung bình {total_boxes / len(image_paths):.1f} box/ảnh)")


if __name__ == "__main__":
    main()
