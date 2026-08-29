#!/usr/bin/env python3
# /// script
# dependencies = [
#   "jinja2>=3.1.0",
#   "typst>=0.15.0",
# ]
# ///
"""Build script for the static GitHub Pages resume site powered by Typst & PDF.js ISO engine."""

import json
import os
import shutil
import sys
from datetime import date, datetime, timezone
from pathlib import Path

try:
    import typst
    from jinja2 import Environment, FileSystemLoader
except ImportError:
    print(
        "Error: jinja2 and typst are required. Run with 'uv run scripts/build_site.py'",
        file=sys.stderr,
    )
    sys.exit(1)


def calculate_age(birthdate_val: str | date | datetime) -> int:
    if isinstance(birthdate_val, str):
        bdate = (
            datetime.strptime(birthdate_val, "%Y-%m-%d")
            .replace(tzinfo=timezone.utc)
            .date()
        )
    elif isinstance(birthdate_val, (datetime, date)):
        bdate = (
            birthdate_val if isinstance(birthdate_val, date) else birthdate_val.date()
        )
    else:
        raise TypeError(f"Unsupported birthdate format: {type(birthdate_val)}")
    today = datetime.now(tz=timezone.utc).date()
    return (
        today.year - bdate.year - ((today.month, today.day) < (bdate.month, bdate.day))
    )


def process_profile_data(profile: dict) -> dict:
    current_year = datetime.now(tz=timezone.utc).year
    if "birthdate" in profile:
        profile["age"] = calculate_age(profile["birthdate"])
    if "email" in profile:
        profile["email_escaped"] = profile["email"].replace("@", "\\@")
    if "skills_seniority" in profile:
        for item in profile["skills_seniority"]:
            end = item.get("end_year") or current_year
            item["years"] = max(1, end - item["start_year"])
    return profile


def get_structured_resume_data(profile: dict) -> dict:
    """Returns rich structured data for the interactive web experience."""
    experiences = [
        {
            "id": "letsignit",
            "company": "LETSIGNIT",
            "role": "Senior Backend Développeur Python R&D",
            "dates": "2026 - Présent",
            "period": "Depuis Janv. 2026",
            "location": "Marseille / Télétravail",
            "domain": "backend",
            "summary": "Conception et évolution de la plateforme SaaS de gestion centralisée des signatures mails et bannières marketing (millions d'utilisateurs M365 / Google Workspace).",
            "bullets": [
                "Cœur Applicatif & Microservices : Évolution du monolithe modulaire et développement de services asynchrones sous Python 3.13, Flask, FastAPI, AsyncIO, Celery, FastStream, Pydantic, Spectree.",
                "Données & Messagerie Haute Charge : Traitements asynchrones et mise en cache avec MongoDB, Redis, RabbitMQ et Azure Blob Storage.",
                "Sécurité, Identité & Droits : Refonte du moteur d'autorisations RBAC (lsi-authz), intégrations protocolaires SAML, SCIM, OAuth2 et connecteurs Microsoft 365.",
                "Cloud Azure & DevOps : Déploiements sur Azure / AKS, conteneurisation Docker, pipelines GitLab CI, monitoring Prometheus et Elastic APM.",
                "Ingénierie Assistée par IA : Intégration structurelle des LLM dans le cycle de développement avec Claude Code, serveurs MCP, agents Dust et orchestrations n8n.",
            ],
            "tags": ["Python 3.13", "FastAPI", "Flask", "AsyncIO", "Celery", "FastStream", "Pydantic", "Spectree", "MongoDB", "Redis", "RabbitMQ", "Azure Storage", "Azure / AKS", "Docker", "GitLab CI", "Prometheus", "Elastic APM", "SAML", "SCIM", "Claude Code", "MCP Servers", "Dust", "n8n"],
            "domains": ["backend", "cloud", "ai"],
            "pipeline": ["Clients M365 / Google", "API Gateway & Authz", "Portal & Microservices", "MongoDB • Redis • RabbitMQ"],
        },
        {
            "id": "unowhy",
            "company": "UNOWHY",
            "role": "Développeur Back End Python",
            "dates": "2021 - 2025",
            "period": "Juin 2021 à Déc. 2025",
            "location": "Paris / Télétravail",
            "domain": "backend",
            "summary": "Conception et développement de la plateforme microservices backend pour l'éducation numérique.",
            "bullets": [
                "Conception & Architecture : Refonte et développement de microservices backend Python 3.9+ (FastAPI, GraphQL, OpenAPI, Asyncpg, Pydantic, Click).",
                "Event-Driven & Stockage : Mise en place d'une architecture orientée événements avec PostgreSQL, EventStore, MQTT et MinIO.",
                "Infrastructure & Conteneurisation : Déploiement et orchestration sous Kubernetes et Docker sur Digital Ocean, gestion de configuration avec Ansible.",
                "Sécurité & Observabilité : Authentification SSO avec Keycloak, reverse-proxy Traefik, workflows Argo, agrégation de logs Fluentd.",
                "Qualité & Méthodologies : Pratiques agiles SCRUM / Kanban, intégration continue GitLab CI, tests complets sous Pytest, GitFlow.",
            ],
            "tags": ["Python", "FastAPI", "GraphQL", "OpenAPI", "Asyncpg", "Pydantic", "Click", "PostgreSQL", "EventStore", "MQTT", "MinIO", "Kubernetes", "Docker", "Ansible", "Keycloak", "Traefik", "Argo", "Fluentd", "GitLab CI", "Pytest", "GitFlow"],
            "domains": ["backend", "cloud"],
            "pipeline": ["Clients (Web / Apps)", "Traefik / Keycloak SSO", "FastAPI Microservices", "PostgreSQL • EventStore • MQTT"],
        },
        {
            "id": "365talents",
            "company": "365TALENTS",
            "role": "Data Engineer Senior",
            "dates": "2019 - 2021",
            "period": "2019 - 2021",
            "location": "Lyon / Télétravail",
            "domain": "backend",
            "summary": "Conception, développement et intégration des algorithmes et pipelines de données pour le matching et la détection de compétences RH.",
            "bullets": [
                "Data Processing & NLP : Pipelines de données pour le matching RH (Python 3.8, Elasticsearch, Redis / Redis Streams, spaCy, Gensim, TensorFlow, Dependency-Injector, Celery).",
                "Microservices & Communication : Développement de services backend haute performance avec FastAPI et gRPC.",
                "Cloud GCP & DevOps : Exploitation de Google Cloud Platform (Compute Engine, Cloud Functions, Pub/Sub, Storage), infrastructure as code avec Terraform et Ansible.",
                "Monitoring & CI/CD : Stack ELK complète (Elasticsearch, Logstash, Kibana, APM), métriques Prometheus et dashboards Grafana, GitHub Actions.",
                "Architecture & Qualité : Clean Architecture, Domain-Driven Design (DDD), tests sous Pytest, API REST, GitFlow.",
            ],
            "tags": ["Python 3.8", "Elasticsearch", "Redis", "spaCy", "Gensim", "TensorFlow", "Celery", "FastAPI", "gRPC", "Google Cloud Platform", "Terraform", "Ansible", "Logstash", "Kibana", "APM", "Prometheus", "GitHub Actions", "Pytest", "GitFlow"],
            "domains": ["backend", "cloud", "ai"],
            "pipeline": ["Sources RH / Profils", "NLP (spaCy / Gensim / TF)", "Elasticsearch Matching", "API gRPC / FastAPI"],
        },
        {
            "id": "forcity",
            "company": "FORCITY",
            "role": "Ingénieur Modèle & Industrialisation",
            "dates": "2019 (4 mois)",
            "period": "2019",
            "location": "Lyon",
            "domain": "sig",
            "summary": "Industrialisation de modèles python de simulation urbaine pour l'optimisation de collecte et traitement des déchets (Waste Vision).",
            "bullets": [
                "Développements & SIG : Modélisation sous Python 3.6, PostgreSQL, PostGIS, JSONB, SQLAlchemy, GeoAlchemy2, GeoPandas, Pytest.",
                "Pipelines & Simulation : Traitements spatiaux et vectoriels pour la simulation de flux démographiques et logistiques.",
                "Environnement & Qualité : Conteneurisation Docker, métriques Grafana, pipelines GitLab CI, GitFlow.",
            ],
            "tags": ["Python", "PostgreSQL", "PostGIS", "JSONB", "SQLAlchemy", "GeoAlchemy2", "GeoPandas", "Pytest", "Docker", "Grafana", "GitLab CI", "GitFlow"],
            "domains": ["backend", "sig", "cloud"],
            "links": [{"label": "Waste Vision", "url": "https://www.forcity.com/forcity-waste-vision-logiciel-optimiser-la-gestion-des-dechets"}],
        },
        {
            "id": "holimetrix",
            "company": "HOLIMETRIX",
            "role": "Ingénieur Logiciel (R&D) & Data Analysis",
            "dates": "2017 - 2018",
            "period": "2017 - 2018",
            "location": "Lyon",
            "domain": "backend",
            "summary": "R&D sur flux massifs publicitaires et chaîne automatisée de traitement broadcast TV.",
            "bullets": [
                "Projet Concurrence : Agrégation et analyse de flux massifs de données publicitaires partenaires (SNPTV) pour établir le champ de concurrence des marques (Python 3.x, MariaDB/MySQL, HDFS, SQLAlchemy, Pandas, Apache Airflow, Jupyter).",
                "Projet Pythie (Crawler TV) : Chaîne automatisée d'acquisition de flux vidéo broadcast et détection de spots publicitaires TV en temps réel (Python 3.x, C++, gRPC, Docker, Rancher, MongoDB, FFMPEG, OpenCV, Flask-admin, Plotly).",
            ],
            "tags": ["Python 3.x", "C++", "gRPC", "Docker", "Rancher", "MongoDB", "FFMPEG", "OpenCV", "MariaDB/MySQL", "HDFS", "SQLAlchemy", "Pandas", "Apache Airflow", "Jupyter", "Flask-admin", "Plotly"],
            "domains": ["backend", "graphics", "cloud"],
        },
        {
            "id": "ign",
            "company": "IGN",
            "role": "Chargé de Recherche (R&D)",
            "dates": "2011 - 2017",
            "period": "2011 - 2017",
            "location": "Saint-Mandé",
            "domain": "graphics",
            "summary": "Recherche et développement en acquisition 3D multi-capteurs, simulation et modélisation géomatique.",
            "bullets": [
                "Projet LI3DS (Large Input 3D System) : Logiciel modulaire d'acquisition et synchronisation temps réel de capteurs multiples (LIDAR, caméras, centrale inertielle) en C++, Python, ROS, Qt, PostGIS, Docker.",
                "Projet TrafiPollu : Production de données géographiques et modélisation de dispersion des polluants dans un SIG QGIS.",
                "Projet iSpace&Time : Cartographie 4D et simulation de flux urbains (SYMUVIA), moteur de rendu OpenSceneGraph / Shaders OpenGL, C++, Qt, CMake, Blender.",
            ],
            "tags": ["C++", "Python", "ROS", "Qt", "PostGIS", "Docker", "OpenSceneGraph", "OpenGL Shaders", "CMake", "Blender", "LIDAR", "SIG", "QGIS"],
            "domains": ["graphics", "sig", "backend"],
            "pipeline": ["LIDAR + Caméras + IMU", "Drivers C++ & ROS Core", "Synchronisation Temps-Réel", "PostGIS 3D & Stockage"],
            "links": [
                {"label": "GitHub LI3DS", "url": "https://github.com/LI3DS", "icon": "github"},
                {"label": "Talk Foss4G (PDF)", "url": "https://osgeo-fr.github.io/presentations_foss4gfr/2016/J2/Foss4g-li3ds.pdf", "icon": "slides"},
                {"label": "Plugin QGIS Map Tracking", "url": "http://remi-c.github.io/interactive_map_tracking/", "icon": "link"},
                {"label": "Article GeoTribu", "url": "http://geotribu.net/node/801", "icon": "link"},
            ],
        },
        {
            "id": "edengames",
            "company": "EDEN GAMES / ATARI",
            "role": "Ingénieur R&D Moteur 3D",
            "dates": "2005 - 2008",
            "period": "2005 - 2008",
            "location": "Lyon",
            "domain": "graphics",
            "summary": "R&D sur moteur 3D propriétaire pour jeu vidéo AAA et collaboration de recherche CIFRE.",
            "bullets": [
                "Jeu Alone in the Dark (PC, Xbox 360, PS3) : R&D et intégration dans le moteur 3D propriétaire d'un système novateur d'ombres douces temps réel sur GPU (C++, DirectX 9/10, Shaders HLSL, Perforce).",
                "Collaboration R&D Thèse CIFRE : Recherche appliquée en rendu graphique temps réel avec le laboratoire ARTIS / GRAVIR (INRIA Rhône-Alpes).",
            ],
            "tags": ["C++", "DirectX 9/10", "Shaders HLSL", "GPU", "Rendu 3D", "Perforce"],
            "domains": ["graphics"],
            "links": [{"label": "Alone in the Dark (2008)", "url": "https://en.wikipedia.org/wiki/Alone_in_the_Dark_%282008_video_game%29"}],
        },
    ]

    projects_and_talks = [
        {
            "title": "suckless-vulkan : Moteur 3D C++17, RenderGraph & RHI BindGroups",
            "dates": "2024 - 2026",
            "category": "Moteur Vulkan & Systèmes GPU",
            "description": "Moteur de rendu 3D haute performance en C++17 sous Vulkan 1.x. Architecture RHI moderne avec BindGroups déclaratifs et RenderGraph automatique (analyse DAG, tri topologique de Kahn, gestion automatique des transitions VkImageMemoryBarrier). Pipeline de post-processing unifié : Bloom Dual-Filtering FP16 (Jimenez 13-tap, 0.228 ms à 1080p), Auto-Exposure temporelle 64-bin LDS avec histogramme HUD procédural, streaming IBL asynchrone KTX2/Zstd. Zéro allocation dynamique sur le hot-path de rendu (745+ FPS). Intégration complète Tracy Profiler (CPU/GPU), Intel VTune, Heaptrack et CI/CD avec validation layers et tests de non-régression visuelle.",
            "tags": ["suckless-vulkan", "Vulkan 1.x", "C++17", "RenderGraph", "BindGroups", "GLSL / SPIR-V", "Dual-Filtering Bloom", "Compute Shaders", "AMD VMA", "Tracy Profiler", "Intel VTune", "Heaptrack", "GitHub Actions"],
            "domain": "graphics",
            "media": {
                "type": "image",
                "src": "assets/projects/suckless-odin-tracy.png",
                "caption": "Capture Profiling Tracy & Pipeline RenderGraph Vulkan",
                "gallery": [
                    {"src": "assets/projects/suckless-odin-tracy.png", "label": "Tracy GPU/CPU Profiler"},
                    {"src": "assets/projects/suckless-odin-imgui.png", "label": "HUD Diagnostique & Télémétrie"},
                ]
            },
            "links": [
                {"label": "GitHub suckless-vulkan", "url": "https://github.com/yoyonel/suckless-vulkan", "icon": "github"},
            ],
        },
        {
            "title": "suckless-odin : Moteur PBR, Compute IBL & Uber-Shader en Odin",
            "dates": "2024 - 2026",
            "category": "Rendu PBR & Langage Odin",
            "description": "Moteur de rendu 3D à base physique (PBR) en langage Odin sous OpenGL 4.5/4.6 Core. Modèle Cook-Torrance (GGX/Smith/Schlick), IBL temps réel piloté par Compute Shaders (conversion HDR 4K, convolution irradiance Monte Carlo, split-sum BRDF LUT), instancing géométrique SSBO (100 matériaux PBR). Pipeline Uber-Shader de post-processing à 15 effets (Bloom tent 13-tap, DoF cinématique avec bokeh, Motion Blur NeighborMax, FXAA 3.11, Color Grading LUT 3D .cube). Accélération vectorielle SIMD AVX2 et machines à états asynchrones TLA+. Port natif Windows AMD64 sans dépendance MSVC, intégration Steam Proton et packaging autonome .tar.zst / .zip.",
            "tags": ["suckless-odin", "Odin Language", "OpenGL 4.5/4.6", "Cook-Torrance PBR", "Compute IBL", "SIMD AVX2", "Uber-Shader (15 FX)", "Dear ImGui", "Cross-Compilation Windows", "Steam Proton", "Tracy Profiler", "Taskfile"],
            "domain": "graphics",
            "media": {
                "type": "image",
                "src": "assets/projects/suckless-odin-pbr.png",
                "caption": "Rendu PBR HDR Cook-Torrance (suckless-odin)",
                "gallery": [
                    {"src": "assets/projects/suckless-odin-pbr.png", "label": "Rendu PBR HDR (Front View)"},
                    {"src": "assets/projects/suckless-odin-imgui.png", "label": "Dear ImGui Overlay HUD"},
                    {"src": "assets/projects/suckless-odin-tracy.png", "label": "Tracy Profiler Trace"},
                ]
            },
            "links": [
                {"label": "GitHub suckless-odin", "url": "https://github.com/yoyonel/suckless-odin", "icon": "github"},
            ],
        },
        {
            "title": "suckless-ogl : Moteur 3D Minimaliste C11 & OpenGL 4.4 Core",
            "dates": "2023 - 2025",
            "category": "Moteur C11 & Architecture Pure",
            "description": "Moteur de rendu 3D minimaliste en C11 pur respectant rigoureusement la philosophie 'suckless' (codebase ultra-compacte, gestion mémoire stricte, zéro dépendance inutile). Pipeline moderne OpenGL 4.4 Core Profile avec GLAD, Skyboxes cubemaps, IcoSpheres procédurales, textures et éclairage Phong. Système de shaders GLSL avec compilation statique optimisée en Release et compilation dynamique à chaud en Debug. Environnement de build isolé sous distrobox (clang-dev), analyse statique stricte clang-tidy, tests unitaires ctest et rapports de couverture HTML llvm-cov.",
            "tags": ["suckless-ogl", "C11", "OpenGL 4.4 Core", "GLSL", "Distrobox", "clang-tidy", "llvm-cov", "CMake", "Makefile", "POSIX Standard", "Minimalist Architecture"],
            "domain": "graphics",
            "media": {
                "type": "image",
                "src": "assets/projects/suckless-ogl-ref.png",
                "caption": "Rendu de référence OpenGL 4.4 Core (suckless-ogl)",
            },
            "links": [
                {"label": "GitHub suckless-ogl", "url": "https://github.com/yoyonel/suckless-ogl", "icon": "github"},
                {"label": "Portail Documentation & Rapports", "url": "https://yoyonel.github.io/suckless-ogl/", "icon": "link"},
            ],
        },
        {
            "title": "rust-firework : Simulation Physique & Particules GPU Temps-Réel",
            "dates": "2023 - 2025",
            "category": "Simulation & Rendu Rust",
            "description": "Moteur de simulation et d'animation de feux d'artifice et particules en Rust. Architecture orientée données (ECS / Data-Oriented), calculs physiques vectorisés SIMD, instancing GPU temps réel et shaders d'illumination volumétrique.",
            "tags": ["rust-firework", "Rust", "Particules", "Simulation", "GPU", "Shaders", "SIMD", "ECS", "Volumetric Lights", "Temps-Réel", "GitHub Actions"],
            "domain": "graphics",
            "media": {
                "type": "gif",
                "src": "assets/projects/firework-demo.gif",
                "caption": "Démo animée : Rendu de particules & traînées de fumée",
                "gallery": [
                    {"src": "assets/projects/firework-demo.gif", "label": "Démo Feux d'artifice (GIF)"},
                    {"src": "assets/projects/smoke-trail-demo.gif", "label": "Traînée de fumée & Érosion (GIF)"},
                    {"src": "assets/projects/volumetric-lights.png", "label": "Lumières Volumétriques GPU"},
                ]
            },
            "links": [
                {"label": "GitHub rust-firework", "url": "https://github.com/yoyonel/rust-firework", "icon": "github"},
                {"label": "Documentation mdBook", "url": "https://yoyonel.github.io/rust-firework/", "icon": "link"},
            ],
        },
        {
            "title": "IA Agentique, Écosystème MCP & Automatisation",
            "dates": "2025 - 2026",
            "category": "IA & Outillage",
            "description": "Outillage d'ingénierie et serveurs MCP pour agents IA sous AGY (Gemini), Claude Code, serveurs MCP Servers (optimisation de contexte), automatisation n8n et assistants Dust.",
            "tags": ["LLM", "IA", "AGY (Gemini)", "Claude Code", "MCP Servers", "Dust", "n8n", "OpenAI API"],
            "domain": "ai",
        },
        {
            "title": "DocString : Mentorat Technique & Masterclasses Vidéo",
            "dates": "2021 - 2022",
            "category": "Formation & Conférence",
            "description": "Conception et animation de masterclasses vidéo techniques dédiées au développement d'applications CLI professionnelles avec Python et CI/CD.",
            "tags": ["Python", "CI/CD", "CLI", "Jupyter", "YouTube", "DocString"],
            "domain": "backend",
            "media": {
                "type": "video",
                "src": "https://img.youtube.com/vi/aaim2oCGedk/hqdefault.jpg",
                "video_url": "https://www.youtube.com/embed/aaim2oCGedk",
                "caption": "Masterclass Vidéo YouTube : Architecture d'applications CLI en Python",
            },
            "links": [
                {"label": "Vidéo Masterclass YouTube", "url": "https://youtu.be/aaim2oCGedk", "icon": "video"},
                {"label": "Support de Présentation (Slides)", "url": "http://bit.ly/36mb5Ez", "icon": "slides"},
            ],
        },
        {
            "title": "Conférences & Formations Spécialisées (PyCon.FR, FOSS4G-fr)",
            "dates": "2011 - 2019",
            "category": "Conférences & Enseignement",
            "description": "Talk PyCon.FR (Microservices gRPC & Python pour le NLP), Conférence FOSS4G-fr (Acquisition temps réel LIDAR / capteurs), Formations supérieures IGN / ENSG (Python Géomatique & calcul scientifique GPU).",
            "tags": ["Python", "gRPC", "NLP", "ROS", "LIDAR", "GPU", "FOSS4G", "PyCon", "LI3DS"],
            "domain": "sig",
            "links": [
                {"label": "Talk Foss4G LI3DS (PDF)", "url": "https://osgeo-fr.github.io/presentations_foss4gfr/2016/J2/Foss4g-li3ds.pdf", "icon": "slides"},
                {"label": "Dépôt GitHub LI3DS", "url": "https://github.com/LI3DS", "icon": "github"},
            ],
        },
    ]

    education = [
        {
            "dates": "2005 - 2009",
            "degree": "Doctorat / Thèse CIFRE (Rendu Graphique Temps-Réel & GPU)",
            "institution": "UJF / INRIA GRAVIR / Eden Games",
            "description": "Algorithmes de calcul et génération d'ombres douces temps réel sur GPU.",
            "publication": {
                "title": "Soft Shadow Maps: Efficient Sampling of Light Source Visibility",
                "journal": "Computer Graphics Forum (CGF), 2006",
                "authors": "Atty et al. - INRIA / Eden Games",
                "url": "http://maverick.inria.fr/Publications/2006/AHLHHS06/",
            },
            "domain": "graphics",
        },
        {
            "dates": "2004 - 2005",
            "degree": "Master 2 Recherche (Image, Vision, Robotique)",
            "institution": "UJF / INRIA (Grenoble)",
            "description": "Étude et amélioration des algorithmes de rendu temps réel et illumination globale (Projet Cyber-II).",
            "domain": "graphics",
        },
        {
            "dates": "2003 - 2004",
            "degree": "Master 1 & Magistère (Informatique & Mathématiques Appliquées)",
            "institution": "UJF Grenoble",
            "description": "Spécialisation en synthèse d'images, illumination temps réel, shaders GPU et géométrie algorithmique.",
            "domain": "graphics",
        },
    ]

    skills_categories = [
        {
            "title": "3D GPU, Rendu, UI & Bas-Niveau",
            "domain": "graphics",
            "tags": ["Vulkan", "OpenGL 4.5+", "C++ (17/20)", "C11", "Rust", "Odin", "Dear ImGui (UI/UX)", "GLSL / SPIR-V", "SIMD / AVX2", "Data-Oriented (SoA)"],
        },
        {
            "title": "Micro-Architecture, Profiling & Debug",
            "domain": "graphics",
            "tags": ["Tracy Profiler", "Intel VTune", "RenderDoc", "Linux perf", "Flamegraph", "Heaptrack", "GDB", "ASan / TSan / UBSan", "Cache Misses L1/L2"],
        },
        {
            "title": "Langages & Backend",
            "domain": "backend",
            "tags": ["Python 3.13", "FastAPI", "Flask", "AsyncIO", "Celery", "FastStream", "Pydantic", "Spectree", "Pytest", "Qt", "Bash"],
        },
        {
            "title": "IA, LLM & Tooling Agentique",
            "domain": "ai",
            "tags": ["AGY (Gemini)", "Claude Code", "MCP Servers", "Dust", "n8n", "OpenAI API", "spaCy", "Gensim"],
        },
        {
            "title": "Bases de Données & Stockage",
            "domain": "backend",
            "tags": ["MongoDB", "Redis", "RabbitMQ", "PostgreSQL", "PostGIS", "JSONB", "Elasticsearch", "EventStore", "Azure Storage"],
        },
        {
            "title": "Cloud, DevOps & Build Systems",
            "domain": "cloud",
            "tags": ["Azure / AKS", "Docker / Podman", "Kubernetes", "QEMU / KVM", "Vagrant", "Terraform", "Ansible", "GitLab CI", "GitHub Actions", "Go-Task", "Just", "CMake", "Conan 2.x", "UV / Ruff", "Typst"],
        },
    ]

    return {
        "profile": profile,
        "experiences": experiences,
        "projects_and_talks": projects_and_talks,
        "education": education,
        "skills_categories": skills_categories,
    }


def build_site(output_dir: Path | None = None) -> Path:
    root_dir = Path(__file__).resolve().parent.parent
    profile_path = root_dir / "data" / "profile.json"
    typst_dir = root_dir / "typst_resume"
    template_dir = root_dir / "site_template"
    output_typ_path = typst_dir / "resume.typ"

    if output_dir is None:
        output_dir = root_dir / "dist"

    assets_dir = output_dir / "assets"
    output_dir.mkdir(parents=True, exist_ok=True)
    assets_dir.mkdir(parents=True, exist_ok=True)

    template_assets_dir = template_dir / "assets"
    if template_assets_dir.exists():
        shutil.copytree(template_assets_dir, assets_dir, dirs_exist_ok=True)

    if not profile_path.exists():
        print(f"Error: Profile file not found at {profile_path}", file=sys.stderr)
        sys.exit(1)

    with open(profile_path, "r", encoding="utf-8") as f:
        profile = json.load(f)

    # Allow environment variable overrides
    env_mappings = {
        "CV_NAME": "name",
        "CV_BIRTHDATE": "birthdate",
        "CV_EMAIL": "email",
        "CV_PHONE": "phone",
        "CV_ADDRESS": "address",
        "CV_MOBILITY": "mobility",
        "CV_TITLE": "title",
        "CV_SPECIALTIES": "specialties",
    }
    for env_var, key in env_mappings.items():
        if env_var in os.environ:
            profile[key] = os.environ[env_var]

    profile = process_profile_data(profile)
    resume_data = get_structured_resume_data(profile)

    # 1. Render Typst template
    jinja_env = Environment(
        loader=FileSystemLoader(typst_dir),
        autoescape=False,
    )
    jinja_env.filters["age"] = calculate_age
    template = jinja_env.get_template("resume.typ.j2")
    rendered_typ = template.render(profile=profile)

    with open(output_typ_path, "w", encoding="utf-8") as f:
        f.write(rendered_typ)

    current_year = datetime.now(tz=timezone.utc).year
    pdf_year_path = root_dir / "data" / "pdf" / str(current_year) / f"{current_year}_ATTY_Resume_Typst.pdf"
    pdf_year_path.parent.mkdir(parents=True, exist_ok=True)

    # 2. Compile to PDF (100% ISO Master Document)
    typst.compile(str(output_typ_path), output=str(pdf_year_path))
    dist_pdf_name = f"{current_year}_ATTY_Resume_Typst.pdf"
    shutil.copy2(pdf_year_path, output_dir / dist_pdf_name)
    shutil.copy2(pdf_year_path, output_dir / "Lionel_ATTY_Resume_Typst.pdf")

    # 3. Compile SVG & PNG for vector fallbacks and social sharing
    svg_raw_pages = typst.compile(str(output_typ_path), format="svg")
    for idx, raw_svg in enumerate(svg_raw_pages):
        svg_file_path = assets_dir / f"cv-page-{idx+1}.svg"
        with open(svg_file_path, "w", encoding="utf-8") as f:
            f.write(raw_svg.decode("utf-8"))

    png_pages = typst.compile(str(output_typ_path), format="png", ppi=150)
    for idx, raw_png in enumerate(png_pages):
        png_file_path = assets_dir / f"cv-page-{idx+1}.png"
        with open(png_file_path, "wb") as f:
            f.write(raw_png)

    # 4. Render index.html via Jinja2 template with rich context
    site_env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=False,
    )
    html_tpl = site_env.get_template("index.html.j2")
    html_content = html_tpl.render(
        profile=profile,
        pdf_filename=dist_pdf_name,
        build_year=current_year,
        resume_data=resume_data,
        resume_json=json.dumps(resume_data, ensure_ascii=False),
    )

    index_html_path = output_dir / "index.html"
    with open(index_html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"✓ Rich & ISO PDF Static Site built in: {output_dir}")
    print(f"  - HTML: {index_html_path}")
    print(f"  - PDF:  {output_dir / dist_pdf_name}")
    print(f"  - SVGs: {len(svg_raw_pages)} vector pages in assets/")
    print(f"  - PNGs: {len(png_pages)} preview images in assets/")
    return output_dir


def main():
    build_site()


if __name__ == "__main__":
    main()
