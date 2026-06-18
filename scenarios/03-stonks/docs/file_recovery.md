# Récupération depuis le ChunkStore Dedup (Tasks 11-13)

**Outils** : `tools/recover_dedup_file.py` (parseur ChunkStore maison), `hashlib`.

Bien que le fichier #46 ait été supprimé, ses **chunks de données restent présents** dans le
ChunkStore de déduplication (la collecte des déchets ne les avait pas encore purgés). On reconstruit
le fichier en suivant la chaîne : `$REPARSE_POINT` → stream map → chunks de données.

## Structure du ChunkStore

`D:\System Volume Information\Dedup\ChunkStore\{6F89FF76-…}.ddp\`

| Dossier | Fichier | Rôle |
|---------|---------|------|
| `Stream\` | `00010000.00000001.ccc` | Conteneur des **stream maps** (liste des chunks par fichier) |
| `Data\` | `00000001.00000001.ccc` | Conteneur des **chunks de données** |

Format des conteneurs `.ccc` : en-tête `Cthr`, puis une suite d'objets. Chaque objet est précédé
d'un **en-tête `Ckhr` de 0x58 octets** (CHUNK HEADER) — **les données suivent l'en-tête**. Les
stream maps sont elles-mêmes stockées comme des chunks (`Smap` = liste des références de chunks,
suivie de son `Ckhr` d'identité dont le hash = celui du reparse-point).

> ⚠️ Piège : un `Smap` précède son `Ckhr` d'identité, mais le `Ckhr` est un **en-tête** — le stream
> map d'un fichier donné est donc le `Smap` situé **après** le `Ckhr` portant son hash, pas celui
> d'avant. (Confondre les deux reconstruit le fichier voisin.)

## Chaîne de récupération

1. Reparse-point (#46) → hash de stream map `f0973cbb…c867d19`.
2. Recherche du `Ckhr` correspondant dans le conteneur Stream (hash à +0x38 → en-tête à `0x5260`).
3. Stream map = le `Smap` suivant (`0x52c8`) ; ses entrées (64 octets) listent les chunks.
4. Pour chaque entrée → offset dans le conteneur Data → `Ckhr` (+0x58) → données du chunk.
5. Concaténation des chunks → fichier reconstruit.

```bash
python3 tools/recover_dedup_file.py /chemin/vers/volume_D 46 Internal_2024.docx
```

---

## Q11 — Nombre de chunks

> After the report was optimized, into how many chunks was its data divided?

**Réponse : `2`**

Le stream map du fichier (`Smap` @ `0x52c8`) contient **2 entrées** de chunk (séquences 7 et 8).

---

## Q12 — Longueur du premier chunk

> What is the data length in bytes of the first deduplicated chunk belonging to the report?

**Réponse : `61095`**

| Chunk | Offset (Data) | Longueur (octets) |
|-------|---------------|-------------------|
| **0 (1er)** | `0x6ce20` | **61095** |
| 1 | `0x7bd20` | 29498 |

Total = `61095 + 29498 = 90593` octets = la taille logique annoncée dans le reparse-point
(`0x161E1`), ce qui valide la reconstruction.

---

## Q13 — SHA-256 du rapport récupéré

> After recovering the file, provide the SHA-256 hash of the recovered financial report.

**Réponse : `e51e773e5404f29cc2816cff3fbdcc8b2c28f9e8040a6e7fe926b21336b66513`**

Le fichier reconstruit (90 593 octets) commence par `PK\x03\x04` : c'est un **DOCX (OOXML)** valide
(archive ZIP de 29 entrées, testée sans erreur). Son contenu révèle la fraude (cf.
[fraud_findings.md](fraud_findings.md)).

```
size   : 90593 bytes
type   : Microsoft OOXML (.docx / ZIP)
sha256 : e51e773e5404f29cc2816cff3fbdcc8b2c28f9e8040a6e7fe926b21336b66513
```
