"""Make an 800px "_m" version of every full-size photo in public/img/ (for cards on sharp phone screens).
Run:  python3 tools/images/make_sizes.py
"""
import os
from PIL import Image

D = os.path.join(os.path.dirname(__file__), '..', '..', 'public', 'img')
made = 0
for name in sorted(os.listdir(D)):
    if not name.endswith('.webp') or name.endswith(('_t.webp', '_m.webp')):
        continue
    out = os.path.join(D, name[:-5] + '_m.webp')
    if os.path.exists(out):
        continue
    im = Image.open(os.path.join(D, name))
    if im.width <= 800:
        continue
    im.thumbnail((800, 800 * im.height // im.width), Image.LANCZOS)
    im.save(out, 'WEBP', quality=80, method=6)
    made += 1
print('made', made)
