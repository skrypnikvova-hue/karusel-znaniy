import sys, datetime
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("PIL_MISSING")
    sys.exit(0)

home = Path.home()
dirs = [home / "Downloads", home / "Desktop", home / "Pictures"]

def dark_blue(c):
    r, g, b = int(c[0]), int(c[1]), int(c[2])
    return max(r, g, b) < 95 and b >= r and b >= g and (b - r) >= 4

def warm_frac(rgb, w, h):
    x0, x1 = int(w * 0.20), int(w * 0.80)
    y0, y1 = int(h * 0.20), int(h * 0.80)
    box = rgb.crop((x0, y0, x1, y1))
    data = list(box.getdata())
    n = len(data) or 1
    warm = 0
    for p in data:
        r, g, b = p[0], p[1], p[2]
        if r > 140 and r > b + 25:
            warm += 1
    return warm / n

rows = []
seen = 0
for d in dirs:
    if not d.is_dir():
        print("NO_DIR:", d)
        continue
    for p in d.rglob("*.png"):
        try:
            with Image.open(p) as im:
                w, h = im.size
        except Exception:
            continue
        if w < 400 or h < 400:
            continue
        if abs(w - h) > max(w, h) * 0.04:
            continue
        seen += 1
        try:
            mt = datetime.datetime.fromtimestamp(p.stat().st_mtime)
            with Image.open(p) as im:
                rgb = im.convert("RGB")
                corners = [rgb.getpixel((0, 0)), rgb.getpixel((w - 1, 0)),
                           rgb.getpixel((0, h - 1)), rgb.getpixel((w - 1, h - 1))]
        except Exception:
            continue
        if not all(dark_blue(c) for c in corners):
            continue
        wf = warm_frac(rgb, w, h)
        match = wf > 0.03
        rows.append((mt, p, w, h, corners, wf, match))

rows.sort(key=lambda r: r[0])
print("SQUARE_SCANNED:", seen)
print("=== DARK-BLUE-CORNER SQUARE PNG (all dates, by mtime) ===")
for mt, p, w, h, corners, wf, match in rows:
    flag = "MATCH" if match else "     "
    print(f"[{flag}] {p}")
    print(f"        {w}x{h} mtime={mt:%Y-%m-%d %H:%M:%S} warm_center={wf:.3f}")
    print(f"        corners={corners}")

matches = [r for r in rows if r[6]]
print("=== RESULT ===")
if matches:
    mt, p, w, h, corners, wf, _ = matches[0]
    print("ORIGINAL:", p)
    print("size:", f"{w}x{h}", "mtime:", mt, "warm_center:", round(wf, 3))
    print("corners:", corners)
    print("match_count:", len(matches))
else:
    print("NO_MATCH")
