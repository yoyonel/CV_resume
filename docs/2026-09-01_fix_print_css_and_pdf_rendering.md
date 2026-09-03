# 🖨️ Fix Rendu d'Impression (@media print) & Rendu 100% Vectoriel Zero-Aliasing (2026-09-01)

## 1. Contexte & Anomalies Détectées

Lors de l'impression (`window.print()` / Ctrl+P / Sauvegarde PDF depuis le navigateur), plusieurs problèmes existaient :
1. **Aliasing du `<canvas>` bitmap à fort zoom (400%+)** : PDF.js rend la prévisualisation écran dans un `<canvas>` HTML5 (bitmap raster). Lors de l'impression native du navigateur, ce canvas matriciel était imprimé, générant un crénelage (aliasing / flou) sur les lecteurs PDF haute résolution (ex: `atril`).
2. **Pollution UI** : Les barres de navigation (`header.top-header`), filtres (`.filter-bar`), contrôles PDF (`.doc-controls`), tags de pagination (`.page-tag`) et raccourcis étaient imprimés.
3. **Superposition du bandeau d'appel** : Le bandeau `.hero-card` ("Mode Portfolio Web & Démos interactives disponible") s'imprimait au bas de chaque page.

## 2. Filet de Sécurité & Tests Automatisés

- Création de [`scripts/test_print_rendering.py`](../scripts/test_print_rendering.py) validant avec Playwright :
  - **Rendu Document ISO 100% vectoriel** : Remplacement du canvas matriciel par les pages SVG vectorielles Typst (`assets/cv-page-1.svg`, `assets/cv-page-2.svg`) en mode `@media print`.
  - Export A4 (`reports/print_previews/document_iso_a4.pdf`) et US Letter (`reports/print_previews/document_iso_letter.pdf`) avec netteté infinie (zéro crénelage à 400%+).
  - Masquage strict de tous les éléments d'interface en `@media print`.
  - Vue par défaut au chargement : Document ISO en Double Page (`#viewDocument`, `#btnModeDual`).
- Intégration de la tâche `task check:print` dans [`Taskfile.yml`](../Taskfile.yml) et dans la suite globale `task check`.

## 3. Correctifs Appliqués

1. **Couche d'impression vectorielle Typst (`cv-page-1.svg` / `cv-page-2.svg`)** :
   - Écran (`@media screen`) : Affichage du canvas PDF.js + couche de sélection texte `.textLayer` (masquage de `.print-vector-page`).
   - Impression (`@media print`) : Masquage du `<canvas>` raster et affichage de `.print-vector-page` (SVG vectoriel pur compilé par Typst), garantissant un rendu vectoriel parfait à tout niveau de zoom sans aucun aliasing.
2. **Règles `@page { size: auto; margin: 0; }` & Reset universel** : Adaptation automatique à tous formats (A4, US Letter, Legal) avec préservation du ratio d'aspect vectoriel.
3. **Masquage UI complet** : Header, filtres, pagination, contrôles de zoom, modales et dialogues Shoelace masqués en `@media print`.
4. **Vue par défaut & Impression exclusive Document ISO** : Le site démarre sur le Document ISO Double Page, et toute impression (bouton, raccourci P, Ctrl+P) imprime les 2 pages Typst à la suite.
