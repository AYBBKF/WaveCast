/*! Flux Intelligent — suivi des leads GA4/Ads (V4). Aucune donnée personnelle transmise.
 * generate_lead : uniquement après confirmation serveur (Forminator « submit:success », devis IA « fdi_final » success).
 * click_whatsapp / click_phone : intentions de contact (événements d'engagement, pas des leads).
 * devis_open, devis_start, devis_contact_saved, devis_submit_error, contact_submit_error : étapes du parcours.
 * Respect du consentement : passe uniquement par gtag() (Consent Mode de Site Kit inchangé).
 */
(function () {
  'use strict';
  if (window.__fiLeadTracking) return; window.__fiLeadTracking = true;
  var DEDUP_MS = 4000, last = {};
  function send(name, params) {
    params = params || {};
    params.page_path = location.pathname;
    params.send_to = 'G-1JX1J3TWVZ'; // GA4 uniquement : évite les doublons vers Ads (conteneur Ads chargé deux fois) ; Ads importera depuis GA4
    if (typeof window.gtag === 'function') window.gtag('event', name, params);
  }
  function onceWithin(key) { var now = Date.now(); if (last[key] && now - last[key] < DEDUP_MS) return false; last[key] = now; return true; }
  function oncePerSession(key) { try { if (sessionStorage.getItem('fi_ev_' + key)) return false; sessionStorage.setItem('fi_ev_' + key, '1'); } catch (e) {} return true; }

  /* 1. Forminator : événement jQuery émis par Forminator uniquement après une réponse serveur réussie */
  function bindForminator() {
    var $ = window.jQuery; if (!$ || bindForminator.done) return; bindForminator.done = true;
    $(document).on('forminator:form:submit:success', function (e) {
      var f = e.target && e.target.closest ? e.target.closest('form') || e.target : e.target;
      var id = (f && f.getAttribute && f.getAttribute('data-form-id')) || 'inconnu';
      if (!onceWithin('fm_' + id)) return;
      send('generate_lead', { lead_source: 'formulaire_contact', form_id: 'forminator_' + id, method: 'forminator' });
    });
    $(document).on('forminator:form:submit:failed', function (e) {
      var f = e.target && e.target.closest ? e.target.closest('form') || e.target : e.target;
      var id = (f && f.getAttribute && f.getAttribute('data-form-id')) || 'inconnu';
      if (onceWithin('fmerr_' + id)) send('contact_submit_error', { form_id: 'forminator_' + id });
    });
  }

  /* 2. Devis IA : observation des réponses aux actions admin-ajax fdi_partiel / fdi_final (plugin non modifié) */
  function bindDevis() {
    var app = document.getElementById('fdi-app') || document.querySelector('[data-fdi], .fdi-app, #fdi');
    if (!app || bindDevis.done) return; bindDevis.done = true;
    if (oncePerSession('devis_open_' + location.pathname)) send('devis_open', { form_id: 'devis_ia' });
    var started = false;
    app.addEventListener('input', function () { if (!started) { started = true; send('devis_start', { form_id: 'devis_ia' }); } }, true);
    var ofetch = window.fetch; if (!ofetch || ofetch.__fi) return;
    var wrapped = function (input, init) {
      var action = null;
      try { if (init && init.body && typeof init.body.get === 'function') action = init.body.get('action'); } catch (e) {}
      var p = ofetch.apply(this, arguments);
      if (action !== 'fdi_partiel' && action !== 'fdi_final') return p;
      return p.then(function (r) {
        r.clone().json().then(function (j) {
          var ok = !!(j && j.success), lid = ok && j.data && j.data.lead_id ? String(j.data.lead_id) : '';
          if (action === 'fdi_partiel' && ok && oncePerSession('devis_contact_' + lid)) send('devis_contact_saved', { form_id: 'devis_ia' });
          if (action === 'fdi_final') {
            if (ok && oncePerSession('devis_lead_' + (lid || Date.now()))) send('generate_lead', { lead_source: 'devis_ia', form_id: 'devis_ia', method: 'devis_ia' });
            else if (!ok) send('devis_submit_error', { form_id: 'devis_ia', error_type: 'serveur' });
          }
        }).catch(function () { if (action === 'fdi_final') send('devis_submit_error', { form_id: 'devis_ia', error_type: 'reponse_invalide' }); });
        return r;
      }, function (err) { if (action === 'fdi_final') send('devis_submit_error', { form_id: 'devis_ia', error_type: 'reseau' }); throw err; });
    };
    wrapped.__fi = true; window.fetch = wrapped;
  }

  /* 3. Intentions de contact : clics WhatsApp et téléphone (délégation, sans numéro transmis) */
  document.addEventListener('click', function (e) {
    var a = e.target && e.target.closest ? e.target.closest('a[href]') : null; if (!a) return;
    var h = a.getAttribute('href') || '';
    var zone = a.closest('header') ? 'entete' : a.closest('footer') ? 'pied' : 'contenu';
    if (/^tel:/i.test(h)) { if (onceWithin('tel_' + zone)) send('click_phone', { link_location: zone }); }
    else if (/(wa\.me\/|api\.whatsapp\.com|whatsapp:\/\/)/i.test(h)) { if (onceWithin('wa_' + zone)) send('click_whatsapp', { link_location: zone }); }
  }, true);

  function init() { bindForminator(); bindDevis(); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
  window.addEventListener('load', init);
})();
