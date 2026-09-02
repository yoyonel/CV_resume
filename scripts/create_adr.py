import argparse
from datetime import datetime, timezone
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Create a new ADR template in docs/")
    parser.add_argument("title", help="Title of the ADR (e.g. 'Migrate to Native UI')")
    parser.add_argument(
        "--status",
        choices=["Proposed", "Accepted", "Superseded", "Deprecated"],
        default="Proposed",
        help="Initial status (default: Proposed)",
    )
    args = parser.parse_args()

    root_dir = Path(__file__).resolve().parent.parent
    docs_dir = root_dir / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)

    # Find highest existing ADR number
    existing_adrs = list(docs_dir.glob("*_adr_*.md"))
    max_num = 0
    for f in existing_adrs:
        name = f.name
        parts = name.split("_adr_")
        if len(parts) == 2:
            try:
                num_str = parts[1].split("_")[0]
                num = int(num_str)
                max_num = max(max_num, num)
            except ValueError:
                pass

    next_num = max_num + 1
    num_str = f"{next_num:04d}"
    today_str = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")
    slug = (
        args.title.strip().lower().replace(" ", "_").replace("-", "_").replace("/", "_")
    )
    slug = "".join(c for c in slug if c.isalnum() or c == "_")

    filename = f"{today_str}_adr_{num_str}_{slug}.md"
    file_path = docs_dir / filename

    content = f"""# ADR {num_str} : {args.title}

## Status

{args.status}

- **Date :** {today_str}
- **Auteur :** Lionel ATTY
- **Décideurs :** Lionel ATTY

---

## 1. Contexte & Problématique

*Décrire le contexte technique, les motivations, contraintes et le problème à résoudre.*

---

## 2. Alternatives Envisagées

### Option 1 : [Nom de l'option 1]
- **Avantages :**
  - ...
- **Inconvénients :**
  - ...

### Option 2 : [Nom de l'option 2]
- **Avantages :**
  - ...
- **Inconvénients :**
  - ...

---

## 3. Décision Retenue & Rationale

*Expliquer pourquoi cette option a été sélectionnée face aux alternatives.*

---

## 4. Conséquences & Impacts

### Impacts Positifs :
- ...

### Compromis / Risques & Mitigations :
- ...

---

## 5. Validation & Métriques de Succès
- [ ] Validation `task check`
- [ ] Documentation synchronisée
"""

    file_path.write_text(content, encoding="utf-8")
    print(f"✓ Nouveau template ADR généré avec succès : {file_path}")
    print(f"  Fichier : docs/{filename}")


if __name__ == "__main__":
    main()
