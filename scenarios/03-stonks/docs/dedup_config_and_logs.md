# Data Deduplication — configuration & journaux (Tasks 1-6)

**Outils** : `python-evtx` (parsing EVTX), `regipy` (registre), lecture des XML d'état Dedup.

Le serveur compromis est `FSERVER01` (Windows Server 2019, fuseau **SE Asia Standard Time, UTC+7**).
Le volume de données `D:` (`Data`, NTFS, 512 Mo dans l'image) est protégé par **Windows Data
Deduplication**. Tous les artefacts Dedup proviennent de :

- Journaux : `C:\Windows\System32\winevt\logs\Microsoft-Windows-Deduplication%4{Operational,Diagnostic}.evtx`, `System.evtx`, `Setup.evtx`
- État/config : `D:\System Volume Information\Dedup\{Settings,State}\*.xml`
- Tâches : `C:\Windows\System32\Tasks\Microsoft\Windows\Deduplication\*`

---

## Q1 — Première installation de la feature Data Deduplication

> When was the Windows Data Deduplication feature first installed on the system?

**Réponse : `2025-09-18 09:56:40`**

L'installation de la feature se matérialise par l'enregistrement du **service** par le Service
Control Manager (`System.evtx`, EventID **7045**) :

| Heure (UTC) | EID | Service |
|-------------|-----|---------|
| **2025-09-18 09:56:40** | 7045 | **Data Deduplication Service** (`svchost -k ddpsvc`) |
| 2025-09-18 09:56:41 | 7045 | Dedup (driver `dedup.sys`) |
| 2025-09-18 09:56:41 | 7045 | Data Deduplication Volume Shadow Copy Service (`ddpvssvc`) |

> Le log `Setup.evtx` (provider Microsoft-Windows-Servicing) montre l'install du *package*
> `Dedup-Core` (EID 7 à 09:56:34, EID 9/succès à 09:56:41), mais la **feature/service** est
> réellement installée à `09:56:40` (premier 7045).

---

## Q2 — Espace disque économisé par le 1er job d'optimisation

> How many bytes of disk space were saved after the first optimization job was completed?

**Réponse : `6805707`**

Premier job d'optimisation terminé — `Microsoft-Windows-Deduplication/Operational`, EventID **6153**
(« optimization job completed »), 2025-09-18 10:11:07 :

```
EventID 6153  VolumeDisplayName=D:  OptimizedFileCount=166  SavedSpace=6805707  FinalJobStage=7
```

---

## Q3 — Dernière ré-activation de Dedup sur D:

> When was Data Deduplication most recently re-enabled on volume D:?

**Réponse : `2025-09-20 03:34:35`**

Le fichier `D:\System Volume Information\Dedup\Settings\dedupConfig.0x.xml` enregistre le moment de
(re)configuration de la déduplication via le champ `changeTime` (FILETIME) :

```
changeTime = 134028128759740533  ->  2025-09-20 03:34:35 UTC
```

Cela correspond au dernier `Set/Enable-DedupVolume` sur `D:` ; un job d'optimisation démarre
d'ailleurs 14 s plus tard (Operational EID 6158 à 03:34:49).

---

## Q4 — Extensions de fichiers non optimisées

> List all file extensions that are not optimized by Data Deduplication in alphabetical order.

**Réponse : `avi, bak, edb, iso, jrs, mp4, tif`**

Depuis `dedupConfig.01.xml` / `dedupConfig.02.xml` :

```xml
<property name='excludeFileExtensions'        value='mp4|avi|iso|bak|tif' />
<property name='excludeFileExtensionsDefault' value='edb|jrs' />
```

Union des deux listes (7 extensions), triées alphabétiquement : **avi, bak, edb, iso, jrs, mp4, tif**.

---

## Q5 — Nombre de fichiers optimisés

> How many files have been optimized by Data Deduplication?

**Réponse : `168`**

`D:\System Volume Information\Dedup\State\dedupStatistics.xml` :

```xml
<property name='optimizedFileCount' value='168' />
```

(confirmé par le dernier EID 6153 Operational : `OptimizedFileCount=168`).

---

## Q6 — Prochaine exécution planifiée du job Throughput Optimization

> When is the next Throughput Optimisation job scheduled to run?

**Réponse : `2025-09-25 06:50:00`**

Tâche planifiée `C:\Windows\System32\Tasks\Microsoft\Windows\Deduplication\ThroughputOptimization` :

```xml
<CalendarTrigger>
  <StartBoundary>2025-09-20T06:50:00</StartBoundary>
  <ScheduleByWeek><DaysOfWeek><Thursday/></DaysOfWeek><WeeksInterval>1</WeeksInterval></ScheduleByWeek>
</CalendarTrigger>
```

Déclenchement **hebdomadaire le jeudi à 06:50**. Le `StartBoundary` (2025-09-20) tombe un **samedi** ;
le premier jeudi suivant est le **2025-09-25 à 06:50:00**.
