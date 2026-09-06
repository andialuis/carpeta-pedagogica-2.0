'use client';
import { useState, useEffect } from 'react';
import { 
  Settings, Server, Cpu, Database, HardDrive, 
  Download, Trash2, CheckCircle2, ShieldCheck, Sparkles, 
  RefreshCw, Info, Key, ShieldAlert, Share2, FileSpreadsheet
} from 'lucide-react';
import GeminiConfigModal from '../components/GeminiConfigModal';

export default function AdministracionPage() {
  const [stats, setStats] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isGeminiModalOpen, setIsGeminiModalOpen] = useState(false);
  const [cacheMessage, setCacheMessage] = useState<string | null>(null);
  const [targetLms, setTargetLms] = useState<'moodle' | 'classroom' | 'teams'>('moodle');
  const [selectedSubject, setSelectedSubject] = useState<string>('');

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    setIsLoading(true);
    try {
      const res = await fetch('/api/system/stats', { cache: 'no-store' });
      if (res.ok) {
        const data = await res.json();
        setStats(data);
        if (data.materias && data.materias.length > 0) {
          setSelectedSubject((prev) => prev || data.materias[0]);
        }
      }
    } catch (e) {
      console.error("Error al obtener estadísticas del sistema");
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearCache = async () => {
    try {
      const res = await fetch('/api/system/clear-cache', { method: 'POST' });
      const data = await res.json();
      setCacheMessage(data.message || "Caché limpiada");
      setTimeout(() => setCacheMessage(null), 3500);
      fetchStats();
    } catch (e) {
      alert("Error al limpiar la caché");
    }
  };

  return (
    <div className="text-slate-800 pb-16 font-sans-clean max-w-5xl mx-auto">
      {/* Header */}
      <header className="mb-8 border-b border-[#E8E3DA] pb-5">
        <div className="flex items-center gap-2 mb-1">
          <span className="text-[10px] font-bold tracking-widest uppercase text-slate-800 bg-slate-200/80 px-2.5 py-0.5 rounded-full border border-slate-300">
            Control de Sistema
          </span>
          <span className="text-[10px] font-medium text-slate-400">• v1.0 Personal Edition</span>
        </div>
        <h1 className="text-3xl font-bold font-editorial text-slate-900 flex items-center gap-3">
          <Settings className="w-8 h-8 text-slate-800" />
          Módulo de Administración de la App Web
        </h1>
        <p className="text-slate-500 text-sm mt-0.5">
          Monitor de infraestructura local, gestión de inteligencia artificial, respaldos y almacenamiento
        </p>
      </header>

      <div className="space-y-6">
        {/* Monitor de Salud de la Plataforma */}
        <div className="bg-white p-6 sm:p-8 rounded-3xl shadow-atelier border border-[#E2DDD5]">
          <div className="flex items-center justify-between border-b border-[#EFEAE1] pb-4 mb-6">
            <div>
              <h2 className="text-lg font-bold font-editorial text-slate-900 flex items-center gap-2">
                <Server className="w-5 h-5 text-indigo-700" />
                Monitor de Salud y Estado de Servicios
              </h2>
              <p className="text-xs text-slate-500 font-medium">
                Infraestructura cliente-servidor ejecutándose de forma local y soberana
              </p>
            </div>
            <button
              onClick={fetchStats}
              className="text-xs bg-[#FAF8F5] hover:bg-slate-100 text-slate-700 px-3 py-1.5 rounded-xl border border-[#DDD7CD] font-semibold flex items-center gap-1.5 transition cursor-pointer shadow-2xs"
            >
              <RefreshCw className={`w-3.5 h-3.5 text-slate-500 ${isLoading ? 'animate-spin' : ''}`} /> Refrescar Estado
            </button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="p-4 rounded-2xl bg-[#FAF8F5] border border-[#E8E3DA]">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-bold text-slate-700">Backend FastAPI</span>
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></span>
              </div>
              <p className="text-base font-bold font-mono text-emerald-800">127.0.0.1:8000</p>
              <span className="text-[10px] text-slate-400 mt-1 block">Python 3.14 Uvicorn</span>
            </div>

            <div className="p-4 rounded-2xl bg-[#FAF8F5] border border-[#E8E3DA]">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-bold text-slate-700">Frontend Next.js</span>
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></span>
              </div>
              <p className="text-base font-bold font-mono text-emerald-800">localhost:3001</p>
              <span className="text-[10px] text-slate-400 mt-1 block">Next.js 16 + React 19</span>
            </div>

            <div className="p-4 rounded-2xl bg-[#FAF8F5] border border-[#E8E3DA]">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-bold text-slate-700">Materias Activas</span>
                <Database className="w-4 h-4 text-amber-700" />
              </div>
              <p className="text-2xl font-bold font-editorial text-slate-900">
                {stats?.total_materias || 0}
              </p>
              <span className="text-[10px] text-slate-400 mt-1 block">
                {stats?.total_archivos || 0} archivos en disco
              </span>
            </div>

            <div className="p-4 rounded-2xl bg-[#FAF8F5] border border-[#E8E3DA]">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-bold text-slate-700">Almacenamiento</span>
                <HardDrive className="w-4 h-4 text-purple-700" />
              </div>
              <p className="text-2xl font-bold font-editorial text-slate-900">
                {stats?.espacio_utilizado_mb || 0} <span className="text-xs font-sans-clean font-semibold text-slate-500">MB</span>
              </p>
              <span className="text-[10px] text-slate-400 mt-1 block">Directorio uploads/</span>
            </div>
          </div>
        </div>

        {/* Panel de Gestión de Inteligencia Artificial */}
        <div className="bg-white p-6 sm:p-8 rounded-3xl shadow-atelier border border-[#E2DDD5]">
          <div className="flex items-center justify-between border-b border-[#EFEAE1] pb-4 mb-6">
            <div>
              <h2 className="text-lg font-bold font-editorial text-slate-900 flex items-center gap-2">
                <Cpu className="w-5 h-5 text-amber-700" />
                Motor de Inteligencia Artificial & Costos
              </h2>
              <p className="text-xs text-slate-500 font-medium">
                Configuración del modelo de Google AI Studio y salvaguarda determinista
              </p>
            </div>
            <button
              onClick={() => setIsGeminiModalOpen(true)}
              className="text-xs bg-slate-900 hover:bg-slate-800 text-amber-300 font-bold px-4 py-2 rounded-xl transition shadow-xs flex items-center gap-1.5 cursor-pointer"
            >
              <Key className="w-3.5 h-3.5 text-amber-400" /> Configurar Clave / Modelo
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
            <div className="p-4 rounded-2xl bg-[#FAF8F5] border border-[#E8E3DA]">
              <span className="font-bold text-slate-700 block mb-1">Modelo Seleccionado:</span>
              <span className="font-mono text-xs font-bold text-slate-900 bg-white px-2.5 py-1 rounded-lg border border-[#DDD7CD] inline-block">
                {stats?.gemini_modelo || 'gemini-3.5-flash-lite'}
              </span>
              <p className="text-[10px] text-slate-500 mt-2">
                Modelo flash optimizado para structured output y baja latencia.
              </p>
            </div>

            <div className="p-4 rounded-2xl bg-emerald-50/70 border border-emerald-200">
              <span className="font-bold text-emerald-950 block mb-1">Costo Estimado de la API:</span>
              <span className="font-mono text-sm font-bold text-emerald-800 bg-white px-2.5 py-1 rounded-lg border border-emerald-300 inline-block">
                $0.00 USD (Nivel Gratuito)
              </span>
              <p className="text-[10px] text-emerald-800/80 mt-2">
                Operando bajo la cuota libre de Google AI Studio sin cobro por tokens.
              </p>
            </div>

            <div className="p-4 rounded-2xl bg-amber-50/70 border border-amber-200">
              <span className="font-bold text-amber-950 block mb-1">Alta Disponibilidad:</span>
              <span className="font-bold text-amber-900 bg-white px-2.5 py-1 rounded-lg border border-amber-300 inline-block">
                Resiliencia Activa
              </span>
              <p className="text-[10px] text-amber-900/80 mt-2">
                Si la API reporta congestión temporal (503), el sistema conmuta automáticamente a la contingencia local.
              </p>
            </div>
          </div>
        </div>

        {/* Mantenimiento, Respaldos y Limpieza */}
        <div className="bg-white p-6 sm:p-8 rounded-3xl shadow-atelier border border-[#E2DDD5]">
          <h2 className="text-lg font-bold font-editorial text-slate-900 mb-2 flex items-center gap-2">
            <HardDrive className="w-5 h-5 text-purple-700" />
            Mantenimiento y Respaldo Integral
          </h2>
          <p className="text-xs text-slate-500 mb-6 font-medium">
            Exporta tus bases de datos o realiza tareas de limpieza periódica de archivos temporales:
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="p-5 rounded-2xl bg-[#FAF8F5] border border-[#E8E3DA] flex flex-col justify-between">
              <div>
                <h4 className="text-sm font-bold text-slate-900 mb-1">Copia de Seguridad (.ZIP)</h4>
                <p className="text-xs text-slate-500 mb-4 leading-relaxed">
                  Descarga un archivo comprimido conteniendo todas las materias, expedientes REV, planes curriculares y datasets.
                </p>
              </div>
              <button
                onClick={() => window.open('/api/system/backup', '_blank')}
                className="bg-slate-900 hover:bg-slate-800 text-amber-300 font-bold px-4 py-2.5 rounded-xl text-xs transition shadow-xs flex items-center justify-center gap-2 cursor-pointer"
              >
                <Download className="w-4 h-4 text-amber-400" />
                Descargar Backup Completo (.zip)
              </button>
            </div>

            <div className="p-5 rounded-2xl bg-[#FAF8F5] border border-[#E8E3DA] flex flex-col justify-between">
              <div>
                <h4 className="text-sm font-bold text-slate-900 mb-1">Limpieza de Archivos Temporales</h4>
                <p className="text-xs text-slate-500 mb-4 leading-relaxed">
                  Purga la carpeta temporal de scripts de prueba (`scratch/`) y libera espacio en disco sin alterar los expedientes de materias.
                </p>
              </div>
              <div className="flex flex-col gap-2">
                {cacheMessage && (
                  <span className="text-[11px] font-bold text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-lg border border-emerald-200">
                    {cacheMessage}
                  </span>
                )}
                <button
                  onClick={handleClearCache}
                  className="bg-white hover:bg-rose-50 text-rose-700 border border-rose-300 font-bold px-4 py-2.5 rounded-xl text-xs transition shadow-2xs flex items-center justify-center gap-2 cursor-pointer"
                >
                  <Trash2 className="w-4 h-4 text-rose-600" />
                  Vaciar Archivos Temporales
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Centro de Interoperabilidad y Conexión LMS */}
        <div className="bg-white p-6 sm:p-8 rounded-3xl shadow-atelier border border-[#E2DDD5]">
          <div className="flex items-center justify-between border-b border-[#EFEAE1] pb-4 mb-6">
            <div>
              <h2 className="text-lg font-bold font-editorial text-slate-900 flex items-center gap-2">
                <Share2 className="w-5 h-5 text-indigo-700" />
                Centro de Interoperabilidad LMS (Moodle • Google Classroom • MS Teams)
              </h2>
              <p className="text-xs text-slate-500 font-medium">
                Exporta planillas de retroalimentación formativa y adaptaciones DUA formateadas para su reimportación directa a plataformas educativas
              </p>
            </div>
            <span className="text-[10px] font-bold bg-indigo-50 text-indigo-800 px-2.5 py-1 rounded-lg border border-indigo-200">
              Interoperabilidad Soberana
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <button
              type="button"
              onClick={() => setTargetLms('moodle')}
              className={`p-4 rounded-2xl border text-left transition cursor-pointer ${
                targetLms === 'moodle'
                  ? 'bg-amber-50/70 border-amber-400 ring-2 ring-amber-400/30'
                  : 'bg-[#FAF8F5] border-[#E8E3DA] hover:border-slate-300'
              }`}
            >
              <div className="flex items-center justify-between mb-1.5">
                <span className="text-xs font-bold text-amber-900">Moodle LMS</span>
                <span className="text-[10px] font-mono bg-amber-100 text-amber-800 px-2 py-0.5 rounded font-bold">CSV UTF-8</span>
              </div>
              <p className="text-[11px] text-slate-600 leading-snug">
                Formato con columnas nativas <code>Número de ID</code>, <code>Calificación</code> y <code>Comentarios de retroalimentación</code> para el calificador de Moodle.
              </p>
            </button>

            <button
              type="button"
              onClick={() => setTargetLms('classroom')}
              className={`p-4 rounded-2xl border text-left transition cursor-pointer ${
                targetLms === 'classroom'
                  ? 'bg-emerald-50/70 border-emerald-400 ring-2 ring-emerald-400/30'
                  : 'bg-[#FAF8F5] border-[#E8E3DA] hover:border-slate-300'
              }`}
            >
              <div className="flex items-center justify-between mb-1.5">
                <span className="text-xs font-bold text-emerald-900">Google Classroom</span>
                <span className="text-[10px] font-mono bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded font-bold">CSV</span>
              </div>
              <p className="text-[11px] text-slate-600 leading-snug">
                Planilla estructurada para calificaciones numéricas y retroalimentación personalizada de entregas y tareas por correo institucional.
              </p>
            </button>

            <button
              type="button"
              onClick={() => setTargetLms('teams')}
              className={`p-4 rounded-2xl border text-left transition cursor-pointer ${
                targetLms === 'teams'
                  ? 'bg-indigo-50/70 border-indigo-400 ring-2 ring-indigo-400/30'
                  : 'bg-[#FAF8F5] border-[#E8E3DA] hover:border-slate-300'
              }`}
            >
              <div className="flex items-center justify-between mb-1.5">
                <span className="text-xs font-bold text-indigo-900">Microsoft Teams</span>
                <span className="text-[10px] font-mono bg-indigo-100 text-indigo-800 px-2 py-0.5 rounded font-bold">Excel (.xlsx)</span>
              </div>
              <p className="text-[11px] text-slate-600 leading-snug">
                Libro Excel compatible con el módulo de Tareas y Asignaciones de Teams Educación para sincronización de notas y feedback.
              </p>
            </button>
          </div>

          <div className="bg-[#FAF8F5] p-4 rounded-2xl border border-[#E8E3DA] flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4">
            <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3">
              <label className="text-xs font-bold text-slate-700 whitespace-nowrap">
                Materia a exportar:
              </label>
              {stats?.materias && stats.materias.length > 0 ? (
                <select
                  value={selectedSubject}
                  onChange={(e) => setSelectedSubject(e.target.value)}
                  className="bg-white border border-[#DDD7CD] text-xs font-bold text-slate-800 px-3 py-2 rounded-xl outline-none focus:border-slate-500"
                >
                  {stats.materias.map((m: string) => (
                    <option key={m} value={m}>{m}</option>
                  ))}
                </select>
              ) : (
                <input
                  type="text"
                  value={selectedSubject}
                  onChange={(e) => setSelectedSubject(e.target.value)}
                  placeholder="Ej: QUIM101"
                  className="bg-white border border-[#DDD7CD] text-xs font-bold text-slate-800 px-3 py-2 rounded-xl outline-none focus:border-slate-500"
                />
              )}
              <span className="text-[11px] text-slate-500">
                LMS Destino: <strong className="text-slate-800 uppercase">{targetLms}</strong>
              </span>
            </div>

            <button
              onClick={() => {
                const sub = selectedSubject || (stats?.materias && stats.materias[0]) || 'QUIM101';
                window.open(`/api/lms/export-feedback/${encodeURIComponent(sub)}?target_lms=${targetLms}`, '_blank');
              }}
              className="bg-indigo-900 hover:bg-indigo-800 text-white font-bold px-4 py-2.5 rounded-xl text-xs transition shadow-xs flex items-center justify-center gap-2 cursor-pointer whitespace-nowrap"
            >
              <Download className="w-4 h-4 text-indigo-300" />
              Descargar Planilla para {targetLms.toUpperCase()}
            </button>
          </div>
        </div>

        {/* Ficha de Autoría y Licenciamiento Institucional */}
        <div className="bg-gradient-to-br from-slate-900 to-indigo-950 text-white p-6 sm:p-8 rounded-3xl shadow-atelier">
          <div className="flex items-center gap-2 mb-2 text-amber-400">
            <ShieldCheck className="w-6 h-6" />
            <h3 className="text-lg font-bold font-editorial">
              Ficha Técnica & Autoría de la Plataforma
            </h3>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed mb-4 font-serif-warm">
            Carpeta Pedagógica 2.0 es un sistema de gestión documental y analítica de aprendizaje humanista diseñado para empoderar al docente en el diseño curricular auténtico (CBL) y la inclusión (DUA marco CAST 2024), garantizando la soberanía de datos y la prevención del outsourcing cognitivo.
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs bg-white/10 p-4 rounded-2xl border border-white/10">
            <div>
              <span className="text-slate-400 block text-[10px] uppercase font-bold tracking-wider">Creador y Autor:</span>
              <strong className="text-amber-300 text-sm block">Luis Alfredo Andia Valverde</strong>
              <span className="text-slate-300 text-[11px]">luis.andia.valverde@gmail.com</span>
            </div>
            <div>
              <span className="text-slate-400 block text-[10px] uppercase font-bold tracking-wider">Versión del Sistema:</span>
              <strong className="text-white text-sm">1.0.0 (Personal & Educational)</strong>
            </div>
            <div>
              <span className="text-slate-400 block text-[10px] uppercase font-bold tracking-wider">Licencia de Uso:</span>
              <strong className="text-emerald-300 text-xs">Uso y Distribución Libre No Comercial (CC BY-NC 4.0)</strong>
            </div>
          </div>
        </div>
      </div>

      <GeminiConfigModal
        isOpen={isGeminiModalOpen}
        onClose={() => setIsGeminiModalOpen(false)}
        onStatusChange={fetchStats}
      />
    </div>
  );
}
