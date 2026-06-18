# La fraude révélée (Tasks 14-15)

**Outils** : extraction OOXML (`zipfile`), lecture `docProps/core.xml`, comparaison des états
financiers (rapport réel récupéré vs rapport « Audited » conservé).

L'entreprise est **Aurora Land Development Limited** (Singapour). Deux versions du rapport annuel
2024 coexistaient dans `Finance\Reports\Annual\2024\` :

- **Audited Consolidated Financial Statements 2024** (.docx/.pdf) — version publiée, **bénéfice gonflé** (conservée).
- **Internal Consolidated Financial Statements 2024.docx** — version interne, **chiffres réels** (supprimée puis récupérée).

---

## Q14 — Rédacteur du rapport

> The person who drafted this report must also be held legally accountable. What is their full name?

**Réponse : `Elaine Chua`**

Métadonnées du DOCX récupéré (`docProps/core.xml`) :

```xml
<dc:creator>Elaine Chua - Senior Accountant</dc:creator>
<cp:lastModifiedBy>Elaine Chua - Senior Accountant</cp:lastModifiedBy>
<dcterms:created>2025-09-16T15:59:00Z</dcterms:created>
```

Le rapport interne (chiffres réels) a été rédigé par **Elaine Chua**, *Senior Accountant*.

---

## Q15 — Surévaluation du « profit for the year »

> How much was the profit for the year overstated in the audited report compared to the actual one?

**Réponse : `4319751`** (en milliers, `$'000`)

Comparaison de la ligne *Profit for the year* (exercice 2024) :

| Rapport | Profit for the year 2024 ($'000) |
|---------|----------------------------------|
| **Audited** (publié, gonflé) | `2 672 196` |
| **Internal** (réel, récupéré) | `−1 647 555` *(perte)* |

Surévaluation = `2 672 196 − (−1 647 555)` = **`4 319 751`**.

Le rapport réel montre une **perte** (`Operating profit −1 269 933`, `Profit before taxation
−1 432 882`, `Profit for the year −1 647 555`), alors que la version auditée affiche un **bénéfice**
de `2 672 196` — une inversion destinée à séduire banques et marché boursier. La suppression du
rapport interne (déduplication + delete) visait à effacer la preuve de la perte réelle.
