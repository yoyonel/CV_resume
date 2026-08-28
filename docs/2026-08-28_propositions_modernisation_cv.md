# Propositions de Modernisation du Rendu Graphique & Layout du CV
*Date : 28 Août 2026*

---

## 1. Diagnostic du Rendu Legacy (2013-2015)

1. **Charte couleur datée** : Vert olive (`#397249`), vert terne (`#9CB770`) et gris moyen (`#757575`). Rendu style "vieux blog 2010", manque de contraste et d'impact.
2. **Hiérarchie & Scannabilité** :
   - Layout 1 colonne monolithique.
   - Les listes d'outils/technologies forment des blocs de texte denses difficiles à scanner pour un recruteur / CTO en 10 secondes.
3. **Typographie & Header** :
   - Helvetica standard sans variations subtiles de graisses ni taille relative harmonisée.
   - En-tête centré brut sans hiérarchie moderne (nom / titre / badges).

---

## 2. Propositions d'Évolution

### Proposition 1 : Modern Tech Minimalist (Évolution ConTeXt / LaTeX)
Modernisation directe des styles ConTeXt (`style_chmduquesne.tex`) et CSS (`style_chmduquesne.css`) sans modifier l'architecture ni les outils de build.

#### Charte graphique
- **Texte principal** : Ardoise sombre / Noir d'encre (`#0F172A`).
- **Couleur primaire / Titres** : Bleu nuit / Indigo tech (`#1E40AF` ou `#2563EB`).
- **Couleur d'accent / Liens** : Bleu cyan / Azur (`#0284C7`).
- **Filets & séparateurs** : Gris clair épuré (`#CBD5E1`).
- **Métadonnées (dates, lieux)** : Gris ardoise (`#64748B`).

#### Améliorations de mise en page
- **En-tête épuré** : Nom fort, Titre de poste mis en avant (`Sénior Développeur Python / C++ / Architecture`), barre de contacts discrets et cliquables avec séparateurs subtils (`|` ou `•`).
- **Blocs d'expériences structurés** :
  - Ligne 1 : Date (à gauche) + **Titre de poste** (en gras) + *Entreprise / Lieu* (en couleur secondaire).
  - Ligne 2+ : Résumé d'impact + Ligne dédiée **Stack :** mise en valeur par texte semi-gras.
- **Section Technologies** : Regroupement en sous-blocs thématiques lisibles (Backend & Cloud / 3D & Graphisme / Méthodologies & CI/CD).

#### Avantages / Inconvénients
- **Avantages** :
  - **100% compatible** avec la chaîne Pandoc / ConTeXt et le Docker existant (0 nouvelle dépendance).
  - Gain immédiat de modernité, netteté et professionnalisme.
- **Inconvénients** :
  - Reste sur un flux vertical 1 colonne.

---

### Proposition 2 : Two-Column Modern / Sidebar Layout (Haute Densité)
Organisation en 2 colonnes asymétriques (1/3 gauche - 2/3 droite).

#### Structure
- **Colonne latérale (gauche - 30%)** :
  - Coordonnées & Liens (GitHub, LinkedIn, Email, Mobilité, Âge).
  - **Boîte à outils / Stack technique** catégorisée (Backend, Cloud/DevOps, 3D/Moteurs, BD/Stockage).
  - Formation & Diplômes.
  - Langues & Loisirs.
- **Colonne principale (droite - 70%)** :
  - Synthèse du profil / Accroche technique.
  - Expériences professionnelles détaillées (Unowhy, 365Talents, ForCity, Holimetrix, IGN, Eden Studios).
  - Conférences, Talks & Formations.

#### Avantages / Inconvénients
- **Avantages** :
  - **Scannabilité maximale** : les compétences techniques et coordonnées sont visibles en permanence sans scroller.
  - Format 2 pages calibré au millimètre, suppression des blancs perdus.
- **Inconvénients** :
  - Nécessite d'adapter le template ConTeXt (`\bTABLE` / colonnes) ou de générer via un template HTML/CSS Paged Media.

---

### Proposition 3 : Modernisation Typst / Weasyprint (Nouvelle Génération)
Migration du moteur de rendu PDF vers **Typst** ou **Pandoc + HTML/CSS paged** (Weasyprint / Playwright).

#### Caractéristiques
- Typographie moderne (Inter, JetBrains Mono pour les tags tech).
- Badges visuels arrondis pour les tags de technologies (`FastAPI`, `C++`, `Docker`, `Kubernetes`, `Vulkan`).
- Icônes vectorielles modernes (GitHub, LinkedIn, Email, Location).

#### Avantages / Inconvénients
- **Avantages** :
  - Flexibilité graphique totale (flexbox, grid, badges, icônes).
  - Vitesse de compilation ultra-rapide (Typst compile en < 50ms).
- **Inconvénients** :
  - Nécessite l'ajout du moteur dans le container Docker (`typst` ou `weasyprint`).

---

## 3. Tableau Comparatif Synthétique

| Critère | Legacy (2013) | Prop 1 : Modern Minimalist | Prop 2 : Two-Column Sidebar | Prop 3 : Typst / HTML-CSS |
|---|---|---|---|---|
| **Palette** | Vert olive / Gris moyen | Indigo / Cyan / Slate | Dark Slate / Accent Blue | Illimitée / Badges CSS |
| **Effort de mise en œuvre** | Existant | **Faible** (styles `.tex`/`.css`) | **Moyen** (template `.tex`) | **Élevé** (nouveau moteur) |
| **Compatibilité Docker actuel** | 100% | **100% (Immédiat)** | **100%** | Requiert update Docker |
| **Impact visuel recruteur** | 3/10 | **8/10** | **9/10** | **9.5/10** |
