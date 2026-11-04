/* WIM Services — nav, reveals, counters, form */
(function () {
  'use strict';

  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---- mobile nav ---- */
  var burger = document.querySelector('.burger');
  var mnav = document.querySelector('.mnav');
  if (burger && mnav) {
    burger.addEventListener('click', function () {
      var open = burger.getAttribute('aria-expanded') === 'true';
      burger.setAttribute('aria-expanded', String(!open));
      mnav.classList.toggle('is-open', !open);
    });
    mnav.addEventListener('click', function (e) {
      if (e.target.tagName === 'A') {
        burger.setAttribute('aria-expanded', 'false');
        mnav.classList.remove('is-open');
      }
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && mnav.classList.contains('is-open')) {
        burger.setAttribute('aria-expanded', 'false');
        mnav.classList.remove('is-open');
        burger.focus();
      }
    });
  }

  /* ---- sticky header shadow ---- */
  var hdr = document.querySelector('.hdr');
  if (hdr) {
    var onScroll = function () {
      hdr.classList.toggle('is-stuck', window.scrollY > 8);
    };
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  /* ---- scroll reveals ---- */
  var rv = document.querySelectorAll('.rv');
  if (rv.length) {
    if (reduce || !('IntersectionObserver' in window)) {
      rv.forEach(function (el) { el.classList.add('is-in'); });
    } else {
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) {
          if (en.isIntersecting) {
            en.target.classList.add('is-in');
            io.unobserve(en.target);
          }
        });
      }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
      rv.forEach(function (el) { io.observe(el); });
    }
  }

  /* ---- count-up stats ---- */
  var nums = document.querySelectorAll('[data-count]');
  if (nums.length && !reduce && 'IntersectionObserver' in window) {
    var cio = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        cio.unobserve(en.target);
        var el = en.target;
        var target = parseFloat(el.getAttribute('data-count'));
        var suffix = el.getAttribute('data-suffix') || '';
        var dur = 1100;
        var t0 = null;
        function tick(ts) {
          if (!t0) t0 = ts;
          var p = Math.min((ts - t0) / dur, 1);
          var eased = 1 - Math.pow(1 - p, 3);
          el.textContent = Math.round(target * eased) + suffix;
          if (p < 1) requestAnimationFrame(tick);
        }
        requestAnimationFrame(tick);
      });
    }, { threshold: 0.4 });
    nums.forEach(function (el) { cio.observe(el); });
  }

  /* ---- phone formatting + validation helpers ---- */
  function digits(s) { return (s || '').replace(/\D/g, ''); }

  function validPhone(v) {
    var d = digits(v);
    if (d.length === 11 && d.charAt(0) === '1') d = d.slice(1);
    if (d.length !== 10) return false;
    if (/^(\d)\1{9}$/.test(d)) return false;
    if (d === '1234567890') return false;
    if (/^[01]/.test(d)) return false;
    if (/^\d{3}[01]/.test(d)) return false;
    return true;
  }

  function fmtPhone(v) {
    var d = digits(v);
    if (d.length === 11 && d.charAt(0) === '1') d = d.slice(1);
    if (d.length !== 10) return v;
    return '(' + d.slice(0, 3) + ') ' + d.slice(3, 6) + '-' + d.slice(6);
  }

  var EMAIL_RE = /^[A-Za-z0-9._%+'\-]+@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}$/;
  function validEmail(v) {
    v = (v || '').trim();
    if (!v || /\s/.test(v) || v.indexOf('..') > -1) return false;
    if ((v.match(/@/g) || []).length !== 1) return false;
    return EMAIL_RE.test(v);
  }

  var TYPOS = {
    'gmial.com': 'gmail.com', 'gmai.com': 'gmail.com', 'gmail.con': 'gmail.com',
    'gmail.co': 'gmail.com', 'gnail.com': 'gmail.com', 'gmaill.com': 'gmail.com',
    'hotmial.com': 'hotmail.com', 'hotmai.com': 'hotmail.com', 'hotmail.con': 'hotmail.com',
    'yahooo.com': 'yahoo.com', 'yaho.com': 'yahoo.com', 'yahoo.con': 'yahoo.com',
    'outlok.com': 'outlook.com', 'outloo.com': 'outlook.com', 'outlook.con': 'outlook.com',
    'iclould.com': 'icloud.com', 'icloud.co': 'icloud.com', 'aol.con': 'aol.com'
  };

  /* ---- contact form ---- */
  var form = document.querySelector('[data-form]');
  if (form) {
    var status = form.querySelector('.form__status');
    var submit = form.querySelector('[type="submit"]');
    var key = form.getAttribute('data-key') || '';

    function errBox(field) {
      var wrap = field.closest('.fld');
      return wrap ? wrap.querySelector('.fld__err') : null;
    }
    function setErr(field, msg) {
      var box = errBox(field);
      if (msg) {
        field.setAttribute('aria-invalid', 'true');
        if (box) { box.textContent = msg; box.classList.add('is-on'); }
      } else {
        field.removeAttribute('aria-invalid');
        if (box) { box.textContent = ''; box.classList.remove('is-on'); }
      }
    }

    function check(field, quiet) {
      var v = (field.value || '').trim();
      var name = field.name;
      var msg = '';
      if (field.hasAttribute('required') && !v) {
        msg = 'This field is required.';
      } else if (v && name === 'email' && !validEmail(v)) {
        msg = 'Enter a valid email address.';
      } else if (v && name === 'phone' && !validPhone(v)) {
        msg = 'Enter a 10-digit US phone number.';
      } else if (field.type === 'checkbox' && field.hasAttribute('required') && !field.checked) {
        msg = 'Please confirm to continue.';
      }
      if (!quiet) setErr(field, msg);

      /* email typo nudge */
      if (name === 'email' && v && validEmail(v)) {
        var dom = v.split('@')[1].toLowerCase();
        var box = errBox(field);
        if (TYPOS[dom] && box) {
          var fixed = v.split('@')[0] + '@' + TYPOS[dom];
          box.innerHTML = 'Did you mean <a href="#" data-fix="' + fixed + '" style="color:var(--brass-dk)">' + fixed + '</a>?';
          box.classList.add('is-on');
          var a = box.querySelector('[data-fix]');
          if (a) a.addEventListener('click', function (e) {
            e.preventDefault();
            field.value = this.getAttribute('data-fix');
            setErr(field, '');
          });
        }
      }
      return !msg;
    }

    var fields = form.querySelectorAll('input[name], select[name], textarea[name]');
    fields.forEach(function (f) {
      if (f.type === 'hidden' || f.name === 'botcheck') return;
      f.addEventListener('blur', function () { setTimeout(function () { check(f); }, 200); });
      f.addEventListener('input', function () {
        if (f.getAttribute('aria-invalid') === 'true') check(f);
      });
      if (f.name === 'phone') {
        f.addEventListener('blur', function () {
          if (validPhone(f.value)) f.value = fmtPhone(f.value);
        });
      }
    });

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var ok = true;
      fields.forEach(function (f) {
        if (f.type === 'hidden' || f.name === 'botcheck') return;
        if (!check(f)) ok = false;
      });
      if (!ok) {
        var bad = form.querySelector('[aria-invalid="true"]');
        if (bad) bad.focus();
        return;
      }

      if (!key) {
        status.className = 'form__status is-err';
        status.textContent = 'This form is not connected yet. Please call or text 360-904-4060, or email warren@wimservicesllc.com.';
        return;
      }

      var data = Object.fromEntries(new FormData(form).entries());
      data.access_key = key;
      data.subject = 'New inquiry from wimservicesllc.com';
      data.consent_recorded_at = new Date().toISOString();
      data.consent_page = window.location.href;

      submit.disabled = true;
      var label = submit.textContent;
      submit.textContent = 'Sending…';
      status.className = 'form__status';
      status.textContent = '';

      fetch('https://api.web3forms.com/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify(data)
      })
        .then(function (r) { return r.json(); })
        .then(function (j) {
          if (j.success) {
            status.className = 'form__status is-ok';
            status.textContent = 'Thank you — your message has been sent. Warren will follow up personally, usually within one business day.';
            form.reset();
            if (window.gtag) window.gtag('event', 'generate_lead', { form_name: 'wim_contact' });
          } else {
            throw new Error(j.message || 'Submit failed');
          }
        })
        .catch(function () {
          status.className = 'form__status is-err';
          status.textContent = 'Something went wrong sending your message. Please call or text 360-904-4060, or email warren@wimservicesllc.com.';
        })
        .finally(function () {
          submit.disabled = false;
          submit.textContent = label;
        });
    });
  }
})();
