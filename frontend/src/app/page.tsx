'use client';
import { useState, useEffect } from 'react';
import { 
  FileSpreadsheet, PlusCircle, BrainCircuit, FolderTree, 
  Bot, Activity, Award, FileText, ArrowRight, Sparkles, 
  UploadCloud, RefreshCw, CheckCircle2, ShieldCheck, ChevronRight, FileDown, Share2
} from 'lucide-react';
import LmsConnectionModal from './components/LmsConnectionModal';

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [aiResult, setAiResult] = useState<any>(null);
  const [confirmed, setConfirmed] = useState(false);
  const [pendingFiles, setPendingFiles] = useState<any[]>([]);
  const [selectedLms, setSelectedLms] = useState<'standard' | 'moodle' | 'classroom' | 'teams'>('standard');
  const [isLmsModalOpen, setIsLmsModalOpen] = useState(false);
  const [lmsModalSubject, setLmsModalSubject] = useState('');

  useEffect(() => {
    fetchPendingFiles();
  }, []);

  const fetchPendingFiles = async () => {
    try {
      const res = await fetch('/api/documents/pending', { cache: 'no-store' });
      const data = await res.json();
      setPendingFiles(data.subjects || []);
    } catch (e) {
      console.error("No se pudo conectar al backend.");
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
      setAiResult(null);
      setConfirmed(false);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('/api/documents/analyze-spreadsheet', {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      setAiResult(data.ai_analysis);
    } catch (error) {
      alert('Error de conexión con el backend.');
    }
    setLoading(false);
  };

  const handleAnalyzeLocal = async (path: string) => {
    setLoading(true);
    setAiResult(null);
    setConfirmed(false);
    try {
      const res = await fetch(`/api/documents/analyze-local?filepath=${encodeURIComponent(path)}`, {
        method: 'POST',
      });
      const data = await res.json();
      setAiResult(data.ai_analysis);
    } catch (error) {
      alert('Error de conexión.');
    }
    setLoading(false);
  };

  const handleConfirm = () => {
    setConfirmed(true);
    alert('Estructura confirmada. Datos sincronizados con el ecosistema de analítica.');
  };

  // Pasos de la lógica de trabajo
  const workflowSteps = [
    { num: '1', title: 'Crear Clase', desc: 'Ingesta de planillas y creación', path: '/', active: true, icon: <PlusCircle className="w-4 h-4" /> },
    { num: '2', title: 'Planificar', desc: 'Diseño curricular por competencias', path: '/planificacion', active: false, icon: <BrainCircuit className="w-4 h-4" /> },
    { num: '3', title: 'Organizar', desc: 'Expedientes y carpetas REV', path: '/organizar', active: false, icon: <FolderTree className="w-4 h-4" /> },
    { num: '4', title: 'Flujo de Agentes', desc: '4 etapas de analítica de datos', path: '/agents', active: false, icon: <Bot className="w-4 h-4" /> },
    { num: '5', title: 'Tablero de Control', desc: 'Métricas, Gauss e insights IA', path: '/analytics', active: false, icon: <Activity className="w-4 h-4" /> },
    { num: '6', title: 'Evaluación', desc: 'Rúbricas CBL, DUA y Dossier', path: '/evaluacion', active: false, icon: <Award className="w-4 h-4" /> },
  ];

  return (
    <div className="text-slate-800 pb-16 font-sans-clean">
      {/* Encabezado Principal */}
      <header className="mb-6 flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-[#E8E3DA] pb-5">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-[10px] font-bold tracking-widest uppercase text-amber-800 bg-amber-100/80 px-2.5 py-0.5 rounded-full border border-amber-300">
              Paso 1 del Flujo Pedagógico
            </span>
            <span className="text-[10px] font-medium text-slate-400">• Ingesta & Creación de Clase</span>
          </div>
          <h1 className="text-3xl font-bold font-editorial text-slate-900 flex items-center gap-3">
            Carpeta Pedagógica 2.0
          </h1>
          <p className="text-slate-500 text-sm mt-0.5">
            Plataforma docente integral: diseño curricular, analítica humanista, DUA y expedientes
          </p>
        </div>
        <div className="flex items-center gap-2.5 flex-wrap">
          <a 
            href="/materias/nueva" 
            className="bg-slate-900 hover:bg-slate-800 text-amber-300 text-xs font-bold px-4 py-2.5 rounded-xl transition shadow-xs flex items-center gap-1.5"
          >
            <PlusCircle className="w-3.5 h-3.5 text-amber-400" />
            Crear Nueva Materia
          </a>
          <a
            href="/documentacion"
            className="bg-white hover:bg-slate-50 text-slate-700 border border-[#DDD7CD] text-xs font-semibold px-3 py-2 rounded-xl transition shadow-2xs flex items-center gap-1.5"
          >
            <FileText className="w-3.5 h-3.5 text-slate-500" />
            Manual de Uso
          </a>
        </div>
      </header>

      {/* Barra de Flujo Pedagógico Secuencial */}
      <section className="mb-8 bg-white border border-[#E8E3DA] p-3.5 rounded-2xl shadow-2xs">
        <div className="flex items-center justify-between mb-2.5 px-2">
          <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5 text-amber-600" /> Secuencia Didáctica de la Plataforma
          </span>
          <span className="text-[10px] font-medium text-slate-400">Paso 1 activo</span>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2">
          {workflowSteps.map((step) => (
            <a
              key={step.num}
              href={step.path}
              className={`p-2.5 rounded-xl border transition flex flex-col justify-between ${
                step.active
                  ? 'bg-slate-900 text-white border-slate-800 shadow-xs'
                  : 'bg-[#FAF8F5]/80 hover:bg-white text-slate-700 border-[#E8E3DA] hover:border-amber-400/60'
              }`}
            >
              <div className="flex items-center justify-between mb-1">
                <span className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-mono font-bold ${
                  step.active ? 'bg-amber-400 text-slate-950' : 'bg-slate-200 text-slate-700'
                }`}>
                  {step.num}
                </span>
                <span className={step.active ? 'text-amber-400' : 'text-slate-400'}>
                  {step.icon}
                </span>
              </div>
              <div>
                <h4 className="text-xs font-bold truncate">{step.title}</h4>
                <p className={`text-[10px] truncate ${step.active ? 'text-slate-300' : 'text-slate-400'}`}>
                  {step.desc}
                </p>
              </div>
            </a>
          ))}
        </div>
      </section>

      {/* Grid Principal con Distribución Eficiente de Espacios */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        
        {/* Columna Lateral Izquierda (4 columnas): Ingesta compacta y Acciones Rápidas */}
        <div className="lg:col-span-4 space-y-5">
          {/* Tarjeta Compacta de Subida de Archivo */}
          <div className="bg-white p-5 rounded-2xl shadow-atelier border border-[#E2DDD5]">
            <div className="flex items-center justify-between border-b border-[#EFEAE1] pb-3 mb-3">
              <div className="flex items-center gap-2">
                <UploadCloud className="w-4 h-4 text-amber-700" />
                <h2 className="text-base font-bold font-editorial text-slate-900">Subir Archivo de Clase</h2>
              </div>
              <span className="text-[10px] bg-slate-100 text-slate-600 px-2 py-0.5 rounded font-mono font-semibold">
                .xlsx / .csv
              </span>
            </div>

            {/* Selector de Origen LMS */}
            <div className="mb-3">
              <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block mb-1">
                Origen de Planilla / Formato LMS:
              </label>
              <div className="grid grid-cols-2 gap-1.5 text-[10px]">
                <button
                  type="button"
                  onClick={() => setSelectedLms('standard')}
                  className={`p-1.5 rounded-lg border text-left font-semibold transition cursor-pointer flex items-center gap-1.5 ${
                    selectedLms === 'standard'
                      ? 'bg-slate-900 text-white border-slate-900'
                      : 'bg-white text-slate-600 border-[#DDD7CD] hover:bg-slate-50'
                  }`}
                >
                  <span>📁</span> Excel Estándar
                </button>
                <button
                  type="button"
                  onClick={() => setSelectedLms('moodle')}
                  className={`p-1.5 rounded-lg border text-left font-semibold transition cursor-pointer flex items-center gap-1.5 ${
                    selectedLms === 'moodle'
                      ? 'bg-amber-600 text-white border-amber-600 shadow-2xs'
                      : 'bg-white text-slate-600 border-[#DDD7CD] hover:bg-slate-50'
                  }`}
                >
                  <span>🟠</span> Moodle LMS
                </button>
                <button
                  type="button"
                  onClick={() => setSelectedLms('classroom')}
                  className={`p-1.5 rounded-lg border text-left font-semibold transition cursor-pointer flex items-center gap-1.5 ${
                    selectedLms === 'classroom'
                      ? 'bg-emerald-600 text-white border-emerald-600 shadow-2xs'
                      : 'bg-white text-slate-600 border-[#DDD7CD] hover:bg-slate-50'
                  }`}
                >
                  <span>🟢</span> Classroom
                </button>
                <button
                  type="button"
                  onClick={() => setSelectedLms('teams')}
                  className={`p-1.5 rounded-lg border text-left font-semibold transition cursor-pointer flex items-center gap-1.5 ${
                    selectedLms === 'teams'
                      ? 'bg-purple-600 text-white border-purple-600 shadow-2xs'
                      : 'bg-white text-slate-600 border-[#DDD7CD] hover:bg-slate-50'
                  }`}
                >
                  <span>🟣</span> MS Teams
                </button>
              </div>
              <p className="text-[9px] text-slate-400 mt-1 italic">
                {selectedLms === 'moodle' && '💡 Compatible con: Calificaciones > Exportar > Hoja de cálculo Excel / CSV'}
                {selectedLms === 'classroom' && '💡 Compatible con: Calificaciones de Google Classroom descargadas a CSV'}
                {selectedLms === 'teams' && '💡 Compatible con: Exportación de Notas desde Microsoft Teams Assignments (.xlsx)'}
                {selectedLms === 'standard' && '💡 Compatible con cualquier planilla con columna de nombres y notas parciales'}
              </p>
            </div>

            <div className="border-2 border-dashed border-[#DDD7CD] bg-[#FAF8F5]/80 rounded-xl p-4 text-center hover:border-amber-500 transition">
              <input 
                type="file" 
                accept=".csv, .xlsx" 
                onChange={handleFileChange}
                className="w-full text-xs text-slate-600 file:mr-2 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-slate-900 file:text-white hover:file:bg-slate-800 cursor-pointer mb-3"
              />
              <p className="text-[11px] text-slate-400 mb-3">
                Planilla de calificaciones, asistencia o registro de aula
              </p>
              <button 
                onClick={handleUpload}
                disabled={!file || loading}
                className="w-full bg-amber-700 hover:bg-amber-800 text-white px-4 py-2.5 rounded-xl text-xs font-bold disabled:opacity-50 transition shadow-xs flex items-center justify-center gap-2 cursor-pointer"
              >
                {loading && file ? 'Analizando con Gemini...' : '✓ Analizar e Integrar'}
              </button>
            </div>
          </div>

          {/* Tarjeta de Acciones Rápidas del Atelier */}
          <div className="bg-white p-5 rounded-2xl shadow-atelier border border-[#E2DDD5]">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3">
              Acciones Rápidas
            </h3>
            <div className="space-y-2 text-xs">
              <a 
                href="/materias/nueva"
                className="w-full flex items-center justify-between p-2.5 rounded-xl bg-[#FAF8F5] hover:bg-amber-50/70 border border-[#E8E3DA] text-slate-800 font-semibold transition"
              >
                <span className="flex items-center gap-2">
                  <PlusCircle className="w-4 h-4 text-amber-600" /> Crear Expediente de Materia
                </span>
                <ChevronRight className="w-3.5 h-3.5 text-slate-400" />
              </a>
              <a 
                href="/organizar"
                className="w-full flex items-center justify-between p-2.5 rounded-xl bg-[#FAF8F5] hover:bg-indigo-50/70 border border-[#E8E3DA] text-slate-800 font-semibold transition"
              >
                <span className="flex items-center gap-2">
                  <FolderTree className="w-4 h-4 text-indigo-600" /> Organizar Archivos y REV
                </span>
                <ChevronRight className="w-3.5 h-3.5 text-slate-400" />
              </a>
              <a 
                href="/documentacion"
                className="w-full flex items-center justify-between p-2.5 rounded-xl bg-[#FAF8F5] hover:bg-emerald-50/70 border border-[#E8E3DA] text-slate-800 font-semibold transition"
              >
                <span className="flex items-center gap-2">
                  <FileText className="w-4 h-4 text-emerald-600" /> Términos y Manual de Uso
                </span>
                <ChevronRight className="w-3.5 h-3.5 text-slate-400" />
              </a>
            </div>
          </div>

          {/* Tarjeta de Licencia y Autoría */}
          <div className="bg-gradient-to-br from-[#FAF8F5] to-[#F3EFE8] p-4 rounded-2xl border border-[#E2DDD5] text-xs text-slate-600">
            <div className="flex items-center gap-2 mb-1.5 font-bold text-slate-900 font-editorial">
              <ShieldCheck className="w-4 h-4 text-amber-700" />
              <span>Carpeta Pedagógica 2.0</span>
            </div>
            <p className="text-[11px] text-slate-500 leading-relaxed mb-2">
              Desarrollada y creada por <strong className="text-slate-800">Luis Alfredo Andia Valverde</strong> (<a href="mailto:luis.andia.valverde@gmail.com" className="text-amber-800 underline font-mono text-[10px]">luis.andia.valverde@gmail.com</a>).
            </p>
            <div className="bg-white/80 p-2 rounded-lg border border-[#E8E3DA] text-[10px] text-slate-500">
              Autorizada su distribución, adaptación y uso para fines académicos y educativos <strong>sin beneficio comercial</strong>.
            </div>
          </div>
        </div>

        {/* Columna Principal Derecha (8 columnas): Materias, Expedientes y Acciones directas */}
        <div className="lg:col-span-8 space-y-5">
          <div className="bg-white p-6 rounded-2xl shadow-atelier border border-[#E2DDD5]">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 border-b border-[#EFEAE1] pb-4 mb-4">
              <div>
                <h2 className="text-xl font-bold font-editorial text-slate-900 flex items-center gap-2">
                  <FolderTree className="w-5 h-5 text-amber-700" />
                  Materias & Expedientes Activos
                </h2>
                <span className="text-xs text-slate-500 font-medium">
                  {pendingFiles.length} {pendingFiles.length === 1 ? 'materia registrada' : 'materias registradas'} en el sistema
                </span>
              </div>
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={() => {
                    setLmsModalSubject(pendingFiles.length > 0 ? pendingFiles[0].name : '');
                    setIsLmsModalOpen(true);
                  }}
                  className="text-xs bg-indigo-50 hover:bg-indigo-100 text-indigo-900 font-bold px-3 py-1.5 rounded-xl transition border border-indigo-200 flex items-center gap-1.5 cursor-pointer shadow-2xs"
                  title="Conectar y vincular con Moodle, Classroom o Teams"
                >
                  <Share2 className="w-3.5 h-3.5 text-indigo-700" />
                  🔗 Vincular LMS (Moodle / Classroom / Teams)
                </button>
                <button 
                  onClick={fetchPendingFiles} 
                  className="text-xs bg-[#FAF8F5] hover:bg-slate-100 text-slate-700 border border-[#DDD7CD] px-3 py-1.5 rounded-xl transition font-semibold flex items-center gap-1.5 cursor-pointer shadow-2xs"
                >
                  <RefreshCw className="w-3 h-3 text-slate-500" /> Refrescar
                </button>
                <a 
                  href="/materias/nueva" 
                  className="text-xs bg-amber-50 text-amber-900 font-bold px-3 py-1.5 rounded-xl hover:bg-amber-100 transition border border-amber-200"
                >
                  + Nueva Materia
                </a>
              </div>
            </div>

            {pendingFiles.length === 0 ? (
              <div className="py-12 text-center text-slate-400 font-editorial">
                <p className="text-base italic mb-2">No hay materias ni archivos detectados.</p>
                <p className="text-xs text-slate-500 font-sans-clean">
                  Carga una planilla en la columna izquierda o haz clic en "+ Nueva Materia" para comenzar.
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                {pendingFiles.map((subj: any, i: number) => {
                  const hasRev = subj.versions?.some((v: any) => v.name.includes('REV'));
                  const baseFilesCount = subj.versions?.find((v: any) => !v.name.includes('REV'))?.files?.length || 0;
                  const revFilesCount = subj.versions?.find((v: any) => v.name.includes('REV'))?.files?.length || 0;
                  return (
                    <div key={i} className="border border-[#E8E3DA] rounded-2xl overflow-hidden shadow-2xs transition hover:border-amber-300">
                      {/* Cabecera de la Materia */}
                      <div className="bg-[#FAF8F5] p-4 border-b border-[#E8E3DA] flex flex-col md:flex-row md:items-center justify-between gap-3">
                        <div className="flex items-center gap-2.5">
                          <div className="w-8 h-8 rounded-xl bg-slate-900 text-amber-400 flex items-center justify-center font-bold font-mono text-xs shadow-xs">
                            {subj.name.substring(0, 3)}
                          </div>
                          <div>
                            <h3 className="font-bold font-editorial text-slate-900 text-base leading-snug">
                              {subj.name}
                            </h3>
                            <div className="flex items-center gap-2 mt-0.5">
                              <span className={`text-[10px] font-bold px-2 py-0.2 rounded-full border ${
                                hasRev 
                                  ? 'bg-emerald-50 text-emerald-800 border-emerald-300' 
                                  : 'bg-amber-50 text-amber-800 border-amber-300'
                              }`}>
                                {hasRev ? 'Expediente REV Procesado' : 'Pendiente de Procesar'}
                              </span>
                              <span className="text-[10px] text-slate-400">•</span>
                              <span className="text-[10px] text-slate-500 font-medium">
                                {baseFilesCount + revFilesCount} archivos totales
                              </span>
                            </div>
                          </div>
                        </div>

                        {/* Barra de Acciones del Flujo por Materia */}
                        <div className="flex items-center gap-1.5 flex-wrap">
                          <a 
                            href={`/planificacion?subject=${encodeURIComponent(subj.name)}`} 
                            className="text-[11px] bg-white border border-[#DDD7CD] text-slate-700 hover:text-amber-800 hover:bg-amber-50/50 px-2.5 py-1.5 rounded-xl font-semibold shadow-2xs transition flex items-center gap-1"
                            title="Paso 2: Plan Curricular & PDC"
                          >
                            <BrainCircuit className="w-3 h-3 text-amber-700" /> Planificar
                          </a>
                          <a 
                            href={`/organizar`} 
                            className="text-[11px] bg-white border border-[#DDD7CD] text-slate-700 hover:text-indigo-800 hover:bg-indigo-50/50 px-2.5 py-1.5 rounded-xl font-semibold shadow-2xs transition flex items-center gap-1"
                            title="Paso 3: Organizar Expediente"
                          >
                            <FolderTree className="w-3 h-3 text-indigo-700" /> Organizar
                          </a>
                          <a 
                            href={`/agents?subject=${encodeURIComponent(subj.name)}`} 
                            className="text-[11px] bg-white border border-[#DDD7CD] text-slate-700 hover:text-indigo-800 hover:bg-indigo-50/50 px-2.5 py-1.5 rounded-xl font-semibold shadow-2xs transition flex items-center gap-1"
                            title="Paso 4: Flujo de Agentes IA"
                          >
                            <Bot className="w-3 h-3 text-indigo-700" /> Agentes
                          </a>
                          <a 
                            href={`/analytics?subject=${encodeURIComponent(subj.name)}`} 
                            className="text-[11px] bg-white border border-[#DDD7CD] text-slate-700 hover:text-emerald-800 hover:bg-emerald-50/50 px-2.5 py-1.5 rounded-xl font-semibold shadow-2xs transition flex items-center gap-1"
                            title="Paso 5: Tablero Analítico & Diagnóstico"
                          >
                            <Activity className="w-3 h-3 text-emerald-700" /> Métricas
                          </a>
                          <a 
                            href={`/evaluacion?subject=${encodeURIComponent(subj.name)}`} 
                            className="text-[11px] bg-white border border-[#DDD7CD] text-slate-700 hover:text-purple-800 hover:bg-purple-50/50 px-2.5 py-1.5 rounded-xl font-semibold shadow-2xs transition flex items-center gap-1"
                            title="Paso 6: Rúbricas CBL y DUA"
                          >
                            <Award className="w-3 h-3 text-purple-700" /> Evaluación
                          </a>
                          <button 
                            onClick={() => window.open(`/api/documents/export-carpeta-completa/${encodeURIComponent(subj.name)}`, '_blank')}
                            className="text-[11px] bg-slate-900 text-amber-300 hover:bg-slate-800 px-3 py-1.5 rounded-xl font-bold shadow-xs transition flex items-center gap-1 cursor-pointer"
                            title="Descargar Dossier Oficial Consolidado (.docx)"
                          >
                            <FileDown className="w-3 h-3 text-amber-400" /> Dossier (.docx)
                          </button>
                        </div>
                      </div>

                      {/* Resumen Compacto y Limpio: Sin saturar la pantalla con archivos (se ven en /organizar) */}
                      <div className="px-4 py-2.5 bg-white flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs">
                        <div className="flex items-center gap-2 text-slate-500 text-[11px] flex-wrap">
                          <span className="font-semibold text-slate-700">Estructura de Expediente:</span>
                          <span className="bg-[#FAF8F5] px-2.5 py-0.5 rounded-md border border-[#E8E3DA] text-slate-700">
                            📂 Base ({baseFilesCount} archivos)
                          </span>
                          <span className="bg-emerald-50 text-emerald-800 px-2.5 py-0.5 rounded-md border border-emerald-200">
                            ✨ REV ({revFilesCount} procesados)
                          </span>
                        </div>

                        <div className="flex items-center gap-2">
                          <button
                            type="button"
                            onClick={() => {
                              setLmsModalSubject(subj.name);
                              setIsLmsModalOpen(true);
                            }}
                            className="text-[11px] bg-indigo-50 hover:bg-indigo-100 text-indigo-900 border border-indigo-200 font-bold px-2.5 py-1 rounded-xl transition flex items-center gap-1 cursor-pointer shadow-2xs"
                            title="Sincronizar o exportar notas y feedback a Moodle, Classroom o Teams"
                          >
                            <Share2 className="w-3 h-3 text-indigo-700" /> Vincular LMS
                          </button>
                          <a
                            href="/organizar"
                            className="text-[11px] text-amber-900 hover:text-amber-700 font-bold flex items-center gap-1 hover:underline ml-1"
                            title="Ver árbol completo de archivos, carpetas y documentos en Organización"
                          >
                            Ver y organizar archivos <ArrowRight className="w-3 h-3" />
                          </a>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Sección de Validación IA Human-in-the-loop si se ha subido un archivo */}
      {aiResult && (
        <section className="mt-8">
          <div className="p-6 bg-white border border-[#E2DDD5] rounded-3xl shadow-atelier animate-in fade-in duration-200">
            <div className="flex items-center justify-between border-b border-[#EFEAE1] pb-3 mb-4">
              <h3 className="text-lg font-bold font-editorial text-slate-900 flex items-center gap-2">
                <span className="bg-slate-900 text-amber-300 w-6 h-6 rounded-full inline-flex items-center justify-center text-xs font-bold">IA</span>
                Validación de Mapeo (Principio Human-in-the-loop)
              </h3>
              <span className="text-xs font-semibold text-emerald-800 bg-emerald-50 px-2.5 py-0.5 rounded-full border border-emerald-200">
                Estructura Pre-analizada
              </span>
            </div>
            
            <p className="text-xs text-slate-600 mb-4 font-medium">
              El motor de inteligencia artificial ha clasificado las columnas de tu archivo. Revisa y autoriza para continuar al pipeline de analítica:
            </p>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4 text-xs">
              <div className="bg-[#FAF8F5] p-4 rounded-xl border border-[#E8E3DA]">
                <strong className="text-slate-800 block mb-1">Identificador de Alumnos (ID/RUT/Nombre):</strong>
                <span className="font-mono text-amber-900 font-bold bg-white px-2 py-1 rounded border border-[#DDD7CD] inline-block">
                  {aiResult.suggested_mapping?.student_identifier_column || 'No detectada automáticamente'}
                </span>
              </div>
              <div className="bg-[#FAF8F5] p-4 rounded-xl border border-[#E8E3DA]">
                <strong className="text-slate-800 block mb-1">Columnas de Calificaciones / Desempeño:</strong>
                <div className="flex flex-wrap gap-1.5">
                  {aiResult.suggested_mapping?.analytics_columns?.map((col: string, i: number) => (
                    <span key={i} className="bg-white border border-[#DDD7CD] text-slate-700 px-2 py-0.5 rounded text-[11px] font-medium">
                      {col}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            <div className="bg-amber-50/80 p-4 rounded-xl border border-amber-200 text-amber-950 mb-5 text-xs leading-relaxed">
              <strong className="block mb-1 font-bold text-amber-900">Observaciones Pedagógicas de la IA:</strong>
              <p>{aiResult.observations || 'Sin observaciones críticas. Estructura compatible con el flujo de 4 etapas.'}</p>
            </div>

            {!confirmed ? (
              <div className="flex flex-col sm:flex-row gap-3">
                <button 
                  onClick={handleConfirm}
                  className="bg-slate-900 text-amber-300 px-6 py-3 rounded-xl font-bold hover:bg-slate-800 shadow-sm transition text-xs flex-1 text-center cursor-pointer"
                >
                  ✓ Autorizar y Conectar al Flujo de Agentes
                </button>
                <a 
                  href="/organizar"
                  className="bg-[#FAF8F5] border border-[#DDD7CD] text-slate-700 px-6 py-3 rounded-xl font-semibold hover:bg-[#F2EDE5] transition text-xs text-center"
                >
                  Ver en Expedientes de Materias
                </a>
              </div>
            ) : (
              <div className="bg-emerald-50 text-emerald-900 p-4 rounded-xl font-bold border border-emerald-200 text-center text-xs flex items-center justify-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                ¡Estructura autorizada! Ya puedes proceder al Paso 2 (Planificar) o Paso 4 (Flujo de Agentes).
              </div>
            )}
          </div>
        </section>
      )}

      {/* Modal de Conexión e Interoperabilidad LMS */}
      <LmsConnectionModal
        isOpen={isLmsModalOpen}
        onClose={() => setIsLmsModalOpen(false)}
        subjects={pendingFiles.map((s: any) => s.name)}
        initialSubject={lmsModalSubject}
      />
    </div>
  );
}
