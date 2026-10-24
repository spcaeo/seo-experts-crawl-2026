#!/usr/bin/env python3
"""Static charts for the README / landing page (PNG, from docs/data/study.json)."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from style import *; apply()
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); D = json.load(open(os.path.join(R, 'docs/data/study.json')))
S = sorted(D['sites'], key=lambda s: s['per_page']); names = [s['site'] for s in S]
OUTS = [os.path.join(R, 'charts'), os.path.join(R, 'docs', 'media')]
def save(fig, name):
    for o in OUTS: os.makedirs(o, exist_ok=True); fig.savefig(os.path.join(o, name), dpi=110)
    plt.close(fig)
foot = 'Polite ~300-page crawl per site, 23 Oct 2026 · Toadstone · data: CC BY 4.0'
# 1. counted issues per page
fig, ax = plt.subplots(figsize=(11, 6.2)); fig.subplots_adjust(left=0.24, right=0.95, top=0.82, bottom=0.12)
v = [s['counted_issues'] / s['pages'] for s in S]
cols = [MINT if x < 0.05 else AMBER for x in v]
ax.barh(names, v, color=cols, height=0.62)
for i, (x, s) in enumerate(zip(v, S)): ax.text(x + 0.012, i, f"{x:.2f}  ({s['counted_issues']} in {s['pages']} pages)" + ('  · 294 are one sitewide badge' if s['site'] == 'seroundtable.com' else ''), va='center', color=INK, fontsize=11)
ax.set_xlim(0, 1.6); ax.set_xlabel('Counted issues per crawled page'); ax.grid(axis='y', visible=False)
fig.text(0.03, 0.93, 'Even the experts: counted issues per page', fontsize=21, fontweight='bold', fontfamily='Space Grotesk')
fig.text(0.03, 0.875, 'Lower is better. Long titles, near-duplicates and bot-blocked URLs are not counted.', color=MUTED, fontsize=12)
fig.text(0.03, 0.03, foot, color=MUTED, fontsize=10); save(fig, 'chart_issues_per_page.png')
# 2. share of pages with each basic gap
keys = [('missing_meta_description', 'No meta description'), ('missing_canonical', 'No canonical'),
        ('pages_content_img_no_alt', 'Content image without alt'), ('missing_h1', 'No H1')]
fig, ax = plt.subplots(figsize=(11, 6.2)); fig.subplots_adjust(left=0.24, right=0.97, top=0.80, bottom=0.12)
y = np.arange(len(S)); h = 0.19
for k, (key, lab) in enumerate(keys):
    ax.barh(y + (1.5 - k) * h, [s['pct'][key] for s in S], h, label=lab, color=ISSUE_COLORS[key])
ax.set_yticks(y); ax.set_yticklabels(names); ax.set_xlim(0, 100); ax.set_xlabel('% of crawled pages (HTTP 200)')
ax.grid(axis='y', visible=False); ax.legend(frameon=False, ncol=4, loc='upper left', bbox_to_anchor=(-0.28, 1.1), fontsize=11)
fig.text(0.03, 0.93, 'Share of pages with a basic on-page gap', fontsize=21, fontweight='bold', fontfamily='Space Grotesk')
fig.text(0.03, 0.03, foot, color=MUTED, fontsize=10); save(fig, 'chart_basics.png')
# 3. links
S2 = sorted(D['sites'], key=lambda s: s['counts']['redirecting_internal_urls'] + s['counts']['broken_urls'])
fig, ax = plt.subplots(figsize=(11, 6.2)); fig.subplots_adjust(left=0.24, right=0.95, top=0.82, bottom=0.12)
r = [s['counts']['redirecting_internal_urls'] for s in S2]; b = [s['counts']['broken_urls'] for s in S2]
ax.barh([s['site'] for s in S2], r, color=ORANGE, height=0.62, label='Linked URLs that redirect')
ax.barh([s['site'] for s in S2], b, left=r, color=CORAL, height=0.62, label='Linked URLs that 404')
for i, (rr, bb) in enumerate(zip(r, b)): ax.text(rr + bb + 0.8, i, f'{rr} redirect · {bb} broken', va='center', fontsize=11)
ax.set_xlim(0, 85); ax.set_xlabel('Internal URLs'); ax.grid(axis='y', visible=False); ax.legend(frameon=False, loc='lower right')
fig.text(0.03, 0.93, 'Broken and redirecting internal links', fontsize=21, fontweight='bold', fontfamily='Space Grotesk')
fig.text(0.03, 0.875, 'Only 3 broken URLs across 2,521 pages. Redirects are mostly content moves.', color=MUTED, fontsize=12)
fig.text(0.03, 0.03, foot, color=MUTED, fontsize=10); save(fig, 'chart_links.png')
print('ok')
