"""Bodies for docs/calculator.html and docs/compare.html (called from build_page.py).
Every price comes from data/screamingfrog-pricing.json; every Toadstone claim points at the Toadstone repo."""
import json, os, html
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
P = json.load(open(os.path.join(R, 'data/screamingfrog-pricing.json')))
SYM = {'GBP': '£', 'USD': '$', 'EUR': '€'}
TR = 'https://github.com/spcaeo/toadstone/blob/main/'
S = {  # id -> (label, url)
    's1': ('Screaming Frog, SEO Spider pricing page', P['source_url']),
    's2': ('Screaming Frog, SEO Spider user guide (General)', 'https://www.screamingfrog.co.uk/seo-spider/user-guide/general/'),
    's3': ('Screaming Frog, MCP Server guide (posted 17 March 2026)', 'https://www.screamingfrog.co.uk/guides/mcp-server/'),
    's4': ('Screaming Frog, SEO Spider FAQ', 'https://www.screamingfrog.co.uk/seo-spider/faq/'),
    't1': ('Toadstone README', TR + 'README.md'),
    't2': ('Toadstone MCP docs', TR + 'docs/mcp.md'),
    't3': ('Toadstone check catalogue', TR + 'docs/checks.md'),
    't5': ('Toadstone report export code (HTML and Markdown)', TR + 'src/api/exports/__init__.py'),
    't4': ('Toadstone licence (Elastic License 2.0)', TR + 'LICENSE'),
}
def cite(*ids):
    return '<sup class="cite">' + ''.join(f'<a href="#src-{i}" aria-label="Source {i.upper()}">[{i.upper()}]</a>' for i in ids) + '</sup>'
def money(cur, n):
    return f'{SYM[cur]}{n:,.0f}'
def tier_for(seats):
    for t in P['tiers']:
        if seats >= t['min'] and (t['max'] is None or seats <= t['max']):
            return t
DEF = dict(seats=5, years=3, cur='USD')

def sources_list(ids):
    return '<ol class="clean srcs">' + ''.join(
        f'<li id="src-{i}"><b>[{i.upper()}]</b> <a href="{S[i][1]}" rel="noopener">{html.escape(S[i][0])}</a> <span class="mono">{S[i][1]}</span>' +
        (f', retrieved {P["retrieved"]}' if i.startswith('s') else ', repo snapshot read 20 October 2026 (commit fe9c951)') + '</li>' for i in ids) + '</ol>'

# ------------------------------------------------------------------ calculator
def calculator():
    seats, years, cur = DEF['seats'], DEF['years'], DEF['cur']
    t = tier_for(seats); price = t[cur]; total = seats * price * years
    rows_tier = ''.join(
        f'<tr data-min="{x["min"]}" data-max="{x["max"] if x["max"] else ""}" data-gbp="{x["GBP"]}" data-usd="{x["USD"]}" data-eur="{x["EUR"]}">'
        f'<th scope="row">{x["label"]} licences</th><td>{money("GBP", x["GBP"])}</td><td>{money("USD", x["USD"])}</td><td>{money("EUR", x["EUR"])}</td></tr>' for x in P['tiers'])
    yrows = ''.join(f'<tr><th scope="row">Year {y}</th><td>{money(cur, seats*price*y)}</td><td>{money(cur, 0)}</td></tr>' for y in range(1, years + 1))
    body = f'''<div class="panel disclose"><p><b>Read this first.</b> Toadstone is our own tool, and this page compares it with one paid competitor, so treat it as our view. It does only arithmetic on Screaming Frog's <em>public list price</em>, which we read from <a href="{P["source_url"]}" rel="noopener">their pricing page</a> on {P["retrieved"]}{cite("s1")}. It does not claim Toadstone is better, only that its licence costs nothing. We are not affiliated with Screaming Frog. See the <a href="compare.html">full comparison</a>, including <a href="compare.html#gaps">what Toadstone doesn't do</a>.</p></div>
<p><b>Might you not need to pay at all?</b> Screaming Frog's free version crawls up to 500 URLs{cite("s1")}. If your sites are smaller than that, the free version may be all you need, and so may Toadstone.</p>
<h2 id="calc-h">Your numbers</h2>
<form id="calc" class="calc" aria-labelledby="calc-h" novalidate>
<div class="fields">
<label for="seats">Team seats<span class="hint">people who would run crawls</span></label><input id="seats" name="seats" type="number" inputmode="numeric" min="1" max="1000" step="1" value="{seats}">
<label for="years">Years<span class="hint">1 to 10</span></label><input id="years" name="years" type="number" inputmode="numeric" min="1" max="10" step="1" value="{years}">
<label for="cur">Currency<span class="hint">prices as shown on their page</span></label><select id="cur" name="cur"><option value="USD" selected>USD ($)</option><option value="GBP">GBP (£)</option><option value="EUR">EUR (€)</option></select>
<label for="own">Your quoted price per licence per year<span class="hint">optional; leave empty to use the list price</span></label><input id="own" name="own" type="number" inputmode="decimal" min="0" step="any" placeholder="e.g. a price you were quoted">
<label for="host">Your Toadstone hosting cost per year<span class="hint">optional; a server or laptop time, default 0</span></label><input id="host" name="host" type="number" inputmode="decimal" min="0" step="any" placeholder="0">
</div>
<p id="calc-err" class="bad" role="alert" hidden></p>
</form>
<h2>The result</h2>
<div id="calc-out" class="result" aria-live="polite">
<p id="calc-line" class="big">Over {years} years for {seats} seats, Screaming Frog's list price comes to <b>{money(cur, total)}</b>. Toadstone's licence costs <b>{money(cur, 0)}</b>.</p>
<p id="calc-math" class="note">{seats} × {money(cur, price)} (the {t["label"]} licence tier) × {years} years = {money(cur, total)}. Taxes not included.</p>
<div class="bars" aria-hidden="true">
<div class="barrow"><span class="bl">Screaming Frog</span><span class="track"><span id="bar-sf" class="fill sf full"></span></span><span id="val-sf" class="bv">{money(cur, total)}</span></div>
<div class="barrow"><span class="bl">Toadstone</span><span class="track"><span id="bar-ts" class="fill ts zero"></span></span><span id="val-ts" class="bv">{money(cur, 0)}</span></div>
</div>
<div class="tablewrap"><table class="plain" id="yeartable"><caption class="note">Cumulative licence cost by year (list price, no discounts beyond the volume tiers)</caption><thead><tr><th scope="col">When</th><th scope="col">Screaming Frog</th><th scope="col">Toadstone</th></tr></thead><tbody id="yearbody">{yrows}</tbody></table></div>
</div>
<noscript><p class="note">Without JavaScript this page shows the example above (5 seats, 3 years, USD). Use the price table below to work out your own numbers.</p></noscript>
<h2>What this calculator does not count</h2>
<ul class="clean">
<li><b>Toadstone is not free to run.</b> It is free to license, but you host it (Docker, or Python 3.11+ with Chromium){cite("t1")}, and someone has to look after it. The hosting field above lets you add that cost. Your own time is not counted anywhere.</li>
<li><b>No support contract.</b> Screaming Frog lists technical support with a licence{cite("s1")}. Toadstone has none.</li>
<li><b>Renewals.</b> Licences last one year{cite("s1", "s4")}. We assume you renew at the same list price. We could not confirm a separate renewal rate, so your real price may differ.</li>
<li><b>Tiers.</b> The per-licence price drops when you buy 5, 10 or 20 or more licences at the same time{cite("s1")}. We assume one purchase for all seats.</li>
<li><b>Features.</b> Cost is only one axis. <a href="compare.html">The comparison</a> lists where Screaming Frog is ahead, including crawl scale and a desktop app.</li>
<li><b>Taxes, discounts, add-on products</b> (such as their Log File Analyser) and promotions are not included.</li></ul>
<h2>The price table the calculator uses</h2>
<p>Screaming Frog SEO Spider, price per licence per year, by number of licences bought at once. Copied from <a href="{P["source_url"]}" rel="noopener">their pricing page</a> on {P["retrieved"]} (GBP is the page default; USD and EUR are what the same page shows after you pick the currency there){cite("s1")}.</p>
<div class="tablewrap"><table class="plain" id="pricetable"><caption class="note">Licences last 1 year and are per user{cite("s1")}</caption><thead><tr><th scope="col">Licences</th><th scope="col">GBP</th><th scope="col">USD</th><th scope="col">EUR</th></tr></thead><tbody>{rows_tier}</tbody></table></div>
<p class="note">Prices change. If the pricing page now says something different, <a href="{P["source_url"]}" rel="noopener">trust it over this page</a> and <a href="https://github.com/spcaeo/seo-experts-crawl-2026/issues">tell us</a>. Data file: <a href="data/screamingfrog-pricing.json">screamingfrog-pricing.json</a>.</p>
<h2>Sources</h2>
{sources_list(["s1", "s4", "t1"])}
<p class="note">This page has no tracking, no cookies and makes no network requests. Everything is computed in your browser.</p>'''
    return body

# ------------------------------------------------------------------ comparison
def row(feature, ts, sf, edge):
    cls = {'Toadstone': 'ok', 'Screaming Frog': 'warn'}.get(edge, '')
    pill = f'<span class="pill {cls}">{edge}</span>' if cls else f'<span class="plainedge">{edge}</span>'
    return f'<tr><th scope="row">{feature}</th><td class="why">{ts}</td><td class="why">{sf}</td><td>{pill}</td></tr>'

def compare():
    t = tier_for(1); t5 = tier_for(5)
    rows = [
        row('Licence fee', f'None. Free, self-hosted{cite("t1")}. You pay for your own hosting and time.',
            f'Free version (500 URLs per crawl); paid licence {money("GBP", t["GBP"])} / {money("USD", t["USD"])} per user per year, less in bulk{cite("s1")}. <a href="calculator.html">Calculator</a>.', 'Toadstone'),
        row('Seats', f'No seat fees{cite("t1")}.', f'Licence is per user{cite("s1")}.', 'Toadstone'),
        row('Licence type', f'Elastic License 2.0: source-available, not open source{cite("t4")}.', f'Commercial licence, one year at a time{cite("s1", "s4")}.', 'Similar'),
        row('Runs on', f'Docker, or Python 3.11+ with Chromium; used through a browser UI, an HTTP API or the command line{cite("t1")}.',
            f'Desktop app for Windows, macOS, Ubuntu and Fedora, plus a command line{cite("s2")}.', 'Screaming Frog'),
        row('Crawl size', f'No licence cap; bounded by the max_urls setting and memory. Built for tens of thousands of pages, not millions{cite("t1")}.',
            f'Free: 500 URLs. Paid: unlimited by licence; their default crawl limit is 5 million URLs, described as not a hard limit{cite("s2")}.', 'Screaming Frog'),
        row('Number of checks', f'222 checks, 180 of them observed firing in the last sweep{cite("t1", "t3")}.',
            'Not counted here. Their issue library is documented by Screaming Frog. Counts are not a common unit, so we do not claim more.', 'Not compared'),
        row('Search Console and GA4 joined to the crawl', f'Yes, both{cite("t1")}.', f'Yes: Google Analytics (GA4) and Search Console integrations{cite("s1", "s2")}.', 'Similar'),
        row('JavaScript rendering', f'Yes, with Playwright and Chromium{cite("t1")}.', f'Yes{cite("s1")}.', 'Similar'),
        row('Crawl comparison between runs', f'Yes, issues carry a stable id so new, fixed and still-open can be diffed{cite("t1", "t2")}.', f'Yes, crawl comparison is a listed feature{cite("s1")}.', 'Similar'),
        row('Scheduling', f'Built-in scheduler for standing crawls{cite("t1")}.', f'Yes, scheduling is a listed feature{cite("s1", "s2")}.', 'Similar'),
        row('Server log analysis', f'Built in: you give it an access log{cite("t1")}.', f'Separate product, the Log File Analyser{cite("s1")}.', 'Toadstone'),
        row('Exports', f'JSON, CSV and XLSX from the HTTP API; HTML and Markdown issue reports{cite("t1", "t5")}.', f'CSV, Excel and Google Sheets exports from the command line{cite("s2")}.', 'Similar'),
        row('MCP server for AI assistants', f'10 tools, read-only by default; starting crawls and muting issues need an explicit write flag{cite("t2")}.',
            f'29 tools including crawl control, bulk exports and a Node.js script runner (off by default). Paid licence only; needs version 24 in database storage mode{cite("s3")}.', 'Screaming Frog'),
        row('Fail a build on new errors', f'Command line mode with <code class="mono">--fail-on error</code> exits non-zero{cite("t1")}.',
            f'Command line can run headless crawls and export data{cite("s2")}. We did not find a documented severity-based exit code. That is not proof there isn\'t one.', 'Toadstone'),
        row('Per-client projects', 'No. See "What Toadstone doesn\'t do" below.', f'Crawls can be organised into project folders, and scheduled crawls take a project name{cite("s2")}.', 'Screaming Frog'),
        row('Support', f'None guaranteed. A small project with no support contract{cite("t1")}.', f'Technical support is listed as a licence feature{cite("s1")}.', 'Screaming Frog'),
    ]
    gaps = [
        ('Per-client projects or workspaces', 'Toadstone has no project or client folder concept. Agencies running many clients will have to separate them by hand.'),
        ('PDF reports', 'Not supported. It produces HTML and Markdown reports and data exports, not PDFs.'),
        ('White-label reports', 'Not supported. You cannot put your own branding on its output.'),
        ('Keyword research', 'Not included, and not planned. It is a crawler, not a keyword tool.'),
        ('Rank tracking', 'Not included, and not planned.'),
        ('A backlink index', 'It has none of its own. It can read domain authority and link counts if you bring a Moz, Majestic or Ahrefs key.'),
        ('Crawling millions of URLs', 'Not what it is for. It stores page bodies and is built for tens of thousands of pages on ordinary hardware.'),
        ('Importing a list of URLs from a CSV', 'Wanted, not started. Screaming Frog has a list mode.'),
        ('Continuous monitoring', 'Crawls run on a schedule. There is no always-on watcher or sub-minute alerting.'),
        ('A support contract or guaranteed answers', 'None. There is no phone line, no SLA and no paid tier.'),
        ('A native desktop installer', 'You need Docker, or Python 3.11+ plus Chromium. Someone has to be comfortable running that.'),
    ]
    gaps_html = ''.join(f'<li><b>{a}.</b> {b}</li>' for a, b in gaps)
    body = f'''<div class="panel disclose"><p><b>Read this first.</b> We make Toadstone, so we have an interest in how this comes out. To limit that: each claim below points at a public page, either Toadstone's own repo or Screaming Frog's own pages, read on {P["retrieved"]}. Where we couldn't confirm something about Screaming Frog we say so rather than guess. We are not affiliated with Screaming Frog, we did not ask them to review this, and "Screaming Frog" is their name and mark. If we got something wrong, <a href="https://github.com/spcaeo/seo-experts-crawl-2026/issues">open an issue</a> and we will correct it.</p></div>
<h2>Side by side</h2>
<div class="tablewrap"><table class="plain cmp"><caption class="note">"Edge" is our own reading of which is better on that row. Where it says "Similar" or "Not compared", neither is. Bracketed codes link to the sources at the bottom.</caption>
<thead><tr><th scope="col">Topic</th><th scope="col">Toadstone</th><th scope="col">Screaming Frog SEO Spider</th><th scope="col">Edge</th></tr></thead>
<tbody>{"".join(rows)}</tbody></table></div>
<h2 id="gaps">What Toadstone doesn't do (yet)</h2>
<p>If one of these is a requirement for you, Toadstone is the wrong choice today. Some are gaps we may close; the keyword and rank items are deliberate.</p>
<ul class="clean">{gaps_html}</ul>
<p class="note">Source: Toadstone's own README and roadmap{cite("t1")}.</p>
<h2>When Screaming Frog is the better pick</h2>
<ul class="clean">
<li>You want a desktop app with a licence and support behind it{cite("s1", "s2")}. Toadstone's own README says as much.</li>
<li>You crawl very large sites. Screaming Frog is built for millions of URLs{cite("s2")}; Toadstone is not{cite("t1")}.</li>
<li>You run many clients and need to keep their crawls in separate project folders{cite("s2")}.</li>
<li>You want the deeper AI-assistant integration: more tools and bulk exports{cite("s3")}.</li>
<li>You value a mature, widely used tool with long documentation history.</li></ul>
<h2>When Toadstone may fit better</h2>
<ul class="clean">
<li>Your team is large and per-seat licence cost matters. Toadstone has no seat fees; <a href="calculator.html">run the numbers</a>.</li>
<li>You want a crawl to gate a deploy: <code class="mono">--fail-on error</code> returns a non-zero exit code{cite("t1")}.</li>
<li>You want your crawl data to stay on your own machine, read by your own AI assistant through a read-only MCP server{cite("t2")}.</li>
<li>Your sites are in the thousands or tens of thousands of pages, and you don't want a licence fee for them.</li></ul>
<h2>Sources and what we could not verify</h2>
{sources_list(["s1", "s2", "s3", "s4", "t1", "t2", "t3", "t4", "t5"])}
<h3>Could not verify</h3>
<ul class="clean">
<li>Whether Screaming Frog's command line can fail on issue severity (we read their user guide{cite("s2")} and found none documented).</li>
<li>Screaming Frog's renewal pricing, if different from the list price.</li>
<li>Screaming Frog features we did not test ourselves. We read their public pages and did not run their software for this page.</li>
<li>That the Toadstone repo has not changed since we read it (commit <span class="mono">fe9c951</span>, 20 October 2026). Their numbers are quoted from that snapshot.</li></ul>'''
    return body

def build(shell, out_dir, BASE, stamp, add_ld):
    pages = {}
    cdesc = 'Enter your seats and years to see Screaming Frog\'s public list price next to Toadstone, our own tool, which has no seat fees.'
    cu = BASE + 'calculator.html'
    cld = {'@context': 'https://schema.org', '@type': 'WebApplication', 'name': 'What does a crawler cost your team?', 'description': cdesc, 'url': cu,
           'applicationCategory': 'BusinessApplication', 'operatingSystem': 'Any (web browser)', 'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'USD'},
           'datePublished': stamp, 'dateModified': stamp, 'author': {'@type': 'Person', 'name': 'Rakesh Patel', 'url': 'https://github.com/spcaeo'}}
    pages['calculator.html'] = shell('What does a crawler cost your team?', cdesc, cu, cld, f'Calculator · priced {P["retrieved"]}',
        'What does a crawler cost your team?', 'Put in your seats and years. See Screaming Frog\'s public list price next to Toadstone, our own free tool, with the caveats that matter.',
        calculator(), stamp=stamp, scripts=['assets/calculator.js'])
    pdesc = 'An honest Toadstone vs Screaming Frog comparison: price, scale, MCP, CI and exports, with sources, plus a section on what Toadstone does not do yet.'
    pu = BASE + 'compare.html'
    pld = {'@context': 'https://schema.org', '@type': 'TechArticle', 'headline': 'Toadstone vs Screaming Frog, honestly', 'description': pdesc, 'url': pu, 'mainEntityOfPage': pu,
           'datePublished': stamp, 'dateModified': stamp, 'author': {'@type': 'Person', 'name': 'Rakesh Patel', 'url': 'https://github.com/spcaeo'}}
    pages['compare.html'] = shell('Toadstone vs Screaming Frog, honestly', pdesc, pu, pld, f'Comparison · sources read {P["retrieved"]}',
        'Toadstone vs Screaming Frog, honestly', 'A side-by-side from public pages, with what Toadstone doesn\'t do yet and where Screaming Frog is the better pick. We make Toadstone, so check our sources.',
        compare(), stamp=stamp)
    for name, text in pages.items():
        open(os.path.join(out_dir, name), 'w').write(text)
    return list(pages)
