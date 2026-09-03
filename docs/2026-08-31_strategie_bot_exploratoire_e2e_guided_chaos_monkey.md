# Stratégie & Architecture du Bot d'Exploration E2E (Guided Chaos Monkey)

**Date** : 2026-08-31  
**Auteur** : Yohan ATTY  
**Branche** : `fix/pdfjs-scale-factor-warning`  
**Composants** : [`scripts/exploratory_bot.py`](../scripts/exploratory_bot.py), [`.github/workflows/pr-preview.yml`](../.github/workflows/pr-preview.yml), [`Taskfile.yml`](../Taskfile.yml)

---

## 1. Philosophie & Problématique

### Les Limites du Testing E2E Traditionnel
Les suites de tests E2E conventionnelles (Playwright / Cypress scénarisés) vérifient des chemins nominaux prédéterminés (*"L'utilisateur clique sur A, puis B, puis vérifie C"*). Cette approche souffre de trois angles morts critiques :
1. **Angle mort combinatoire** : Une interface riche avec filtres cumulatifs, modales imbriquées, bascules de thèmes et visualiseur PDF génère des milliers d'états possibles qu'aucun test statique ne peut couvrir exhaustivement.
2. **Sensibilité aux conditions de course (Race Conditions)** : Les interactions asynchrones rapides (ex: ouvrir une modale et changer de thème pendant le chargement du TextLayer PDF) ne sont presque jamais testées dans les scénarios déterministes.
3. **Inadéquation du Random Monkey Test brut** : Un test purement aléatoire (clics sur des coordonnées aléatoires de l'écran) est inefficace sur une Single Page Application moderne : il clique dans le vide, déclenche des navigations parasites ou boucle sans jamais activer les fonctionnalités métier.

### Le Paradigme du "Hasard Guidé" (Guided Chaos Monkey)
Le bot implémenté repose sur une **marche aléatoire pondérée sur graphe d'états (Markov Random Walk)** :
- Il connaît l'espace fonctionnel de l'application (modales, filtres, palette, visualiseur PDF, thèmes, viewports).
- Il choisit dynamiquement ses actions selon une **distribution de probabilités calibrée**.
- Il surveille en continu la santé interne du navigateur (runtime JS, accessibilité WAI-ARIA, erreurs CSS, flux réseau).
- Il enregistre l'intégralité de sa session pour permettre un **rejeu déterministe au bit près**.

---

## 2. Architecture & Moteur d'Exécution

```
                                      ┌───────────────────────────────┐
                                      │       PLAYWRIGHT RUNTIME      │
                                      │   (Chromium Headless Linux)   │
                                      └───────────────┬───────────────┘
                                                      │
                       ┌──────────────────────────────┴──────────────────────────────┐
                       │                                                             │
         ┌─────────────▼─────────────┐                                 ┌─────────────▼─────────────┐
         │   4 CANAUX DE TÉLÉMÉTRIE  │                                 │   DISTRIBUTION DU HASARD  │
         ├───────────────────────────┤                                 ├───────────────────────────┤
         │ 1. pageerror (Uncaught)   │                                 │ • Bascule Vues (12%)      │
         │ 2. console.error / warn   │                                 │ • Filtres Domaines (15%)  │
         │ 3. requestfailed (Réseau) │                                 │ • Filtres Tech (12%)      │
         │ 4. dialog (Prompts/Alerts)│                                 │ • Smart Palette (15%)     │
         └─────────────┬─────────────┘                                 │ • Galeries Médias (12%)   │
                       │                                               │ • Modales Lightbox (8%)   │
                       │ (Interception continue)                       │ • Lecteur Vidéo (5%)      │
                       │                                               │ • Contrôles PDF ISO (12%) │
         ┌─────────────▼─────────────┐                                 │ • Thème Dynamique (4%)    │
         │    FLIGHT RECORDER ENGINE │                                 │ • Morph Viewport (5%)     │
         ├───────────────────────────┤                                 └─────────────▲─────────────┘
         │ • session_*.jsonl (data)  │                                               │ (Next Action)
         │ • session_*.md (rapport)  │◀──────────────────────────────────────────────┘
         │ • fail_step_*.png (crash) │
         └───────────────────────────┘
```

---

## 3. Le Moteur de Hasard Guidé & Table de Distribution

Chaque étape d'exploration sélectionne une action parmi 10 catégories pondérées :

| Catégorie d'Action | Poids | Description & Comportement Guidé | Cibles DOM / Méthodes |
|:---|:---:|:---|:---|
| **`view_switch`** | `12%` | Bascule aléatoire entre la vue Portfolio Web interactif et la vue Document ISO. | `switchMainView('web' \| 'doc')` |
| **`domain_filters`** | `15%` | Filtrage par domaine métier (Python, C++ 3D, Spatial, Management) avec simulation aléatoire de clics simples ou **Shift+Click cumulatifs**. | `.filter-tag[data-domain=...]` |
| **`tech_filters`** | `12%` | Filtrage par mot-clé technologique (Vulkan, Docker, FastAPI, Typst, etc.) avec accumulation. | `.tech-kw[...]` |
| **`palette_search`** | `15%` | Ouverture (`Ctrl+K`), saisie floue de requêtes réelles et hors-index, navigation clavier (`ArrowDown`), validation (`Enter`) ou fermeture (`Escape`). | `#cmdPaletteDialog`, `#paletteSearchInput` |
| **`gallery_media`** | `12%` | Exploration et bascule des 14 variantes de miniatures projets (PNG, démos animées GIF, slides). | `.media-thumb-btn-*` |
| **`image_lightbox`** | `8%` | Ouverture de la modale plein écran d'images, vérification du chargement et fermeture propre. | `#imageModalDialog`, `openImageModalByElem()` |
| **`media_modal`** | `5%` | Ouverture et fermeture de la modale de masterclasses vidéo / présentations. | `#mediaModalDialog`, `openMediaModalByElem()` |
| **`pdf_controls`** | `12%` | Manipulation du visualiseur PDF.js : modes Simple/Double/Continu, pagination (`prevDocPage`/`nextDocPage`), zoom différentiel (+/-10%). | `#viewDocument`, `setDocMode()`, `zoomDoc()` |
| **`theme_toggle`** | `4%` | Bascule à chaud du thème Clair / Sombre en pleine interaction pour éprouver les transitions CSS et la palette Web Awesome. | `#themeToggleBtn`, `toggleTheme()` |
| **`viewport_morph`** | `5%` | Redimensionnement dynamique de la fenêtre parmi 5 résolutions (Mobile 360px/390px, Tablette 768px, Desktop 1280px, UltraWide 1920px). | `page.set_viewport_size()` |

---

## 4. Instrumentation & Gardes Télémetriques

Le bot écoute 4 canaux de signaux bas-niveau émis par le moteur Chromium :

### A. Exceptions Runtime Non Gérées (`pageerror`)
Capture instantanée de toute exception JavaScript (`TypeError`, `ReferenceError`, promesse rejetée non interceptée).

### B. Console DevTools (`console`)
- **Erreurs (`msg.type == "error"`)** : Toute erreur de script, échec de parsing ou violation de sécurité.
- **Avertissements d'Accessibilité WAI-ARIA (`Blocked aria-hidden`)** : Détection des conflits de focus sur les composants modaux Shoelace `<sl-dialog>`.
- **Avertissements CSS PDF.js (`--scale-factor`)** : Détection des anomalies d'échelle lors des rendus sur éléments masqués.

### C. Échecs Réseau (`requestfailed`)
Surveillance de toutes les requêtes HTTP internes :
- Détection des 404, 500, corruptions d'assets ou erreurs CORS.
- **Filtrage intelligent de `net::ERR_ABORTED`** : Les requêtes d'images intentionnellement annulées par le navigateur lors de la fermeture rapide d'une modale ne sont pas considérées comme des défaillances.

### D. Capture Visuelle sur Défaillance (`page.screenshot`)
En cas de statut `FAIL` à l'étape $N$, le bot réalise immédiatement un snapshot visuel du viewport enregistré dans :
`reports/bot_sessions/screenshots/fail_step_<step>_<seed>.png`

---

## 5. Historisation & "Boîte Noire" d'Exécution

Chaque session d'exploration produit deux artefacts complémentaires dans `reports/bot_sessions/` :

### 1. Journal Machine JSON Lines (`session_<timestamp>_seed<seed>.jsonl`)
Chaque ligne représente un enregistrement JSON atomique :
```json
{
  "step": 42,
  "time_iso": "2026-08-31T12:51:04.123456+00:00",
  "action": "palette_search",
  "description": "Command Palette search 'vulkan'",
  "target": "#cmdPaletteDialog",
  "duration_ms": 225.7,
  "view_before": "Portfolio Web",
  "view_after": "Portfolio Web",
  "errors": [],
  "warnings": [],
  "status": "PASS"
}
```

### 2. Rapport Synthétique Markdown (`session_<timestamp>_seed<seed>.md`)
- Métriques globales d'exploration (taux de succès, durée, exceptions).
- Matrice de couverture fonctionnelle par composant.
- Tableau chronologique complet de toutes les étapes exécutées.
- **Commande de rejeu déterministe** :
  ```markdown
  > 🔁 **Commande de Rejeu Déterministe** :  
  > `task test:bot -- --seed 59933 --duration 60`
  ```

---

## 6. Intégration CI/CD & Commandes Go-Task

### A. Intégration GitHub Actions (`.github/workflows/pr-preview.yml`)
Sur chaque Pull Request, après le déploiement sur Surge :
1. Le bot est lancé en direct sur l'URL Surge pendant **60 secondes chrono** (`--duration 60`).
2. Le rapport Markdown est concaténé dans le résumé d'exécution GitHub Actions (`$GITHUB_STEP_SUMMARY`).
3. L'ensemble des traces et captures d'écran est archivé via `actions/upload-artifact@v4` sous le nom **`bot-exploratory-session-reports`** (`if: always()`).

### B. Commandes Go-Task

```bash
# 1. Exploration locale par défaut (50 actions)
task test:bot

# 2. Exploration locale chronométrée (ex: 60 secondes)
task test:bot -- --duration 60

# 3. Rejeu déterministe d'une graine identifiée en CI
task test:bot -- --seed 59933 --duration 60

# 4. Exploration directe sur la Production GitHub Pages
task test:bot:prod -- --duration 60

# 5. Exploration directe sur la prévisualisation Surge courante
task test:bot:surge -- --duration 60

# 6. Exploration sur une URL Surge arbitraire
task test:bot:surge URL=https://mon-deploiement.surge.sh -- --duration 60
```
