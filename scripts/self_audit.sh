#!/usr/bin/env bash
# Self-audit: crawl a local copy of docs/ with Toadstone, served under /seo-experts-crawl-2026/ (same path as GitHub Pages).
# Canonical/OG/sitemap URLs are rebuilt for the local origin for the test only (Toadstone rightly flags a canonical on another host).
#   ./scripts/self_audit.sh            -> as GitHub Pages serves it (no custom response headers)
#   ./scripts/self_audit.sh --headers  -> same files behind a server that sets security headers (what a self-hoster can do)
# Needs TOADSTONE_REPO (a Toadstone checkout) and TOADSTONE_HOME (dir containing venv/bin/python); defaults are the author box paths.
# The throttle is off because the target is our own localhost server (the throttle wait otherwise shows up as a fake ~1000 ms response time).
# robots.txt + sitemap.xml are also copied to the origin root, simulating a custom domain: on github.io the origin root belongs to another site.
set -euo pipefail
R="$(cd "$(dirname "$0")/.." && pwd)"; T="${TOADSTONE_HOME:-/workspace/toadstone}"; PORT="${PORT:-8101}"; MODE=pages; EXTRA=""
[ "${1:-}" = "--headers" ] && MODE=headers && EXTRA="--headers"
SERVE="$(mktemp -d)"; TARGET="$SERVE/seo-experts-crawl-2026"; BASE="http://127.0.0.1:$PORT/seo-experts-crawl-2026/"
cp -r "$R/docs" "$TARGET"; "$T/venv/bin/python" "$R/scripts/build_page.py" --base "$BASE" --out "$TARGET/index.html" >/dev/null
cp "$TARGET/robots.txt" "$TARGET/sitemap.xml" "$SERVE/"
python3 "$R/scripts/serve_local.py" "$PORT" "$SERVE" $EXTRA & SPID=$!; sleep 1
mkdir -p "$R/self-audit"
"$T/venv/bin/python" "$R/scripts/ts_crawl.py" "$BASE" "$R/self-audit/raw-crawl-$MODE.json" --max 100 --delay 0 --concurrency 2 --rps 1000 --sitemaps > "$R/self-audit/crawl-$MODE.log" 2>&1 || true
kill $SPID 2>/dev/null || true
"$T/venv/bin/python" "$R/scripts/self_audit_report.py" "$R/self-audit/raw-crawl-$MODE.json" | tee "$R/self-audit/self-audit-$MODE.txt"
