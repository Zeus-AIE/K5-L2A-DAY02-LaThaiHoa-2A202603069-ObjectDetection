#!/usr/bin/env python3
"""Generate a standalone HTML viewer comparing Student annotations vs Gold Ground Truth."""

import base64
import json
from pathlib import Path


CLASS_NAMES = {0: "car", 1: "truck", 2: "bus", 3: "van"}
CLASS_COLORS = {0: "#00E676", 1: "#2979FF", 2: "#FFD600", 3: "#FF1744"}


def parse_yolo_file(file_path: Path):
    boxes = []
    if not file_path.exists():
        return boxes
    for line in file_path.read_text(encoding="utf-8").splitlines():
        parts = line.strip().split()
        if len(parts) == 5:
            cls_id, xc, yc, w, h = map(float, parts)
            cls_id = int(cls_id)
            boxes.append({
                "cls": cls_id,
                "name": CLASS_NAMES.get(cls_id, "unknown"),
                "color": CLASS_COLORS.get(cls_id, "#FFFFFF"),
                "x": xc - w / 2,
                "y": yc - h / 2,
                "w": w,
                "h": h
            })
    return boxes


def main():
    root = Path(__file__).resolve().parent.parent
    img_dir = root / "dataset/images/train"
    student_dir = root / "dataset/labels/train"
    gold_dir = Path(r"d:\App\gold_train_labels")

    images_data = []
    for img_path in sorted(img_dir.glob("*.jpg")):
        student_boxes = parse_yolo_file(student_dir / f"{img_path.stem}.txt")
        gold_boxes = parse_yolo_file(gold_dir / f"{img_path.stem}.txt")
        b64 = base64.b64encode(img_path.read_bytes()).decode("utf-8")

        images_data.append({
            "name": img_path.name,
            "student_boxes": student_boxes,
            "gold_boxes": gold_boxes,
            "data_url": f"data:image/jpeg;base64,{b64}"
        })

    html_content = f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<title>Đối Chiếu Nhãn 50 Ảnh: Bạn vs Gold Ground Truth</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0F172A; color: #F1F5F9; margin: 0; padding: 20px; text-align: center; }}
  .container {{ max-width: 950px; margin: 0 auto; background: #1E293B; padding: 24px; border-radius: 14px; box-shadow: 0 10px 30px rgba(0,0,0,0.6); }}
  h2 {{ color: #38BDF8; margin-top: 0; margin-bottom: 8px; }}
  .subtitle {{ color: #94A3B8; font-size: 14px; margin-bottom: 16px; }}
  .canvas-wrapper {{ position: relative; width: 640px; height: 640px; margin: 15px auto; border-radius: 8px; overflow: hidden; box-shadow: 0 6px 20px rgba(0,0,0,0.5); border: 1px solid #334155; }}
  #bg-image {{ width: 640px; height: 640px; display: block; }}
  #overlay {{ position: absolute; top: 0; left: 0; width: 640px; height: 640px; pointer-events: none; }}
  .mode-switch {{ display: flex; justify-content: center; gap: 10px; margin: 15px 0; }}
  .mode-btn {{ background: #334155; color: #E2E8F0; border: 2px solid transparent; padding: 10px 18px; border-radius: 8px; font-size: 15px; cursor: pointer; font-weight: 600; transition: all 0.2s; }}
  .mode-btn:hover {{ background: #475569; }}
  .mode-btn.active {{ background: #0284C7; color: #FFFFFF; border-color: #38BDF8; box-shadow: 0 0 12px rgba(56, 189, 248, 0.4); }}
  .controls {{ margin: 20px 0; display: flex; justify-content: center; align-items: center; gap: 15px; }}
  .nav-btn {{ background: #2563EB; color: white; border: none; padding: 10px 22px; border-radius: 8px; font-size: 15px; cursor: pointer; font-weight: bold; transition: 0.2s; }}
  .nav-btn:hover {{ background: #1D4ED8; }}
  .legend {{ display: flex; justify-content: center; gap: 20px; margin-top: 15px; flex-wrap: wrap; }}
  .legend-item {{ display: flex; align-items: center; gap: 8px; font-size: 14px; font-weight: 500; }}
  .legend-box {{ width: 14px; height: 14px; border-radius: 3px; display: inline-block; }}
  .stats-box {{ display: flex; justify-content: center; gap: 25px; margin: 12px 0; font-size: 15px; color: #CBD5E1; background: #0F172A; padding: 10px; border-radius: 8px; border: 1px solid #334155; }}
  .tag {{ font-weight: bold; }}
  .tag-gold {{ color: #F59E0B; }}
  .tag-student {{ color: #10B981; }}
</style>
</head>
<body>
<div class="container">
  <h2>Đối Chiếu Nhãn 50 Ảnh: Bạn vs Gold Ground Truth</h2>
  <div class="subtitle">Phím tắt: [1] Xem Gold | [2] Xem Nhãn Bạn | [3] Chế độ So Sánh | [A] / [D] hoặc [←] / [→] để chuyển ảnh</div>

  <div class="mode-switch">
    <button class="mode-btn active" id="btn-gold" onclick="setMode('gold')">⭐ 1. Nhãn Chuẩn (Gold GT)</button>
    <button class="mode-btn" id="btn-student" onclick="setMode('student')">✏️ 2. Nhãn của Bạn (CVAT)</button>
    <button class="mode-btn" id="btn-compare" onclick="setMode('compare')">🔍 3. Chế Độ So Sánh Cả Hai</button>
  </div>

  <div class="stats-box" id="stats-bar">
    <div>Ảnh: <span id="img-name" style="font-weight: bold; color: #38BDF8;">drive_001.jpg</span></div>
    <div>Gold boxes: <span id="gold-count" class="tag tag-gold">0</span></div>
    <div>Nhãn bạn: <span id="student-count" class="tag tag-student">0</span></div>
    <div>Trạng thái hiển thị: <span id="mode-label" style="font-weight: bold; color: #F59E0B;">Chỉ Gold Ground Truth</span></div>
  </div>

  <div class="canvas-wrapper">
    <img id="bg-image" src="" alt="Frame">
    <canvas id="overlay" width="640" height="640"></canvas>
  </div>

  <div class="controls">
    <button class="nav-btn" onclick="prevImage()">❮ Ảnh trước (A / ←)</button>
    <span id="counter" style="font-size: 17px; font-weight: bold; min-width: 100px;">1 / 50</span>
    <button class="nav-btn" onclick="nextImage()">Ảnh tiếp theo (D / →) ❯</button>
  </div>

  <div class="legend">
    <div class="legend-item"><span class="legend-box" style="background:#00E676;"></span> car (0)</div>
    <div class="legend-item"><span class="legend-box" style="background:#2979FF;"></span> truck (1)</div>
    <div class="legend-item"><span class="legend-box" style="background:#FFD600;"></span> bus (2)</div>
    <div class="legend-item"><span class="legend-box" style="background:#FF1744;"></span> van (3)</div>
  </div>
  <div class="legend" style="margin-top: 8px; font-size: 13px; color: #94A3B8;">
    * Trong chế độ so sánh: <b style="color:#F59E0B">Nét liền dày = Gold GT</b>, <b style="color:#38BDF8">Nét đứt mỏng = Nhãn của bạn</b>
  </div>
</div>

<script>
  const data = {json.dumps(images_data)};
  let currentIndex = 0;
  let currentMode = 'gold'; // 'gold', 'student', 'compare'

  const imgEl = document.getElementById('bg-image');
  const canvas = document.getElementById('overlay');
  const ctx = canvas.getContext('2d');
  const imgNameEl = document.getElementById('img-name');
  const goldCountEl = document.getElementById('gold-count');
  const studentCountEl = document.getElementById('student-count');
  const modeLabelEl = document.getElementById('mode-label');
  const counterEl = document.getElementById('counter');

  function setMode(mode) {{
    currentMode = mode;
    document.getElementById('btn-gold').classList.toggle('active', mode === 'gold');
    document.getElementById('btn-student').classList.toggle('active', mode === 'student');
    document.getElementById('btn-compare').classList.toggle('active', mode === 'compare');
    
    if (mode === 'gold') modeLabelEl.textContent = 'Chỉ Gold Ground Truth (Chuẩn)';
    else if (mode === 'student') modeLabelEl.textContent = 'Chỉ Nhãn Bạn Gán (CVAT)';
    else modeLabelEl.textContent = 'So Sánh (Gold nét liền vs Bạn nét đứt)';
    
    renderOverlay();
  }}

  function drawBoxes(boxes, isGold, isDashed = false) {{
    const W = canvas.width;
    const H = canvas.height;
    ctx.font = 'bold 12px sans-serif';

    boxes.forEach(b => {{
      const x = b.x * W;
      const y = b.y * H;
      const w = b.w * W;
      const h = b.h * H;

      ctx.save();
      if (isDashed) {{
        ctx.setLineDash([4, 4]);
        ctx.strokeStyle = '#38BDF8';
        ctx.lineWidth = 2;
      }} else {{
        ctx.setLineDash([]);
        ctx.strokeStyle = isGold ? (currentMode === 'compare' ? '#F59E0B' : b.color) : b.color;
        ctx.lineWidth = (currentMode === 'compare' && isGold) ? 3 : 2;
      }}

      ctx.strokeRect(x, y, w, h);

      // Label background
      const tag = (currentMode === 'compare' ? (isGold ? '[Gold] ' : '[Bạn] ') : '') + b.name;
      const tw = ctx.measureText(tag).width + 8;
      ctx.fillStyle = isDashed ? 'rgba(56, 189, 248, 0.85)' : (isGold && currentMode === 'compare' ? 'rgba(245, 158, 11, 0.85)' : b.color);
      const ly = Math.max(16, y - 4);
      ctx.fillRect(x, ly - 14, tw, 16);
      
      ctx.fillStyle = '#000000';
      ctx.fillText(tag, x + 4, ly - 2);
      ctx.restore();
    }});
  }}

  function renderOverlay() {{
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    const item = data[currentIndex];
    
    if (currentMode === 'gold') {{
      drawBoxes(item.gold_boxes, true, false);
    }} else if (currentMode === 'student') {{
      drawBoxes(item.student_boxes, false, false);
    }} else if (currentMode === 'compare') {{
      // Draw student first with dashed line, then gold with solid line
      drawBoxes(item.student_boxes, false, true);
      drawBoxes(item.gold_boxes, true, false);
    }}
  }}

  function renderImage(idx) {{
    const item = data[idx];
    imgEl.src = item.data_url;
    imgNameEl.textContent = item.name;
    goldCountEl.textContent = item.gold_boxes.length;
    studentCountEl.textContent = item.student_boxes.length;
    counterEl.textContent = `${{idx + 1}} / ${{data.length}}`;
    renderOverlay();
  }}

  function prevImage() {{
    currentIndex = (currentIndex - 1 + data.length) % data.length;
    renderImage(currentIndex);
  }}

  function nextImage() {{
    currentIndex = (currentIndex + 1) % data.length;
    renderImage(currentIndex);
  }}

  window.addEventListener('keydown', (e) => {{
    if (e.key === 'ArrowLeft' || e.key.toLowerCase() === 'a') prevImage();
    if (e.key === 'ArrowRight' || e.key.toLowerCase() === 'd') nextImage();
    if (e.key === '1') setMode('gold');
    if (e.key === '2') setMode('student');
    if (e.key === '3') setMode('compare');
  }});

  // Initial render
  renderImage(0);
</script>
</body>
</html>"""

    out_file1 = root / "visualize_comparison.html"
    out_file2 = Path(r"D:\App\visualize_comparison.html")

    out_file1.write_text(html_content, encoding="utf-8")
    out_file2.write_text(html_content, encoding="utf-8")
    print(f"[OK] Da tao cong cu truc quan hoa: {out_file1}")
    print(f"[OK] Da tao cong cu truc quan hoa tai: {out_file2}")


if __name__ == "__main__":
    main()
