import hashlib
from pathlib import Path
from collections import deque
from PIL import Image, ImageDraw

SRC = Path(r"C:\Users\Vladimir\Pictures\karuselznaniy.png")
COPIES = [
    SRC,
    Path(r"C:\Users\Vladimir\Downloads\ivetta-pay\kz-logo.png"),
    Path(r"C:\Users\Vladimir\Downloads\svisual-check\kz-logo.png"),
]
print("=== MD5 (original vs copies) ===")
for p in COPIES:
    print(hashlib.md5(p.read_bytes()).hexdigest(), p)

img = Image.open(SRC).convert("RGB")
w, h = img.size
MARK = (255, 0, 255)
for seed in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]:
    ImageDraw.floodfill(img, seed, MARK, thresh=40)

mask = bytearray(1 if p != MARK else 0 for p in img.getdata())
fg_total = sum(mask)

seen = bytearray(w * h)
start = (h // 2) * w + (w // 2)
if not mask[start]:
    for i in range(w * h):
        if mask[i]:
            start = i
            break
seen[start] = 1
dq = deque([start])
while dq:
    i = dq.popleft()
    x = i % w
    y = i // w
    for dy in (-1, 0, 1):
        ny = y + dy
        if ny < 0 or ny >= h:
            continue
        base = ny * w
        for dx in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx = x + dx
            if nx < 0 or nx >= w:
                continue
            j = base + nx
            if mask[j] and not seen[j]:
                seen[j] = 1
                dq.append(j)

kept = sum(seen)
table = bytes(255 if i == 1 else 0 for i in range(256))
alpha = seen.translate(table)
out = img.copy()
out.putalpha(Image.frombytes("L", (w, h), alpha))
Path("assets").mkdir(exist_ok=True)
out.save("assets/kz-logo.png")

total = w * h
print("=== RESULT ===")
print("saved: assets/kz-logo.png")
print("size:", f"{w}x{h}")
print("foreground_before:", fg_total, "kept_mandala:", kept,
      "removed_islands(watermark etc):", fg_total - kept)
print("transparent_fraction:", round((total - kept) / total, 4))
