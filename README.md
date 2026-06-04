# T-SEC-902 — DFIR / Forensic Investigations

Projet d'investigation forensique Epitech. Chaque scénario d'analyse d'artefacts est rangé dans
son propre dossier sous `scenarios/`, avec ses artefacts, son analyse détaillée (`docs/`) et son
rapport DFIR.

## Scénarios

| # | Scénario | Source | Type | Statut |
|---|----------|--------|------|--------|
| 1 | [**Lockdown**](scenarios/01-lockdown/) — serveur IIS compromis (TechNova) | CyberDefenders #269 | PCAP + Memory + Malware | ✅ Fait |
| 2 | [**XWorm**](scenarios/02-xworm/) — RAT .NET | CyberDefenders #247 | Malware | ✅ Fait |

## Organisation du repo

```
T-SEC-902/
├── README.md              # ce fichier (index)
├── report_template.md     # template DFIR partagé entre scénarios
├── project.pdf            # sujet du projet
└── scenarios/
    ├── 01-lockdown/
    │   ├── README.md      # synthèse du scénario
    │   ├── report.pdf     # rapport DFIR
    │   ├── docs/          # analyse détaillée par artefact
    │   └── artifacts/     # preuves (non versionnées — cf .gitignore)
    └── 02-xworm/
        ├── README.md
        ├── docs/
        └── artifacts/
```

## Conventions

- **Un dossier par scénario** sous `scenarios/NN-nom/`.
- **Artefacts** dans `artifacts/` — fichiers lourds **non versionnés** (voir `.gitignore`).
  Les archives chiffrées d'origine et leurs mots de passe sont rappelés dans chaque `README.md`.
- **Analyse** dans `docs/`, un fichier Markdown par artefact / axe d'analyse.
- **Rapport final** : `report.pdf`, basé sur `report_template.md`.
