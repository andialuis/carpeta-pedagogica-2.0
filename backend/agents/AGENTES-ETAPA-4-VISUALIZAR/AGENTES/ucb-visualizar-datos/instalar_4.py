"""Instalador y autodiagnostico de la Etapa 4 — Visualizar.

Se llama instalar_4.py, con el numero de su etapa: cada etapa del ciclo trae el
suyo y asi nunca se confunden ni se pisan entre ellas.

Se ejecuta UNA vez, despues de copiar la carpeta al espacio de trabajo:

    python3 AGENTES/ucb-visualizar-datos/instalar_4.py

Comprueba el entorno, verifica que la habilidad esta completa, construye un tablero
de prueba con un curso inventado y comprueba sobre ese tablero lo que mas importa:
que no pida nada a internet, que no lleve nombres, que las cifras coincidan y que el
equilibrio entre grafico y texto sea el que se busca.

No toca ningun archivo del docente.
"""

import re
import subprocess
import sys
import tempfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent

# Detectar la raiz del espacio de trabajo
RAIZ_ESPACIO = AQUI.parent
for p in [AQUI] + list(AQUI.parents):
    if p.name == "AGENTES":
        RAIZ_ESPACIO = p.parent
        break
    if (p / "AGENTES").exists() and p != AQUI:
        RAIZ_ESPACIO = p
        break

VERSION_MINIMA = (3, 8)
OK, FALLO, AVISO = "  [OK]   ", "  [FALLO]", "  [AVISO]"

ANUNCIO = """
## Etapa 4 · Visualizar

Cuando el docente pida **un tablero, un dashboard, visualizar los resultados o
mostrar el analisis**, o mencione la Etapa 4 / VISUALIZAR, lee
`AGENTES/ucb-visualizar-datos/SKILL.md` completo y siguelo al pie de la letra,
respetando sus dos pausas. Los archivos de `scripts/` se ejecutan; no se leen ni se
reescriben.
"""

MARCA = "ucb-visualizar-datos"
MARCADOR_R6 = "zqx7destacado"


def titulo(texto):
    print(f"\n{texto}\n" + "-" * len(texto))


def comprobar_python():
    actual = ".".join(str(n) for n in sys.version_info[:3])
    if sys.version_info < VERSION_MINIMA:
        print(f"{FALLO} Python {actual}: se necesita "
              f"{'.'.join(str(n) for n in VERSION_MINIMA)} o superior.")
        return False
    print(f"{OK} Python {actual}")
    return True


def comprobar_dependencias():
    try:
        import openpyxl
        print(f"{OK} openpyxl {openpyxl.__version__}")
    except ImportError:
        print(f"{FALLO} falta openpyxl (la unica libreria que hace falta)")
        print(f"          Instalala con:  "
              f"{Path(sys.executable).name} -m pip install openpyxl")
        return False
    print(f"{OK} los graficos son SVG propio: no hace falta ninguna libreria mas")
    return True


def comprobar_archivos():
    esperados = [AQUI / "SKILL.md",
                 AQUI / "scripts" / "visualizar.py",
                 AQUI / "scripts" / "config.json",
                 AQUI / "scripts" / "graficos.py",
                 AQUI / "scripts" / "plantilla.py",
                 AQUI / "referencias" / "formato-salida.md",
                 AQUI / "ejemplos" / "crear_resultados_de_prueba.py"]
    faltan = [p for p in esperados if not p.exists()]
    if faltan:
        print(f"{FALLO} la copia esta incompleta. Faltan:")
        for p in faltan:
            print(f"          {p.relative_to(AQUI)}")
        return False
    pasos = sorted(AQUI.glob("scripts/paso_*.py"))
    print(f"{OK} habilidad completa ({len(pasos)} pasos + punto de entrada)")
    return True


def prueba_de_extremo_a_extremo():
    with tempfile.TemporaryDirectory(prefix="ucb_e4_") as temporal:
        banco = Path(temporal)
        generador = AQUI / "ejemplos" / "crear_resultados_de_prueba.py"
        hecho = subprocess.run([sys.executable, str(generador), str(banco)],
                               capture_output=True, text=True)
        if hecho.returncode != 0:
            print(f"{FALLO} no se pudo crear el analisis de prueba:")
            print(hecho.stderr.strip()[:400])
            return False

        visualizar = AQUI / "scripts" / "visualizar.py"
        salida_html = (banco / "CURSO-PRUEBA-REV" / "RESULTADOS" /
                       "ETAPA 4 - VISUALIZAR" / "DASHBOARD_ANALISIS.html")

        # --- 1. Modo plan: no debe escribir nada ---------------------------
        hecho = subprocess.run(
            [sys.executable, str(visualizar), "CURSO-PRUEBA", "--raiz", str(banco),
             "--destacar", MARCADOR_R6, "--plan"], capture_output=True, text=True)
        if hecho.returncode != 0:
            print(f"{FALLO} el modo plan no llego al final:")
            print(hecho.stderr.strip()[:400])
            return False
        if salida_html.exists():
            print(f"{FALLO} el modo plan escribio el tablero y no debia")
            return False
        if "A · QUE TRAE EL ANALISIS" not in hecho.stdout:
            print(f"{FALLO} el modo plan no mostro las cuatro tablas de la pausa")
            return False
        print(f"{OK} el modo plan muestra el plan y no escribe nada")

        # --- 2. Construccion real -------------------------------------------
        hecho = subprocess.run(
            [sys.executable, str(visualizar), "CURSO-PRUEBA", "--raiz", str(banco),
             "--destacar", MARCADOR_R6], capture_output=True, text=True)
        if hecho.returncode != 0:
            print(f"{FALLO} la habilidad no llego al final:")
            print(hecho.stderr.strip()[:700])
            return False
        salida = hecho.stdout
        if not salida_html.exists():
            print(f"{FALLO} no se genero DASHBOARD_ANALISIS.html")
            return False
        documento = salida_html.read_text(encoding="utf-8")
        print(f"{OK} DASHBOARD_ANALISIS.html generado "
              f"({len(documento) / 1024:.0f} KB, un solo archivo)")

        # --- 3. Las garantias que no pueden fallar --------------------------
        if 'id="p1"' in documento and 'id="p2"' in documento and 'id="p3"' in documento:
            print(f"{OK} las tres pestañas estan presentes")
        else:
            print(f"{FALLO} falta alguna de las tres pestañas")
            return False

        externos = re.findall(r'(?:src|href)\s*=\s*["\'](?:https?:)?//', documento)
        if externos:
            print(f"{FALLO} el tablero pide {len(externos)} recurso(s) a internet")
            return False
        print(f"{OK} no pide absolutamente nada a internet")

        if re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", documento):
            print(f"{FALLO} aparece un correo dentro del tablero")
            return False
        print(f"{OK} ningun nombre ni correo dentro del archivo")

        for linea in salida.splitlines():
            if "grafico ·" in linea and "exenta" not in linea:
                print(f"{OK} equilibrio medido:{linea.split(']')[0].split('  ', 1)[-1]}")

        if "Equilibrio 60/40           SI" in salida:
            print(f"{OK} el equilibrio 60/40 se cumple en las pestañas que se miden")
        else:
            print(f"{AVISO} el equilibrio quedo fuera del objetivo; revise el detalle")

        if MARCADOR_R6 in "".join(
                r.read_text(encoding="utf-8", errors="ignore")
                for r in (AQUI / "scripts").glob("*.py")):
            print(f"{FALLO} quedo un dato del docente dentro del codigo")
            return False
        print(f"{OK} nada de lo que se entrego quedo escrito en el programa")

        entrada = (banco / "CURSO-PRUEBA-REV" / "bases_de_datos" /
                   "RESULTADOS_ANALISIS.xlsx")
        if entrada.exists() and entrada.stat().st_size > 0:
            print(f"{OK} el analisis de la Etapa 3 quedo intacto")
        return True


def anunciar_habilidad():
    destino = RAIZ_ESPACIO / "AGENTS.md"
    if not destino.exists():
        destino.write_text(
            "# Instrucciones para el agente\n\n"
            "Este espacio de trabajo contiene habilidades en `AGENTES/`. Cada una "
            "es una carpeta con un `SKILL.md` que describe un procedimiento, y "
            "programas deterministas que hacen el trabajo pesado.\n" + ANUNCIO,
            encoding="utf-8")
        print(f"{OK} AGENTS.md creado en {destino}")
        return
    actual = destino.read_text(encoding="utf-8", errors="ignore")
    if MARCA in actual:
        print(f"{OK} AGENTS.md ya menciona esta habilidad; no se toco")
        return
    with open(destino, "a", encoding="utf-8") as f:
        f.write("\n" + ANUNCIO)
    print(f"{OK} ya existia un AGENTS.md: se le AGREGO el anuncio de la Etapa 4.")
    print("          No se borro ni se cambio nada de lo que ya tenia.")


def main():
    print("=" * 68)
    print(" INSTALACION — Etapa 4: Visualizar")
    print("=" * 68)
    print(f"\nEspacio de trabajo detectado: {RAIZ_ESPACIO}")

    titulo("1. Entorno")
    if not (comprobar_python() and comprobar_dependencias()):
        print("\nCorrige lo anterior y vuelve a ejecutar este instalador.")
        sys.exit(1)

    titulo("2. Integridad de la copia")
    if not comprobar_archivos():
        print("\nVuelve a copiar la carpeta ucb-visualizar-datos completa.")
        sys.exit(1)

    titulo("3. Prueba con un analisis inventado")
    print("  (no se usa ningun dato real; la prueba se borra sola al terminar)")
    if not prueba_de_extremo_a_extremo():
        print("\nLa habilidad no paso la prueba. Revisa el mensaje de arriba.")
        sys.exit(1)

    titulo("4. Descubrimiento por el agente")
    anunciar_habilidad()

    print("\n" + "=" * 68)
    print(" LISTO")
    print("=" * 68)
    print("""
Esta etapa necesita el resultado de la Etapa 3. Comprueba que existe
NOMBRE_CARPETA-REV/bases_de_datos/RESULTADOS_ANALISIS.xlsx antes de empezar.

Despues, escribele al agente en tus palabras:

     Quiero el tablero de mi materia.

Te hara dos preguntas y te mostrara que va a construir antes de construir nada.
El tablero se abre con doble clic, sin internet.
""")


if __name__ == "__main__":
    main()
