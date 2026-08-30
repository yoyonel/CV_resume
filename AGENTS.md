# CV_resume Development Guidelines

## 🚫 Golden Rules

1. **INTERDICTION ABSOLUE DE COMMIT OU PUSH SANS ACCORD ET DEMANDE EXPLICITE DU DÉVELOPPEUR** — Toujours présenter les modifications, diffs et résultats pour review. Attendre l'ordre explicite de commit de l'utilisateur (ex: "tu peux committer", "commit"). Ne JAMAIS exécuter `git commit` ou `git push` de sa propre initiative.
2. **INTERDICTION DE TRAVAILLER DIRECTEMENT SUR `master` OU `develop`** — Systématiquement créer une branche de travail dédiée (`fix/...`, `feat/...`) depuis `develop`. Toujours ouvrir une Pull Request vers `develop` avec prévisualisation Surge et validation CI complète avant fusion.
3. **Validation locale obligatoire (`task check`)** — Vérifier que Python (ruff), Jinja2 AST, compilation Typst et build du site statique passent sans erreur.
4. **Docs always in sync** — Mettre à jour ou créer la documentation dans `docs/` avec horodatage (`YYYY-MM-DD_...`).
5. **Caveman Mode** — Répondre en style ultra-compressé, technique, zéro superflu, avec liens de fichiers précis.

---

## 📝 Commit Discipline

- Un commit par sujet / intent clair (`feat`, `fix`, `perf`, `docs`, `ci`, `chore`, `style`).
- Format Conventional Commits strict.
- **Toujours attendre la validation et confirmation explicite de l'utilisateur avant d'exécuter `git commit` ou `git push`.**
