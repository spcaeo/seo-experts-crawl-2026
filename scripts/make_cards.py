#!/usr/bin/env python3
"""OG image (1200x630) + social cards (1200x675) with headline stats. Background = the real per-page health grid."""
import json, os
from PIL import Image, ImageDraw, ImageFont
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); F = os.environ.get('STUDY_FONTS', '/workspace/toadstone/fonts')
D = json.load(open(os.path.join(R, 'docs/data/study.json')))
def font(n, s): return ImageFont.truetype(os.path.join(F, n + '.ttf'), s)
BG, INK, MUTED = (13, 20, 17), (234, 242, 236), (147, 168, 158)
AMBER, MINT, CORAL = (245, 185, 66), (94, 227, 161), (255, 107, 107)
CELL = {'0': (34, 74, 55), '1': (120, 95, 40), '2': (150, 110, 40), '3': (170, 120, 40), 'B': (150, 60, 60)}
def grid_bg(img, x0, y0, w, h, alpha=0.55):
    layer = Image.new('RGBA', img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    rows = D['sites']; rh = h / len(rows)
    for i, s in enumerate(rows):
        g = s['grid']; cw = w / 300
        for j, c in enumerate(g):
            x = x0 + j * cw; y = y0 + i * rh
            d.rounded_rectangle([x + 0.6, y + 2, x + cw - 0.6, y + rh - 2], radius=1, fill=CELL[c] + (int(255 * alpha),))
    img.alpha_composite(layer)
def fade(img, top=0, strength=235):
    W, H = img.size; ov = Image.new('RGBA', img.size); d = ImageDraw.Draw(ov)
    for x in range(W):
        a = int(strength * max(0, 1 - x / (W * 0.95)) ** 0.7); d.line([(x, 0), (x, H)], fill=BG + (a,))
    img.alpha_composite(ov)
def card(size, kicker, big, sub, foot, name, big_color=AMBER):
    W, H = size; img = Image.new('RGBA', size, BG + (255,))
    grid_bg(img, 40, 40, W - 80, H - 80); fade(img)
    d = ImageDraw.Draw(img)
    d.text((72, 70), kicker.upper(), font=font('Inter-Bold', 24), fill=MINT)
    y = 118
    for line in big.split('\n'):
        f = font('SpaceGrotesk-Bold', 86 if len(big) < 40 else 70); d.text((68, y), line, font=f, fill=big_color); y += f.size + 8
    y += 14
    for line in sub.split('\n'):
        d.text((72, y), line, font=font('Inter-SemiBold', 34), fill=INK); y += 46
    d.text((72, H - 78), foot, font=font('Inter-Regular', 22), fill=MUTED)
    d.rounded_rectangle([W - 300, H - 92, W - 64, H - 50], radius=21, fill=(28, 44, 36))
    d.text((W - 282, H - 84), 'toadstone · study', font=font('JetBrainsMono-Bold', 20), fill=MINT)
    for o in ('docs/media', 'docs'):
        if o == 'docs' and name != 'og-image.png': continue
        img.convert('RGB').save(os.path.join(R, o, name), optimize=True)
T = D['totals']; foot = 'Polite ~300-page crawl per site · 23 Oct 2026 · open data, CC BY 4.0'
card((1200, 630), 'Audit the experts · 2026', 'We crawled 10 of the\nbest-known SEO sites.', f"{T['pages']:,} pages. {T['broken']} broken URLs.\nMostly spotless, and kind of reassuring.", foot, 'og-image.png', INK)
card((1200, 675), 'Audit the experts · finding 1', f"{T['broken']} broken URLs\nin {T['pages']:,} pages", 'No site had more than one.\nThat is a seriously high bar.', foot, 'card-1-broken.png')
card((1200, 675), 'Audit the experts · finding 2', '1 template line\n= 294 of 300 pages', 'One sitewide badge with no alt text.\nFix templates first, then the long tail.', foot, 'card-2-template.png')
card((1200, 675), 'Audit the experts · finding 3', '0 counted issues\nin 300 pages', "Semrush's blog came back clean on\nevery basic we checked.", foot, 'card-3-clean.png', MINT)
card((1200, 675), 'Audit the experts · finding 4', '56 links take a\ndetour first', 'Backlinko links that 301 to sister site\nsearchengineland.com. A content move, not a mistake.', foot, 'card-4-redirects.png')
print('ok')
