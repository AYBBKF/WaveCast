/* Éditeur visuel simple pour les leçons (contenteditable, sans dépendance).
   Le HTML est nettoyé côté serveur à l'enregistrement (liste blanche de balises). */
(function () {
  "use strict";

  var uploadUrl = document.body.dataset.uploadUrl;
  var csrf = (document.querySelector("input[name=csrfmiddlewaretoken]") || {}).value;

  function exec(cmd, value) {
    document.execCommand(cmd, false, value || null);
  }

  function wrapBlock(area, className) {
    var sel = window.getSelection();
    if (!sel.rangeCount) return;
    var range = sel.getRangeAt(0);
    if (!area.contains(range.commonAncestorContainer)) return;
    var div = document.createElement("div");
    div.className = className;
    var content = range.extractContents();
    if (!content.textContent.trim()) {
      var p = document.createElement("p");
      p.textContent = className === "exemple" ? "Décrivez ici un exemple concret…" : "Votre texte…";
      div.appendChild(p);
    } else {
      div.appendChild(content);
    }
    range.insertNode(div);
  }

  var tools = [
    { label: "Titre", title: "Titre de section", run: function () { exec("formatBlock", "<h2>"); } },
    { label: "Sous-titre", title: "Sous-titre", run: function () { exec("formatBlock", "<h3>"); } },
    { label: "¶", title: "Paragraphe normal", run: function () { exec("formatBlock", "<p>"); } },
    { label: "G", title: "Gras", run: function () { exec("bold"); }, style: "font-weight:800" },
    { label: "I", title: "Italique", run: function () { exec("italic"); }, style: "font-style:italic" },
    { label: "• Liste", title: "Liste à puces", run: function () { exec("insertUnorderedList"); } },
    { label: "1. Liste", title: "Liste numérotée", run: function () { exec("insertOrderedList"); } },
    { label: "Citation", title: "Citation / mise en avant", run: function () { exec("formatBlock", "<blockquote>"); } },
    { label: "Exemple", title: "Encadré « Exemple concret »", block: "exemple" },
    { label: "Astuce", title: "Encadré astuce", block: "astuce" },
    { label: "Attention", title: "Encadré attention", block: "attention" },
    { label: "Lien", title: "Insérer un lien", run: function () {
        var url = window.prompt("Adresse du lien (https://…)");
        if (url && /^https?:\/\//i.test(url)) exec("createLink", url);
      } },
    { label: "Image", title: "Insérer une image", image: true },
    { label: "Effacer", title: "Retirer la mise en forme", run: function () { exec("removeFormat"); } },
  ];

  document.querySelectorAll("input[data-editor]").forEach(function (hidden) {
    var small = hidden.dataset.editor === "key_takeaway";
    var wrap = document.createElement("div");
    wrap.className = "editor";
    var bar = document.createElement("div");
    bar.className = "editor-toolbar";
    bar.setAttribute("role", "toolbar");
    var area = document.createElement("div");
    area.className = "editor-area prose-edit" + (small ? " small" : "");
    area.contentEditable = "true";
    area.setAttribute("role", "textbox");
    area.setAttribute("aria-multiline", "true");
    area.dataset.placeholder = small ? "Les 2 à 4 points essentiels de la leçon (liste à puces conseillée)…" : "Rédigez votre leçon : titres, paragraphes, listes, exemples, images…";
    area.innerHTML = hidden.value;

    var fileInput = document.createElement("input");
    fileInput.type = "file";
    fileInput.accept = "image/png,image/jpeg,image/webp,image/gif";
    fileInput.hidden = true;
    fileInput.addEventListener("change", function () {
      if (!fileInput.files.length) return;
      var fd = new FormData();
      fd.append("image", fileInput.files[0]);
      fetch(uploadUrl, { method: "POST", body: fd, headers: { "X-CSRFToken": csrf }, credentials: "same-origin" })
        .then(function (r) { return r.json(); })
        .then(function (data) {
          if (data.url) {
            area.focus();
            var alt = window.prompt("Texte alternatif de l'image (description courte)", "") || "";
            exec("insertHTML", '<img src="' + data.url + '" alt="' + alt.replace(/"/g, "&quot;") + '">');
          } else {
            window.alert(data.error || "Téléversement impossible.");
          }
        })
        .catch(function () { window.alert("Téléversement impossible."); });
      fileInput.value = "";
    });

    (small ? tools.filter(function (t) { return ["G", "I", "• Liste", "1. Liste", "Effacer"].indexOf(t.label) >= 0; }) : tools).forEach(function (t) {
      var b = document.createElement("button");
      b.type = "button";
      b.textContent = t.label;
      b.title = t.title;
      if (t.style) b.setAttribute("style", t.style);
      b.addEventListener("mousedown", function (e) { e.preventDefault(); });
      b.addEventListener("click", function () {
        area.focus();
        if (t.image) { fileInput.click(); return; }
        if (t.block) { wrapBlock(area, t.block); return; }
        t.run();
      });
      bar.appendChild(b);
    });

    wrap.appendChild(bar);
    wrap.appendChild(area);
    wrap.appendChild(fileInput);
    hidden.parentNode.insertBefore(wrap, hidden);

    var form = hidden.form;
    if (form) form.addEventListener("submit", function () { hidden.value = area.innerHTML; });
  });
})();
