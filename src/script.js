(function () {
  // live date in the hero corner, like the day line on a magazine page
  try {
    var d = new Date();
    document.getElementById('today').textContent = d.toLocaleDateString('en-IN', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' });
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

  // newsletter: preview only, the live site posts this to the form service
  var form = document.getElementById('letter');
  var status = document.getElementById('letter-status');
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var email = document.getElementById('letter-email');
    var consent = document.getElementById('letter-consent');
    if (!email.value || !email.checkValidity()) { status.textContent = 'Enter an email address like name@example.com.'; email.focus(); return; }
    if (!consent.checked) { status.textContent = 'Tick the box to agree before we can send you the letter.'; consent.focus(); return; }
    status.textContent = 'This is the preview, so nothing was sent. On the live site this adds you to the list.';
  });
})();
