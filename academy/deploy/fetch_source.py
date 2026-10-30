"""Télécharge le dossier academy/ du dépôt GitHub à une révision donnée (utilisé à la construction de l'image)."""
import io
import sys
import tarfile
import urllib.request

ref, dest = sys.argv[1], sys.argv[2]
url = f"https://codeload.github.com/AYBBKF/WaveCast/tar.gz/{ref}"
with urllib.request.urlopen(url, timeout=60) as resp:
    archive = tarfile.open(fileobj=io.BytesIO(resp.read()), mode="r:gz")
members = []
for m in archive.getmembers():
    parts = m.name.split("/", 2)
    if len(parts) == 3 and parts[1] == "academy" and parts[2]:
        m.name = parts[2]
        members.append(m)
if not members:
    sys.exit(f"Dossier academy/ introuvable à la révision {ref}")
archive.extractall(dest, members=members, filter="data")
print(f"{len(members)} fichiers extraits depuis {ref}")
