#!/usr/bin/env python3
"""Turn a ts_crawl.py JSON into conservative per-site metrics + examples.
Rules (to stay fair to the site):
 * page-level checks only count on HTML pages that returned 200 to us;
 * 'broken' means a crawled internal URL/image that returned 404/410/5xx; 401/403/429/0 (bot walls, WAFs,
   signed CDN URLs) are NOT counted as broken;
 * 'missing alt' ignores 1x1 tracking pixels and non-content images (Toadstone's own is_probably_content flag
   is reported separately)."""
import json, sys, ast, collections
from urllib.parse import urlparse
def v(x):
    if isinstance(x, str) and x[:1] in '[{(' :
        try: return ast.literal_eval(x)
        except Exception: return x
    if x in ('None',): return None
    return x
def sc(p):
    try: return int(p.get('status_code'))
    except Exception: return 0
TRACK = ('facebook.com/tr', 'px.ads.linkedin', 'doubleclick', 'google-analytics', 'bat.bing', 't.co/', 'analytics.twitter')
CHECKS = {'missing_meta': ['missing_meta_description'], 'duplicate_meta': ['duplicate_meta_description'],
          'duplicate_title': ['duplicate_title'], 'missing_canonical': ['missing_canonical'],
          'missing_h1': ['missing_h1'], 'multiple_h1': ['multiple_h1'], 'title_too_long': ['title_too_long'],
          'duplicate_content': ['duplicate_content']}
def load(path):
    d = json.load(open(path)); pages = d['pages']
    host = urlparse(d['url']).netloc.replace('www.', '')
    html = [p for p in pages if 'html' in (p.get('content_type') or '')]
    ok = {p['url']: p for p in html if sc(p) == 200}
    m = {'site': host, 'start': d['url'], 'html_pages': len(html), 'ok_pages': len(ok),
         'blocked_or_offsite_403': sum(1 for p in pages if sc(p) in (401, 403, 429)),
         'requests': d.get('http_requests'), 'elapsed_s': round(d.get('elapsed', 0)), 'date': d.get('date'), 'settings': d.get('settings')}
    ex = collections.defaultdict(list)
    # broken internal URLs / images (real 404/410/5xx only)
    broken = [p for p in pages if sc(p) in (404, 410) or 500 <= sc(p) < 600]
    m['broken_urls'] = len(broken)
    for p in broken: ex['broken_urls'].append({'url': p['url'], 'status': sc(p), 'type': p.get('content_type'), 'linked_from': (v(p.get('linked_from')) or [])[:5]})
    # internal links that redirect (and how many redirect off-site)
    rd = [p for p in pages if v(p.get('redirects'))]
    m['redirecting_internal_urls'] = len(rd)
    off = []
    for p in rd:
        chain = v(p.get('redirects')) or []
        last = chain[-1] if chain else {}
        tgt = (last.get('to') or last.get('url') or last.get('location') or '') if isinstance(last, dict) else str(last)
        if tgt and host not in urlparse(tgt).netloc: off.append((p['url'], tgt))
    m['redirects_offsite'] = len(off); ex['redirects'] = [{'url': p['url'], 'redirects': v(p.get('redirects'))} for p in rd[:5]]
    # alt text
    alt_pages, alt_content_pages = [], []
    for u, p in ok.items():
        imgs = v(p.get('images')) or []
        real = [i for i in imgs if isinstance(i, dict) and not i.get('has_alt') and str(i.get('width')) != '1' and str(i.get('height')) != '1'
                and not any(t in (i.get('src') or '') for t in TRACK)]
        if real: alt_pages.append((u, len(real), len(imgs), real[0].get('src')))
        if any(i.get('is_probably_content') for i in real): alt_content_pages.append(u)
    m['pages_img_no_alt'] = len(alt_pages); m['pages_content_img_no_alt'] = len(alt_content_pages)
    ex['alt'] = alt_pages[:5]
    # issue-based page checks
    by = collections.defaultdict(list)
    for i in d['issues']:
        if i.get('url') in ok: by[i['check']].append(i)
    for k, checks in CHECKS.items():
        its = [i for c in checks for i in by.get(c, [])]
        m[k] = len({i['url'] for i in its}); ex[k] = its[:5]
    m['canonical_cross_domain'] = len({i['url'] for i in by.get('canonical_cross_domain', [])})
    ex['canonical_cross_domain'] = by.get('canonical_cross_domain', [])[:5]
    return d, m, ex, by, pages
if __name__ == '__main__':
    d, m, ex, by, pages = load(sys.argv[1])
    print(json.dumps({k: x for k, x in m.items() if k != 'settings'}, indent=1))
    for k, items in ex.items():
        for i in items[:3]:
            print(k, '|', (json.dumps(i, default=str) if not isinstance(i, dict) or 'check' not in i else f"{i['url']} | {(i.get('details') or '')[:120]}")[:300])
