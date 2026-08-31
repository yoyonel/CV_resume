# Bot E2E Exploratoire & Historisation des Sessions

**Date** : 2026-08-31  
**Branche** : `fix/pdfjs-scale-factor-warning`  
**Outil** : `scripts/exploratory_bot.py`  
**Cibles Taskfile** : `task test:bot`, `task test:bot:prod`, `task test:bot:surge` / `task test:bot:preview`  
**Intégration CI** : `.github/workflows/pr-preview.yml` (1 minute sur Surge) & `.github/workflows/deploy-pages.yml` (30s)

---

## 1. Description & Objectifs

Le bot exploratoire (**Guided Chaos Monkey E2E**) teste de manière autonome et pseudo-aléatoire guidée l'ensemble des interactions de l'application frontend :
- **Bascule des vues** : Web Portfolio <-> Document ISO.
- **Filtrage interactif** : par domaine et mots-clés techniques (clic simple et accumulation Shift+Click).
- **Palette de recherche interactive** : Ctrl+K, saisie de termes variés, navigation clavier, sélection.
- **Galeries multimédias** : bascule des 11 miniatures PNG/GIF, ouverture/fermeture des lightbox et modales de présentation.
- **Visualiseur Document ISO PDF.js** : modes Single/Dual/Continu, pagination Page 1/2, zoom +/-, navigation clavier.
- **Bascule de thèmes** : Clair / Sombre en cours d'action.
- **Morphing dynamique du viewport** : Mobile, Tablette, Desktop, UltraWide.

---

## 2. Que se passe-t-il en cas de FAIL détecté ?

En cas d'anomalie (exception JavaScript non gérée, erreur console DevTools, warning d'accessibilité avec `--fail-on-warn`, ou échec réseau) :

1. **Code de retour système `exit 1`** : La tâche Taskfile ou le step CI échoue immédiatement.
2. **Identification précise de l'étape** : Le numéro d'étape (`#`), l'horodatage exact et la dernière action exécutée sont immédiatement pointés.
3. **Capture d'écran automatique** : Une capture PNG de l'état exact du DOM au moment du crash est enregistrée dans `reports/bot_sessions/screenshots/fail_step_<step>_<seed>.png`.
4. **Section d'audit dans le Markdown** : La section `⚠️ Journal des Anomalies Détectées` recense l'erreur exacte, la stack trace et la requête concernée.
5. **Rejouabilité 100% Déterministe via la Graine (`--seed`)** :
   - Le rapport affiche la commande de rejeu avec la graine exacte :
     ```bash
     task test:bot -- --seed <SEED> --steps <TOTAL_STEPS>
     ```
   - Permet de reproduire fidèlement l'anomalie en local pas-à-pas en debug.

---

## 3. Récupération des Traces & Rapports en CI/CD GitHub Actions

Dans `.github/workflows/pr-preview.yml` :
- Le bot tourne pendant **60 secondes chrono** (`--duration 60`) avec une graine aléatoire sur l'URL de prévisualisation Surge.
- Le rapport Markdown est automatiquement injecté dans le **Job Summary GitHub** (`$GITHUB_STEP_SUMMARY`).
- L'ensemble des sessions (`.jsonl`, `.md` et captures screenshots en cas d'erreur) est uploadé via `actions/upload-artifact@v4` avec `if: always()` sous le nom **`bot-exploratory-session-reports`**.
- Tout rapport ou capture est directement téléchargeable depuis l'interface GitHub Actions pour analyse et rejeu local immédiat via `task test:bot -- --seed <SEED>`.

---

## 4. Commandes Go-Task Dédiées (Zéro Commande Manuelle)

```bash
# 1. Lancement local standard (sur dist/ - 50 étapes)
task test:bot

# 2. Lancement local chronométré (ex: 60 secondes)
task test:bot -- --duration 60

# 3. Lancement local avec options personnalisées
task test:bot -- --steps 100 --seed 4242

# 4. Lancement direct sur la Production GitHub Pages (https://yoyonel.github.io/CV_resume/)
task test:bot:prod -- --duration 60

# 5. Lancement direct sur la prévisualisation Surge
task test:bot:surge -- --duration 60

# 6. Lancement direct sur une URL Surge personnalisée
task test:bot:surge URL=https://mon-deploiement-perso.surge.sh -- --duration 60
```

---

## 5. Bilan de Validation

- [x] Correction du point de défaillance initial (`handlePaletteKeyDown` -> `page.keyboard.press`).
- [x] Rejeu déterministe de la graine `50628` (**100% PASS**).
- [x] Support du mode durée chronométrée `--duration` (testé sur 5s et 60s).
- [x] Capture automatique de screenshot en cas de FAIL dans `reports/bot_sessions/screenshots/`.
- [x] Intégration GitHub Actions (`pr-preview.yml` & `deploy-pages.yml`) avec téléversement d'artefacts.
- [x] Validation complète `task check` (**100% PASS**).
