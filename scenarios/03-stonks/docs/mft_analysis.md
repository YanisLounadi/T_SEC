# Analyse $MFT — le rapport supprimé (Tasks 7-10)

**Outils** : parseur `$MFT` Python maison (cf. raisonnement ci-dessous), extraction AD1.

Le `$MFT` du volume `D:` (`D:\$MFT`, 512 Ko = 512 enregistrements de 1024 octets) a été extrait de
l'image AD1. Tous les fichiers utilisateur du volume sont **optimisés par déduplication** : leur
enregistrement MFT porte un attribut `$REPARSE_POINT` avec le tag `0x80000013`
(`IO_REPARSE_TAG_DEDUP`) et un `$DATA` non-résident sparse (taille logique conservée, données dans le
ChunkStore).

---

## Q7 — Nom du rapport financier récemment supprimé

> What is the name of the financial report that was recently deleted to cover up criminal activity?

**Réponse : `Internal Consolidated Financial Statements 2024.docx`**

En parcourant le `$MFT`, **un seul** enregistrement de rapport financier est marqué **supprimé**
(flag « in-use » à 0) tout en portant un reparse-point Dedup :

| MFT # | État | Chemin |
|-------|------|--------|
| 44 | actif | `Finance\Reports\Annual\2024\Audited Consolidated Financial Statements 2024.docx` |
| 45 | actif | `Finance\Reports\Annual\2024\Audited Consolidated Financial Statements 2024.pdf` |
| **46** | **SUPPRIMÉ** | `Finance\Reports\Annual\2024\Internal Consolidated Financial Statements 2024.docx` |

La version « **Internal** » (chiffres réels) a été supprimée, tandis que la version « Audited »
(chiffres gonflés) a été conservée — cf. [fraud_findings.md](fraud_findings.md).

---

## Q8 — Numéro d'entrée MFT du rapport

> What is the MFT entry number of that report file?

**Réponse : `46`**

L'enregistrement débute à l'offset `46 × 1024 = 0xB800` dans `$MFT`, signature `FILE`, flags `0x0`
(supprimé, fichier).

---

## Q9 — Drapeaux FILE_ATTRIBUTE positionnés

> List all the FILE_ATTRIBUTE flags set on the report file, in ascending order of each flag's hex value.

**Réponse : `FILE_ATTRIBUTE_ARCHIVE, FILE_ATTRIBUTE_SPARSE_FILE, FILE_ATTRIBUTE_REPARSE_POINT`**

Lus dans l'attribut `$STANDARD_INFORMATION` de l'enregistrement #46 : champ flags = `0x620`.

| Valeur hex | Constante |
|------------|-----------|
| `0x20` | FILE_ATTRIBUTE_ARCHIVE |
| `0x200` | FILE_ATTRIBUTE_SPARSE_FILE |
| `0x400` | FILE_ATTRIBUTE_REPARSE_POINT |

`0x20 | 0x200 | 0x400 = 0x620`. `SPARSE_FILE` + `REPARSE_POINT` sont la signature d'un fichier
optimisé par déduplication.

---

## Q10 — Offset du $REPARSE_POINT dans $MFT

> At what offset in the $MFT file does the $REPARSE_POINT attribute of the report begin?
> (8-digit hexadecimal, prefixed with 0x)

**Réponse : `0x0000b9b0`**

Disposition des attributs de l'enregistrement #46 (base `0xB800`) :

| Attribut | Offset dans l'enreg. | Offset dans `$MFT` |
|----------|----------------------|--------------------|
| `$STANDARD_INFORMATION` (0x10) | 56 | 0x0000b838 |
| `$FILE_NAME` (0x30) | 152 | 0x0000b898 |
| `$DATA` (0x80, non-résident) | 352 | 0x0000b960 |
| **`$REPARSE_POINT` (0xC0)** | **432** | **`0x0000b9b0`** |

`0xB800 + 432 = 0xB9B0`. Le buffer reparse (résident, 124 octets) contient le GUID du ChunkStore
`{6F89FF76-AE45-4802-BD0E-4075177C075F}`, la taille logique (`0x161E1 = 90593` octets) et le **hash
du stream map** (`f0973cbb…c867d19`) — utilisé pour la récupération (cf.
[file_recovery.md](file_recovery.md)).
