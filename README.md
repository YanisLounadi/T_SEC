# T-SEC-902 — DFIR / Forensic Investigations

Projet d'investigation forensique Epitech. Trois scénarios indépendants, chacun rangé dans son
propre dossier sous `scenarios/`, avec ses artefacts et son analyse détaillée (`docs/`). Les
trois investigations sont consolidées dans un **rapport DFIR général unique** : [`report.pdf`](report.pdf).

## Scénarios

| # | Scénario | Source | Type | Statut |
|---|----------|--------|------|--------|
| 1 | [**Lockdown**](scenarios/01-lockdown/) — serveur IIS compromis (TechNova) | CyberDefenders #269 | PCAP + Memory + Malware | ✅ Fait |
| 2 | [**XWorm**](scenarios/02-xworm/) — RAT .NET | CyberDefenders #247 | Malware | ✅ Fait |
| 3 | [**Stonks**](scenarios/03-stonks/) — image disque AD1, fraude financière | HTB Sherlock | Disk forensics + Dedup | ✅ Fait |

## Organisation du repo

```
T-SEC-902/
├── README.md              # ce fichier (index)
├── report.pdf             # rapport DFIR général (livrable final)
├── project.pdf            # sujet du projet
└── scenarios/
    ├── 01-lockdown/
    │   ├── README.md      # synthèse du scénario + Q/A
    │   ├── docs/          # analyse détaillée par artefact
    │   └── artifacts/     # preuves (non versionnées — cf .gitignore)
    ├── 02-xworm/
    │   ├── README.md
    │   ├── docs/
    │   └── artifacts/
    └── 03-stonks/
        ├── README.md
        ├── docs/
        └── artifacts/
```

## Conventions

- **Un dossier par scénario** sous `scenarios/NN-nom/`.
- **Artefacts** dans `artifacts/` — fichiers lourds **non versionnés** (voir `.gitignore`).
  Les archives chiffrées d'origine et leurs mots de passe sont rappelés dans chaque `README.md`.
- **Analyse** dans `docs/`, un fichier Markdown par artefact / axe d'analyse.
- **Rapport final** : un rapport DFIR général unique à la racine, [`report.pdf`](report.pdf),
  qui consolide les trois investigations (executive summary, une partie par scénario,
  recommandations transverses, appendices).
