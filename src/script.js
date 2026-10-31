(function () {
  var root = document.documentElement;
  var still = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // live date in the hero corner, like the day line on a magazine page
  try {
    var t = document.getElementById('today');
    if (t) t.textContent = new Date().toLocaleDateString('en-IN', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' });
  } catch (e) {}

  // header ink follows the colour field underneath it; the header tucks away while reading down
  var head = document.getElementById('head');
  var fields = document.querySelectorAll('[data-ink]');
  function setInk(el) {
    root.style.setProperty('--ink', 'var(--' + el.dataset.ink + ')');
    root.style.setProperty('--field', 'var(--' + el.dataset.field + ')');
  }
  if (fields.length) setInk(fields[0]);
  if ('IntersectionObserver' in window) {
    var inkObs = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) setInk(en.target); });
    }, { rootMargin: '0px 0px -94% 0px' });
    fields.forEach(function (f) { inkObs.observe(f); });
  }

  // mobile menu
  var overlay = document.getElementById('overlay');
  var openBtn = document.getElementById('menu-open');
  var closeBtn = document.getElementById('menu-close');
  function closeMenu(refocus) { overlay.hidden = true; openBtn.setAttribute('aria-expanded', 'false'); if (refocus) openBtn.focus(); }
  openBtn.addEventListener('click', function () { overlay.hidden = false; openBtn.setAttribute('aria-expanded', 'true'); closeBtn.focus(); });
  closeBtn.addEventListener('click', function () { closeMenu(true); });
  overlay.addEventListener('click', function (e) { if (e.target.tagName === 'A') closeMenu(false); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && !overlay.hidden) closeMenu(true); });

  // ---------- motion ----------
  if (!still) {
    // hero headline: each word rises out of its own line
    document.querySelectorAll('.hero h1').forEach(function (h) {
      var i = 0;
      (function walk(node) {
        Array.prototype.slice.call(node.childNodes).forEach(function (n) {
          if (n.nodeType === 3) {
            var frag = document.createDocumentFragment();
            n.textContent.split(/(\s+)/).forEach(function (part) {
              if (!part) return;
              if (/^\s+$/.test(part)) { frag.appendChild(document.createTextNode(part)); return; }
              var w = document.createElement('span'); w.className = 'w';
              var s = document.createElement('span'); s.textContent = part; s.style.setProperty('--i', i++);
              w.appendChild(s); frag.appendChild(w);
            });
            node.replaceChild(frag, n);
          } else if (n.nodeType === 1 && n.tagName !== 'BR') { walk(n); }
        });
      })(h);
      h.setAttribute('aria-label', h.textContent.replace(/\s+/g, ' ').trim());
    });

    // things settle into place as they arrive, one after another
    var groups = ['.case-head', '.why-head', '.how-head', '.brands-head', '.craft-head', '.facts li', '.cases li', '.principles li',
      '.track li', '.brand-card', '.brand-list li', '.next-brands li', '.episode', '.part', '.highlights li', '.ledger p',
      '.record-text > *', '.about .idea > *', '.facts-list div', '.why-close', '.anthem', '.form-wrap', '.file-body > *',
      '.photo', '.porthole', '.listen-row', '.join h2', '.join-row', '.web', '.cine', '.stepper', '.rec-card'];
    var items = document.querySelectorAll(groups.join(','));
    var seen = new Map();
    items.forEach(function (el) {
      if (el.closest('.hero') || el.closest('.craft-track')) return;
      var n = seen.get(el.parentNode) || 0; seen.set(el.parentNode, n + 1);
      el.style.setProperty('--d', Math.min(n, 6) * 110 + 'ms');
      el.classList.add('rv');
    });
    if ('IntersectionObserver' in window) {
      var revObs = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add('in'); revObs.unobserve(en.target); } });
      }, { rootMargin: '0px 0px -12% 0px', threshold: 0.01 });
      document.querySelectorAll('.rv').forEach(function (el) { revObs.observe(el); });
    } else {
      document.querySelectorAll('.rv').forEach(function (el) { el.classList.add('in'); });
    }
    // the craft reel's own photographs reveal as they slide in
    document.querySelectorAll('.craft-item .photo').forEach(function (p, i) { p.classList.add('rv', 'in'); });

    // numbers in the ledger count up once
    var counted = document.querySelectorAll('.ledger .n');
    if (counted.length && 'IntersectionObserver' in window) {
      var cObs = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) {
          if (!en.isIntersecting) return;
          var el = en.target, to = parseInt(el.textContent, 10), start = null;
          cObs.unobserve(el);
          (function step(ts) {
            if (!start) start = ts;
            var p = Math.min((ts - start) / 1400, 1), e = 1 - Math.pow(1 - p, 4);
            el.textContent = Math.round(e * to);
            if (p < 1) requestAnimationFrame(step);
          })(performance.now());
        });
      }, { threshold: 0.6 });
      counted.forEach(function (el) { cObs.observe(el); });
    }

    // the craft reel: on wide screens, scrolling down carries the photographs sideways
    var crafts = document.querySelectorAll('.craft');
    function sizeCraft() {
      crafts.forEach(function (c) {
        var track = c.querySelector('.craft-track');
        var wide = window.innerWidth > 900;
        c.classList.toggle('pinned', wide);
        if (!wide) { track.style.transform = ''; return; }
        var travel = Math.max(0, track.scrollWidth - window.innerWidth);
        c._travel = travel;
        c.style.setProperty('--craft-h', (window.innerHeight + travel * 1.15) + 'px');
      });
    }

    // slow parallax on photographs marked for it
    var drift = document.querySelectorAll('[data-drift]');
    var ticking = false, lastY = window.scrollY;
    function frame() {
      ticking = false;
      var vh = window.innerHeight;
      crafts.forEach(function (c) {
        if (!c.classList.contains('pinned')) return;
        var r = c.getBoundingClientRect();
        var span = r.height - vh;
        var p = span > 0 ? Math.min(Math.max(-r.top / span, 0), 1) : 0;
        c.querySelector('.craft-track').style.transform = 'translate3d(' + (-p * c._travel).toFixed(1) + 'px,0,0)';
        var bar = c.querySelector('.craft-progress');
        if (bar) bar.style.setProperty('--p', p.toFixed(3));
      });
      drift.forEach(function (el) {
        var r = el.parentNode.getBoundingClientRect();
        if (r.bottom < 0 || r.top > vh) return;
        var k = parseFloat(el.dataset.drift) || 0.12;
        var off = (r.top + r.height / 2 - vh / 2) * -k;
        el.style.transform = 'translate3d(0,' + off.toFixed(1) + 'px,0)';
      });
      var y = window.scrollY;
      if (head) head.classList.toggle('tuck', y > lastY && y > 240 && overlay.hidden);
      lastY = y;
    }
    function onScroll() { if (!ticking) { ticking = true; requestAnimationFrame(frame); } }
    sizeCraft(); frame();
    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', function () { sizeCraft(); onScroll(); });
    window.addEventListener('load', function () { sizeCraft(); onScroll(); });
  }

  // every form on the site posts to /api/submit, which stores it in the Zeroing database
  var DONE = {
    join: 'Thank you. Your application is in. We will write back within 14 days.',
    guest: 'Thank you. We will look into their work and reach out ourselves.',
    contact: 'Thank you. Your message is in and we will reply by email.',
    details: 'Thank you. Your answer is saved, and it may become a lead for our research.',
    newsletter: 'You are on the list. One letter when a new conversation goes on record.'
  };
  document.querySelectorAll('form[data-form]').forEach(function (form) {
    var status = form.querySelector('.status');
    var button = form.querySelector('button[type="submit"]');
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var bad = Array.prototype.find.call(form.elements, function (el) { return el.willValidate && !el.checkValidity(); });
      if (bad) {
        status.textContent = bad.type === 'checkbox' ? 'Tick the consent box so we can store your details.' :
          bad.type === 'email' ? 'Enter an email address like name@example.com.' :
          'Fill in ' + ((form.querySelector('label[for="' + bad.id + '"]') || {}).textContent || 'every required field').trim().toLowerCase() + '.';
        bad.focus();
        return;
      }
      var data = { form: form.dataset.form };
      new FormData(form).forEach(function (v, k) { data[k] = v; });
      var consent = form.querySelector('input[name="consent"]');
      data.consent = !!(consent && consent.checked);
      var label = consent && form.querySelector('label[for="' + consent.id + '"]');
      data.consent_text = label ? label.textContent.trim() : '';
      button.disabled = true;
      status.textContent = 'Sending.';
      fetch('/api/submit', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(data) })
        .then(function (r) { return r.json().catch(function () { return { ok: false }; }); })
        .then(function (res) {
          if (res.ok) { form.reset(); status.textContent = DONE[form.dataset.form] || 'Thank you. It is in.'; }
          else { status.textContent = res.error || 'That did not go through. Try again, or email zeroingindia@gmail.com.'; }
        })
        .catch(function () { status.textContent = 'That did not go through. Check your connection and try again, or email zeroingindia@gmail.com.'; })
        .then(function () { button.disabled = false; });
    });
  });
})();
