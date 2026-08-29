# Architecture Typst & Intégration dans le Projet CV_Resume

*Date : 28 Août 2026*

---

## 1. Vue d'Ensemble & Remplacement de l'Ancienne Chaîne

Le projet reposait historiquement sur une chaîne **Pandoc + ConTeXt MkIV (LuaTeX 2014)** encapsulée dans une image Docker de 2,5 Go, générant le PDF en 5 à 12 secondes avec une syntaxe TeX rigide.

L'introduction du moteur **Typst** (Proposition 3) modernise intégralement la chaîne de production :

- **Compilateur en Rust** : Temps de build < 30 ms.
- **Zéro conteneur obligatoire** : Exécution directe via `uv` et le package Python `typst` (30 Mo).
- **Langage de composition programmable** : Syntaxe claire (croisement de Markdown et Python/Rust), gestion native des structures de données (JSON, YAML, CSV).
- **Rendu vectoriel moderne** : Typographie Inter + JetBrains Mono, icônes vectorielles SVG intégrées, badges colorés par domaine et composants DataViz natifs.

---

## 2. Architecture des Données & Flux de Compilation

```text
┌─────────────────────────────────────────────────────────────────┐
│                        DONNÉES SOURCES                          │
│  data/profile.json (identifiants, dates, jauges de compétences) │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                     GÉNÉRATION & TEMPLATING                     │
│  - scripts/compile_typst.py (Calcul âge + durées d'expérience)  │
│  - typst_resume/resume.typ.j2 (Template Typst paramétré)        │
│  - typst_resume/icons/*.svg (Icônes vectorielles SVG)           │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                       MOTEUR TYPST                              │
│  - Typographie vectorielle : Inter + JetBrains Mono             │
│  - Badges sémantiques colorés par domaine (6 palettes)          │
│  - Timeline verticale connectée (Connected Stepper B.3)         │
│  - Jauges de séniorité dynamiques (Seniority Gauges B.2)        │
│  - Pipelines d'architecture vectoriels (Architecture B.4)       │
│  - Icônes vectorielles natives (mail, phone, pin, github...)    │
└────────────────────────────────┬────────────────────────────────┘
                                 │  (< 30ms)
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                           LIVRABLE                              │
│         data/pdf/2026/2026_ATTY_Resume_Typst.pdf                │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Composants Graphiques & DataViz Validés

### A. Badges Sémantiques par Domaine (`#tag`)

Les briques technologiques sont classifiées automatiquement via `#tech-domain(name)` et reçoivent une palette pastel à haute lisibilité :

| Domaine Technique | Nuance | Palette (Fond / Bordure / Texte) | Exemples |
|---|---|---|---|
| **Langages & Backend** | Indigo | `#EEF2FF` / `#C7D2FE` / `#312E81` | `Python`, `FastAPI`, `C++`, `Pydantic`, `Pytest` |
| **3D Temps-Réel & GPU** | Violet | `#F5F3FF` / `#DDD6FE` / `#4C1D95` | `OpenGL`, `Vulkan`, `DirectX`, `CUDA`, `GLSL`, `ROS` |
| **Bases de Données & Stockage** | Émeraude | `#ECFDF5` / `#A7F3D0` / `#064E3B` | `PostgreSQL`, `PostGIS`, `Redis`, `MongoDB`, `EventStore` |
| **Cloud, DevOps & Infra** | Azur / Cyan | `#F0F9FF` / `#BAE6FD` / `#0369A1` | `Docker`, `Kubernetes`, `GCP`, `Terraform`, `Ansible`, `GitLab CI` |
| **Observabilité & Monitoring** | Ambre | `#FFFBEB` / `#FDE68A` / `#92400E` | `Prometheus`, `Grafana`, `ELK Stack`, `Kibana`, `Airflow` |
| **Architecture & Méthodes** | Ardoise | `#F1F5F9` / `#CBD5E1` / `#334155` | `Clean Architecture`, `Microservices`, `Event-Driven`, `gRPC` |

---

### B. Timeline Verticale Connectée (Proposition B.3)

- **Fonctionnement** : Un fil conducteur vertical fin (`#E2E8F0`) relie dynamiquement les postes de haut en bas sur les Pages 1 et 2.
- **Nœuds vectoriels** : Pastille circulaire `●` avec halo blanc, dont la couleur s'adapte automatiquement au domaine de l'entreprise (`UNOWHY` -> Indigo, `365TALENTS` -> Ambre, `FORCITY` -> Azur, `HOLIMETRIX` -> Émeraude, `IGN` -> Indigo, `EDEN GAMES` -> Violet).
- **Scalabilité** : 100% extensible vers le bas pour tous les postes futurs sans distorsion graphique ni maintenance de largeur.

---

### C. Jauges de Séniorité 100% Dynamiques (Proposition B.2)

- **Source de vérité** : Déclarée dans `data/profile.json` avec année de départ (`start_year`) et fin éventuelle (`end_year` ou `null`) :
  ```json
  "skills_seniority": [
    { "label": "Python & Microservices", "start_year": 2011, "end_year": null, "domain": "backend" },
    { "label": "C++ & Rendu 3D GPU", "start_year": 2005, "end_year": 2018, "domain": "graphics" },
    { "label": "Bases de Données & PostGIS", "start_year": 2011, "end_year": null, "domain": "db" },
    { "label": "Cloud, DevOps & Conteneurs", "start_year": 2017, "end_year": null, "domain": "cloud" }
  ]
  ```
- **Calcul automatique** : `years = (end_year or current_year) - start_year`.
- **Rendu vectoriel** : Barres de progression proportionnelles arrondies avec code couleur du domaine et années réelles affichées en regard. Zéro maintenance manuelle au fil des années.

---

### D. Pipelines d'Architecture Vectoriels (Proposition B.4)

Helper générique `#pipeline-diagram(steps)` permettant d'illustrer les flux techniques clés :

1. **UNOWHY** (Cloud & Microservices) :
   `[Clients (Web / Apps)]` ▶ `[Traefik / Keycloak SSO]` ▶ `[FastAPI Microservices]` ▶ `[Postgres • EventStore • MQTT]`
2. **365TALENTS** (NLP & Data Engineering) :
   `[Sources RH / Profils]` ▶ `[NLP (spaCy / Gensim / TF)]` ▶ `[ElasticSearch Matching]` ▶ `[API gRPC / FastAPI]`
3. **IGN / LI3DS** (R&D 3D & Systèmes Embarqués) :
   `[LIDAR + Caméras + IMU]` ▶ `[Drivers C++ & ROS Core]` ▶ `[Synchronisation Temps-Réel]` ▶ `[PostGIS 3D & Stockage]`

---

## 4. Commandes de Développement & Qualité (Go-Task & Makefile)

### Tâches Go-Task (`Taskfile.yml`)

```bash
task                  # Liste toutes les tâches disponibles
task lint             # Validation complète (Ruff Python + AST Jinja + JSON + Compilation Typst)
task fmt              # Formatage automatique du code Python via Ruff
task check            # Suite complète de validation et test de build
task watch            # Mode Live Watch avec recompilation instantanée sur modification (0% CPU)
```

### Cibles Makefile (`Makefile`)

```bash
make typst            # Compile le CV Typst (data/pdf/YYYY/YYYY_ATTY_Resume_Typst.pdf)
make typst-watch      # Lance le watcher Typst autonome
make all              # Compile le CV Typst + le CV ConTeXt legacy
make clean            # Nettoie les artefacts et PDF générés
```

---

## 5. Mécanisme du Watcher (`scripts/watch_typst.py`)

- **Surveillance par horodatage (`mtime`)** : Surveille uniquement `data/profile.json` et `typst_resume/resume.typ.j2`.
- **Immunité totale aux boucles** : Insensible aux accès disques / ouvertures de fichiers émises lors de l'inclusion des icônes SVG.
- **Charge CPU au repos** : 0.0%.
- **Temps de compilation en mémoire** : ~200 ms.
