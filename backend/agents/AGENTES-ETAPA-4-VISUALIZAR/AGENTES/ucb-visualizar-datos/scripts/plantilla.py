"""El armazon del tablero: estructura HTML, estilos y el cambio de pestañas.

Todo va dentro del mismo archivo, sin una sola peticion a la red. Es la unica forma
de garantizar que el tablero se abra con doble clic en la sala de reuniones donde el
wifi no funciona, que es exactamente el momento en el que hace falta.

Las tipografias son las del sistema por el mismo motivo: pedirlas a un servidor de
fuentes convertiria el tablero en dependiente de internet por un detalle estetico.
"""

CABECERA = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titulo}</title>
<style>
:root{{
  --ucb:{ucb}; --ucb2:{ucb2}; --teal:{teal}; --teal2:{teal2};
  --coral:{coral}; --gold:{gold}; --lav:{lav};
  --tinta:#1e293b; --papel:#ffffff; --linea:#e2e8f0; --gris:#64748b;
  --bg-main:#f8fafc; --bg-card:#ffffff;
  --shadow-sm:0 1px 3px 0 rgba(0, 0, 0, 0.07), 0 1px 2px 0 rgba(0, 0, 0, 0.04);
  --shadow-md:0 4px 6px -1px rgba(0, 0, 0, 0.08), 0 2px 4px -1px rgba(0, 0, 0, 0.04);
  --shadow-lg:0 10px 15px -3px rgba(0, 0, 0, 0.08), 0 4px 6px -2px rgba(0, 0, 0, 0.04);
}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg-main);color:var(--tinta);
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
  font-size:15px;line-height:1.55;-webkit-font-smoothing:antialiased}}
.marco{{max-width:{ancho}px;margin:0 auto;padding:0 24px 64px}}

header.top{{background:linear-gradient(135deg, #00254d 0%, #003366 50%, #0b4f8a 100%);
  color:#fff;padding:28px 0 24px;border-bottom:1px solid rgba(255,255,255,0.1)}}
header.top .marco{{padding-bottom:0}}
.top .eyebrow{{display:inline-flex;align-items:center;gap:8px;font-size:11.5px;letter-spacing:.15em;text-transform:uppercase;
  color:#93c5fd;margin:0 0 8px;font-weight:700;background:rgba(255,255,255,0.1);padding:4px 10px;border-radius:20px}}
.top h1{{margin:0;font-size:32px;line-height:1.2;font-weight:800;letter-spacing:-.02em}}
.top .sub{{margin:8px 0 0;color:#e2e8f0;font-size:15px;font-weight:400}}

nav.tabs{{background:#00254d;position:sticky;top:0;z-index:100;
  box-shadow:0 4px 12px rgba(0,0,0,.15);border-bottom:1px solid rgba(255,255,255,.08)}}
nav.tabs .marco{{padding:0 24px;display:flex;gap:4px;flex-wrap:wrap}}
nav.tabs button{{background:none;border:0;color:#cbd5e1;font-size:15.5px;font-weight:600;
  padding:15px 22px;cursor:pointer;border-bottom:3px solid transparent;
  font-family:inherit;transition:all .2s ease;border-radius:6px 6px 0 0}}
nav.tabs button:hover{{color:#fff;background:rgba(255,255,255,.08)}}
nav.tabs button[aria-selected="true"]{{color:#fff;border-bottom-color:#38bdf8;
  background:rgba(255,255,255,.14);font-weight:700}}

.panel{{display:none;padding-top:28px;animation:fadeIn .25s ease-in-out}}
.panel[data-activo="si"]{{display:block}}
@keyframes fadeIn {{ from {{ opacity:0; transform:translateY(4px) }} to {{ opacity:1; transform:translateY(0) }} }}

.intro{{background:#fff;border-left:5px solid var(--ucb);border-radius:0 12px 12px 0;
  padding:16px 20px;margin:0 0 24px;font-size:15px;color:#334155;box-shadow:var(--shadow-sm);border:1px solid #e2e8f0;border-left-width:5px}}

h2.sec{{font-size:20px;margin:32px 0 16px;font-weight:800;letter-spacing:-.01em;color:#0f172a;
  display:flex;align-items:center;gap:10px}}
h2.sec:first-of-type{{margin-top:4px}}

.kpis{{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin:0 0 24px}}
.kpi{{background:#fff;border:1px solid var(--linea);border-top:4px solid var(--ucb2);
  border-radius:12px;padding:20px;box-shadow:var(--shadow-sm);transition:transform .2s ease, box-shadow .2s ease}}
.kpi:hover{{transform:translateY(-2px);box-shadow:var(--shadow-md)}}
.kpi .n{{font-size:38px;font-weight:800;line-height:1;letter-spacing:-.02em}}
.kpi .t{{font-size:13.5px;color:var(--gris);margin-top:8px;line-height:1.35;font-weight:500}}

.hero{{background:linear-gradient(135deg,#00254d 0%,#003366 60%,#0f766e 100%);color:#fff;
  border-radius:14px;padding:26px 30px;margin:0 0 26px;display:flex;
  gap:26px;align-items:center;flex-wrap:wrap;box-shadow:var(--shadow-md);border:1px solid rgba(255,255,255,0.1)}}
.hero .cifra{{font-size:54px;font-weight:800;line-height:1;letter-spacing:-.03em;
  color:#38bdf8}}
.hero .lado{{flex:1 1 320px}}
.hero .eti{{font-size:11.5px;letter-spacing:.16em;text-transform:uppercase;
  color:#93c5fd;font-weight:700;margin-bottom:6px}}
.hero .txt{{font-size:16.5px;color:#f1f5f9;margin:0;line-height:1.45}}

.rejilla{{display:grid;grid-template-columns:repeat(2,1fr);gap:20px;margin:0 0 20px}}
.caja{{background:#fff;border:1px solid var(--linea);border-radius:12px;
  padding:22px;box-shadow:var(--shadow-sm)}}
.caja h3{{margin:0 0 16px;font-size:15.5px;font-weight:750;color:#0f172a;letter-spacing:-.01em}}

.perfiles-grid{{display:grid;grid-template-columns:repeat(auto-fill, minmax(360px, 1fr));gap:16px;margin:0 0 26px}}
.perfil-card{{background:#fff;border:1px solid #e2e8f0;border-radius:12px;padding:18px 20px;box-shadow:var(--shadow-sm);border-left:5px solid #64748b}}
.perfil-card.destacado{{border-left-color:#059669}}
.perfil-card.medio{{border-left-color:#2563eb}}
.perfil-card.autonomo{{border-left-color:#7c3aed}}
.perfil-card.riesgo{{border-left-color:#dc2626}}
.perfil-card.alerta{{border-left-color:#d97706}}
.perfil-card .header-p{{display:flex;justify-content:space-between;align-items:center;margin-bottom:8px}}
.perfil-card .nom{{font-size:16px;font-weight:750;color:#0f172a}}
.perfil-card .count{{background:#f1f5f9;color:#334155;font-weight:700;font-size:12.5px;padding:3px 10px;border-radius:20px}}
.perfil-card .desc{{font-size:13.5px;color:#475569;margin:0 0 12px;line-height:1.4}}
.perfil-card .metricas{{display:flex;gap:12px;font-size:12.5px;color:#64748b;background:#f8fafc;padding:8px 12px;border-radius:8px;margin-bottom:12px}}
.perfil-card .codigos{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:12px;color:#334155}}

table.tabla{{width:100%;border-collapse:collapse;font-size:14px;background:#fff;
  border-radius:12px;overflow:hidden;box-shadow:var(--shadow-sm);border:1px solid #e2e8f0}}
table.tabla th{{background:#003366;color:#fff;text-align:left;padding:12px 16px;
  font-size:12px;letter-spacing:.05em;text-transform:uppercase;font-weight:700}}
table.tabla td{{padding:11px 16px;border-bottom:1px solid #f1f5f9;vertical-align:middle;color:#334155}}
table.tabla tr:hover td{{background:#f8fafc}}
table.tabla tr:last-child td{{border-bottom:0}}
.pill{{display:inline-flex;align-items:center;gap:4px;padding:3px 10px;border-radius:14px;font-size:12px;
  font-weight:700;color:#fff;letter-spacing:.02em}}
.cod{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-weight:700;color:#0f172a}}

.marcador{{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin:0 0 26px}}
.marcador .m{{border-radius:12px;padding:22px;text-align:center;color:#fff;
  box-shadow:var(--shadow-sm)}}
.marcador .m .n{{font-size:48px;font-weight:800;line-height:1}}
.marcador .m .t{{font-size:13px;font-weight:700;letter-spacing:.06em;
  text-transform:uppercase;margin-top:6px;opacity:.95}}

.tarjeta{{background:#fff;border:1px solid #e2e8f0;border-left:5px solid var(--gris);
  border-radius:12px;padding:22px;margin:0 0 18px;
  box-shadow:var(--shadow-sm)}}
.tarjeta .ver{{display:inline-block;font-size:11.5px;font-weight:800;letter-spacing:.06em;
  text-transform:uppercase;padding:4px 10px;border-radius:6px;color:#fff}}
.tarjeta h4{{margin:10px 0 6px;font-size:17.5px;line-height:1.3;font-weight:750;color:#0f172a}}
.tarjeta .llano{{font-size:15px;color:#334155;margin:8px 0 0;line-height:1.5}}
.tarjeta .campos{{display:grid;grid-template-columns:repeat(2,1fr);gap:12px;
  margin-top:14px}}
.tarjeta .campo{{background:#f8fafc;border-radius:8px;padding:12px 14px;border:1px solid #e2e8f0}}
.tarjeta .campo b{{display:block;font-size:11px;letter-spacing:.08em;
  text-transform:uppercase;color:#64748b;margin-bottom:4px}}
details.detalle{{margin-top:12px;font-size:13.5px}}
details.detalle summary{{cursor:pointer;color:#0369a1;font-weight:600}}
details.detalle .cuerpo{{margin-top:8px;color:#64748b;
  font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:12px;background:#f1f5f9;padding:8px 12px;border-radius:6px}}

.aviso{{background:#fffbeb;border:1px solid #fef3c7;border-left:5px solid #d97706;border-radius:10px;
  padding:14px 18px;margin:20px 0;font-size:14.5px;color:#92400e}}
.vacio{{background:#fff;border:1px dashed #cbd5e1;border-radius:10px;
  padding:24px;text-align:center;color:#64748b;font-size:14.5px}}

/* Graficos SVG */
.g-tit{{font-size:13.5px;font-weight:750;fill:#0f172a}}
.g-eti{{font-size:12px;fill:#475569}}
.g-val{{font-size:12.5px;font-weight:700;fill:#0f172a}}
.g-tick{{font-size:11px;fill:#64748b}}
.g-eje{{font-size:11.5px;font-weight:700;fill:#475569}}
.g-dona-num{{font-size:32px;font-weight:800;fill:#0f172a}}
.g-dona-txt{{font-size:12px;font-weight:500;fill:#64748b}}
.g-semaforo{{font-size:24px;font-weight:800;fill:#0f172a}}
.g-alcance{{font-size:28px;font-weight:800;fill:#0f172a}}

footer.pie{{margin-top:48px;padding-top:22px;border-top:1px solid #e2e8f0;
  font-size:13px;color:#64748b;text-align:center}}

@media (max-width:900px){{
  .kpis{{grid-template-columns:repeat(2,1fr)}}
  .rejilla,.tarjeta .campos,.perfiles-grid{{grid-template-columns:1fr}}
  .marcador{{grid-template-columns:1fr}}
  .hero .cifra{{font-size:42px}}
}}
@media print{{
  nav.tabs{{position:static}}
  .panel{{display:block!important;page-break-before:always}}
}}
</style>
</head>
<body>
<header class="top"><div class="marco">
  <div class="eyebrow">Analítica del Aprendizaje UCB · AGENTE-E4</div>
  <h1>{titulo}</h1>
  <p class="sub">{subtitulo}</p>
</div></header>

<nav class="tabs" role="tablist"><div class="marco">
  <button role="tab" aria-selected="true" aria-controls="p1" onclick="verPestana(1,this)">1 · Radiografía y Perfiles del Curso</button>
  <button role="tab" aria-selected="false" aria-controls="p2" onclick="verPestana(2,this)">2 · Hipótesis y Hallazgos Demostrados</button>
  <button role="tab" aria-selected="false" aria-controls="p3" onclick="verPestana(3,this)">3 · Plan de Acción Pedagógica</button>
</div></nav>

<div class="marco">
"""

PIE = """
<footer class="pie">
  {pie}
</footer>
</div>
<script>
function verPestana(n, boton){
  for (var i = 1; i <= 3; i++) {
    document.getElementById('p' + i).setAttribute('data-activo', i === n ? 'si' : 'no');
  }
  var botones = document.querySelectorAll('nav.tabs button');
  for (var j = 0; j < botones.length; j++) {
    botones[j].setAttribute('aria-selected', botones[j] === boton ? 'true' : 'false');
  }
  window.scrollTo(0, 0);
}
</script>
</body>
</html>
"""


def armar(config, titulo, subtitulo, paneles, pie):
    colores = config["colores"]
    cabecera = CABECERA.format(titulo=titulo, subtitulo=subtitulo,
                               ancho=config["ancho_tablero"], **colores)
    cuerpo = []
    for numero, contenido in enumerate(paneles, start=1):
        activo = "si" if numero == 1 else "no"
        cuerpo.append(f'<section class="panel" id="p{numero}" role="tabpanel" '
                      f'data-activo="{activo}">{contenido}</section>')
    return cabecera + "".join(cuerpo) + PIE.replace("{pie}", pie)
