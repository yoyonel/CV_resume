# CV & Resume — Lionel ATTY

Dépôt pour la génération et le versionnement de CV / Resume techniques en PDF.

Le projet supporte deux moteurs de génération :
1. **Typst (Moderne - Proposition 3)** : Compilation ultra-rapide en Rust (< 30ms), typographie vectorielle (Inter + JetBrains Mono), badges de compétences colorés par domaine et icônes vectorielles SVG.
2. **Pandoc + ConTeXt MkIV (Legacy - Proposition 1)** : Compilation via conteneur Docker LaTeX/ConTeXt.

---

## Structure du Dépôt

- `data/` :
  - `profile.json` : Données personnelles, coordonnées, spécialités, date de naissance.
  - `pdf/` : Dossier de sortie des PDF générés par année (ex. `data/pdf/2026/`).
- `typst_resume/` :
  - `resume.typ.j2` : Template principal Typst avec Jinja2.
  - `icons/` : Icônes vectorielles SVG (mail, phone, map-pin, laptop, calendar, github, etc.).
- `pandoc_resume/` :
  - `resume.md.j2` & `sections/*.md` : Template et sections modulaires Markdown pour la chaîne ConTeXt.
  - `style_chmduquesne.tex` & `style_chmduquesne.css` : Feuilles de style ConTeXt et CSS.
- `scripts/` :
  - `compile_typst.py` : Rendu du template Jinja2 et compilation Typst directe.
  - `watch_typst.py` : Live preview / watcher instantané avec polling `mtime` (0% CPU au repos).
  - `render_resume.py` : Rendu Jinja2 pour la chaîne Markdown/Pandoc.
- `docs/` :
  - `2026-08-28_propositions_modernisation_cv.md` : Comparatif des propositions de modernisation graphique.
  - `2026-08-28_typst_architecture_et_possibilites.md` : Documentation détaillée de l'intégration Typst.

---

## Commandes & Utilisation

### Avec Go-Task (`task`)

Utilisé pour les tâches de développement, qualité et prévisualisation :

```bash
task                  # Liste toutes les commandes disponibles
task watch            # Mode Live Watch (recompile à chaud sur modification de profile.json ou template)
task lint             # Linting Python (Ruff), AST Jinja2, JSON et compilation Typst
task fmt              # Formatage automatique du code Python (Ruff)
task check            # Suite complète de validation et test de build
```

### Avec Makefile (`make`)

Utilisé pour la génération des artefacts PDF finaux :

```bash
make typst            # Génère le PDF Typst (data/pdf/2026/2026_ATTY_Resume_Typst.pdf)
make typst-watch      # Lance le live watcher Typst
make all              # Génère les PDF ConTeXt et Typst
make clean            # Supprime les PDF et artefacts de build
```

---

## Dépendances

- **Python 3.10+** avec [`uv`](https://docs.astral.sh/uv/) (gère automatiquement `jinja2`, `typst` et les dépendances sans installation globale).
- **Go-Task** ([`task`](https://taskfile.dev/)) pour l'exécution des workflows dev.
- **Docker** (uniquement nécessaire pour la cible legacy `make pdf` via Pandoc/ConTeXt).
