"""Make a light China map for the website from the dashboard map (src/data/map-china.svg).
Keeps the land and province lines, drops shapes outside the view, simplifies lines (Douglas-Peucker)
and rounds numbers. Output: public/map/china.svg
Run: python3 tools/map/simplify_map.py
"""
import re, os

ROOT = os.path.join(os.path.dirname(__file__), '..', '..')
src = open(os.path.join(ROOT, 'src/data/map-china.svg'), encoding='utf-8').read()
land = re.search(r'<path class="land" d="([^"]*)"', src).group(1)
prov = re.search(r'<path class="prov" d="([^"]*)"', src).group(1)


def parse(d):
    subs, cur, closed = [], [], []
    for cmd, x, y in re.findall(r'([MLZ])\s*(-?[\d.]+)?,?(-?[\d.]+)?', d):
        if cmd == 'M':
            if cur: subs.append((cur, False))
            cur = [(float(x), float(y))]
        elif cmd == 'L':
            cur.append((float(x), float(y)))
        elif cmd == 'Z':
            if cur: subs.append((cur, True)); cur = []
    if cur: subs.append((cur, False))
    return subs


def rdp(pts, eps):
    if len(pts) < 3: return pts
    (x1, y1), (x2, y2) = pts[0], pts[-1]
    dx, dy = x2 - x1, y2 - y1
    n = (dx * dx + dy * dy) ** .5 or 1e-9
    i, dmax = 0, -1
    for k in range(1, len(pts) - 1):
        x0, y0 = pts[k]
        dist = abs(dy * x0 - dx * y0 + x2 * y1 - y2 * x1) / n
        if dist > dmax: i, dmax = k, dist
    if dmax <= eps: return [pts[0], pts[-1]]
    return rdp(pts[:i + 1], eps)[:-1] + rdp(pts[i:], eps)


def build(d, eps, margin=40, min_size=1.5):
    out = []
    for pts, closed in parse(d):
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        if max(xs) < -margin or min(xs) > 760 + margin or max(ys) < -margin or min(ys) > 760 + margin:
            continue
        if closed and max(xs) - min(xs) < min_size and max(ys) - min(ys) < min_size:
            continue
        s = rdp(pts, eps)
        if len(s) < 2: continue
        out.append('M' + 'L'.join(f'{x:.1f},{y:.1f}'.replace('.0,', ',').rstrip('0').rstrip('.') if False else f'{round(x,1):g},{round(y,1):g}' for x, y in s) + ('Z' if closed else ''))
    return ''.join(out)


L = build(land, 0.5)
P = build(prov, 0.6)
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 760">'
       f'<path d="{L}" fill="#EDE8DC" stroke="#D3CCBD" stroke-width="1"/>'
       f'<path d="{P}" fill="none" stroke="#D3CCBD" stroke-width=".8" opacity=".7"/></svg>\n')
os.makedirs(os.path.join(ROOT, 'public/map'), exist_ok=True)
open(os.path.join(ROOT, 'public/map/china.svg'), 'w').write(svg)
# Dark-mode version
dark = svg.replace('fill="#EDE8DC" stroke="#D3CCBD"', 'fill="#2B322D" stroke="#3E4640"').replace('stroke="#D3CCBD" stroke-width=".8"', 'stroke="#46504A" stroke-width=".8"')
open(os.path.join(ROOT, 'public/map/china-dark.svg'), 'w').write(dark)
print('land', len(land), '->', len(L), '| prov', len(prov), '->', len(P), '| file', len(svg))
