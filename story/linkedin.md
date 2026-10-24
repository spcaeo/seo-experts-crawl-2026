# LinkedIn post (Rakesh's voice)

*Attach: `docs/media/issues-race.mp4` (native video, square 1080×1080, captions burned in) or `card-2-template.png` as a fallback. Put the link in the first comment, not the post, if you want more reach. Do not post until you have checked that the Pages URL is live.*

---

I wanted to know if the people who write the SEO playbooks follow them.

So I crawled 10 of the best-known SEO sites. About 300 pages each, politely: 2 requests a second at most, robots.txt respected.

The honest result: they're in great shape.

→ 3 broken URLs in 2,521 pages
→ 77% of pages passed every basic check
→ Semrush's blog: 0 issues in 300 pages

What did slip through was the stuff every busy team has:

• One sitewide badge with no alt text. It accounts for 294 of the 298 counted issues on one site. One template line, 294 pages.
• 66 links that redirect first. 56 of them end on a sister brand's site after a content move. Not a mistake, just extra hops.
• Meta descriptions missing in clusters, where one page type went out without them.

The lesson I took away: fix templates before pages.

I left out anything I couldn't confirm: bot-blocked 403s, syndicated canonicals, long titles. Every example was re-checked with curl before I wrote it down.

Disclosure: the crawler is mine. Toadstone is a free, self-hosted, source-available (Elastic License 2.0) SEO crawler. I ran it on the study's own page too, and it passes its own audit.

All the data is CC BY 4.0 (CSV, evidence, a data dictionary), plus an animated version of the story. If a number for your site looks off, tell me and I'll re-check it.

Link in the first comment 👇

#SEO #TechnicalSEO #DataJournalism

**First comment:** https://spcaeo.github.io/seo-experts-crawl-2026/
