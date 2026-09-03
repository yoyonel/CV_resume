# CV_resume Development Guidelines

## 🚫 Golden Rules

1. **INTERDICTION ABSOLUE DE COMMIT OU PUSH SANS ACCORD ET DEMANDE EXPLICITE DU DÉVELOPPEUR** — Toujours présenter les modifications, diffs et résultats pour review. Attendre l'ordre explicite de commit de l'utilisateur (ex: "tu peux committer", "commit"). Ne JAMAIS exécuter `git commit` ou `git push` de sa propre initiative.
2. **INTERDICTION DE TRAVAILLER DIRECTEMENT SUR `master` OU `develop`** — Systématiquement créer une branche de travail dédiée (`fix/...`, `feat/...`) depuis `develop`. Toujours ouvrir une Pull Request vers `develop` avec prévisualisation Surge et validation CI complète avant fusion.
3. **Validation locale obligatoire (`task check`)** — Vérifier que Python (ruff), Jinja2 AST, compilation Typst et build du site statique passent sans erreur.
4. **Docs always in sync** — Mettre à jour ou créer la documentation dans `docs/` avec horodatage (`YYYY-MM-DD_...`).
5. **ADR obligatoire pour tout changement d'architecture** — Tout choix technique structurant (changement de framework/bibliothèque UI, refonte du pipeline de build, modification des formats de données pivots, ajout/suppression de dépendance majeure) DOIT obligatoirement faire l'objet d'un nouvel Architecture Decision Record via `task adr:new -- "Titre"` ou de l'amendement d'un ADR existant, avec mise à jour du registre [`docs/README.md`](docs/README.md) et vérification du visualiseur (`task adr:build` / `task adr:serve`).
6. **Zéro chemin absolu hôte (`$HOME` / `file:///home/...`) dans les fichiers** — INTERDICTION d'écrire des chemins locaux absolus (`/home/...`, `file:///home/...`, `/Users/...`) dans les fichiers versionnés du dépôt (documentation Markdown, code source, templates, scripts, configurations). Toujours utiliser des chemins relatifs au dépôt (`docs/README.md`, `scripts/...`).
7. **Caveman Mode** — Répondre en style ultra-compressé, technique, zéro superflu, avec liens de fichiers précis.

---

## 📝 Commit Discipline

- Un commit par sujet / intent clair (`feat`, `fix`, `perf`, `docs`, `ci`, `chore`, `style`).
- Format Conventional Commits strict.
- **Toujours attendre la validation et confirmation explicite de l'utilisateur avant d'exécuter `git commit` ou `git push`.**
