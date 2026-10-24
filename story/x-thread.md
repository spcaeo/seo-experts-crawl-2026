# X thread v2: "audit the experts" (DRAFT, not posted)

Replaces thread-v1. Corrections vs v1: Backlinko has **66** redirecting links, **56** of which end on searchengineland.com (v1 said "50+"); the Moz link is to "Local Search Marketing"; all examples were re-verified 19:45–19:48 ET on 23 Oct 2026.

Media files are in `docs/media/` (also copied to `/workspace/toadstone/study/media/`).

1/ — attach `issues-race.mp4` (33 s, 1080×1080)
We pointed a polite crawler at 10 of the best-known SEO sites (Semrush, Ahrefs, Moz, Backlinko, Yoast, SEJ & more). ~300 pages each, 2,521 pages in total.

Most were close to spotless. The slips we did find are the same ones on your site. 🧵

2/ — attach `chart_issues_per_page.png`
The bar is high: 3 broken URLs in 2,521 pages. 77% of pages passed every basic check.

Semrush's blog: 0 issues in 300 pages. Neil Patel: 1 in 240. Surfer: 4 in 103.

3/ — attach `card-2-template.png`
Biggest pattern: one template = hundreds of pages.

One sitewide badge with no alt text is 294 of the 298 counted issues on Search Engine Roundtable. One line in one template fixes all of them. Fix templates first, then the long tail.

4/ — attach `card-4-redirects.png`
What else showed up was ordinary, busy-team stuff:
• a placeholder link left in a Backlinko article (404)
• a "Local Search Marketing" link on 7 Moz guide pages that now 404s
• 66 Backlinko links that hop through a redirect first, 56 of them ending on searchengineland.com (a sister brand, so likely a content move, not an error)

5/ — no media
Being fair matters, so we threw out anything we couldn't confirm:
• bot-blocked 403s aren't "broken" (177 URLs)
• cross-domain canonicals can be correct
• long titles are a choice, not an error

Every example was re-fetched with curl before we posted. The evidence log is in the repo.

6/ — attach `quick-audit-terminal.gif` (or `.mp4`)
Full disclosure: the crawler is ours. Toadstone is a free, self-hosted, source-available SEO crawler (Elastic License 2.0). We also ran it on this study's own page, and it passes its own audit.

7/ — attach `og-image.png` (link card will show it)
All the data (CC BY 4.0), the verified examples, and an animated version of the story:
https://spcaeo.github.io/seo-experts-crawl-2026/

Code: https://github.com/spcaeo/toadstone

---

*Check before posting: the old demo page (https://spcaeo.github.io/toadstone/) had no meta description when last checked 23 Oct 2026. Fix it first, or the "we ran it on ourselves" line invites the obvious reply.*
