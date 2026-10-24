#!/usr/bin/env python3
"""Derive the small JSON the landing page and videos use, from data/pages.csv + data/sites.json.
'Counted issues' = missing meta description + missing canonical + missing H1 + multiple H1 + pages with a
content image without alt + broken (404/410/5xx) URLs + internally linked URLs that redirect.
Informational columns (long titles, near-duplicates, cross-domain canonicals) and anything blocked are never counted."""
import csv, json, os, collections
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sites = json.load(open(os.path.join(R, 'data', 'sites.json')))
rows = list(csv.DictReader(open(os.path.join(R, 'data', 'pages.csv'))))
ISS = [('missing_meta_description', 'No meta description'), ('missing_canonical', 'No canonical'), ('missing_h1', 'No H1'),
       ('multiple_h1', 'More than one H1'), ('pages_content_img_no_alt', 'Content image without alt'),
       ('broken_urls', 'Broken URL (404)'), ('redirecting_internal_urls', 'Linked URL redirects')]
by = collections.defaultdict(list)
for r in rows: by[r['site']].append(r)
out = {'issues': [{'key': k, 'label': l} for k, l in ISS], 'sites': []}
for s in sites:
    grid, race, n, total = [], [[0, 0]], 0, 0
    for r in by[s['site']]:
        add = 0
        if r['page_checks_applied'] == '1':
            g = (r['meta_description_present'] == '0') + (r['canonical_present'] == '0') + (r['h1_present'] == '0') + \
                (r['multiple_h1'] == '1') + (int(r['content_images_without_alt'] or 0) > 0)
            grid.append(str(min(g, 3))); add += g; n += 1
        if r['status_class'] == 'broken': grid.append('B'); add += 1
        if r['redirected'] == '1': add += 1
        if add:
            total += add; race.append([n, total])
    race.append([n, total])
    counted = sum(s[k] for k, _ in ISS)
    assert counted == total, (s['site'], counted, total)
    out['sites'].append({'site': s['site'], 'pages': s['html_pages_200'], 'counted_issues': counted,
                         'per_page': round(counted / s['html_pages_200'], 2),
                         'counts': {k: s[k] for k, _ in ISS}, 'pct': {k: round(100 * s[k] / s['html_pages_200'], 1) for k, _ in ISS},
                         'title_over_60': s['title_over_60_chars'], 'near_dup': s['near_duplicate_pages_informational'],
                         'blocked_not_counted': s['blocked_not_counted'], 'requests': s['http_requests'], 'urls_crawled': s['urls_crawled'],
                         'scope': s['scope'], 'grid': ''.join(grid), 'race': race})
out['totals'] = {'sites': len(sites), 'pages': sum(s['html_pages_200'] for s in sites), 'urls': sum(s['urls_crawled'] for s in sites),
                 'requests': sum(s['http_requests'] for s in sites), 'broken': sum(s['broken_urls'] for s in sites),
                 'alt_pages': sum(s['pages_content_img_no_alt'] for s in sites), 'blocked_not_counted': sum(s['blocked_not_counted'] for s in sites)}
os.makedirs(os.path.join(R, 'docs', 'data'), exist_ok=True)
json.dump(out, open(os.path.join(R, 'docs', 'data', 'study.json'), 'w'), separators=(',', ':'))
for s in out['sites']: print(s['site'], s['pages'], s['counted_issues'], s['per_page'], len(s['grid']))
print(out['totals'])
