# Extraction de configuration — XWorm.malware

**Outils utilisés** : ILSpy (`ilspycmd`), Python (`pycryptodome`, `dnfile`)

---

## Schéma de chiffrement

La classe de configuration stocke chaque paramètre sous forme de chaîne **Base64 chiffrée en
AES**. La routine de déchiffrement (Rijndael/AES en mode **ECB**) dérive sa clé du hash MD5 d'une
chaîne codée en dur :

```csharp
RijndaelManaged rijndael = new RijndaelManaged();
MD5CryptoServiceProvider md5 = new MD5CryptoServiceProvider();
byte[] array = new byte[32];
byte[] hash = md5.ComputeHash(Encoding.UTF8.GetBytes(KEY)); // KEY = "8xTJ0EKPuiQsJVaT"
Array.Copy(hash, 0, array, 0, 16);
Array.Copy(hash, 0, array, 15, 16);   // <-- quirk : offset 15 (chevauchement)
rijndael.Key  = array;
rijndael.Mode = CipherMode.ECB;
ICryptoTransform dec = rijndael.CreateDecryptor();
byte[] data = Convert.FromBase64String(input);
return Encoding.UTF8.GetString(dec.TransformFinalBlock(data, 0, data.Length));
```

> Particularité notable : le second `Array.Copy` écrit à l'offset **15** (et non 16), ce qui fait
> chevaucher les deux copies du MD5. La clé AES-256 effective n'est donc pas un simple `MD5||MD5`,
> détail indispensable pour reproduire le déchiffrement.

### Script de déchiffrement (reproductible)

```python
import base64, hashlib
from Crypto.Cipher import AES

KEY = "8xTJ0EKPuiQsJVaT"
md5 = hashlib.md5(KEY.encode()).digest()
arr = bytearray(32)
arr[0:16]   = md5      # copie 1 : offset 0
arr[15:31]  = md5      # copie 2 : offset 15 (quirk)

def dec(b64):
    d = AES.new(bytes(arr), AES.MODE_ECB).decrypt(base64.b64decode(b64))
    return d[:-d[-1]].decode()   # retrait du padding PKCS7

print(dec("t9jQo4UCbK2ZCYwUUSBf2oYT7q1ogMGVrgjUqWnzqLxMXw3GIeVZpids5gIz2YZu"))
# 185.117.250.169,66.175.239.149,185.117.249.43
```

### Configuration déchiffrée complète

| Champ chiffré (Base64) | Valeur déchiffrée | Rôle |
|------------------------|-------------------|------|
| `t9jQo4UCbK2ZCYwUUSBf2oYT7q1ogMGVrgjUqWnzqLxMXw3GIeVZpids5gIz2YZu` | `185.117.250.169,66.175.239.149,185.117.249.43` | **Hosts (C2)** |
| `3qBjH4yDUHjhZBxWK56eYw==` | `7000` | **Port C2** |
| `P/4B29PWaJ6Raw+51xox2A==` | `<123456789>` | Marqueur de version |
| `fwWlqX1XMU7EFmHRUHk3Jw==` | `<Xwormmm>` | Splitter / mutex |
| `TowG+c1OR3RBmATvJwUFKQ==` | `Default` | Groupe |
| `lXEVYeoDw31nYYF2ts9aUQ==` | `USB.exe` | Nom de copie USB |
| `gcbmRCfQRwasaegNU1/NvQ==` | `%AppData%` | Dossier d'installation |
| `sJHKF5x7kjxy85oLMym05A==` | `WmiPrvSE.exe` | Binaire déposé |
| `llBblX1iqHd1zfZIV8Z0jL3MzbCo6zP7QWx7R9nEvuQbIA25kxWNjjY8WYEY+Xh1` | `bc1q2a4jgxmvslng5khwvzkt9pechms20ghff42s5g` | Clipper BTC |
| `ILq1reLnyJdhfez8kYLyBYJr+EjguBMQ6n4dPjgAia6wJGxs5SWbzuMPh1LUk/Ig` | `0x10cE3E5678f40f0B94A2fB5003f04012ecA407C5` | Clipper ETH |
| `6I60HSsPViAp3nyv1OYEEQ==` | `TRC20_Address` | Clipper TRC20 (placeholder) |

---

## Q6 — Algorithme cryptographique

> Which cryptographic algorithm does the malware use to encrypt or obfuscate its configuration data?

**Réponse : `AES`**

Le déchiffrement repose sur `System.Security.Cryptography.RijndaelManaged` (implémentation .NET
d'AES), en mode ECB avec padding PKCS7.

---

## Q7 — Chaîne codée en dur dérivant clé + IV

> The malware uses a hardcoded string as input to derive the key and IV. What is its value?

**Réponse : `8xTJ0EKPuiQsJVaT`**

Cette chaîne de 16 caractères est passée à `MD5.ComputeHash`, dont le résultat alimente la clé
AES (et l'IV dans les variantes utilisant un IV). C'est l'unique secret nécessaire pour déchiffrer
toute la configuration.

---

## Q8 — Adresses IP du C2

> What are the Command and Control (C2) IP addresses obtained after the malware decrypts them?

**Réponse : `185.117.250.169, 66.175.239.149, 185.117.249.43`**

Le champ `Hosts` déchiffré contient une liste de trois serveurs C2 séparés par des virgules.

---

## Q9 — Port C2

> What port number does the malware use for communication with its Command and Control (C2) server?

**Réponse : `7000`**

Le champ `Port` déchiffré vaut `7000` ; le malware ouvre une socket TCP vers chacune des trois IP
sur ce port.
