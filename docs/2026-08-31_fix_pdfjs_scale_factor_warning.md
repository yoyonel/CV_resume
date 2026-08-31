# Correctif PDF.js & Modales : Suppression des Warnings `--scale-factor` et `Blocked aria-hidden`

**Date** : 2026-08-31  
**Branche** : `fix/pdfjs-scale-factor-warning`  
**Composant** : `site_template/index.html.j2` (Visualiseur Document ISO, TextLayer PDF.js & Modales `<sl-dialog>`)

---

## 1. Contexte & Problématiques

### A. Warning PDF.js `--scale-factor`

Lors de la navigation sur le site en mode Document ISO (`viewDocument`), une erreur/avertissement apparaissait dans la console DevTools :

```text
The `--scale-factor` CSS-variable must be set, to the same value as `viewport.scale`, 
either on the `container`-element itself or higher up in the DOM. (pdf.min.js:22)
```

**Cause Racine** :
1. **Rendu aveugle de toutes les pages** : En mode Document `Page Simple` (`mode-single`), la Page 2 (`#pageContainer2`) est masquée via `display: none`. Or la fonction `renderDocPages()` déclenchait le rendu simultané de la page 1 et de la page 2.
2. **Calcul CSS sur élément masqué (`display: none`)** :
   - Lorsque Chromium évalue `getComputedStyle(textLayer2).getPropertyValue('--scale-factor')` sur un élément masqué, il renvoie une chaîne vide `""`.
   - La routine interne de PDF.js tente de parser cette valeur : `parseFloat("")` -> `NaN`.
   - La condition de validation `scaleFactor !== viewport.scale` devenant vraie (`NaN !== 1.411`), PDF.js émet le warning console.

---

### B. Warning Accessibilité `Blocked aria-hidden` sur `<sl-dialog>`

Lors de l'ouverture/fermeture des modales d'images (ex: lightbox `rust-firework`) ou vidéos :

```text
Blocked aria-hidden on an element because its descendant retained focus. 
The focus must not be hidden from assistive technology users.
Element with focus: <div.dialog__panel>
```

**Cause Racine** :
- Chromium 128+ interdit formellement d'appliquer `aria-hidden="true"` sur un élément de dialogue lorsque le focus actif (`document.activeElement`) se trouve encore sur `dialog__panel` ou un de ses enfants sans avoir été préalablement libéré (`blur()`).

---

## 2. Solutions Appliquées

1. **Rendu sélectif selon le mode** :
   - En mode `mode-single` : Rendu exclusif de la page active (`docPageNum === 1 ? page1 : page2`).
   - En modes `mode-dual` et `mode-continuous` : Rendu parallèle de toutes les pages visibles.
2. **Garde d'affichage DOM (`offsetParent === null`)** :
   - Ajout d'une condition `container.offsetParent === null` dans `renderDocPage()` pour interdire tout rendu sur un conteneur non affiché dans le viewport.
3. **Propagation Globale de `--scale-factor`** :
   - Assignation dynamique de `--scale-factor` sur `document.documentElement` (`:root`) ainsi que sur le conteneur et le `textLayerDiv`.
4. **Gestion de Focus sur `<sl-dialog>`** :
   - Écouteurs globaux `sl-hide` et `sl-after-hide` sur tous les `<sl-dialog>` pour libérer (`blur()`) le focus actif avant l'application de `aria-hidden="true"`.
   - Attributs `data-card-idx` et `data-title` sur les déclencheurs avec gestionnaire `openImageModalByElem(this)`.

---

## 3. Validation

- [x] Compilation du site statique (`task site:build`)
- [x] Linting Python & Types (`ruff` & `pyright`)
- [x] Validation AST Jinja2
- [x] Test Mobile Responsiveness (5 viewports Playwright)
- [x] Test Console Guard & Click Crawler (497 éléments interactifs avec zéro erreur)
- [x] Test E2E UI Regressions (6/6 tests)
