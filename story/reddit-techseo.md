# r/TechSEO post (data post, no hard sell)

*Check the subreddit rules on self-promotion first. Post the data link in the body, not Toadstone. Reply to comments with data, not links to the tool. Attach `chart_issues_per_page.png` as an image if the sub allows it.*

**Title:** I crawled ~300 pages on each of 10 big SEO sites (2,521 pages). 3 broken URLs total. Data + method inside (CC BY 4.0)

**Body:**

I wanted to see how well the sites that publish SEO advice follow their own basics, so I ran a polite crawl of Semrush, Ahrefs, Moz, Backlinko, Yoast, SEJ, SERoundtable, Neil Patel, SE Ranking and Surfer on 23 Oct 2026.

**Method:** up to 300 pages or 25 min per site, 2 req/s max, robots.txt respected, UA identifies the crawler. Four sites (Ahrefs, SE Ranking, Neil Patel, Moz) hit the 25 min cap before 300 pages, so those numbers describe the pages reached. It's a sample, not a census.

**Counted:** broken (404/410/5xx), linked URLs that redirect, missing meta description, missing canonical, no H1, 2+ H1s, content images with no alt attribute (`alt=""` counts as present).
**Not counted:** 401/403/429 (177 URLs, bot walls), cross-domain canonicals, titles >60 chars (633 pages), near-duplicates (91).

**Results:**
- 3 broken URLs in 2,521 pages (Backlinko, Moz, SE Ranking, one each)
- 736 counted issues overall, 29.2 per 100 pages. 77% of pages pass all five page-level checks.
- Semrush: 0/300. Neil Patel: 1/240. Surfer: 4/103.
- SERoundtable: 294 of the 298 counted issues are one sitewide badge image with no alt.
- Backlinko: 66 internal links redirect, 56 of them end on searchengineland.com (sister brand, probably a content move).
- Moz: 90 of 299 pages have no meta description. Yoast: 40.
- Yoast: 42 linked URLs redirect.

I re-fetched every example I quote with curl before posting; the log is in the repo.

Per-page CSV, per-site CSV, data dictionary and the curl evidence: https://github.com/spcaeo/seo-experts-crawl-2026 (there's also a landing page with the animated version: https://spcaeo.github.io/seo-experts-crawl-2026/).

**Disclosure:** the crawler is mine (Toadstone, free, self-hosted, source-available under Elastic License 2.0), so treat my checks accordingly. I'm not affiliated with any of the sites.

Questions I'd like opinions on: does counting `alt=""` as present match how you'd audit? Would you count redirecting internal links as an issue, or only chains? Happy to re-run with different rules, the CSVs have enough to recompute.
