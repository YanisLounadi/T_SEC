# Analyse statique — XWorm.malware

**Outils utilisés** : `file`, `pefile` (Python), `dnfile`, ILSpy (`ilspycmd`), Detect It Easy / CFF Explorer / PEStudio (équivalents OSINT)

---

## Informations générales

| Propriété | Valeur |
|-----------|--------|
| Nom | `XWorm.malware` |
| Type | PE32 executable (GUI) Intel 80386 Mono/.NET assembly, for MS Windows |
| Taille | 85 Ko (87 553 bytes) |
| SHA256 | `ced525930c76834184b4e194077c8c4e7342b3323544365b714943519a0f92af` |
| MD5 | `7c7aff561f11d16a6ec8a999a2b8cdad` |
| Assembly | `xWmDDA`, version `2.12.0.20` |
| Famille | XWorm (RAT .NET) |

L'échantillon est un assembly .NET non packé (pas d'UPX), mais fortement **obfusqué** : les noms de
types/méthodes/champs sont aléatoires. Les chaînes littérales restent toutefois en clair dans le tas
`#US`, et la configuration est chiffrée en AES (voir [config_extraction.md](config_extraction.md)).

```bash
file XWorm.malware
sha256sum XWorm.malware
# Décompilation complète en C# :
ilspycmd XWorm.malware > xworm_decompiled.cs
```

---

## Q1 — Timestamp de compilation (UTC)

> What is the compile timestamp (UTC) of the sample?

**Réponse : `2024-02-25 22:53`**

Le champ `TimeDateStamp` de l'en-tête PE (`IMAGE_FILE_HEADER`) vaut `0x65DBC4F4`, soit
`2024-02-25 22:53:40 UTC`.

```python
import pefile, datetime
pe = pefile.PE("XWorm.malware")
print(datetime.datetime.utcfromtimestamp(pe.FILE_HEADER.TimeDateStamp))
# 2024-02-25 22:53:40
```

---

## Q2 — Société légitime usurpée

> Which legitimate company does the malware impersonate in an attempt to appear trustworthy?

**Réponse : `Adobe`**

Les ressources de version du PE et les attributs d'assembly se font passer pour un produit Adobe
afin de paraître légitime auprès de l'utilisateur et des outils de tri.

| Champ | Valeur |
|-------|--------|
| `CompanyName` | `Adobe Inc.` |
| `FileDescription` / `ProductName` | `Adobe Installer` |
| `LegalCopyright` | `© 2015-2023 Adobe. All rights reserved.` |
| `OriginalFilename` | `xWmDDA.exe` |

```text
[assembly: AssemblyCompany("Adobe Inc.")]
[assembly: AssemblyProduct("Adobe Installer")]
[assembly: AssemblyTitle("Adobe Installer")]
[assembly: AssemblyCopyright("© 2015-2023 Adobe. All rights reserved.")]
```

---

## Q3 — Nombre de checks anti-analyse

> How many anti-analysis checks does the malware perform to detect/evade sandboxes and debugging environments?

**Réponse : `5`**

La méthode de garde anti-analyse évalue **5** conditions ; si l'**une** d'elles est vraie, le
malware appelle `Environment.FailFast(null)` et se termine immédiatement.

```csharp
if (CheckVM() || CheckDebugger() || CheckSandboxie() || CheckWindowsXP() || CheckHosting())
{
    Environment.FailFast(null);
}
```

| # | Check | Technique | Détail |
|---|-------|-----------|--------|
| 1 | Machine virtuelle | WMI `Win32_ComputerSystem` | `Manufacturer == "microsoft corporation"` & `Model` contient `VIRTUAL`, ou `vmware`, ou `VirtualBox` |
| 2 | Débogueur | `CheckRemoteDebuggerPresent` (kernel32) | Détection d'un debugger attaché |
| 3 | Sandbox | `GetModuleHandle("SbieDll.dll")` | Détection de **Sandboxie** (voir Q12) |
| 4 | Windows XP | `ComputerInfo.OSFullName` contient `xp` | Évite les anciens environnements d'analyse |
| 5 | Hébergement / cloud | `http://ip-api.com/line/?fields=hosting` | Réponse `true` ⇒ IP de datacenter (sandbox cloud) |

---

## Q12 — DLL de détection de sandbox

> What is the name of the DLL the malware uses to detect if it is running in a sandbox environment?

**Réponse : `SbieDll.dll`**

Le malware appelle `GetModuleHandle("SbieDll.dll")` : si le module est chargé dans son espace
d'adressage, c'est la signature de l'environnement **Sandboxie**, et l'exécution est avortée.

```csharp
result = (GetModuleHandle("SbieDll.dll").ToInt32() != 0);
```
