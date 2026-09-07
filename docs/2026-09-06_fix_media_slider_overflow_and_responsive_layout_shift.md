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

### E. Système Universel de Tooltip Web Flottant (Restauration ISO & Zéro Rognage)

- **Problème identifié** : Les boutons du bandeau supérieur (`header.top-header`) utilisaient des info-bulles pseudo-éléments CSS (`[data-tooltip]::after`) qui étaient tronquées par `overflow: hidden` sur le header. Une première tentative de contournement via l'attribut HTML standard `title="..."` avait provoqué une régression visuelle majeure : affichage du tooltip natif et brut de l'OS (boîte noire rectangulaire, police système sans serif, absence d'arrondis et d'ombres portées), brisant l'harmonie graphique ISO avec le reste de l'application.
- **Solution définitive appliquée** :
  - Mise en place d'un composant flottant universel `#web-tooltip` rattaché directement à `document.body` (`position: fixed; z-index: 999999; pointer-events: none;`).
  - Totalement affranchi de tout conteneur parent : **impossible à rogner** par `overflow: hidden`, `overflow: clip` ou `contain: paint`.
  - Restauration stricte des design tokens ISO legacy : coins arrondis (`border-radius: 6px`), fond sombre translucide (`#0f172a` en thème sombre / `#1e293b` en thème clair), bordure subtile (`1px solid rgba(255,255,255,0.12)`), ombre portée (`box-shadow: 0 4px 14px rgba(0,0,0,0.4)`), typographie fine et animation douce (`opacity` / `scale`).
  - Positionnement intelligent auto-adaptatif : placé en dessous pour les éléments hauts du viewport (`rect.top < 70px`), placé au-dessus ailleurs, avec recentrage horizontal et marge de sécurité par rapport aux bords d'écran.
  - Détection universelle par délégation d'événements : actif au survol souris (`mouseenter` / `mouseleave`) et au focus clavier (`focusin` / `focusout`), masquage immédiat sur défilement (`scroll`) ou touche `Escape`.
  - Suppression de tout attribut `title` sur les éléments interactifs (`data-tooltip` exclusif) pour empêcher le déclenchement de l'infobulle système brute de l'OS.

---

## 4. Vérification, Suite de Tests & Checker Automatisé

### A. Nouveau Vérificateur d'Homogénéité Web Components (`scripts/check_ui_components.py`)
Intégré directement dans la commande `task check` (`task check:components`) et dans la CI :
1. **Garde statique (Zéro reliquat Web Awesome)** : vérifie l'absence totale de balises orphelines `<sl-*>` et de scripts/liens Shoelace dans les templates et le site compilé.
2. **Garde dynamique Playwright (Design Tokens & Accessibilité)** :
   - Audite tous les boutons du header (`#tabDoc`, `#tabWeb`, `#search-trigger`, `#themeToggleBtn`, `.btn-print`, `.btn-download`) et les chips de contact.
   - Contrôle que chaque élément possède un attribut `data-tooltip` et **aucun** attribut `title` brut.
   - Simule le survol et le focus clavier : valide en temps réel les styles calculés du tooltip flottant (`position: fixed`, `borderRadius >= 6px`, présence de `boxShadow`, couleurs de fond `#0f172a` / `#1e293b`).
   - Valide le masquage au départ du curseur (`mouseleave`).

### B. Suite de Tests E2E (15 Tests)
La suite de tests [`scripts/test_ui_regressions.py`](scripts/test_ui_regressions.py) couvre l'intégralité des fonctionnalités :
1. Centrage et ajustement du Lightbox image unique
2. Navigation flèches et raccourcis clavier Lightbox multi-ressources
3. Navigation par vignettes de galerie et chips de contact (tooltips riches)
4. Bascule dynamique de thèmes sombre/clair
5. Accessibilité clavier générale
6. Alignement DOM du Text Layer PDF
7. Guard console et exceptions JavaScript
8. Couche d'annotation et hyperliens interactifs du PDF
9. Repliement/dépliement des sections, clavier et persistance au reload (F5)
10. Accordéon repliable de la stack technique des fiches
11. Drag & Swipe des médias de projet, flèches de navigation, et zéro layout shift sur clics de vignettes
12. Préservation et synchronisation de la clipart active lors de l'ouverture plein écran Lightbox (TDD)
13. Navigation Drag & Swipe en vue Fullscreen Lightbox (TDD)
14. Auto-dépliage des sections et navigation fluide via Smart Search (TDD)
15. Verrouillage strict de frontière Header & zéro recouvrement (TDD) sur 3 viewports et 2 thèmes.

Validation globale `task check` : 100% vert (0 erreurs, 0 avertissements, 15/15 tests UI, audit de conformité composants web 100% vert).
