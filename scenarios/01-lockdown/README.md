# TechNova Systems — Incident Response & Forensic Analysis

## Contexte

Le SOC de TechNova Systems a détecté du trafic sortant suspect depuis un serveur IIS exposé publiquement sur son infrastructure cloud. L'activité suggère un dépôt de web-shell suivi de connexions furtives vers un hôte inconnu.

Trois artefacts ont été collectés pour l'investigation :

| Artefact | Fichier | Description |
|----------|---------|-------------|
| Capture réseau | `artifacts/capture.pcapng` | Trafic réseau de l'intrusion initiale |
| Image mémoire | `artifacts/memdump.mem` | Dump mémoire complet du serveur (4.5 Go) |
| Échantillon malware | `artifacts/updatenow.exe` | Binaire malveillant récupéré sur le disque |

## Synthèse de l'attaque

```
10.0.2.4 (Attaquant)                         10.0.2.15 (Serveur IIS)
        |                                            |
        |── 1. Port scan (1002 ports) ──────────────>|
        |── 2. Enum SMB shares (T1046) ────────────->|
        |       \\10.0.2.15\IPC$                      |
        |       \\10.0.2.15\Documents                 |
        |── 3. Upload shell.aspx via SMB ───────────>|
        |<─ 4. Reverse shell callback :4443 ─────────|
        |── 5. Drop updatenow.exe (Agent Tesla) ────>|
        |       -> Startup folder (T1547.001)         |
        |<─ 6. C2 beacon -> cp8nl.hyperhost.ua ──────|
```

## Résultats par phase d'analyse

### 1. Analyse PCAP — [Détails](docs/pcap_analysis.md)

| Question | Réponse |
|----------|---------|
| IP source de la reconnaissance | `10.0.2.4` |
| Technique MITRE ATT&CK (énumération ciblée) | `T1046` — Network Service Discovery |
| UNC paths des Tree Connect SMB | `\\10.0.2.15\Documents, \\10.0.2.15\IPC$` |
| Fichier uploadé + taille SMB2 Write | `shell.aspx, 1015024` |
| Port du reverse shell | `4443` |

### 2. Analyse Memory Dump — [Détails](docs/memory_analysis.md)

| Question | Réponse |
|----------|---------|
| Kernel base address | `0xf80079213000` |
| Chemin de l'implant + technique de persistance | `C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup\updatenow.exe, T1547.001` |
| Processus gérant le reverse shell + PID | `w3wp.exe, 4332` |

### 3. Analyse Malware — [Détails](docs/malware_analysis.md)

| Question | Réponse |
|----------|---------|
| Packer utilisé | `UPX` |
| FQDN du C2 | `cp8nl.hyperhost.ua` |
| Famille de malware | `Agent Tesla` |
