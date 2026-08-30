# 🛠️ Fix du Rendu PDF.js en Modes Continu & Double Page (2026-08-30)

## 1. Contexte & Problème

En affichage Document (ISO PDF Typst), lors du basculement vers les modes **Continu** (`setDocMode('continuous')`), **Double Page** (`setDocMode('dual')`), ou lors du changement de page en mode unique (`toggleDocSingle()`), la page 2 n'était pas affichée (canvas noir/vide).

## 2. Cause Racine

Dans le commit `a35c1f8`, la ligne `if (container && getComputedStyle(container).display === 'none') return;` a été introduite dans `renderDocPage()`. Au chargement initial (où la page 2 est masquée par défaut), son rendu était annulé. Les fonctions de changement de mode et de pagination mettaient à jour les classes CSS sans réinvoquer `renderDocPages()`, laissant le canvas de la page 2 vierge.

## 3. Solution & Verrouillage

1. Invocations automatiques de `renderDocPages()` dans `setDocMode()` et `updateDocSingle()` ([`site_template/index.html.j2`](../site_template/index.html.j2)).
2. Assertion stricte Playwright dans [`scripts/check_console.py`](../scripts/check_console.py) vérifiant que `canvasPage1.height > 100` et `canvasPage2.height > 100` en modes continu, double page et pagination.
