#!/usr/bin/env python3
"""Bar-chart-race video (1080x1080, H.264, captions burned in, no audio) from docs/data/study.json.
x = pages crawled (0..300, in crawl order), bar = cumulative counted issues. Also writes a .vtt and a poster."""
import json, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); F = os.environ.get('STUDY_FONTS', '/workspace/toadstone/fonts')
D = json.load(open(os.path.join(R, 'docs/data/study.json'))); S = D['sites']; T = D['totals']
W = H = 1080; FPS = 30; T_RACE0, T_RACE1, T_END = 3.0, 23.0, 33.0
BG, PANEL, INK, MUTED, GRID = (13, 20, 17), (21, 32, 27), (234, 242, 236), (147, 168, 158), (36, 50, 41)
COLS = [(94,227,161),(108,182,255),(245,185,66),(255,159,67),(182,156,255),(255,123,123),(255,209,102),(247,143,179),(127,214,232),(200,226,122)]
def font(n, s): return ImageFont.truetype(os.path.join(F, n + '.ttf'), s)
fT, fL, fV, fC, fS = font('SpaceGrotesk-Bold', 46), font('Inter-SemiBold', 28), font('JetBrainsMono-Bold', 30), font('Inter-Bold', 38), font('Inter-Regular', 24)
def at(s, n):
    r = s['race']; n = min(n, r[-1][0]); v0 = 0.0
    for (p0, i0), (p1, i1) in zip(r, r[1:]):
        if p0 <= n <= p1: return i0 + (i1 - i0) * ((n - p0) / (p1 - p0) if p1 > p0 else 1)
    return r[-1][1]
fin = {s['site']: s['counted_issues'] for s in S}
CAPS = [(0, 3, 'Ten well-known SEO sites. About 300 pages each.'),
        (3, 9, 'A polite crawl: at most 2 requests a second, robots.txt respected.'),
        (9, 16, 'Each bar counts the gaps our crawler meets, page by page.'),
        (16, 23, 'Most lines stay flat. Spotless pages are the norm.'),
        (23, 26.5, f"Search Engine Roundtable: {fin['seroundtable.com']}. {294} of them are one sitewide badge with no alt text."),
        (26.5, 29.5, f"Semrush: {fin['semrush.com']}. Neil Patel: {fin['neilpatel.com']}. Surfer: {fin['surfer.ai']}."),
        (29.5, T_END, f"{T['broken']} broken URLs in {T['pages']:,} pages. Data: CC BY 4.0.")]
def wrap(d, text, f, maxw):
    words, lines, cur = text.split(), [], ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=f) <= maxw: cur = t
        else: lines.append(cur); cur = w
    return lines + [cur]
slot = {s['site']: float(i) for i, s in enumerate(S)}; vmax = 20.0; ease = lambda x: x * x * (3 - 2 * x)
def render(t, st):
    p = 0 if t < T_RACE0 else (1 if t >= T_RACE1 else ease((t - T_RACE0) / (T_RACE1 - T_RACE0)))
    n = 300 * p; vals = {s['site']: at(s, n) for s in S}
    order = sorted(S, key=lambda s: (-vals[s['site']], s['site']))
    for r, s in enumerate(order): slot[s['site']] += (r - slot[s['site']]) * 0.2
    vm = max(20.0, max(vals.values()) * 1.12); st['vmax'] += (vm - st['vmax']) * 0.12
    img = Image.new('RGB', (W, H), BG); d = ImageDraw.Draw(img)
    d.text((60, 48), 'Audit the experts', font=fT, fill=INK); d.text((60, 104), 'Cumulative counted issues as the crawl progresses', font=fS, fill=MUTED)
    d.text((W - 60, 56), f'{int(round(n))}', font=font('SpaceGrotesk-Bold', 92), fill=(245, 185, 66), anchor='ra')
    d.text((W - 60, 154), 'pages crawled (up to 300 per site)', font=fS, fill=MUTED, anchor='ra')
    x0, x1, y0, rh = 400, 1010, 215, 58
    for k in range(0, int(st['vmax']) + 1, 20 if st['vmax'] < 120 else 50):
        x = x0 + k / st['vmax'] * (x1 - x0)
        if x < x1: d.line([(x, y0 - 8), (x, y0 + 10 * rh)], fill=GRID, width=2)
    for i, s in enumerate(S):
        y = y0 + slot[s['site']] * rh; v = vals[s['site']]; w = max(4, v / st['vmax'] * (x1 - x0 - 80))
        d.rounded_rectangle([x0, y + 6, x0 + w, y + rh - 8], radius=8, fill=COLS[i])
        d.text((x0 - 14, y + rh / 2 - 2), s['site'], font=fL, fill=INK, anchor='rm')
        d.text((x0 + w + 12, y + rh / 2 - 2), f'{int(round(v))}', font=fV, fill=INK, anchor='lm')
    cap = next((c for c in CAPS if c[0] <= t < c[1]), CAPS[-1])[2]
    d.rounded_rectangle([40, 850, W - 40, 1000], radius=18, fill=PANEL)
    lines = wrap(d, cap, fC, W - 140); y = 925 - 26 * len(lines) + 4
    for ln in lines: d.text((W / 2, y), ln, font=fC, fill=INK, anchor='mm'); y += 52
    d.text((60, 1036), 'Polite crawl, 23 Oct 2026 · Toadstone (free, self-hosted, source-available)', font=font('Inter-Regular', 20), fill=MUTED, anchor='lm')
    return img
def vtt_time(s): return f'{int(s//60):02d}:{s%60:06.3f}'
if __name__ == '__main__':
    out = sys.argv[1]; os.makedirs(os.path.dirname(out), exist_ok=True); st = {'vmax': 20.0}
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
        '-c:v', 'libx264', '-preset', 'slow', '-crf', '21', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', '-an', out], stdin=subprocess.PIPE)
    N = int(T_END * FPS); last = None
    for f in range(N):
        im = render(f / FPS, st); last = im; p.stdin.write(im.tobytes())
    p.stdin.close(); p.wait()
    last.convert('RGB').save(os.path.join(os.path.dirname(out), 'race-poster.jpg'), quality=82)
    with open(os.path.join(os.path.dirname(out), 'issues-race.vtt'), 'w') as v:
        v.write('WEBVTT\n\n')
        for a, b, t in CAPS: v.write(f'{vtt_time(a)} --> {vtt_time(b)}\n{t}\n\n')
    print('done', out)
