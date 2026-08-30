# Optimisation Responsive Mobile & Visibilité de l'URL GitHub Pages

**Date** : 2026-08-30  
**Auteur** : Lionel ATTY  
**Projet** : `yoyonel/CV_resume`  
**URL de Production** : [https://yoyonel.github.io/CV_resume/](https://yoyonel.github.io/CV_resume/)

---

## 1. Problématique Initiale

Sur les navigateurs mobiles (ex: Brave Android, Chrome Mobile, Safari iOS), le site statique présentait un défaut d'alignement et d'échelle :
- **Débordement horizontal du Header** : Les boutons du header (`top-header`) et la barre de filtres (`filter-bar`) forçaient une largeur de document (`scrollWidth`) d'environ 934px sur un viewport de 390px.
- **Décalage visuel "Centré à gauche"** : La vue interactive (`#viewInteractive`), dimensionnée à 100% de la largeur du document artificiellement dilatée, affichait son contenu uniquement sur la moitié gauche de l'écran visible au zoom 100%, laissant un espace vide à droite.
- **Dimensionnement fixe PDF.js ISO** : Le rendu canvas PDF ciblait une largeur fixe de 840px, débordant également sur les écrans mobiles étroits.
- **Absence de l'URL sur le dépôt GitHub** : L'URL GitHub Pages du site n'était pas affichée sur le README ni sur la page principale du dépôt.

---

## 2. Solutions Techniques Implémentées

### A. Fluidité du Header & Breakpoints Réactifs (`top-header`)
- **Adaptation dynamique des boutons** :
  - Sur mobile (`<= 640px`), les labels textuels des boutons d'actions et de bascule de vue sont masqués au profit des icônes Shoelace (`file-earmark-pdf`, `grid-3x3-gap`, `search`, `download`), avec préservation des `sl-tooltip` et `aria-labels`.
  - Le badge `Ctrl K` et le bouton `Imprimer` (inutile sur mobile) sont automatiquement cachés.
  - Hauteur de navbar ajustée à 56px (`--header-height: 56px;`).

### B. Barre de Filtres Tactile (`filter-bar`)
- Remplacement du passage en colonne par un **défilement horizontal tactile fluide** (`overflow-x: auto; -webkit-overflow-scrolling: touch; scrollbar-width: none;`).
- Les chips de domaines et coordonnées de contact restent alignés et scrollables sans élargir la page.

### C. Centrage et Grilles CSS Responsive (`#viewInteractive`)
- Application de `min-width: 0; max-width: 100%;` sur l'ensemble des conteneurs (`.project-wrapper`, `.skill-wrapper`, `.wa-project-card`, `.wa-exp-card`).
- Grilles CSS adaptatives avec `grid-template-columns: minmax(0, 1fr)` sur mobile (`<= 640px`) et `repeat(auto-fit, minmax(min(100%, 280px), 1fr))` sur tablette/desktop.
- Ajustement du padding de la timeline (`timeline-container`) et centrage de la bannière Hero.

### D. Rendu ISO PDF Auto-Scalable (`#viewDocument`)
- Calcul adaptatif de `targetWidth` dans `renderDocPage()` :
  ```javascript
  const isMobile = window.innerWidth <= 860;
  const vDoc = document.getElementById('viewDocument');
  const maxAvail = vDoc ? Math.max(280, vDoc.clientWidth - 24) : (window.innerWidth - 32);
  const baseWidth = isMobile ? Math.min(840, maxAvail) : 840;
  const targetWidth = Math.round(baseWidth * docZoom);
  ```
- Ajout d'un écouteur `resize` avec debounce pour recalculer le rendu vectoriel lors des rotations d'écran (portrait / paysage).

### E. Visibilité de l'URL GitHub Pages dans le Répertoire
- Ajout de badges officiels et d'un bandeau d'accès direct en haut du `README.md` :
  - Lien : **[https://yoyonel.github.io/CV_resume/](https://yoyonel.github.io/CV_resume/)**
  - Section dédiée détaillant les fonctionnalités web et ISO.

---

## 3. Protocoles de Test Local de la Vue Mobile (100% Taskfile)

Toutes les étapes passent exclusivement par des tâches `Taskfile` dédiées :

### Option A : DevTools Navigateur (`task site:serve`)
1. Démarrer le serveur local de dev :
   ```bash
   task site:serve
   ```
2. Ouvrir le navigateur sur `http://localhost:8000/`.
3. Ouvrir les outils de développement (`F12` ou `Ctrl + Shift + I`).
4. Activer le mode Device Toolbar (`Ctrl + Shift + M`).
5. Tester les profils d'appareils et rotations : *iPhone 14 (390x844)*, *Pixel 7 (412x915)*, *Galaxy (360x740)*.

### Option B : Test Réel sur Smartphone via Wi-Fi Local (`task site:serve:lan`)
1. Lancer le serveur lié à `0.0.0.0` avec détection automatique de l'IP LAN :
   ```bash
   task site:serve:lan
   ```
2. La console affiche l'adresse réseau locale, par exemple :
   ```text
   ==========================================================
     🚀 PREVIEW SERVER READY:
     👉 Local: http://localhost:8000/
     📱 LAN (Smartphone Wi-Fi): http://192.168.1.45:8000/
   ==========================================================
   ```
3. Ouvrir l'URL LAN sur le smartphone connecté au même réseau Wi-Fi.

### Option C : Suite de Validation Automatisée Playwright (`task site:check:mobile`)
Validation headless multi-résolutions (360px, 390px, 412px, 768px, 1280px) vérifiant que `docScrollWidth <= docClientWidth` sur les deux vues (Interactive + Document ISO) :
```bash
task site:check:mobile
# ou
task check:mobile
```
Les captures d'écran de vérification sont archivées automatiquement dans `reports/mobile_previews/`.

Cette vérification est également intégrée dans la suite de contrôle globale :
```bash
task check
```
