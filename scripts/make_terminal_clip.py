#!/usr/bin/env python3
"""Terminal clip of quick_audit.sh. Output text is the REAL output captured in data/evidence/quick-audit-sample-site.txt
(sample site: 7 deliberately broken pages served on localhost). The ~12 s crawl is shown sped up; the clip says so."""
import os, subprocess, sys, shutil
from PIL import Image, ImageDraw, ImageFont
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); F = os.environ.get('STUDY_FONTS', '/workspace/toadstone/fonts')
W, H, FPS = 1280, 720, 24
BG, BAR, INK, MUTED, GREEN, AMBER, CORAL = (10, 16, 13), (24, 36, 30), (222, 236, 227), (120, 145, 133), (94, 227, 161), (245, 185, 66), (255, 123, 123)
fm = ImageFont.truetype(os.path.join(F, 'JetBrainsMono-Regular.ttf'), 22); fb = ImageFont.truetype(os.path.join(F, 'JetBrainsMono-Bold.ttf'), 22)
lines = open(os.path.join(R, 'data/evidence/quick-audit-sample-site.txt')).read().splitlines()
head, bullets = lines[0], [l for l in lines if l.startswith('•')]
assert len(bullets) == 3
import textwrap
def wrapb(b): return textwrap.wrap(b, 84, subsequent_indent='  ')
CMD = '$ ./quick_audit.sh http://localhost:8099/'
def frame(t):
    img = Image.new('RGB', (W, H), BG); d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 44], fill=BAR)
    for i, c in enumerate(((255, 95, 86), (255, 189, 46), (39, 201, 63))): d.ellipse([18 + i * 26, 14, 34 + i * 26, 30], fill=c)
    d.text((W / 2, 22), 'quick_audit.sh · sample site (7 pages, deliberately broken)', font=fm, fill=MUTED, anchor='mm')
    y = 70; n = int(max(0, t - 0.6) * 22)
    d.text((30, y), CMD[:n], font=fb, fill=GREEN)
    if n <= len(CMD) and int(t * 2) % 2 == 0: d.rectangle([30 + 13.2 * min(n, len(CMD)), y + 2, 30 + 13.2 * min(n, len(CMD)) + 12, y + 28], fill=GREEN)
    y += 50
    ts = 0.6 + len(CMD) / 22 + 0.4
    if t > ts:
        p = min(1, (t - ts) / 3.0); done = p >= 1
        d.text((30, y), f"Crawling… {int(p*7)}/7 pages · {int(p*19)} requests · {int(p*12)}s", font=fm, fill=AMBER if not done else MUTED); 
        bw = 560; d.rectangle([30, y + 36, 30 + bw, y + 50], outline=MUTED); d.rectangle([32, y + 38, 32 + (bw - 4) * p, y + 48], fill=GREEN)
        d.text((30 + bw + 16, y + 43), 'crawl shown sped up', font=ImageFont.truetype(os.path.join(F, 'JetBrainsMono-Regular.ttf'), 16), fill=MUTED, anchor='lm')
        y += 90
        if done:
            t2 = t - (ts + 3.0)
            d.text((30, y), head.replace('http://localhost:8099/', 'http://localhost:8099/'), font=fb, fill=INK); y += 44
            for i, b in enumerate(bullets):
                if t2 > 0.6 + i * 1.5:
                    for j, ln in enumerate(wrapb(b)):
                        d.text((30, y), ln, font=fm, fill=(CORAL if i == 0 else AMBER) if j == 0 and False else INK); y += 30
                    d.ellipse([0, 0, 0, 0]); y += 12
    return img
T_END = 0.6 + len(CMD) / 22 + 0.4 + 3.0 + 0.6 + 3 * 1.5 + 3.2
def build(out, scale=None):
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'slow', '-crf', '22', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', '-an', out], stdin=subprocess.PIPE)
    N = int(T_END * FPS); last = None
    for f in range(N): last = frame(f / FPS); p.stdin.write(last.tobytes())
    p.stdin.close(); p.wait(); return last
if __name__ == '__main__':
    out = sys.argv[1]; last = build(out)
    last.save(os.path.join(os.path.dirname(out), 'terminal-poster.jpg'), quality=85)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', out, '-vf', 'fps=10,scale=960:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=64[p];[b][p]paletteuse=dither=bayer', os.path.join(os.path.dirname(out), 'quick-audit-terminal.gif')])
    print('done', T_END)
