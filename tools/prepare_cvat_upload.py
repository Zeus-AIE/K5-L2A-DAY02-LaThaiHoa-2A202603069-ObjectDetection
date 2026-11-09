#!/usr/bin/env python3
"""Prepare CVAT-compatible ZIP packages for easy annotation import into CVAT."""

from __future__ import annotations

import io
import json
import zipfile
from pathlib import Path


CLASS_NAMES = ["car", "truck", "bus", "van"]


def make_yolo11_cvat_zip(images_dir: Path, labels_dir: Path, output_zip: Path):
    """Create standard CVAT YOLO 1.1 format zip."""
    img_files = sorted(images_dir.glob("*.jpg"))
    
    obj_names_content = "\n".join(CLASS_NAMES) + "\n"
    obj_data_content = f"classes = {len(CLASS_NAMES)}\ntrain = train.txt\nnames = obj.names\nbackup = backup/\n"
    train_txt_content = "\n".join(f"data/obj_train_data/{img.name}" for img in img_files) + "\n"

    with zipfile.ZipFile(output_zip, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("obj.names", obj_names_content)
        zf.writestr("obj.data", obj_data_content)
        zf.writestr("train.txt", train_txt_content)

        for img in img_files:
            label_file = labels_dir / f"{img.stem}.txt"
            content = label_file.read_text(encoding="utf-8") if label_file.exists() else ""
            zf.writestr(f"obj_train_data/{img.stem}.txt", content)

    print(f"[OK] Da tao goi CVAT YOLO 1.1: {output_zip} ({output_zip.stat().st_size / 1024:.1f} KB)")


def make_coco_cvat_zip(images_dir: Path, labels_dir: Path, output_zip: Path):
    """Create standard CVAT COCO 1.0 format zip (super reliable in CVAT)."""
    img_files = sorted(images_dir.glob("*.jpg"))
    
    categories = [{"id": i + 1, "name": name, "supercategory": "vehicle"} for i, name in enumerate(CLASS_NAMES)]
    images = []
    annotations = []
    ann_id = 1

    for img_id, img_path in enumerate(img_files, start=1):
        # Image dimensions 640x640
        images.append({
            "id": img_id,
            "file_name": img_path.name,
            "width": 640,
            "height": 640
        })

        label_file = labels_dir / f"{img_path.stem}.txt"
        if not label_file.exists():
            continue

        for line in label_file.read_text(encoding="utf-8").splitlines():
            parts = line.strip().split()
            if len(parts) != 5:
                continue
            cls_id, xc, yc, w, h = map(float, parts)
            cls_id = int(cls_id)
            if cls_id not in (0, 1, 2, 3):
                continue

            # convert normalized xywh to absolute pixel xywh for COCO
            abs_w = w * 640.0
            abs_h = h * 640.0
            abs_x = (xc - w / 2.0) * 640.0
            abs_y = (yc - h / 2.0) * 640.0

            annotations.append({
                "id": ann_id,
                "image_id": img_id,
                "category_id": cls_id + 1,  # COCO 1-indexed
                "bbox": [round(abs_x, 2), round(abs_y, 2), round(abs_w, 2), round(abs_h, 2)],
                "area": round(abs_w * abs_h, 2),
                "iscrowd": 0,
                "attributes": {"occluded": False}
            })
            ann_id += 1

    coco_doc = {
        "images": images,
        "annotations": annotations,
        "categories": categories
    }

    with zipfile.ZipFile(output_zip, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("annotations/instances_default.json", json.dumps(coco_doc, indent=2))

    print(f"[OK] Da tao goi CVAT COCO 1.0: {output_zip} ({output_zip.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    imgs = Path("dataset/images/train")
    lbls = Path("dataset/labels/train")
    make_yolo11_cvat_zip(imgs, lbls, Path("dataset/cvat_yolo11_import.zip"))
    make_coco_cvat_zip(imgs, lbls, Path("dataset/cvat_coco_import.zip"))
