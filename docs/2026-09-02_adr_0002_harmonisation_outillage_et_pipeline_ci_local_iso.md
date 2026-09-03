# ADR 0002 : Harmonisation de l'Outillage & Pipeline CI/Local ISO (Single Source of Truth)

## Status

Accepted

- **Date :** 2026-09-02
- **Auteurs :** Lionel ATTY & Antigravity Assistant
- **Décideurs :** Lionel ATTY
- **Contexte Technique :** Dépendances Python, Taskfile, Pre-commit hooks, GitHub Actions Workflows

---

## 1. Contexte & Problématique

Le projet s'appuyait sur trois déclarations distinctes et non synchronisées des commandes et dépendances d'outillage :
1. **`Taskfile.yml`** déclarait des flags ad-hoc verbeux (`uv run --with pyright --with typst --with jinja2 --with playwright --with adr-viewer pyright ...`).
2. **`.pre-commit-config.yaml`** dupliquait manuellement ces listes de packages.
3. **Les workflows GitHub Actions (`pr-preview.yml`, `deploy-pages.yml`, `build-pdf.yml`)** dupliquaient à leur tour des blocs de scripts bash avec des listes de packages hardcodées.

### Problème Identifié :
Lors de l'ajout d'un nouvel outil (ex: `adr-viewer`), l'environnement local (`task check`) passait avec succès, mais la CI échouait en raison d'un oubli de synchronisation manuelle dans `.github/workflows/pr-preview.yml`.

---

## 2. Alternatives Envisagées

### Option 1 : Maintien des flags `--with` inline et synchronisation manuelle
- **Avantages :** Zéro nouveau fichier de configuration.
- **Inconvénients :** Risque permanent de divergence (drift) entre local et CI, duplication de code, maintenance fastidieuse.

### Option 2 : Centralisation `pyproject.toml` + Exécution `Taskfile` universelle (Retenue)
- **Avantages :**
  - **Single Source of Truth** pour toutes les dépendances via standard `pyproject.toml` (`[dependency-groups] dev`).
  - Suppression de tous les flags `--with ...` dans le dépôt.
  - Exécution de `task check` directement en CI via `arduino/setup-task@v2`.
  - Isomorphisme strict : ce qui passe en local passera **obligatoirement à l'identique en CI**.
- **Inconvénients :** Nécessite l'installation de l'action `arduino/setup-task` dans les workflows.

---

## 3. Décision Retenue & Architecture

1. **Centralisation des Dépendances (`pyproject.toml`) :**
   - Déclaration de `jinja2`, `typst`, `playwright`, `adr-viewer` dans `dependencies`.
   - Déclaration de `ruff`, `pyright`, `pre-commit` dans `[dependency-groups] dev`.
   - Configuration centralisée de Ruff et Pyright dans `pyproject.toml`.

2. **`Taskfile.yml` comme Moteur d'Exécution Unique :**
   - Simplification de toutes les commandes en `uv run ruff`, `uv run pyright`, etc.
   - Les workflows CI appellent directement `task check` et `task test:bot`.

3. **Génération Automatique des ADRs :**
   - Intégration de `build_adr_docs()` directement dans `scripts/build_site.py` afin que `dist/adr/index.html` soit toujours généré et synchronisé à chaque build du site statique.

---

## 4. Conséquences & Bénéfices

- **Isomorphisme 100% garanti :** Aucune divergence possible entre l'environnement local du développeur, les hooks pre-commit et GitHub Actions.
- **Maintenance simplifiée :** Ajouter un outil ou modifier une version se fait en 1 seul endroit (`pyproject.toml`).
- **Workflows CI concis & lisibles :** Remplacement de dizaines de lignes bash dupliquées par un appel direct `task check`.

---

## 5. Validation

- [x] Résolution unifiée via `uv sync`
- [x] Linting Ruff et typage Pyright sans `--with` : 0 erreurs
- [x] Pre-commit hooks validés : `pre-commit run --all-files` PASS
- [x] Validation complète locale : `task check` PASS
- [x] CI GitHub Actions harmonisée
