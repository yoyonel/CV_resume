# 🚀 Système de Déploiement Éphémère PR & Checks Automatisés Surge.sh (2026-08-30)

## 1. Objectif

Permettre l'audit distant tiers (Google PageSpeed Insights, WebPageTest, appareils physiques) de chaque Pull Request **sans impacter la production** ni le serveur local de dev.

---

## 2. Architecture & Fonctionnement

Le workflow GitHub Actions [`.github/workflows/pr-preview.yml`](../.github/workflows/pr-preview.yml) s'exécute à chaque création ou mise à jour de Pull Request :

1. **Batterie Complète de Checks CI** :
   - Linter Python (`ruff`).
   - Typage Python (`pyright`).
   - Validation de l'AST Jinja2 (`parse()`).
   - Compilation Typst & génération du PDF ISO.
   - Build du site statique `dist/`.
   - Test Playwright Responsive (5 viewports sans débordement horizontal).
   - Test Playwright Guard Runtime (0 exception console / pageerror sur l'ensemble du cycle de vie).
   - Health check de tous les hyperliens (50 URLs).
2. **Déploiement Éphémère Surge.sh** :
   - Déploiement automatique sur `https://yoyonel-cv-resume-pr-<PR_NUMBER>.surge.sh`.
   - Utilisation des credentials GitHub Secrets (`SURGE_LOGIN` & `SURGE_TOKEN`).
3. **Commentaire Automatique Bot PR** :
   - Lien direct vers le site de preview éphémère.
   - Lien pré-généré pour lancer l'audit Google PageSpeed Insights distant.
   - Lien pré-généré pour lancer l'audit WebPageTest distant.
   - Résumé des 6 étapes de tests validées.
4. **Nettoyage Automatique (Teardown)** :
   - Destruction automatique du domaine Surge dès que la PR est fermée ou mergée.

---

## 3. Résultats Validés sur PR #6

- **Preview Live** : [https://yoyonel-cv-resume-pr-6.surge.sh](https://yoyonel-cv-resume-pr-6.surge.sh)
- **Desktop Performance** : **`100 / 100` 🟢** (FCP: 0.4s, LCP: 0.4s, TBT: 20ms)
- **Mobile Performance** : **`86 / 100` 🟢** (FCP: 1.9s, LCP: 2.1s, TBT: 390ms)
