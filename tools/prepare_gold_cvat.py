#!/usr/bin/env python3
"""Prepare CVAT packages (YOLO 1.1 and COCO 1.0) for Gold Train Labels."""

import json
from pathlib import Path
import zipfile


CLASS_NAMES = ["car", "truck", "bus", "van"]


def make_gold_packages():
    root = Path(__file__).resolve().parent.parent
    gold_dir = Path(r"d:\App\gold_train_labels")
    images_dir = root / "dataset/images/train"
    out_dir = Path(r"D:\App")

    img_files = sorted(images_dir.glob("*.jpg"))
    print(f"Loading {len(img_files)} images and {len(list(gold_dir.glob('*.txt')))} gold labels...")

    # 1. Package CVAT YOLO 1.1 format
    yolo_zip = out_dir / "cvat_gold_yolo11.zip"
    obj_names_content = "\n".join(CLASS_NAMES) + "\n"
    obj_data_content = f"classes = {len(CLASS_NAMES)}\ntrain = train.txt\nnames = obj.names\nbackup = backup/\n"

    # In CVAT, depending on how task was created, paths might be data/obj_train_data/... or data/obj_Train_data/train - Copy/...
    # We include both paths in train.txt and files in both folders for maximum compatibility!
    train_txt_lines = []
    for img in img_files:
        train_txt_lines.append(f"data/obj_train_data/{img.name}")
        train_txt_lines.append(f"data/obj_Train_data/train - Copy/{img.name}")
    train_txt_content = "\n".join(train_txt_lines) + "\n"

    with zipfile.ZipFile(yolo_zip, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("obj.names", obj_names_content)
        zf.writestr("obj.data", obj_data_content)
        zf.writestr("train.txt", train_txt_content)
        zf.writestr("Train.txt", train_txt_content)

        for img in img_files:
            lbl_file = gold_dir / f"{img.stem}.txt"
            content = lbl_file.read_text(encoding="utf-8") if lbl_file.exists() else ""
            zf.writestr(f"obj_train_data/{img.stem}.txt", content)
            zf.writestr(f"obj_Train_data/{img.stem}.txt", content)
            zf.writestr(f"obj_Train_data/train - Copy/{img.stem}.txt", content)

    print(f"[OK] Da tao CVAT YOLO 1.1 zip: {yolo_zip} ({yolo_zip.stat().st_size / 1024:.1f} KB)")

    # 2. Package CVAT COCO 1.0 format (super recommended for CVAT because no path issues)
    coco_zip = out_dir / "cvat_gold_coco.zip"
    categories = [{"id": i + 1, "name": name, "supercategory": "vehicle"} for i, name in enumerate(CLASS_NAMES)]
    images = []
    annotations = []
    ann_id = 1

    for img_id, img_path in enumerate(img_files, start=1):
        images.append({
            "id": img_id,
            "file_name": img_path.name,
            "width": 640,
            "height": 640
        })

        lbl_file = gold_dir / f"{img_path.stem}.txt"
        if not lbl_file.exists():
            continue

        for line in lbl_file.read_text(encoding="utf-8").splitlines():
            parts = line.strip().split()
            if len(parts) != 5:
                continue
            cls_id, xc, yc, w, h = map(float, parts)
            cls_id = int(cls_id)
            if cls_id not in (0, 1, 2, 3):
                continue

            abs_w = w * 640.0
            abs_h = h * 640.0
            abs_x = (xc - w / 2.0) * 640.0
            abs_y = (yc - h / 2.0) * 640.0

            annotations.append({
                "id": ann_id,
                "image_id": img_id,
                "category_id": cls_id + 1,
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

    with zipfile.ZipFile(coco_zip, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("annotations/instances_default.json", json.dumps(coco_doc, indent=2))

    print(f"[OK] Da tao CVAT COCO 1.0 zip: {coco_zip} ({coco_zip.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    make_gold_packages()
