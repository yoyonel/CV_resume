# 🛡️ Verrouillage Anti-Régression : Suite de Tests Console & Fix PDF.js (2026-08-30)

## 1. Contexte & Diagnostic des Erreurs Console

Lors du premier chargement ou du basculement vers la vue Document PDF, deux erreurs JavaScript survenaient dans la console :

1. **`ReferenceError: pdfjsLib is not defined` (Ligne 1696)** :
   - Une ligne résiduelle `pdfjsLib.GlobalWorkerOptions.workerSrc = ...` s'exécutait au chargement initial du script principal, alors que PDF.js est chargé à la demande (lazy-loading).
2. **`ReferenceError: Cannot access 'pdfJsLoadingPromise' before initialization`** :
   - La variable `pdfJsLoadingPromise` était déclarée après certaines fonctions l'utilisant, causant une Temporal Dead Zone (TDZ).
3. **`[Desktop Console ERROR] The --scale-factor CSS-variable must be set...`** :
   - En mode page simple (`mode-single`), la page 2 du PDF était masquée (`display: none;`). L'appel à `pdfjsLib.renderTextLayer` sur un élément masqué empêchait `getComputedStyle()` de calculer `--scale-factor`, générant un warning d'erreur PDF.js.

---

## 2. Corrections Appliquées

1. **Initialisation Propre & Zéro TDZ** :
   - Déclaration de `let pdfJsLoadingPromise = null;` et `let currentMainView = 'web';` au sommet du script.
   - Configuration du worker PDF.js uniquement dans la callback `onload` de `ensurePdfJsLoaded()`.
2. **Gestion du Text Layer Masqué** :
   - `renderDocPage` ignore le rendu du textLayer pour les conteneurs masqués (`display: none;`).
   - Définition de `--scale-factor: 1;` sur `:root`, `html`, `.pdf-page-container` et `.textLayer`.

---

## 3. Verrouillage Permanent : `scripts/check_console.py`

Création d'une suite de tests automatisée Playwright [`scripts/check_console.py`](../scripts/check_console.py) qui simule l'ensemble du cycle de vie utilisateur et intercepte :
- `page.on('pageerror')` : Exceptions non rattrapées (`ReferenceError`, `TypeError`, etc.).
- `page.on('console')` : Tous les `console.error` et `console.warn`.

### 🧪 Parcours Validé par le Test (7 étapes) :
1. Chargement initial de la vue Interactive Web (Desktop).
2. Bascule de thème sombre / clair (`toggleTheme()`).
3. Filtrage dynamique par tags de domaine (`filterByDomain()`).
4. Ouverture et recherche dans la palette de commandes (`Ctrl+K`).
5. Bascule vers la vue Document PDF et rendu TextLayer.
6. Contrôles de zoom (+ / -) et modes continu / double page.
7. Chargement initial sur viewport Mobile (iPhone / Android).

### ⚙️ Intégration CI / Taskfile / Makefile :
- `task check:console` / `make check-console`
- Intégré dans `task check` (bloque les commits en local si une erreur console existe).
- Intégré dans le workflow GitHub Actions [`.github/workflows/deploy-pages.yml`](../.github/workflows/deploy-pages.yml).
