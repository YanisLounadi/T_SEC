# Analyse PCAP — capture.pcapng

**Outil utilisé** : tshark (Wireshark CLI)

---

## Q1 — IP source de la reconnaissance

> After flooding the IIS host with rapid-fire probes, the attacker reveals their origin. Which IP address generated this reconnaissance traffic?

**Réponse : `10.0.2.4`**

L'attaquant a envoyé des paquets SYN vers **1 002 ports distincts** sur la cible `10.0.2.15`, caractéristique d'un scan de ports. Cette IP représente la majorité du trafic capturé (6 007 frames dans la conversation avec la victime).

**Commande** :
```bash
tshark -r capture.pcapng -z conv,tcp -q
```

---

## Q2 — Technique MITRE ATT&CK de l'énumération ciblée

> Zeroing in on a single open service to gain a foothold, the attacker carries out targeted enumeration. Which MITRE ATT&CK technique ID covers this activity?

**Réponse : `T1046` — Network Service Discovery**

Après le scan de ports, l'attaquant a ciblé le service SMB (port 445). Il s'est connecté au partage `IPC$` et a exécuté un appel DCERPC `NetShareEnumAll` (opnum 15 sur srvsvc) pour lister les partages réseau disponibles.

**Commande** :
```bash
tshark -r capture.pcapng -Y "dcerpc.opnum == 15" -T fields -e ip.src -e ip.dst
```

---

## Q3 — UNC paths des Tree Connect SMB

> While reviewing the SMB traffic, you observe two consecutive Tree Connect requests that expose the first shares the intruder probes on the IIS host. Which two full UNC paths are accessed?

**Réponse : `\\10.0.2.15\Documents, \\10.0.2.15\IPC$`**

Deux requêtes SMB2 Tree Connect consécutives :
- Frame 2672 : `\\10.0.2.15\IPC$` (utilisé pour l'énumération via srvsvc)
- Frame 2678 : `\\10.0.2.15\Documents` (partage découvert, ciblé pour l'upload)

**Commande** :
```bash
tshark -r capture.pcapng -Y "smb2.cmd == 3 && smb2.flags.response == 0" -T fields -e frame.number -e smb2.tree
```

---

## Q4 — Fichier malveillant uploadé

> Inside the share, the attacker plants a web-accessible payload that will grant remote code execution. What is the filename of the malicious file they uploaded, and what byte length is specified in the corresponding SMB2 Write Request?

**Réponse : `shell.aspx, 1015024`**

L'attaquant a uploadé un web-shell ASP.NET dans le partage Documents (probablement mappé au webroot IIS). Le fichier a été écrit via une requête SMB2 Write.

**Commande** :
```bash
tshark -r capture.pcapng -Y "smb2.cmd == 9" -T fields -e frame.number -e smb2.filename -e smb2.write_length
```

---

## Q5 — Port du reverse shell

> The newly planted shell calls back to the attacker over an uncommon but firewall-friendly port. Which listening port did the attacker use for the reverse shell?

**Réponse : `4443`**

Après l'upload du web-shell (frame 3505), la victime `10.0.2.15` a initié une connexion TCP sortante depuis le port 49688 vers l'attaquant `10.0.2.4` sur le port **4443** (frame 3585). Ce port imite le HTTPS (443) pour contourner les pare-feux.

**Commande** :
```bash
tshark -r capture.pcapng -Y "tcp.flags.syn == 1 && tcp.flags.ack == 0 && ip.src == 10.0.2.15 && ip.dst == 10.0.2.4"
```
