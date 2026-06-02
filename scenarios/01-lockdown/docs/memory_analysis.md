# Analyse Memory Dump — memdump.mem

**Outil utilisé** : Volatility 3

---

## Q1 — Kernel base address

> Your memory snapshot captures the system's kernel in situ, providing vital context for the breach. What is the kernel base address in the dump?

**Réponse : `0xf80079213000`**

Informations système extraites :

| Propriété | Valeur |
|-----------|--------|
| OS | Windows Server 2019 (10.0.17763) |
| Architecture | x86_64 |
| Kernel Base | `0xf80079213000` |
| Date du dump | 2024-09-10 06:14:13 UTC |
| NtSystemRoot | `C:\Windows` |
| NtProductType | NtProductServer |

**Commande** :
```bash
vol -f memdump.mem windows.info
```

---

## Q2 — Implant de persistance

> A trusted service launches an unfamiliar executable residing outside the usual IIS stack, signalling a persistence implant. What is the final full on-disk path of that executable, and which MITRE ATT&CK persistence technique ID corresponds to this behaviour?

**Réponse : `C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup\updatenow.exe, T1547.001`**

Chaîne de processus observée :

```
services.exe (PID 628)
  └── svchost.exe (PID 2452, -k iissvcs)
        └── w3wp.exe (PID 4332, IIS Worker Process)
              └── updatenow.exe (PID 900) ← MALVEILLANT
                   Chemin : C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup\updatenow.exe
                   Wow64 : True (binaire 32-bit sur OS 64-bit)
                   Créé : 2024-09-10 06:08:23 UTC
```

Le binaire est placé dans le dossier **Startup** commun, ce qui correspond à la technique MITRE ATT&CK **T1547.001** (Boot or Logon Autostart Execution: Registry Run Keys / Startup Folder). Tout exécutable placé dans ce dossier est lancé automatiquement à chaque ouverture de session.

Un second processus suspect est aussi visible :
- `RegSvcs.exe` (PID 4200) lancé avec la ligne de commande pointant vers `C:\Users\admin\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\update.exe` — signe de process hollowing.

**Commande** :
```bash
vol -f memdump.mem windows.pstree
```

---

## Q3 — Processus du reverse shell

> The reverse shell's outbound traffic is handled by a built-in Windows process that also spawns the implanted executable. What is the name of this process, and what PID does it run under?

**Réponse : `w3wp.exe, 4332`**

La connexion réseau sortante vers l'attaquant est attribuée à `w3wp.exe` (IIS Worker Process) :

```
Source : 10.0.2.15:49688 → Destination : 10.0.2.4:4443
État : CLOSED
PID : 4332 (w3wp.exe)
Créé : 2024-09-10 05:49:51 UTC
```

Ce processus est le worker IIS qui a exécuté le web-shell `shell.aspx`. C'est lui qui :
1. Gère la connexion reverse shell vers le port 4443 de l'attaquant
2. Spawn le binaire malveillant `updatenow.exe` (PID 900) en tant que processus enfant

**Commande** :
```bash
vol -f memdump.mem windows.netscan
```
