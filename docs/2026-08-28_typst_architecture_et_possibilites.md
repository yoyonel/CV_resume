# Architecture Typst & Intégration dans le Projet CV_Resume

*Date : 28 Août 2026*

---

## 1. Vue d'Ensemble & Remplacement de l'Ancienne Chaîne

Le projet reposait historiquement sur une chaîne **Pandoc + ConTeXt MkIV (LuaTeX 2014)** encapsulée dans une image Docker de 2,5 Go, générant le PDF en 5 à 12 secondes avec une syntaxe TeX rigide.

L'introduction du moteur **Typst** (Proposition 3) modernise intégralement la chaîne de production :

- **Compilateur en Rust** : Temps de build < 30 ms.
- **Zéro conteneur obligatoire** : Exécution directe via `uv` et le package Python `typst` (30 Mo).
- **Langage de composition programmable** : Syntaxe claire (croisement de Markdown et Python/Rust), gestion native des structures de données (JSON, YAML, CSV).
- **Rendu vectoriel moderne** : Typographie Inter + JetBrains Mono, icônes vectorielles SVG intégrées, badges colorés par domaine.

---

## 2. Architecture des Données & Flux de Compilation

```text
┌─────────────────────────────────────────────────────────────┐
│                       DONNÉES SOURCES                       │
│    data/profile.json (métadonnées, dates, coordonnées)      │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                GÉNÉRATION & TEMPLATING                      │
│   scripts/compile_typst.py (Calcul âge dynamique + Jinja2)  │
│   typst_resume/resume.typ.j2 (Template Typst paramétré)     │
│   typst_resume/icons/*.svg (Icônes vectorielles)            │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                      MOTEUR TYPST                           │
│  - Typographie vectorielle : Inter + JetBrains Mono         │
│  - Badges sémantiques colorés par domaine (6 palettes)      │
│  - Grilles fractionnaires asymétriques                      │
│  - Icônes vectorielles natives (mail, phone, pin, etc.)     │
└──────────────────────────────┬──────────────────────────────┘
                               │  (< 30ms)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                        LIVRABLE                             │
│       data/pdf/2026/2026_ATTY_Resume_Typst.pdf              │
└──────────────────────────────┴──────────────────────────────┘
```

---

## 3. Système de Badges Sémantiques par Domaine

Les briques technologiques sont classifiées automatiquement via une fonction `#tech-domain(name)` et reçoivent une palette pastel à haute lisibilité :

| Domaine Technique | Nuance | Palette (Fond / Bordure / Texte) | Exemples |
|---|---|---|---|
| **Langages & Backend** | Indigo | `#EEF2FF` / `#C7D2FE` / `#312E81` | `Python`, `FastAPI`, `C++`, `Pydantic`, `Pytest` |
| **3D Temps-Réel & GPU** | Violet | `#F5F3FF` / `#DDD6FE` / `#4C1D95` | `OpenGL`, `Vulkan`, `DirectX`, `CUDA`, `GLSL`, `ROS` |
| **Bases de Données & Stockage** | Émeraude | `#ECFDF5` / `#A7F3D0` / `#064E3B` | `PostgreSQL`, `PostGIS`, `Redis`, `MongoDB`, `ElasticSearch` |
| **Cloud, DevOps & Infra** | Azur / Cyan | `#F0F9FF` / `#BAE6FD` / `#0369A1` | `Docker`, `Kubernetes`, `GCP`, `Terraform`, `Ansible`, `GitLab CI` |
| **Observabilité & Monitoring** | Ambre | `#FFFBEB` / `#FDE68A` / `#92400E` | `Prometheus`, `Grafana`, `ELK Stack`, `Kibana`, `Airflow` |
| **Architecture & Méthodes** | Ardoise | `#F1F5F9` / `#CBD5E1` / `#334155` | `Clean Architecture`, `Microservices`, `Event-Driven`, `gRPC` |

---

## 4. Composants & Helpers Typst Disponibles

Dans `typst_resume/resume.typ.j2` :

- **`#tag(name, domain: auto)`** : Génère un badge arrondi avec typographie JetBrains Mono et couleur automatique selon le domaine de la technologie.
- **`#icon(path, height: 8.8pt)`** : Intègre une icône vectorielle SVG inline avec alignement optique du baseline.
- **`#cv-section(title)`** : Génère un en-tête de section avec filet cyan et titre en gras indigo.
- **`#cv-entry(dates, role, company, location, details)`** : Structure une expérience professionnelle en grille 2 colonnes (dates à gauche, contenu et puces avec puces cyan à droite).

---

## 5. Commandes de Développement & Qualité (Go-Task & Makefile)

### Tâches Go-Task (`Taskfile.yml`)

```bash
task                  # Liste toutes les tâches disponibles
task lint             # Validation complète (Ruff Python + AST Jinja + JSON + Compilation Typst)
task fmt              # Formatage automatique du code Python via Ruff
task check            # Suite complète de validation et test de build
task watch            # Mode Live Watch avec recompilation instantanée sur modification
```

### Cibles Makefile (`Makefile`)

```bash
make typst            # Compile le CV Typst (data/pdf/YYYY/YYYY_ATTY_Resume_Typst.pdf)
make typst-watch      # Lance le watcher Typst autonome
make all              # Compile le CV Typst + le CV ConTeXt legacy
make clean            # Nettoie les artefacts et PDF générés
```

---

## 6. Mécanisme du Watcher (`scripts/watch_typst.py`)

- **Surveillance par horodatage (`mtime`)** : Surveille uniquement `data/profile.json` et `typst_resume/resume.typ.j2`.
- **Zéro cascade d'événements** : Insensible aux accès disques / lectures de fichiers lors de l'inclusion des icônes SVG.
- **Charge CPU au repos** : 0.0%.
- **Recompilation en mémoire** : Environ 200 ms (Jinja2 + décodage vectoriel SVG + Typst).

---

## 7. Perspectives & Capacités Avancées

### A. CV Multi-profils & Multi-formats automatisé
- **Déclinaison par spécialité** : Génération automatisée d'un profil ciblé *Lead Backend Python* ou *Expert 3D / Temps-Réel* par filtrage conditionnel sur les tags.
- **Déclinaison 1 page vs 2 pages** : Production conjointe d'un format 1 page (format US compact) et 2 pages (format Europe détaillé) depuis la même source JSON.

### B. Graphisme vectoriel & DataViz intégrée (Package `CeTZ`)
- Création de timelines de carrière vectorielles.
- Radar charts de compétences et jauges de séniorité.
- Intégration de diagrammes d'architecture directement dans le PDF.

### C. CI/CD ultra-légère
- Compilation en CI GitHub Actions en 2 à 3 secondes via `uv run` sans nécessiter de téléchargement d'image Docker volumineuse.
