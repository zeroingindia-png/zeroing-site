(function () {
  var root = document.documentElement;
  var still = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // live date in the hero corner, like the day line on a magazine page
  try {
    var t = document.getElementById('today');
    if (t) t.textContent = new Date().toLocaleDateString('en-IN', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' });
  } catch (e) {}

  // header ink follows the colour field underneath it; once the page moves, the header turns to frosted glass
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
      if (head) head.classList.toggle('solid', y > 60);
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
        status.textContent = bad.type === 'checkbox' ? (bad.name === 'declaration' ? 'Tick the box to confirm your details are true.' : 'Tick the consent box so we can store your details.') :
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
  // ---------- small details ----------
  (function () {
    var bar = document.getElementById('progress');
    var topBtn = document.getElementById('to-top');
    var ring = document.getElementById('to-top-ring');
    var toast = document.getElementById('toast');
    var tid;
    function say(msg) {
      if (!toast) return;
      toast.textContent = msg; toast.classList.add('show');
      clearTimeout(tid); tid = setTimeout(function () { toast.classList.remove('show'); }, 2200);
    }
    // reading progress along the top edge, and on the back-to-top ring
    function progress() {
      var h = document.documentElement.scrollHeight - window.innerHeight;
      var p = h > 0 ? Math.min(window.scrollY / h, 1) : 0;
      if (bar) bar.style.transform = 'scaleX(' + p.toFixed(4) + ')';
      if (ring) ring.style.strokeDashoffset = (1 - p).toFixed(4);
      if (topBtn) topBtn.classList.toggle('show', window.scrollY > window.innerHeight * 1.2);
    }
    window.addEventListener('scroll', progress, { passive: true });
    window.addEventListener('resize', progress); progress();

    // the chapter bar shows where you are
    var links = document.querySelectorAll('.ln-links a[href^="#"]');
    if (links.length && 'IntersectionObserver' in window) {
      var map = {};
      links.forEach(function (a) { var t = document.getElementById(a.getAttribute('href').slice(1)); if (t) map[t.id] = a; });
      var spy = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) {
          if (!en.isIntersecting) return;
          links.forEach(function (a) { a.removeAttribute('aria-current'); });
          var a = map[en.target.id]; if (a) a.setAttribute('aria-current', 'true');
        });
      }, { rootMargin: '-45% 0px -50% 0px' });
      Object.keys(map).forEach(function (id) { spy.observe(document.getElementById(id)); });
    }

    // copy buttons
    document.querySelectorAll('[data-copy]').forEach(function (b) {
      b.addEventListener('click', function () {
        var v = b.getAttribute('data-copy');
        (navigator.clipboard ? navigator.clipboard.writeText(v) : Promise.reject()).then(function () {
          b.textContent = 'Copied'; say('Copied ' + v); setTimeout(function () { b.textContent = 'Copy'; }, 1800);
        }, function () { say('Select the text to copy it'); });
      });
    });

    // characters left in long answers
    document.querySelectorAll('textarea[maxlength]').forEach(function (t) {
      var max = +t.getAttribute('maxlength');
      var c = document.createElement('span'); c.className = 'count'; c.setAttribute('aria-hidden', 'true');
      t.insertAdjacentElement('afterend', c);
      function upd() { var n = max - t.value.length; c.textContent = n + ' characters left'; c.classList.toggle('low', n < max * 0.1); }
      t.addEventListener('input', upd); upd();
    });

    // photographs fade in once loaded, never pop
    document.querySelectorAll('img[loading="lazy"]').forEach(function (im) {
      if (im.complete) return;
      im.classList.add('pending');
      im.addEventListener('load', function () { im.classList.remove('pending'); }, { once: true });
      im.addEventListener('error', function () { im.classList.remove('pending'); }, { once: true });
    });

    // a quiet "New" on episodes out in the last 30 days
    document.querySelectorAll('[data-released]').forEach(function (el) {
      var d = new Date(el.getAttribute('data-released'));
      if (!isNaN(d) && (Date.now() - d) / 864e5 < 30) el.insertAdjacentHTML('beforeend', ' <span class="new">New</span>');
    });

    // time in New Delhi, beside the date
    var clock = document.getElementById('today');
    if (clock) {
      var tick = function () {
        try {
          var d = new Date();
          clock.textContent = d.toLocaleDateString('en-IN', { weekday: 'long', day: 'numeric', month: 'long', timeZone: 'Asia/Kolkata' }) + ', ' +
            d.toLocaleTimeString('en-IN', { hour: 'numeric', minute: '2-digit', timeZone: 'Asia/Kolkata' }).toLowerCase() + ' IST';
        } catch (e) {}
      };
      tick(); setInterval(tick, 30000);
    }
  })();
})();
