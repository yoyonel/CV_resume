# CV & Resume — Lionel ATTY

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
- **Système de Badges Sémantiques par Domaine** : 8 palettes de couleurs harmonisées :
  - *Backend & Langages Core* (Indigo) : `Python 3.13`, `FastAPI`, `Flask`, `AsyncIO`, `Celery`, `C++ (17/20)`, `Rust`, etc.
  - *3D GPU, Rendu & Bas-Niveau* (Violet) : `Vulkan`, `OpenGL 4.5+`, `SIMD / AVX2`, `Data-Oriented (SoA)`, `GLSL / SPIR-V`.
  - *Micro-Architecture & Profiling* (Slate) : `Tracy Profiler`, `Intel VTune`, `RenderDoc`, `Linux perf`, `Flamegraph`, `Heaptrack`, `ASan / TSan / UBSan`.
  - *UI & Tooling Graphique* (Teal) : `Dear ImGui (UI/UX)`, `Qt`.
  - *IA, LLM & Tooling Agentique* (Ambre) : `AGY (Gemini)`, `Claude Code`, `MCP Servers`, `Dust`, `n8n`, `OpenAI API`.
  - *Bases de Données & Message Brokers* (Émeraude) : `MongoDB`, `Redis`, `RabbitMQ`, `PostgreSQL`, `PostGIS`, `JSONB`.
  - *Cloud, DevOps & Virtualisation* (Ciel) : `Azure / AKS`, `Docker / Podman`, `Kubernetes`, `QEMU / KVM`, `Terraform`, `GitLab CI`, `GitHub Actions`.
  - *Build Systems & Tooling* (Rose) : `Go-Task`, `Just`, `CMake`, `Conan 2.x`, `UV / Ruff`, `Typst`.
- **Composants Graphiques Sur-Mesure** :
  - *Stepper vertical temporel* avec nœuds colorés par expérience.
  - *Jauges de séniorité dynamiques* pilotées par les données.
  - *Diagrammes d'architecture pipeline* intégrés (`[Clients] ▶ [Gateway] ▶ [Microservices] ▶ [Stockage]`).
- **Équilibre & Gabarit Strict** : Calibrage millimétré sur **strictement 2 pages A4** avec zéro ligne orpheline et aération verticale maîtrisée.

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
task watch            # Lance le watcher temps réel (recompile le PDF instantanément à chaque sauvegarde)
task lint             # Analyse statique : Ruff sur scripts/, AST Jinja2 et compilation Typst
task fmt              # Formatage automatique du code Python avec Ruff
task check            # Suite complète de vérification et validation avant commit / merge
```

### Workflow Makefile (`make`)

```bash
make typst            # Compile le CV Typst (génère data/pdf/2026/2026_ATTY_Resume_Typst.pdf)
make typst-watch      # Démarre le watcher Typst
make all              # Compile l'ensemble des cibles (Typst + ConTeXt via Docker)
make clean            # Nettoie les artefacts générés
```

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
