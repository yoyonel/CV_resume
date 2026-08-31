# Résolution des Issues DevTools Chromium (Accessibilité Formulaire & Dimensions d'Images)

**Date** : 2026-08-31  
**Auteur** : Yohan ATTY  
**Branche** : `fix/devtools-issues-and-image-aspect-ratio`  
**Composants impactés** : [`site_template/index.html.j2`](file:///home/latty/Prog/__PERSO__/CV_resume/site_template/index.html.j2)

---

## 1. Contexte & Diagnostic

L'audit DevTools Chromium (onglet *Issues*) sur le site déployé a identifié deux catégories d'améliorations :

### A. Issue Formulaire : `A form field element should have an id or name attribute`
* **Élément concerné** : `<input id="paletteSearchInput" class="palette-search-input">`
* **Explication** : Bien que doté d'un `id`, le champ de recherche ne disposait pas d'attribut standard `name`. Chromium et les moteurs d'assistance recommandent la présence conjointe des attributs `id` et `name` pour garantir la compatibilité des formulaires W3C et l'autocomplétion sans warning.
* **Correction** : Ajout explicite de `name="palette_search"`.

### B. Issue Performance & Layout Shift : `Lazy-loaded images should have explicit dimensions` (7 éléments)
* **Éléments concernés** : Les 7 vignettes de cartes projets R&D dotées de l'attribut `loading="lazy"`.
* **Explication** : En CSS, `.project-media-main` et `.project-media-main img` définissaient une hauteur fixe `height: 200px` et `width: 100%` sans déclarer formellement la propriété CSS `aspect-ratio: 16 / 9`. Lors du défilement, le navigateur allouait initialement un cadre sans ratio intrinsèque garanti, risquant d'induire du Cumulative Layout Shift (CLS).
* **Correction** :
  - Déclaration explicite de `aspect-ratio: 16 / 9;` sur `.project-media-main` et `.project-media-main img`.
  - Passage de `height: auto; max-height: 220px;` pour préserver le ratio natif 16:9 (`800x450`).

---

## 2. Diffs Appliqués

```diff
--- a/site_template/index.html.j2
+++ b/site_template/index.html.j2
@@ -876,7 +876,9 @@
     .project-media-main {
       position: relative;
       width: 100%;
-      height: 200px;
+      aspect-ratio: 16 / 9;
+      height: auto;
+      max-height: 220px;
       overflow: hidden;
       cursor: pointer;
       display: flex;
@@ -887,6 +889,7 @@
     .project-media-main img {
       width: 100%;
       height: 100%;
+      aspect-ratio: 16 / 9;
       object-fit: cover;
       transition: transform 0.3s ease;
     }
@@ -1825,7 +1828,7 @@
     <div class="palette-header-box">
       <div class="palette-search-wrapper">
         <svg class="icon palette-search-icon"><use href="#icon-search"></use></svg>
-        <input type="text" id="paletteSearchInput" class="palette-search-input" placeholder="Rechercher..." autocomplete="off" spellcheck="false" oninput="handlePaletteSearch(this.value)">
+        <input type="text" id="paletteSearchInput" name="palette_search" class="palette-search-input" placeholder="Rechercher..." autocomplete="off" spellcheck="false" oninput="handlePaletteSearch(this.value)">
         <kbd class="palette-esc-kbd" onclick="closePalette()">ESC</kbd>
       </div>
     </div>
```

---

## 3. Validation

* **`task check`** : 100% PASS (Python Ruff, Pyright, AST Jinja2, Typst PDF, Mobile 5 viewports, Crawler Playwright 520 éléments, 6/6 tests de non-régression UI, 53 hyperliens valides).
