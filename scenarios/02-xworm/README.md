# Scénario 2 — XWorm (CyberDefenders #247)

> **Statut : terminé** ✅ — 16/16 questions résolues.

## Contexte

Un employé a téléchargé par erreur un fichier joint à un e-mail de phishing. Le fichier s'est
exécuté silencieusement et a déclenché un comportement système anormal. En tant qu'analyste
malware, l'objectif est de disséquer l'échantillon pour mettre en évidence son comportement, ses
mécanismes de persistance, sa communication avec le C2 et ses capacités d'exfiltration.

L'échantillon est un **RAT XWorm** (.NET, famille de remote access trojan dérivée de la lignée
NjRAT/Quasar), se faisant passer pour un installeur **Adobe**.

| Artefact | Fichier | Description |
|----------|---------|-------------|
| Échantillon malware | `artifacts/XWorm.malware` | PE32 .NET, 85 Ko, XWorm RAT |

> Mot de passe de l'archive d'origine (`247-XWorm.zip`) : `cyberdefenders.org`

## Identification

| Propriété | Valeur |
|-----------|--------|
| SHA256 | `ced525930c76834184b4e194077c8c4e7342b3323544365b714943519a0f92af` |
| MD5 | `7c7aff561f11d16a6ec8a999a2b8cdad` |
| Type | PE32 (GUI) Intel 80386 Mono/.NET assembly, for MS Windows |
| Assembly | `xWmDDA`, version `2.12.0.20` |
| Métadonnées usurpées | « Adobe Inc. » / « Adobe Installer » |
| Compilation (UTC) | `2024-02-25 22:53:40` |

## Synthèse comportementale

```
                         XWorm.malware ("Adobe Installer")
                                     |
   ┌─────────────────────────────────┼─────────────────────────────────┐
   |               |                  |                |                 |
 ANTI-ANALYSE   PERSISTANCE        PRIV-ESC         ÉVASION          COLLECTE / C2
   |               |                  |                |                 |
 5 checks :     • copie dans       schtasks         • RtlSetProcess   • Keylogger
 • WMI VM         %AppData%\         /create /RL      IsCritical         (SetWindowsHookEx)
 • Debugger       WmiPrvSE.exe       HIGHEST /tn      (process          • Clipper crypto
 • SbieDll.dll   • .lnk dans le     "WmiPrvSE"        non-killable)      (BTC/ETH/TRC20)
 • OS == XP        dossier Startup  /sc minute       • ShowSuperHidden  • AES config →
 • ip-api        • clé Run                             = 0 (cache)        C2 TCP :7000
   "hosting"     • spread USB                        • exclusions         185.117.250.169
   → FailFast      → USB.exe +                         Defender           66.175.239.149
                   .lnk leurres                                           185.117.249.43
```

## Résultats — 16 questions

> Détails et commandes dans les documents liés ci-dessous.

### Identification & anti-analyse — [docs/static_analysis.md](docs/static_analysis.md)

| # | Question | Réponse |
|---|----------|---------|
| Q1 | Timestamp de compilation (UTC) | `2024-02-25 22:53` |
| Q2 | Société légitime usurpée | `Adobe` |
| Q3 | Nombre de checks anti-analyse | `5` |
| Q12 | DLL utilisée pour détecter une sandbox | `SbieDll.dll` |

### Configuration & C2 — [docs/config_extraction.md](docs/config_extraction.md)

| # | Question | Réponse |
|---|----------|---------|
| Q6 | Algorithme cryptographique de la config | `AES` |
| Q7 | Chaîne codée en dur dérivant clé + IV | `8xTJ0EKPuiQsJVaT` |
| Q8 | Adresses IP du C2 (déchiffrées) | `185.117.250.169, 66.175.239.149, 185.117.249.43` |
| Q9 | Port de communication C2 | `7000` |

### Comportement, persistance & collecte — [docs/behavior_analysis.md](docs/behavior_analysis.md)

| # | Question | Réponse |
|---|----------|---------|
| Q4 | Nom de la tâche planifiée (priv-esc) | `WmiPrvSE` |
| Q5 | Binaire déposé dans `%AppData%` | `WmiPrvSE.exe` |
| Q10 | Nom de la copie sur les périphériques amovibles | `USB.exe` |
| Q11 | Extension des fichiers créés pour l'exécution | `.lnk` |
| Q13 | Clé de registre contrôlant l'affichage des éléments cachés | `ShowSuperHidden` |
| Q14 | API marquant le processus comme critique | `RtlSetProcessIsCritical` |
| Q15 | API insérant des hooks clavier | `SetWindowsHookEx` |
| Q16 | Fonctionnalité principale liée aux hooks clavier | `Keylogger` |

## Indicateurs de compromission (IOC)

| Type | Valeur |
|------|--------|
| SHA256 | `ced525930c76834184b4e194077c8c4e7342b3323544365b714943519a0f92af` |
| MD5 | `7c7aff561f11d16a6ec8a999a2b8cdad` |
| C2 | `185.117.250.169:7000`, `66.175.239.149:7000`, `185.117.249.43:7000` |
| Mutex / splitter | `<Xwormmm>` |
| Fichier (install) | `%AppData%\WmiPrvSE.exe` |
| Persistance | Startup `WmiPrvSE.lnk`, clé `HKCU\...\CurrentVersion\Run\WmiPrvSE`, tâche `WmiPrvSE` |
| Spread USB | `USB.exe` + leurres `*.lnk` (cible `cmd.exe`) |
| Clipper BTC | `bc1q2a4jgxmvslng5khwvzkt9pechms20ghff42s5g` |
| Clipper ETH | `0x10cE3E5678f40f0B94A2fB5003f04012ecA407C5` |

## Livrables

- [x] `docs/` — analyse détaillée (statique, config, comportement)
- [x] `report.pdf` — rapport DFIR (cf. `../../report_template.md`)
