'use client';
import { useState, useEffect } from 'react';
import { 
  BrainCircuit, Sparkles, Copy, FolderInput, FolderOutput, Check, 
  BookOpen, PlusCircle, FileText, Download, Play, RefreshCw, 
  ExternalLink, Layers, CheckCircle2, AlertCircle, Code, Eye
} from 'lucide-react';

export default function PlanificacionPage() {
  const [subjects, setSubjects] = useState<any[]>([]);
  const [selectedSubject, setSelectedSubject] = useState<string>('');
  const [models, setModels] = useState<any[]>([]);
  const [selectedModelId, setSelectedModelId] = useState<string>('cbl_modular_inv101');
  const [activeModel, setActiveModel] = useState<any>(null);

  // Parámetros del Formulario
  const [params, setParams] = useState({
    codigo_modulo: 'INV101',
    docente: 'Docente Titular',
    periodo: 'Módulo 1 - 2026',
    duracion_horas: '80 horas académicas',
    modalidad: 'Semipresencial / Aula Invertida',
    problema_contexto: 'Outsourcing cognitivo y desinformación en formulación de investigaciones.',
    estudiantes_ac: 'E. L. (Adaptación visual DUA)'
  });

  const [draftText, setDraftText] = useState<string>('');
  const [hasDraft, setHasDraft] = useState(false);
  const [outputFiles, setOutputFiles] = useState<string[]>([]);
  const [dirs, setDirs] = useState<any>(null);

  // Estados de carga y feedback
  const [isLoading, setIsLoading] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [copiedPrompt, setCopiedPrompt] = useState(false);
  const [copiedScript, setCopiedScript] = useState(false);
  const [copiedDraft, setCopiedDraft] = useState(false);
  const [feedback, setFeedback] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  // Modal nuevo modelo
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newModel, setNewModel] = useState({
    id: '',
    name: '',
    description: '',
    system: 'superior',
    prompt_template: '',
    script_export: '',
    drive_config: {
      input_folder: '',
      output_folder: '',
      template_id: ''
    }
  });

  useEffect(() => {
    fetchInitialData();
  }, []);

  useEffect(() => {
    if (selectedSubject) {
      fetchSubjectPlanning(selectedSubject);
    }
  }, [selectedSubject]);

  useEffect(() => {
    const found = models.find((m) => m.id === selectedModelId);
    if (found) {
      setActiveModel(found);
    }
  }, [selectedModelId, models]);

  const fetchInitialData = async () => {
    setIsLoading(true);
    try {
      // 1. Obtener materias
      const resSubj = await fetch('/api/documents/pending', { cache: 'no-store' });
      const dataSubj = await resSubj.json();
      const list = dataSubj.subjects || [];
      setSubjects(list);
      
      const searchParams = new URLSearchParams(window.location.search);
      const urlSubj = searchParams.get('subject');
      if (urlSubj && list.some((s: any) => s.name === urlSubj || s.name.startsWith(urlSubj))) {
        const found = list.find((s: any) => s.name === urlSubj || s.name.startsWith(urlSubj));
        setSelectedSubject(found ? found.name : urlSubj);
      } else if (list.length > 0) {
        setSelectedSubject(list[0].name);
      }

      // 2. Obtener modelos de planificación
      const resMod = await fetch('/api/planning/models', { cache: 'no-store' });
      const dataMod = await resMod.json();
      setModels(dataMod.models || []);
      if (dataMod.models && dataMod.models.length > 0) {
        setSelectedModelId(dataMod.models[0].id);
        setActiveModel(dataMod.models[0]);
      }
    } catch (e) {
      console.error('Error cargando datos de planificación', e);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchSubjectPlanning = async (subject: string) => {
    try {
      const res = await fetch(`/api/planning/subject/${encodeURIComponent(subject)}`, { cache: 'no-store' });
      const data = await res.json();
      setDirs(data.dirs);
      setHasDraft(data.has_draft);
      setDraftText(data.draft_text || '');
      setOutputFiles(data.output_files || []);
      if (data.model?.id) {
        setSelectedModelId(data.model.id);
        setActiveModel(data.model);
      }
    } catch (e) {
      console.error('Error cargando planificación de asignatura', e);
    }
  };

  const handleGenerateDraft = async () => {
    setIsGenerating(true);
    setFeedback(null);
    try {
      const res = await fetch(`/api/planning/subject/${encodeURIComponent(selectedSubject)}/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(params)
      });
      const data = await res.json();
      setDraftText(data.draft_text || '');
      setHasDraft(true);
      setFeedback({
        type: 'success',
        message: `¡Borrador generado con éxito utilizando motor: ${data.motor_utilizado || 'IA'}!`
      });
      fetchSubjectPlanning(selectedSubject);
    } catch (e: any) {
      setFeedback({ type: 'error', message: `Error generando borrador: ${e.message}` });
    } finally {
      setIsGenerating(false);
    }
  };

  const handleProcessOutput = async () => {
    setIsProcessing(true);
    setFeedback(null);
    try {
      const res = await fetch(`/api/planning/subject/${encodeURIComponent(selectedSubject)}/process`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      const data = await res.json();
      if (data.success) {
        setFeedback({
          type: 'success',
          message: `¡Documento final generado en la carpeta de salida! Se inyectaron ${data.tags_count} etiquetas.`
        });
        fetchSubjectPlanning(selectedSubject);
      } else {
        setFeedback({ type: 'error', message: data.message || 'Error procesando plan.' });
      }
    } catch (e: any) {
      setFeedback({ type: 'error', message: `Fallo de inyección: ${e.message}` });
    } finally {
      setIsProcessing(false);
    }
  };

  const handleCopyPrompt = () => {
    if (!activeModel?.prompt_template) return;
    let fullPrompt = activeModel.prompt_template
      .replace('{{MATERIA}}', selectedSubject)
      .replace('{{CODIGO_MODULO}}', params.codigo_modulo)
      .replace('{{DOCENTE}}', params.docente)
      .replace('{{PERIODO_MODULO}}', params.periodo)
      .replace('{{DURACION_HORAS}}', params.duracion_horas)
      .replace('{{MODALIDAD}}', params.modalidad)
      .replace('{{PROBLEMA_CONTEXTO}}', params.problema_contexto)
      .replace('{{ESTUDIANTES_AC}}', params.estudiantes_ac);

    navigator.clipboard.writeText(fullPrompt);
    setCopiedPrompt(true);
    setTimeout(() => setCopiedPrompt(false), 2000);
  };

  const handleSaveNewModel = async () => {
    if (!newModel.name.trim()) return;
    try {
      const res = await fetch('/api/planning/models', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newModel)
      });
      const data = await res.json();
      if (data.success) {
        setIsModalOpen(false);
        fetchInitialData();
      }
    } catch (e) {
      console.error('Error guardando modelo', e);
    }
  };

  return (
    <div className="text-slate-800 pb-16 font-sans-clean">
      {/* Cabecera Atelier */}
      <header className="mb-8 flex flex-col md:flex-row md:justify-between md:items-center gap-4 border-b border-[#E8E3DA] pb-5">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-[10px] font-bold tracking-widest uppercase text-amber-800 bg-amber-100/80 px-2.5 py-0.5 rounded-full border border-amber-300">
              Arquitectura Curricular
            </span>
            <span className="text-[10px] font-medium text-slate-400">• Modelos Reutilizables & DUA</span>
          </div>
          <h1 className="text-3xl font-bold font-editorial text-slate-900 flex items-center gap-3">
            <BrainCircuit className="w-8 h-8 text-amber-700" />
            Planificación Docente por Competencias
          </h1>
          <p className="text-slate-500 text-sm mt-0.5 font-medium">
            Modelos globales de planificación, inyección estructurada por etiquetas y sincronización con Google Drive
          </p>
        </div>

        {/* Selectores Superiores de Asignatura y Modelo */}
        <div className="flex flex-wrap items-center gap-3">
          {/* Selector de Asignatura */}
          <div className="bg-white border border-[#E2DDD5] p-2 rounded-xl shadow-xs flex items-center gap-2">
            <label className="font-semibold text-slate-700 text-xs pl-2 flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-amber-500"></span> Asignatura:
            </label>
            <select
              className="bg-[#FAF8F5] border border-[#DDD7CD] text-slate-900 text-xs rounded-lg p-2 font-bold focus:ring-amber-500"
              value={selectedSubject}
              onChange={(e) => setSelectedSubject(e.target.value)}
            >
              {subjects.map((s, idx) => (
                <option key={idx} value={s.name}>{s.name}</option>
              ))}
            </select>
          </div>

          {/* Selector de Modelo Global */}
          <div className="bg-white border border-[#E2DDD5] p-2 rounded-xl shadow-xs flex items-center gap-2">
            <label className="font-semibold text-slate-700 text-xs pl-2 flex items-center gap-1.5">
              <Layers className="w-3.5 h-3.5 text-indigo-600" /> Modelo:
            </label>
            <select
              className="bg-[#FAF8F5] border border-[#DDD7CD] text-slate-900 text-xs rounded-lg p-2 font-bold focus:ring-indigo-500"
              value={selectedModelId}
              onChange={(e) => setSelectedModelId(e.target.value)}
            >
              {models.map((m) => (
                <option key={m.id} value={m.id}>{m.name}</option>
              ))}
            </select>
          </div>

          <button
            onClick={() => setIsModalOpen(true)}
            className="bg-amber-50 hover:bg-amber-100/90 text-amber-900 border border-amber-300 text-xs font-bold px-3 py-2.5 rounded-xl shadow-xs flex items-center gap-1.5 transition"
          >
            <PlusCircle className="w-4 h-4 text-amber-700" />
            + Nuevo Modelo
          </button>
        </div>
      </header>

      {/* Banner de Información del Modelo Seleccionado */}
      <div className="bg-gradient-to-r from-[#FAF6EE] via-[#F5EFE6] to-[#FFF] border border-[#E2DDD5] rounded-2xl p-6 shadow-atelier mb-8">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div className="max-w-3xl">
            <span className="text-[10px] font-bold tracking-widest uppercase text-amber-800 bg-amber-100/90 px-2.5 py-0.5 rounded-full border border-amber-300 inline-block mb-1.5">
              Modelo Activo • {activeModel?.system === 'superior' ? 'Educación Superior' : 'Subsistema Regular'}
            </span>
            <h2 className="font-editorial font-bold text-slate-900 text-xl">
              {activeModel?.name || 'Cargando modelo...'}
            </h2>
            <p className="text-xs text-slate-600 mt-1 leading-relaxed">
              {activeModel?.description}
            </p>
          </div>
          
          <div className="flex gap-2 flex-shrink-0">
            <button
              onClick={handleCopyPrompt}
              className="bg-slate-900 text-amber-300 hover:bg-slate-800 font-bold px-4 py-2.5 rounded-xl text-xs flex items-center gap-1.5 shadow-sm transition"
            >
              {copiedPrompt ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4 text-amber-400" />}
              {copiedPrompt ? '¡Megaprompt Copiado!' : 'Copiar Megaprompt'}
            </button>
          </div>
        </div>
      </div>

      {/* Feedback Toast */}
      {feedback && (
        <div className={`mb-6 p-4 rounded-2xl border text-xs flex items-center gap-3 shadow-xs ${
          feedback.type === 'success'
            ? 'bg-emerald-50 border-emerald-300 text-emerald-900'
            : 'bg-rose-50 border-rose-300 text-rose-900'
        }`}>
          {feedback.type === 'success' ? (
            <CheckCircle2 className="w-5 h-5 text-emerald-600 flex-shrink-0" />
          ) : (
            <AlertCircle className="w-5 h-5 text-rose-600 flex-shrink-0" />
          )}
          <span className="font-semibold">{feedback.message}</span>
        </div>
      )}

      {/* Grid Principal: Formulario de Parámetros & Ecosistema de Carpetas */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Columna Izquierda: Parámetros y Generación */}
        <div className="lg:col-span-1 space-y-6">
          <div className="bg-white p-6 rounded-2xl border border-[#E2DDD5] shadow-atelier space-y-4">
            <h3 className="font-editorial font-bold text-slate-900 text-base flex items-center gap-2 border-b border-[#EFEAE1] pb-3">
              <BookOpen className="w-4 h-4 text-amber-700" />
              Parámetros del Módulo
            </h3>

            <div className="space-y-3 text-xs">
              <div>
                <label className="font-bold text-slate-700 block mb-1">Código del Módulo:</label>
                <input
                  type="text"
                  value={params.codigo_modulo}
                  onChange={(e) => setParams({ ...params, codigo_modulo: e.target.value })}
                  className="w-full p-2.5 bg-[#FAF8F5] border border-[#DDD7CD] rounded-xl font-mono text-slate-900"
                />
              </div>

              <div>
                <label className="font-bold text-slate-700 block mb-1">Docente Titular:</label>
                <input
                  type="text"
                  value={params.docente}
                  onChange={(e) => setParams({ ...params, docente: e.target.value })}
                  className="w-full p-2.5 bg-[#FAF8F5] border border-[#DDD7CD] rounded-xl text-slate-900"
                />
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="font-bold text-slate-700 block mb-1">Periodo:</label>
                  <input
                    type="text"
                    value={params.periodo}
                    onChange={(e) => setParams({ ...params, periodo: e.target.value })}
                    className="w-full p-2.5 bg-[#FAF8F5] border border-[#DDD7CD] rounded-xl text-slate-900"
                  />
                </div>
                <div>
                  <label className="font-bold text-slate-700 block mb-1">Carga Horaria:</label>
                  <input
                    type="text"
                    value={params.duracion_horas}
                    onChange={(e) => setParams({ ...params, duracion_horas: e.target.value })}
                    className="w-full p-2.5 bg-[#FAF8F5] border border-[#DDD7CD] rounded-xl text-slate-900"
                  />
                </div>
              </div>

              <div>
                <label className="font-bold text-slate-700 block mb-1">Problema del Contexto Real:</label>
                <textarea
                  rows={2}
                  value={params.problema_contexto}
                  onChange={(e) => setParams({ ...params, problema_contexto: e.target.value })}
                  className="w-full p-2.5 bg-[#FAF8F5] border border-[#DDD7CD] rounded-xl text-slate-900"
                />
              </div>

              <div>
                <label className="font-bold text-slate-700 block mb-1">Estudiantes con Adecuación AC / DUA:</label>
                <input
                  type="text"
                  value={params.estudiantes_ac}
                  onChange={(e) => setParams({ ...params, estudiantes_ac: e.target.value })}
                  placeholder="Ej: E. L. (Adaptación visual)"
                  className="w-full p-2.5 bg-[#FAF8F5] border border-[#DDD7CD] rounded-xl text-slate-900"
                />
              </div>
            </div>

            {/* Botón de Generación en Vivo */}
            <div className="pt-2">
              <button
                onClick={handleGenerateDraft}
                disabled={isGenerating}
                className="w-full bg-slate-900 text-amber-300 hover:bg-slate-800 font-bold py-3 px-4 rounded-xl text-xs flex items-center justify-center gap-2 shadow-sm transition disabled:opacity-50"
              >
                {isGenerating ? (
                  <RefreshCw className="w-4 h-4 animate-spin text-amber-400" />
                ) : (
                  <Sparkles className="w-4 h-4 text-amber-400" />
                )}
                {isGenerating ? 'Generando Plan con IA...' : '⚡ Generar Borrador con IA'}
              </button>
            </div>
          </div>

          {/* Ecosistema Google Drive y Carpetas */}
          <div className="bg-white p-6 rounded-2xl border border-[#E2DDD5] shadow-atelier space-y-3 text-xs">
            <h4 className="font-editorial font-bold text-slate-900 text-sm flex items-center gap-2">
              <FolderInput className="w-4 h-4 text-amber-700" />
              Ecosistema de Carpetas & Google Drive
            </h4>
            <p className="text-slate-500 text-[11px] leading-relaxed">
              El script inyecta el borrador en la plantilla oficial y deposita el producto en la salida.
            </p>

            <div className="space-y-2 pt-1">
              <a
                href={activeModel?.drive_config?.input_folder || 'https://drive.google.com'}
                target="_blank"
                rel="noreferrer"
                className="flex items-center justify-between p-2.5 rounded-xl border border-[#E2DDD5] bg-[#FAF8F5] hover:bg-[#F2EDE5] transition text-slate-700 font-semibold"
              >
                <span className="flex items-center gap-2">
                  <FolderInput className="w-4 h-4 text-amber-700" /> Carpeta Entrada (Drive)
                </span>
                <ExternalLink className="w-3.5 h-3.5 text-slate-400" />
              </a>

              <a
                href={activeModel?.drive_config?.output_folder || 'https://drive.google.com'}
                target="_blank"
                rel="noreferrer"
                className="flex items-center justify-between p-2.5 rounded-xl border border-[#E2DDD5] bg-[#FAF8F5] hover:bg-[#F2EDE5] transition text-slate-700 font-semibold"
              >
                <span className="flex items-center gap-2">
                  <FolderOutput className="w-4 h-4 text-emerald-700" /> Carpeta Salida (Drive)
                </span>
                <ExternalLink className="w-3.5 h-3.5 text-slate-400" />
              </a>

              <div className="p-2.5 rounded-xl border border-[#E2DDD5] bg-slate-50 text-slate-600 text-[11px]">
                <span className="font-bold block text-slate-800 mb-0.5">Plantilla Vinculada:</span>
                <span className="font-mono text-[10px] text-slate-500 block truncate">
                  {activeModel?.drive_config?.template_id || 'Plantilla_CBL_Modular.docx'}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Columna Derecha: Visor de Borrador Estructurado y Procesamiento */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white p-6 rounded-2xl border border-[#E2DDD5] shadow-atelier space-y-4 flex flex-col h-full">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#EFEAE1] pb-3">
              <div>
                <h3 className="font-editorial font-bold text-slate-900 text-lg flex items-center gap-2">
                  <FileText className="w-5 h-5 text-amber-700" />
                  Borrador Estructurado por Etiquetas V14
                </h3>
                <p className="text-slate-500 text-xs mt-0.5">
                  Texto etiquetado con delimitadores <code className="text-amber-800 font-mono text-[11px]">[INICIO:TAG]...[FIN:TAG]</code> listo para inyección.
                </p>
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={() => {
                    navigator.clipboard.writeText(draftText);
                    setCopiedDraft(true);
                    setTimeout(() => setCopiedDraft(false), 2000);
                  }}
                  disabled={!draftText}
                  className="px-3 py-1.5 bg-[#FAF8F5] border border-[#DDD7CD] text-slate-700 hover:bg-[#F2EDE5] rounded-xl text-xs font-semibold flex items-center gap-1.5 transition disabled:opacity-50"
                >
                  {copiedDraft ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
                  {copiedDraft ? '¡Copiado!' : 'Copiar'}
                </button>

                <button
                  onClick={handleProcessOutput}
                  disabled={!draftText || isProcessing}
                  className="px-4 py-2 bg-emerald-700 hover:bg-emerald-800 text-white font-bold rounded-xl text-xs flex items-center gap-1.5 shadow-sm transition disabled:opacity-50"
                >
                  {isProcessing ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Play className="w-3.5 h-3.5" />}
                  {isProcessing ? 'Procesando...' : '⚙️ Procesar Documento Final'}
                </button>
              </div>
            </div>

            {/* Área de Texto del Borrador */}
            <div className="flex-1 min-h-[360px]">
              <textarea
                value={draftText}
                onChange={(e) => setDraftText(e.target.value)}
                placeholder="El borrador generado con IA aparecerá aquí con las etiquetas [INICIO:TAG]...[FIN:TAG]..."
                className="w-full h-full min-h-[360px] p-4 bg-[#FAF8F5] border border-[#DDD7CD] rounded-xl font-mono text-xs text-slate-800 leading-relaxed focus:outline-none focus:ring-2 focus:ring-amber-500/50"
              />
            </div>

            {/* Panel de Descarga del Documento Procesado */}
            <div className="bg-[#FAF8F5] border border-[#E2DDD5] p-4 rounded-xl flex flex-col sm:flex-row items-center justify-between gap-3">
              <div className="flex items-center gap-3 text-xs">
                <div className="w-9 h-9 rounded-xl bg-emerald-100 text-emerald-800 flex items-center justify-center font-bold flex-shrink-0">
                  DOCX
                </div>
                <div>
                  <span className="font-bold text-slate-900 block">
                    Documento Oficial en Carpeta de Salida:
                  </span>
                  <span className="text-[11px] text-slate-500 font-mono">
                    {outputFiles.length > 0 ? outputFiles[0] : 'Pendiente de procesar borrador.'}
                  </span>
                </div>
              </div>

              <button
                onClick={() => window.open(`/api/planning/subject/${encodeURIComponent(selectedSubject)}/download-final`, '_blank')}
                disabled={outputFiles.length === 0}
                className="w-full sm:w-auto px-5 py-2.5 bg-slate-900 text-amber-300 hover:bg-slate-800 font-bold rounded-xl text-xs flex items-center justify-center gap-2 shadow-xs transition disabled:opacity-40"
              >
                <Download className="w-4 h-4" />
                Descargar Plan Oficial (.docx)
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Modal: Crear Nuevo Modelo de Planificación */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-xs p-4 animate-in fade-in">
          <div className="bg-white border border-[#E2DDD5] w-full max-w-2xl rounded-2xl shadow-2xl p-6 space-y-4 max-h-[90vh] overflow-y-auto">
            <h3 className="font-editorial font-bold text-lg text-slate-900 border-b pb-2">
              Crear Nuevo Modelo de Planificación Reutilizable
            </h3>

            <div className="space-y-3 text-xs">
              <div>
                <label className="font-bold text-slate-700 block mb-1">Nombre del Modelo:</label>
                <input
                  type="text"
                  placeholder="Ej: Planificación Basada en Proyectos (ABP)"
                  value={newModel.name}
                  onChange={(e) => setNewModel({ ...newModel, name: e.target.value })}
                  className="w-full p-2.5 bg-[#FAF8F5] border border-[#DDD7CD] rounded-xl text-slate-900"
                />
              </div>

              <div>
                <label className="font-bold text-slate-700 block mb-1">Descripción Pedagógica:</label>
                <textarea
                  rows={2}
                  placeholder="Objetivos pedagógicos, metodología y estructura general..."
                  value={newModel.description}
                  onChange={(e) => setNewModel({ ...newModel, description: e.target.value })}
                  className="w-full p-2.5 bg-[#FAF8F5] border border-[#DDD7CD] rounded-xl text-slate-900"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="font-bold text-slate-700 block mb-1">Carpeta Entrada Drive (URL):</label>
                  <input
                    type="text"
                    placeholder="https://drive.google.com/..."
                    value={newModel.drive_config.input_folder}
                    onChange={(e) => setNewModel({ ...newModel, drive_config: { ...newModel.drive_config, input_folder: e.target.value } })}
                    className="w-full p-2.5 bg-[#FAF8F5] border border-[#DDD7CD] rounded-xl text-slate-900"
                  />
                </div>
                <div>
                  <label className="font-bold text-slate-700 block mb-1">Carpeta Salida Drive (URL):</label>
                  <input
                    type="text"
                    placeholder="https://drive.google.com/..."
                    value={newModel.drive_config.output_folder}
                    onChange={(e) => setNewModel({ ...newModel, drive_config: { ...newModel.drive_config, output_folder: e.target.value } })}
                    className="w-full p-2.5 bg-[#FAF8F5] border border-[#DDD7CD] rounded-xl text-slate-900"
                  />
                </div>
              </div>

              <div>
                <label className="font-bold text-slate-700 block mb-1">Megaprompt Maestro con Variables:</label>
                <textarea
                  rows={4}
                  placeholder="Instrucciones para la IA con variables como {{MATERIA}} y etiquetas [INICIO:TAG]...[FIN:TAG]..."
                  value={newModel.prompt_template}
                  onChange={(e) => setNewModel({ ...newModel, prompt_template: e.target.value })}
                  className="w-full p-2.5 bg-[#FAF8F5] border border-[#DDD7CD] rounded-xl font-mono text-slate-900 text-[11px]"
                />
              </div>
            </div>

            <div className="flex justify-end gap-2 pt-3 border-t">
              <button
                onClick={() => setIsModalOpen(false)}
                className="px-4 py-2 text-xs font-semibold text-slate-600 bg-slate-100 hover:bg-slate-200 rounded-xl transition"
              >
                Cancelar
              </button>
              <button
                onClick={handleSaveNewModel}
                className="px-5 py-2 text-xs font-bold text-amber-300 bg-slate-900 hover:bg-slate-800 rounded-xl transition shadow-xs"
              >
                Guardar Modelo
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
