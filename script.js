/* ═══════════════════════════════════════════════════════════════════
   myDynasty — script.js
   ═══════════════════════════════════════════════════════════════════ */

/* —— Waitlist counter animation —— */
const ob = new IntersectionObserver(function(entries) {
  if (entries[0].isIntersecting) {
    animateCount(document.getElementById('cnt'), 247, 1400);
    ob.disconnect();
  }
});
ob.observe(document.querySelector('.stats'));

function animateCount(el, target, ms) {
  var v = 0, step = target / (ms / 16);
  var t = setInterval(function() {
    v += step;
    if (v >= target) { el.textContent = target; clearInterval(t); return; }
    el.textContent = Math.floor(v);
  }, 16);
}

/* —— Waitlist → Google Sheets —— */
var SHEET_URL = 'https://script.google.com/macros/s/AKfycbzuHMy4bSzBuXSdwYRslZjr9SPD6JkrkPbzanq7qUENahu2yXrgIvpmDXh1f-v3Rugm/exec';
var EMAIL_RE  = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
var _pageBorn = Date.now();

async function join(n) {
  var inp   = document.getElementById('em' + n);
  var email = inp.value.trim();

  if (!email || !EMAIL_RE.test(email)) {
    inp.classList.add('err');
    var prev = inp.placeholder;
    inp.placeholder = 'Please enter a valid email \u2191';
    inp.value = '';
    setTimeout(function() { inp.classList.remove('err'); inp.placeholder = prev; }, 2500);
    inp.focus();
    return;
  }

  var pill = inp.closest('.wl-pill, .cta-row');
  var hp   = pill ? pill.querySelector('.hp-trap') : null;
  if (hp && hp.value) return;
  if (Date.now() - _pageBorn < 2000) return;

  var btn = pill ? pill.querySelector('button') : null;
  if (btn) { btn.innerHTML = '\u2026'; btn.disabled = true; }

  try {
    await fetch(SHEET_URL, {
      method: 'POST',
      mode: 'no-cors',
      headers: { 'Content-Type': 'text/plain' },
      body: JSON.stringify({
        email: email,
        hp: hp ? hp.value : '',
        source: 'mydynasty.app',
        ts: new Date().toISOString()
      })
    });
  } catch(err) { /* network unavailable — request may still reach server */ }

  var el = document.getElementById('cnt');
  var newCount = (parseInt(el.textContent, 10) || 247) + 1;
  el.textContent = newCount;

  if (n === 1) {
    document.getElementById('wlMain').style.display = 'none';
    var ok = document.getElementById('wlOk');
    ok.classList.add('visible');
    var sc = document.getElementById('scCount');
    if (sc) sc.textContent = newCount;
    confetti({ particleCount: 120, spread: 80, origin: { y: 0.55 },
               colors: ['#f97316','#ea580c','#fbbf24','#fb923c','#fed7aa'] });
    setTimeout(function() {
      confetti({ particleCount: 60, angle: 60, spread: 55,
                 origin: { x: 0, y: 0.6 }, colors: ['#f97316','#fbbf24','#c2410c'] });
    }, 200);
    setTimeout(function() {
      confetti({ particleCount: 60, angle: 120, spread: 55,
                 origin: { x: 1, y: 0.6 }, colors: ['#f97316','#fbbf24','#c2410c'] });
    }, 400);
  } else {
    inp.value = '';
    inp.placeholder = '\u2713 You\u2019re on the list!';
    inp.style.color = 'var(--accent)';
    if (btn) btn.innerHTML = '\u2713';
  }
}

document.getElementById('em1').addEventListener('keydown', function(e) { if (e.key === 'Enter') join(1); });

/* —— Contact form → Google Sheet + mailto fallback —— */
document.getElementById('contactForm').addEventListener('submit', async function(e) {
  e.preventDefault();
  var name    = document.getElementById('cf-name').value.trim();
  var email   = document.getElementById('cf-email').value.trim();
  var message = document.getElementById('cf-message').value.trim();
  if (!name || !email || !message) return;

  var btn = this.querySelector('.cf-btn');
  btn.textContent = '\u2026';
  btn.disabled = true;

  /* 1. Send email field to Google Sheet (same script as waitlist) */
  try {
    await fetch(SHEET_URL, {
      method: 'POST',
      mode: 'no-cors',
      headers: { 'Content-Type': 'text/plain' },
      body: JSON.stringify({
        email:   email,
        name:    name,
        message: message,
        source:  'contact-form',
        ts:      new Date().toISOString()
      })
    });
  } catch(err) { /* silent */ }

  /* 2. Open mailto so the full message also arrives in your inbox */
  var subject = encodeURIComponent('myDynasty — message from ' + name);
  var body    = encodeURIComponent('Name: ' + name + '\nEmail: ' + email + '\n\n' + message);
  window.open('mailto:hello@mydynasty.app?subject=' + subject + '&body=' + body);

  /* 3. Show success state */
  this.innerHTML =
    '<div class="cf-ok">' +
      '<div class="cf-ok-icon">&#10003;</div>' +
      '<div class="cf-ok-title">Message sent!</div>' +
      '<div class="cf-ok-sub">We\'ll get back to you soon &nbsp;&#128521;</div>' +
    '</div>';
});

/* —— Tree SVG lines (app-exact: red dual-stroke spouse, blue bezier parent-child) —— */
function drawTree() {
  var svg  = document.getElementById('treeSvg');
  var wrap = document.getElementById('treeWrap');
  var wr = wrap.getBoundingClientRect(), sy = window.scrollY, sx = window.scrollX;

  function c(id) {
    var r = document.getElementById(id).getBoundingClientRect();
    return {
      cx  : r.left + sx - (wr.left + sx) + r.width  / 2,
      topY: r.top  + sy - (wr.top  + sy),
      botY: r.top  + sy - (wr.top  + sy) + r.height
    };
  }

  var pts  = ['p1','p2','p3','p4','p5','p6','p7','p8'].map(c);
  var p1=pts[0],p2=pts[1],p3=pts[2],p4=pts[3],p5=pts[4],p6=pts[5],p7=pts[6],p8=pts[7];
  var cpl1 = { cx: (p1.cx+p2.cx)/2, y: p1.botY };
  var cpl2 = { cx: (p3.cx+p4.cx)/2, y: p3.botY };
  var cpl3 = { cx: (p5.cx+p6.cx)/2, y: p5.botY };
  var g3   = { cx: (p7.cx+p8.cx)/2, topY: p7.topY };

  svg.setAttribute('height', wrap.getBoundingClientRect().height);
  [].forEach.call(svg.querySelectorAll('path,circle,line'), function(n) { n.remove(); });

  var NS = 'http://www.w3.org/2000/svg';

  function pcLine(x1, y1, x2, y2) {
    var g = (y2 - y1) * 0.46;
    var d = 'M'+x1+','+y1+' C'+x1+','+(y1+g)+' '+x2+','+(y2-g)+' '+x2+','+y2;
    [['6','.28'],['1.5','.9']].forEach(function(sw) {
      var path = document.createElementNS(NS, 'path');
      path.setAttribute('d', d);
      path.setAttribute('stroke', 'url(#pcLine)');
      path.setAttribute('stroke-width', sw[0]);
      path.setAttribute('fill', 'none');
      path.setAttribute('opacity', sw[1]);
      svg.appendChild(path);
    });
    [[x1,y1],[x2,y2]].forEach(function(pt) {
      var circle = document.createElementNS(NS, 'circle');
      circle.setAttribute('cx', pt[0]);
      circle.setAttribute('cy', pt[1]);
      circle.setAttribute('r', '4');
      circle.setAttribute('fill', 'url(#pcLine)');
      circle.setAttribute('opacity', '.65');
      svg.appendChild(circle);
    });
  }

  pcLine(cpl1.cx, cpl1.y, p5.cx, p5.topY);
  pcLine(cpl2.cx, cpl2.y, p6.cx, p6.topY);
  pcLine(cpl3.cx, cpl3.y, g3.cx,  g3.topY);
}

window.addEventListener('load', function() { setTimeout(drawTree, 300); });
window.addEventListener('resize', drawTree);
