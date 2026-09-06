"""Skill: clasificar

Copia los archivos de la carpeta de origen a las subcarpetas de trabajo dentro de
la carpeta -REV. No modifica nada en la carpeta de origen: solo lee y copia.
Ningun archivo se descarta: lo que no tiene extension conocida va a 'documentos'
y queda reportado.
"""

import hashlib
import shutil
from pathlib import Path


def huella_archivo(ruta):
    """Huella SHA-256 del contenido de un archivo."""
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for bloque in iter(lambda: f.read(65536), b""):
            h.update(bloque)
    return h.hexdigest()


def clasificar(carpeta_origen, carpeta_rev, config):
    """Devuelve (inventario, rutas_subcarpetas).

    inventario: una entrada por archivo con su destino, extension y huella.
    """
    rutas = {}
    for sub in config["subcarpetas"]:
        destino = carpeta_rev / sub
        destino.mkdir(parents=True, exist_ok=True)
        rutas[sub] = destino

    mapa = config["mapa_extensiones"]
    inventario = []

    # Orden alfabetico fijo: el orden del sistema de archivos varia entre maquinas.
    for archivo in sorted(carpeta_origen.iterdir(), key=lambda p: p.name):
        if not archivo.is_file():
            continue
        if archivo.name.startswith("~$") or archivo.name.startswith("."):
            continue

        extension = archivo.suffix.lower()
        subcarpeta = mapa.get(extension)
        extension_conocida = subcarpeta is not None
        if not extension_conocida:
            subcarpeta = "documentos"

        destino = rutas[subcarpeta] / archivo.name
        shutil.copy2(archivo, destino)

        inventario.append({
            "archivo": archivo.name,
            "extension": extension or "(sin extension)",
            "extension_conocida": extension_conocida,
            "subcarpeta": subcarpeta,
            "ruta_copia": destino,
            "huella_origen": huella_archivo(archivo),
        })

    return inventario, rutas
