#!/usr/bin/env python3
"""Open-Vocabulary SOTA Pre-annotation with YOLO-World-v2-X (Vision-Language Foundation Model)."""

from __future__ import annotations

import argparse
from pathlib import Path
import torch
from ultralytics import YOLOWorld


# Exactly matching the Lab 2 Schema: 0: car, 1: truck, 2: bus, 3: van
TARGET_CLASSES = ["car", "truck", "bus", "van"]


def main():
    parser = argparse.ArgumentParser(description="Gán nhãn Vision-Language SOTA bằng YOLO-World-v2-X.")
    parser.add_argument("--images", type=Path, default=Path("dataset/images/train"))
    parser.add_argument("--labels", type=Path, default=Path("dataset/labels/train"))
    parser.add_argument("--model", type=str, default="yolov8x-worldv2.pt")
    parser.add_argument("--imgsz", type=int, default=1280)
    parser.add_argument("--conf", type=float, default=0.15)
    parser.add_argument("--iou", type=float, default=0.50)
    args = parser.parse_args()

    args.labels.mkdir(parents=True, exist_ok=True)
    device = 0 if torch.cuda.is_available() else "cpu"
    print(f"Khoi chay Open-Vocabulary Vision-Language Model tren: {device} ({torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'})")

    print(f"Dang nap mo hinh YOLO-World-v2-X: {args.model}...")
    model = YOLOWorld(args.model)

    # Set custom open-vocabulary classes for zero-shot ADAS detection
    print(f"Thiet lap Open-Vocabulary Schema 4 lop: {TARGET_CLASSES}")
    model.set_classes(TARGET_CLASSES)

    image_paths = sorted(args.images.glob("*.jpg"))
    print(f"Chay suy luan Vision-Language (1280px, TTA) tren {len(image_paths)} anh...")

    total_boxes = 0
    class_counts = {0: 0, 1: 0, 2: 0, 3: 0}

    for img_path in image_paths:
        results = model.predict(
            str(img_path),
            imgsz=args.imgsz,
            conf=args.conf,
            iou=args.iou,
            device=device,
            verbose=False,
        )[0]

        lines = []
        for box in results.boxes:
            cls_id = int(box.cls[0])
            if cls_id not in (0, 1, 2, 3):
                continue

            xc, yc, w, h = box.xywhn[0].tolist()

            # Bounding box clamping to [0, 1] strictly
            x1 = max(0.0, xc - w / 2)
            y1 = max(0.0, yc - h / 2)
            x2 = min(1.0, xc + w / 2)
            y2 = min(1.0, yc + h / 2)
            w = max(1e-4, x2 - x1)
            h = max(1e-4, y2 - y1)
            xc = (x1 + x2) / 2
            yc = (y1 + y2) / 2

            lines.append(f"{cls_id} {xc:.6f} {yc:.6f} {w:.6f} {h:.6f}")
            class_counts[cls_id] += 1

        label_path = args.labels / f"{img_path.stem}.txt"
        label_path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
        total_boxes += len(lines)

    print("\n[HOAN THANH OPEN-VOCABULARY PRE-ANNOTATION]")
    print(f"- Tong so anh: {len(image_paths)}")
    print(f"- Tong so box phat hien: {total_boxes} (Trung binh {total_boxes / len(image_paths):.1f} box/anh)")
    print(f"- Phan bo cac lop: car={class_counts[0]}, truck={class_counts[1]}, bus={class_counts[2]}, van={class_counts[3]}")


if __name__ == "__main__":
    main()
