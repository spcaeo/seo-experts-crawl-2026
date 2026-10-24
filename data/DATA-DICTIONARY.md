# Data dictionary

All files come from one polite crawl run on **23 Oct 2026, about 18:50–19:27 ET (America/Toronto, UTC-4)**, plus curl re-checks at 19:45–19:48 ET. Licence: **CC BY 4.0**. Only public page metadata is published: no page text, no response headers, no cookies.

Counting rules in one paragraph: page-level checks apply only to HTML pages that returned HTTP 200. A URL is *broken* only if it returned 404, 410 or 5xx. 401, 403, 429 and no-response URLs are *blocked, not counted* (bot walls are not errors). **Counted issues** = `missing_meta_description` + `missing_canonical` + `missing_h1` + `multiple_h1` + `pages_content_img_no_alt` + `broken_urls` + `redirecting_internal_urls`. Columns marked *informational* are published but never counted.

## sites.csv / sites.json (one row per site)

| Column | Meaning |
|---|---|
| `site` | Site (host without `www.`) |
| `scope` | Which part of the site the crawl started from |
| `start_url` | Seed URL |
| `crawl_finished` | When the crawl ended (local time of the crawl box, EDT) |
| `urls_crawled` | All URLs the crawler fetched or checked (pages, images, files) |
| `html_pages_200` | HTML pages that returned 200; the denominator for every page-level rate |
| `blocked_not_counted` | URLs that answered 401/403/429 (bot walls, WAFs, signed CDN URLs). Not counted as errors. (3 no-response URLs in total are marked `no_response_not_counted` in pages.csv and not counted either) |
| `http_requests` | Every HTTP request made, including image checks and robots.txt |
| `crawl_seconds` | Wall-clock crawl time. The crawl stopped at 300 URLs or 1,500 s, whichever came first |
| `broken_urls` | Internal URLs returning 404/410/5xx |
| `redirecting_internal_urls` | Internal URLs that return a 3xx and are linked from a crawled page |
| `missing_meta_description` | Pages with no `<meta name="description">` |
| `missing_meta_description_distinct_paths` | Same, counting distinct URL paths (collapses query-string variants) |
| `missing_canonical` | Pages with no `rel=canonical` |
| `missing_h1` / `multiple_h1` | Pages with no H1 / with more than one H1 |
| `pages_content_img_no_alt` | Pages with at least one content image (not a 1×1 pixel or tracker) that has no `alt` attribute. `alt=""` counts as present |
| `pages_any_img_no_alt` | Looser version including non-content images. Informational |
| `title_over_60_chars` | Titles longer than 60 characters. Informational |
| `duplicate_title`, `duplicate_meta_description` | Pages sharing a title / description with another crawled page. Informational |
| `near_duplicate_pages_informational` | Pages the crawler flagged as near-duplicates. Informational |
| `canonical_cross_domain_informational` | Pages whose canonical points to another domain (often intentional, e.g. syndication). Informational |
| `pct_*` | The matching count divided by `html_pages_200`, as a percentage |

## pages.csv (one row per crawled URL, 15,326 rows)

| Column | Meaning |
|---|---|
| `site`, `url` | Site and the URL as crawled |
| `http_status`, `status_class` | Status code and its class: `ok`, `broken` (404/410/5xx; 3 URLs), `blocked_not_counted` (401/403/429; 177 URLs) or `no_response_not_counted` (3 URLs). The last two are never counted as errors |
| `content_type` | Response content type (media type only) |
| `page_checks_applied` | `1` if this is an HTML 200 page, so page checks apply. Otherwise the check columns are blank |
| `redirected`, `redirect_hops`, `redirect_first_status`, `redirect_final_url` | Redirect details when the URL redirects |
| `title_present`, `title_length` | Title tag present and its length |
| `meta_description_present` | `1`/`0` |
| `canonical_present`, `canonical_url` | Canonical tag and target |
| `canonical_cross_domain_informational` | `1` if the canonical is on another domain. Informational |
| `h1_present`, `multiple_h1` | H1 checks |
| `title_over_60_chars`, `near_duplicate_informational` | Informational flags |
| `images_total`, `images_without_alt`, `content_images_without_alt` | Image counts on the page; 1×1 images excluded from the "without alt" counts |
| `links_to_broken_urls`, `links_to_redirecting_urls` | How many links on this page point at a broken / redirecting crawled URL |
| `linked_from_count` | How many crawled pages link to this URL |

## verified-examples.csv / .json

Every example quoted in the story, re-requested with curl (one request at a time, at least 1 s apart, 19:45–19:48 ET). `still_true` is `True` if the observation matched. `evidence_snippet` is a short public HTML fragment. Full request log: `evidence/curl-log.jsonl` (`checked_at_utc` is in UTC; subtract 4 h for ET).

## backlinko-redirects.csv (66 rows)

Every internal Backlinko URL we found redirecting. `goes_to_searchengineland` is `1` if the redirect chain ends on searchengineland.com (56 of 66), else `0`. Both Backlinko and Search Engine Land belong to Semrush, so this looks like content moving between sister brands. It is not an error, just an extra hop.

## excluded-flags.csv

Checks Toadstone raised that we chose **not** to count, with the number of raw flags and the reason.

## evidence/

- `curl-log.jsonl`: one JSON line per curl re-check.
- `quick-audit-sample-site.txt`: the real output of `quick_audit.sh` on the small deliberately-broken sample site shown in the terminal clip.
