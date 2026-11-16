/* Data Portal — Supabase client, tier helpers, and section gating.
   All authorization lives in the database; this layer is UX only. */
(function () {
  'use strict';

  var SB_URL = 'https://weoqdchulumtdsamcsdi.supabase.co';
  var SB_KEY = 'sb_publishable_0EMmDUAYP20wlykVeLHb-w_5lJoB4z2';
  var TIER_RANK = { guest: 0, member: 1, admin: 2 };

  var client = window.supabase.createClient(SB_URL, SB_KEY);

  var state = { ready: false, tier: 'guest', displayName: null, pages: null };
  var readyPromise = null;

  function rpc(name, args) {
    return client.schema('portal').rpc(name, args || {}).then(function (res) {
      if (res.error) {
        var e = new Error(res.error.message || 'RPC error');
        e.detail = res.error;
        throw e;
      }
      return res.data;
    });
  }

  function getSession() {
    return client.auth.getSession()
      .then(function (r) { return r.data && r.data.session; })
      .catch(function () { return null; });
  }

  function signOut() { return client.auth.signOut(); }

  function getTier() {
    return rpc('me').then(function (m) {
      state.tier = (m && m.tier) || 'guest';
      state.displayName = (m && m.display_name) || null;
      return state;
    }).catch(function () {
      state.tier = 'guest';
      state.displayName = null;
      return state;
    });
  }

  function getPages() {
    return rpc('pages').then(function (p) {
      state.pages = Array.isArray(p) ? p : [];
      return state.pages;
    }).catch(function () {
      state.pages = null;
      return null;
    });
  }

  function tierRank(t) { return TIER_RANK[t] == null ? 0 : TIER_RANK[t]; }
  function tierAllows(minTier) { return tierRank(state.tier) >= tierRank(minTier); }

  function pageVisible(page) {
    if (!state.pages) return true; // backend unavailable — degrade, don't block
    return state.pages.some(function (p) { return p.page === page && p.visible; });
  }

  function guardPage(page) {
    if (!pageVisible(page)) {
      window.location.href = 'index.html?denied=' + encodeURIComponent(page);
      return false;
    }
    return true;
  }

  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  function injectAuth() {
    var hero = document.querySelector('.portal-hero');
    if (!hero) return;
    var bar = document.createElement('div');
    bar.className = 'portal-auth';
    var badge = '<span class="tier-badge tier-' + esc(state.tier) + '">' + esc(state.tier) + '</span>';
    if (state.tier === 'guest') {
      bar.innerHTML = badge +
        '<span class="portal-auth-name">Browsing as guest</span>' +
        '<a class="btn btn-sm btn-outline-primary portal-auth-btn" href="../login.html">Sign in</a>';
    } else {
      bar.innerHTML = badge +
        '<span class="portal-auth-name">Signed in as <strong>' + esc(state.displayName || state.tier) + '</strong></span>' +
        '<button type="button" class="btn btn-sm btn-outline-primary portal-auth-btn" id="portal-signout">Sign out</button>';
      bar.querySelector('#portal-signout').addEventListener('click', function () {
        signOut().finally(function () { window.location.href = '../login.html'; });
      });
    }
    hero.appendChild(bar);
    if (state.tier === 'guest') {
      var note = document.createElement('p');
      note.className = 'portal-guest-note';
      note.textContent = 'Sign in for more.';
      hero.appendChild(note);
    }
  }

  function showDenied() {
    var box = document.getElementById('denied-notice');
    if (!box) return;
    var denied = new URLSearchParams(window.location.search).get('denied');
    if (denied) {
      box.textContent = 'The "' + denied + '" page is not available at your current access tier.';
      box.hidden = false;
    }
  }

  /* Only http(s) URLs from the DB may be linked/opened. */
  function safeUrl(u) {
    try {
      var p = new URL(u).protocol;
      return (p === 'http:' || p === 'https:') ? u : null;
    } catch (e) { return null; }
  }

  function errorMessage(err) {
    var m = (err && (err.message || '')) || '';
    if (/insufficient tier/i.test(m)) return 'This view requires a higher access tier than your account has.';
    return 'This view isn\u2019t available right now — the backend may still be under construction.';
  }

  function sectionError(el, err) {
    if (!el) return;
    el.innerHTML = '<div class="portal-error"><strong>Unavailable.</strong> ' + esc(errorMessage(err)) + '</div>';
  }

  /* Render a tiered section: removes the element entirely when the tier is too
     low (no "locked" teasers), otherwise runs renderFn and shows an inline
     friendly message on backend errors. */
  function section(minTier, el, renderFn) {
    if (!el) return Promise.resolve(false);
    if (!tierAllows(minTier)) {
      el.parentNode.removeChild(el);
      return Promise.resolve(false);
    }
    return Promise.resolve()
      .then(function () { return renderFn(el); })
      .catch(function (err) { sectionError(el, err); return true; });
  }

  /* One-shot page bootstrap: resolve tier + visible pages, optionally guard the
     current page, inject the auth bar into .portal-hero. Resolves false if the
     page guard redirected. */
  function ready(opts) {
    opts = opts || {};
    if (!readyPromise) {
      readyPromise = getTier()
        .then(getPages)
        .then(function () {
          state.ready = true;
          injectAuth();
          showDenied();
          return opts.page ? guardPage(opts.page) : true;
        });
    }
    return readyPromise;
  }

  window.Portal = {
    client: client,
    rpc: rpc,
    getSession: getSession,
    signOut: signOut,
    getTier: getTier,
    getPages: getPages,
    tierRank: tierRank,
    tierAllows: tierAllows,
    guardPage: guardPage,
    section: section,
    sectionError: sectionError,
    ready: ready,
    esc: esc,
    safeUrl: safeUrl,
    state: state
  };
})();
