#!/usr/bin/env python3
"""Tiny static server for the self-audit. --headers adds the security headers a self-hoster (nginx/Cloudflare) can set but GitHub Pages cannot."""
import http.server, sys, os
port = int(sys.argv[1]); root = sys.argv[2]; hard = '--headers' in sys.argv
CSP = "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; media-src 'self'; connect-src 'self'; font-src 'self'; object-src 'none'; base-uri 'self'; form-action 'none'; frame-ancestors 'none'"
class H(http.server.SimpleHTTPRequestHandler):
    def __init__(s, *a, **k): super().__init__(*a, directory=root, **k)
    def version_string(s): return 'static'
    def log_message(s, *a): pass
    def address_string(s): return '127.0.0.1'
    def end_headers(s):
        s.send_header('Cache-Control', 'max-age=600')
        if hard:
            s.send_header('Content-Security-Policy', CSP); s.send_header('X-Content-Type-Options', 'nosniff'); s.send_header('X-Frame-Options', 'DENY')
            s.send_header('Referrer-Policy', 'strict-origin-when-cross-origin'); s.send_header('Permissions-Policy', 'camera=(), microphone=(), geolocation=()')
        super().end_headers()
http.server.ThreadingHTTPServer(('127.0.0.1', port), H).serve_forever()
