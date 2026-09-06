"""Skill: identidad

Reconoce a la misma persona escrita de formas distintas en cada archivo, usando la
lista oficial de matricula como unica version correcta.

La busqueda va en cascada, de lo mas seguro a lo mas dudoso, y siempre deja
registrado con que metodo se resolvio:

  1. codigo exacto
  2. correo electronico completo
  3. nombre exacto sin importar el orden  (apellido primero o nombre primero)
  4. nombre con inicial abreviada         ("Nombre Segundo A.")
  5. parecido de texto, solo si es alto y el segundo candidato queda lejos

Usa unicamente la biblioteca estandar de Python: el resultado no puede depender de
que una libreria opcional este instalada o no.
"""

import re
import unicodedata
from difflib import SequenceMatcher


def reparar_acentos(texto):
    """Repara texto UTF-8 leido como latin-1 (ej. 'NuÃ±ez' -> 'Nunez')."""
    if any(marca in texto for marca in ("Ã", "Â", "â€")):
        try:
            return texto.encode("latin-1").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            return texto
    return texto


def normalizar(valor):
    if valor is None:
        return ""
    texto = reparar_acentos(str(valor)).strip().lower()
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    texto = re.sub(r"[^a-z0-9@.\s]", " ", texto)
    return " ".join(texto.split())


def tokens(valor):
    texto = normalizar(valor)
    texto = re.sub(r"[@.]", " ", texto)
    return {t for t in texto.split() if t}


class Reconocedor:
    def __init__(self, estudiantes, config):
        """estudiantes: lista de dicts con id, nombre y correo oficiales."""
        self.estudiantes = []
        for indice, est in enumerate(estudiantes):
            self.estudiantes.append({
                "fila": indice,
                "id": est["id"],
                "nombre": est["nombre"],
                "correo": est["correo"],
                "n_id": normalizar(est["id"]),
                "n_nombre": normalizar(est["nombre"]),
                "n_correo": normalizar(est["correo"]),
                "tokens": tokens(est["nombre"]),
            })
        self.umbral = config["umbral_similitud"]
        self.margen = config["margen_minimo_similitud"]
        self.min_tokens = config["minimo_tokens_comunes"]
        self._cache = {}

    # ---------------------------------------------------------------- etapas
    def _por_codigo(self, valor):
        n = normalizar(valor)
        if not n:
            return []
        return [e for e in self.estudiantes if e["n_id"] and e["n_id"] == n]

    def _por_correo(self, valor):
        n = normalizar(valor)
        if "@" not in n:
            return []
        return [e for e in self.estudiantes if e["n_correo"] and e["n_correo"] == n]

    def _por_nombre_exacto(self, valor):
        t = tokens(valor)
        if len(t) < self.min_tokens:
            return []
        return [e for e in self.estudiantes if e["tokens"] == t]

    def _por_inicial(self, valor):
        """Acepta nombres con una parte abreviada a su inicial."""
        t = tokens(valor)
        if len(t) < self.min_tokens:
            return []
        completos = {x for x in t if len(x) > 1}
        iniciales = {x for x in t if len(x) == 1}
        candidatos = []
        for est in self.estudiantes:
            if not completos <= est["tokens"]:
                continue
            restantes = est["tokens"] - completos
            if all(any(r.startswith(i) for r in restantes) for i in iniciales):
                candidatos.append(est)
        return candidatos if len(completos) >= self.min_tokens else []

    def _por_parecido(self, valor):
        n = normalizar(valor)
        if not n:
            return [], 0.0
        puntajes = []
        for est in self.estudiantes:
            base = SequenceMatcher(None, n, est["n_nombre"]).ratio()
            orden = SequenceMatcher(None, " ".join(sorted(tokens(valor))),
                                    " ".join(sorted(est["tokens"]))).ratio()
            puntajes.append((max(base, orden), est))
        puntajes.sort(key=lambda p: (-p[0], p[1]["fila"]))
        mejor, segundo = puntajes[0], (puntajes[1] if len(puntajes) > 1 else (0.0, None))
        if mejor[0] >= self.umbral and (mejor[0] - segundo[0]) >= self.margen:
            return [mejor[1]], mejor[0]
        if mejor[0] >= self.umbral:
            return [mejor[1], segundo[1]], mejor[0]      # empate -> ambiguo
        return [], mejor[0]

    # ---------------------------------------------------------------- publica
    def buscar(self, valor):
        """Devuelve (estudiante | None, metodo, puntaje, candidatos_ambiguos)."""
        clave = str(valor)
        if clave in self._cache:                # los registros repiten identidades
            return self._cache[clave]
        resultado = self._buscar(valor)
        self._cache[clave] = resultado
        return resultado

    def _buscar(self, valor):
        if valor is None or not str(valor).strip():
            return None, "vacio", 0.0, []

        for metodo, funcion in (("codigo", self._por_codigo),
                                ("correo", self._por_correo),
                                ("nombre_exacto", self._por_nombre_exacto),
                                ("nombre_con_inicial", self._por_inicial)):
            encontrados = funcion(valor)
            if len(encontrados) == 1:
                return encontrados[0], metodo, 1.0, []
            if len(encontrados) > 1:
                return None, f"ambiguo_{metodo}", 1.0, encontrados

        encontrados, puntaje = self._por_parecido(valor)
        if len(encontrados) == 1:
            return encontrados[0], "parecido", puntaje, []
        if len(encontrados) > 1:
            return None, "ambiguo_parecido", puntaje, encontrados
        return None, "sin_coincidencia", puntaje, []
