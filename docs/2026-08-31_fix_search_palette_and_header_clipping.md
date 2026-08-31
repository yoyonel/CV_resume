# 🛠️ Fix Palette de Recherche & Alignement Header (2026-08-31)

## 1. Contexte & Anomalies Détectées

1. **Badge `Ctrl K` mal positionné** : Le badge flottait au-dessus du bouton de recherche dans le header au lieu d'être centré à l'intérieur.
2. **Champ de recherche invisible / inactif dans la palette** : `<sl-input>` n'était pas inclus dans le bundle Shoelace personnalisé, devenant un `HTMLUnknownElement` non stylisé et sans champ de saisie réel.
3. **Clipping des tooltips & textes de contact** : Les tooltips sans attribut `hoist` dans `.filter-bar` (`overflow-x: auto`) étaient rognés au bord supérieur.

## 2. Filet de Sécurité & Reproduction

Création de la suite de tests automatisée [`scripts/test_ui_regressions.py`](../scripts/test_ui_regressions.py) intégrée à `task check` et à la CI GitHub Actions.

## 3. Correctifs Appliqués

1. Remplacement de `<sl-badge>` par `<kbd class="search-shortcut-kbd">Ctrl K</kbd>` centré en inline-flex.
2. Remplacement de `<sl-input>` par un champ HTML5 réactif `<input type="text" class="palette-search-input">` avec focus automatique et filtrage dynamique.
3. Ajout de `hoist` sur tous les `<sl-tooltip>` de la barre de filtres et ajustement de hauteur/line-height des pastilles de contact.
