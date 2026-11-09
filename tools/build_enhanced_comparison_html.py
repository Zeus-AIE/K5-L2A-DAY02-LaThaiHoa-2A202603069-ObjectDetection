#!/usr/bin/env python3
"""Build Enhanced Comparison HTML with complete metrics, confusion breakdown, and error analysis."""

import base64
from collections import defaultdict
import json
from pathlib import Path


CLASS_NAMES = {0: "car", 1: "truck", 2: "bus", 3: "van"}
# CVAT standard colors
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
                "xc": xc, "yc": yc, "w": w, "h": h,
                "x": xc - w / 2, "y": yc - h / 2,
                "x2": xc + w / 2, "y2": yc + h / 2
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

        # Compute matches
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

        # Mark boxes
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

    summary_stats = {
        "tp": total_tp, "fp": total_fp, "fn": total_fn,
        "precision": overall_p, "recall": overall_r, "f1": overall_f1,
        "mean_iou": overall_iou,
        "per_class": {}
    }
    for c in range(4):
        c_tp = per_class_tp[c]
        c_fp = per_class_fp[c]
        c_fn = per_class_fn[c]
        c_p = round(c_tp / (c_tp + c_fp) if (c_tp + c_fp) else 0.0, 4)
        c_r = round(c_tp / (c_tp + c_fn) if (c_tp + c_fn) else 0.0, 4)
        c_f1 = round(2 * c_p * c_r / (c_p + c_r) if (c_p + c_r) else 0.0, 4)
        c_iou = round(sum(per_class_ious[c]) / len(per_class_ious[c]) if per_class_ious[c] else 0.0, 4)
        summary_stats["per_class"][CLASS_NAMES[c]] = {
            "tp": c_tp, "fp": c_fp, "fn": c_fn, "p": c_p, "r": c_r, "f1": c_f1, "iou": c_iou
        }

    html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<title>Đối Chiếu và Phân Tích Nhãn ADAS (50 Ảnh Train)</title>
<style>
  :root {{
    --bg-main: #0B1120;
    --bg-card: #1E293B;
    --border-card: #334155;
    --text-primary: #F8FAFC;
    --text-muted: #94A3B8;
    --accent-blue: #38BDF8;
    --accent-green: #10B981;
    --accent-gold: #F59E0B;
    --accent-red: #EF4444;
  }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: var(--bg-main); color: var(--text-primary); margin: 0; padding: 20px; text-align: center; }}
  .container {{ max-width: 1050px; margin: 0 auto; background: var(--bg-card); padding: 24px; border-radius: 16px; box-shadow: 0 16px 40px rgba(0,0,0,0.6); border: 1px solid var(--border-card); }}
  h2 {{ color: var(--accent-blue); margin-top: 0; margin-bottom: 6px; font-size: 24px; }}
  .subtitle {{ color: var(--text-muted); font-size: 14px; margin-bottom: 20px; }}

  /* Dashboard Summary */
  .dashboard {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px; margin-bottom: 20px; }}
  .metric-card {{ background: #0F172A; padding: 12px 8px; border-radius: 10px; border: 1px solid var(--border-card); }}
  .metric-label {{ font-size: 12px; color: var(--text-muted); text-transform: uppercase; font-weight: 600; margin-bottom: 4px; }}
  .metric-value {{ font-size: 20px; font-weight: bold; color: var(--accent-blue); }}
  .metric-desc {{ font-size: 11px; color: #64748B; margin-top: 2px; }}

  /* Class Breakdown Bar */
  .class-bar {{ display: flex; justify-content: center; gap: 15px; margin-bottom: 20px; flex-wrap: wrap; background: #0F172A; padding: 10px 16px; border-radius: 10px; border: 1px solid var(--border-card); }}
  .class-chip {{ font-size: 13px; font-weight: 600; display: flex; align-items: center; gap: 6px; }}
  .color-dot {{ width: 12px; height: 12px; border-radius: 3px; display: inline-block; }}

  /* Mode Switches */
  .mode-switch {{ display: flex; justify-content: center; gap: 8px; margin: 16px 0; flex-wrap: wrap; }}
  .mode-btn {{ background: #334155; color: #E2E8F0; border: 2px solid transparent; padding: 9px 16px; border-radius: 8px; font-size: 14px; cursor: pointer; font-weight: 600; transition: all 0.2s; }}
  .mode-btn:hover {{ background: #475569; }}
  .mode-btn.active {{ background: #0284C7; color: #FFFFFF; border-color: var(--accent-blue); box-shadow: 0 0 14px rgba(56, 189, 248, 0.4); }}

  /* Image Tag Bar */
  .image-info-bar {{ display: flex; justify-content: space-between; align-items: center; background: #0F172A; padding: 12px 18px; border-radius: 10px; margin: 12px 0; border: 1px solid var(--border-card); font-size: 14px; }}
  .image-stats {{ display: flex; gap: 16px; font-size: 14px; }}
  .stat-badge {{ padding: 3px 8px; border-radius: 6px; font-weight: 700; font-size: 13px; }}
  .badge-tp {{ background: rgba(16, 185, 129, 0.2); color: #10B981; border: 1px solid #10B981; }}
  .badge-fp {{ background: rgba(239, 68, 68, 0.2); color: #EF4444; border: 1px solid #EF4444; }}
  .badge-fn {{ background: rgba(245, 158, 11, 0.2); color: #F59E0B; border: 1px solid #F59E0B; }}

  /* Canvas */
  .canvas-wrapper {{ position: relative; width: 640px; height: 640px; margin: 15px auto; border-radius: 8px; overflow: hidden; box-shadow: 0 8px 24px rgba(0,0,0,0.6); border: 2px solid var(--border-card); background: #000; }}
  #bg-image {{ width: 640px; height: 640px; display: block; }}
  #overlay {{ position: absolute; top: 0; left: 0; width: 640px; height: 640px; pointer-events: none; }}

  /* Navigation */
  .controls {{ margin: 18px 0; display: flex; justify-content: center; align-items: center; gap: 14px; }}
  .nav-btn {{ background: #2563EB; color: white; border: none; padding: 10px 20px; border-radius: 8px; font-size: 15px; cursor: pointer; font-weight: bold; transition: 0.2s; }}
  .nav-btn:hover {{ background: #1D4ED8; }}
</style>
</head>
<body>
<div class="container">
  <h2>Đối Chiếu và Phân Tích Nhãn ADAS (50 Ảnh Train)</h2>
  <div class="subtitle">Bộ nhãn đã đồng bộ chuẩn: 0: car | 1: truck | 2: bus | 3: van • Phím tắt: [1] Gold | [2] Bạn | [3] So sánh | [4] Bóc tách Lỗi | [A/D] hoặc [←/→] Chuyển ảnh</div>

  <!-- Overall Dashboard -->
  <div class="dashboard">
    <div class="metric-card">
      <div class="metric-label">True Positives (TP)</div>
      <div class="metric-value" style="color: #10B981;">{summary_stats["tp"]} / 653</div>
      <div class="metric-desc">Số xe gán đúng cả vị trí & nhãn</div>
    </div>
    <div class="metric-card">
      <div class="metric-label">Recall (Độ phủ)</div>
      <div class="metric-value" style="color: #10B981;">{summary_stats["recall"] * 100:.2f}%</div>
      <div class="metric-desc">Tỷ lệ phát hiện xe chuẩn</div>
    </div>
    <div class="metric-card">
      <div class="metric-label">False Positives (FP)</div>
      <div class="metric-value" style="color: #EF4444;">{summary_stats["fp"]}</div>
      <div class="metric-desc">Xe đỗ xa/lề đường ngoài luồng</div>
    </div>
    <div class="metric-card">
      <div class="metric-label">False Negatives (FN)</div>
      <div class="metric-value" style="color: #F59E0B;">{summary_stats["fn"]}</div>
      <div class="metric-desc">Số xe bị sót cần bổ sung</div>
    </div>
    <div class="metric-card">
      <div class="metric-label">Mean IoU (Độ sít)</div>
      <div class="metric-value" style="color: #38BDF8;">{summary_stats["mean_iou"] * 100:.2f}%</div>
      <div class="metric-desc">Độ khớp hộp bao so với chuẩn</div>
    </div>
  </div>

  <!-- Per-Class Metrics Chips -->
  <div class="class-bar">
    <div class="class-chip"><span class="color-dot" style="background:#2080c0;"></span> <b>car:</b> TP={summary_stats["per_class"]["car"]["tp"]}, Recall={summary_stats["per_class"]["car"]["r"]*100:.1f}%, IoU={summary_stats["per_class"]["car"]["iou"]*100:.1f}%</div>
    <div class="class-chip"><span class="color-dot" style="background:#906080;"></span> <b>truck:</b> TP={summary_stats["per_class"]["truck"]["tp"]}, Recall={summary_stats["per_class"]["truck"]["r"]*100:.1f}%, IoU={summary_stats["per_class"]["truck"]["iou"]*100:.1f}%</div>
    <div class="class-chip"><span class="color-dot" style="background:#204080;"></span> <b>bus:</b> TP={summary_stats["per_class"]["bus"]["tp"]}, Recall={summary_stats["per_class"]["bus"]["r"]*100:.1f}%, IoU={summary_stats["per_class"]["bus"]["iou"]*100:.1f}%</div>
    <div class="class-chip"><span class="color-dot" style="background:#10a040;"></span> <b>van:</b> TP={summary_stats["per_class"]["van"]["tp"]}, Recall={summary_stats["per_class"]["van"]["r"]*100:.1f}%, IoU={summary_stats["per_class"]["van"]["iou"]*100:.1f}%</div>
  </div>

  <!-- Mode Selector -->
  <div class="mode-switch">
    <button class="mode-btn active" id="btn-gold" onclick="setMode('gold')">⭐ 1. Nhãn Chuẩn (Gold GT)</button>
    <button class="mode-btn" id="btn-student" onclick="setMode('student')">✏️ 2. Nhãn của Bạn (CVAT)</button>
    <button class="mode-btn" id="btn-compare" onclick="setMode('compare')">🔍 3. Chế Độ So Sánh (Gold nét liền vs Bạn nét đứt)</button>
    <button class="mode-btn" id="btn-error" onclick="setMode('error')">🎯 4. Bóc Tách Lỗi (TP xanh / FP đỏ / FN cam)</button>
  </div>

  <!-- Image Info Tag Bar -->
  <div class="image-info-bar">
    <div>Ảnh: <span id="img-name" style="font-weight: bold; color: var(--accent-blue);">drive_001.jpg</span></div>
    <div class="image-stats">
      <span class="stat-badge badge-tp">TP (Đạt): <span id="img-tp">0</span></span>
      <span class="stat-badge badge-fp">FP (Dư): <span id="img-fp">0</span></span>
      <span class="stat-badge badge-fn">FN (Sót): <span id="img-fn">0</span></span>
      <span>Recall: <b id="img-recall" style="color: #10B981;">0%</b></span>
      <span>Mean IoU: <b id="img-iou" style="color: #38BDF8;">0%</b></span>
    </div>
  </div>

  <!-- Canvas Stage -->
  <div class="canvas-wrapper">
    <img id="bg-image" src="" alt="Frame">
    <canvas id="overlay" width="640" height="640"></canvas>
  </div>

  <!-- Controls -->
  <div class="controls">
    <button class="nav-btn" onclick="prevImage()">❮ Ảnh trước (A / ←)</button>
    <span id="counter" style="font-size: 16px; font-weight: bold; min-width: 90px;">1 / 50</span>
    <button class="nav-btn" onclick="nextImage()">Ảnh tiếp theo (D / →) ❯</button>
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
  const imgTpEl = document.getElementById('img-tp');
  const imgFpEl = document.getElementById('img-fp');
  const imgFnEl = document.getElementById('img-fn');
  const imgRecallEl = document.getElementById('img-recall');
  const imgIouEl = document.getElementById('img-iou');
  const counterEl = document.getElementById('counter');

  function setMode(mode) {{
    currentMode = mode;
    document.querySelectorAll('.mode-btn').forEach(btn => btn.classList.remove('active'));
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
    imgTpEl.textContent = item.tp;
    imgFpEl.textContent = item.fp;
    imgFnEl.textContent = item.fn;
    imgRecallEl.textContent = (item.recall * 100).toFixed(1) + '%';
    imgIouEl.textContent = (item.mean_iou * 100).toFixed(1) + '%';
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
    print(f"[OK] Da tao {p1}")
    print(f"[OK] Da tao {p2}")


if __name__ == "__main__":
    main()
