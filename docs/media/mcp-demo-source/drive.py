#!/usr/bin/env python3
"""Drives the REAL Toadstone MCP server over stdio and records every request/response to transcript-raw.json.
No results are fabricated: the video is rendered only from this file. (Agent 'thinking' text is added later in build_video.py and is illustrative.)"""
import json, subprocess, sys, time, os
REPO = '/workspace/toadstone/repo'
env = dict(os.environ, TOADSTONE_MCP_URL='http://localhost:5057')
PY = '/workspace/toadstone/venv/bin/python'
class Srv:
    def __init__(s, extra):
        s.cmd = [PY, '-m', 'src.mcp'] + extra
        s.p = subprocess.Popen(s.cmd, cwd=REPO, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
        s.id = 0; s.log = []
    def rpc(s, method, params=None):
        s.id += 1; msg = {'jsonrpc': '2.0', 'id': s.id, 'method': method}
        if params is not None: msg['params'] = params
        t0 = time.time(); s.p.stdin.write(json.dumps(msg) + '\n'); s.p.stdin.flush()
        reply = json.loads(s.p.stdout.readline())
        s.log.append({'request': msg, 'response': reply, 'seconds': round(time.time() - t0, 2)}); return reply
    def tool(s, name, args):
        r = s.rpc('tools/call', {'name': name, 'arguments': args})
        return json.loads(r['result']['content'][0]['text'])
    def close(s): s.p.stdin.close(); s.p.wait(timeout=10)
init = {'protocolVersion': '2025-06-18', 'capabilities': {}, 'clientInfo': {'name': 'demo-agent', 'version': '0'}}
# Session A: the demo agent. Writes allowed ONLY for host localhost, 50-URL cap.
A = Srv(['--allow-writes', '--allow-host', 'localhost', '--max-urls', '100'])
A.rpc('initialize', init); tl = A.rpc('tools/list')
c = A.tool('start_crawl', {'url': 'http://localhost:8099/', 'max_urls': 50}); cid = c['crawl_id']
while True:
    s = A.tool('crawl_status', {'crawl_id': cid})
    if s['status'] in ('completed', 'failed', 'stopped'): break
    time.sleep(1)
A.tool('list_issues', {'crawl_id': cid, 'severity': 'error', 'limit': 50})
A.tool('check_reference', {'check': 'missing_meta_description'})
A.tool('page_detail', {'crawl_id': cid, 'url': 'http://localhost:8099/shop/rakes/', 'link_limit': 5})
A.tool('start_crawl', {'url': 'https://example.com/'})   # guardrail: host not allowed -> refused, no request sent
A.close()
# Session B: default (read-only) server
B = Srv(['--url', 'http://localhost:5057'])
B.rpc('initialize', init); B.tool('start_crawl', {'url': 'http://localhost:8099/'}); B.close()
json.dump({'crawl_id': cid, 'cmdA': A.cmd, 'cmdB': B.cmd, 'tools_list': tl, 'calls': A.log, 'readonly_calls': B.log}, open('transcript-raw.json', 'w'), indent=1)
print('ok', cid, len(A.log))
