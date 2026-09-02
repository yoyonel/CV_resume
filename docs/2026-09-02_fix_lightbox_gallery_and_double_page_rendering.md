# Résolution des régressions UI : Double Page, Lightbox & Navigation Galerie Multi-Ressources

**Date :** 2026-09-02  
**Branche :** `feat/native-html-css-ui-migration`  
**Auteur :** Lionel ATTY / Antigravity AI  

---

## 1. Contexte & Problématiques Identifiées

Lors de la migration vers l'UI native HTML5/CSS (ADR 0001, suppression de Shoelace), plusieurs régressions et améliorations d'expérience utilisateur ont été identifiées :

1. **Régression Double Page (Vue Document ISO) :**
   - En mode « Double Page » sur grand écran, seule la Page 1 s'affichait au centre et la Page 2 passait en dessous (wrapping vertical) au lieu d'un affichage côte à côte.
2. **Affichage Lightbox Image décentré et non maximisé :**
   - L'ouverture de l'image agrandie plaçait l'image sur la gauche d'un cadre élargi à 92vw, avec le bouton `[✕]` rejeté à l'extrémité droite et un grand espace vide.
3. **Absence de navigation multi-ressources dans la Lightbox :**
   - Lorsqu'un projet comporte plusieurs visuels (ex: `suckless-odin` avec vue PBR et vue Profiler), la modale ne permettait pas de naviguer entre les visuels, et les touches fléchées faisaient défiler la page web en arrière-plan.
4. **Cache HTTP persistant sur les captures de projets (`cv-resume-doc.png`) :**
   - Une capture prise prématurément (canvas blanc pendant le chargement PDF.js) restait bloquée dans le cache du navigateur local (`localhost:8000`), masquant la capture réelle à jour sur le disque.

---

## 2. Causes Racines & Solutions Appliquées

### A. Fix Double Page (Côte à côte sur Desktop)

- **Cause :**
  - La classe `.pages-wrapper.mode-dual` autorisait `flex-wrap: wrap`.
  - `.pdf-page-container` avait un `margin: 0 auto` qui consommait l'espace horizontal disponible.
  - La largeur de page dans JavaScript `renderDocPage()` était fixée à 840px indépendamment de l'espace disponible (840px * 2 + gap = 1704px > largeur disponible sur écrans 1080p avec marge).
- **Solution :**
  - CSS : `flex-wrap: nowrap`, `margin: 0` sur `.pages-wrapper.mode-dual .pdf-page-container`.
  - JS : Calcul dynamique de la largeur cible par page :
    ```javascript
    if (docMode === 'dual' && !isMobile) {
      baseWidth = Math.min(840, Math.max(340, Math.floor((maxAvail - 32) / 2)));
    }
    ```
  - Résultat : Les 2 pages s'affichent parfaitement côte à côte et s'adaptent automatiquement à toute largeur d'écran (1920px, 1440px, 1280px).

---

### B. Fix Centrage & Maximisation Lightbox

- **Cause :**
  - L'élément natif `<dialog>` avec `max-width: 92vw` et sans conteneur flex interne alignait les éléments en block standard.
- **Solution :**
  - Ajout d'un conteneur `.image-dialog-wrapper` en `display: inline-flex; flex-direction: column; align-items: center;`.
  - `dialog.image-dialog img` dimensionné avec `max-width: 90vw; max-height: 80vh; object-fit: contain;`.
  - Bouton `[✕]` flottant circulaire fixé au coin supérieur droit (`top: -14px; right: -14px;`).

---

### C. Navigation Galerie Multi-Ressources & Verrouillage Scroll

- **Solution :**
  - Détection automatique des ressources associées à la carte (`.media-thumb-btn-${cardIdx}`).
  - Ajout de boutons de navigation latéraux `‹` (`#lightboxPrevBtn`) et `›` (`#lightboxNextBtn`).
  - Ajout d'une barre inférieure avec légende dynamique (`1 / 2`) et pastilles de miniatures cliquables (`.lightbox-thumbs`).
  - Écoute des touches clavier (`ArrowLeft`, `ArrowRight`, `ArrowUp`, `ArrowDown`, `Escape`) avec `e.preventDefault()` pour bloquer tout défilement arrière-plan.
  - Verrouillage du scroll du body : `document.body.style.overflow = 'hidden'` à l'ouverture, rétabli à la fermeture.
  - Synchronisation bidirectionnelle : le changement d'image dans la lightbox met à jour le bouton actif sur la carte du projet sous-jacente.

---

### D. Cache-Busting des Assets Locaux

- **Cause :**
  - Les serveurs de développement locaux ne renvoyant pas toujours d'en-têtes `Cache-Control: no-cache`, Chromium persistait l'ancienne capture blanche de 64.0 kB.
- **Solution :**
  - Injection dans Jinja d'un identifiant de build unique `build_id` (timestamp UTC).
  - Ajout du paramètre `?v={{ build_id }}` sur les images locales dans `site_template/index.html.j2` (en excluant les CDN externes comme YouTube pour éviter les 404).
  - Régénération des 3 captures de démonstration du site (`cv-resume-doc.png`, `cv-resume-web.png`, `cv-resume-palette.png`).

---

### E. Fix Espacement Vertical Mobile en Mode « Page Simple »

- **Cause :**
  - `.pages-wrapper` définissait un `min-height: 1188px` et un `align-items: center` par défaut.
  - Sur mobile, en mode « Page Simple », la page unique haute d'environ 540px était centrée verticalement dans les 1188px, créant un vide anormal de plus de 320px sous les boutons de contrôle.
- **Solution :**
  - Passage de `.pages-wrapper` à `min-height: auto` et `align-items: flex-start`.
  - Alignement vertical immédiat et homogène sous les boutons de contrôle sur tous les modes (Page Simple, Double Page, Continu) et tous les viewports mobiles/desktop.

---

## 3. Validation & Tests Automatisés

- Ajout du **Test 7** dans [`scripts/test_ui_regressions.py`](../scripts/test_ui_regressions.py) validant l'ouverture, la navigation clavier `ArrowRight`/`ArrowLeft`, le bouton précédent et la fermeture `Escape`.
- Exécution complète de `task check` :
  - `lint:python` (ruff) : ✅ Pass
  - `lint:types` (pyright) : ✅ Pass
  - `lint:jinja` (AST) : ✅ Pass
  - `lint:typst` : ✅ Pass
  - `site:check:html` : ✅ Pass (511 inline handlers & scripts valides)
  - `site:check:mobile` (Playwright 5 viewports) : ✅ Pass
  - `site:check:console` (Playwright runtime errors) : ✅ Pass
  - `site:check:ui` (Playwright 7 régression suites) : ✅ Pass
  - `site:check:print` : ✅ Pass
  - `links:check` (57 URLs) : ✅ Pass
