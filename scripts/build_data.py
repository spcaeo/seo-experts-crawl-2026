#!/usr/bin/env python3
"""Build the published datasets in data/ from raw Toadstone crawl JSON (raw files are not published:
they contain full page text and response headers).

Usage: python scripts/build_data.py RAW_DIR
Counting rules are identical to scripts/summarize.py (the script that produced the study numbers)."""
import sys, os, csv, json, collections
from urllib.parse import urlparse
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from summarize import load, v, sc, TRACK, CHECKS
RAW = sys.argv[1] if len(sys.argv) > 1 else 'raw'
OUT = os.path.join(HERE, '..', 'data')
SITES = ['semrush', 'surfer', 'neilpatel', 'ahrefs', 'sej', 'yoast', 'seranking', 'seroundtable', 'backlinko', 'moz']
SCOPE = {'moz.com': 'moz.com/learn/seo + /blog', 'ahrefs.com': 'ahrefs.com/blog', 'semrush.com': 'semrush.com/blog',
         'yoast.com': 'yoast.com (from /seo-blog)', 'neilpatel.com': 'neilpatel.com/blog', 'seranking.com': 'seranking.com/blog',
         'surfer.ai': 'surfer.ai/blog', 'backlinko.com': 'backlinko.com (from homepage)',
         'searchenginejournal.com': 'searchenginejournal.com (from homepage)', 'seroundtable.com': 'seroundtable.com (from homepage)'}
EXCLUDED = {  # Toadstone checks we did not count, and why
  '403_client_error': 'Bot wall / WAF / signed CDN answered 403 to a non-browser. Not a broken page.',
  '401_client_error': 'Signed CDN answered 401 to a HEAD request. Not a broken resource.',
  '429_client_error': 'Rate-limit answer to a bot. Not a broken page.',
  'links_to_broken_urls': 'Toadstone counts 401/403 targets as broken; we recount broken links ourselves using only 404/410/5xx.',
  'canonical_blocked_by_robots': 'Target robots.txt sat behind a Cloudflare challenge (401/403), so the block could not be confirmed.',
  'modified_date_mismatch': 'JSON-LD date vs HTTP Last-Modified is noisy behind CDNs.',
  'canonical_cross_domain': 'Cross-domain canonicals can be correct; reviewed by hand (see per-site note).',
  'images_missing_alt': 'Replaced by our own recount from the image data, which drops tracking pixels and 1x1 images (see pages_content_img_no_alt).',
}
SITE_NOTE = {
  ('searchenginejournal.com', 'canonical_cross_domain'): 'Checked by hand: 4 syndicated guest posts whose canonical points at the author\'s original article. Correct usage.',
  ('yoast.com', 'canonical_cross_domain'): 'Checked by hand: 2 privacy pages canonicalised to the parent company\'s (Newfold) privacy centre. Looks intentional.',
  ('backlinko.com', 'canonical_cross_domain'): 'Fired on the 404 placeholder URL, not on a live page; page checks only apply to 200 pages.',
}
def status_class(code):
    if code == 200: return 'ok'
    if code in (404, 410) or 500 <= code < 600: return 'broken'
    if code in (401, 403, 429): return 'blocked_not_counted'
    if code == 0: return 'no_response_not_counted'
    return 'other'
sites, pages_rows, excluded_rows = [], [], []
for key in SITES:
    d, m, ex, by, pages = load(os.path.join(RAW, key + '.json'))
    site = m['site']
    ok = {p['url'] for p in pages if 'html' in (p.get('content_type') or '') and sc(p) == 200}
    flagged = {k: {i['url'] for c in cs for i in by.get(c, [])} for k, cs in CHECKS.items()}
    xdom = {i['url'] for i in by.get('canonical_cross_domain', [])}
    broken = {p['url'] for p in pages if status_class(sc(p)) == 'broken'}
    redir = {p['url'] for p in pages if v(p.get('redirects'))}
    links_to_broken, links_to_redir = collections.Counter(), collections.Counter()
    for p in pages:
        for src in (v(p.get('linked_from')) or []):
            if p['url'] in broken: links_to_broken[src] += 1
            if p['url'] in redir: links_to_redir[src] += 1
    for p in pages:
        code = sc(p); is_ok = p['url'] in ok; chain = v(p.get('redirects')) or []
        imgs = v(p.get('images')) or [] if is_ok else []
        real = [i for i in imgs if isinstance(i, dict) and not i.get('has_alt') and str(i.get('width')) != '1'
                and str(i.get('height')) != '1' and not any(t in (i.get('src') or '') for t in TRACK)]
        title = (p.get('title') or '') if is_ok else ''
        title = '' if title == 'None' else title
        canon = (p.get('canonical_url') or '') if is_ok else ''
        canon = '' if canon == 'None' else canon
        lf = v(p.get('linked_from')) or []
        row = {'site': site, 'url': p['url'], 'http_status': code, 'status_class': status_class(code),
               'content_type': (p.get('content_type') or '').split(';')[0], 'page_checks_applied': int(is_ok),
               'redirected': int(bool(chain)), 'redirect_hops': len(chain),
               'redirect_first_status': (chain[0].get('status_code') if chain and isinstance(chain[0], dict) else ''),
               'redirect_final_url': (p.get('redirected_to') if chain and p.get('redirected_to') not in (None, 'None') else ''),
               'title_present': int(bool(title.strip())) if is_ok else '', 'title_length': len(title) if is_ok else '',
               'meta_description_present': (0 if p['url'] in flagged['missing_meta'] else 1) if is_ok else '',
               'canonical_present': (0 if p['url'] in flagged['missing_canonical'] else 1) if is_ok else '',
               'canonical_url': canon,
               'canonical_cross_domain_informational': (int(p['url'] in xdom) if is_ok else ''),
               'h1_present': (0 if p['url'] in flagged['missing_h1'] else 1) if is_ok else '',
               'multiple_h1': (int(p['url'] in flagged['multiple_h1'])) if is_ok else '',
               'title_over_60_chars': (int(p['url'] in flagged['title_too_long'])) if is_ok else '',
               'near_duplicate_informational': (int(p['url'] in flagged['duplicate_content'])) if is_ok else '',
               'images_total': len(imgs) if is_ok else '',
               'images_without_alt': len(real) if is_ok else '',
               'content_images_without_alt': sum(1 for i in real if i.get('is_probably_content')) if is_ok else '',
               'links_to_broken_urls': links_to_broken.get(p['url'], 0) if is_ok else '',
               'links_to_redirecting_urls': links_to_redir.get(p['url'], 0) if is_ok else '',
               'linked_from_count': len(lf)}
        pages_rows.append(row)
    nq = len({u.split('?')[0] for u in flagged['missing_meta']})
    s = {'site': site, 'scope': SCOPE[site], 'start_url': m['start'], 'crawl_finished': m['date'],
         'urls_crawled': len(pages), 'html_pages_200': m['ok_pages'], 'blocked_not_counted': m['blocked_or_offsite_403'],
         'http_requests': m['requests'], 'crawl_seconds': m['elapsed_s'],
         'broken_urls': m['broken_urls'], 'redirecting_internal_urls': m['redirecting_internal_urls'],
         'missing_meta_description': m['missing_meta'], 'missing_meta_description_distinct_paths': nq,
         'missing_canonical': m['missing_canonical'], 'missing_h1': m['missing_h1'], 'multiple_h1': m['multiple_h1'],
         'pages_content_img_no_alt': m['pages_content_img_no_alt'], 'pages_any_img_no_alt': m['pages_img_no_alt'],
         'title_over_60_chars': m['title_too_long'], 'duplicate_title': m['duplicate_title'],
         'duplicate_meta_description': m['duplicate_meta'], 'near_duplicate_pages_informational': m['duplicate_content'],
         'canonical_cross_domain_informational': m['canonical_cross_domain']}
    for k in ('missing_meta_description', 'missing_canonical', 'missing_h1', 'pages_content_img_no_alt'):
        s['pct_' + k] = round(100 * s[k] / max(s['html_pages_200'], 1), 1)
    sites.append(s)
    raw_counts = collections.Counter(i['check'] for i in d['issues'])
    for chk, why in EXCLUDED.items():
        if raw_counts.get(chk): excluded_rows.append({'site': site, 'toadstone_check': chk, 'raw_flags': raw_counts[chk], 'why_not_counted': SITE_NOTE.get((site, chk), why)})
def wcsv(name, rows):
    with open(os.path.join(OUT, name), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
wcsv('sites.csv', sites); json.dump(sites, open(os.path.join(OUT, 'sites.json'), 'w'), indent=1)
wcsv('pages.csv', pages_rows); wcsv('excluded-flags.csv', excluded_rows)
print(len(sites), 'sites;', len(pages_rows), 'url rows;', len(excluded_rows), 'excluded-flag rows')
