'use client';
import { useState, useEffect } from 'react';
import { 
  ShieldCheck, AlertTriangle, FileDown, CheckCircle2, 
  RefreshCw, Play, Brain, Sparkles, Scale, CloudUpload, FileSpreadsheet
} from 'lucide-react';
import DriveBackupModal from '../components/DriveBackupModal';

export default function AgentsDashboard() {
  const [modules, setModules] = useState<any[]>([]);
  const [history, setHistory] = useState<any[]>([]);
  const [logs, setLogs] = useState<string[]>([]);
  const [loadingId, setLoadingId] = useState<string | null>(null);
  const [subjects, setSubjects] = useState<any[]>([]);
  const [selectedSubject, setSelectedSubject] = useState<string>('');
  
  // Estado para el Modal HITL de Auditoría de Datos
  const [showAuditModal, setShowAuditModal] = useState(false);
  const [auditLoading, setAuditLoading] = useState(false);
  const [auditData, setAuditData] = useState<any>(null);
  const [pendingModuleId, setPendingModuleId] = useState<string | null>(null);

  // Estado para el Respaldo en Google Drive
  const [showDriveModal, setShowDriveModal] = useState(false);
  const [stage1JustCompleted, setStage1JustCompleted] = useState(false);

  useEffect(() => {
    fetchModules();
    fetchSubjects();
  }, []);

  useEffect(() => {
    if (selectedSubject) {
      fetchHistory(selectedSubject);
    }
  }, [selectedSubject]);

  const fetchSubjects = async () => {
    try {
      const res = await fetch('/api/documents/pending', { cache: 'no-store' });
      const data = await res.json();
      setSubjects(data.subjects || []);
      if (data.subjects && data.subjects.length > 0) {
        setSelectedSubject(data.subjects[0].name);
      }
    } catch (e) {
      console.error("Error fetching subjects");
    }
  };

  const fetchHistory = async (subject: string) => {
    try {
      const res = await fetch(`/api/agents/history/${encodeURIComponent(subject)}`, { cache: 'no-store' });
      const data = await res.json();
      setHistory(data.history || []);
    } catch (e) {
      console.error("Error fetching history");
    }
  };

  const fetchModules = async () => {
    try {
      const res = await fetch('/api/agents/list', { cache: 'no-store' });
      const data = await res.json();
      setModules(data.modules && data.modules.length > 0 ? data.modules : fallbackModules);
    } catch (e) {
      console.error("Error fetching modules", e);
      setModules(fallbackModules);
    }
  };

  const fallbackModules = [
    { id: "e1", name: "Etapa 1: Preparar Datos & Control de Versiones", description: "Limpia y clasifica los datos crudos, e inicializa la Matriz de Control de Versiones Documental (ISO 21001:2018 Cláusula 7.5).", products: "BASE_INTEGRADA.xlsx, CONTROL_VERSIONES_DOCUMENTAL.xlsx" },
    { id: "e2", name: "Etapa 2: Procesar Datos", description: "Anonimiza e imputa datos vacíos (Crea diccionario de nombres).", products: "BASE_LIMPIA_ANONIMIZADA.xlsx, llave_nombres.json" },
    { id: "e3", name: "Etapa 3: Analizar Datos & Auditoría Cognitiva", description: "Genera indicadores multidimensionales, auditoría de outsourcing e hipótesis usando Gemini.", products: "INFORME_COMPLETO_E3.docx, insights.json" },
    { id: "e4", name: "Etapa 4: Visualizar Datos", description: "Construye los tableros analíticos interactivos.", products: "Dashboard Interactivo Web (Next.js)" }
  ];

  // Dispara la auditoría de suficiencia antes de ejecutar
  const initiateStageExecution = async (moduleId: string) => {
    if (!selectedSubject) return alert("Selecciona una materia primero");
    setPendingModuleId(moduleId);
    setAuditLoading(true);
    setShowAuditModal(true);

    try {
      const res = await fetch(`/api/stages/audit/${encodeURIComponent(selectedSubject)}/${moduleId}`, { 
        method: 'POST',
        cache: 'no-store' 
      });
      const data = await res.json();
      setAuditData(data);
    } catch (e) {
      console.error("Error al auditar datos", e);
    }
    setAuditLoading(false);
  };

  // Ejecución real una vez autorizada por el docente
  const executeAuthorizedAgent = async () => {
    if (!pendingModuleId || !selectedSubject) return;
    const moduleId = pendingModuleId;
    setShowAuditModal(false);
    setLoadingId(moduleId);
    
    setLogs((prev) => [
      ...prev, 
      `[AUTORIZACIÓN HUMANA] Docente autorizó ejecución de ${moduleId} con estado: ${auditData?.status || 'verificado'}.`,
      `[SISTEMA] Iniciando ejecución de ${moduleId} para ${selectedSubject}...`
    ]);

    try {
      const res = await fetch(`/api/agents/run/${moduleId}?subject_name=${encodeURIComponent(selectedSubject)}`, { method: 'POST' });
      const data = await res.json();
      
      if (!res.ok) {
        setLogs((prev) => [
          ...prev, 
          `[ERROR] ${data.detail || 'Falló la ejecución del agente.'}`,
          `[SUGERENCIA] Haz clic en el botón de reintentar (↻) para volver a ejecutar con el motor robusto.`,
          ''
        ]);
        setLoadingId(null);
        setPendingModuleId(null);
        return;
      }

      setLogs((prev) => [...prev, `[SISTEMA] Ejecutando: ${data.script_executed}`]);
      
      if (data.output) {
        const outputLines = data.output.split('\n');
        outputLines.forEach((line: string) => {
           if (line.trim()) {
             setLogs((prev) => [...prev, `[AGENTE] ${line.trim()}`]);
           }
        });
      }

      setLogs((prev) => [...prev, `[ÉXITO] Módulo completado correctamente.`, '']);
      fetchHistory(selectedSubject);
      
      if (moduleId === 'e1') {
        setStage1JustCompleted(true);
        setLogs((prev) => [
          ...prev,
          `[SISTEMA] Carpeta -REV preparada con éxito y BASE_INTEGRADA.xlsx consolidada.`,
          `[RESPALDO RECOMENDADO] Puedes guardar una copia segura en Google Drive haciendo clic en 'Respaldar en Google Drive'.`,
          ''
        ]);
      }

      if (moduleId === 'e4') {
        setLogs((prev) => [...prev, `[SISTEMA] Redirigiendo al Dashboard Analítico...`]);
        setTimeout(() => {
          window.location.href = '/analytics';
        }, 1500);
      }

    } catch (e: any) {
      setLogs((prev) => [
        ...prev, 
        `[ERROR] Falló la ejecución del agente: ${e.message || 'Error de conexión con el servidor.'}`,
        `[SUGERENCIA] Presiona el botón de actualizar (↻) para reintentar la inferencia.`
      ]);
    }
    setLoadingId(null);
    setPendingModuleId(null);
  };

  const handleDownloadInstrument = (instrumentId: string) => {
    window.open(`/api/instruments/download/${instrumentId}`, '_blank');
  };

  const handleDownloadVersionControl = () => {
    if (!selectedSubject) return alert("Selecciona una materia primero");
    window.open(`/api/documents/version-control/${encodeURIComponent(selectedSubject)}`, '_blank');
  };

  return (
    <div className="text-slate-800 pb-12 font-sans-clean">
      <header className="mb-8 flex flex-col md:flex-row md:justify-between md:items-center gap-4 border-b border-[#E8E3DA] pb-5">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-[10px] font-bold tracking-widest uppercase text-amber-800 bg-amber-100/80 px-2.5 py-0.5 rounded-full border border-amber-300">
              Orquestación Autónoma
            </span>
            <span className="text-[10px] font-medium text-slate-400">• Supervisión Pedagógica</span>
          </div>
          <h1 className="text-3xl font-bold font-editorial text-slate-900 flex items-center gap-3">
            <Brain className="w-8 h-8 text-amber-700" />
            Flujo de Agentes & Auditoría de Datos
          </h1>
          <p className="text-slate-500 text-sm mt-0.5 font-medium">
            Supervisión humanista con consentimiento informado (HITL), rigor estadístico y trazabilidad
          </p>
        </div>
        <div className="bg-white border border-[#E2DDD5] p-2 rounded-xl shadow-xs flex items-center gap-2.5">
          <label className="font-semibold text-slate-700 text-xs pl-2 flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-amber-500"></span> Materia Activa:
          </label>
          <select 
            className="bg-[#FAF8F5] border border-[#DDD7CD] text-slate-900 text-xs rounded-lg focus:ring-amber-500 focus:border-amber-500 block p-2 font-bold"
            value={selectedSubject}
            onChange={(e) => setSelectedSubject(e.target.value)}
          >
            {subjects.length === 0 && <option value="">Sin materias detectadas</option>}
            {subjects.map((subj, idx) => (
              <option key={idx} value={subj.name}>{subj.name}</option>
            ))}
          </select>
        </div>
      </header>

      {/* Banner reactivo de Respaldo tras completar la Etapa 1 */}
      {stage1JustCompleted && (
        <div className="mb-6 p-4 rounded-2xl bg-blue-50 border border-blue-200 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 shadow-2xs animate-in fade-in">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-blue-600 text-white flex items-center justify-center shrink-0 shadow-xs">
              <CloudUpload className="w-5 h-5" />
            </div>
            <div>
              <p className="text-xs font-bold text-blue-950">
                ¡Carpetas de la Etapa 1 preparadas para {selectedSubject}!
              </p>
              <p className="text-[11px] text-blue-900/80">
                Se generó la estructura <code className="bg-blue-100 px-1 py-0.5 rounded text-blue-950 font-mono">-REV</code> y se consolidó <code className="bg-blue-100 px-1 py-0.5 rounded text-blue-950 font-mono">BASE_INTEGRADA.xlsx</code>. ¿Deseas subir una copia segura a Google Drive ahora mismo?
              </p>
            </div>
          </div>
          <button
            onClick={() => setShowDriveModal(true)}
            className="bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs px-4 py-2 rounded-xl transition shadow-xs flex items-center gap-1.5 shrink-0 cursor-pointer"
          >
            <CloudUpload className="w-3.5 h-3.5" />
            Subir a Google Drive
          </button>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <main className="space-y-6">
          {modules.map((mod, idx) => (
            <div key={mod.id} className="bg-white border border-[#E2DDD5] p-6 rounded-2xl shadow-atelier hover:border-amber-300 transition">
              <div className="flex justify-between items-start mb-2">
                <h2 className="text-lg font-bold font-editorial text-slate-900 flex items-center gap-2.5">
                  <span className="w-7 h-7 rounded-full bg-slate-900 text-amber-300 text-xs flex items-center justify-center font-bold">
                    {idx + 1}
                  </span>
                  {mod.name}
                </h2>
                <span className="text-[11px] px-2.5 py-1 bg-amber-50 text-amber-900 border border-amber-200 font-semibold rounded-full flex items-center gap-1">
                  <ShieldCheck className="w-3.5 h-3.5 text-amber-700" /> HITL Activo
                </span>
              </div>
              <p className="text-slate-600 text-xs leading-relaxed mb-4">{mod.description}</p>
              
              {mod.products && (
                <div className="mb-5 bg-[#FAF8F5] border border-[#E8E3DA] p-3 rounded-xl">
                  <span className="text-[10px] font-bold text-slate-700 uppercase tracking-wider block mb-1">
                    Productos Esperados:
                  </span>
                  <span className="text-xs font-mono text-slate-600 break-all">{mod.products}</span>
                </div>
              )}

              <div className="flex gap-3">
                <button 
                  onClick={() => initiateStageExecution(mod.id)}
                  disabled={loadingId !== null || !selectedSubject}
                  className="flex-1 bg-slate-900 text-amber-300 font-bold py-3 px-4 rounded-xl hover:bg-slate-800 transition flex items-center justify-center gap-2 shadow-xs disabled:opacity-50 text-xs"
                >
                  <Play className="w-4 h-4 text-amber-400" />
                  {loadingId === mod.id ? 'Ejecutando...' : 'Evaluar y Ejecutar'}
                </button>
                <button 
                  onClick={() => initiateStageExecution(mod.id)}
                  disabled={loadingId !== null || !selectedSubject}
                  title="Re-ejecutar con nueva planilla o datos actualizados"
                  className="bg-[#FAF8F5] hover:bg-[#F2EDE5] text-slate-700 p-3 rounded-xl transition border border-[#DDD7CD]"
                >
                  <RefreshCw className="w-4 h-4" />
                </button>
              </div>

              {/* Controles de Calidad, Control de Versiones Documental (ISO 21001) y Respaldo Nube */}
              {mod.id === 'e1' && (
                <div className="mt-4 pt-3 border-t border-[#E8E3DA] space-y-3">
                  <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
                    <div className="text-[11px] text-slate-600">
                      <span className="font-semibold text-slate-800">Control de Versiones ISO 21001:</span> Matriz documental y Hash SHA-256
                    </div>
                    <button
                      type="button"
                      onClick={handleDownloadVersionControl}
                      disabled={!selectedSubject}
                      className="text-xs bg-emerald-50 hover:bg-emerald-100 text-emerald-900 font-bold px-3 py-1.5 rounded-xl transition border border-emerald-300 flex items-center gap-1.5 cursor-pointer shadow-2xs"
                      title="Descargar libro Excel de control de versiones y auditoría de documentos"
                    >
                      <FileSpreadsheet className="w-3.5 h-3.5 text-emerald-700" />
                      📑 Control de Versiones (.xlsx)
                    </button>
                  </div>

                  <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
                    <div className="text-[11px] text-slate-500">
                      <span className="font-semibold text-slate-700">Respaldo en la Nube:</span> Copia de carpetas Base y REV
                    </div>
                    <button
                      type="button"
                      onClick={() => setShowDriveModal(true)}
                      disabled={!selectedSubject}
                      className="text-xs bg-blue-50 hover:bg-blue-100 text-blue-800 font-bold px-3 py-1.5 rounded-xl transition border border-blue-200 flex items-center gap-1.5 cursor-pointer shadow-2xs"
                      title="Subir copia de seguridad de las carpetas de la materia a Google Drive"
                    >
                      <CloudUpload className="w-3.5 h-3.5 text-blue-600" />
                      ☁️ Respaldar en Google Drive
                    </button>
                  </div>

                  {/* Banner de Advertencia de Trazabilidad ISO 21001 */}
                  <div className="p-3 bg-amber-50/90 border border-amber-200/90 rounded-xl flex items-start gap-2.5">
                    <AlertTriangle className="w-4 h-4 text-amber-700 shrink-0 mt-0.5" />
                    <p className="text-[11px] text-amber-950 leading-relaxed">
                      <strong className="font-bold">Aviso de Auditoría Institucional (ISO 21001 Cláusula 7.5):</strong> Si editas manualmente los archivos Word o Excel fuera del software, debes registrar el cambio actualizando la versión (ej. 1.0 a 1.1) y fecha en la hoja <code className="bg-amber-100 px-1 py-0.5 rounded text-amber-950 font-mono font-bold">CONTROL_VERSIONES_DOCUMENTAL.xlsx</code> para no invalidar la trazabilidad ante pares evaluadores y comités de acreditación.
                    </p>
                  </div>
                </div>
              )}
            </div>
          ))}
        </main>
        
        <aside className="bg-slate-950 rounded-2xl shadow-xl border border-slate-800 flex flex-col h-[620px] overflow-hidden">
          <div className="bg-slate-900 p-4 flex justify-between items-center border-b border-slate-800">
            <div className="flex gap-2 items-center">
              <div className="w-3 h-3 rounded-full bg-rose-500"></div>
              <div className="w-3 h-3 rounded-full bg-amber-500"></div>
              <div className="w-3 h-3 rounded-full bg-emerald-500"></div>
              <span className="ml-2 text-xs text-slate-300 font-mono font-semibold">Consola de Agentes y Trazabilidad</span>
            </div>
            <span className="text-xs text-emerald-400 font-mono">En Línea</span>
          </div>
          <div className="flex-1 p-5 overflow-y-auto font-mono text-xs text-emerald-400 space-y-1">
            {logs.length === 0 ? (
              <p className="text-slate-500 italic">Haz clic en 'Evaluar y Ejecutar' en cualquier etapa para auditar suficiencia e iniciar el procesamiento...</p>
            ) : (
              logs.map((log, i) => (
                <div key={i} className="leading-relaxed">{log}</div>
              ))
            )}
            {loadingId && (
              <div className="text-amber-400 animate-pulse flex items-center gap-2 pt-2">
                <RefreshCw className="w-3.5 h-3.5 animate-spin" /> Procesando etapa {loadingId}...
              </div>
            )}
          </div>
        </aside>
      </div>

      {/* MODAL HITL: AUDITORÍA DE DATOS, PROS/CONTRAS Y AUTORIZACIÓN */}
      {showAuditModal && (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl shadow-2xl border border-[#E2DDD5] max-w-2xl w-full max-h-[90vh] overflow-y-auto p-6 md:p-8 animate-in fade-in zoom-in-95 duration-200">
            
            {auditLoading ? (
              <div className="py-16 text-center">
                <RefreshCw className="w-10 h-10 text-amber-700 animate-spin mx-auto mb-4" />
                <h3 className="text-lg font-bold font-editorial text-slate-800">Auditando Suficiencia de Datos...</h3>
                <p className="text-slate-500 text-sm mt-1">Evaluando dimensiones CBL, micro-quizzes y factores sociodemográficos</p>
              </div>
            ) : auditData ? (
              <div className="space-y-6">
                
                {/* Cabecera del Modal */}
                <div className="flex items-start justify-between border-b border-[#EFEAE1] pb-4">
                  <div>
                    <span className="text-[10px] font-bold uppercase tracking-wider text-amber-900 bg-amber-100/80 px-2.5 py-1 rounded-full border border-amber-300">
                      Control Pedagógico (Human-in-the-Loop)
                    </span>
                    <h2 className="text-2xl font-bold font-editorial text-slate-900 mt-2.5">
                      Auditoría de Datos: {auditData.stage_id.toUpperCase()}
                    </h2>
                    <p className="text-slate-500 text-xs mt-1">Materia: <span className="font-semibold text-slate-700">{auditData.subject_name}</span></p>
                  </div>
                  <div className={`px-3 py-1 rounded-full text-xs font-bold ${
                    auditData.status === 'completo' ? 'bg-emerald-100 text-emerald-800 border border-emerald-200' :
                    auditData.status === 'parcial' ? 'bg-amber-100 text-amber-800 border border-amber-200' : 'bg-rose-100 text-rose-800 border border-rose-200'
                  }`}>
                    Estado: {auditData.status.toUpperCase()}
                  </div>
                </div>

                {/* 1. Dimensiones Evaluadas */}
                <div>
                  <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700 mb-3">
                    1. Cobertura de Dimensiones de Analítica:
                  </h3>
                  <div className="space-y-2">
                    {auditData.dimensions_detected.map((dim: any) => (
                      <div key={dim.id} className="flex items-start gap-2.5 bg-emerald-50 border border-emerald-200 p-2.5 rounded-xl text-xs text-emerald-900">
                        <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0 mt-0.5" />
                        <div>
                          <span className="font-bold">{dim.name}:</span> {dim.detail}
                        </div>
                      </div>
                    ))}
                    {auditData.dimensions_missing.map((dim: any) => (
                      <div key={dim.id} className="flex items-start gap-2.5 bg-amber-50 border border-amber-200 p-2.5 rounded-xl text-xs text-amber-900">
                        <AlertTriangle className="w-4 h-4 text-amber-600 flex-shrink-0 mt-0.5" />
                        <div>
                          <span className="font-bold">{dim.name} (Faltante):</span> {dim.impact}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* 2. Balanza de Ventajas y Desventajas */}
                <div className="bg-[#FAF8F5] p-4 rounded-2xl border border-[#E2DDD5]">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-slate-800 mb-3 flex items-center gap-2">
                    <Scale className="w-4 h-4 text-amber-700" />
                    2. Análisis de Decisión: ¿Continuar con los datos actuales?
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                    <div className="bg-white p-3.5 rounded-xl border border-[#E2DDD5] shadow-xs">
                      <span className="font-bold text-emerald-700 block mb-1.5">✓ Ventajas de avanzar ahora:</span>
                      <ul className="list-disc ml-4 space-y-1 text-slate-600 leading-relaxed">
                        {auditData.trade_offs.ventajas.map((v: string, i: number) => (
                          <li key={i}>{v}</li>
                        ))}
                      </ul>
                    </div>
                    <div className="bg-white p-3.5 rounded-xl border border-[#E2DDD5] shadow-xs">
                      <span className="font-bold text-rose-700 block mb-1.5">⚠ Desventajas / Limitaciones:</span>
                      <ul className="list-disc ml-4 space-y-1 text-slate-600 leading-relaxed">
                        {auditData.trade_offs.desventajas.map((d: string, i: number) => (
                          <li key={i}>{d}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>

                {/* 3. Instrumento Sugerido Proactivamente */}
                {auditData.instrument_suggested && (
                  <div className="bg-[#FAF6EE] border border-amber-200 rounded-2xl p-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div>
                      <div className="flex items-center gap-2 text-amber-950 font-bold text-xs">
                        <Sparkles className="w-4 h-4 text-amber-600" />
                        Instrumento Recomendado: {auditData.instrument_suggested.name}
                      </div>
                      <p className="text-xs text-slate-600 mt-1">
                        {auditData.instrument_suggested.description}
                      </p>
                      <span className="text-[11px] text-emerald-700 font-semibold block mt-1">
                        ★ Beneficio: {auditData.instrument_suggested.benefit}
                      </span>
                    </div>
                    <button 
                      onClick={() => handleDownloadInstrument(auditData.instrument_suggested.instrument_id)}
                      className="bg-white hover:bg-amber-50 text-amber-900 border border-amber-300 font-semibold text-xs px-4 py-2.5 rounded-xl transition shadow-xs flex items-center justify-center gap-1.5 whitespace-nowrap"
                    >
                      <FileDown className="w-4 h-4" />
                      Descargar Plantilla
                    </button>
                  </div>
                )}

                {/* Botones de Acción y Consentimiento */}
                <div className="pt-3 border-t border-[#EFEAE1] flex flex-col md:flex-row justify-end gap-3">
                  <button 
                    onClick={() => setShowAuditModal(false)}
                    className="px-5 py-2.5 rounded-xl border border-[#DDD7CD] text-slate-700 font-medium text-xs hover:bg-slate-50 transition"
                  >
                    Pausar para subir nuevos datos
                  </button>
                  <button 
                    onClick={executeAuthorizedAgent}
                    className="px-6 py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-amber-300 font-bold text-xs transition flex items-center justify-center gap-2 shadow-sm"
                  >
                    <CheckCircle2 className="w-4 h-4 text-amber-400" />
                    Autorizar y Ejecutar Etapa
                  </button>
                </div>

              </div>
            ) : null}

          </div>
        </div>
      )}

      {/* Modal Interactivo de Respaldo a Google Drive */}
      <DriveBackupModal 
        isOpen={showDriveModal} 
        onClose={() => setShowDriveModal(false)} 
        subjectName={selectedSubject} 
      />

    </div>
  );
}
