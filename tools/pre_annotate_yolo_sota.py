#!/usr/bin/env python3
"""SOTA Pre-annotation pipeline using YOLO11-Extra Large (yolo11x) + Multi-scale TTA + ADAS 4-Class Classification."""

from __future__ import annotations

import argparse
from pathlib import Path
import torch
from ultralytics import YOLO


def classify_vehicle(coco_cls: int, w: float, h: float, conf: float) -> int:
    """Classify vehicle into ADAS 4-class schema:
    0: car (sedan, hatchback, SUV, pickup)
    1: truck (cargo truck, flatbed, heavy truck)
    2: bus (public bus, coach, long passenger vehicle)
    3: van (minivan, cargo van, boxy monovolume vehicle)
    """
    aspect_ratio = w / max(h, 1e-4)

    if coco_cls == 5:
        # Bus
        return 2

    if coco_cls == 7:
        # Truck: if compact boxy without separate cargo bed, could be large van
        if aspect_ratio < 0.95 and (w * h) < 0.035:
            return 3  # tall compact boxy van
        return 1

    if coco_cls == 2:
        # Car: distinguish tall boxy vans/minivans from standard cars
        # In CCTV intersection cameras, vans have taller profile (aspect ratio 0.85 - 1.15)
        # and medium-large area
        area = w * h
        if 0.80 <= aspect_ratio <= 1.18 and area > 0.012:
            return 3  # van / minivan
        return 0  # standard car

    return 0


def main():
    parser = argparse.ArgumentParser(description="Gán nhãn độ chính xác cao nhất (SOTA) bằng YOLO11x.")
    parser.add_argument("--images", type=Path, default=Path("dataset/images/train"))
    parser.add_argument("--labels", type=Path, default=Path("dataset/labels/train"))
    parser.add_argument("--model", type=str, default="yolo11x.pt")
    parser.add_argument("--imgsz", type=int, default=1280)
    parser.add_argument("--conf", type=float, default=0.25)
    parser.add_argument("--iou", type=float, default=0.45)
    args = parser.parse_args()

    args.labels.mkdir(parents=True, exist_ok=True)
    device = 0 if torch.cuda.is_available() else "cpu"
    print(f"Thiet bi: {device} ({torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'})")

    print(f"Dang nap mo hinh SOTA: {args.model}...")
    model = YOLO(str(args.model))

    image_paths = sorted(args.images.glob("*.jpg"))
    print(f"Chay suy luan da ty le (Multi-scale {args.imgsz}) + TTA tren {len(image_paths)} anh...")

    total_boxes = 0
    counts = {0: 0, 1: 0, 2: 0, 3: 0}

    for img_path in image_paths:
        results = model.predict(
            str(img_path),
            imgsz=args.imgsz,
            conf=args.conf,
            iou=args.iou,
            augment=True,
            device=device,
            classes=[2, 5, 7],  # car, bus, truck
            verbose=False,
        )[0]

        lines = []
        for box in results.boxes:
            coco_cls = int(box.cls[0])
            conf_val = float(box.conf[0])
            xc, yc, w, h = box.xywhn[0].tolist()

            adas_cls = classify_vehicle(coco_cls, w, h, conf_val)

            # Bounding box clamping to [0, 1] strictly
            x1 = max(0.0, xc - w / 2)
            y1 = max(0.0, yc - h / 2)
            x2 = min(1.0, xc + w / 2)
            y2 = min(1.0, yc + h / 2)
            w_clamped = max(1e-4, x2 - x1)
            h_clamped = max(1e-4, y2 - y1)
            xc_clamped = (x1 + x2) / 2
            yc_clamped = (y1 + y2) / 2

            lines.append(f"{adas_cls} {xc_clamped:.6f} {yc_clamped:.6f} {w_clamped:.6f} {h_clamped:.6f}")
            counts[adas_cls] += 1

        label_path = args.labels / f"{img_path.stem}.txt"
        label_path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
        total_boxes += len(lines)

    print(f"\n[HOAN THANH PRE-ANNOTATION SOTA]")
    print(f"- So anh da gan nhan: {len(image_paths)}")
    print(f"- Tong so bounding box: {total_boxes} (trung binh {total_boxes / len(image_paths):.1f} box/anh)")
    print(f"- Thong ke cac lop: car(0)={counts[0]}, truck(1)={counts[1]}, bus(2)={counts[2]}, van(3)={counts[3]}")


if __name__ == "__main__":
    main()
