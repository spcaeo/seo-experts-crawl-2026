# MCP demo: how it was made
- `drive.py` starts the real `python -m src.mcp` server (stdio) against a local Toadstone and a small practice site (6 pages, 9 URLs counting a 404 and a redirect) (`localhost:8099`), and records every JSON-RPC request and reply into `transcript-raw.json`.
- `build_video.py` renders `mcp-demo.mp4` from that transcript with Pillow and ffmpeg. Tool calls and results are copied from the transcript. The one-line agent narration at the top of each step is illustrative text written by us (no model was actually driving).
- The `page_detail` call is shown with an abbreviated URL (`.../shop/rakes/`); the real call used `http://localhost:8099/shop/rakes/`.
- Recorded 24 Oct 2026 against Toadstone `main` as cloned on the box.
