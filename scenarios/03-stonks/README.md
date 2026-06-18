# Scénario 3 — Stonks (HackTheBox Sherlock)

> **Statut : terminé** ✅ — 15/15 tâches résolues.

## Contexte

Une grande société immobilière (**Aurora Land Development Limited**) fait l'objet d'une enquête pour
fraude financière de grande ampleur : revenus gonflés et dettes dissimulées pour obtenir des prêts
bancaires et préparer une introduction en bourse. Un serveur d'entreprise (`FSERVER01`, Windows
Server 2019) a été saisi. Les enquêteurs soupçonnent que les **états financiers réels** (montrant les
pertes) ont été **supprimés** pour étouffer l'affaire. Mission : **récupérer le fichier manquant**.

Le volume `D:` utilise **Windows Data Deduplication** : les fichiers supprimés restent récupérables
tant que leurs **chunks** subsistent dans le ChunkStore.

| Artefact | Fichier | Description |
|----------|---------|-------------|
| Image disque | `artifacts/evidence.ad1` | Image logique FTK Imager (AD1, ~170 Mo) — 2 partitions (C: système, D: données dédupliquées) |

> Mot de passe de l'archive d'origine (`Stonks.zip`) : `hacktheblue`

## Démarche

1. **Extraction de l'AD1** — `pyad1` désynchronisait ; un extracteur C maison basé sur
   [`al3ks1s/AD1-tools`](https://github.com/al3ks1s/AD1-tools) (compilé sur macOS, mode `mkdir` corrigé
   en `0755`) a extrait 867 fichiers.
2. **Journaux & registre Dedup** (Tasks 1-6) — `python-evtx`, `regipy`, XML d'état.
3. **Analyse `$MFT`** (Tasks 7-10) — parseur maison : repérage du rapport supprimé + reparse-point.
4. **Reconstruction depuis le ChunkStore** (Tasks 11-13) — `tools/recover_dedup_file.py`.
5. **Analyse du contenu** (Tasks 14-15) — métadonnées + comparaison des états financiers.

## Résultats — 15 tâches

### Data Deduplication : config & journaux — [docs/dedup_config_and_logs.md](docs/dedup_config_and_logs.md)

| # | Question | Réponse |
|---|----------|---------|
| 1 | Première installation de la feature Dedup | `2025-09-18 09:56:40` |
| 2 | Octets économisés par le 1er job d'optimisation | `6805707` |
| 3 | Dernière ré-activation de Dedup sur D: | `2025-09-20 03:34:35` |
| 4 | Extensions non optimisées (alphabétique) | `avi, bak, edb, iso, jrs, mp4, tif` |
| 5 | Nombre de fichiers optimisés | `168` |
| 6 | Prochaine exécution du job Throughput Optimization | `2025-09-25 06:50:00` |

### Analyse $MFT — [docs/mft_analysis.md](docs/mft_analysis.md)

| # | Question | Réponse |
|---|----------|---------|
| 7 | Nom du rapport supprimé | `Internal Consolidated Financial Statements 2024.docx` |
| 8 | Numéro d'entrée MFT | `46` |
| 9 | Drapeaux FILE_ATTRIBUTE (ordre croissant) | `FILE_ATTRIBUTE_ARCHIVE, FILE_ATTRIBUTE_SPARSE_FILE, FILE_ATTRIBUTE_REPARSE_POINT` |
| 10 | Offset du $REPARSE_POINT dans $MFT | `0x0000b9b0` |

### Récupération ChunkStore — [docs/file_recovery.md](docs/file_recovery.md)

| # | Question | Réponse |
|---|----------|---------|
| 11 | Nombre de chunks | `2` |
| 12 | Longueur du 1er chunk (octets) | `61095` |
| 13 | SHA-256 du fichier récupéré | `e51e773e5404f29cc2816cff3fbdcc8b2c28f9e8040a6e7fe926b21336b66513` |

### La fraude — [docs/fraud_findings.md](docs/fraud_findings.md)

| # | Question | Réponse |
|---|----------|---------|
| 14 | Rédacteur du rapport | `Elaine Chua` |
| 15 | Surévaluation du profit de l'exercice ($'000) | `4319751` |

## Conclusion

Le rapport interne réel (rédigé par **Elaine Chua**, Senior Accountant) montrait une **perte** de
`1 647 555` ($'000) pour 2024 ; la version auditée publiée affichait un **bénéfice** de `2 672 196`,
soit une **surévaluation de 4 319 751**. Le fichier interne a été dédupliqué puis supprimé pour
masquer la perte — mais ses chunks, toujours présents dans le ChunkStore, ont permis sa
reconstruction intégrale.

## Reproductibilité

- `tools/recover_dedup_file.py` — reconstruit le fichier #46 depuis le ChunkStore (SHA-256 vérifié).
- Artefact reconstruit : `artifacts/Internal_Consolidated_Financial_Statements_2024.docx` (non versionné).

## Livrables

- [x] `docs/` — analyse détaillée (config/logs, MFT, récupération, fraude)
- [x] `tools/recover_dedup_file.py` — script de reconstruction
- [x] `report.pdf` — rapport DFIR
