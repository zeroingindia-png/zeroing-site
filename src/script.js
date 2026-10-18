(function () {
  // live date in the hero corner, like the day line on a magazine page
  try {
    var d = new Date();
    var t = document.getElementById('today');
    if (t) t.textContent = d.toLocaleDateString('en-IN', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' });
  } catch (e) {}

  // header ink follows the colour field underneath it
  var head = document.getElementById('head');
  var root = document.documentElement;
  var fields = document.querySelectorAll('[data-ink]');
  function setInk(el) {
    root.style.setProperty('--ink', 'var(--' + el.dataset.ink + ')');
    root.style.setProperty('--field', 'var(--' + el.dataset.field + ')');
  }
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) setInk(en.target); });
    }, { rootMargin: '-0px 0px -92% 0px', threshold: 0 });
    fields.forEach(function (f) { io.observe(f); });
  }
  setInk(fields[0]);

  // mobile menu
  var overlay = document.getElementById('overlay');
  var openBtn = document.getElementById('menu-open');
  var closeBtn = document.getElementById('menu-close');
  function close() { overlay.hidden = true; openBtn.setAttribute('aria-expanded', 'false'); openBtn.focus(); }
  openBtn.addEventListener('click', function () { overlay.hidden = false; openBtn.setAttribute('aria-expanded', 'true'); closeBtn.focus(); });
  closeBtn.addEventListener('click', close);
  overlay.addEventListener('click', function (e) { if (e.target.tagName === 'A') { overlay.hidden = true; openBtn.setAttribute('aria-expanded', 'false'); } });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && !overlay.hidden) close(); });

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
