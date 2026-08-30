# ⚡ Optimisation Mobile : Vendoring Local Shoelace & Sprites SVG Natifs (2026-08-30)

## 1. Diagnostic des Goulots d'Étranglement Mobile

Sur profil mobile émulé (CPU bridé 4x et réseau 4G simulé), deux goulots d'étranglement majeurs pénalisaient le Total Blocking Time (TBT) et le Largest Contentful Paint (LCP) :

1. **Waterfalls de sous-modules CDN distants** :
   - Les imports ES Modules depuis `cdn.jsdelivr.net` déclenchaient une cascade de 20+ micro-requêtes asynchrones pour charger les sous-dépendances LitElement et Shoelace.
2. **Cycle de vie lourd de `<sl-icon>`** :
   - Chaque balise `<sl-icon name="...">` déclenchait au runtime un appel `fetch()` vers le fichier SVG, suivi d'un `DOMParser().parseFromString()` et d'une injection dans le Shadow DOM. Avec 20+ icônes sur la page, cela générait ~600 ms de surcharge CPU bloquante.
3. **Ordre DOM et Polices** :
   - L'absence de préchargement de la police `Inter` et le positionnement de la vue interactive après la vue PDF dans le DOM retardaient le LCP initial.

---

## 2. Solutions Techniques Implémentées

### A. Bundling & Vendoring Local Autonome
- Création d'un bundle standalone minifié via `esbuild` : [`site_template/assets/vendor/shoelace/shoelace.bundle.min.js`](../site_template/assets/vendor/shoelace/shoelace.bundle.min.js) (122 Ko).
- 0 requête externe vers des CDNs tiers.
- Chargement asynchrone non-bloquant en fin de `<body>`.

### B. Sprites SVG Vectoriels Natifs
- Intégration d'un sprite SVG unique contenant les 18 symboles vectoriels utilisés :
  ```html
  <svg class="icon"><use href="#icon-github"></use></svg>
  ```
- **0 appel `fetch()` au runtime**, 0 `DOMParser()`, rendu vectoriel instantané par le moteur de rendu C++ du navigateur.

### C. Optimisation Typographie & DOM
- Préchargement de la police principale :
  ```html
  <link rel="preload" href="assets/fonts/font_3.woff2" as="font" type="font/woff2" crossorigin />
  ```
- Nettoyage du fichier [`fonts.css`](../site_template/assets/fonts/fonts.css) pour ne conserver que les subsets Latin / Latin-ext nécessaires.
- Inversion de l'ordre dans le balisage HTML : `<main id="viewInteractive">` est désormais parsé et rendu en premier.

---

## 3. Résultats des Benchmarks sur Tunnel Public Staging

| Métrique | 💻 **Desktop (Tunnel)** | 📱 **Mobile (Tunnel)** |
| :--- | :---: | :---: |
| ⚡ **Performance** | **`100 / 100` 🟢** | **`86 / 100` 🟢** |
| ♿ **Accessibilité** | **`96 / 100` 🟢** | **`96 / 100` 🟢** |
| 🛡️ **Bonnes Pratiques** | **`96 / 100` 🟢** | **`96 / 100` 🟢** |
| 🔍 **SEO** | **`100 / 100` 🟢** | **`100 / 100` 🟢** |
| **First Contentful Paint (FCP)** | **`0.4 s` 🟢** | **`1.6 s` 🟢** |
| **Largest Contentful Paint (LCP)** | **`0.4 s` 🟢** | **`1.6 s` 🟢** |
| **Speed Index** | **`0.5 s` 🟢** | **`1.7 s` 🟢** |
| **Cumulative Layout Shift (CLS)** | **`0.015` 🟢** | **`0.003` 🟢** |
