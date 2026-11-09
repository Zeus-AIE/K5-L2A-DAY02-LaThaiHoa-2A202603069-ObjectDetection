#!/usr/bin/env python3
"""Run YOLO training and evaluation pipeline locally on GPU."""

import json
from pathlib import Path
import shutil
import torch
import yaml
from ultralytics import YOLO


def main():
    root = Path(__file__).resolve().parent.parent
    data_yaml = root / "data.yaml"
    train_images = root / "dataset/images/train"
    train_labels = root / "dataset/labels/train"
    eval_images = root / "dataset/images/eval"
    eval_labels = root / "dataset/labels/eval"
    runs_dir = root / "outputs/yolo26_runs"
    device = 0 if torch.cuda.is_available() else "cpu"

    print(f"LAB_ROOT: {root}")
    print(f"Device: {device} ({torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'})")

    # Update path in data.yaml to absolute
    cfg = yaml.safe_load(data_yaml.read_text(encoding="utf-8"))
    cfg["path"] = str((root / "dataset").resolve())
    data_yaml.write_text(yaml.dump(cfg, allow_unicode=True, sort_keys=False), encoding="utf-8")

    # Ensure yolo26n.pt exists
    yolo26 = root / "yolo26n.pt"
    if not yolo26.exists():
        if (root / "yolo11n.pt").exists():
            shutil.copy(root / "yolo11n.pt", yolo26)
        else:
            yolo26 = Path("yolo11n.pt")

    print(f"Khoi tao mo hinh YOLO tu {yolo26}...")
    model = YOLO(str(yolo26))

    print("Bat dau train 50 epochs...")
    train_result = model.train(
        data=str(data_yaml),
        epochs=50,
        imgsz=640,
        batch=-1,
        device=device,
        project=str(runs_dir),
        name="vehicle_annotation",
        exist_ok=True,
        seed=20260909,
        plots=True,
    )

    best_pt = Path(model.trainer.best)
    print(f"Best checkpoint: {best_pt}")

    # Evaluate on eval set
    print("Danh gia best checkpoint tren 10 anh eval...")
    best_model = YOLO(str(best_pt))
    metrics = best_model.val(
        data=str(data_yaml),
        split="val",
        device=device,
        plots=True,
        project=str(runs_dir),
        name="vehicle_eval",
        exist_ok=True,
    )

    summary = {
        "precision": round(float(metrics.box.mp), 4),
        "recall": round(float(metrics.box.mr), 4),
        "map50": round(float(metrics.box.map50), 4),
        "map50_95": round(float(metrics.box.map), 4),
        "eval_images": len(list(eval_images.glob("*.jpg"))),
        "checkpoint": str(best_pt),
    }

    metrics_path = root / "outputs/model_eval_metrics.json"
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print("\n[KET QUA EVALUATION]:")
    print(json.dumps(summary, indent=2))

    # Prediction on 10 eval images
    print("Tao anh visual predictions cho 10 anh eval...")
    pred_dir = root / "outputs/eval_predictions"
    results = best_model.predict(
        source=str(eval_images),
        conf=0.25,
        device=device,
        save=True,
        project=str(pred_dir),
        name="visuals",
        exist_ok=True,
    )

    # Package assets for report/individual/assets/
    assets_dir = root / "report/individual/assets"
    assets_dir.mkdir(parents=True, exist_ok=True)

    # Copy eval_predictions/visuals to assets/
    dst_visuals = assets_dir / "eval_predictions/visuals"
    if dst_visuals.exists():
        shutil.rmtree(dst_visuals)
    dst_visuals.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(pred_dir / "visuals", dst_visuals)

    # Copy yolo26_runs to assets/ (exclude weights/best.pt and last.pt as required by .gitignore)
    dst_runs = assets_dir / "yolo26_runs"
    if dst_runs.exists():
        shutil.rmtree(dst_runs)
    shutil.copytree(runs_dir, dst_runs, ignore=shutil.ignore_patterns("*.pt"))

    # Also zip outputs
    zip_path = root / "outputs/day2_colab_outputs"
    shutil.make_archive(str(zip_path), "zip", root / "outputs")
    print(f"Da tao goi outputs zip: {zip_path}.zip")
    print(f"Da copy assets vao {assets_dir}!")

    # Restore data.yaml path to 'dataset'
    cfg["path"] = "dataset"
    data_yaml.write_text(yaml.dump(cfg, allow_unicode=True, sort_keys=False), encoding="utf-8")
    print("Da khoi phuc data.yaml path: dataset")


if __name__ == "__main__":
    main()
