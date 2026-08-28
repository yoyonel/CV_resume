#set page(
  paper: "a4",
  margin: (x: 14mm, top: 11mm, bottom: 11mm),
)
#set text(
  font: ("Inter", "Liberation Sans", "DejaVu Sans"),
  size: 9.3pt,
  fill: rgb("#0F172A"),
  spacing: 120%,
  lang: "fr"
)
#set par(justify: true, leading: 0.54em)

// Theme Colors
#let color-title = rgb("#0F172A")
#let color-brand = rgb("#1E40AF")
#let color-accent = rgb("#0284C7")
#let color-rule = rgb("#38BDF8")
#let color-muted = rgb("#64748B")

// Vector Icon Helper
#let icon(path, height: 8.8pt, baseline: 18%) = box(
  baseline: baseline,
  height: height,
)[#image("icons/" + path)]

// Domain-based Tag Palette
#let tag-colors = (
  // Backend & Core Languages (Indigo)
  backend: (bg: rgb("#EEF2FF"), border: rgb("#C7D2FE"), text: rgb("#312E81")),
  // 3D & Graphics (Purple/Violet)
  graphics: (bg: rgb("#F5F3FF"), border: rgb("#DDD6FE"), text: rgb("#4C1D95")),
  // Database & Storage (Emerald/Teal)
  db: (bg: rgb("#ECFDF5"), border: rgb("#A7F3D0"), text: rgb("#064E3B")),
  // Cloud & DevOps (Sky/Cyan)
  cloud: (bg: rgb("#F0F9FF"), border: rgb("#BAE6FD"), text: rgb("#0369A1")),
  // Monitoring & Observability (Amber/Warm)
  monitoring: (bg: rgb("#FFFBEB"), border: rgb("#FDE68A"), text: rgb("#92400E")),
  // Architecture & Methods (Slate)
  arch: (bg: rgb("#F1F5F9"), border: rgb("#CBD5E1"), text: rgb("#334155")),
  // Default neutral
  default: (bg: rgb("#F8FAFC"), border: rgb("#E2E8F0"), text: rgb("#1E293B")),
)

// Automatic technology domain classifier
#let tech-domain(name) = {
  let n = lower(name)
  if n in ("python", "python 3.8", "python 3.9+", "python 3.x", "fastapi", "graphql", "openapi", "asyncpg", "pydantic", "click", "cookiecutter", "jinja2", "pytest", "celery", "pandas", "sqlalchemy", "geoalchemy2", "geopandas", "c++", "c++ (98/11/14/17)", "stl", "qt", "bash", "flask-admin", "flask", "dependency-injector", "spacy", "gensim", "tensorflow") {
    "backend"
  } else if n in ("opengl", "vulkan", "directx 9/10", "directx", "glsl / hlsl", "glsl", "hlsl", "shaders hlsl", "opengl shaders", "opencl", "cuda", "openscenegraph", "ros", "blender", "opencv", "ffmpeg", "mpeg-ts") {
    "graphics"
  } else if n in ("postgresql", "postgis", "jsonb", "redis", "redis / streams", "redis streams", "elasticsearch", "mongodb", "eventstore", "mariadb/mysql", "mariadb", "mysql", "hdfs", "minio", "mqtt") {
    "db"
  } else if n in ("docker", "kubernetes", "gcp", "google cloud platform", "terraform", "ansible", "github actions", "gitlab ci", "traefik", "keycloak", "keycloak sso", "rancher", "argo", "fluentd", "digital ocean", "perforce", "youtrack") {
    "cloud"
  } else if n in ("prometheus", "grafana", "elk stack", "logstash", "kibana", "apm", "filebeat", "apache airflow", "jupyter", "plotly") {
    "monitoring"
  } else if n in ("clean architecture", "microservices", "event-driven", "grpc", "rest", "scrum / kanban", "scrum", "kanban", "gitflow", "ddd", "domain-driven design (ddd)", "api rest") {
    "arch"
  } else {
    "default"
  }
}

// Helper: Technology Tag Badge with Semantic Colors
#let tag(name, domain: auto) = {
  let dom = if domain == auto { tech-domain(name) } else { domain }
  let c = tag-colors.at(dom, default: tag-colors.default)
  box(
    fill: c.bg,
    stroke: 0.5pt + c.border,
    radius: 3pt,
    inset: (x: 3.5pt, y: 1.8pt),
    outset: 0pt,
    baseline: 0%,
  )[#text(size: 7.8pt, font: ("JetBrains Mono", "DejaVu Sans Mono"), weight: "medium", fill: c.text)[#name]]
}

// Helper: Section Heading
#let cv-section(title) = {
  v(7pt)
  block(width: 100%, below: 6pt)[
    #stack(
      spacing: 4pt,
      [
        #box(width: 18mm, height: 2.5pt, fill: color-rule)
        #h(6pt)
        #text(size: 11pt, weight: "bold", fill: color-brand)[#title]
      ]
    )
  ]
}

// Helper: Experience Entry
#let cv-entry(
  dates: "",
  role: "",
  company: "",
  location: "",
  details: ()
) = {
  block(width: 100%, below: 7pt)[
    #grid(
      columns: (26mm, 1fr),
      column-gutter: 4mm,
      align: (left, left),
      [
        #text(weight: "bold", size: 8.8pt, fill: color-title)[#dates]
      ],
      [
        #text(weight: "bold", size: 9.6pt, fill: color-title)[#role]
        #text(weight: "bold", size: 9.6pt, fill: color-brand)[ — #company]
        #if location != "" [
          #text(style: "italic", size: 8.8pt, fill: color-muted)[ (#location)]
        ]
        
        #v(1.5pt)
        #list(
          tight: true,
          marker: text(fill: color-accent, size: 7pt)[●],
          ..details
        )
      ]
    )
  ]
}

// --- HEADER ---
#align(center)[
  #text(size: 18pt, weight: "bold", fill: color-title)[Lionel ATTY]
  
  #v(2.5pt)
  #text(size: 10pt, weight: "bold", fill: color-brand)[Sénior Développeur]
  #text(size: 9.2pt, fill: color-muted)[ • Backend, Architecture, SIG, 3D Temps-Réel, Python, C++]
  
  #v(3pt)
  #text(size: 8.8pt, fill: color-muted)[
    #icon("mail.svg") #link("mailto:lionel.atty@gmail.com")[#text(fill: color-accent)[lionel.atty\@gmail.com]] #h(6pt)
    #icon("phone.svg") +33 6 01 59 00 23 #h(6pt)
    #icon("map-pin.svg") 25 Bd Bouès, Marseille #h(6pt)
    #icon("laptop.svg") Télétravail / Hybride #h(6pt)
    #icon("calendar.svg") 45 ans
  ]
]

#v(-1pt)
#line(length: 100%, stroke: 0.5pt + rgb("#E2E8F0"))

// --- EXPERIENCES PROFESSIONNELLES (Page 1) ---
#cv-section("Expériences Professionnelles")

#cv-entry(
  dates: "2021 - 2025",
  role: "Développeur Back End Python",
  company: "UNOWHY",
  location: "Paris / Télétravail — Juin 2021 à Déc. 2025",
  details: (
    [#text(style: "italic")[Conception et développement de la plateforme microservices backend pour l'éducation numérique.]],
    [#strong[Conception & Architecture] : Refonte et développement de microservices backend Python 3.9+ #tag("FastAPI") #tag("GraphQL") #tag("OpenAPI") #tag("Asyncpg") #tag("Pydantic") #tag("Click")],
    [#strong[Event-Driven & Stockage] : Mise en place d'une architecture orientée événements avec #tag("PostgreSQL") #tag("EventStore") #tag("MQTT") #tag("MinIO")],
    [#strong[Infrastructure & Cloud] : Déploiement et orchestration sous #tag("Kubernetes") et #tag("Docker") sur Digital Ocean, gestion de configuration avec #tag("Ansible")],
    [#strong[Sécurité & Observabilité] : Authentification SSO avec #tag("Keycloak"), reverse-proxy #tag("Traefik"), workflows #tag("Argo"), logs #tag("Fluentd")],
    [#strong[Qualité & Méthodes] : Pratiques agiles SCRUM / Kanban, CI/CD #tag("GitLab CI"), tests sous #tag("Pytest"), #tag("GitFlow"), Notion, Jira.],
  )
)

#cv-entry(
  dates: "2019 - 2021",
  role: "Data Engineer Senior",
  company: "365TALENTS",
  location: "Lyon / Télétravail",
  details: (
    [#text(style: "italic")[Conception, développement et intégration des algorithmes et pipelines de données pour le matching et la détection de compétences RH.]],
    [#strong[Data Processing & NLP] : Conception d'algorithmes et pipelines de données pour le matching de compétences RH #tag("Python 3.8") #tag("ElasticSearch") #tag("Redis") #tag("spaCy") #tag("Gensim") #tag("TensorFlow") #tag("Celery")],
    [#strong[Microservices & Communication] : Développement de services backend haute performance avec #tag("FastAPI") et #tag("gRPC")],
    [#strong[Cloud GCP & DevOps] : Exploitation de #tag("Google Cloud Platform") (Compute Engine, Cloud Functions, Pub/Sub, Cloud Scheduler, Cloud Storage), infrastructure as code avec #tag("Terraform") et #tag("Ansible")],
    [#strong[Monitoring & CI/CD] : Stack ELK complète #tag("Elasticsearch") #tag("Logstash") #tag("Kibana") #tag("APM"), métriques #tag("Prometheus") et dashboards #tag("Grafana"), pipelines #tag("GitHub Actions") avec runners auto-hébergés.],
    [#strong[Architecture & Qualité] : Clean Architecture, Domain-Driven Design (DDD), tests sous #tag("Pytest"), API REST, #tag("GitFlow").],
  )
)

#cv-entry(
  dates: "2019 (4 mois)",
  role: "Ingénieur Modèle & Industrialisation",
  company: "FORCITY",
  location: "Lyon",
  details: (
    [#text(style: "italic")[Industrialisation de modèles python de simulation urbaine pour l'optimisation de collecte et traitement des déchets (#link("https://www.forcity.com/forcity-waste-vision-logiciel-optimiser-la-gestion-des-dechets")[#text(fill: color-accent)[Waste Vision]]).]],
    [#strong[Développements & SIG] : Modélisation sous Python 3.6, #tag("PostgreSQL") #tag("PostGIS") #tag("JSONB") #tag("SQLAlchemy") #tag("GeoAlchemy2") #tag("GeoPandas") #tag("Pytest")],
    [#strong[Pipelines & Simulation] : Traitements spatiaux et vectoriels pour la simulation de flux démographiques et logistiques.],
    [#strong[Environnement & Qualité] : Conteneurisation #tag("Docker"), métriques #tag("Grafana"), pipelines #tag("GitLab CI"), #tag("GitFlow"), YouTrack.],
  )
)

#cv-entry(
  dates: "2017 - 2018",
  role: "Ingénieur Logiciel (R&D) & Data Analysis",
  company: "HOLIMETRIX",
  location: "Lyon",
  details: (
    [#strong[Projet Concurrence] : Agrégation et analyse de flux massifs de données publicitaires partenaires (SNPTV) pour établir le champ de concurrence des marques #tag("Python 3.x") #tag("MariaDB/MySQL") #tag("HDFS") #tag("SQLAlchemy") #tag("Pandas") #tag("Apache Airflow") #tag("Jupyter")],
    [#strong[Projet Pythie (Crawler TV)] : Conception d'une chaîne automatisée d'acquisition de flux vidéo broadcast et détection de spots publicitaires TV en temps réel #tag("Python 3.x") #tag("C++") #tag("gRPC") #tag("Docker") #tag("Rancher") #tag("MongoDB") #tag("FFMPEG") #tag("OpenCV") #tag("Flask-admin") #tag("Plotly")],
  )
)

#pagebreak()

// --- EXPERIENCES (Suite Page 2) ---
#cv-entry(
  dates: "2011 - 2017",
  role: "Chargé de Recherche (R&D)",
  company: "IGN",
  location: "Saint-Mandé",
  details: (
    [#strong[Projet LI3DS (Large Input 3D System)] : Conception et développement d'un logiciel modulaire pilotant l'acquisition et la synchronisation temps réel de capteurs multiples (LIDAR, caméras, centrale inertielle) en #tag("C++") #tag("Python") #tag("ROS") #tag("Qt") #tag("PostGIS") #tag("Docker"). #link("https://github.com/LI3DS")[#icon("github.svg") #text(fill: color-accent)[GitHub LI3DS]] • #link("https://osgeo-fr.github.io/presentations_foss4gfr/2016/J2/Foss4g-li3ds.pdf")[#icon("slides.svg") #text(fill: color-accent)[Talk Foss4G]].],
    [#strong[Projet TrafiPollu] : Production de données géographiques et modélisation de dispersion des polluants dans un SIG QGIS. #link("http://remi-c.github.io/interactive_map_tracking/")[#text(fill: color-accent)[Plugin QGIS Map Tracking]] • #link("http://geotribu.net/node/801")[#text(fill: color-accent)[Article GeoTribu]].],
    [#strong[Projet iSpace&Time] : Cartographie 4D et simulation de flux urbains (SYMUVIA), moteur de rendu #tag("OpenSceneGraph") #tag("OpenGL Shaders") #tag("C++") #tag("Qt") #tag("CMake") Blender.],
  )
)

#cv-entry(
  dates: "2005 - 2008",
  role: "Ingénieur R&D Moteur 3D",
  company: "EDEN GAMES / ATARI",
  location: "Lyon",
  details: (
    [#strong[Jeu #link("https://en.wikipedia.org/wiki/Alone_in_the_Dark_%282008_video_game%29")[#text(fill: color-accent)[Alone in the Dark]] (PC, Xbox 360, PS3)] : R&D et intégration dans le moteur 3D propriétaire d'un système novateur d'ombres douces temps réel sur GPU #tag("C++") #tag("DirectX 9/10") #tag("Shaders HLSL") Perforce.],
    [#strong[Collaboration R&D Thèse CIFRE] : Travaux de recherche appliquée en rendu graphique temps réel avec le laboratoire ARTIS / GRAVIR (INRIA Rhône-Alpes).],
  )
)

// --- OUTILS & TECHNOLOGIES ---
#cv-section("Outils & Technologies")

#block(width: 100%, below: 6pt)[
  #grid(
    columns: (1fr, 1fr),
    column-gutter: 6mm,
    row-gutter: 5pt,
    [
      #text(weight: "bold", size: 8.8pt, fill: color-title)[Langages & Frameworks]\
      #tag("Python") #tag("FastAPI") #tag("Pydantic") #tag("Asyncpg") #tag("Pytest") #tag("Celery") #tag("Pandas") #tag("SQLAlchemy") #tag("C++ (98/11/14/17)") #tag("STL") #tag("Qt") #tag("Bash")
    ],
    [
      #text(weight: "bold", size: 8.8pt, fill: color-title)[3D Temps-Réel & Graphisme]\
      #tag("OpenGL") #tag("Vulkan") #tag("DirectX 9/10") #tag("GLSL / HLSL") #tag("OpenCL") #tag("CUDA") #tag("OpenSceneGraph") #tag("ROS")
    ],
    [
      #text(weight: "bold", size: 8.8pt, fill: color-title)[Bases de Données & Stockage]\
      #tag("PostgreSQL") #tag("PostGIS") #tag("JSONB") #tag("Redis / Streams") #tag("ElasticSearch") #tag("MongoDB") #tag("EventStore") #tag("MariaDB/MySQL") #tag("HDFS")
    ],
    [
      #text(weight: "bold", size: 8.8pt, fill: color-title)[Cloud, DevOps & Infra]\
      #tag("Docker") #tag("Kubernetes") #tag("GCP") #tag("Terraform") #tag("Ansible") #tag("GitHub Actions") #tag("GitLab CI") #tag("Traefik") #tag("Keycloak SSO")
    ],
    [
      #text(weight: "bold", size: 8.8pt, fill: color-title)[Observabilité & Monitoring]\
      #tag("Prometheus") #tag("Grafana") #tag("ELK Stack") #tag("Logstash") #tag("Kibana") #tag("APM") #tag("Filebeat")
    ],
    [
      #text(weight: "bold", size: 8.8pt, fill: color-title)[Architecture & Méthodes]\
      #tag("Clean Architecture") #tag("Microservices") #tag("Event-Driven") #tag("gRPC") #tag("REST") #tag("SCRUM / KANBAN") #tag("GitFlow")
    ]
  )
]

// --- ETUDES & DIPLOMES ---
#cv-section("Études & Diplômes")

#block(width: 100%, below: 5pt)[
  #grid(
    columns: (26mm, 1fr),
    column-gutter: 4mm,
    row-gutter: 4pt,
    [#text(weight: "bold", size: 8.8pt, fill: color-title)[2005 - 2009]],
    [
      #text(weight: "bold", size: 9.2pt, fill: color-title)[Thèse CIFRE (Rendu Graphique Temps-Réel & GPU)]
      #text(style: "italic", size: 8.6pt, fill: color-muted)[ — UJF / INRIA GRAVIR / Eden Games]\
      #text(size: 8.6pt)[Algorithmes de calcul et génération d'ombres douces temps réel sur GPU.]\
      #text(size: 8.4pt)[#icon("book.svg") #strong[Publication internationale] : #text(style: "italic")[Soft Shadow Maps: Efficient Sampling of Light Source Visibility], #strong[Computer Graphics Forum (CGF)], 2006 (#link("http://maverick.inria.fr/Publications/2006/AHLHHS06/")[#text(fill: color-accent)[Atty et al. - INRIA]]).]
    ],
    [#text(weight: "bold", size: 8.8pt, fill: color-title)[2004 - 2005]],
    [
      #text(weight: "bold", size: 9.2pt, fill: color-title)[Master 2 Recherche (Image, Vision, Robotique)]
      #text(style: "italic", size: 8.6pt, fill: color-muted)[ — UJF / INRIA (Grenoble)]\
      #text(size: 8.6pt)[Étude et amélioration des algorithmes de rendu temps réel et illumination globale (Projet Cyber-II).]
    ],
    [#text(weight: "bold", size: 8.8pt, fill: color-title)[2003 - 2004]],
    [
      #text(weight: "bold", size: 9.2pt, fill: color-title)[Master 1 / Magistère (Informatique & Mathématiques Appliquées)]
      #text(style: "italic", size: 8.6pt, fill: color-muted)[ — UJF Grenoble]\
      #text(size: 8.6pt)[Spécialisation en synthèse d'images, illumination temps réel, shaders GPU et géométrie algorithmique.]
    ]
  )
]

// --- CONFERENCES, FORMATIONS & OPEN SOURCE ---
#cv-section("Conférences, Formations & Open Source")

#block(width: 100%, below: 5pt)[
  #grid(
    columns: (26mm, 1fr),
    column-gutter: 4mm,
    row-gutter: 3.5pt,
    [#text(weight: "bold", size: 8.8pt, fill: color-title)[2021 - 2022]],
    [
      #strong[DocString] : Mentorat technique & masterclass vidéo #link("https://youtu.be/aaim2oCGedk")[#icon("video.svg") #text(fill: color-accent)[Application CLI avec Python & CI/CD]] (#link("https://youtu.be/aaim2oCGedk")[#text(fill: color-accent)[Partie 1]], #link("https://youtu.be/zD1F3xJzJzY")[#text(fill: color-accent)[Partie 2]], #link("http://bit.ly/36mb5Ez")[#icon("slides.svg") #text(fill: color-accent)[Slides]]).
    ],
    [#text(weight: "bold", size: 8.8pt, fill: color-title)[2019]],
    [
      #strong[PyCon.FR (Bordeaux)] : Talk & démo #link("https://youtu.be/99uF4pfXmDI")[#icon("video.svg") #text(fill: color-accent)[Microservices gRPC/Python pour une application NLP d'analyse sémantique]] (#link("https://youtu.be/99uF4pfXmDI")[#text(fill: color-accent)[Vidéo]] • #link("https://docs.google.com/presentation/d/1taQVHdxZWcQIcI84e8H9y8GBPD8LHtt1ALGXvJZgVxo/edit?usp=sharing")[#icon("slides.svg") #text(fill: color-accent)[Slides]]).
    ],
    [#text(weight: "bold", size: 8.8pt, fill: color-title)[2019]],
    [
      #strong[ForCity] : Présentation technique interne sur l'architecture microservices gRPC appliquée aux SIG.
    ],
    [#text(weight: "bold", size: 8.8pt, fill: color-title)[2016]],
    [
      #strong[FOSS4G-fr] : Conférence #link("https://osgeo-fr.github.io/presentations_foss4gfr/2016/J2/Foss4g-li3ds.pdf")[#icon("slides.svg") #text(fill: color-accent)[Projet LI3DS - Acquisition et synchronisation 3D temps réel]].
    ],
    [#text(weight: "bold", size: 8.8pt, fill: color-title)[2011 - 2016]],
    [
      #strong[IGN / ENSG] : Formations supérieures #link("https://github.com/yoyonel/Python_ENSG_Geomatique")[#icon("github.svg") #text(fill: color-accent)[Python Géomatique]] (cours/TD/examens) et calcul scientifique sur GPU (OpenCL / CUDA).
    ]
  )
]

// --- LANGUES & DIVERS ---
#cv-section("Langues & Divers")

#block(width: 100%, below: 0pt)[
  #list(
    tight: true,
    marker: text(fill: color-accent, size: 7pt)[●],
    [#strong[Langues] : Anglais (technique courant, veille & documentation quotidienne), Allemand (notions scolaires).],
    [#strong[Pratiques Musicales] : Guitare-Basse (15 ans de pratique en groupe), Percussions Africaines (2 ans).],
    [#strong[Sports & Activités] : Volley-ball (15 ans en compétition régionale), Football.],
    [#strong[Centres d'intérêt] : Architecture logicielle, Moteurs 3D bas-niveau / Vulkan, Écosystème Open Source, Science-Fiction.]
  )
]