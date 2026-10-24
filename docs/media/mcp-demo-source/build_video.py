#!/usr/bin/env python3
"""Renders the MCP demo video from transcript-raw.json (REAL stdio JSON-RPC session against a local Toadstone).
Tool-call JSON and result values come straight from the transcript. Agent narration lines (top strip) are illustrative text written by us."""
import json, os, subprocess, sys, textwrap
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); F = os.environ.get('STUDY_FONTS', '/workspace/toadstone/fonts')
OUT = sys.argv[1] if len(sys.argv) > 1 else HERE
T = json.load(open(os.path.join(HERE, 'transcript-raw.json')))
W, H, FPS = 1280, 720, 24
BG, BAR, PANEL, LINE = (13, 20, 17), (24, 37, 31), (19, 29, 24), (36, 51, 43)
INK, MUTED, MINT, AMBER, CORAL, BLUE = (234, 242, 236), (159, 179, 169), (94, 227, 161), (245, 185, 66), (255, 123, 123), (108, 182, 255)
def font(n, s): return ImageFont.truetype(os.path.join(F, n), s)
fm, fmb, fms = font('JetBrainsMono-Regular.ttf', 20), font('JetBrainsMono-Bold.ttf', 20), font('JetBrainsMono-Regular.ttf', 15)
fi, fib, fh, fbig = font('Inter-Regular.ttf', 24), font('Inter-SemiBold.ttf', 24), font('SpaceGrotesk-Bold.ttf', 54), font('SpaceGrotesk-Bold.ttf', 40)
fsm = font('Inter-Regular.ttf', 17)

def res(call): return json.loads(call['response']['result']['content'][0]['text'])
A = T['calls']; tl = [t['name'] for t in T['tools_list']['result']['tools']]
start, st1, st2, iss, chk, page, refused = res(A[2]), res(A[3]), res(A[4]), res(A[5]), res(A[6]), res(A[7]), res(A[8])
ro = res(T['readonly_calls'][1]); cid = T['crawl_id']
def args(call): return json.dumps(call['request']['params']['arguments'])
def jl(d): return json.dumps(d)
by = iss['by_check']
first404 = next(i for i in iss['issues'] if i['check'] == '404_client_error')

# Each step: narration (illustrative), call line, result lines [(text,color)], duration
steps = [
 dict(n='I will audit the practice site with Toadstone. First, what can the server do?', c='tools/list',
      r=[(f"{len(tl)} tools: " + ', '.join(tl[:5]) + ',', INK), ('          ' + ', '.join(tl[5:]), INK),
         ('start_crawl, accept_issue = writes (off unless --allow-writes)', AMBER)], d=5.0),
 dict(n='Start a small crawl of the practice site, capped at 50 URLs.', c='start_crawl ' + args(A[2]),
      r=[(f"crawl_id: {start['crawl_id']}   max_urls: {start['max_urls']}   render: {str(start['render']).lower()}", MINT)], d=4.2),
 dict(n='Poll until it is done.', c=f'crawl_status {{"crawl_id": {cid}}}',
      r=[(f"status: {st1['status']}   pages: {st1['pages_done']}/{st1['pages_total']}", AMBER), (f"status: {st2['status']}   pages: {st2['pages_done']}/{st2['pages_total']}   progress: {st2['progress']:.0f}%", MINT)], d=4.2),
 dict(n='Now the errors only.', c='list_issues ' + args(A[5]),
      r=[(f"total: {iss['total']} errors on {st2['pages_total']} pages", CORAL)] + [(f"{k:<26}{v:>3}  " + '█' * v, INK) for k, v in by.items()], d=6.0),
 dict(n='The 404 matters most. What is the missing meta description check?', c='check_reference ' + args(A[6]),
      r=[(f"name: {chk['check']['name']}   category: {chk['check']['category']}", INK), (f"severity: {chk['check']['severity']}   pages affected: {chk['check']['pages']}", AMBER)], d=4.4),
 dict(n='Look at one page, /shop/rakes/.', c='page_detail {"crawl_id": %d, "url": ".../shop/rakes/"}' % cid,
      r=[(f"status_code: {page['page']['status_code']}   title: \"{page['page']['title']}\"   h1: \"{page['page']['h1']}\"", INK), (f"meta_description: \"{page['page']['meta_description']}\"   <- empty", CORAL), (f"canonical_url: \"{page['page']['canonical_url']}\"   word_count: {page['page']['word_count']}", INK)], d=5.0),
 dict(n='What if I drift off the practice site? Guardrails answer.', c='start_crawl {"url": "https://example.com/"}',
      r=[(f"refused: true   rule: {refused['rule']}", CORAL), ('Host \'example.com\' is not on this server\'s allow-list (localhost).', AMBER),
         ('', INK), ('default read-only server, start_crawl on the practice site:', MUTED), (f"refused: true   rule: {ro['rule']}", CORAL)], d=6.0),
]
INTRO, OUTRO = 3.2, 6.0
starts = []; t = INTRO
for s in steps: starts.append(t); t += s['d']
T_END = t + OUTRO

def wrap_lines(txt, width): return textwrap.wrap(txt, width) or ['']
def draw_frame(t):
    img = Image.new('RGB', (W, H), BG); d = ImageDraw.Draw(img)
    # header bar
    d.rectangle([0, 0, W, 48], fill=BAR)
    for i, c in enumerate(((255, 95, 86), (255, 189, 46), (39, 201, 63))): d.ellipse([18 + i * 26, 16, 34 + i * 26, 32], fill=c)
    d.text((W / 2, 24), 'AI agent + Toadstone MCP server · practice site · localhost', font=fms, fill=MUTED, anchor='mm')
    if t < INTRO:
        a = min(1, t / 0.8)
        d.text((80, 200), 'An AI agent audits a site', font=fh, fill=tuple(int(c * a) for c in INK))
        d.text((80, 270), 'through Toadstone’s MCP server', font=fh, fill=tuple(int(c * a) for c in MINT))
        d.text((80, 380), 'Real tool calls. Real output. Nothing mocked.', font=fib, fill=tuple(int(c * a) for c in MUTED))
        d.text((80, 425), 'Free · self-hosted · source-available (Elastic License 2.0)', font=fi, fill=tuple(int(c * a) for c in MUTED))
        footer(d, 0); return img
    if t >= T_END - OUTRO:
        k = t - (T_END - OUTRO); a = min(1, k / 0.7)
        c = lambda col: tuple(int(x * a) for x in col)
        d.text((80, 100), 'What the agent found', font=fbig, fill=c(INK))
        n404 = by.get('404_client_error', 0)
        lines = [(f"1 broken page: {first404['url'].replace('http://localhost:8099','')} returns 404", CORAL),
                 (f"7 pages missing a meta description", AMBER),
                 (f"8 pages with no structured data · 1 missing viewport · 1 sitemap error", AMBER),
                 (f"{iss['total']} errors in total on {st2['pages_total']} pages, found in seconds, no browser opened", MINT)]
        y = 190
        for txt, col in lines: d.text((80, y), '•  ' + txt, font=fi, fill=c(col)); y += 52
        d.text((80, 440), 'No seat fees, no URL cap in the app. MCP is read-only by default.', font=fib, fill=c(INK))
        d.text((80, 485), 'github.com/spcaeo/toadstone', font=fbig, fill=c(MINT))
        d.text((80, 560), 'Agent narration in this video is illustrative; every tool call and result is real.', font=fsm, fill=c(MUTED))
        footer(d, len(steps)); return img
    # find step
    idx = max(i for i, s in enumerate(starts) if t >= s); s = steps[idx]; k = t - starts[idx]
    # agent strip
    d.rounded_rectangle([40, 70, W - 40, 170], radius=14, fill=PANEL, outline=LINE)
    d.text((64, 84), 'AGENT', font=fms, fill=MINT)
    n = int(k * 45); txt = s['n'][:n]
    for j, ln in enumerate(wrap_lines(txt if txt else ' ', 78)[:2]): d.text((64, 108 + j * 32), ln, font=fib if False else fi, fill=INK)
    # terminal panel
    d.rounded_rectangle([40, 192, W - 40, 640], radius=14, fill=(10, 16, 13), outline=LINE)
    y = 214
    d.text((64, y), 'MCP tool call', font=fms, fill=MUTED); y += 30
    call = '→ ' + s['c']; m = int(max(0, k - 0.5) * 70)
    cl = wrap_lines(call, 80)
    shown = call[:m]
    sl = []; rem = shown
    for ln in cl:
        sl.append(rem[:len(ln) + (1 if False else 0)]); rem = rem[len(ln):].lstrip()
    for ln in textwrap.wrap(shown, 80) or ['']: d.text((64, y), ln, font=fmb, fill=BLUE); y += 28
    y = 214 + 30 + 28 * len(cl) + 14
    typed = m >= len(call)
    if typed and k > 0.5 + len(call) / 70 + 0.3:
        d.text((64, y), '← server reply (real)', font=fms, fill=MUTED); y += 30
        k2 = k - (0.5 + len(call) / 70 + 0.3)
        for i, (tx, col) in enumerate(s['r']):
            if k2 > i * 0.55:
                prog = min(1, (k2 - i * 0.55) / 0.35)
                cc = tuple(int(BG[j] + (col[j] - BG[j]) * prog) for j in range(3))
                for ln in (textwrap.wrap(tx, 86, subsequent_indent='    ') or ['']): d.text((64, y), ln, font=fm, fill=cc); y += 28
    footer(d, idx + 1); return img
def footer(d, i):
    d.rectangle([0, H - 60, W, H], fill=BAR)
    d.text((40, H - 30), 'Real MCP stdio session against local Toadstone · agent narration is illustrative', font=fms, fill=MUTED, anchor='lm')
    d.text((W - 40, H - 30), f'step {min(i, len(steps))}/{len(steps)}' if 0 < i <= len(steps) else 'toadstone', font=fms, fill=MINT, anchor='rm')
def build(out):
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'slow', '-crf', '22', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', '-an', out], stdin=subprocess.PIPE)
    for f in range(int(T_END * FPS)): p.stdin.write(draw_frame(f / FPS).tobytes())
    p.stdin.close(); p.wait()
def vtt(path):
    def ts(x): return f'{int(x//60):02d}:{x%60:06.3f}'
    cues = [(0.2, INTRO - 0.2, 'An AI agent audits a small site through Toadstone’s MCP server. Real tool calls, real output.')]
    for s, st in zip(steps, starts): cues.append((st + 0.3, st + s['d'] - 0.2, 'Agent (illustrative): ' + s['n'] + ' — tool: ' + s['c'].split(' ')[0]))
    cues.append((T_END - OUTRO + 0.5, T_END - 0.3, 'Found: 1 broken page, 7 pages without a meta description, 8 without structured data, 1 missing viewport, 1 sitemap error: 18 errors on 9 pages. Toadstone is free, self-hosted and source-available.'))
    open(path, 'w').write('WEBVTT\n\n' + '\n'.join(f'{ts(a)} --> {ts(b)}\n{c}\n' for a, b, c in cues))
if __name__ == '__main__':
    mp4 = os.path.join(OUT, 'mcp-demo.mp4'); build(mp4)
    draw_frame(starts[3] + 5.0).save(os.path.join(OUT, 'mcp-demo-poster.jpg'), quality=88)
    vtt(os.path.join(OUT, 'mcp-demo.vtt'))
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', mp4, '-vf', 'fps=8,scale=800:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=64[p];[b][p]paletteuse=dither=bayer', os.path.join(OUT, 'mcp-demo.gif')])
    print('done', round(T_END, 1))
