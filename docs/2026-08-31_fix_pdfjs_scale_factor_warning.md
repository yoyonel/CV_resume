# Correctif PDF.js : Suppression du Warning `--scale-factor`

**Date** : 2026-08-31  
**Branche** : `fix/pdfjs-scale-factor-warning`  
**Composant** : `site_template/index.html.j2` (Visualiseur Document ISO & TextLayer PDF.js)

---

## 1. Contexte & Problématique

Lors de la navigation sur le site en mode Document ISO (`viewDocument`), une erreur/avertissement apparaissait dans la console DevTools :

```text
The `--scale-factor` CSS-variable must be set, to the same value as `viewport.scale`, 
either on the `container`-element itself or higher up in the DOM. (pdf.min.js:22)
```

### Cause Racine

1. **Rendu aveugle de toutes les pages** : En mode Document `Page Simple` (`mode-single`), la Page 2 (`#pageContainer2`) est masquée via `display: none`. Or la fonction `renderDocPages()` déclenchait le rendu simultané de la page 1 et de la page 2.
2. **Calcul CSS sur élément masqué (`display: none`)** :
   - Lorsque Chromium évalue `getComputedStyle(textLayer2).getPropertyValue('--scale-factor')` sur un élément masqué, il renvoie une chaîne vide `""`.
   - La routine interne de PDF.js tente de parser cette valeur : `parseFloat("")` -> `NaN`.
   - La condition de validation `scaleFactor !== viewport.scale` devenant vraie (`NaN !== 1.411`), PDF.js émet le warning console.

---

## 2. Solution Appliquée

1. **Rendu sélectif selon le mode** :
   - En mode `mode-single` : Rendu exclusif de la page active (`docPageNum === 1 ? page1 : page2`).
   - En modes `mode-dual` et `mode-continuous` : Rendu parallèle de toutes les pages visibles.
2. **Garde d'affichage DOM (`offsetParent === null`)** :
   - Ajout d'une condition `container.offsetParent === null` dans `renderDocPage()` pour interdire tout rendu sur un conteneur non affiché dans le viewport.
3. **Propagation Globale de `--scale-factor`** :
   - Assignation dynamique de `--scale-factor` sur `document.documentElement` (`:root`) ainsi que sur le conteneur et le `textLayerDiv`.

---

## 3. Validation

- [x] Compilation du site statique (`task site:build`)
- [x] Linting Python & Types (`ruff` & `pyright`)
- [x] Validation AST Jinja2
- [x] Test Mobile Responsiveness (5 viewports Playwright)
- [x] Test Console Guard & Click Crawler (497 éléments interactifs avec zéro erreur)
- [x] Test E2E UI Regressions (6/6 tests)
