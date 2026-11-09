#!/usr/bin/env python3
"""Generate a standalone HTML viewer to inspect all 50 annotated images locally."""

from __future__ import annotations

import base64
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


CLASS_NAMES = {0: "car", 1: "truck", 2: "bus", 3: "van"}
CLASS_COLORS = {0: "#00E676", 1: "#2979FF", 2: "#FFD600", 3: "#FF1744"}


def main():
    img_dir = Path("dataset/images/train")
    lbl_dir = Path("dataset/labels/train")
    output_html = Path("visualize_annotations.html")

    images_data = []
    for img_path in sorted(img_dir.glob("*.jpg")):
        lbl_path = lbl_dir / f"{img_path.stem}.txt"
        boxes = []
        if lbl_path.exists():
            for line in lbl_path.read_text(encoding="utf-8").splitlines():
                parts = line.strip().split()
                if len(parts) == 5:
                    cls_id, xc, yc, w, h = map(float, parts)
                    boxes.append({
                        "cls": int(cls_id),
                        "name": CLASS_NAMES.get(int(cls_id), "unknown"),
                        "color": CLASS_COLORS.get(int(cls_id), "#FFFFFF"),
                        "x": xc - w / 2,
                        "y": yc - h / 2,
                        "w": w,
                        "h": h
                    })
        
        # Load image as base64 thumbnail/jpeg
        b64 = base64.b64encode(img_path.read_bytes()).decode("utf-8")
        images_data.append({
            "name": img_path.name,
            "boxes": boxes,
            "data_url": f"data:image/jpeg;base64,{b64}"
        })

    html_content = f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<title>Trình Duyệt Bounding Box 50 Ảnh Train (ADAS)</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #121212; color: #E0E0E0; margin: 0; padding: 20px; text-align: center; }}
  .container {{ max-width: 900px; margin: 0 auto; background: #1E1E1E; padding: 20px; border-radius: 12px; box-shadow: 0 8px 24px rgba(0,0,0,0.5); }}
  h2 {{ color: #00E676; margin-top: 0; }}
  .canvas-wrapper {{ position: relative; width: 640px; height: 640px; margin: 15px auto; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 16px rgba(0,0,0,0.4); }}
  #bg-image {{ width: 640px; height: 640px; display: block; }}
  #overlay {{ position: absolute; top: 0; left: 0; width: 640px; height: 640px; pointer-events: none; }}
  .controls {{ margin: 20px 0; display: flex; justify-content: center; align-items: center; gap: 15px; }}
  button {{ background: #2979FF; color: white; border: none; padding: 10px 20px; border-radius: 6px; font-size: 15px; cursor: pointer; font-weight: bold; transition: 0.2s; }}
  button:hover {{ background: #1565C0; }}
  .legend {{ display: flex; justify-content: center; gap: 20px; margin-top: 15px; }}
  .legend-item {{ display: flex; align-items: center; gap: 8px; font-size: 14px; font-weight: 500; }}
  .legend-box {{ width: 14px; height: 14px; border-radius: 3px; display: inline-block; }}
  .stats {{ font-size: 16px; margin: 10px 0; color: #B0BEC5; }}
</style>
</head>
<body>
<div class="container">
  <h2>Trình Duyệt Nhãn Bounding Box 50 Ảnh Train (YOLO11x SOTA)</h2>
  <div class="stats" id="info-text">Đang tải...</div>
  <div class="canvas-wrapper">
    <img id="bg-image" src="" alt="Frame">
    <canvas id="overlay" width="640" height="640"></canvas>
  </div>
  <div class="controls">
    <button onclick="prevImage()">❮ Ảnh trước (D)</button>
    <span id="counter" style="font-size: 16px; font-weight: bold; min-width: 90px;">1 / 50</span>
    <button onclick="nextImage()">Ảnh tiếp theo (F) ❯</button>
  </div>
  <div class="legend">
    <div class="legend-item"><span class="legend-box" style="background:#00E676;"></span> car (0)</div>
    <div class="legend-item"><span class="legend-box" style="background:#2979FF;"></span> truck (1)</div>
    <div class="legend-item"><span class="legend-box" style="background:#FFD600;"></span> bus (2)</div>
    <div class="legend-item"><span class="legend-box" style="background:#FF1744;"></span> van (3)</div>
  </div>
</div>
<script>
  const data = {json.dumps(images_data)};
  let currentIndex = 0;
  const imgEl = document.getElementById('bg-image');
  const canvas = document.getElementById('overlay');
  const ctx = canvas.getContext('2d');
  const infoText = document.getElementById('info-text');
  const counter = document.getElementById('counter');

  function renderImage(idx) {{
    const item = data[idx];
    imgEl.src = item.data_url;
    counter.textContent = (idx + 1) + " / " + data.length;
    infoText.innerHTML = "Ảnh: <b>" + item.name + "</b> — Tổng số vật thể: <b>" + item.boxes.length + "</b> boxes";

    imgEl.onload = () => {{
      ctx.clearRect(0, 0, 640, 640);
      item.boxes.forEach(b => {{
        const x = b.x * 640;
        const y = b.y * 640;
        const w = b.w * 640;
        const h = b.h * 640;

        ctx.strokeStyle = b.color;
        ctx.lineWidth = 2;
        ctx.strokeRect(x, y, w, h);

        ctx.fillStyle = b.color;
        ctx.font = "bold 11px sans-serif";
        const text = b.name;
        const tw = ctx.measureText(text).width;
        ctx.fillRect(x, Math.max(0, y - 16), tw + 6, 16);
        ctx.fillStyle = "#000000";
        ctx.fillText(text, x + 3, Math.max(12, y - 4));
      }});
    }};
  }}

  function nextImage() {{
    if (currentIndex < data.length - 1) {{
      currentIndex++;
      renderImage(currentIndex);
    }}
  }}

  function prevImage() {{
    if (currentIndex > 0) {{
      currentIndex--;
      renderImage(currentIndex);
    }}
  }}

  window.addEventListener('keydown', (e) => {{
    if (e.key === 'f' || e.key === 'F' || e.key === 'ArrowRight') nextImage();
    if (e.key === 'd' || e.key === 'D' || e.key === 'ArrowLeft') prevImage();
  }});

  renderImage(0);
</script>
</body>
</html>
"""
    output_html.write_text(html_content, encoding="utf-8")
    print(f"[OK] Da tao trinh xem truc quan offline: {output_html.resolve()}")


if __name__ == "__main__":
    main()
