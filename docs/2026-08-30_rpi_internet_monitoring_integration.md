# 📊 Intégration du Projet Perso `rpi-internet-monitoring` (2026-08-30)

## 1. Contexte & Présentation du Projet

Intégration du projet personnel open source [**rpi-internet-monitoring**](https://github.com/yoyonel/rpi-internet-monitoring) dans l'ensemble des formats du CV (Portfolio Web Interactif, CV Typst ISO, Pandoc Markdown).

- **Dépôt GitHub** : [https://github.com/yoyonel/rpi-internet-monitoring](https://github.com/yoyonel/rpi-internet-monitoring)
- **Site Live GitHub Pages** : [https://yoyonel.github.io/rpi-internet-monitoring/](https://yoyonel.github.io/rpi-internet-monitoring/)
- **Description** : Stack conteneurisée de métrologie et observabilité réseau (débit download/upload, ping, jitter, packet loss) et métriques système sur Raspberry Pi 4 (Docker Compose, InfluxDB / VictoriaMetrics, Telegraf, Speedtest CLI, Grafana, Systemd timers, publication automatique toutes les 10 min vers dashboard web Chart.js 100/100 Lighthouse).

---

## 2. Captures d'Écran & Galerie Multimédia

Captures haute résolution générées et intégrées dans `site_template/assets/projects/` :
- `rpi-monitoring-dashboard.png` : Tableau de bord web interactif & télémétrie débit/latence.
- `rpi-monitoring-mobile.png` : Vue responsive mobile.
- `rpi-monitoring-grafana.png` : Tableau de bord Grafana métriques et alertes système.

---

## 3. Fichiers Mis à Jour

- [`data/resume_data.json`](../data/resume_data.json) : Ajout du projet dans `projects_and_talks` avec galerie multimédia, tags et liens.
- [`typst_resume/resume.typ.j2`](../typst_resume/resume.typ.j2) : Ajout du projet dans la section *Projets R&D Personnels, Open Source & Conférences*.
- [`pandoc_resume/sections/04_conferences.md`](../pandoc_resume/sections/04_conferences.md) : Ajout des références dans le CV Markdown.
- [`site_template/index.html.j2`](../site_template/index.html.j2) : Support multi-domaines (`cloud`, `backend`), dictionnaire de synonymes enrichi (`rpi`, `speedtest`, `influxdb`, `grafana`, `victoriametrics`).
