'use client';
import { useState } from 'react';
import { 
  BookOpen, FileText, ShieldCheck, HeartHandshake, 
  Brain, Award, PlusCircle, FolderTree, Bot, Activity, 
  Compass, CheckCircle2, AlertTriangle, Download, Sparkles, Share2
} from 'lucide-react';

export default function DocumentacionPage() {
  const [activeTab, setActiveTab] = useState<'manual' | 'terminos' | 'pedagogia'>('manual');

  return (
    <div className="text-slate-800 pb-20 font-sans-clean max-w-5xl mx-auto">
      {/* Header */}
      <header className="mb-6 border-b border-[#E8E3DA] pb-5">
        <div className="flex items-center gap-2 mb-1">
          <span className="text-[10px] font-bold tracking-widest uppercase text-amber-800 bg-amber-100/80 px-2.5 py-0.5 rounded-full border border-amber-300">
            Documentación Integral
          </span>
          <span className="text-[10px] font-medium text-slate-400">• v1.0 Personal & Educational</span>
        </div>
        <h1 className="text-3xl font-bold font-editorial text-slate-900 flex items-center gap-3">
          <BookOpen className="w-8 h-8 text-amber-700" />
          Manual de Uso, Términos y Marco Pedagógico
        </h1>
        <p className="text-slate-500 text-sm mt-0.5">
          Guía operativa completa, condiciones de licenciamiento no comercial y fundamentos didácticos
        </p>
      </header>

      {/* Tabs Selector */}
      <div className="flex border-b border-[#E2DDD5] mb-8 gap-2">
        <button
          onClick={() => setActiveTab('manual')}
          className={`pb-3 px-4 text-xs font-bold transition border-b-2 flex items-center gap-2 cursor-pointer ${
            activeTab === 'manual'
              ? 'border-slate-900 text-slate-900'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <BookOpen className="w-4 h-4" />
          Manual de Uso (6 Pasos)
        </button>
        <button
          onClick={() => setActiveTab('terminos')}
          className={`pb-3 px-4 text-xs font-bold transition border-b-2 flex items-center gap-2 cursor-pointer ${
            activeTab === 'terminos'
              ? 'border-slate-900 text-slate-900'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <ShieldCheck className="w-4 h-4" />
          Términos de Uso & Licencia
        </button>
        <button
          onClick={() => setActiveTab('pedagogia')}
          className={`pb-3 px-4 text-xs font-bold transition border-b-2 flex items-center gap-2 cursor-pointer ${
            activeTab === 'pedagogia'
              ? 'border-slate-900 text-slate-900'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <Brain className="w-4 h-4" />
          Marco Pedagógico & DUA
        </button>
      </div>

      {/* PESTAÑA 1: MANUAL DE USO PASO A PASO */}
      {activeTab === 'manual' && (
        <div className="space-y-6 animate-in fade-in duration-200">
          <div className="bg-white p-6 sm:p-8 rounded-3xl shadow-atelier border border-[#E2DDD5]">
            <h2 className="text-xl font-bold font-editorial text-slate-900 mb-2">
              Guía Operativa del Flujo Pedagógico
            </h2>
            <p className="text-xs text-slate-500 mb-6 font-medium leading-relaxed">
              Carpeta Pedagógica 2.0 organiza el trabajo docente en una secuencia lógica y sistemática de 6 fases, garantizando que los datos cuantitativos se transformen en decisiones cualitativas y humanas:
            </p>

            <div className="space-y-6">
              {/* Paso 1 */}
              <div className="flex gap-4 items-start">
                <div className="w-8 h-8 rounded-2xl bg-amber-500 text-white font-mono font-bold text-sm flex items-center justify-center flex-shrink-0 mt-0.5 shadow-xs">
                  1
                </div>
                <div className="flex-1 bg-[#FAF8F5] p-5 rounded-2xl border border-[#E8E3DA]">
                  <div className="flex items-center gap-2 mb-1 font-bold text-slate-900 text-sm">
                    <PlusCircle className="w-4 h-4 text-amber-700" />
                    <span>Crear Clase & Ingesta Documental</span>
                  </div>
                  <p className="text-xs text-slate-600 leading-relaxed font-serif-warm mb-2">
                    En la pantalla principal (<code>/</code>), sube una planilla Excel (<code>.xlsx</code>) o CSV con las calificaciones del curso, o haz clic en <strong>"+ Crear Nueva Materia"</strong> para configurar un expediente desde cero con su nivel, sistema y competencias esperadas.
                  </p>
                  <span className="text-[10px] bg-white text-slate-700 font-semibold px-2.5 py-1 rounded-lg border border-[#DDD7CD] inline-block">
                    ✓ Validación Human-in-the-loop antes de inyectar datos
                  </span>
                </div>
              </div>

              {/* Paso 2 */}
              <div className="flex gap-4 items-start">
                <div className="w-8 h-8 rounded-2xl bg-indigo-600 text-white font-mono font-bold text-sm flex items-center justify-center flex-shrink-0 mt-0.5 shadow-xs">
                  2
                </div>
                <div className="flex-1 bg-[#FAF8F5] p-5 rounded-2xl border border-[#E8E3DA]">
                  <div className="flex items-center gap-2 mb-1 font-bold text-slate-900 text-sm">
                    <Brain className="w-4 h-4 text-indigo-700" />
                    <span>Planificación Curricular & PDC</span>
                  </div>
                  <p className="text-xs text-slate-600 leading-relaxed font-serif-warm mb-2">
                    En <code>/planificacion</code>, diseña las unidades didácticas, los criterios de desempeño por competencias (CBL) y los saberes formativos. Puedes generar un borrador curricular con IA o redactarlo manualmente según el modelo de tu institución educativa.
                  </p>
                  <span className="text-[10px] bg-white text-slate-700 font-semibold px-2.5 py-1 rounded-lg border border-[#DDD7CD] inline-block">
                    ✓ Estructuración de unidades y objetivos holísticos
                  </span>
                </div>
              </div>

              {/* Paso 3 */}
              <div className="flex gap-4 items-start">
                <div className="w-8 h-8 rounded-2xl bg-slate-800 text-white font-mono font-bold text-sm flex items-center justify-center flex-shrink-0 mt-0.5 shadow-xs">
                  3
                </div>
                <div className="flex-1 bg-[#FAF8F5] p-5 rounded-2xl border border-[#E8E3DA]">
                  <div className="flex items-center gap-2 mb-1 font-bold text-slate-900 text-sm">
                    <FolderTree className="w-4 h-4 text-slate-700" />
                    <span>Organizar Expedientes & Versiones REV</span>
                  </div>
                  <p className="text-xs text-slate-600 leading-relaxed font-serif-warm mb-2">
                    En <code>/organizar</code>, supervisa la estructura física de carpetas dentro del directorio <code>uploads/</code>. Compara la versión original con la versión integrada (<code>-REV</code>) que contiene los manifiestos, planes modulares y bases de datos limpias.
                  </p>
                  <span className="text-[10px] bg-white text-slate-700 font-semibold px-2.5 py-1 rounded-lg border border-[#DDD7CD] inline-block">
                    ✓ Descarga de respaldos y verificación de integridad
                  </span>
                </div>
              </div>

              {/* Paso 4 */}
              <div className="flex gap-4 items-start">
                <div className="w-8 h-8 rounded-2xl bg-purple-700 text-white font-mono font-bold text-sm flex items-center justify-center flex-shrink-0 mt-0.5 shadow-xs">
                  4
                </div>
                <div className="flex-1 bg-[#FAF8F5] p-5 rounded-2xl border border-[#E8E3DA]">
                  <div className="flex items-center gap-2 mb-1 font-bold text-slate-900 text-sm">
                    <Bot className="w-4 h-4 text-purple-700" />
                    <span>Flujo de Agentes (Pipeline de Analítica)</span>
                  </div>
                  <p className="text-xs text-slate-600 leading-relaxed font-serif-warm mb-2">
                    En <code>/agents</code>, ejecuta el pipeline metodológico de 4 etapas:
                  </p>
                  <ul className="text-xs space-y-1 text-slate-600 font-serif-warm list-disc pl-5 mb-2">
                    <li><strong>Etapa 1:</strong> Prepara e integra los datos crudos en <code>BASE_INTEGRADA.xlsx</code>.</li>
                    <li><strong>Etapa 2:</strong> Anonimiza criptográficamente los nombres y genera la <code>llave_nombres.json</code>.</li>
                    <li><strong>Etapa 3:</strong> Calcula estadística avanzada (asimetría de Fisher, curtosis) e inferencia con IA.</li>
                    <li><strong>Etapa 4:</strong> Renderiza los gráficos interactivos para el tablero de control.</li>
                  </ul>
                </div>
              </div>

              {/* Paso 5 */}
              <div className="flex gap-4 items-start">
                <div className="w-8 h-8 rounded-2xl bg-emerald-700 text-white font-mono font-bold text-sm flex items-center justify-center flex-shrink-0 mt-0.5 shadow-xs">
                  5
                </div>
                <div className="flex-1 bg-[#FAF8F5] p-5 rounded-2xl border border-[#E8E3DA]">
                  <div className="flex items-center gap-2 mb-1 font-bold text-slate-900 text-sm">
                    <Activity className="w-4 h-4 text-emerald-700" />
                    <span>Tablero de Control & Diagnóstico Ejecutivo</span>
                  </div>
                  <p className="text-xs text-slate-600 leading-relaxed font-serif-warm mb-2">
                    En <code>/analytics</code>, explora la distribución gaussiana del grupo, la correlación de notas vs asistencia, el radar de autodeterminación (Autonomía, Competencia, Relación) y haz clic en <strong>"✨ Diagnóstico Ejecutivo (IA)"</strong> para generar el informe cualitativo para coordinación académica.
                  </p>
                  <span className="text-[10px] bg-white text-slate-700 font-semibold px-2.5 py-1 rounded-lg border border-[#DDD7CD] inline-block">
                    ✓ Exportación del dataset anonimizado a Excel o CSV para SPSS/R
                  </span>
                </div>
              </div>

              {/* Paso 6 */}
              <div className="flex gap-4 items-start">
                <div className="w-8 h-8 rounded-2xl bg-rose-700 text-white font-mono font-bold text-sm flex items-center justify-center flex-shrink-0 mt-0.5 shadow-xs">
                  6
                </div>
                <div className="flex-1 bg-[#FAF8F5] p-5 rounded-2xl border border-[#E8E3DA]">
                  <div className="flex items-center gap-2 mb-1 font-bold text-slate-900 text-sm">
                    <Award className="w-4 h-4 text-rose-700" />
                    <span>Evaluación Formativa, DUA & Dossier Oficial</span>
                  </div>
                  <p className="text-xs text-slate-600 leading-relaxed font-serif-warm mb-2">
                    En <code>/evaluacion</code>, genera rúbricas analíticas por niveles de desempeño y descárgalas en Word (<code>.docx</code>). En la <strong>Matriz DUA</strong>, activa el botón <strong>"✨ Sugerir con IA"</strong> para personalizar la adaptación según los 3 principios CAST, y compila el <strong>Dossier Oficial Consolidado (.docx)</strong> con un solo clic.
                  </p>
                  <span className="text-[10px] bg-white text-slate-700 font-semibold px-2.5 py-1 rounded-lg border border-[#DDD7CD] inline-block">
                    ✓ Detección de outsourcing cognitivo y entrevista de triangulación socrática
                  </span>
                </div>
              </div>
            </div>

            {/* Subsección: Guía de Vinculación con LMS */}
            <div className="mt-8 pt-8 border-t border-[#EFEAE1]">
              <div className="flex items-center gap-2 mb-3">
                <span className="text-[10px] font-bold tracking-widest uppercase text-indigo-800 bg-indigo-100/80 px-2.5 py-0.5 rounded-full border border-indigo-300">
                  Interoperabilidad Docente
                </span>
              </div>
              <h3 className="text-lg font-bold font-editorial text-slate-900 flex items-center gap-2 mb-2">
                <Share2 className="w-5 h-5 text-indigo-700" />
                Guía de Vinculación y Automatización con LMS (Moodle, Classroom, Teams)
              </h3>
              <p className="text-xs text-slate-600 leading-relaxed font-serif-warm mb-4">
                Como docentes, frecuentemente trabajamos en entornos virtuales institucionales. Carpeta Pedagógica 2.0 se integra de manera no invasiva, cerrando el ciclo entre la gestión analítica y la entrega formativa:
              </p>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs font-serif-warm">
                <div className="p-4 rounded-2xl bg-[#FAF8F5] border border-[#E8E3DA]">
                  <div className="flex items-center justify-between font-bold font-sans-clean text-amber-900 mb-2">
                    <span>1. Moodle LMS</span>
                    <span className="text-[9px] bg-amber-100 text-amber-800 px-2 py-0.5 rounded font-mono font-bold">CSV UTF-8</span>
                  </div>
                  <p className="text-slate-600 mb-2 leading-relaxed">
                    <strong>Exportación desde Moodle:</strong> Ve a tu curso &gt; <em>Calificaciones &gt; Exportar &gt; Hoja de cálculo de texto plano (CSV)</em>.
                  </p>
                  <p className="text-slate-600 leading-relaxed">
                    <strong>Reimportación de Feedback:</strong> Tras procesar y descargar desde el Centro LMS de la app, ve a <em>Calificaciones &gt; Importar &gt; Archivo CSV</em>. Mapea la columna <code>Número de ID</code> para identificar estudiantes y <code>Comentarios de retroalimentación</code> para inyectar las devoluciones DUA directamente al libro de notas.
                  </p>
                </div>

                <div className="p-4 rounded-2xl bg-[#FAF8F5] border border-[#E8E3DA]">
                  <div className="flex items-center justify-between font-bold font-sans-clean text-emerald-900 mb-2">
                    <span>2. Google Classroom</span>
                    <span className="text-[9px] bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded font-mono font-bold">CSV</span>
                  </div>
                  <p className="text-slate-600 mb-2 leading-relaxed">
                    <strong>Exportación desde Classroom:</strong> Abre cualquier tarea entregada &gt; rueda dentada ⚙ &gt; <em>Descargar todas las calificaciones como CSV</em>.
                  </p>
                  <p className="text-slate-600 leading-relaxed">
                    <strong>Uso en la App:</strong> Carga la planilla. Los agentes asocian nombres y correos institucionales. Al descargar el feedback formativo, obtienes un archivo tabulado listo para copiar observaciones o sincronizar con hojas de cálculo de Google Drive.
                  </p>
                </div>

                <div className="p-4 rounded-2xl bg-[#FAF8F5] border border-[#E8E3DA]">
                  <div className="flex items-center justify-between font-bold font-sans-clean text-indigo-900 mb-2">
                    <span>3. Microsoft Teams</span>
                    <span className="text-[9px] bg-indigo-100 text-indigo-800 px-2 py-0.5 rounded font-mono font-bold">Excel (.xlsx)</span>
                  </div>
                  <p className="text-slate-600 mb-2 leading-relaxed">
                    <strong>Exportación desde Teams:</strong> En el equipo de clase &gt; pestaña <em>Notas (Grades) &gt; Exportar a Excel</em> (genera <code>Grades.xlsx</code>).
                  </p>
                  <p className="text-slate-600 leading-relaxed">
                    <strong>Uso en la App:</strong> Sube el archivo Excel en la app. Al finalizar, exporta en formato Teams desde el módulo de Administración para obtener un libro de trabajo consolidado con notas ponderadas y adaptaciones metodológicas.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* PESTAÑA 2: TÉRMINOS DE USO Y LICENCIA */}
      {activeTab === 'terminos' && (
        <div className="space-y-6 animate-in fade-in duration-200">
          <div className="bg-white p-6 sm:p-8 rounded-3xl shadow-atelier border border-[#E2DDD5]">
            <div className="flex items-center gap-3 border-b border-[#EFEAE1] pb-4 mb-6">
              <div className="p-3 rounded-2xl bg-slate-900 text-amber-400 shadow-xs">
                <ShieldCheck className="w-6 h-6" />
              </div>
              <div>
                <h2 className="text-xl font-bold font-editorial text-slate-900">
                  Términos de Uso & Licencia de Distribución
                </h2>
                <p className="text-xs text-slate-500 font-medium">
                  Versión 1.0 Personal & Educational Edition • Autoría & Licencia No Comercial
                </p>
              </div>
            </div>

            <div className="space-y-6 text-xs leading-relaxed text-slate-700 font-serif-warm">
              <div className="p-5 rounded-2xl bg-amber-50/70 border border-amber-200">
                <h3 className="text-sm font-bold text-amber-950 font-sans-clean mb-1">
                  1. Autoría y Créditos del Software
                </h3>
                <p>
                  El creador, diseñador y desarrollador oficial de la plataforma <strong>Carpeta Pedagógica 2.0</strong> es <strong className="text-slate-900">Luis Alfredo Andia Valverde</strong> (<a href="mailto:luis.andia.valverde@gmail.com" className="text-amber-900 underline font-mono font-semibold">luis.andia.valverde@gmail.com</a>). Todos los derechos morales de autor sobre la arquitectura de agentes, algoritmos de analítica humanista, diseño de interfaz y diseño instruccional le pertenecen.
                </p>
              </div>

              <div className="p-5 rounded-2xl bg-[#FAF8F5] border border-[#E8E3DA]">
                <h3 className="text-sm font-bold text-slate-900 font-sans-clean mb-1">
                  2. Licencia de Distribución y Uso No Comercial (CC BY-NC 4.0)
                </h3>
                <p className="mb-2">
                  El autor autoriza expresamente la <strong>distribución, reproducción, instalación, ejecución y adaptación libre</strong> de esta aplicación web para fines personales, educativos y científicos, bajo las siguientes condiciones:
                </p>
                <ul className="list-disc pl-5 space-y-1.5 font-medium">
                  <li><strong>Sin beneficio comercial:</strong> Queda terminantemente prohibida su venta, comercialización, cobro por licenciamiento o integración en plataformas con fines de lucro directo o indirecto.</li>
                  <li><strong>Reconocimiento de autoría:</strong> Toda copia o versión adaptada debe citar de manera clara y visible la autoría de <strong className="text-slate-900">Luis Alfredo Andia Valverde</strong>.</li>
                  <li><strong>Distribución solidaria:</strong> Los derivados desarrollados deben compartirse bajo los mismos términos de libertad pedagógica y código abierto no lucrativo.</li>
                </ul>
              </div>

              <div className="p-5 rounded-2xl bg-[#FAF8F5] border border-[#E8E3DA]">
                <h3 className="text-sm font-bold text-slate-900 font-sans-clean mb-1">
                  3. Principio "Human-in-the-loop" (Soberanía Docente)
                </h3>
                <p>
                  La inteligencia artificial (Google Gemini) y el motor determinista local actúan exclusivamente como <strong>asistentes y copilotos metodológicos</strong>. Ninguna métrica, alerta de riesgo o recomendación de adaptación exime ni reemplaza el criterio ético y pedagógico soberano del docente frente al estudiante.
                </p>
              </div>

              <div className="p-5 rounded-2xl bg-[#FAF8F5] border border-[#E8E3DA]">
                <h3 className="text-sm font-bold text-slate-900 font-sans-clean mb-1">
                  4. Privacidad y Soberanía de los Datos Estudiantiles
                </h3>
                <p>
                  El sistema opera bajo arquitectura local soberana: las planillas y bases de datos residen en la máquina del usuario. La Etapa 2 del pipeline anonimiza mediante hash criptográfico las identidades antes de cualquier procesamiento con modelos externos, previniendo la exposición de datos personales sensibles.
                </p>
              </div>

              <div className="p-5 rounded-2xl bg-[#FAF8F5] border border-[#E8E3DA]">
                <h3 className="text-sm font-bold text-slate-900 font-sans-clean mb-1">
                  5. Interoperabilidad Ética con Moodle, Classroom y Teams
                </h3>
                <p>
                  Las herramientas de importación y exportación LMS funcionan mediante intercambio estandarizado de archivos tabulares (CSV y Excel). No se almacenan credenciales sensibles ni tokens de acceso que puedan comprometer la seguridad de las plataformas institucionales del docente o de la universidad.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* PESTAÑA 3: MARCO PEDAGÓGICO & DUA */}
      {activeTab === 'pedagogia' && (
        <div className="space-y-6 animate-in fade-in duration-200">
          <div className="bg-white p-6 sm:p-8 rounded-3xl shadow-atelier border border-[#E2DDD5]">
            <h2 className="text-xl font-bold font-editorial text-slate-900 mb-2">
              Fundamentación Teórica & Pedagógica
            </h2>
            <p className="text-xs text-slate-500 mb-6 font-medium">
              Pilares epistemológicos que sustentan los algoritmos e instrumentos de Carpeta Pedagógica 2.0:
            </p>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-5 text-xs font-serif-warm text-slate-700 leading-relaxed">
              <div className="p-5 rounded-2xl bg-[#FAF8F5] border border-[#E8E3DA]">
                <div className="flex items-center gap-2 mb-2 font-bold font-sans-clean text-slate-900">
                  <Compass className="w-4 h-4 text-amber-700" />
                  <span>Pedagogía Crítica (Paulo Freire)</span>
                </div>
                <p>
                  Superación radical de la <em>educación bancaria</em>, donde el estudiante es visto como un recipiente pasivo de notas. La plataforma evalúa el diálogo, la autoría y la capacidad de cuestionamiento crítico frente al saber.
                </p>
              </div>

              <div className="p-5 rounded-2xl bg-[#FAF8F5] border border-[#E8E3DA]">
                <div className="flex items-center gap-2 mb-2 font-bold font-sans-clean text-slate-900">
                  <Award className="w-4 h-4 text-purple-700" />
                  <span>Diseño Universal (CAST 2024)</span>
                </div>
                <p>
                  Garantiza accesibilidad plena mediante 3 redes neuronales de aprendizaje: <strong>Compromiso</strong> (por qué aprender), <strong>Representación</strong> (qué aprender) y <strong>Acción/Expresión</strong> (cómo demostrar el saber).
                </p>
              </div>

              <div className="p-5 rounded-2xl bg-[#FAF8F5] border border-[#E8E3DA]">
                <div className="flex items-center gap-2 mb-2 font-bold font-sans-clean text-slate-900">
                  <Sparkles className="w-4 h-4 text-indigo-700" />
                  <span>Zona de Desarrollo Próximo (Vygotsky)</span>
                </div>
                <p>
                  El andamiaje formativo ajusta los apoyos según la distancia entre la capacidad autónoma del estudiante y el nivel de resolución con orientación docente o colaborativa.
                </p>
              </div>

              <div className="p-5 rounded-2xl bg-[#FAF8F5] border border-[#E8E3DA]">
                <div className="flex items-center gap-2 mb-2 font-bold font-sans-clean text-slate-900">
                  <HeartHandshake className="w-4 h-4 text-emerald-700" />
                  <span>Retroalimentación de Alto Impacto (Hattie)</span>
                </div>
                <p>
                  Basado en la evidencia de John Hattie ($d=1.16$), donde el feedback formativo temprano y continuo produce uno de los mayores efectos en el logro académico genuino.
                </p>
              </div>
            </div>

            {/* Protocolo Anti-Outsourcing */}
            <div className="mt-6 p-5 rounded-2xl bg-amber-50/80 border border-amber-300 text-xs">
              <h4 className="font-bold text-amber-950 font-sans-clean flex items-center gap-2 mb-1.5">
                <AlertTriangle className="w-4 h-4 text-amber-700" />
                Vigilancia Epistémica contra el Outsourcing Cognitivo
              </h4>
              <p className="text-amber-900 leading-relaxed font-serif-warm">
                El <em>outsourcing cognitivo</em> ocurre cuando un estudiante delega a la inteligencia artificial el proceso de abstracción, síntesis y redacción sin ejercitar su propio esfuerzo reflexivo ("sudor intelectual"). La plataforma no castiga punitivamente el uso de IA, sino que prescribe la <strong>Guía de Triangulación Socrática</strong>: una entrevista dialógica breve de 5 minutos donde el alumno valida su comprensión verbal y defiende sus fuentes.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
