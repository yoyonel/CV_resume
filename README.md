# CV & Resume — Lionel ATTY

[![GitHub Pages](https://img.shields.io/badge/Live_Site-GitHub_Pages-0284c7?style=flat-square&logo=githubpages&logoColor=white)](https://yoyonel.github.io/CV_resume/)
[![Typst 0.15](https://img.shields.io/badge/Engine-Typst_0.15-239dad?style=flat-square&logo=typst&logoColor=white)](https://typst.app)
[![CI/CD Pages](https://github.com/yoyonel/CV_resume/actions/workflows/deploy-pages.yml/badge.svg)](https://github.com/yoyonel/CV_resume/actions/workflows/deploy-pages.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)

> 🌐 **Site Web Interactif & Document ISO Typst en ligne** : **[https://yoyonel.github.io/CV_resume/](https://yoyonel.github.io/CV_resume/)**

Dépôt pour la conception, la génération automatisée et le versionnement continu de CV et dossiers de compétences d'ingénierie logicielle haute performance.

Ce projet implémente une architecture **Data-Driven & Multi-Moteurs** permettant de générer des livrables PDF optimisés tant pour les recruteurs humains (design graphique soigné, hiérarchie visuelle, diagrammes de flux) que pour les robots de recrutement ATS (couche textuelle vectorielle structurée).

---

## 🏗️ Architecture & Stratégie Technique

```text
               ┌──────────────────────┐
               │   data/profile.json  │ (Source Unique de Vérité)
               └──────────┬───────────┘
                          │
          ┌───────────────┴───────────────┐
          │                               │
          ▼                               ▼
┌──────────────────┐            ┌──────────────────┐
│  typst_resume/   │            │  pandoc_resume/  │
│  resume.typ.j2   │            │  resume.md.j2    │
└─────────┬────────┘            └────────┬─────────┘
          │ (Jinja2 + uv)                │ (Docker + Pandoc)
          ▼                              ▼
┌──────────────────────────────┐┌──────────────────────────────┐
│ 2026_ATTY_Resume_Typst.pdf   ││ 2026_ATTY_Resume_Legacy.pdf  │
│ (Moteur Moderne Typst 0.15)  ││ (Moteur Legacy ConTeXt MkIV) │
└──────────────────────────────┘└──────────────────────────────┘
```

### 1. Source Unique de Données (`data/profile.json`)
- Centralisation des coordonnées, titres, dates clés, métadonnées et jauges d'expérience.
- Calcul dynamique automatique de l'âge et de l'ancienneté à chaque compilation via `scripts/render_resume.py` et `scripts/compile_typst.py` (zéro maintenance manuelle de dates).

### 2. Moteur Moderne Typst (`typst_resume/`)
- **Vitesse & Compilation Instantanée** : Moteur Typst 0.15 compilé en Rust (`< 30ms` de temps de rendu).
- **Design System & Typographie Vectorielle** : Polices *Inter* pour le corps et *JetBrains Mono* pour les badges techniques.
- **Système de Badges Sémantiques Feutrés (4 Familles Ardoise)** :
  - *Core Languages, Frameworks & Moteurs 3D* (Bleu Ardoise) : `Python 3.13`, `FastAPI`, `C++ (17/20)`, `Rust`, `Odin`, `Vulkan`, `OpenGL 4.5+`, `SIMD / AVX2`.
  - *Data, Cloud, Infra & DevOps* (Sauge Ardoise) : `MongoDB`, `Redis`, `RabbitMQ`, `PostgreSQL`, `PostGIS`, `Azure / AKS`, `Docker`, `Kubernetes`, `GitLab CI`.
  - *IA, LLM & Tooling Agentique* (Sable Ardoise) : `AGY (Gemini)`, `Claude Code`, `MCP Servers`, `Dust`, `n8n`, `OpenAI API`.
  - *Tooling, Profiling, UI & Build* (Ardoise Neutre) : `Dear ImGui`, `Tracy Profiler`, `Intel VTune`, `RenderDoc`, `Heaptrack`, `Go-Task`, `CMake`, `UV / Ruff`.
- **Composants Graphiques Sur-Mesure** :
  - *Stepper vertical temporel* élégant reliant chronologiquement les postes.
  - *Grille thématique de compétences* structurée en 6 blocs de spécialisation.
  - *Diagrammes d'architecture pipeline* intégrés (`[Clients] ▶ [Gateway] ▶ [Microservices] ▶ [Stockage]`).
- **Équilibre & Gabarit Strict** : Calibrage millimétré sur **strictement 2 pages A4** avec zéro ligne orpheline et aération verticale maximale.

### 3. Moteur Legacy ConTeXt / Pandoc (`pandoc_resume/`)
- Chaîne de secours basée sur Docker (`yoyonel/pandoc:latest`) compilant les sections modulaires Markdown via Pandoc et ConTeXt MkIV.

---

## 📂 Structure du Répertoire

```text
.
├── .github/workflows/          # Pipelines CI/CD GitHub Actions
│   └── build-pdf.yml           # Workflow automatisé de test, lint, compilation et release
├── data/
│   ├── profile.json            # Source de données principale du profil
│   ├── bib/bibtex.bib          # Bibliographie et publications de recherche (CGF 2006)
│   └── pdf/2026/               # Sorties locales des PDFs compilés
├── typst_resume/
│   ├── resume.typ.j2           # Template maître Typst avec directives Jinja2
│   ├── resume.typ              # Code Typst compilé
│   └── icons/                  # Icônes vectorielles SVG (mail, phone, map-pin, github, etc.)
├── pandoc_resume/
│   ├── resume.md.j2            # Template maître Markdown/Pandoc
│   ├── sections/               # Sections modulaires Markdown
│   │   ├── 00_header.md.j2
│   │   ├── 01_experiences.md
│   │   ├── 02_skills.md
│   │   ├── 03_education.md
│   │   ├── 04_projects.md
│   │   └── 05_misc.md
│   ├── style_chmduquesne.tex   # Feuille de style ConTeXt
│   └── Makefile                # Makefile interne Pandoc
├── scripts/
│   ├── compile_typst.py        # Compilateur Typst autonome avec calcul d'âge dynamique
│   ├── watch_typst.py          # Live watcher à chaud avec polling mtime optimisé (0% CPU)
│   └── render_resume.py        # Générateur Jinja2 pour la chaîne Markdown
├── docs/                       # Spécifications graphiques, rapports de profiling et R&D
├── Taskfile.yml                # Définition des tâches de dev et contrôle qualité (Go-Task)
└── Makefile                    # Interface make standard pour builds locaux et Docker
```

---

## 🛠️ Outillage & Commandes de Développement

Le projet utilise [`uv`](https://docs.astral.sh/uv/) pour l'environnement Python sans pollution globale et [`task`](https://taskfile.dev/) comme exécuteur de tâches moderne.

### Workflow Go-Task (`task`)

```bash
task                  # Affiche l'aide et la liste des tâches
task site:serve       # Lance le serveur de preview web local (http://localhost:8000)
task site:serve:lan   # Lance le serveur sur 0.0.0.0 avec IP LAN pour test smartphone Wi-Fi
task site:check:mobile# Validation automatisée du layout mobile & zéro-overflow (Playwright)
task site:build       # Construit le site statique HTML/SVG/PDF dans dist/
task watch            # Lance le watcher temps réel Typst (recompile le PDF instantanément)
task lint             # Analyse statique : Ruff sur scripts/, AST Jinja2 et compilation Typst
task fmt              # Formatage automatique du code Python avec Ruff
task check            # Suite complète de vérification (lint + build + mobile + links)
```

### Workflow Makefile (`make`)

```bash
make site-serve       # Démarre le serveur de prévisualisation web locale
make site-serve-lan   # Démarre le serveur sur 0.0.0.0 pour test mobile sur Wi-Fi local
make check-mobile     # Lance la validation automatisée responsive Playwright
make site             # Construit le site web statique dans dist/
make typst            # Compile le CV Typst (génère data/pdf/2026/2026_ATTY_Resume_Typst.pdf)
make typst-watch      # Démarre le watcher Typst
make all              # Compile l'ensemble des cibles (Typst + ConTeXt via Docker)
make clean            # Nettoie les artefacts générés
```

---

## 🌐 Déploiement Statique GitHub Pages

Le site interactif et portfolio est accessible publiquement à l'adresse :
👉 **[https://yoyonel.github.io/CV_resume/](https://yoyonel.github.io/CV_resume/)**

Le pipeline `.github/workflows/deploy-pages.yml` assure le build et déploiement continu à chaque push :
- **Double Vue Unifiée** :
  - *Vue Document ISO Typst* : Moteur PDF.js avec scaling dynamique multi-écrans, zoom et sélection de texte vectoriel.
  - *Vue Interactive Web Awesome* : Design 100% responsive (mobile, tablette, desktop), moteur de recherche fuzzy Raycast (`Ctrl + K`), timeline animée, filtres dynamiques et lightboxes multimédias.
- **Fonctionnalités & Accessibilité** : Thème Sombre / Clair avec mémorisation locale, raccourcis clavier (`V`, `T`, `P`, `D`), impression CSS A4 calibrée, téléchargement direct du livrable PDF officiel.

---

## 🚀 CI/CD & Stratégie de Release Automatisée

Le pipeline GitHub Actions (`.github/workflows/build-pdf.yml`) est déclenché sur chaque Pull Request et push sur `master` :

1. **Linting & Validation** : Exécution de `uvx ruff check` et contrôle syntaxique de l'AST Jinja2 des templates.
2. **Compilation Multi-Moteurs** :
   - Génération instantanée du PDF Typst via `uv run scripts/compile_typst.py`.
   - Génération du PDF ConTeXt via conteneur Docker `yoyonel/pandoc`.
3. **Artifacts & GitHub Release** :
   - Sur merge sur la branche `master`, création automatique d'une **GitHub Release** (`YYYY-resume`) avec attachement des livrables PDF finaux :
     - `2026_ATTY_Resume_Typst.pdf` *(Recommandé pour LinkedIn et candidatures)*
     - `2026_ATTY_Resume_Legacy.pdf` *(Version ConTeXt)*
     - `2026_ATTY_References.pdf` *(Document de références)*

---

## 📋 Prérequis Locaux

- **Python 3.10+** avec [`uv`](https://docs.astral.sh/uv/) (gestion automatique et instantanée des dépendances).
- **Go-Task** (`task`) pour les workflows de développement.
- **Docker** *(Optionnel)* : uniquement requis si vous souhaitez compiler la cible legacy ConTeXt / Pandoc.
