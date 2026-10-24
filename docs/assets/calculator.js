(function () {
  'use strict';
  var doc = document.documentElement; doc.classList.remove('no-js');
  var form = document.getElementById('calc'); if (!form) return;
  var $ = function (id) { return document.getElementById(id); };
  var tiers = [].map.call(document.querySelectorAll('#pricetable tbody tr'), function (tr) {
    return { min: +tr.dataset.min, max: tr.dataset.max === '' ? Infinity : +tr.dataset.max, label: tr.cells[0].textContent.replace(' licences', ''),
             GBP: +tr.dataset.gbp, USD: +tr.dataset.usd, EUR: +tr.dataset.eur };
  });
  var fmtCache = {};
  function money(cur, n) {
    if (!fmtCache[cur]) fmtCache[cur] = new Intl.NumberFormat('en-US', { style: 'currency', currency: cur, maximumFractionDigits: 0 });
    return fmtCache[cur].format(n);
  }
  function whole(v, lo, hi) { var n = Number(v); return v !== '' && isFinite(n) && Math.floor(n) === n && n >= lo && n <= hi ? n : null; }
  function optional(v) { if (v === '') return 0; var n = Number(v); return isFinite(n) && n >= 0 ? n : null; }
  function text(id, s) { $(id).textContent = s; }
  function run() {
    var seats = whole($('seats').value, 1, 1000), years = whole($('years').value, 1, 10), cur = $('cur').value;
    var own = optional($('own').value), host = optional($('host').value), err = $('calc-err'), bad = [];
    if (seats === null) bad.push('seats must be a whole number from 1 to 1000');
    if (years === null) bad.push('years must be a whole number from 1 to 10');
    if (own === null) bad.push('your quoted price must be a number, 0 or more');
    if (host === null) bad.push('hosting cost must be a number, 0 or more');
    if (bad.length) { err.textContent = 'Please check: ' + bad.join('; ') + '.'; err.hidden = false; return; }
    err.hidden = true;
    var t = tiers.filter(function (x) { return seats >= x.min && seats <= x.max; })[0];
    var useOwn = $('own').value !== '' && own > 0;
    var price = useOwn ? own : t[cur];
    var sf = seats * price * years, ts = host * years;
    var how = useOwn ? 'your quoted price' : 'the ' + t.label + ' licence tier';
    var line = 'Over ' + years + (years === 1 ? ' year' : ' years') + ' for ' + seats + (seats === 1 ? ' seat' : ' seats') +
      ', Screaming Frog\u2019s ' + (useOwn ? 'cost at your quoted price' : 'list price') + ' comes to ' + money(cur, sf) + '. ' +
      (host > 0 ? 'Toadstone\u2019s licence costs ' + money(cur, 0) + ' and your own hosting estimate adds ' + money(cur, ts) + '.' : 'Toadstone\u2019s licence costs ' + money(cur, 0) + '.');
    text('calc-line', line);
    text('calc-math', seats + ' \u00d7 ' + money(cur, price) + ' (' + how + ') \u00d7 ' + years + (years === 1 ? ' year' : ' years') + ' = ' + money(cur, sf) +
      '. Taxes not included.' + (sf > 0 && ts > sf ? ' Note: your hosting estimate is higher than the licence cost here.' : ''));
    var top = Math.max(sf, ts, 1);
    var bs = $('bar-sf'), bt = $('bar-ts');
    bs.classList.remove('full', 'zero'); bt.classList.remove('full', 'zero');
    bs.style.width = Math.max(sf / top * 100, 0.5) + '%'; bt.style.width = Math.max(ts / top * 100, 0.5) + '%';
    text('val-sf', money(cur, sf)); text('val-ts', money(cur, ts));
    var body = $('yearbody'); while (body.firstChild) body.removeChild(body.firstChild);
    for (var y = 1; y <= years; y++) {
      var tr = document.createElement('tr'), th = document.createElement('th'); th.scope = 'row'; th.textContent = 'Year ' + y; tr.appendChild(th);
      [money(cur, seats * price * y), money(cur, host * y)].forEach(function (s) { var td = document.createElement('td'); td.textContent = s; tr.appendChild(td); });
      body.appendChild(tr);
    }
  }
  form.addEventListener('submit', function (e) { e.preventDefault(); });
  form.addEventListener('input', run); form.addEventListener('change', run);
  run();
})();
