(function () {
  var still = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // date and time in New Delhi
  var clock = document.getElementById('today');
  function tick() {
    if (!clock) return;
    try {
      var d = new Date();
      clock.textContent = d.toLocaleDateString('en-IN', { weekday: 'long', day: 'numeric', month: 'long', timeZone: 'Asia/Kolkata' }) + ', ' +
        d.toLocaleTimeString('en-IN', { hour: 'numeric', minute: '2-digit', timeZone: 'Asia/Kolkata' }).toLowerCase() + ' IST';
    } catch (e) {}
  }
  tick(); setInterval(tick, 30000);

  // a hairline under the header once the page moves
  var head = document.getElementById('head');
  function onScroll() { if (head) head.classList.toggle('solid', window.scrollY > 8); }
  window.addEventListener('scroll', onScroll, { passive: true }); onScroll();

  // phone menu
  var overlay = document.getElementById('overlay');
  var openBtn = document.getElementById('menu-open');
  var closeBtn = document.getElementById('menu-close');
  function closeMenu(refocus) { overlay.hidden = true; openBtn.setAttribute('aria-expanded', 'false'); if (refocus) openBtn.focus(); }
  openBtn.addEventListener('click', function () { overlay.hidden = false; openBtn.setAttribute('aria-expanded', 'true'); closeBtn.focus(); });
  closeBtn.addEventListener('click', function () { closeMenu(true); });
  overlay.addEventListener('click', function (e) { if (e.target.tagName === 'A') closeMenu(false); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && !overlay.hidden) closeMenu(true); });

  // the one motion: content fades up gently as it arrives
  if (!still && 'IntersectionObserver' in window) {
    var items = document.querySelectorAll('.tile, .brand-list li, .pillar, .facts li, .brand-card, .cases li, .principles li, .part, .episode, .stepper li, .gallery .photo');
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); } });
    }, { rootMargin: '0px 0px -8% 0px' });
    items.forEach(function (el) { el.classList.add('rv'); io.observe(el); });
  }

  // chapter bar shows where you are
  var links = document.querySelectorAll('.ln-links a[href^="#"]');
  if (links.length && 'IntersectionObserver' in window) {
    var map = {};
    links.forEach(function (a) { var t = document.getElementById(a.getAttribute('href').slice(1)); if (t) map[t.id] = a; });
    var spy = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        links.forEach(function (a) { a.removeAttribute('aria-current'); });
        if (map[en.target.id]) map[en.target.id].setAttribute('aria-current', 'true');
      });
    }, { rootMargin: '-45% 0px -50% 0px' });
    Object.keys(map).forEach(function (id) { spy.observe(document.getElementById(id)); });
  }

  // copy buttons
  var toast = document.getElementById('toast'), tid;
  function say(msg) { if (!toast) return; toast.textContent = msg; toast.classList.add('show'); clearTimeout(tid); tid = setTimeout(function () { toast.classList.remove('show'); }, 2000); }
  document.querySelectorAll('[data-copy]').forEach(function (b) {
    b.addEventListener('click', function () {
      var v = b.getAttribute('data-copy');
      (navigator.clipboard ? navigator.clipboard.writeText(v) : Promise.reject()).then(function () {
        b.textContent = 'Copied'; say('Copied ' + v); setTimeout(function () { b.textContent = 'Copy'; }, 1600);
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

  // photographs fade in once loaded
  document.querySelectorAll('img[loading="lazy"]').forEach(function (im) {
    if (im.complete) return;
    im.classList.add('pending');
    var done = function () { im.classList.remove('pending'); };
    im.addEventListener('load', done, { once: true }); im.addEventListener('error', done, { once: true });
  });

  // "New" on episodes out in the last 30 days
  document.querySelectorAll('[data-released]').forEach(function (el) {
    var d = new Date(el.getAttribute('data-released'));
    if (!isNaN(d) && (Date.now() - d) / 864e5 < 30) el.insertAdjacentHTML('beforeend', ' <span class="new">New</span>');
  });

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
})();
