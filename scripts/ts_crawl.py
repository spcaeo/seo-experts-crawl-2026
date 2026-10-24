#!/usr/bin/env python3
"""Polite headless Toadstone crawl with overrides (the stock --crawl CLI has no max-urls/UA flags).
Usage: ts_crawl.py URL OUT.json [--max 300] [--delay 0.5] [--concurrency 2]"""
import sys, os, json, time, argparse
REPO = os.environ.get('TOADSTONE_REPO', '/workspace/toadstone/repo')
os.environ['TS_CWD'] = os.getcwd(); sys.path.insert(0, REPO); os.chdir(REPO)
p = argparse.ArgumentParser()
p.add_argument('url'); p.add_argument('out')
p.add_argument('--max', type=int, default=300)
p.add_argument('--delay', type=float, default=0.5)   # 0.5s => <=2 req/s
p.add_argument('--concurrency', type=int, default=2)
p.add_argument('--depth', type=int, default=5)
p.add_argument('--timeout', type=int, default=1500)
p.add_argument('--include', default='')
p.add_argument('--sitemaps', action='store_true')
p.add_argument('--rps', type=float, default=2.0)
a = p.parse_args(); a.out = os.path.abspath(os.path.join(os.environ.get("TS_CWD", os.getcwd()), a.out))
from src.settings_manager import SettingsManager
from src.crawler import WebCrawler
cfg = SettingsManager().get_crawler_config()
cfg.update({'max_urls': a.max, 'delay': a.delay, 'concurrency': a.concurrency,
            'max_depth': a.depth, 'respect_robots': True,
            'user_agent': 'ToadstoneBot/1.0 (+https://github.com/spcaeo/toadstone; polite research crawl, <=2 req/s)'})
cfg['discover_sitemaps'] = a.sitemaps; cfg['audit_sitemaps'] = a.sitemaps
if a.include: cfg['include_patterns'] = [a.include]
c = WebCrawler(); c.update_config(cfg)
# Hard global throttle: every HTTP request this crawler makes (pages, HEAD image checks,
# robots, sitemaps) goes through one lock, so we never exceed --rps against the site.
import threading
_lock = threading.Lock(); _last = [0.0]; _orig = c.session.request; _count = [0]
def _throttled(method, url, *args, **kw):
    with _lock:
        wait = _last[0] + 1.0 / a.rps - time.time()
        if wait > 0: time.sleep(wait)
        _last[0] = time.time(); _count[0] += 1
    return _orig(method, url, *args, **kw)
c.session.request = _throttled
ok, msg = c.start_crawl(a.url)
if not ok: print('start failed', msg); sys.exit(2)
t0 = time.time()
while c.is_running:
    time.sleep(1)
    if time.time() - t0 > a.timeout:
        print('timeout, stopping'); c.stop_crawl() if hasattr(c, 'stop_crawl') else None; break
time.sleep(2)
issues = c.issue_detector.get_issues() if c.issue_detector else []
urls = []
for attr in ('crawl_results', 'results'):
    if hasattr(c, attr): urls = getattr(c, attr); break
json.dump({'url': a.url, 'crawled': c.stats.get('crawled'), 'stats': c.stats, 'issues': issues,
           'pages': urls, 'http_requests': _count[0], 'settings': {'max': a.max, 'delay': a.delay, 'concurrency': a.concurrency, 'depth': a.depth, 'rps_cap': a.rps, 'include': a.include, 'sitemaps': a.sitemaps, 'ua': cfg['user_agent']}, 'elapsed': time.time() - t0, 'date': time.strftime('%Y-%m-%d %H:%M %Z')},
          open(a.out, 'w'), default=str)
print(f"{a.url}: crawled {c.stats.get('crawled')} in {time.time()-t0:.0f}s, {len(issues)} issues -> {a.out}")
