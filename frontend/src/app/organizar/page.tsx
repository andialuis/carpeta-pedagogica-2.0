'use client';
import { useState, useEffect } from 'react';
import { 
  FolderTree, FileText, FileSpreadsheet, Download, 
  CheckCircle2, AlertCircle, ArrowRight, Brain, Award, 
  RefreshCw, Sparkles, Shield, Database, FileDown
} from 'lucide-react';

export default function OrganizarExpedientesPage() {
  const [subjects, setSubjects] = useState<any[]>([]);
  const [selectedSubject, setSelectedSubject] = useState<string>('');
  const [summaryData, setSummaryData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    fetchSubjects();
  }, []);

  useEffect(() => {
    if (selectedSubject) {
      fetchSubjectSummary(selectedSubject);
    }
  }, [selectedSubject]);

  const fetchSubjects = async () => {
    try {
      const res = await fetch('/api/documents/pending', { cache: 'no-store' });
      const data = await res.json();
      const list = data.subjects || [];
      setSubjects(list);
      
      const searchParams = new URLSearchParams(window.location.search);
      const urlSubj = searchParams.get('subject');
      if (urlSubj && list.some((s: any) => s.name === urlSubj || s.name.startsWith(urlSubj))) {
        const found = list.find((s: any) => s.name === urlSubj || s.name.startsWith(urlSubj));
        setSelectedSubject(found ? found.name : urlSubj);
      } else if (list.length > 0) {
        setSelectedSubject(list[0].name);
      }
    } catch (e) {
      console.error("Error al cargar materias");
    }
  };

  const fetchSubjectSummary = async (subj: string) => {
    setIsLoading(true);
    try {
      const res = await fetch(`/api/subjects/summary/${encodeURIComponent(subj)}`, { cache: 'no-store' });
      if (res.ok) {
        const data = await res.json();
        setSummaryData(data);
      }
    } catch (e) {
      console.error("Error al obtener resumen de expediente");
    } finally {
      setIsLoading(false);
    }
  };

  const currentSubjectObj = subjects.find(s => s.name === selectedSubject);

  return (
    <div className="text-slate-800 pb-16 font-sans-clean">
      {/* Header */}
      <header className="mb-6 flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-[#E8E3DA] pb-5">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-[10px] font-bold tracking-widest uppercase text-indigo-800 bg-indigo-100/80 px-2.5 py-0.5 rounded-full border border-indigo-300">
              Paso 3 del Flujo Pedagógico
            </span>
            <span className="text-[10px] font-medium text-slate-400">• Organización & Expedientes REV</span>
          </div>
          <h1 className="text-3xl font-bold font-editorial text-slate-900 flex items-center gap-3">
            <FolderTree className="w-8 h-8 text-indigo-700" />
            Organización de Expedientes de Clase
          </h1>
          <p className="text-slate-500 text-sm mt-0.5">
            Estructuración de carpetas académicas, versiones integradas (-REV) y consolidación de evidencias
          </p>
        </div>

        {/* Selector de Materia */}
        <div className="flex items-center gap-3 bg-white border border-[#DDD7CD] p-2 rounded-2xl shadow-xs">
          <label className="text-xs font-bold text-slate-700 pl-2">Materia:</label>
          <select 
            value={selectedSubject} 
            onChange={(e) => setSelectedSubject(e.target.value)}
            className="bg-[#FAF8F5] border border-[#DDD7CD] text-slate-900 text-xs rounded-xl p-2 font-bold focus:ring-amber-500 focus:border-amber-500"
          >
            {subjects.length === 0 && <option value="">Sin materias</option>}
            {subjects.map((s, idx) => (
              <option key={idx} value={s.name}>{s.name}</option>
            ))}
          </select>
        </div>
      </header>

      {/* Grid de Estado del Expediente y Acciones */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Columna Izquierda (8 cols): Estructura del Expediente y Archivos */}
        <div className="lg:col-span-8 space-y-6">
          <div className="bg-white p-6 rounded-3xl shadow-atelier border border-[#E2DDD5]">
            <div className="flex items-center justify-between border-b border-[#EFEAE1] pb-4 mb-4">
              <div>
                <h2 className="text-lg font-bold font-editorial text-slate-900">
                  Expediente Académico: {selectedSubject || 'Ninguna seleccionada'}
                </h2>
                <p className="text-xs text-slate-500 font-medium">
                  Arquitectura documental y carpetas del curso
                </p>
              </div>
              <button 
                onClick={() => fetchSubjectSummary(selectedSubject)} 
                className="text-xs bg-[#FAF8F5] hover:bg-slate-100 text-slate-700 px-3 py-1.5 rounded-xl border border-[#DDD7CD] font-semibold flex items-center gap-1.5 transition"
              >
                <RefreshCw className={`w-3.5 h-3.5 text-slate-500 ${isLoading ? 'animate-spin' : ''}`} /> Refrescar
              </button>
            </div>

            {/* Checklist de Documentos Esenciales */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-6">
              <div className="p-3.5 rounded-2xl bg-[#FAF8F5] border border-[#E8E3DA] flex items-start gap-3">
                <div className="p-2 rounded-xl bg-white border border-[#E2DDD5] text-amber-700 mt-0.5">
                  <Brain className="w-4 h-4" />
                </div>
                <div>
                  <h4 className="text-xs font-bold text-slate-800">Plan Curricular (PDC)</h4>
                  <p className="text-[11px] text-slate-500">
                    {summaryData?.plan_curricular?.unidades_count 
                      ? `${summaryData.plan_curricular.unidades_count} unidades estructuradas` 
                      : 'Listo para diseñar o autogenerar'}
                  </p>
                </div>
              </div>

              <div className="p-3.5 rounded-2xl bg-[#FAF8F5] border border-[#E8E3DA] flex items-start gap-3">
                <div className="p-2 rounded-xl bg-white border border-[#E2DDD5] text-emerald-700 mt-0.5">
                  <Database className="w-4 h-4" />
                </div>
                <div>
                  <h4 className="text-xs font-bold text-slate-800">Dataset Limpio y Anonimizado</h4>
                  <p className="text-[11px] text-slate-500">
                    {summaryData?.diagnostico?.total_estudiantes 
                      ? `${summaryData.diagnostico.total_estudiantes} estudiantes con clave hash` 
                      : 'Generado en Etapa 2 del pipeline'}
                  </p>
                </div>
              </div>

              <div className="p-3.5 rounded-2xl bg-[#FAF8F5] border border-[#E8E3DA] flex items-start gap-3">
                <div className="p-2 rounded-xl bg-white border border-[#E2DDD5] text-purple-700 mt-0.5">
                  <Award className="w-4 h-4" />
                </div>
                <div>
                  <h4 className="text-xs font-bold text-slate-800">Matriz de Adaptación DUA</h4>
                  <p className="text-[11px] text-slate-500">
                    {summaryData?.dua?.adaptaciones_personalizadas 
                      ? `${summaryData.dua.adaptaciones_personalizadas} adaptaciones CAST formuladas` 
                      : 'Marcos CAST 2024 asignados'}
                  </p>
                </div>
              </div>

              <div className="p-3.5 rounded-2xl bg-[#FAF8F5] border border-[#E8E3DA] flex items-start gap-3">
                <div className="p-2 rounded-xl bg-white border border-[#E2DDD5] text-indigo-700 mt-0.5">
                  <FileText className="w-4 h-4" />
                </div>
                <div>
                  <h4 className="text-xs font-bold text-slate-800">Dossier Institucional (.docx)</h4>
                  <p className="text-[11px] text-slate-500">
                    {summaryData?.dossier?.disponible ? 'Documento formal compilado' : 'Listo para compilar y descargar'}
                  </p>
                </div>
              </div>
            </div>

            {/* Árbol de Versiones de la Materia */}
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3">
              Archivos en el Repositorio Local (Uploads)
            </h3>
            <div className="space-y-3">
              {currentSubjectObj?.versions?.map((ver: any, idx: number) => (
                <div key={idx} className="border border-[#E8E3DA] rounded-2xl overflow-hidden shadow-2xs">
                  <div className="bg-[#FAF8F5] px-4 py-2.5 text-xs font-bold text-slate-900 border-b border-[#E8E3DA] flex justify-between items-center">
                    <span>{ver.name === 'Original' ? '📂' : '✨'} Versión: {ver.name} ({ver.folder_name})</span>
                    <span className="text-[11px] text-slate-400 font-mono">{ver.files?.length || 0} archivos</span>
                  </div>
                  <div className="p-3 bg-white divide-y divide-[#F2EDE5]">
                    {ver.files?.map((file: any, fidx: number) => (
                      <div key={fidx} className="py-2 flex items-center justify-between text-xs">
                        <div className="flex items-center gap-2 truncate">
                          <FileSpreadsheet className="w-3.5 h-3.5 text-slate-400 flex-shrink-0" />
                          <span className="font-mono text-slate-700 truncate">{file.filename}</span>
                        </div>
                        <span className="text-[10px] text-slate-400 bg-slate-50 px-2 py-0.5 rounded border border-slate-200">
                          {file.path.split('.').pop()?.toUpperCase()}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Columna Derecha (4 cols): Acciones de Exportación y Conexión de Flujo */}
        <div className="lg:col-span-4 space-y-6">
          {/* Tarjeta de Exportación Oficial */}
          <div className="bg-white p-6 rounded-3xl shadow-atelier border border-[#E2DDD5]">
            <h3 className="text-base font-bold font-editorial text-slate-900 mb-2 flex items-center gap-2">
              <FileDown className="w-5 h-5 text-amber-700" />
              Exportaciones del Expediente
            </h3>
            <p className="text-xs text-slate-500 mb-4 font-medium">
              Descarga los productos consolidados generados a lo largo de las etapas:
            </p>

            <div className="space-y-3">
              <button
                onClick={() => window.open(`/api/documents/export-carpeta-completa/${encodeURIComponent(selectedSubject)}`, '_blank')}
                disabled={!selectedSubject}
                className="w-full bg-slate-900 hover:bg-slate-800 text-amber-300 font-bold p-3 rounded-2xl transition shadow-xs flex items-center justify-between text-xs cursor-pointer disabled:opacity-50"
              >
                <div className="flex items-center gap-2">
                  <FileText className="w-4 h-4 text-amber-400" />
                  <div className="text-left">
                    <span className="block leading-tight">Dossier Oficial (.docx)</span>
                    <span className="text-[10px] text-slate-400 font-normal">Carpeta Pedagógica Completa</span>
                  </div>
                </div>
                <Download className="w-4 h-4" />
              </button>

              <button
                onClick={() => window.open(`/api/documents/export-anonymized/${encodeURIComponent(selectedSubject)}?format=xlsx`, '_blank')}
                disabled={!selectedSubject}
                className="w-full bg-[#FAF8F5] hover:bg-emerald-50/80 text-emerald-900 border border-emerald-300/80 font-bold p-3 rounded-2xl transition shadow-2xs flex items-center justify-between text-xs cursor-pointer disabled:opacity-50"
              >
                <div className="flex items-center gap-2">
                  <FileSpreadsheet className="w-4 h-4 text-emerald-700" />
                  <div className="text-left">
                    <span className="block leading-tight">Dataset Anonimizado (.xlsx)</span>
                    <span className="text-[10px] text-slate-500 font-normal">Para R, SPSS o Stata</span>
                  </div>
                </div>
                <Download className="w-4 h-4" />
              </button>

              <button
                onClick={() => window.open(`/api/documents/export-anonymized/${encodeURIComponent(selectedSubject)}?format=csv`, '_blank')}
                disabled={!selectedSubject}
                className="w-full bg-white hover:bg-slate-50 text-slate-700 border border-[#DDD7CD] font-semibold p-2.5 rounded-2xl transition shadow-2xs flex items-center justify-between text-xs cursor-pointer disabled:opacity-50"
              >
                <span className="text-slate-600 font-mono">Dataset CSV Plano</span>
                <Download className="w-3.5 h-3.5 text-slate-400" />
              </button>
            </div>
          </div>

          {/* Tarjeta de Siguiente Paso en la Lógica de Trabajo */}
          <div className="bg-gradient-to-br from-indigo-900 to-slate-900 text-white p-6 rounded-3xl shadow-atelier">
            <span className="text-[10px] font-bold uppercase tracking-widest text-amber-400 bg-white/10 px-2 py-0.5 rounded-full border border-white/10">
              Siguiente Paso en el Flujo
            </span>
            <h3 className="text-lg font-bold font-editorial mt-2 mb-1">
              4. Flujo de Agentes IA
            </h3>
            <p className="text-xs text-slate-300 mb-4 leading-relaxed font-sans-clean">
              Ejecuta las 4 etapas metodológicas (Ingesta, Anonimización, Análisis con Gemini y Tableros) sobre este expediente.
            </p>
            <a
              href={`/agents?subject=${encodeURIComponent(selectedSubject)}`}
              className="w-full bg-amber-400 hover:bg-amber-300 text-slate-950 font-bold p-3 rounded-2xl transition shadow-xs flex items-center justify-center gap-2 text-xs"
            >
              Ir a Flujo de Agentes <ArrowRight className="w-4 h-4" />
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
