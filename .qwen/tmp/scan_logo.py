import sys, datetime
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("PIL_MISSING")
    sys.exit(0)

home = Path.home()
dirs = [home / "Downloads", home / "Desktop", home / "Pictures"]
today = datetime.date.today()
print("TODAY:", today)

def near(c, target, tol):
    return all(abs(int(c[i]) - target[i]) <= tol for i in range(3))

rows = []
for d in dirs:
    if not d.is_dir():
        print("NO_DIR:", d)
        continue
    for p in d.rglob("*.png"):
        try:
            st = p.stat()
            mt = datetime.datetime.fromtimestamp(st.st_mtime)
        except OSError:
            continue
        if mt.date() != today:
            continue
        try:
            with Image.open(p) as im:
                w, h = im.size
                rgb = im.convert("RGB")
                corners = {
                    "TL": rgb.getpixel((0, 0)),
                    "TR": rgb.getpixel((w - 1, 0)),
                    "BL": rgb.getpixel((0, h - 1)),
                    "BR": rgb.getpixel((w - 1, h - 1)),
                }
                center = rgb.getpixel((w // 2, h // 2))
        except Exception as e:
            print("SKIP:", p, repr(e))
            continue
        square = abs(w - h) <= max(w, h) * 0.03
        big = 1400 <= w <= 2800 and 1400 <= h <= 2800
        dark = all(near(c, (25, 25, 50), 45) for c in corners.values())
        match = square and big and dark
        rows.append((mt, p, w, h, corners, center, match))

rows.sort(key=lambda r: r[0])
print("=== TODAY PNG (sorted by mtime) ===")
for mt, p, w, h, corners, center, match in rows:
    flag = "MATCH" if match else "     "
    print(f"[{flag}] {p}")
    print(f"        size={w}x{h} mtime={mt:%Y-%m-%d %H:%M:%S} center={center}")
    print(f"        corners={corners}")

matches = [r for r in rows if r[6]]
print("=== RESULT ===")
if matches:
    mt, p, w, h, corners, center, _ = matches[0]
    print("ORIGINAL:", p)
    print("size:", f"{w}x{h}", "mtime:", mt)
    print("corners:", corners)
    print("match_count:", len(matches))
else:
    print("NO_MATCH (square ~2048 + dark-blue corners not found today)")
