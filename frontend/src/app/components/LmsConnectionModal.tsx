'use client';
import { useState } from 'react';
import { 
  X, Share2, Download, CheckCircle2, FileSpreadsheet, 
  ExternalLink, ShieldCheck, ArrowRight, RefreshCw, Info, HelpCircle
} from 'lucide-react';

interface LmsConnectionModalProps {
  isOpen: boolean;
  onClose: () => void;
  subjects?: string[];
  initialSubject?: string;
}

export default function LmsConnectionModal({ 
  isOpen, 
  onClose, 
  subjects = [], 
  initialSubject = '' 
}: LmsConnectionModalProps) {
  const [selectedSubject, setSelectedSubject] = useState<string>(initialSubject || (subjects.length > 0 ? subjects[0] : 'QUIM101'));
  const [selectedPlatform, setSelectedPlatform] = useState<'moodle' | 'classroom' | 'teams'>('moodle');
  const [isExporting, setIsExporting] = useState(false);
  const [exportSuccess, setExportSuccess] = useState(false);

  if (!isOpen) return null;

  const handleDownload = () => {
    const subj = selectedSubject || 'QUIM101';
    setIsExporting(true);
    window.open(`/api/lms/export-feedback/${encodeURIComponent(subj)}?target_lms=${selectedPlatform}`, '_blank');
    setTimeout(() => {
      setIsExporting(false);
      setExportSuccess(true);
      setTimeout(() => setExportSuccess(false), 4000);
    }, 1000);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-xs p-4 animate-in fade-in duration-200">
      <div className="bg-white w-full max-w-3xl rounded-3xl shadow-2xl border border-[#E2DDD5] overflow-hidden flex flex-col max-h-[90vh]">
        {/* Modal Header */}
        <div className="bg-[#FAF8F5] px-6 py-4 border-b border-[#E8E3DA] flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-2xl bg-indigo-600 text-white flex items-center justify-center shadow-xs">
              <Share2 className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-[10px] font-bold tracking-wider uppercase text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded-full border border-indigo-200">
                  Conexión & Sincronización
                </span>
                <span className="text-[10px] text-slate-400 font-medium">• Interoperabilidad Soberana</span>
              </div>
              <h2 className="text-lg font-bold font-editorial text-slate-900">
                Vincular con Plataformas LMS (Moodle, Classroom, Teams)
              </h2>
            </div>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-full hover:bg-slate-200 text-slate-400 hover:text-slate-700 flex items-center justify-center transition cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 overflow-y-auto space-y-6 text-xs text-slate-700">
          {/* Explicación Pedagógica del Método de Vinculación */}
          <div className="p-4 rounded-2xl bg-indigo-50/70 border border-indigo-200">
            <div className="flex items-start gap-2.5">
              <ShieldCheck className="w-5 h-5 text-indigo-700 flex-shrink-0 mt-0.5" />
              <div>
                <h4 className="font-bold text-indigo-950 text-sm mb-1">
                  ¿Cómo se conecta Carpeta Pedagógica 2.0 con tu plataforma educativa?
                </h4>
                <p className="text-indigo-900 leading-relaxed font-serif-warm">
                  Nos vinculamos mediante <strong>interoperabilidad de datos de grado institucional</strong> (Gradebook Data Exchange). 
                  En lugar de exigirte contraseñas universitarias o tokens de API en la nube (que a menudo violan las políticas de seguridad de los campus), el sistema procesa las planillas exportadas desde tu LMS, calcula los diagnósticos DUA y analíticos de forma <strong>100% local</strong>, y te genera la planilla formateada lista para <strong>reimportar masivamente las devoluciones formativas en segundos</strong>.
                </p>
              </div>
            </div>
          </div>

          {/* Selector de Plataforma */}
          <div>
            <label className="font-bold text-slate-900 text-xs block mb-2 uppercase tracking-wider">
              1. Selecciona la plataforma donde gestionas tu asignatura:
            </label>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              {/* Moodle */}
              <button
                type="button"
                onClick={() => setSelectedPlatform('moodle')}
                className={`p-4 rounded-2xl border text-left transition cursor-pointer relative ${
                  selectedPlatform === 'moodle'
                    ? 'bg-amber-50/80 border-amber-400 ring-2 ring-amber-400/40'
                    : 'bg-[#FAF8F5] border-[#E8E3DA] hover:border-slate-300'
                }`}
              >
                <div className="flex items-center justify-between mb-1.5">
                  <span className="font-bold text-amber-950 text-sm flex items-center gap-1.5">
                    <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></span>
                    Moodle LMS
                  </span>
                  <span className="text-[10px] font-mono bg-amber-100 text-amber-900 font-bold px-1.5 py-0.5 rounded">
                    CSV UTF-8
                  </span>
                </div>
                <p className="text-[11px] text-slate-600 leading-snug mb-2">
                  Compatible con el Libro de Calificaciones de Moodle 3.x y 4.x.
                </p>
                <div className="text-[10px] text-amber-800 font-semibold bg-white/80 p-1.5 rounded-lg border border-amber-200/80">
                  Mapeo por: <code>Número de ID</code> o correo.
                </div>
              </button>

              {/* Classroom */}
              <button
                type="button"
                onClick={() => setSelectedPlatform('classroom')}
                className={`p-4 rounded-2xl border text-left transition cursor-pointer relative ${
                  selectedPlatform === 'classroom'
                    ? 'bg-emerald-50/80 border-emerald-400 ring-2 ring-emerald-400/40'
                    : 'bg-[#FAF8F5] border-[#E8E3DA] hover:border-slate-300'
                }`}
              >
                <div className="flex items-center justify-between mb-1.5">
                  <span className="font-bold text-emerald-950 text-sm flex items-center gap-1.5">
                    <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></span>
                    Google Classroom
                  </span>
                  <span className="text-[10px] font-mono bg-emerald-100 text-emerald-900 font-bold px-1.5 py-0.5 rounded">
                    CSV Google
                  </span>
                </div>
                <p className="text-[11px] text-slate-600 leading-snug mb-2">
                  Descarga y subida de tareas en Google Workspace for Education.
                </p>
                <div className="text-[10px] text-emerald-800 font-semibold bg-white/80 p-1.5 rounded-lg border border-emerald-200/80">
                  Mapeo por: Correo institucional.
                </div>
              </button>

              {/* Teams */}
              <button
                type="button"
                onClick={() => setSelectedPlatform('teams')}
                className={`p-4 rounded-2xl border text-left transition cursor-pointer relative ${
                  selectedPlatform === 'teams'
                    ? 'bg-indigo-50/80 border-indigo-400 ring-2 ring-indigo-400/40'
                    : 'bg-[#FAF8F5] border-[#E8E3DA] hover:border-slate-300'
                }`}
              >
                <div className="flex items-center justify-between mb-1.5">
                  <span className="font-bold text-indigo-950 text-sm flex items-center gap-1.5">
                    <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></span>
                    Microsoft Teams
                  </span>
                  <span className="text-[10px] font-mono bg-indigo-100 text-indigo-900 font-bold px-1.5 py-0.5 rounded">
                    Excel .xlsx
                  </span>
                </div>
                <p className="text-[11px] text-slate-600 leading-snug mb-2">
                  Compatible con la pestaña Notas y Tareas de Teams Educación.
                </p>
                <div className="text-[10px] text-indigo-800 font-semibold bg-white/80 p-1.5 rounded-lg border border-indigo-200/80">
                  Mapeo por: Nombre y email de Teams.
                </div>
              </button>
            </div>
          </div>

          {/* Pasos Prácticos de Conexión */}
          <div className="p-5 rounded-2xl bg-[#FAF8F5] border border-[#E8E3DA]">
            <h4 className="font-bold text-slate-900 text-xs uppercase tracking-wider mb-3 flex items-center gap-1.5">
              <Info className="w-4 h-4 text-indigo-600" />
              2. Pasos para completar la vinculación:
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-white p-3.5 rounded-xl border border-[#E8E3DA]">
                <span className="font-bold text-slate-800 block mb-1 text-xs">
                  Paso A: Desde tu LMS hacia la App (Ingesta)
                </span>
                <p className="text-[11px] text-slate-500 leading-relaxed font-serif-warm">
                  {selectedPlatform === 'moodle' && 'En Moodle: Calificaciones > Exportar > Hoja de cálculo de texto plano (CSV). Luego súbela en la columna izquierda de la app.'}
                  {selectedPlatform === 'classroom' && 'En Classroom: Abre cualquier tarea entregada > icono de engranaje ⚙ > "Descargar todas las calificaciones como CSV". Súbela en la app.'}
                  {selectedPlatform === 'teams' && 'En Teams: En el equipo de clase > pestaña Notas (Grades) > "Exportar a Excel". Sube el archivo Grades.xlsx en la app.'}
                </p>
              </div>

              <div className="bg-white p-3.5 rounded-xl border border-[#E8E3DA]">
                <span className="font-bold text-slate-800 block mb-1 text-xs">
                  Paso B: Desde la App hacia tu LMS (Devolución Masiva)
                </span>
                <p className="text-[11px] text-slate-500 leading-relaxed font-serif-warm">
                  {selectedPlatform === 'moodle' && 'Descarga la planilla formateada abajo. En Moodle: Calificaciones > Importar > Archivo CSV. Mapea "Número de ID" y "Comentarios de retroalimentación". ¡Listo!'}
                  {selectedPlatform === 'classroom' && 'Descarga la planilla abajo con los comentarios DUA y notas estructuradas para importar o pegar directamente en tu hoja de evaluación.'}
                  {selectedPlatform === 'teams' && 'Descarga el archivo Excel abajo formateado para sincronizar notas y observaciones en las tareas creadas en Microsoft Teams.'}
                </p>
              </div>
            </div>
          </div>

          {/* Descarga / Generación Inmediata */}
          <div className="bg-slate-900 text-white p-5 rounded-2xl flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4">
            <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3">
              <div>
                <span className="text-[10px] uppercase font-bold text-amber-400 block tracking-wider">
                  Asignatura a Sincronizar:
                </span>
                {subjects.length > 0 ? (
                  <select
                    value={selectedSubject}
                    onChange={(e) => setSelectedSubject(e.target.value)}
                    className="bg-slate-800 border border-slate-700 text-amber-300 font-bold text-xs px-3 py-1.5 rounded-xl outline-none mt-1"
                  >
                    {subjects.map((s) => (
                      <option key={s} value={s}>{s}</option>
                    ))}
                  </select>
                ) : (
                  <span className="font-bold text-xs text-amber-300 mt-1 block">
                    {selectedSubject || 'QUIM101'}
                  </span>
                )}
              </div>
            </div>

            <button
              type="button"
              onClick={handleDownload}
              disabled={isExporting}
              className="bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold px-5 py-2.5 rounded-xl text-xs transition shadow-md flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50 whitespace-nowrap"
            >
              <Download className="w-4 h-4 text-slate-950" />
              {isExporting ? 'Generando archivo...' : `Descargar Planilla para ${selectedPlatform.toUpperCase()}`}
            </button>
          </div>

          {exportSuccess && (
            <div className="p-3 rounded-xl bg-emerald-50 text-emerald-800 border border-emerald-200 flex items-center gap-2 animate-in fade-in duration-150">
              <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
              <span className="font-semibold text-xs">
                ¡Planilla para {selectedPlatform.toUpperCase()} generada y descargada exitosamente! Puedes reimportarla en tu plataforma.
              </span>
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="bg-[#FAF8F5] px-6 py-3 border-t border-[#E8E3DA] flex items-center justify-between">
          <span className="text-[11px] text-slate-400">
            Privacidad garantizada: Sin envío de contraseñas ni credenciales a servidores externos.
          </span>
          <button
            onClick={onClose}
            className="text-xs font-bold text-slate-700 hover:bg-slate-200 px-4 py-2 rounded-xl transition cursor-pointer"
          >
            Cerrar
          </button>
        </div>
      </div>
    </div>
  );
}
