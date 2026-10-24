#!/usr/bin/env python3
"""Render docs/index.html from data/ (every number on the page comes from the data files).
Usage: python scripts/build_page.py [--base https://spcaeo.github.io/seo-experts-crawl-2026/]"""
import csv, json, os, sys, html, shutil, re as _re
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
BASE = sys.argv[sys.argv.index('--base') + 1] if '--base' in sys.argv else 'https://spcaeo.github.io/seo-experts-crawl-2026/'
OUT = sys.argv[sys.argv.index('--out') + 1] if '--out' in sys.argv else os.path.join(R, 'docs/index.html')
REPO = 'https://github.com/spcaeo/seo-experts-crawl-2026'
TOOL = 'https://spcaeo.github.io/toadstone/'; TOOL_REPO = 'https://github.com/spcaeo/toadstone'
DATE = '2026-10-23'; STAMP = os.environ.get('PAGE_STAMP', '2026-10-23T20:00:00-04:00')  # set PAGE_STAMP=<ISO time> if you redeploy later
import datetime as _dt
UPD = _dt.datetime.fromisoformat(STAMP).strftime('%-d %B %Y')
e = html.escape
sites = list(csv.DictReader(open(os.path.join(R, 'data/sites.csv'))))
D = json.load(open(os.path.join(R, 'docs/data/study.json')))
EX = {x['id']: x for x in json.load(open(os.path.join(R, 'data/verified-examples.json')))}
BL = list(csv.DictReader(open(os.path.join(R, 'data/backlinko-redirects.csv'))))
T = D['totals']; I = lambda s, k: int(s[k])
counted = {s['site']: s['counted_issues'] for s in D['sites']}
by = {s['site']: s for s in sites}
tot = lambda k: sum(I(s, k) for s in sites)
n_sel = sum(1 for b in BL if b['goes_to_searchengineland'] == '1')
ser = by['seroundtable.com']; sem = by['semrush.com']
assert T['broken'] == tot('broken_urls') == 3 and len(BL) == 66 and n_sel == 56
broken_sites = [s['site'] for s in sites if I(s, 'broken_urls')]
clean_pages = sum(s['grid'].count('0') for s in D['sites'])
total_counted = sum(counted.values())
# copy downloadable data into docs/ so Pages serves it
for f in ('sites.csv', 'sites.json', 'pages.csv', 'excluded-flags.csv', 'verified-examples.csv', 'verified-examples.json', 'backlinko-redirects.csv', 'DATA-DICTIONARY.md'):
    p = os.path.join(R, 'data', f)
    if os.path.exists(p): shutil.copy(p, os.path.join(R, 'docs/data', f))
def kb(f):
    p = os.path.join(R, 'docs/data', f); return f"{os.path.getsize(p)/1024:,.0f} KB" if os.path.exists(p) else ''

cols = [('site', 'Site'), ('html_pages_200', 'Pages'), ('counted', 'Counted issues'), ('per100', 'Per 100 pages'),
        ('missing_meta_description', 'No meta'), ('missing_canonical', 'No canonical'), ('missing_h1', 'No H1'), ('multiple_h1', '2+ H1'),
        ('pages_content_img_no_alt', 'Img no alt'), ('broken_urls', 'Broken'), ('redirecting_internal_urls', 'Redirects'), ('blocked_not_counted', 'Blocked (not counted)')]
rows = []
for s in sorted(sites, key=lambda s: counted[s['site']] / I(s, 'html_pages_200')):
    c = counted[s['site']]; p = I(s, 'html_pages_200'); cells = []
    for k, _ in cols:
        if k == 'site': cells.append(f'<th scope="row">{e(s["site"])}</th>'); continue
        v = {'counted': c, 'per100': round(c * 100 / p, 1)}.get(k, s.get(k))
        v = float(v) if k == 'per100' else int(v)
        cls = ' class="zero"' if v == 0 else (' class="hi"' if k == 'counted' and v >= 100 else '')
        cells.append(f'<td data-v="{v}"{cls}>{v:,}</td>' if k != 'per100' else f'<td data-v="{v}"{cls}>{v:.1f}</td>')
    rows.append('<tr>' + ''.join(cells) + '</tr>')
thead = ''.join(f'<th scope="col" data-k="{k}"><button type="button">{e(l)}</button></th>' for k, l in cols)
tfoot = (f'<tr><th scope="row">All 10 sites</th><td>{T["pages"]:,}</td><td>{total_counted:,}</td><td>{total_counted*100/T["pages"]:.1f}</td>' +
         ''.join(f'<td>{tot(k):,}</td>' for k in ('missing_meta_description', 'missing_canonical', 'missing_h1', 'multiple_h1', 'pages_content_img_no_alt', 'broken_urls', 'redirecting_internal_urls', 'blocked_not_counted')) + '</tr>')

def et(u):
    h, m = int(u[11:13]), u[14:16]; return f'{(h-4)%24:02d}:{m}'

def ex(id_, title, body, pill, pillcls=''):
    x = EX[id_]; snip = x['evidence_snippet']
    url = x['url'] if x['url'].startswith('http') else ''
    return f'''<article class="ex reveal"><div class="site">{e(x["site"])} · {e(id_)}</div><h3>{title}</h3><p>{body}</p>
<div><span class="pill {pillcls}">{e(pill)}</span> <span class="note">re-checked with curl at {et(x["checked_at_utc"])} ET, 23 Oct 2026</span></div>
{f'<code>{e(url)}</code>' if url else ''}{f'<pre>{e(snip[:260])}{"…" if len(snip) > 260 else ""}</pre>' if snip else ''}</article>'''
examples = ''.join([
    ex('E1', 'A placeholder link that slipped through', 'On <a href="https://backlinko.com/pillar-pages" rel="nofollow noopener">/pillar-pages</a>, the anchor “strong network of internal links” points at a URL that looks like a page-builder placeholder. It returns 404. Ironic, and very human.', 'HTTP 404'),
    ex('E2', f'{len(BL)} links that take a detour', f'Every one of the {len(BL)} internal URLs we found redirecting on Backlinko does so with a 301/308; {n_sel} end on sister site searchengineland.com (both sites are owned by Semrush, so this looks like content moving between sister brands). Not broken, just an extra hop. Full list in <a href="data/backlinko-redirects.csv">backlinko-redirects.csv</a>.', f'{len(BL)} × 301/308', 'warn'),
    ex('E3', 'One guide link, seven pages', 'Seven Moz Learn Center pages link to “Local Search Marketing” at a URL that now returns 404, probably a renamed guide. One template-level fix clears all seven.', 'HTTP 404'),
    ex('E4', 'Sibling pages, different metadata', 'Moz’s <code>/learn/seo/google-eat</code> has no meta description, while its sibling <code>/learn/seo/what-is-seo</code> has a well-written one. Across Moz, 90 pages (59 distinct paths) lack one.', 'no meta description', 'warn'),
    ex('E5', 'A lazy-loaded image that is not there', 'An author photo on an SE Ranking article is lazy-loaded via <code>data-lazy-src</code> and returns 404, so readers see an empty circle.', 'HTTP 404'),
    ex('E6', 'One badge, 294 pages', f'Search Engine Roundtable’s sitewide “preferred source” badge has no <code>alt</code>. That single template line accounts for 294 of its 298 counted issues. Add one attribute and the site is near-perfect.', 'no alt attribute', 'warn'),
    ex('E7', 'A chart without words', 'An Ahrefs chart (<code>qfo-fanouts-per-response.png</code>) has width, height and lazy-loading, everything except alt text. Charts are exactly where screen-reader users need it.', 'no alt attribute', 'warn'),
])
title = 'Audit the Experts: 10 SEO Sites Crawled (2026 Study)'
desc = f'We politely crawled {T["pages"]:,} pages on Moz, Ahrefs, Semrush, Backlinko, Yoast and 5 more SEO sites. Mostly spotless: {T["broken"]} broken URLs. Open data, CC BY 4.0.'
ld = [{
  '@context': 'https://schema.org', '@type': 'Dataset', 'name': 'SEO experts crawl 2026: technical SEO basics on 10 SEO websites',
  'description': f'Public page metadata from a polite ~300-page crawl of 10 well-known SEO websites on {DATE}: HTTP status, title/meta/canonical/H1 presence, images without alt, broken and redirecting internal links. {T["urls"]:,} URLs, {T["pages"]:,} HTML pages.',
  'url': BASE, 'sameAs': REPO, 'license': 'https://creativecommons.org/licenses/by/4.0/', 'isAccessibleForFree': True,
  'creator': {'@type': 'Person', 'name': 'Rakesh Patel', 'url': 'https://github.com/spcaeo'},
  'temporalCoverage': DATE, 'datePublished': STAMP, 'dateModified': STAMP,
  'keywords': ['technical SEO', 'site audit', 'crawl data', 'meta description', 'canonical', 'alt text', 'broken links'],
  'variableMeasured': ['HTTP status', 'meta description present', 'canonical present', 'H1 present', 'images without alt', 'links to broken URLs', 'links to redirecting URLs'],
  'measurementTechnique': 'Toadstone crawler, max 300 URLs per site, max 2 requests/second, robots.txt respected',
  'distribution': [{'@type': 'DataDownload', 'encodingFormat': 'text/csv', 'name': n, 'contentUrl': BASE + 'data/' + n} for n in ('sites.csv', 'pages.csv', 'verified-examples.csv', 'backlinko-redirects.csv')]
}, {
  '@context': 'https://schema.org', '@type': 'Article', 'headline': 'We audited 10 of the best-known SEO sites. They are mostly spotless.',
  'description': desc, 'image': [BASE + 'og-image.png'], 'datePublished': STAMP, 'dateModified': STAMP, 'url': BASE, 'mainEntityOfPage': BASE,
  'author': {'@type': 'Person', 'name': 'Rakesh Patel', 'url': 'https://github.com/spcaeo'},
  'publisher': {'@type': 'Organization', 'name': 'Toadstone', 'url': TOOL}
}]
media = 'media/'
page = f'''<!doctype html>
<html lang="en" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{BASE}">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; media-src 'self'; connect-src 'self'; font-src 'self'; object-src 'none'; base-uri 'self'; form-action 'none'">
<meta name="referrer" content="strict-origin-when-cross-origin">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta name="author" content="Rakesh Patel">
<meta name="theme-color" content="#0d1411">
<meta name="color-scheme" content="dark">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="assets/site.css">
<link rel="sitemap" type="application/xml" href="sitemap.xml">
<meta property="og:type" content="article">
<meta property="og:site_name" content="Toadstone study">
<meta property="og:title" content="We audited 10 of the best-known SEO sites. They're mostly spotless.">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{BASE}">
<meta property="og:image" content="{BASE}og-image.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="We crawled 10 of the best-known SEO sites: {T['pages']:,} pages, {T['broken']} broken URLs.">
<meta property="og:locale" content="en_US">
<meta property="article:published_time" content="{STAMP}">
<meta property="article:modified_time" content="{STAMP}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="We audited 10 of the best-known SEO sites. They're mostly spotless.">
<meta name="twitter:description" content="{e(desc)}">
<meta name="twitter:image" content="{BASE}og-image.png">
<meta name="twitter:image:alt" content="We crawled 10 of the best-known SEO sites: {T['pages']:,} pages, {T['broken']} broken URLs.">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<script src="assets/app.js" defer></script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="top"><div class="wrap"><a class="brand" href="{BASE}">Audit the <span>experts</span></a>
<nav class="links" aria-label="Sections"><a href="#grid">Health grid</a><a href="#charts">Charts</a><a href="#sites">Per-site table</a><a href="#examples">Examples</a><a href="methodology.html">Method</a><a href="faq.html">FAQ</a><a href="#data">Data</a></nav>
<a class="btn sm" href="#run">Audit your site</a></div></header>
<main id="main">
<section class="hero" aria-labelledby="h1">
<canvas id="crawl" aria-hidden="true"></canvas>
<div class="wrap">
<p class="kicker">Crawl study · data from 23 Oct 2026</p>
<h1 id="h1">We audited 10 of the best-known SEO sites. They're <em>mostly spotless.</em></h1>
<p class="lede">A polite, ~300-page crawl of each of Moz, Ahrefs, Semrush, Backlinko, Yoast, Search Engine Journal, Search Engine Roundtable, SE Ranking, Surfer and Neil Patel. Here is what even the experts occasionally miss, every example re-checked by hand, and every row of data free to download.</p>
<div class="cta-row"><a class="btn" href="#run">Run the same audit on your site</a><a class="btn ghost" href="{REPO}">Get the data on GitHub</a></div>
<ul class="stats">
<li class="stat"><b data-count="{T['pages']}">{T['pages']:,}</b><span>HTML pages checked across 10 sites ({T['urls']:,} URLs in total)</span></li>
<li class="stat good"><b data-count="{T['broken']}">{T['broken']}</b><span>broken internal URLs in the whole study. No site had more than one.</span></li>
<li class="stat"><b data-count="{I(ser, 'pages_content_img_no_alt')}">{I(ser, 'pages_content_img_no_alt')}</b><span>pages affected by one template line: a badge without alt text</span></li>
<li class="stat good"><b data-count="{counted['semrush.com']}">{counted['semrush.com']}</b><span>counted issues on {I(sem, 'html_pages_200')} Semrush blog pages. Spotless.</span></li>
</ul></div></section>

<section id="grid" aria-labelledby="grid-h"><div class="wrap">
<h2 id="grid-h" class="reveal">The crawl, page by page</h2>
<p class="sub reveal">Each cell is one page, in the order our crawler reached it. Green means none of our counted checks fired; amber gets brighter with each gap; red is a broken URL. {clean_pages:,} of {T['pages']:,} pages ({clean_pages*100/T['pages']:.0f}%) are fully green. Hover or tab onto a cell for details.</p>
<div class="panel reveal"><div id="hg"><p class="note">The interactive grid needs JavaScript. The same data is in the table below and in <a href="data/pages.csv">pages.csv</a>.</p></div>
<div class="legend" aria-hidden="true"><span><i class="c0"></i>no counted gap</span><span><i class="c1"></i>1 gap</span><span><i class="c2"></i>2 gaps</span><span><i class="c3"></i>3+ gaps</span><span><i class="cB"></i>broken URL</span><span>% = share of pages with no gap</span></div></div>
</div></section>

<section id="charts" aria-labelledby="charts-h"><div class="wrap">
<h2 id="charts-h" class="reveal">Where the gaps are</h2>
<p class="sub reveal">Counted issues per 100 pages, stacked by type. Toggle a type off to see how the order changes: switch off “Content image without alt” and Search Engine Roundtable drops from first to near the bottom.</p>
<div class="panel reveal"><div class="toggles" id="stacked-toggles" role="group" aria-label="Issue types to include"></div><div id="stacked"></div></div>
<div class="mt">
<div class="panel reveal"><h3>Heatmap: site × issue</h3><p class="note">Number of affected pages; colour strength is the share of the site's pages.</p><div id="heat"></div></div>
<div class="panel reveal mt"><h3>Issues pile up (or don't) as the crawl goes on</h3><p class="note">Cumulative counted issues vs pages crawled. Flat lines are clean sites; steep ones are template-level patterns. Toggle sites below.</p><div class="toggles" id="race-toggles" role="group" aria-label="Sites to show"></div><div id="race"></div></div>
</div>
<div class="media-grid mt">
<figure class="reveal"><video data-lazy muted autoplay loop playsinline preload="none" poster="{media}race-poster.jpg" width="1080" height="1080" aria-label="Animated bar chart race: cumulative counted issues per site as the crawl progresses, from 0 to 300 pages. Captions are burned in."><source src="{media}issues-race.mp4" type="video/mp4"><track kind="captions" src="{media}issues-race.vtt" srclang="en" label="English (same as burned-in)"></video>
<figcaption>The crawl as a race: cumulative counted issues per site, page by page. 30 seconds, no audio.</figcaption></figure>
<figure class="media reveal"><img src="{media}chart_issues_per_page.png" width="1210" height="682" decoding="async" alt="Bar chart of counted issues per crawled page. Search Engine Roundtable 0.99 (294 of them one sitewide badge), Moz 0.39, Yoast 0.35, Backlinko 0.33, Ahrefs 0.31, Search Engine Journal 0.15, SE Ranking 0.09, Surfer 0.04, Neil Patel 0.00, Semrush 0.00.">
<figcaption>Static version for sharing. <a href="{media}chart_basics.png">Basics chart</a> · <a href="{media}chart_links.png">Links chart</a></figcaption></figure>
</div></div></section>

<section id="sites" aria-labelledby="sites-h"><div class="wrap">
<h2 id="sites-h" class="reveal">Every site, every number</h2>
<p class="sub reveal">Sorted cleanest first. Click a column to sort. “Counted issues” adds up the columns from <em>No meta</em> to <em>Redirects</em>; the last column is shown for transparency and never counted.</p>
<div class="tablewrap reveal"><table id="sites-table"><caption class="note">Pages = HTML pages that returned 200 within each site's crawl scope. Broken = 404/410/5xx only. Blocked (401/403/429/no response) URLs are bot walls and are not counted as errors.</caption>
<thead><tr>{thead}</tr></thead><tbody>{''.join(rows)}</tbody><tfoot>{tfoot}</tfoot></table></div>
<p id="sort-status" class="note" aria-live="polite"></p>
</div></section>

<section id="examples" aria-labelledby="examples-h"><div class="wrap">
<h2 id="examples-h" class="reveal">Seven examples, each re-checked by hand</h2>
<p class="sub reveal">We re-requested every headline example with curl, one request at a time, about an hour after the crawl. All seven still held. The full log is in <a href="{REPO}/blob/main/data/evidence/curl-log.jsonl">data/evidence/curl-log.jsonl</a>. We share these because they are useful, not because anyone did anything wrong: each one is a single-line fix.</p>
<div class="examples">{examples}</div>
</div></section>

<section id="not-counted" aria-labelledby="nc-h"><div class="wrap grid2">
<div class="reveal"><h2 id="nc-h">What we didn't count, and why</h2>
<ul class="clean">
<li><b>{T['blocked_not_counted']} bot-walled URLs</b> (403 and similar, mostly on Moz and Backlinko). A firewall saying no to a crawler is not a broken page.</li>
<li><b>Long titles</b> ({tot('title_over_60_chars'):,} pages over 60 characters). Google rewrites titles anyway; it is a style choice, not an error.</li>
<li><b>Near-duplicate pages</b> ({sum(s['near_dup'] for s in D['sites']):,}) and <b>cross-domain canonicals</b> (e.g. SEJ's syndicated posts). Usually intentional.</li>
<li><b>Tracking pixels and 1×1 images</b> without alt. They are not content.</li>
<li><b>Anything outside each site's blog/learn scope</b>, and anything behind a login. Every exclusion is listed in <a href="data/excluded-flags.csv">excluded-flags.csv</a>.</li>
</ul></div>
<div class="reveal"><h2>The honest caveats</h2>
<ul class="clean"><li>~300 pages is a sample, not a full audit. A different crawl order would find slightly different pages.</li>
<li>Toadstone is our tool. We built it, so we have a reason to want it to find things. That is why every rule, script and row is public.</li>
<li>These are some of the best-run sites on the web. {T['pages']:,} pages with {T['broken']} broken URLs is a seriously high bar, and the patterns here are the ones every large site has.</li></ul></div>
</div></section>

<section id="method" aria-labelledby="method-h"><div class="wrap">
<h2 id="method-h" class="reveal">Method</h2>
<div class="grid2">
<div class="panel reveal"><ul class="clean">
<li><b>When:</b> crawls ran 23 Oct 2026, about 18:50–19:27 ET; examples re-verified 19:45–19:48 ET.</li>
<li><b>How much:</b> up to 300 URLs per site, depth 5, starting from each site's blog or learn hub.</li>
<li><b>How politely:</b> at most 2 requests per second per site, 0.5 s delay, concurrency 2, robots.txt respected, no logins, no cookies kept.</li>
<li><b>Who:</b> <code class="mono">ToadstoneBot/1.0 (+https://github.com/spcaeo/toadstone; polite research crawl, &lt;=2 req/s)</code></li>
<li><b>What we kept:</b> public page metadata only (status, title/meta/canonical/H1 presence, image alt counts, link status). No page text, headers or cookies.</li></ul></div>
<div class="panel reveal"><h3>Counting rules</h3><ul class="clean">
<li>Page checks apply only to HTML pages that returned 200.</li>
<li>Broken = 404, 410 or 5xx. 401/403/429 and timeouts are “blocked, not counted”.</li>
<li>Counted issues = no meta description + no canonical + no H1 + more than one H1 + pages with a content image missing alt + broken URLs + internally linked URLs that redirect.</li>
<li>Full definitions: <a href="data/DATA-DICTIONARY.md">DATA-DICTIONARY.md</a> and the <a href="methodology.html">full methodology page</a> (every exclusion, reproduce commands). Questions? See the <a href="faq.html">FAQ</a>.</li></ul></div>
</div></div></section>

<section id="run" aria-labelledby="run-h"><div class="wrap"><div class="cta reveal">
<h2 id="run-h">Run the same audit on your site in 5 minutes</h2>
<p class="sub tight">Toadstone is free, self-hosted, source-available (Elastic License 2.0). It runs on your machine, so your crawl data stays with you.</p>
<div class="media-grid">
<div><ol class="steps">
<li>Install Toadstone from <a href="{TOOL_REPO}">github.com/spcaeo/toadstone</a>.</li>
<li>Run the quick audit against your site:<pre class="cmd">./quick_audit.sh https://your-site.example/</pre></li>
<li>Read the three plain-English bullets it prints, then open the full report for the details.</li></ol>
<div class="cta-row"><a class="btn" href="{TOOL}">Get Toadstone</a><a class="btn ghost" href="{REPO}">Reproduce this study</a></div></div>
<figure><video data-lazy muted autoplay loop playsinline preload="none" poster="{media}terminal-poster.jpg" width="1280" height="720" aria-label="Terminal recording: quick_audit.sh crawls a small sample site and prints three bullets: 1 internal URL returns 404, 1 linked URL redirects, 2 pages share a duplicate title."><source src="{media}quick-audit-terminal.mp4" type="video/mp4"></video>
<figcaption>quick_audit.sh on a deliberately broken 7-page sample site (sped up). It prints three bullets.</figcaption></figure>
</div></div></div></section>

<section id="data" aria-labelledby="data-h"><div class="wrap">
<h2 id="data-h" class="reveal">Download the data</h2>
<p class="sub reveal">Licensed CC BY 4.0: use it, chart it, disagree with it. Please credit “Toadstone SEO experts crawl 2026”. Scripts are MIT.</p>
<div class="dl reveal">
<a href="data/sites.csv"><b>sites.csv</b><span>One row per site, all totals ({kb('sites.csv')})</span></a>
<a href="data/sites.json"><b>sites.json</b><span>Same, as JSON ({kb('sites.json')})</span></a>
<a href="data/pages.csv"><b>pages.csv</b><span>{T['urls']:,} URLs with status and per-page checks ({kb('pages.csv')})</span></a>
<a href="data/verified-examples.csv"><b>verified-examples.csv</b><span>The seven examples and their curl results</span></a>
<a href="data/backlinko-redirects.csv"><b>backlinko-redirects.csv</b><span>All {len(BL)} redirect hops, verified</span></a>
<a href="data/excluded-flags.csv"><b>excluded-flags.csv</b><span>What we chose not to count, and why</span></a>
<a href="data/DATA-DICTIONARY.md"><b>DATA-DICTIONARY.md</b><span>Every column explained</span></a>
<a href="{REPO}"><b>GitHub repo</b><span>Scripts, charts, evidence log, story</span></a>
</div></div></section>
</main>
<footer><div class="wrap">
<p><b>Disclosure:</b> Toadstone is our tool; this study was run by its maker, Rakesh Patel. If you run one of these sites and something here is out of date, open an issue on <a href="{REPO}/issues">GitHub</a> and we will update it quickly.</p>
<p>Data and text CC BY 4.0 · Code MIT · Crawled <time datetime="{DATE}">23 October 2026</time> · <a href="methodology.html">Method</a> · <a href="faq.html">FAQ</a></p>
</div></footer>
<div id="tip" role="tooltip"></div>
</body></html>
'''
open(OUT, 'w').write(page)
print('wrote', OUT, len(page), 'bytes')

# ---------- methodology page (second page: full rules, exclusions, reproduce commands) ----------
INCL = {'semrush.com': r'^https://www\.semrush\.com/blog', 'surfer.ai': r'^https://surfer\.ai/blog', 'neilpatel.com': r'^https://neilpatel\.com/blog',
        'ahrefs.com': r'^https://ahrefs\.com/blog', 'searchenginejournal.com': '', 'yoast.com': r'^https://yoast\.com/', 'seranking.com': r'^https://seranking\.com/blog',
        'seroundtable.com': '', 'backlinko.com': '', 'moz.com': r'^https://moz\.com/(learn|blog)'}
excl = list(csv.DictReader(open(os.path.join(R, 'data/excluded-flags.csv'))))
m_title = 'Methodology: how we crawled 10 SEO sites'
m_desc = 'How we crawled 10 SEO sites politely (2 requests/second), what we counted, every flag we excluded, and the commands to reproduce it.'
MURL = BASE + 'methodology.html'
cmds = '\n'.join(f"python scripts/ts_crawl.py {s['start_url']} raw/{s['site']}.json --max 300 --delay 0.5 --concurrency 2 --rps 2 --depth 5 --timeout 1500" + (f" --include '{INCL[s['site']]}'" if INCL[s['site']] else '') for s in sites)
erows = ''.join(f"<tr><th scope=\"row\">{e(x['site'])}</th><td>{e(x['toadstone_check'])}</td><td>{e(x['raw_flags'])}</td><td class=\"why\">{e(x['why_not_counted'])}</td></tr>" for x in excl)
mld = {'@context': 'https://schema.org', '@type': 'TechArticle', 'headline': m_title, 'description': m_desc, 'url': MURL, 'mainEntityOfPage': MURL,
       'datePublished': STAMP, 'dateModified': STAMP, 'image': [BASE + 'og-image.png'], 'isPartOf': {'@type': 'WebSite', 'name': 'Toadstone study', 'url': BASE},
       'author': {'@type': 'Person', 'name': 'Rakesh Patel', 'url': 'https://github.com/spcaeo'}, 'publisher': {'@type': 'Organization', 'name': 'Toadstone', 'url': TOOL}}
def shell(title, desc, url, ld, kicker, h1, lede, body):
    ldj = json.dumps(ld, ensure_ascii=False)
    alt = f"We crawled 10 of the best-known SEO sites: {T['pages']:,} pages, {T['broken']} broken URLs."
    return f'''<!doctype html>
<html lang="en" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; media-src 'self'; connect-src 'self'; font-src 'self'; object-src 'none'; base-uri 'self'; form-action 'none'">
<meta name="referrer" content="strict-origin-when-cross-origin">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta name="author" content="Rakesh Patel">
<meta name="theme-color" content="#0d1411">
<meta name="color-scheme" content="dark">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="assets/site.css">
<link rel="sitemap" type="application/xml" href="sitemap.xml">
<meta property="og:type" content="article">
<meta property="og:site_name" content="Toadstone study">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{BASE}og-image.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{e(alt)}">
<meta property="og:locale" content="en_US">
<meta property="article:published_time" content="{STAMP}">
<meta property="article:modified_time" content="{STAMP}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(title)}">
<meta name="twitter:description" content="{e(desc)}">
<meta name="twitter:image" content="{BASE}og-image.png">
<meta name="twitter:image:alt" content="{e(alt)}">
<script type="application/ld+json">{ldj}</script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="top"><div class="wrap"><a class="brand" href="{BASE}">Audit the <span>experts</span></a>
<nav class="links" aria-label="Sections"><a href="{BASE}#sites">Per-site table</a><a href="methodology.html">Method</a><a href="faq.html">FAQ</a><a href="{BASE}#data">Data</a></nav>
<a class="btn sm" href="{BASE}#run">Audit your site</a></div></header>
<main id="main"><div class="wrap prose">
<p class="kicker">{kicker}</p>
<h1 class="h1s">{h1}</h1>
<p class="lede">{lede}</p>
{body}
</div></main>
<footer><div class="wrap"><p>Data and text CC BY 4.0 · Code MIT · <a href="{BASE}">Home</a> · <a href="methodology.html">Method</a> · <a href="faq.html">FAQ</a> · <a href="{REPO}">GitHub</a></p></div></footer>
</body></html>
'''

mbody = f'''<h2>The crawl</h2>
<ul class="clean"><li>Tool: <a href="{TOOL}">Toadstone</a>, our own crawler (free, self-hosted, source-available under the Elastic License 2.0). Because we built it, we publish every rule so you can check our work.</li>
<li>Date: 23 Oct 2026, roughly 18:50–19:27 ET. Examples re-verified with curl 19:45–19:48 ET.</li>
<li>Limits: up to 300 URLs per site or 25 minutes, whichever came first (four sites hit the time cap, which is why a few have fewer than 300 pages), depth 5, 0.5 s delay, concurrency 2, and a hard global cap of 2 requests per second (including image checks and robots.txt). Sitemaps were not fetched.</li>
<li>robots.txt respected; no logins; no cookies kept.</li>
<li>User agent: <code class="mono">ToadstoneBot/1.0 (+https://github.com/spcaeo/toadstone; polite research crawl, &lt;=2 req/s)</code></li>
<li>Start points: each site's blog or learn hub, or the homepage where there is no hub (see commands below). Scope is the first ~300 URLs the crawler reached, which is a sample, not a census.</li></ul>
<h2>What counts as an issue</h2>
<ul class="clean"><li>Page checks only apply to HTML pages that returned HTTP 200.</li>
<li><b>No meta description</b>, <b>no canonical</b>, <b>no H1</b>, <b>more than one H1</b>: per page.</li>
<li><b>Content image without alt</b>: a page counts once if it has at least one non-decorative image (not a 1×1 pixel or tracker) with no alt attribute. An empty alt (<code class="mono">alt=""</code>) is valid for decorative images and is not flagged.</li>
<li><b>Broken URL</b>: an internal URL returning 404, 410 or any 5xx.</li>
<li><b>Linked URL redirects</b>: an internal URL that returns a 3xx and is linked from another crawled page.</li>
<li><b>Counted issues</b> = the sum of those seven columns. See the <a href="data/DATA-DICTIONARY.md">data dictionary</a>.</li></ul>
<h2>What we deliberately did not count</h2>
<ul class="clean"><li>401, 403, 429 and no-response URLs ({T['blocked_not_counted']} in total): bot walls, not errors.</li>
<li>Titles over 60 characters, near-duplicate pages, cross-domain canonicals: informational columns only.</li>
<li>Flags Toadstone raised that we replaced with a stricter recount or judged to be false positives. Every one is below and in <a href="data/excluded-flags.csv">excluded-flags.csv</a>.</li></ul>
<div class="tablewrap"><table class="plain"><caption class="note">Toadstone flags excluded from the counts, with the reason</caption><thead><tr><th scope="col">Site</th><th scope="col">Toadstone check</th><th scope="col">Raw flags</th><th scope="col">Why not counted</th></tr></thead><tbody>{erows}</tbody></table></div>
<h2>Reproduce it</h2>
<p>You need a local Toadstone checkout and Python. Run each crawl (about 5–25 minutes each at 2 requests/second), then build the data and charts from the raw JSON. The raw JSON includes page text, so we do not publish it; the cleaned data is in the repo.</p>
<pre class="cmd">{e(cmds)}
python scripts/build_data.py raw/
python scripts/verify_examples.py
python scripts/build_web_data.py && python scripts/make_charts.py && python scripts/build_page.py</pre>
<p>Found a mistake? <a href="{REPO}/issues">Open an issue</a>. If you run one of these sites and want a row updated or removed, we will do it quickly.</p>
'''
mpage = shell(m_title, m_desc, MURL, mld, 'Methodology · 23 Oct 2026', 'How we crawled 10 SEO sites, and what we did and didn\'t count',
              f'Short version: polite crawls, conservative rules, every exclusion shown. <a href="{BASE}">Back to the results</a> or read the <a href="faq.html">FAQ</a>.', mbody)
open(os.path.join(os.path.dirname(OUT), 'methodology.html'), 'w').write(mpage)
FURL = BASE + 'faq.html'
f_title = 'FAQ: the 2026 SEO experts crawl'
f_desc = 'Answers about the 2026 crawl of 10 SEO sites: who we crawled, what we counted, how to reuse the data, and how to audit your own site.'
FAQ = [('Which sites did you crawl?', 'Semrush, Surfer, Neil Patel, Ahrefs, Search Engine Journal, Yoast, SE Ranking, Search Engine Roundtable, Backlinko and Moz. The first ~300 URLs the crawler reached on each, mostly blog and learn pages.'), ('Were these sites bad at SEO?', 'No. They were mostly excellent: most pages had a meta description, canonical and a single H1. We are showing the few places where even careful teams slip, because it is useful to see what slips through.'), ('Why do the numbers differ from a raw Toadstone report?', 'We counted conservatively. 403 and 429 answers to a bot are bot walls, not broken pages, so we did not count them. The <a href="methodology.html">methodology page</a> lists every flag we excluded and why.'), ('Is Toadstone free?', 'Yes. Toadstone is free, self-hosted and source-available under the Elastic License 2.0. It is our own tool, so we publish the rules and the data to let you check our work.'), ('Can I reuse the data?', 'Yes. The data and text are CC BY 4.0, so please credit the study and link back. The scripts are MIT licensed.'), ('Can I audit my own site the same way?', 'Yes: clone Toadstone and run its quick audit script against your URL. It crawls up to 200 pages at 2 requests a second or less and prints the three issues most worth fixing.'), ('What if one of these sites wants a row corrected or removed?', 'Open an issue on the repo and we will fix it quickly. Every figure is re-checkable with the curl evidence in the data folder.')]
fld = {'@context': 'https://schema.org', '@type': 'FAQPage', 'url': FURL, 'datePublished': STAMP, 'dateModified': STAMP, 'mainEntity': [
    {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in [(q, _re.sub(r'<[^>]+>', '', a)) for q, a in FAQ]]}
fbody = ''.join(f'<h2>{q}</h2><p>{a}</p>' for q, a in FAQ)
fpage = shell(f_title, f_desc, FURL, fld, 'FAQ · 23 Oct 2026', 'Frequently asked questions',
              f'Quick answers. The full detail is on the <a href="methodology.html">methodology page</a>, and the numbers are on the <a href="{BASE}">results page</a>.', fbody)
open(os.path.join(os.path.dirname(OUT), 'faq.html'), 'w').write(fpage)
open(os.path.join(os.path.dirname(OUT), 'sitemap.xml'), 'w').write(f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>{BASE}</loc><lastmod>{STAMP}</lastmod></url>
  <url><loc>{MURL}</loc><lastmod>{STAMP}</lastmod></url>
  <url><loc>{FURL}</loc><lastmod>{STAMP}</lastmod></url>
</urlset>
''')
open(os.path.join(os.path.dirname(OUT), 'robots.txt'), 'w').write(f'User-agent: *\nAllow: /\n\nSitemap: {BASE}sitemap.xml\n')
print('wrote methodology + sitemap + robots')
