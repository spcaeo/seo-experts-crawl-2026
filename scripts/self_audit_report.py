#!/usr/bin/env python3
"""List EVERY issue Toadstone raised for the self-audit crawl (no filtering), plus the 3-bullet quick summary."""
import json, sys, collections
d = json.load(open(sys.argv[1])); pages = d['pages']
print(f"Self-audit of {d.get('url')}: {len(pages)} URLs crawled")
iss = collections.Counter(); ex = collections.defaultdict(list)
def walk(p):
    for key in ('issues', 'issue_list'):
        for i in (p.get(key) or []):
            yield i
top = d.get('issues') or []
for i in top:
    k = i.get('check') or i.get('type') or str(i)[:40]; iss[(k, i.get('severity'))] += 1; ex[k].append(i.get('url'))
for p in pages:
    for i in walk(p):
        k = (i.get('check') or i.get('type') or str(i)[:40]); iss[(k, i.get('severity'))] += 1; ex[k].append(p.get('url'))
print('status codes:', dict(collections.Counter(str(p.get('status_code')) for p in pages)))
if not iss: print('ISSUES: none raised by Toadstone')
for (k, sev), n in sorted(iss.items(), key=lambda x: -x[1]): print(f'  [{sev}] {k} x{n}: e.g. {ex[k][0]}')
