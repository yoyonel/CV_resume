#set page(
  paper: "a4",
  margin: (x: 12.0mm, top: 7.0mm, bottom: 7.0mm),
)
#set text(
  font: ("Inter", "Liberation Sans", "DejaVu Sans"),
  size: 8.2pt,
  fill: rgb("#0F172A"),
  lang: "fr"
)
#set par(justify: true, leading: 0.44em)

// Theme Colors (Sleek Slate & Navy - Modern Senior Tech)
#let color-title = rgb("#0F172A")
#let color-brand = rgb("#1E40AF")
#let color-accent = rgb("#0284C7")
#let color-rule = rgb("#38BDF8")
#let color-muted = rgb("#64748B")
#let color-border = rgb("#E2E8F0")

// Vector Icon Helper
#let icon(path, height: 7.6pt, baseline: 18%) = box(
  baseline: baseline,
  height: height,
)[#image("icons/" + path)]

// 4 Muted & Sophisticated Tinted-Slate Palettes (Barely-tinted, ultra-clean)
#let tag-families = (
  // 1. Core Languages, Frameworks & Graphics Engines (Subtle Blue-Slate)
  core: (bg: rgb("#F1F5F9"), border: rgb("#CBD5E1"), text: rgb("#1E3A8A")),
  // 2. Data, Cloud, Storage & DevOps (Subtle Sage-Slate)
  infra: (bg: rgb("#F1F6F4"), border: rgb("#CFE0D8"), text: rgb("#164E3A")),
  // 3. AI, LLM & Agentic Tooling (Subtle Warm Sand-Slate)
  ai: (bg: rgb("#F7F5EE"), border: rgb("#E6DEC9"), text: rgb("#714513")),
  // 4. Tools, Profiling, Debug, UI & Build (Subtle Neutral Slate)
  tools: (bg: rgb("#F3F4F6"), border: rgb("#D1D5DB"), text: rgb("#374151")),
)

// Classifier into 4 High-Level Technical Families
#let tech-family(name) = {
  let n = lower(name)
  // AI Family
  if n in ("agy (gemini)", "antigravity (agy)", "claude code", "dust", "n8n", "mcp", "mcp servers", "openai api", "spacy", "gensim", "tensorflow", "nlp") {
    "ai"
  }
  // Data, Cloud, Infra & Storage Family
  else if n in ("mongodb", "mongoengine", "pymongo", "redis", "redis / streams", "redis streams", "rabbitmq", "postgresql", "postgis", "jsonb", "elasticsearch", "eventstore", "mariadb/mysql", "mariadb", "mysql", "hdfs", "minio", "mqtt", "azure storage", "azure", "azure / aks", "aks", "docker", "docker / podman", "podman", "kubernetes", "qemu / kvm", "qemu", "vagrant", "gcp", "google cloud platform", "terraform", "ansible", "gitlab ci", "github actions", "ci/cd", "saml", "scim", "rancher", "argo", "fluentd", "digital ocean", "perforce", "youtrack") {
    "infra"
  }
  // Core Languages, Graphics & Frameworks Family
  else if n in ("python", "python 3.13", "python 3.9+", "python 3.8", "python 3.x", "fastapi", "flask", "asyncio", "aiohttp", "graphql", "openapi", "asyncpg", "pydantic", "click", "cookiecutter", "jinja2", "pytest", "celery", "faststream", "pandas", "sqlalchemy", "geoalchemy2", "geopandas", "c++", "c++ (17/20)", "c++ (98/11/14/17)", "c11", "rust", "odin", "stl", "qt", "bash", "flask-admin", "dependency-injector", "structlog", "spectree", "grpc", "vulkan", "opengl 4.5+", "opengl", "directx 9/10", "directx", "glsl / spir-v", "glsl / hlsl", "glsl", "hlsl", "shaders hlsl", "opengl shaders", "opencl", "cuda", "openscenegraph", "ros", "blender", "opencv", "ffmpeg", "mpeg-ts", "simd / avx2", "data-oriented (soa)", "gpu", "li3ds") {
    "core"
  }
  // Tools, Profiling, Debug, UI & Build Family
  else {
    "tools"
  }
}

// Sophisticated Tinted Badge Helper
#let tag(name, family: auto) = {
  let fam = if family == auto { tech-family(name) } else { family }
  let c = tag-families.at(fam, default: tag-families.tools)
  box(
    fill: c.bg,
    stroke: 0.5pt + c.border,
    radius: 2.5pt,
    inset: (x: 2.7pt, y: 1.0pt),
    outset: 0pt,
    baseline: 0%,
  )[#text(size: 6.8pt, font: ("JetBrains Mono", "DejaVu Sans Mono"), weight: "medium", fill: c.text)[#name]]
}

// Helper: Section Heading with Generous Vertical Breathing Room
#let cv-section(title) = {
  v(8.5pt)
  block(width: 100%, below: 5.5pt)[
    #stack(
      spacing: 3pt,
      [
        #box(width: 14mm, height: 1.8pt, fill: color-rule)
        #h(4.5pt)
        #text(size: 9.6pt, weight: "bold", fill: color-brand)[#title]
      ]
    )
  ]
}

// Helper: Generic Reusable Pipeline Diagram Helper (Subtle Slate)
#let pipeline-diagram(steps) = {
  v(0.8pt)
  block(
    width: 100%,
    fill: rgb("#F8FAFC"),
    stroke: 0.5pt + rgb("#E2E8F0"),
    radius: 2.5pt,
    inset: (x: 2.5pt, y: 1.5pt),
  )[
    #let count = steps.len()
    #let cols = ()
    #for i in range(count) {
      cols.push(1fr)
      if i < count - 1 {
        cols.push(2.5mm)
      }
    }
    #grid(
      columns: cols,
      align: center + horizon,
      ..steps.map(step => {
        let is-primary = if "primary" in step { step.primary } else { false }
        let bg = if is-primary { rgb("#EFF6FF") } else { rgb("#FFFFFF") }
        let border = if is-primary { rgb("#CBD5E1") } else { rgb("#E2E8F0") }
        let text-col = if is-primary { rgb("#1E3A8A") } else { rgb("#334155") }
        box(
          width: 100%,
          height: 12.0pt,
          fill: bg,
          stroke: 0.5pt + border,
          radius: 2.0pt,
          inset: (x: 1pt, y: 1pt)
        )[
          #align(center + horizon)[#text(size: 5.5pt, weight: "bold", fill: text-col)[#step.label]]
        ]
      }).intersperse(text(size: 5.6pt, fill: rgb("#94A3B8"))[▶])
    )
  ]
}

// Helper: Experience Entry with Connected Vertical Stepper (Unified Navy)
#let cv-entry(
  dates: "",
  role: "",
  company: "",
  location: "",
  details: (),
  is-last: false,
  extra: none
) = {
  let is-current = "présent" in lower(dates) or "present" in lower(dates)
  let node-col = if is-current { color-brand } else { rgb("#475569") }
  grid(
    columns: (22mm, 1fr),
    column-gutter: 3.0mm,
    align: (right + top, left + top),
    [
      #v(0.5pt)
      #text(weight: "bold", size: 8.2pt, fill: color-title)[#dates]
    ],
    [
      #block(
        stroke: (left: if not is-last { 1.1pt + rgb("#E2E8F0") } else { 0pt }),
        inset: (left: 7.5pt, bottom: if not is-last { 3.2pt } else { 1pt }),
      )[
        #place(top + left, dx: -10.8pt, dy: 1.3pt)[
          #circle(radius: 2.8pt, fill: node-col, stroke: 1.2pt + rgb("#FFFFFF"))
        ]
        #text(weight: "bold", size: 8.7pt, fill: color-title)[#role]
        #text(weight: "bold", size: 8.7pt, fill: color-brand)[ — #company]
        #if location != "" [
          #text(style: "italic", size: 7.8pt, fill: color-muted)[ (#location)]
        ]
        
        #v(0.4pt)
        #list(
          tight: true,
          marker: text(fill: color-accent, size: 5.5pt)[●],
          ..details
        )
        #if extra != none [
          #extra
        ]
      ]
    ]
  )
}

// --- HEADER ---
#align(center)[
  #text(size: 16.0pt, weight: "bold", fill: color-title)[Lionel ATTY]
  
  #v(0.8pt)
  #text(size: 9.1pt, weight: "bold", fill: color-brand)[Sénior Développeur]
  #text(size: 8.2pt, fill: color-muted)[ • Backend, Architecture, SIG, 3D Temps-Réel, Python, C++]
  
  #v(1.2pt)
  #text(size: 7.8pt, fill: color-muted)[
    #icon("mail.svg") #link("mailto:lionel.atty@gmail.com")[#text(fill: color-accent)[lionel.atty\@gmail.com]] #h(3.5pt) | #h(3.5pt)
    #icon("phone.svg") +33 6 01 59 00 23 #h(3.5pt) | #h(3.5pt)
    #icon("map-pin.svg") 25 Bd Bouès, Marseille #h(3.5pt) | #h(3.5pt)
    #icon("laptop.svg") Télétravail / Hybride #h(3.5pt) | #h(3.5pt)
    #icon("calendar.svg") 45 ans
  ]
]

#v(-3pt)
#line(length: 100%, stroke: 0.5pt + rgb("#E2E8F0"))

// --- EXPERIENCES PROFESSIONNELLES (Page 1) ---
#cv-section("Expériences Professionnelles")

#cv-entry(
  dates: "2026 - Présent",
  role: "Senior Backend Développeur Python R&D",
  company: "LETSIGNIT",
  location: "Marseille / Télétravail — Depuis Janv. 2026",
  details: (
    [#text(style: "italic")[Conception et évolution de la plateforme SaaS de gestion centralisée des signatures mails et bannières marketing (millions d'utilisateurs M365 / Google Workspace).]],
    [#strong[Cœur Applicatif & Microservices] : Évolution du monolithe modulaire et services asynchrones sous #tag("Python 3.13") #tag("Flask") #tag("FastAPI") #tag("AsyncIO") #tag("Celery") #tag("FastStream") #tag("Pydantic") #tag("Spectree")],
    [#strong[Données & Messagerie Haute Charge] : Traitements asynchrones et mise en cache avec #tag("MongoDB") #tag("Redis") #tag("RabbitMQ") et #tag("Azure Storage")],
    [#strong[Sécurité, Identité & Droits] : Moteur d'autorisations RBAC (*lsi-authz*), intégrations protocolaires #tag("SAML"), #tag("SCIM"), OAuth2 et connecteurs Microsoft 365],
    [#strong[Cloud Azure & DevOps] : Déploiements sur #tag("Azure / AKS"), conteneurisation #tag("Docker"), pipelines #tag("GitLab CI"), monitoring #tag("Prometheus") et #tag("Elastic APM")],
    [#strong[Ingénierie Assistée par IA] : Intégration structurelle des LLM dans le cycle d'ingénierie avec #tag("Claude Code"), serveurs #tag("MCP Servers"), agents #tag("Dust") et orchestrations #tag("n8n").],
  ),
  extra: pipeline-diagram((
    (label: "Clients M365 / Google"),
    (label: "API Gateway & Authz"),
    (label: "Portal & Microservices", primary: true),
    (label: "MongoDB • Redis • RabbitMQ"),
  ))
)

#cv-entry(
  dates: "2021 - 2025",
  role: "Développeur Back End Python",
  company: "UNOWHY",
  location: "Paris / Télétravail — Juin 2021 à Déc. 2025",
  details: (
    [#text(style: "italic")[Conception et développement de la plateforme microservices backend pour l'éducation numérique.]],
    [#strong[Conception & Architecture] : Refonte et développement de microservices backend Python 3.9+ #tag("FastAPI") #tag("GraphQL") #tag("OpenAPI") #tag("Asyncpg") #tag("Pydantic") #tag("Click")],
    [#strong[Event-Driven & Stockage] : Architecture orientée événements avec #tag("PostgreSQL") #tag("EventStore") #tag("MQTT") #tag("MinIO")],
    [#strong[Infrastructure & Cloud] : Déploiement et orchestration sous #tag("Kubernetes") et #tag("Docker") sur Digital Ocean, gestion de configuration avec #tag("Ansible")],
    [#strong[Sécurité & Observabilité] : Authentification SSO avec #tag("Keycloak"), reverse-proxy #tag("Traefik"), workflows #tag("Argo"), logs #tag("Fluentd")],
    [#strong[Qualité & Méthodes] : Pratiques agiles SCRUM / Kanban, CI/CD #tag("GitLab CI"), tests sous #tag("Pytest"), #tag("GitFlow"), Notion, Jira.],
  ),
  extra: pipeline-diagram((
    (label: "Clients (Web / Apps)"),
    (label: "Traefik / Keycloak SSO"),
    (label: "FastAPI Microservices", primary: true),
    (label: "PostgreSQL • EventStore • MQTT"),
  ))
)

#cv-entry(
  dates: "2019 - 2021",
  role: "Data Engineer Senior",
  company: "365TALENTS",
  location: "Lyon / Télétravail",
  details: (
    [#text(style: "italic")[Conception, développement et intégration des algorithmes et pipelines de données pour le matching et la détection de compétences RH.]],
    [#strong[Data Processing & NLP] : Pipelines de données pour le matching RH #tag("Python 3.8") #tag("Elasticsearch") #tag("Redis") #tag("spaCy") #tag("Gensim") #tag("TensorFlow") #tag("Celery")],
    [#strong[Microservices & Communication] : Développement de services backend haute performance avec #tag("FastAPI") et #tag("gRPC")],
    [#strong[Cloud GCP & DevOps] : Exploitation de #tag("Google Cloud Platform") (Compute Engine, Pub/Sub, Storage), infrastructure as code avec #tag("Terraform") et #tag("Ansible")],
    [#strong[Monitoring & CI/CD] : Stack ELK complète #tag("Elasticsearch") #tag("Logstash") #tag("Kibana") #tag("APM"), métriques #tag("Prometheus"), pipelines #tag("GitHub Actions").],
    [#strong[Architecture & Qualité] : Clean Architecture, Domain-Driven Design (DDD), tests sous #tag("Pytest"), API REST, #tag("GitFlow").],
  ),
  extra: pipeline-diagram((
    (label: "Sources RH / Profils"),
    (label: "NLP (spaCy / Gensim / TF)"),
    (label: "Elasticsearch Matching"),
    (label: "API gRPC / FastAPI", primary: true),
  ))
)

#cv-entry(
  dates: "2019 (4 mois)",
  role: "Ingénieur Modèle & Industrialisation",
  company: "FORCITY",
  location: "Lyon",
  details: (
    [#text(style: "italic")[Industrialisation de modèles python de simulation urbaine pour l'optimisation de collecte et traitement des déchets (#link("https://web.archive.org/web/20180424075109/http://www.forcity.com/")[#text(fill: color-accent)[Archive ForCity]]).]],
    [#strong[Développements & SIG] : Modélisation sous Python 3.6, #tag("PostgreSQL") #tag("PostGIS") #tag("JSONB") #tag("SQLAlchemy") #tag("GeoAlchemy2") #tag("GeoPandas") #tag("Pytest")],
    [#strong[Environnement & Qualité] : Conteneurisation #tag("Docker"), métriques #tag("Grafana"), pipelines #tag("GitLab CI"), #tag("GitFlow"), YouTrack.],
  ),
  is-last: true
)

#pagebreak()

// --- EXPERIENCES (Suite Page 2) ---
#cv-entry(
  dates: "2017 - 2018",
  role: "Ingénieur Logiciel (R&D) & Data Analysis",
  company: "HOLIMETRIX",
  location: "Lyon",
  details: (
    [#strong[Projet Concurrence] : Agrégation et analyse de flux massifs de données publicitaires partenaires (SNPTV) pour établir le champ de concurrence des marques #tag("Python 3.x") #tag("MariaDB/MySQL") #tag("HDFS") #tag("SQLAlchemy") #tag("Pandas") #tag("Apache Airflow") #tag("Jupyter")],
    [#strong[Projet Pythie (Crawler TV)] : Chaîne automatisée d'acquisition de flux vidéo broadcast et détection de spots publicitaires TV en temps réel #tag("Python 3.x") #tag("C++") #tag("gRPC") #tag("Docker") #tag("Rancher") #tag("MongoDB") #tag("FFMPEG") #tag("OpenCV") #tag("Flask-admin") #tag("Plotly")],
  )
)

#cv-entry(
  dates: "2011 - 2017",
  role: "Chargé de Recherche (R&D)",
  company: "IGN",
  location: "Saint-Mandé",
  details: (
    [#strong[Projet LI3DS (Large Input 3D System)] : Logiciel modulaire d'acquisition et synchronisation temps réel de capteurs multiples (LIDAR, caméras, centrale inertielle) en #tag("C++") #tag("Python") #tag("ROS") #tag("Qt") #tag("PostGIS") #tag("Docker"). #link("https://github.com/LI3DS")[#icon("github.svg") #text(fill: color-accent)[GitHub LI3DS]] • #link("https://osgeo-fr.github.io/presentations_foss4gfr/2016/J2/Foss4g-li3ds.pdf")[#icon("slides.svg") #text(fill: color-accent)[Talk Foss4G]].],
    [#strong[Projet TrafiPollu] : Modélisation de dispersion des polluants dans un SIG QGIS. #link("https://remi.cura.info/interactive_map_tracking/")[#text(fill: color-accent)[Plugin QGIS Map Tracking]] • #link("https://web.archive.org/web/20160803093259/http://geotribu.net/node/801")[#text(fill: color-accent)[Article GeoTribu]].],
    [#strong[Projet iSpace&Time] : Cartographie 4D et simulation de flux urbains (SYMUVIA), moteur de rendu #tag("OpenSceneGraph") #tag("OpenGL Shaders") #tag("C++") #tag("Qt") #tag("CMake") Blender.],
  ),
  extra: pipeline-diagram((
    (label: "LIDAR + Caméras + IMU"),
    (label: "Drivers C++ & ROS Core", primary: true),
    (label: "Synchronisation Temps-Réel", primary: true),
    (label: "PostGIS 3D & Stockage"),
  ))
)

#cv-entry(
  dates: "2005 - 2008",
  role: "Ingénieur R&D Moteur 3D",
  company: "EDEN GAMES / ATARI",
  location: "Lyon",
  details: (
    [#strong[Jeu #link("https://en.wikipedia.org/wiki/Alone_in_the_Dark_%282008_video_game%29")[#text(fill: color-accent)[Alone in the Dark]] (PC, Xbox 360, PS3)] : R&D et intégration dans le moteur 3D propriétaire d'un système novateur d'ombres douces temps réel sur GPU #tag("C++") #tag("DirectX 9/10") #tag("Shaders HLSL") Perforce.],
    [#strong[Collaboration R&D Thèse CIFRE] : Recherche appliquée en rendu graphique temps réel avec le laboratoire ARTIS / GRAVIR (INRIA Rhône-Alpes).],
  ),
  is-last: true
)

// --- OUTILS & TECHNOLOGIES ---
#cv-section("Outils & Technologies")

#block(width: 100%, below: 2.0pt)[
  #grid(
    columns: (1fr, 1fr),
    column-gutter: 5mm,
    row-gutter: 3.2pt,
    [
      #text(weight: "bold", size: 8.2pt, fill: color-title)[3D GPU, Rendu, UI & Bas-Niveau]\
      #tag("Vulkan") #tag("OpenGL 4.5+") #tag("GLSL / SPIR-V") #tag("Dear ImGui (UI/UX)") #tag("SIMD / AVX2") #tag("Data-Oriented (SoA)")
    ],
    [
      #text(weight: "bold", size: 8.2pt, fill: color-title)[Micro-Architecture, Profiling & Debug]\
      #link("https://www.intel.com/content/www/us/en/developer/tools/oneapi/vtune-profiler.html")[#tag("Intel VTune Profiler")] #link("https://fr.wikipedia.org/wiki/Perf_%28Linux%29")[#tag("perf (Linux)")] #tag("Tracy Profiler") #tag("RenderDoc") #tag("Flamegraph") #tag("Heaptrack") #tag("GDB") #tag("ASan / TSan / UBSan") #tag("Cache Misses L1/L2/L3")
    ],
    [
      #text(weight: "bold", size: 8.2pt, fill: color-title)[Langages & Backend]\
      #tag("Python 3.13") #tag("C++ (17/20)") #tag("Rust") #tag("C11") #tag("Odin") #tag("FastAPI") #tag("Flask") #tag("AsyncIO") #tag("Celery") #tag("FastStream") #tag("Pydantic") #tag("Spectree") #tag("Pytest") #tag("Qt") #tag("Bash")
    ],
    [
      #text(weight: "bold", size: 8.2pt, fill: color-title)[IA, LLM & Tooling Agentique]\
      #tag("AGY (Gemini)") #tag("Claude Code") #tag("MCP Servers") #tag("Dust") #tag("n8n") #tag("OpenAI API") #tag("spaCy") #tag("Gensim")
    ],
    [
      #text(weight: "bold", size: 8.2pt, fill: color-title)[Bases de Données & Stockage]\
      #tag("MongoDB") #tag("Redis") #tag("RabbitMQ") #tag("PostgreSQL") #tag("PostGIS") #tag("JSONB") #tag("Elasticsearch") #tag("EventStore") #tag("Azure Storage")
    ],
    [
      #text(weight: "bold", size: 8.2pt, fill: color-title)[Cloud, DevOps & Build Systems]\
      #tag("Azure / AKS") #tag("Docker / Podman") #tag("Kubernetes") #tag("QEMU / KVM") #tag("Vagrant") #tag("Terraform") #tag("Ansible") #tag("GitLab CI") #tag("GitHub Actions") #tag("Go-Task") #tag("Just") #tag("CMake") #tag("Conan 2.x") #tag("UV / Ruff") #tag("Typst")
    ]
  )
]

// --- FORMATION & DIPLOMES ---
#cv-section("Formation & Diplômes")

#block(width: 100%, below: 2.0pt)[
  #grid(
    columns: (26mm, 1fr),
    column-gutter: 3.0mm,
    row-gutter: 3.0pt,
    [#text(weight: "bold", size: 8.1pt, fill: color-title)[2005 - 2009]],
    [
      #text(weight: "bold", size: 8.4pt, fill: color-title)[Doctorat / Thèse CIFRE (Rendu Graphique Temps-Réel & GPU)]
      #text(style: "italic", size: 7.8pt, fill: color-muted)[ — UJF / INRIA GRAVIR / Eden Games]\
      #text(size: 7.8pt)[Algorithmes de calcul et génération d'ombres douces temps réel sur GPU.]\
      #text(size: 7.6pt)[#icon("book.svg") #strong[Publication internationale] : #text(style: "italic")[Soft Shadow Maps: Efficient Sampling of Light Source Visibility], #strong[Computer Graphics Forum (CGF)], 2006 (#link("http://maverick.inria.fr/Publications/2006/AHLHHS06/")[#text(fill: color-accent)[Atty et al. - INRIA]]).]
    ],
    [#text(weight: "bold", size: 8.1pt, fill: color-title)[2004 - 2005]],
    [
      #text(weight: "bold", size: 8.4pt, fill: color-title)[Master 2 Recherche (Image, Vision, Robotique)]
      #text(style: "italic", size: 7.8pt, fill: color-muted)[ — UJF / INRIA (Grenoble)]\
      #text(size: 7.8pt)[Étude et amélioration des algorithmes de rendu temps réel et illumination globale (Projet Cyber-II).]
    ],
    [#text(weight: "bold", size: 8.1pt, fill: color-title)[2003 - 2004]],
    [
      #text(weight: "bold", size: 8.4pt, fill: color-title)[Master 1 & Magistère (Informatique & Mathématiques Appliquées)]
      #text(style: "italic", size: 7.8pt, fill: color-muted)[ — UJF Grenoble]\
      #text(size: 7.8pt)[Spécialisation en synthèse d'images, illumination temps réel, shaders GPU et géométrie algorithmique.]
    ]
  )
]

// --- PROJETS R&D PERSONNELS & OPEN SOURCE ---
#cv-section("Projets R&D Personnels, Open Source & Conférences")

#block(width: 100%, below: 2.0pt)[
  #grid(
    columns: (26mm, 1fr),
    column-gutter: 3.0mm,
    row-gutter: 3.0pt,
    [#text(weight: "bold", size: 8.1pt, fill: color-title)[2024 - 2026]],
    [
      #strong[Moteurs 3D Temps-Réel, UI/UX & Optimisation Bas-Niveau] : Moteurs de rendu et pipelines graphiques (RenderGraph, BindGroups) sous #tag("Vulkan") et #tag("OpenGL 4.5+") en #tag("C++ (17/20)"), #tag("C11"), #tag("Rust") et #tag("Odin"). Interfaces & HUD temps réel sous #tag("Dear ImGui (UI/UX)"). Vectorisation #tag("SIMD / AVX2"), architecture mémoire #tag("Data-Oriented (SoA)"), alignement 64B & prefetching. Réduction L1/L2/L3 Cache Misses & False Sharing via #link("https://fr.wikipedia.org/wiki/Perf_%28Linux%29")[#tag("perf (Linux)")] #tag("Flamegraph"), profiling #tag("Tracy Profiler") #link("https://www.intel.com/content/www/us/en/developer/tools/oneapi/vtune-profiler.html")[#tag("Intel VTune Profiler")] #tag("RenderDoc"), zéro-allocation validé sous #tag("Heaptrack"), sanitizers #tag("ASan / TSan / UBSan"), CI/CD #tag("GitHub Actions").
    ],
    [#text(weight: "bold", size: 8.1pt, fill: color-title)[2022 - 2026]],
    [
      #strong[Observabilité Réseau & IoT (#link("https://github.com/yoyonel/rpi-internet-monitoring")[#text(fill: color-accent)[rpi-internet-monitoring]])] : Stack de métrologie réseau et métriques système sur #tag("Raspberry Pi 4") (#tag("Docker Compose"), #tag("InfluxDB"), #tag("VictoriaMetrics"), #tag("Telegraf"), Ookla #tag("Speedtest CLI"), tableaux de bord #tag("Grafana"), timers #tag("Systemd")). Publication automatisée vers dashboard web sous #link("https://yoyonel.github.io/rpi-internet-monitoring/")[#text(fill: color-accent)[GitHub Pages]] (#tag("Chart.js"), 100/100 Lighthouse), tests E2E #tag("Playwright"), CI/CD #tag("GitHub Actions").
    ],
    [#text(weight: "bold", size: 8.1pt, fill: color-title)[2025 - 2026]],
    [
      #strong[IA Agentique & Écosystème MCP] : Outillage d'ingénierie et serveurs MCP pour agents IA sous #tag("AGY (Gemini)"), #tag("Claude Code"), serveurs #tag("MCP Servers") (optimisation de contexte), automatisation #tag("n8n") et assistants #tag("Dust").
    ],
    [#text(weight: "bold", size: 8.3pt, fill: color-title)[2021 - 2022]],
    [
      #strong[DocString] : Mentorat technique & masterclasses vidéo #link("https://youtu.be/aaim2oCGedk")[#icon("video.svg") #text(fill: color-accent)[Application CLI avec #tag("Python") & #tag("CI/CD")]] (#link("http://bit.ly/36mb5Ez")[#icon("slides.svg") #text(fill: color-accent)[Slides]]).
    ],
    [#text(weight: "bold", size: 8.1pt, fill: color-title)[2011 - 2019]],
    [
      #strong[Talks & Formations] : Talk #strong[PyCon.FR] (Microservices #tag("gRPC") et #tag("Python") pour le #tag("NLP")), Conférence #strong[FOSS4G-fr] (Acquisition temps réel LIDAR / capteurs), Formations supérieures #strong[IGN / ENSG] (#tag("Python") Géomatique & calcul scientifique #tag("GPU")).
    ]
  )
]

// --- LANGUES & DIVERS ---
#cv-section("Langues & Divers")

#block(width: 100%, below: 0pt)[
  #v(2.0pt)
  #list(
    tight: true,
    marker: text(fill: color-accent, size: 5.2pt)[●],
    [#strong[Langues] : Anglais (technique courant, veille & documentation quotidienne), Allemand (notions scolaires).],
    [#strong[Pratiques Musicales] : Guitare-Basse (15 ans de pratique en groupe), Percussions Africaines (2 ans).],
    [#strong[Sports & Activités] : Tennis en compétition (4ᵉ série, depuis 2021), Volley-ball (15 ans en compétition régionale), Football.],
    [#strong[Centres d'intérêt] : Architecture logicielle, Moteurs 3D bas-niveau / Vulkan, IA Agentique, Écosystème Open Source, Science-Fiction.]
  )
]