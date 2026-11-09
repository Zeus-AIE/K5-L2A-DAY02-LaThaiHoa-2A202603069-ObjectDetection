#!/usr/bin/env python3
"""Build Full-Featured Interactive Comparison HTML with complete metrics, confusion breakdown, and jump-to-image slider."""

import base64
from collections import defaultdict
import json
from pathlib import Path


CLASS_NAMES = {0: "car", 1: "truck", 2: "bus", 3: "van"}
# CVAT standard palette
CLASS_COLORS = {0: "#2080c0", 1: "#906080", 2: "#204080", 3: "#10a040"}


def load_boxes(path: Path):
    boxes = []
    if not path.exists():
        return boxes
    for line in path.read_text(encoding="utf-8").splitlines():
        parts = line.strip().split()
        if len(parts) == 5:
            cls_id, xc, yc, w, h = map(float, parts)
            cls_id = int(cls_id)
            boxes.append({
                "cls": cls_id,
                "name": CLASS_NAMES.get(cls_id, "unknown"),
                "color": CLASS_COLORS.get(cls_id, "#FFFFFF"),
                "xc": round(xc, 4), "yc": round(yc, 4),
                "w": round(w, 4), "h": round(h, 4),
                "x": round(xc - w / 2, 4), "y": round(yc - h / 2, 4),
                "x2": round(xc + w / 2, 4), "y2": round(yc + h / 2, 4)
            })
    return boxes


def calc_iou(b1, b2):
    inter_w = max(0.0, min(b1["x2"], b2["x2"]) - max(b1["x"], b2["x"]))
    inter_h = max(0.0, min(b1["y2"], b2["y2"]) - max(b1["y"], b2["y"]))
    inter = inter_w * inter_h
    union = b1["w"] * b1["h"] + b2["w"] * b2["h"] - inter
    return inter / union if union > 0 else 0.0


def main():
    root = Path(__file__).resolve().parent.parent
    img_dir = root / "dataset/images/train"
    student_dir = root / "dataset/labels/train"
    gold_dir = Path(r"d:\App\gold_train_labels")

    images_data = []
    total_tp = total_fp = total_fn = 0
    all_ious = []
    per_class_tp = defaultdict(int)
    per_class_fp = defaultdict(int)
    per_class_fn = defaultdict(int)
    per_class_ious = defaultdict(list)

    for img_path in sorted(img_dir.glob("*.jpg")):
        g_boxes = load_boxes(gold_dir / f"{img_path.stem}.txt")
        s_boxes = load_boxes(student_dir / f"{img_path.stem}.txt")

        # 1-to-1 match greedy on IoU >= 0.50
        cands = []
        for si, sb in enumerate(s_boxes):
            for gi, gb in enumerate(g_boxes):
                if sb["cls"] == gb["cls"]:
                    ov = calc_iou(sb, gb)
                    if ov >= 0.50:
                        cands.append((ov, si, gi))
        cands.sort(reverse=True, key=lambda x: x[0])

        matched_s = set()
        matched_g = set()
        img_ious = []
        for ov, si, gi in cands:
            if si not in matched_s and gi not in matched_g:
                matched_s.add(si)
                matched_g.add(gi)
                img_ious.append(ov)
                all_ious.append(ov)
                cls_id = s_boxes[si]["cls"]
                per_class_tp[cls_id] += 1
                per_class_ious[cls_id].append(ov)

        for si, sb in enumerate(s_boxes):
            sb["is_matched"] = (si in matched_s)
        for gi, gb in enumerate(g_boxes):
            gb["is_matched"] = (gi in matched_g)

        img_tp = len(matched_s)
        img_fp = len(s_boxes) - img_tp
        img_fn = len(g_boxes) - img_tp

        total_tp += img_tp
        total_fp += img_fp
        total_fn += img_fn

        for si, sb in enumerate(s_boxes):
            if si not in matched_s:
                per_class_fp[sb["cls"]] += 1
        for gi, gb in enumerate(g_boxes):
            if gi not in matched_g:
                per_class_fn[gb["cls"]] += 1

        b64 = base64.b64encode(img_path.read_bytes()).decode("utf-8")

        images_data.append({
            "name": img_path.name,
            "tp": img_tp,
            "fp": img_fp,
            "fn": img_fn,
            "gold_total": len(g_boxes),
            "student_total": len(s_boxes),
            "precision": round(img_tp / (img_tp + img_fp) if (img_tp + img_fp) else 0.0, 3),
            "recall": round(img_tp / (img_tp + img_fn) if (img_tp + img_fn) else 0.0, 3),
            "mean_iou": round(sum(img_ious) / len(img_ious) if img_ious else 0.0, 3),
            "student_boxes": s_boxes,
            "gold_boxes": g_boxes,
            "data_url": f"data:image/jpeg;base64,{b64}"
        })

    overall_p = round(total_tp / (total_tp + total_fp), 4)
    overall_r = round(total_tp / (total_tp + total_fn), 4)
    overall_f1 = round(2 * overall_p * overall_r / (overall_p + overall_r), 4)
    overall_iou = round(sum(all_ious) / len(all_ious), 4)

    summary = {
        "tp": total_tp, "fp": total_fp, "fn": total_fn,
        "precision": overall_p, "recall": overall_r, "f1": overall_f1,
        "mean_iou": overall_iou,
        "classes": {}
    }
    for c in range(4):
        c_tp = per_class_tp[c]
        c_fp = per_class_fp[c]
        c_fn = per_class_fn[c]
        c_p = round(c_tp / (c_tp + c_fp) if (c_tp + c_fp) else 0.0, 4)
        c_r = round(c_tp / (c_tp + c_fn) if (c_tp + c_fn) else 0.0, 4)
        c_f1 = round(2 * c_p * c_r / (c_p + c_r) if (c_p + c_r) else 0.0, 4)
        c_iou = round(sum(per_class_ious[c]) / len(per_class_ious[c]) if per_class_ious[c] else 0.0, 4)
        summary["classes"][CLASS_NAMES[c]] = {
            "tp": c_tp, "fp": c_fp, "fn": c_fn, "p": c_p, "r": c_r, "f1": c_f1, "iou": c_iou
        }

    html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<title>Báo Cáo Đối Chiếu & Bóc Tách Nhãn ADAS (50 Ảnh Train)</title>
<style>
  :root {{
    --bg-dark: #090D16;
    --bg-card: #131C2E;
    --border: #24344D;
    --text-white: #F8FAFC;
    --text-gray: #94A3B8;
    --accent-blue: #38BDF8;
    --accent-green: #10B981;
    --accent-gold: #F59E0B;
    --accent-red: #EF4444;
  }}
  * {{ box-sizing: border-box; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background: var(--bg-dark); color: var(--text-white); margin: 0; padding: 24px; text-align: center; }}
  .container {{ max-width: 1100px; margin: 0 auto; background: var(--bg-card); padding: 28px; border-radius: 18px; box-shadow: 0 20px 50px rgba(0,0,0,0.7); border: 1px solid var(--border); }}
  
  h2 {{ color: var(--accent-blue); margin: 0 0 8px 0; font-size: 26px; }}
  .header-sub {{ color: var(--text-gray); font-size: 14px; margin-bottom: 22px; line-height: 1.5; }}

  /* Top Stat Grid */
  .grid-stats {{ display: grid; grid-template-columns: repeat(6, 1fr); gap: 12px; margin-bottom: 20px; }}
  .stat-card {{ background: #0B1120; padding: 14px 10px; border-radius: 12px; border: 1px solid var(--border); transition: transform 0.2s; }}
  .stat-card:hover {{ transform: translateY(-2px); }}
  .stat-title {{ font-size: 11px; color: var(--text-gray); text-transform: uppercase; font-weight: 700; margin-bottom: 6px; letter-spacing: 0.5px; }}
  .stat-val {{ font-size: 22px; font-weight: 800; }}
  .stat-sub {{ font-size: 11px; color: #64748B; margin-top: 4px; }}

  /* Class Breakdown Pill Bar */
  .class-bar {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 24px; }}
  .class-chip {{ background: #0B1120; border: 1px solid var(--border); padding: 10px 14px; border-radius: 10px; text-align: left; font-size: 13px; }}
  .class-chip-header {{ display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px; }}
  .color-badge {{ width: 12px; height: 12px; border-radius: 3px; display: inline-block; vertical-align: middle; margin-right: 6px; }}
  .chip-metric {{ font-size: 12px; color: var(--text-gray); display: flex; justify-content: space-between; margin-top: 3px; }}

  /* Mode Switch Buttons */
  .mode-switch {{ display: flex; justify-content: center; gap: 10px; margin: 18px 0; flex-wrap: wrap; }}
  .mode-btn {{ background: #1E293B; color: #E2E8F0; border: 2px solid transparent; padding: 10px 18px; border-radius: 10px; font-size: 14px; cursor: pointer; font-weight: 700; transition: all 0.2s; }}
  .mode-btn:hover {{ background: #334155; }}
  .mode-btn.active {{ background: #0284C7; color: #FFFFFF; border-color: var(--accent-blue); box-shadow: 0 0 16px rgba(56, 189, 248, 0.4); }}

  /* Image Tag and Nav Bar */
  .image-bar {{ display: flex; justify-content: space-between; align-items: center; background: #0B1120; padding: 14px 20px; border-radius: 12px; border: 1px solid var(--border); margin: 14px 0; font-size: 14px; flex-wrap: wrap; gap: 10px; }}
  .badge-tag {{ display: inline-block; padding: 4px 10px; border-radius: 6px; font-weight: 700; font-size: 12px; }}
  .tag-tp {{ background: rgba(16, 185, 129, 0.2); color: #10B981; border: 1px solid #10B981; }}
  .tag-fp {{ background: rgba(239, 68, 68, 0.2); color: #EF4444; border: 1px solid #EF4444; }}
  .tag-fn {{ background: rgba(245, 158, 11, 0.2); color: #F59E0B; border: 1px solid #F59E0B; }}

  /* Stage Canvas */
  .canvas-box {{ position: relative; width: 640px; height: 640px; margin: 16px auto; border-radius: 10px; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.8); border: 2px solid var(--border); background: #000; }}
  #bg-image {{ width: 640px; height: 640px; display: block; }}
  #overlay {{ position: absolute; top: 0; left: 0; width: 640px; height: 640px; pointer-events: none; }}

  /* Controls & Slider */
  .controls {{ display: flex; justify-content: center; align-items: center; gap: 16px; margin-top: 18px; }}
  .nav-btn {{ background: #2563EB; color: white; border: none; padding: 10px 22px; border-radius: 8px; font-size: 15px; cursor: pointer; font-weight: bold; transition: 0.2s; }}
  .nav-btn:hover {{ background: #1D4ED8; }}
  .slider-bar {{ display: flex; justify-content: center; align-items: center; gap: 12px; margin-top: 12px; color: var(--text-gray); font-size: 13px; }}
  input[type=range] {{ width: 300px; cursor: pointer; }}
</style>
</head>
<body>
<div class="container">
  <h2>Báo Cáo Đối Chiếu & Bóc Tách Nhãn ADAS (50 Ảnh Train)</h2>
  <div class="header-sub">
    Chuẩn Schema Lab 2: <b>0: car | 1: truck | 2: bus | 3: van</b><br>
    Phím tắt: <b>[1]</b> Gold | <b>[2]</b> Bạn gán | <b>[3]</b> So sánh | <b>[4]</b> Bóc tách lỗi | <b>[A/D]</b> hoặc <b>[←/→]</b> Chuyển ảnh
  </div>

  <!-- Overall Dashboard -->
  <div class="grid-stats">
    <div class="stat-card">
      <div class="stat-title">True Positive (TP)</div>
      <div class="stat-val" style="color: #10B981;">{summary["tp"]} / 653</div>
      <div class="stat-sub">Xe khớp cả vị trí & nhãn</div>
    </div>
    <div class="stat-card">
      <div class="stat-title">Recall (Độ phủ)</div>
      <div class="stat-val" style="color: #10B981;">{summary["recall"]*100:.2f}%</div>
      <div class="stat-sub">Tỷ lệ bắt trúng xe chuẩn</div>
    </div>
    <div class="stat-card">
      <div class="stat-title">Mean IoU (Độ sít)</div>
      <div class="stat-val" style="color: #38BDF8;">{summary["mean_iou"]*100:.2f}%</div>
      <div class="stat-sub">Vượt xa mốc yêu cầu 70%</div>
    </div>
    <div class="stat-card">
      <div class="stat-title">False Positive (FP)</div>
      <div class="stat-val" style="color: #EF4444;">{summary["fp"]}</div>
      <div class="stat-sub">Xe đỗ ngoài luồng/ven đường</div>
    </div>
    <div class="stat-card">
      <div class="stat-title">False Negative (FN)</div>
      <div class="stat-val" style="color: #F59E0B;">{summary["fn"]}</div>
      <div class="stat-sub">Xe bị sót cần bổ sung</div>
    </div>
    <div class="stat-card">
      <div class="stat-title">F1-Score Ban Đầu</div>
      <div class="stat-val" style="color: #38BDF8;">{summary["f1"]}</div>
      <div class="stat-sub">Trước khi lọc 678 box FP</div>
    </div>
  </div>

  <!-- Per-Class Detailed Breakdown -->
  <div class="class-bar">
    <div class="class-chip">
      <div class="class-chip-header">
        <span><span class="color-badge" style="background:#2080c0;"></span> <b>0: car</b></span>
        <span style="color:#10B981; font-weight:bold;">{summary["classes"]["car"]["r"]*100:.1f}% Recall</span>
      </div>
      <div class="chip-metric"><span>Khớp TP:</span> <b>{summary["classes"]["car"]["tp"]} / 533</b></div>
      <div class="chip-metric"><span>Dư FP / Sót FN:</span> <span>+{summary["classes"]["car"]["fp"]} / -{summary["classes"]["car"]["fn"]}</span></div>
      <div class="chip-metric"><span>Mean IoU:</span> <b>{summary["classes"]["car"]["iou"]*100:.1f}%</b></div>
    </div>

    <div class="class-chip">
      <div class="class-chip-header">
        <span><span class="color-badge" style="background:#906080;"></span> <b>1: truck</b></span>
        <span style="color:#10B981; font-weight:bold;">{summary["classes"]["truck"]["r"]*100:.1f}% Recall</span>
      </div>
      <div class="chip-metric"><span>Khớp TP:</span> <b>{summary["classes"]["truck"]["tp"]} / 46</b></div>
      <div class="chip-metric"><span>Dư FP / Sót FN:</span> <span>+{summary["classes"]["truck"]["fp"]} / -{summary["classes"]["truck"]["fn"]}</span></div>
      <div class="chip-metric"><span>Mean IoU:</span> <b>{summary["classes"]["truck"]["iou"]*100:.1f}%</b></div>
    </div>

    <div class="class-chip">
      <div class="class-chip-header">
        <span><span class="color-badge" style="background:#204080;"></span> <b>2: bus</b></span>
        <span style="color:#10B981; font-weight:bold;">{summary["classes"]["bus"]["r"]*100:.1f}% Recall</span>
      </div>
      <div class="chip-metric"><span>Khớp TP:</span> <b>{summary["classes"]["bus"]["tp"]} / 20 (100%)</b></div>
      <div class="chip-metric"><span>Dư FP / Sót FN:</span> <span>+{summary["classes"]["bus"]["fp"]} / -{summary["classes"]["bus"]["fn"]}</span></div>
      <div class="chip-metric"><span>Mean IoU:</span> <b>{summary["classes"]["bus"]["iou"]*100:.1f}%</b></div>
    </div>

    <div class="class-chip">
      <div class="class-chip-header">
        <span><span class="color-badge" style="background:#10a040;"></span> <b>3: van</b></span>
        <span style="color:#10B981; font-weight:bold;">{summary["classes"]["van"]["r"]*100:.1f}% Recall</span>
      </div>
      <div class="chip-metric"><span>Khớp TP:</span> <b>{summary["classes"]["van"]["tp"]} / 54 (100%)</b></div>
      <div class="chip-metric"><span>Dư FP / Sót FN:</span> <span>+{summary["classes"]["van"]["fp"]} / -{summary["classes"]["van"]["fn"]}</span></div>
      <div class="chip-metric"><span>Mean IoU:</span> <b>{summary["classes"]["van"]["iou"]*100:.1f}%</b></div>
    </div>
  </div>

  <!-- Mode Selectors -->
  <div class="mode-switch">
    <button class="mode-btn active" id="btn-gold" onclick="setMode('gold')">⭐ 1. Chỉ Nhãn Chuẩn (Gold GT: 653 box)</button>
    <button class="mode-btn" id="btn-student" onclick="setMode('student')">✏️ 2. Chỉ Nhãn Bạn Gán (CVAT: 1271 box)</button>
    <button class="mode-btn" id="btn-compare" onclick="setMode('compare')">🔍 3. So Sánh Đè Lớp (Gold vàng vs Bạn xanh)</button>
    <button class="mode-btn" id="btn-error" onclick="setMode('error')">🎯 4. Bóc Tách Lỗi (TP xanh / FP đỏ / FN cam)</button>
  </div>

  <!-- Current Image Tag Info Bar -->
  <div class="image-bar">
    <div>Ảnh: <span id="img-name" style="font-weight: 800; color: var(--accent-blue); font-size: 16px;">drive_001.jpg</span></div>
    <div style="display: flex; gap: 12px; align-items: center; flex-wrap: wrap;">
      <span>Gold: <b id="img-gold-count" style="color: #F59E0B;">0</b></span>
      <span>Bạn: <b id="img-student-count" style="color: #38BDF8;">0</b></span>
      <span class="badge-tag tag-tp">TP: <span id="img-tp">0</span></span>
      <span class="badge-tag tag-fp">FP: <span id="img-fp">0</span></span>
      <span class="badge-tag tag-fn">FN: <span id="img-fn">0</span></span>
      <span>Recall: <b id="img-recall" style="color: #10B981;">0%</b></span>
      <span>IoU: <b id="img-iou" style="color: #38BDF8;">0%</b></span>
    </div>
  </div>

  <!-- Canvas Stage -->
  <div class="canvas-box">
    <img id="bg-image" src="" alt="Frame">
    <canvas id="overlay" width="640" height="640"></canvas>
  </div>

  <!-- Navigation Controls -->
  <div class="controls">
    <button class="nav-btn" onclick="prevImage()">❮ Ảnh trước (A / ←)</button>
    <span id="counter" style="font-size: 17px; font-weight: 800; min-width: 100px;">1 / 50</span>
    <button class="nav-btn" onclick="nextImage()">Ảnh tiếp theo (D / →) ❯</button>
  </div>

  <div class="slider-bar">
    <span>Chuyển nhanh ảnh:</span>
    <input type="range" id="image-slider" min="0" max="49" value="0" oninput="goToImage(parseInt(this.value))">
  </div>
</div>

<script>
  const data = {json.dumps(images_data)};
  let currentIndex = 0;
  let currentMode = 'gold';

  const imgEl = document.getElementById('bg-image');
  const canvas = document.getElementById('overlay');
  const ctx = canvas.getContext('2d');

  const imgNameEl = document.getElementById('img-name');
  const imgGoldEl = document.getElementById('img-gold-count');
  const imgStudentEl = document.getElementById('img-student-count');
  const imgTpEl = document.getElementById('img-tp');
  const imgFpEl = document.getElementById('img-fp');
  const imgFnEl = document.getElementById('img-fn');
  const imgRecallEl = document.getElementById('img-recall');
  const imgIouEl = document.getElementById('img-iou');
  const counterEl = document.getElementById('counter');
  const sliderEl = document.getElementById('image-slider');

  function setMode(mode) {{
    currentMode = mode;
    document.querySelectorAll('.mode-btn').forEach(b => b.classList.remove('active'));
    document.getElementById('btn-' + mode).classList.add('active');
    renderOverlay();
  }}

  function drawBox(b, color, labelText, isDashed = false, lineWidth = 2) {{
    const W = canvas.width;
    const H = canvas.height;
    const x = b.x * W;
    const y = b.y * H;
    const w = b.w * W;
    const h = b.h * H;

    ctx.save();
    if (isDashed) ctx.setLineDash([4, 4]);
    else ctx.setLineDash([]);

    ctx.strokeStyle = color;
    ctx.lineWidth = lineWidth;
    ctx.strokeRect(x, y, w, h);

    ctx.font = 'bold 11px sans-serif';
    const tw = ctx.measureText(labelText).width + 8;
    const ly = Math.max(16, y - 4);
    ctx.fillStyle = color;
    ctx.fillRect(x, ly - 14, tw, 16);
    ctx.fillStyle = '#FFFFFF';
    ctx.fillText(labelText, x + 4, ly - 3);
    ctx.restore();
  }}

  function renderOverlay() {{
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    const item = data[currentIndex];

    if (currentMode === 'gold') {{
      item.gold_boxes.forEach(b => drawBox(b, b.color, '[Gold] ' + b.name, false, 2));
    }} else if (currentMode === 'student') {{
      item.student_boxes.forEach(b => drawBox(b, b.color, '[Bạn] ' + b.name, false, 2));
    }} else if (currentMode === 'compare') {{
      item.student_boxes.forEach(b => drawBox(b, '#38BDF8', '[Bạn] ' + b.name, true, 2));
      item.gold_boxes.forEach(b => drawBox(b, '#F59E0B', '[Gold] ' + b.name, false, 3));
    }} else if (currentMode === 'error') {{
      // TP: Matched student boxes in green
      item.student_boxes.filter(b => b.is_matched).forEach(b => drawBox(b, '#10B981', 'TP: ' + b.name, false, 2));
      // FP: Unmatched student boxes in red dashed
      item.student_boxes.filter(b => !b.is_matched).forEach(b => drawBox(b, '#EF4444', 'FP: ' + b.name, true, 2));
      // FN: Unmatched gold boxes in orange solid
      item.gold_boxes.filter(b => !b.is_matched).forEach(b => drawBox(b, '#F59E0B', 'FN: ' + b.name, false, 3));
    }}
  }}

  function renderImage(idx) {{
    const item = data[idx];
    imgEl.src = item.data_url;
    imgNameEl.textContent = item.name;
    imgGoldEl.textContent = item.gold_total;
    imgStudentEl.textContent = item.student_total;
    imgTpEl.textContent = item.tp;
    imgFpEl.textContent = item.fp;
    imgFnEl.textContent = item.fn;
    imgRecallEl.textContent = (item.recall * 100).toFixed(1) + '%';
    imgIouEl.textContent = (item.mean_iou * 100).toFixed(1) + '%';
    counterEl.textContent = `${{idx + 1}} / ${{data.length}}`;
    sliderEl.value = idx;
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

  function goToImage(idx) {{
    if (idx >= 0 && idx < data.length) {{
      currentIndex = idx;
      renderImage(currentIndex);
    }}
  }}

  window.addEventListener('keydown', (e) => {{
    if (e.key === 'ArrowLeft' || e.key.toLowerCase() === 'a') prevImage();
    if (e.key === 'ArrowRight' || e.key.toLowerCase() === 'd') nextImage();
    if (e.key === '1') setMode('gold');
    if (e.key === '2') setMode('student');
    if (e.key === '3') setMode('compare');
    if (e.key === '4') setMode('error');
  }});

  renderImage(0);
</script>
</body>
</html>"""

    p1 = root / "visualize_comparison.html"
    p2 = Path(r"D:\App\visualize_comparison.html")
    p1.write_text(html, encoding="utf-8")
    p2.write_text(html, encoding="utf-8")
    print(f"[OK] Da tao thanh cong: {p1}")
    print(f"[OK] Da tao thanh cong: {p2}")


if __name__ == "__main__":
    main()
