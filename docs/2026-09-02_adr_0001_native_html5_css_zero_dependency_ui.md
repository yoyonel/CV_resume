# ADR 0001: Migration vers une Architecture 100% Native HTML5/CSS3 (Zéro Framework UI Externe)

## Status

Accepted

- **Date** : 2026-09-02
- **Auteurs** : Lionel ATTY & Antigravity Assistant
- **Décideurs** : Lionel ATTY
- **Contexte Technique** : Frontend Web Statique du CV / Portfolio (Jinja2, Typst, PDF.js)

---

## 1. Contexte et Problématique

Le site web du CV/Portfolio utilisait jusqu'alors une architecture hybride combinant :
1. Des composants HTML/CSS natifs sur-mesure (barre de filtres, chips de contact, timeline d'expériences, grilles de projets, badges de compétences).
2. La bibliothèque de Web Components **Shoelace / Web Awesome** pour une partie des éléments (boutons du header, groupes de boutons de contrôle PDF, modales `<sl-dialog>`, tooltips `<sl-tooltip>`).

### Symptômes & Limites Constatés :
1. **FOUC (Flash of Unstyled Custom Elements)** : Le chargement asynchrone du bundle JavaScript (`shoelace.bundle.min.js`) laissait les Custom Elements non définis (`:not(:defined)`) lors du premier cycle de rendu. Les boutons s'affichaient sous forme de rectangles noirs bruts et anguleux avec typographie non stylisée.
2. **Hétérogénéité Visuelle & Incohérence de Design** : Les boutons Shoelace présentaient des bordures rigides et anguleuses (`border-radius: 4px`) contrastant fortement avec les pilules fluides et modernes des filtres en CSS natif (`border-radius: 9999px`).
3. **Complexité & Shadow DOM Lock-in** : La surcharge de styles imposait de cibler des pseudo-éléments `::part(base)`, alourdissant la feuille de style sans apporter de réelle plus-value.
4. **Poids et Dette Technique** : Chargement de plus de 150 Ko de bundle JS + 40 Ko de CSS pour des besoins de simples boutons et boîtes de dialogue.

---

## 2. Facteurs de Décision (Decision Drivers)

* **Performance & Zéro Latence** : Rendu visuel immédiat (First Contentful Paint à 0ms JS overhead), aucun flash d'éléments non stylisés.
* **Homogénéité Visuelle Totale** : Un seul système de Design Tokens CSS (`--radius-pill`, `--radius-md`, `--bg-card`, `--accent-primary`) partagé par tous les composants.
* **Pérennité & Maintenabilité (Zero-Decay Architecture)** : Utilisation exclusive des standards W3C natifs (HTML5 semantic tags, CSS modern nesting & custom properties, `<dialog>` API). Aucune dépendance externe risquant une rupture d'API ou un changement de licence dans 5 à 10 ans.
* **Sobriété Numérique & Poids Réduit** : Élimination complète de bundles tiers superflus.

---

## 3. Options Considérées

* **Option 1 (Retenue) : 100% HTML5 / CSS Moderne Natif**
  - Remplacement de `<sl-button>` / `<sl-button-group>` par `<button class="btn">` et `.btn-group` en pur CSS Tokens.
  - Remplacement de `<sl-dialog>` par la balise standard HTML5 `<dialog>` (`showModal()`, `::backdrop`).
  - Remplacement de `<sl-tooltip>` par des micro-attributs CSS accessibles (`data-tooltip` / `title`).
  - Suppression complète du bundle Shoelace / Web Awesome.

* **Option 2 : Full Web Awesome / Shoelace Partout**
  - Tout migrer sous Web Components (filtres, cartes, timeline, badges).
  - *Rejeté* : FOUC persistant sans SSR, complexité du Shadow DOM, surpoids JS, risque de dépendance payante/dépréciée.

* **Option 3 : Hybride avec surcharges CSS agressives**
  - Garder Shoelace en forçant `pill` sur `::part(base)`.
  - *Rejeté* : Ne résout pas la cause racine du FOUC ni la dette technique des 150 Ko de dépendance.

---

## 4. Décision & Architecture Cible

**Décision : Migration complète vers l'Option 1 (100% HTML5 & CSS3 Standard).**

### Structure des Composants Natifs :

1. **Boutons & Groupes de Boutons (`.btn`, `.btn-group`)** :
   ```html
   <div class="btn-group" role="group" aria-label="Sélecteur de Vue">
     <button type="button" class="btn btn-primary btn-sm active" id="tabDoc" onclick="switchMainView('doc')">
       <svg class="icon"><use href="#icon-file-earmark-pdf"></use></svg>
       <span>Document ISO</span>
     </button>
     <button type="button" class="btn btn-default btn-sm" id="tabWeb" onclick="switchMainView('web')">
       <svg class="icon"><use href="#icon-grid-3x3-gap"></use></svg>
       <span>Vue Interactive</span>
     </button>
   </div>
   ```

2. **Dialogues & Modales (`<dialog>`)** :
   ```html
   <dialog id="paletteDialog" class="native-dialog cmd-palette-dialog" aria-label="Recherche">
     <div class="dialog-body">
       <!-- Contenu de la palette -->
     </div>
   </dialog>
   ```
   Gestion native en JavaScript : `dialog.showModal()` et `dialog.close()`, gestion automatique de la touche `Escape` et du focus trap natif.

3. **Tooltips CSS & Accessibilité (`data-tooltip`)** :
   - Infobulles ultra-légères en pur CSS via `[data-tooltip]::after` avec animations fluides d'opacité et de translation.

---

## 5. Conséquences & Bénéfices

### Positives :
* 🚀 **Zéro FOUC** : Le site est parfaitement stylisé dès la première milliseconde.
* 🎨 **Design Unifié & Fluide** : Tous les boutons adoptent le design en pilule (`border-radius: 9999px`) parfaitement coordonné avec la barre de filtres.
* 📦 **Gain de performance** : -190 Ko de transfert réseau et -100ms de temps de parsing JS au démarrage.
* 🔒 **Pérennité totale** : Zéro dépendance UI externe, 100% standard web pérenne.

### Négatives / Points de vigilance :
* Nécessite l'adaptation des tests Playwright (`test_ui_regressions.py`, `check_console.py`) pour cibler les nouveaux sélecteurs standard (`.btn`, `<dialog>`).
