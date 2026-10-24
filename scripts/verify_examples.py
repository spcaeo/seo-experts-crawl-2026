#!/usr/bin/env python3
"""Re-fetch every headline example with curl and record status, redirect target and the matching HTML snippet.
Writes data/evidence/curl-log.jsonl, data/verified-examples.csv/.json, data/backlinko-redirects.csv.
Polite: one request at a time, >=1 s apart. Records only status codes, Location targets and short public HTML snippets."""
import subprocess, json, time, re, csv, os, html, datetime
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36 (Toadstone study re-check)'
LOG = open(os.path.join(OUT, 'evidence', 'curl-log.jsonl'), 'w')
_last = [0.0]
def curl(url, follow=False, body=False):
    w = time.time() - _last[0]
    if w < 1.0: time.sleep(1.0 - w)
    _last[0] = time.time()
    cmd = ['curl', '-s', '-A', UA, '--compressed', '-m', '30', '-o', '-' if body else '/dev/null',
           '-w', '\n__META__%{http_code} %{num_redirects} %{redirect_url} %{url_effective}']
    if follow: cmd += ['-L', '--max-redirs', '5']
    cmd.append(url)
    out = subprocess.run(cmd, capture_output=True, text=True, errors='replace').stdout
    page, meta = out.rsplit('\n__META__', 1)
    code, nred, *rest = meta.split(' ')
    redirect_url = rest[0] if len(rest) == 2 else ''; eff = rest[-1]
    rec = {'checked_at_utc': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
           'command': ' '.join(['curl', '-s', '-A', '"<browser UA>"'] + (['-L'] if follow else []) + [url]),
           'url': url, 'http_status': int(code), 'redirects_followed': int(nred), 'location': redirect_url, 'final_url': eff}
    LOG.write(json.dumps(rec) + '\n'); LOG.flush()
    return rec, page
def snippet(page, pattern):
    m = re.search(pattern, page, re.S | re.I)
    return re.sub(r'\s+', ' ', m.group(0))[:300] if m else ''
examples = []
def add(eid, site, claim, url, expected, rec, evidence_url='', snip='', ok=None):
    examples.append({'id': eid, 'site': site, 'claim': claim, 'url': url, 'expected': expected,
                     'observed_status': rec['http_status'], 'observed_location': rec['location'],
                     'evidence_page': evidence_url, 'evidence_snippet': snip,
                     'still_true': ok if ok is not None else '', 'checked_at_utc': rec['checked_at_utc']})
# E1 Backlinko placeholder link
u = 'https://backlinko.com/hidereveal_piece_of_content/interlink'; r, _ = curl(u)
src = 'https://backlinko.com/pillar-pages'; r2, pg = curl(src, follow=True, body=True)
sn = snippet(pg, r'<a[^>]+hidereveal_piece_of_content/interlink[^>]*>.*?</a>')
add('E1', 'backlinko.com', 'Placeholder link inside an article points to a URL that returns 404', u, 404, r, src, sn, r['http_status'] == 404 and bool(sn))
# E2 Backlinko redirects (first hop + final)
rows = []
for line in open(os.path.join(os.path.dirname(OUT), 'scripts', 'backlinko_redirect_urls.txt')):
    u = line.strip()
    if not u: continue
    a, _ = curl(u); b, _ = curl(u, follow=True)
    rows.append({'url': u, 'first_status': a['http_status'], 'first_location': a['location'], 'hops': b['redirects_followed'],
                 'final_url': b['final_url'], 'final_status': b['http_status'],
                 'goes_to_searchengineland': int('searchengineland.com' in b['final_url']), 'checked_at_utc': a['checked_at_utc']})
with open(os.path.join(OUT, 'backlinko-redirects.csv'), 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
n_red = sum(1 for x in rows if x['first_status'] in (301, 302, 307, 308)); n_sel = sum(x['goes_to_searchengineland'] for x in rows)
examples.append({'id': 'E2', 'site': 'backlinko.com', 'claim': f'{n_red} of {len(rows)} internally linked URLs redirect; {n_sel} end on searchengineland.com',
                 'url': 'data/backlinko-redirects.csv', 'expected': '301/308', 'observed_status': f'{n_red} redirecting', 'observed_location': '',
                 'evidence_page': '', 'evidence_snippet': '', 'still_true': n_red > 0, 'checked_at_utc': rows[-1]['checked_at_utc']})
# E3 Moz Local SEO 404 + sources
u = 'https://moz.com/learn/seo/what-is-local-search-marketing-seo'; r, _ = curl(u)
srcs = ['what-is-seo', 'international-seo', 'serp-features', 'off-site-seo', 'search-engine-marketing', 'conversion-rate-optimization', 'role-of-seo-in-digital-marketing']
hits = []
for s in srcs:
    su = 'https://moz.com/learn/seo/' + s; rr, pg = curl(su, follow=True, body=True)
    sn = snippet(pg, r'<a[^>]+what-is-local-search-marketing-seo[^>]*>.*?</a>')
    if sn: hits.append(su)
add('E3', 'moz.com', f'Link to Moz\'s local search marketing guide returns 404; link found on {len(hits)} of 7 Learn Center pages re-checked', u, 404, r, ' '.join(hits),
    snippet(pg, r'<a[^>]+what-is-local-search-marketing-seo[^>]*>.*?</a>') or '', r['http_status'] == 404 and len(hits) > 0)
# E3b Moz redirect
u = 'https://moz.com/blog/how-to-view-website-as-googlebot'; r, _ = curl(u)
add('E3b', 'moz.com', 'Internally linked blog URL 301s to its renamed version', u, 301, r, ok=r['http_status'] in (301, 308))
# E4 Moz missing meta description
u = 'https://moz.com/learn/seo/google-eat'; r, pg = curl(u, follow=True, body=True)
has = bool(re.search(r'<meta[^>]+name=["\']description["\']', pg, re.I))
r2, pg2 = curl('https://moz.com/learn/seo/what-is-seo', follow=True, body=True)
sib = snippet(pg2, r'<meta[^>]+name=["\']description["\'][^>]*>')
add('E4', 'moz.com', 'Page has no <meta name="description"> while sibling /learn/seo/what-is-seo has one', u, 'no meta description', r,
    'https://moz.com/learn/seo/what-is-seo', 'sibling: ' + sib, (not has) and r['http_status'] == 200 and bool(sib))
# E5 SE Ranking missing image
img = 'https://seranking.com/blog/wp-content/uploads/2026/03/yagmur-simsek-media.png'; r, _ = curl(img)
src = 'https://seranking.com/blog/google-links-in-ai-mode-answers/'; r2, pg = curl(src, follow=True, body=True)
sn = snippet(pg, r'<img[^>]+yagmur-simsek-media\.png[^>]*>')
add('E5', 'seranking.com', 'Embedded image returns 404', img, 404, r, src, sn, r['http_status'] == 404 and bool(sn))
# E6 SER badge without alt
src = 'https://www.seroundtable.com/'; r, pg = curl(src, follow=True, body=True)
sn = snippet(pg, r'<img[^>]+preferred_source_publisher\.webp[^>]*>')
add('E6', 'seroundtable.com', 'Sitewide "preferred source" badge image has no alt attribute (template-level)', src, 'img without alt', r, src, sn, bool(sn) and 'alt=' not in sn.lower())
# E7 Ahrefs chart without alt
src = 'https://ahrefs.com/blog/query-fan-out-chatgpt/'; r, pg = curl(src, follow=True, body=True)
sn = snippet(pg, r'<img[^>]+qfo-fanouts-per-response\.png[^>]*>')
add('E7', 'ahrefs.com', 'Article chart image has no alt attribute', src, 'img without alt', r, src, sn, bool(sn) and not re.search(r'\salt=["\'][^"\']+', sn))
json.dump(examples, open(os.path.join(OUT, 'verified-examples.json'), 'w'), indent=1)
with open(os.path.join(OUT, 'verified-examples.csv'), 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(examples[0])); w.writeheader(); w.writerows(examples)
for e in examples: print(e['id'], e['still_true'], e['observed_status'], e['claim'][:90], '|', e['evidence_snippet'][:140])
