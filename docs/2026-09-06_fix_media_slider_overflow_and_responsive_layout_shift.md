# Résolution de l'instabilité de layout et du débordement horizontal sur le slider/galerie média

**Date :** 2026-09-06  
**Branche :** `fix/carousel-layout-shift`  
**Auteur :** Lionel ATTY / Antigravity AI  

---

## 1. Problématique UI/UX & Symptômes Identifiés

Lors de l'interaction avec le sélecteur de prévisualisations/galeries multimédias sur les cartes de projets (`.media-gallery-thumbs`) ou lors du redimensionnement dynamique (slider de redimensionnement DevTools / tablettes) :

1. **Déformation globale du layout et apparition d'une marge noire/vide à droite :**
   - Le défilement ou le clic sur les boutons de vignettes provoquait un décalage horizontal de la page entière (`window.scrollX > 0`).
   - L'espace à droite de l'écran s'élargissait progressivement, rétrécissant visuellement la colonne de contenu web.

2. **Éclatement en 2 colonnes étroites entre 641px et 860px :**
   - La grille `.projects-grid` utilisait `grid-template-columns: repeat(auto-fit, minmax(min(100%, 280px), 1fr))` avec un repli à 1 colonne limité à `max-width: 640px`.
   - Sur tablettes et viewports intermédiaires (641px - 860px), la grille créait 2 colonnes trop étroites (~284px) pour des fiches de projets riches (images 16:9, descriptions techniques, badges, nuage de tags), et laissait une colonne entière vide sur les listes impaires ou filtrées.

---

## 2. Causes Racines

1. **Absence de confinement de défilement horizontal (`overscroll-behavior-x`) :**
   - Les bandeaux déroulants `.media-gallery-thumbs` et `.filter-bar` propageaient les gestes tactiles/glissés et le focus clavier au conteneur parent (`window` / `html`), décalant le scroll horizontal du viewport global.
2. **Débordement du Header (`top-header`) et `100vw` :**
   - `max-width: 100vw` incluait la largeur de la barre de défilement verticale, causant un débordement artificiel de ~15-17px.
   - Les libellés masqués du header (`.search-label`, `.btn-label-*`) et `.brand-group` (`min-width: 220px`) augmentaient le `scrollWidth` du header au-delà de la largeur visible.
3. **Absence de `contain: paint` et `overflow-x: clip` :**
   - Les conteneurs `.project-media-box`, `.project-media-main` et `#viewInteractive` ne bornaient pas strictement le débordement sous-pixel des éléments enfants.

---

## 3. Solutions Appliquées

### A. Confinement strict du scroll & zéro déformation (`site_template/index.html.j2`)

- **Remplacement de `scrollIntoView` par `container.scrollTo`** :
  - L'appel natif `btn.scrollIntoView({ inline: 'center' })` causait un défilement horizontal du document entier (`window.scrollX > 0`).
  - Remplacé par un défilement circonscrit au conteneur parent (`parent.scrollTo({ left: targetLeft, behavior: 'smooth' })`), garantissant que la fenêtre ne bouge jamais.
- **`html, body`** :
  ```css
  html, body {
    width: 100%;
    max-width: 100%;
    overflow-x: clip;
    overscroll-behavior-x: none;
  }
  ```
- **`#viewInteractive`** :
  ```css
  #viewInteractive {
    max-width: 1100px;
    margin: 0 auto;
    width: 100%;
    box-sizing: border-box;
    overflow-x: clip;
  }
  ```
- **`.media-gallery-thumbs` & `.filter-bar`** :
  ```css
  .media-gallery-thumbs {
    overflow-x: auto;
    overscroll-behavior-x: contain;
    touch-action: pan-x;
    cursor: grab;
  }
  ```
- **`.project-media-box` & `.project-media-main`** :
  - Ajout de `contain: paint;` et `overflow: hidden;` garantissant une surface 16:9 immuable sans fuite sous-pixel.

### B. Navigation Drag & Swipe Unifiée et Flèches Interactives

- **Glisser / Déposer (Drag & Swipe)** :
  - Glisser tactile sur mobile (`touchstart`, `touchmove`, `touchend`).
  - Glisser souris sur desktop (`mousedown`, `mousemove`, `mouseup`) avec curseur `grab` / `grabbing` et classe `.is-dragging`.
  - Glisser horizontal des vignettes (`attachDragToScroll`).
- **Boutons Précédent / Suivant (`.media-card-prev`, `.media-card-next`)** :
  - Flèches discrètes avec hover glow (`‹` / `›`) pour naviguer sans dépendre uniquement du geste.

### C. Sections Repliables & Accordéon Stack Technique

- Sections portfolio repliables avec persistance locale (`cv_collapsed_sections` dans `localStorage`).
- Accordéon `<details class="exp-tags-details">` pour les listes de technologies avec auto-dépliage lors des filtrages.

### D. Unification du breakpoint 1 colonne à 860px

- Extension du repli 1 colonne (`grid-template-columns: minmax(0, 1fr)`) jusqu'au breakpoint tablette de 860px pour `.projects-grid` et `.skills-grid`.
- Header compacté dynamiquement sous 860px (`.brand-group { min-width: 0; }`, masquage des labels textuels au profit des icônes et tooltips).

---

## 4. Vérification et Suite de Tests E2E (12 Tests)

La suite de tests [`scripts/test_ui_regressions.py`](scripts/test_ui_regressions.py) couvre désormais l'intégralité des fonctionnalités :
1. Centrage et ajustement du Lightbox image unique
2. Navigation flèches et raccourcis clavier Lightbox multi-ressources
3. Navigation par vignettes de galerie
4. Bascule dynamique de thèmes sombre/clair
5. Accessibilité clavier générale
6. Alignement DOM du Text Layer PDF
7. Guard console et exceptions JavaScript
8. Couche d'annotation et hyperliens interactifs du PDF
9. Repliement/dépliement des sections, clavier et persistance au reload (F5)
10. Accordéon repliable de la stack technique des fiches
11. Drag & Swipe des médias de projet, flèches de navigation, et zéro layout shift sur clics de vignettes
12. Préservation et synchronisation de la clipart active lors de l'ouverture plein écran Lightbox (TDD)
13. Navigation Drag & Swipe en vue Fullscreen Lightbox (TDD) : support complet du glisser à la souris (desktop avec curseur `grab`/`grabbing`) et du geste tactile (mobile), avec désactivation du drag natif navigateur (`draggable="false"`, `pointer-events: none`, `dragstart` intercepté).
14. **Auto-dépliage des sections et navigation fluide via Smart Search (TDD)** : lors de la sélection d'un résultat (expérience, projet, compétence, formation) dans la Command Palette (`Ctrl+K`), la section parente repliée est automatiquement dépliée (`expandSection`), l'accordéon éventuel ouvert, et l'élément ciblé est amené au centre du viewport avec surbrillance animée temporaire (`navigateToElement`). De même, le filtrage par domaine (`filterByDomain`) auto-déplie désormais les sections contenant des fiches correspondantes.

Validation globale `task check` : 100% vert (0 erreurs, 0 avertissements, 14/14 tests UI).
