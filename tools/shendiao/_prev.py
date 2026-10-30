import sys, os
from PIL import Image
src, dst = sys.argv[1], sys.argv[2]
im = Image.open(src).convert("RGB")
w, h = im.size
m = max(w, h)
if m > 900:
    im = im.resize((int(w*900/m), int(h*900/m)), Image.LANCZOS)
im.save(dst, "PNG", optimize=True)
print(dst, im.size, os.path.getsize(dst)//1024, "KB")
