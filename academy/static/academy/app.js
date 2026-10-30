/* Flux Intelligent Academy — interactions légères (aucune dépendance). */
(function () {
  "use strict";

  // Menu mobile et sommaire repliable
  document.querySelectorAll("[data-toggle]").forEach(function (btn) {
    var target = document.getElementById(btn.getAttribute("data-toggle"));
    if (!target) return;
    btn.addEventListener("click", function () {
      var open = target.classList.toggle("open");
      btn.setAttribute("aria-expanded", open ? "true" : "false");
    });
  });

  // Empêche les doubles envois (examen, réclamation, certificat).
  document.querySelectorAll("form[data-once]").forEach(function (form) {
    form.addEventListener("submit", function (e) {
      if (form.dataset.sent === "1") { e.preventDefault(); return; }
      form.dataset.sent = "1";
      form.querySelectorAll("button[type=submit]").forEach(function (b) {
        b.setAttribute("disabled", "disabled");
        if (b.dataset.loading) b.textContent = b.dataset.loading;
      });
    });
  });

  // Examen : compteur de réponses et confirmation si des questions restent vides.
  var exam = document.getElementById("exam-form");
  if (exam) {
    var total = exam.querySelectorAll("fieldset.question").length;
    var counter = document.getElementById("answered-count");
    var update = function () {
      var answered = exam.querySelectorAll("fieldset.question input:checked").length;
      if (counter) counter.textContent = answered + " / " + total;
      return answered;
    };
    exam.addEventListener("change", update);
    update();
    exam.addEventListener("submit", function (e) {
      var missing = total - update();
      if (missing > 0 && exam.dataset.sent !== "1") {
        var ok = window.confirm(missing + " question(s) sans réponse compteront comme fausses. Envoyer quand même ?");
        if (!ok) { e.preventDefault(); e.stopImmediatePropagation(); }
      }
    }, true);
  }
})();
