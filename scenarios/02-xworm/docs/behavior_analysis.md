# Analyse comportementale — XWorm.malware

**Outils utilisés** : ILSpy (`ilspycmd`), ProcMon / RegShot (équivalents dynamiques), analyse statique du flux .NET

---

## Persistance & privilèges

Le malware se copie dans `%AppData%\WmiPrvSE.exe` (usurpation du légitime *WMI Provider Host*)
puis installe **trois** mécanismes de persistance/exécution :

1. **Tâche planifiée** (priv-esc) — `schtasks /create /f /RL HIGHEST /sc minute /mo 1` toutes les
   minutes avec privilèges les plus élevés (voir Q4).
2. **Clé Run** — `HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Run\WmiPrvSE`.
3. **Raccourci Startup** — `WmiPrvSE.lnk` dans le dossier de démarrage (voir Q11).

---

## Q4 — Tâche planifiée (exécution privilégiée)

> What is the name of the scheduled task created by the malware to achieve execution with elevated privileges?

**Réponse : `WmiPrvSE`**

Le nom de la tâche est dérivé du binaire d'installation, sans extension :
`Path.GetFileNameWithoutExtension("WmiPrvSE.exe")` → `WmiPrvSE`.

```csharp
new ProcessStartInfo("schtasks.exe") {
  Arguments = "/create /f /RL HIGHEST /sc minute /mo 1 /tn \"" +
              Path.GetFileNameWithoutExtension(dropName) + "\" /tr \"" + targetPath + "\""
};
// dropName = "WmiPrvSE.exe"  ->  /tn "WmiPrvSE"
```

Le flag `/RL HIGHEST` force l'exécution avec les privilèges les plus élevés (T1053.005 +
contournement UAC), et `/sc minute /mo 1` relance le malware chaque minute.

---

## Q5 — Binaire déposé dans `%AppData%`

> What is the filename of the malware binary that is dropped in the AppData directory?

**Réponse : `WmiPrvSE.exe`**

Le champ de configuration déchiffré (dossier `%AppData%` + nom de fichier) donne le chemin
d'installation `%AppData%\WmiPrvSE.exe`. Ce nom imite un processus système Windows légitime.

---

## Évasion défensive

| Technique | Détail |
|-----------|--------|
| Exclusions Defender | `powershell -ExecutionPolicy Bypass Add-MpPreference -ExclusionPath/-ExclusionProcess` sur lui-même et le dossier d'install |
| Masquage | `ShowSuperHidden = 0` (voir Q13) |
| Auto-protection | `RtlSetProcessIsCritical` (voir Q14) |

---

## Q13 — Clé de registre d'affichage des éléments cachés

> What is the name of the registry key manipulated by the malware to control the visibility of hidden items in Windows Explorer?

**Réponse : `ShowSuperHidden`**

Sous `HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced`, le malware force
`ShowSuperHidden = 0` afin de masquer les fichiers système protégés (dont ses propres copies et
leurres sur les périphériques amovibles).

```csharp
registryKey = Registry.CurrentUser.OpenSubKey(
    "Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced", writable: true);
registryKey.SetValue("ShowSuperHidden", 0);
```

---

## Q14 — API marquant le processus comme critique

> Which API does the malware use to mark its process as critical in order to prevent termination or interference?

**Réponse : `RtlSetProcessIsCritical`**

Importée depuis `NTdll.dll`, cette API marque le processus comme **critique** : sa terminaison
provoque un BSOD (`CRITICAL_PROCESS_DIED`), dissuadant l'analyste et empêchant l'arrêt du malware.

```csharp
[DllImport("NTdll.dll", EntryPoint = "RtlSetProcessIsCritical", SetLastError = true)]
public static extern ...
```

---

## Propagation par périphériques amovibles

Le malware énumère les lecteurs (`DriveInfo.GetDrives()`), repère les volumes
`DriveType.Removable`, s'y copie sous le nom **`USB.exe`** et crée des **raccourcis `.lnk`** leurres
pointant vers `cmd.exe` (qui relance la charge) pour piéger l'utilisateur.

---

## Q10 — Nom de la copie sur périphériques amovibles

> The malware spreads by copying itself to every connected removable device. What is the name of the new copy created on each infected device?

**Réponse : `USB.exe`**

Champ de configuration déchiffré (`USB.exe`), utilisé comme nom de la copie déposée sur chaque
support amovible détecté.

---

## Q11 — Extension des fichiers créés pour l'exécution

> To ensure its execution, the malware creates specific types of files. What is the file extension of these created files?

**Réponse : `.lnk`**

Le malware crée des fichiers raccourcis **`.lnk`** :
- `WmiPrvSE.lnk` dans le dossier Startup (persistance) ;
- des `.lnk` leurres sur les périphériques amovibles, ciblant `cmd.exe` / `explorer` pour
  relancer la charge tout en masquant les fichiers d'origine.

```csharp
string lnk = Environment.GetFolderPath(Environment.SpecialFolder.Startup)
           + "\\" + Path.GetFileNameWithoutExtension(dropName) + ".lnk";
// ... CreateShortcut(...).TargetPath = ...
```

---

## Collecte & exfiltration

Le malware capture les frappes clavier via des hooks bas niveau et embarque un **clipper** crypto
(remplacement d'adresses BTC/ETH/TRC20 dans le presse-papiers). Les commandes du C2 incluent
notamment `Xchat`, `RunShell`, `StartDDos`, `PCShutdown`, gestion de plugins, etc.

---

## Q15 — API d'insertion de hooks clavier

> Which API does the malware use to insert keyboard hooks into running processes in order to monitor or capture user input?

**Réponse : `SetWindowsHookEx`**

Importée depuis `user32.dll`, `SetWindowsHookEx` installe un hook clavier (`WH_KEYBOARD_LL`)
permettant d'intercepter les frappes de tous les processus.

```csharp
[DllImport("user32.dll", CharSet = CharSet.Auto, EntryPoint = "SetWindowsHookEx", SetLastError = true)]
public static extern IntPtr SetWindowsHookEx(...);
```

Les APIs complémentaires confirment la chaîne de keylogging : `GetKeyboardState`,
`GetKeyboardLayout`, `ToUnicodeEx`, `MapVirtualKey`, `GetForegroundWindow`.

---

## Q16 — Fonctionnalité principale liée aux hooks clavier

> Given the malware's ability to insert keyboard hooks into running processes, what is its primary functionality or objective?

**Réponse : `Keylogger`**

L'usage de `SetWindowsHookEx` couplé au décodage des touches (`ToUnicodeEx`, normalisation des
touches spéciales `[ENTER]`, `[CTRL]`, `[SPACE]`…) et à l'enregistrement de la fenêtre active
caractérise un **keylogger** : capture des frappes pour dérober identifiants et données sensibles.
