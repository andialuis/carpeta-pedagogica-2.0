'use client';
import { useState, useEffect } from 'react';
import { 
  Award, CheckCircle2, AlertCircle, FileDown, Sparkles, 
  ShieldAlert, UserCheck, Sliders, Layers, RefreshCw, 
  PlusCircle, BookOpen, HeartHandshake, Eye, Check, Copy,
  Search, User, Settings2, FileText, CheckCheck, Clock
} from 'lucide-react';

export default function EvaluacionPage() {
  const [subjects, setSubjects] = useState<any[]>([]);
  const [selectedSubject, setSelectedSubject] = useState<string>('');
  const [activeTab, setActiveTab] = useState<'plan_base' | 'adaptaciones_ac' | 'alertas' | 'galeria' | 'rubricas'>('plan_base');

  const [planData, setPlanData] = useState<any>(null);
  const [catalog, setCatalog] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [feedback, setFeedback] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  // Estados para Personalización DUA por Estudiante
  const [studentsDua, setStudentsDua] = useState<any[]>([]);
  const [selectedDuaStudent, setSelectedDuaStudent] = useState<any>(null);
  const [isDuaModalOpen, setIsDuaModalOpen] = useState(false);
  const [subTabAc, setSubTabAc] = useState<'matriz_estudiantes' | 'casos_ac'>('matriz_estudiantes');
  const [duaFilter, setDuaFilter] = useState<'todos' | 'alertas' | 'faltantes'>('todos');
  const [duaSearch, setDuaSearch] = useState('');
  const [isSavingDua, setIsSavingDua] = useState(false);

  // Nuevo registro de AC
  const [newAc, setNewAc] = useState({
    estudiante_iniciales: '',
    diagnostico_necesidad: '',
    ajustes_ponderacion: { formativa: 45, sumativa: 35 },
    instrumentos_diferenciados: ['rubrica_cbl', 'registro_sudor'],
    observaciones: ''
  });
  const [showAddAc, setShowAddAc] = useState(false);

  // Generador de rúbricas
  const [rubricRequest, setRubricRequest] = useState({
    actividad_nombre: 'Perfil de Investigación Científica',
    competencia: 'Formulación y sustentación metodológica rigurosa'
  });
  const [generatedRubric, setGeneratedRubric] = useState<any>(null);
  const [isGeneratingRubric, setIsGeneratingRubric] = useState(false);
  const [isSuggestingDua, setIsSuggestingDua] = useState(false);
  const [isExportingRubric, setIsExportingRubric] = useState(false);

  useEffect(() => {
    fetchInitialData();
  }, []);

  useEffect(() => {
    if (selectedSubject) {
      fetchSubjectPlan(selectedSubject);
      fetchStudentsDua(selectedSubject);
    }
  }, [selectedSubject]);

  const fetchInitialData = async () => {
    setIsLoading(true);
    try {
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

      const resCat = await fetch('/api/instruments/catalog', { cache: 'no-store' });
      const dataCat = await resCat.json();
      setCatalog(dataCat.catalog || []);
    } catch (e) {
      console.error('Error cargando catálogo de evaluación', e);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchSubjectPlan = async (subject: string) => {
    try {
      const res = await fetch(`/api/evaluation/plan/${encodeURIComponent(subject)}`, { cache: 'no-store' });
      const data = await res.json();
      setPlanData(data);
    } catch (e) {
      console.error('Error cargando plan de evaluación', e);
    }
  };

  const fetchStudentsDua = async (subject: string) => {
    try {
      const res = await fetch(`/api/evaluation/students-dua/${encodeURIComponent(subject)}`, { cache: 'no-store' });
      const data = await res.json();
      setStudentsDua(data.students || []);
    } catch (e) {
      console.error('Error cargando estudiantes DUA', e);
    }
  };

  const handleOpenDuaModal = (student: any) => {
    setSelectedDuaStudent({ ...student });
    setIsDuaModalOpen(true);
  };

  const handleSaveStudentDua = async () => {
    if (!selectedDuaStudent) return;
    setIsSavingDua(true);
    try {
      const res = await fetch(`/api/evaluation/students-dua/${encodeURIComponent(selectedSubject)}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          student_id: selectedDuaStudent.id,
          profile: selectedDuaStudent
        })
      });
      const data = await res.json();
      if (data.success) {
        setIsDuaModalOpen(false);
        fetchStudentsDua(selectedSubject);
        setFeedback({ type: 'success', message: `¡Ajustes DUA guardados para el estudiante ${selectedDuaStudent.iniciales}!` });
      }
    } catch (e: any) {
      alert(`Error guardando DUA: ${e.message}`);
    } finally {
      setIsSavingDua(false);
    }
  };

  const handleExportDuaDocx = () => {
    window.open(`/api/evaluation/students-dua/${encodeURIComponent(selectedSubject)}/export-docx`, '_blank');
  };

  const handleSavePlan = async () => {
    if (!planData) return;
    setIsSaving(true);
    setFeedback(null);
    try {
      const res = await fetch(`/api/evaluation/plan/${encodeURIComponent(selectedSubject)}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(planData)
      });
      const data = await res.json();
      if (data.success) {
        setFeedback({ type: 'success', message: '¡Plan de Evaluación y Adaptaciones guardado exitosamente!' });
        fetchSubjectPlan(selectedSubject);
      } else {
        setFeedback({ type: 'error', message: data.message || 'Error guardando plan.' });
      }
    } catch (e: any) {
      setFeedback({ type: 'error', message: `Error: ${e.message}` });
    } finally {
      setIsSaving(false);
    }
  };

  const handleAddAc = () => {
    if (!newAc.estudiante_iniciales.trim()) return;
    const currentAcs = planData?.adaptaciones_curriculares_ac || [];
    const updated = [...currentAcs, { ...newAc, id: `ac_${Date.now()}` }];
    setPlanData({ ...planData, adaptaciones_curriculares_ac: updated });
    setShowAddAc(false);
    setNewAc({
      estudiante_iniciales: '',
      diagnostico_necesidad: '',
      ajustes_ponderacion: { formativa: 45, sumativa: 35 },
      instrumentos_diferenciados: ['rubrica_cbl', 'registro_sudor'],
      observaciones: ''
    });
  };

  const handleGenerateRubric = async () => {
    setIsGeneratingRubric(true);
    try {
      const res = await fetch(`/api/evaluation/generate-rubric/${encodeURIComponent(selectedSubject)}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(rubricRequest)
      });
      const data = await res.json();
      setGeneratedRubric(data);
    } catch (e) {
      console.error('Error generando rúbrica', e);
    } finally {
      setIsGeneratingRubric(false);
    }
  };

  const handleAiSuggestDua = async () => {
    if (!selectedDuaStudent || isSuggestingDua) return;
    setIsSuggestingDua(true);
    try {
      const res = await fetch(`/api/evaluation/suggest-dua/${encodeURIComponent(selectedSubject)}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          student_id: selectedDuaStudent.id,
          iniciales: selectedDuaStudent.iniciales,
          promedio: selectedDuaStudent.promedio || 0,
          iteraciones: selectedDuaStudent.iteraciones || 0,
          alerta_outsourcing: !!selectedDuaStudent.alerta_outsourcing,
          riesgo_alto: !!selectedDuaStudent.riesgo_alto,
          observaciones_previas: selectedDuaStudent.observaciones || ''
        })
      });
      const data = await res.json();
      setSelectedDuaStudent((prev: any) => ({
        ...prev,
        principio_1_compromiso: data.principio_1_compromiso || prev.principio_1_compromiso,
        principio_2_representacion: data.principio_2_representacion || prev.principio_2_representacion,
        principio_3_accion_expresion: data.principio_3_accion_expresion || prev.principio_3_accion_expresion,
        instrumento_clave: data.instrumento_clave || prev.instrumento_clave,
        tiempo_extendido: data.tiempo_extendido !== undefined ? data.tiempo_extendido : prev.tiempo_extendido,
        evaluacion_fragmentada: data.evaluacion_fragmentada !== undefined ? data.evaluacion_fragmentada : prev.evaluacion_fragmentada,
        observaciones: data.observaciones || prev.observaciones
      }));
    } catch (e) {
      console.error('Error al sugerir adaptación DUA', e);
    } finally {
      setIsSuggestingDua(false);
    }
  };

  const handleExportRubricDocx = async () => {
    if (!generatedRubric || isExportingRubric) return;
    setIsExportingRubric(true);
    try {
      const res = await fetch('/api/evaluation/export-rubric-docx', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          actividad: generatedRubric.actividad || rubricRequest.actividad_nombre,
          competencia: generatedRubric.competencia || rubricRequest.competencia,
          criterios: generatedRubric.criterios || []
        })
      });
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `RUBRICA_${encodeURIComponent(rubricRequest.actividad_nombre.slice(0, 20))}.docx`;
      document.body.appendChild(a);
      a.click();
      a.remove();
    } catch (e) {
      console.error('Error al descargar rúbrica', e);
    } finally {
      setIsExportingRubric(false);
    }
  };

  const handleDownload = (instrumentId: string) => {
    window.open(`/api/instruments/download/${instrumentId}`, '_blank');
  };

  // Cálculo total de ponderaciones
  const etapas = planData?.plan_base?.etapas || [];
  const sumaPonderaciones = etapas.reduce((acc: number, cur: any) => acc + (Number(cur.ponderacion) || 0), 0);
  const esSumaValida = sumaPonderaciones === 100;

  return (
    <div className="text-slate-800 pb-16 font-sans-clean">
      {/* Cabecera Atelier */}
      <header className="mb-8 flex flex-col md:flex-row md:justify-between md:items-center gap-4 border-b border-[#E8E3DA] pb-5">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-[10px] font-bold tracking-widest uppercase text-amber-800 bg-amber-100/80 px-2.5 py-0.5 rounded-full border border-amber-300">
              Evaluación Auténtica & DUA
            </span>
            <span className="text-[10px] font-medium text-slate-400">• Efecto Hattie d = 1.16</span>
          </div>
          <h1 className="text-3xl font-bold font-editorial text-slate-900 flex items-center gap-3">
            <Award className="w-8 h-8 text-amber-700" />
            Plan de Evaluación y Adaptaciones
          </h1>
          <p className="text-slate-500 text-sm mt-0.5 font-medium">
            Diseño del plan de evaluación por asignatura, adecuaciones curriculares (AC), alertas anti-outsourcing y DUA
          </p>
        </div>

        {/* Selector de Asignatura */}
        <div className="flex items-center gap-3">
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

          <button
            onClick={handleSavePlan}
            disabled={isSaving || !esSumaValida}
            className="bg-slate-900 text-amber-300 hover:bg-slate-800 font-bold px-4 py-2.5 rounded-xl text-xs flex items-center gap-1.5 shadow-sm transition disabled:opacity-50"
          >
            {isSaving ? <RefreshCw className="w-4 h-4 animate-spin" /> : <CheckCircle2 className="w-4 h-4 text-emerald-400" />}
            {isSaving ? 'Guardando...' : 'Guardar Plan'}
          </button>
        </div>
      </header>

      {/* Banner Proactivo: Detección de Instrumentos Faltantes */}
      {planData?.instrumentos_faltantes && planData.instrumentos_faltantes.length > 0 && (
        <div className="bg-amber-50/80 border border-amber-300/80 rounded-2xl p-5 mb-8 shadow-xs">
          <div className="flex items-start gap-3.5">
            <div className="p-2 rounded-xl bg-amber-100 text-amber-800 flex-shrink-0 mt-0.5">
              <AlertCircle className="w-5 h-5 text-amber-700" />
            </div>
            <div className="flex-1 text-xs space-y-1">
              <h3 className="font-bold text-amber-950 text-sm">
                Sugerencia Pedagógica Proactiva: Datos e Instrumentos Faltantes
              </h3>
              <p className="text-slate-600 leading-relaxed">
                Para personalizar la evaluación según DUA y medir el esfuerzo real (Sudor Intelectual), se detectaron instrumentos no cargados aún en la carpeta de la asignatura:
              </p>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-2.5 pt-2">
                {planData.instrumentos_faltantes.map((ins: any, i: number) => (
                  <div key={i} className="bg-white p-3 rounded-xl border border-amber-200/80 flex flex-col justify-between">
                    <div>
                      <span className="font-bold text-slate-800 block text-xs mb-0.5">{ins.name}</span>
                      <p className="text-[11px] text-slate-500 line-clamp-2">{ins.motivo}</p>
                    </div>
                    <button
                      onClick={() => handleDownload(ins.instrument_id)}
                      className="mt-2.5 w-full bg-amber-100 hover:bg-amber-200 text-amber-900 font-bold py-1.5 px-2.5 rounded-lg text-[11px] flex items-center justify-center gap-1.5 transition"
                    >
                      <FileDown className="w-3 h-3" /> Descargar Plantilla
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Feedback Toast */}
      {feedback && (
        <div className={`mb-6 p-4 rounded-2xl border text-xs flex items-center gap-3 shadow-xs ${
          feedback.type === 'success' ? 'bg-emerald-50 border-emerald-300 text-emerald-900' : 'bg-rose-50 border-rose-300 text-rose-900'
        }`}>
          {feedback.type === 'success' ? <CheckCircle2 className="w-5 h-5 text-emerald-600 flex-shrink-0" /> : <AlertCircle className="w-5 h-5 text-rose-600 flex-shrink-0" />}
          <span className="font-semibold">{feedback.message}</span>
        </div>
      )}

      {/* Tabs de Navegación del Módulo de Evaluación */}
      <div className="bg-[#EFEAE1]/70 p-1.5 rounded-2xl border border-[#E2DDD5] flex flex-wrap gap-1.5 mb-8 shadow-xs">
        <button
          onClick={() => setActiveTab('plan_base')}
          className={`px-4 py-2 text-xs font-bold rounded-xl transition-all duration-150 flex items-center gap-1.5 ${
            activeTab === 'plan_base' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-600 hover:text-slate-900 hover:bg-white/50'
          }`}
        >
          <Sliders className="w-3.5 h-3.5 text-amber-700" /> Plan Base de la Asignatura
        </button>

        <button
          onClick={() => setActiveTab('adaptaciones_ac')}
          className={`px-4 py-2 text-xs font-bold rounded-xl transition-all duration-150 flex items-center gap-1.5 ${
            activeTab === 'adaptaciones_ac' ? 'bg-white text-indigo-900 shadow-sm' : 'text-slate-600 hover:text-slate-900 hover:bg-white/50'
          }`}
        >
          <HeartHandshake className="w-3.5 h-3.5 text-indigo-600" /> Adaptaciones Curriculares (AC & DUA)
        </button>

        <button
          onClick={() => setActiveTab('alertas')}
          className={`px-4 py-2 text-xs font-bold rounded-xl transition-all duration-150 flex items-center gap-1.5 ${
            activeTab === 'alertas' ? 'bg-white text-rose-900 shadow-sm' : 'text-rose-700 hover:bg-rose-50'
          }`}
        >
          <ShieldAlert className="w-3.5 h-3.5" /> Intervenciones por Alertas
        </button>

        <button
          onClick={() => setActiveTab('galeria')}
          className={`px-4 py-2 text-xs font-bold rounded-xl transition-all duration-150 flex items-center gap-1.5 ${
            activeTab === 'galeria' ? 'bg-white text-emerald-900 shadow-sm' : 'text-slate-600 hover:text-slate-900 hover:bg-white/50'
          }`}
        >
          <BookOpen className="w-3.5 h-3.5 text-emerald-700" /> Galería de Instrumentos (6)
        </button>

        <button
          onClick={() => setActiveTab('rubricas')}
          className={`px-4 py-2 text-xs font-bold rounded-xl transition-all duration-150 flex items-center gap-1.5 ${
            activeTab === 'rubricas' ? 'bg-white text-purple-900 shadow-sm' : 'text-slate-600 hover:text-slate-900 hover:bg-white/50'
          }`}
        >
          <Sparkles className="w-3.5 h-3.5 text-purple-600" /> Generador de Rúbricas CBL
        </button>
      </div>

      {/* CONTENIDO DE PESTAÑAS */}

      {/* PESTAÑA 1: PLAN BASE DE LA MATERIA */}
      {activeTab === 'plan_base' && (
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-2xl border border-[#E2DDD5] shadow-atelier space-y-5">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#EFEAE1] pb-4">
              <div>
                <h3 className="font-editorial font-bold text-slate-900 text-lg">
                  Etapas y Ponderaciones del Plan de Evaluación
                </h3>
                <p className="text-slate-500 text-xs mt-0.5">
                  Define los momentos evaluativos y ponderaciones para <strong>{selectedSubject}</strong>.
                </p>
              </div>

              {/* Indicador de suma 100% */}
              <div className={`px-3.5 py-1.5 rounded-xl border text-xs font-bold flex items-center gap-2 ${
                esSumaValida ? 'bg-emerald-50 border-emerald-300 text-emerald-900' : 'bg-rose-50 border-rose-300 text-rose-900 animate-pulse'
              }`}>
                <span>Total Ponderación:</span>
                <span className="text-sm">{sumaPonderaciones}%</span>
                {esSumaValida ? (
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                ) : (
                  <span className="text-[10px] bg-rose-200 px-1.5 py-0.5 rounded">Debe sumar 100%</span>
                )}
              </div>
            </div>

            {/* Matriz de Etapas */}
            <div className="space-y-4">
              {etapas.map((etapa: any, idx: number) => (
                <div key={idx} className="bg-[#FAF8F5] p-4 rounded-xl border border-[#DDD7CD] flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
                  <div className="flex-1 text-xs space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="w-5 h-5 rounded-full bg-slate-900 text-amber-300 font-bold flex items-center justify-center text-[10px]">
                        {idx + 1}
                      </span>
                      <input
                        type="text"
                        value={etapa.nombre}
                        onChange={(e) => {
                          const updated = [...etapas];
                          updated[idx].nombre = e.target.value;
                          setPlanData({ ...planData, plan_base: { ...planData.plan_base, etapas: updated } });
                        }}
                        className="font-bold text-slate-900 bg-white px-2 py-1 rounded border border-[#DDD7CD] text-xs focus:ring-amber-500"
                      />
                      <span className="text-[10px] text-slate-400 bg-slate-200/70 px-2 py-0.5 rounded-full">
                        {etapa.dimension}
                      </span>
                    </div>
                    <p className="text-slate-600 text-[11px] pt-1">{etapa.criterio}</p>
                  </div>

                  <div className="flex items-center gap-4 flex-shrink-0">
                    <div className="flex items-center gap-1.5">
                      <label className="text-xs font-bold text-slate-700">Ponderación:</label>
                      <input
                        type="number"
                        min={0}
                        max={100}
                        value={etapa.ponderacion}
                        onChange={(e) => {
                          const updated = [...etapas];
                          updated[idx].ponderacion = Number(e.target.value);
                          setPlanData({ ...planData, plan_base: { ...planData.plan_base, etapas: updated } });
                        }}
                        className="w-16 p-1.5 text-center font-bold text-slate-900 bg-white border border-[#DDD7CD] rounded-lg text-xs"
                      />
                      <span className="text-xs font-bold text-slate-500">%</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* PESTAÑA 2: ADAPTACIONES CURRICULARES (AC & DUA) */}
      {activeTab === 'adaptaciones_ac' && (
        <div className="space-y-6">
          {/* Sub-navegación: Matriz Completa vs Casos Formales */}
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 bg-white p-4 rounded-2xl border border-[#E2DDD5] shadow-xs">
            <div className="flex items-center gap-2 bg-[#FAF8F5] p-1 rounded-xl border border-[#E8E3DA]">
              <button
                onClick={() => setSubTabAc('matriz_estudiantes')}
                className={`px-3.5 py-1.5 rounded-lg text-xs font-bold transition flex items-center gap-1.5 ${
                  subTabAc === 'matriz_estudiantes' ? 'bg-indigo-900 text-white shadow-xs' : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                <UserCheck className="w-3.5 h-3.5" />
                Matriz DUA por Estudiante ({studentsDua.length})
              </button>
              <button
                onClick={() => setSubTabAc('casos_ac')}
                className={`px-3.5 py-1.5 rounded-lg text-xs font-bold transition flex items-center gap-1.5 ${
                  subTabAc === 'casos_ac' ? 'bg-indigo-900 text-white shadow-xs' : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                <HeartHandshake className="w-3.5 h-3.5" />
                Adecuaciones Formales ({(planData?.adaptaciones_curriculares_ac || []).length})
              </button>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={handleExportDuaDocx}
                className="bg-slate-900 hover:bg-slate-800 text-amber-300 font-bold px-3.5 py-2 rounded-xl text-xs flex items-center gap-1.5 transition shadow-xs"
              >
                <FileText className="w-3.5 h-3.5" />
                Descargar Matriz DUA (.docx)
              </button>
              {subTabAc === 'casos_ac' && (
                <button
                  onClick={() => setShowAddAc(true)}
                  className="bg-indigo-50 hover:bg-indigo-100 text-indigo-900 border border-indigo-300 font-bold px-3 py-2 rounded-xl text-xs flex items-center gap-1.5 transition"
                >
                  <PlusCircle className="w-3.5 h-3.5 text-indigo-700" /> + Añadir Caso
                </button>
              )}
            </div>
          </div>

          {/* VISTA A: MATRIZ COMPLETA DUA POR ESTUDIANTE */}
          {subTabAc === 'matriz_estudiantes' && (
            <div className="space-y-4">
              {/* Barra de Búsqueda y Filtros Rápidos */}
              <div className="bg-white p-4 rounded-2xl border border-[#E2DDD5] shadow-xs flex flex-col md:flex-row items-center justify-between gap-3 text-xs">
                <div className="relative w-full md:w-72">
                  <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
                  <input
                    type="text"
                    placeholder="Buscar por iniciales o ID (ej: Est_012)..."
                    value={duaSearch}
                    onChange={(e) => setDuaSearch(e.target.value)}
                    className="w-full pl-9 pr-3 py-2 bg-[#FAF8F5] border border-[#DDD7CD] rounded-xl text-slate-800 text-xs focus:ring-indigo-500"
                  />
                </div>

                <div className="flex items-center gap-2 w-full md:w-auto overflow-x-auto pb-1 md:pb-0">
                  <span className="text-slate-400 font-bold text-[11px]">Filtrar:</span>
                  <button
                    onClick={() => setDuaFilter('todos')}
                    className={`px-3 py-1 rounded-lg font-bold text-[11px] transition ${
                      duaFilter === 'todos' ? 'bg-slate-900 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                    }`}
                  >
                    Todos ({studentsDua.length})
                  </button>
                  <button
                    onClick={() => setDuaFilter('alertas')}
                    className={`px-3 py-1 rounded-lg font-bold text-[11px] transition ${
                      duaFilter === 'alertas' ? 'bg-rose-700 text-white' : 'bg-rose-50 text-rose-800 border border-rose-200 hover:bg-rose-100'
                    }`}
                  >
                    Con Alertas ({studentsDua.filter(s => s.alerta_outsourcing || s.riesgo_alto).length})
                  </button>
                  <button
                    onClick={() => setDuaFilter('faltantes')}
                    className={`px-3 py-1 rounded-lg font-bold text-[11px] transition ${
                      duaFilter === 'faltantes' ? 'bg-amber-700 text-white' : 'bg-amber-50 text-amber-900 border border-amber-200 hover:bg-amber-100'
                    }`}
                  >
                    Faltan Instrumentos ({studentsDua.filter(s => s.estado_datos === 'requiere_instrumentos').length})
                  </button>
                </div>
              </div>

              {/* Grid de Estudiantes */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {studentsDua
                  .filter(st => {
                    const matchSearch = st.iniciales.toLowerCase().includes(duaSearch.toLowerCase()) || 
                                        st.id.toLowerCase().includes(duaSearch.toLowerCase());
                    if (!matchSearch) return false;
                    if (duaFilter === 'alertas') return st.alerta_outsourcing || st.riesgo_alto;
                    if (duaFilter === 'faltantes') return st.estado_datos === 'requiere_instrumentos';
                    return true;
                  })
                  .map((st) => (
                    <div 
                      key={st.id} 
                      className={`bg-white rounded-2xl border p-4 shadow-atelier flex flex-col justify-between transition hover:shadow-md ${
                        st.alerta_outsourcing ? 'border-rose-300 bg-gradient-to-b from-white to-rose-50/20' : 
                        st.riesgo_alto ? 'border-amber-300 bg-gradient-to-b from-white to-amber-50/20' : 
                        'border-[#E2DDD5]'
                      }`}
                    >
                      <div className="space-y-3">
                        {/* Cabecera Tarjeta Estudiante */}
                        <div className="flex items-start justify-between gap-2 border-b border-[#EFEAE1] pb-2.5">
                          <div className="flex items-center gap-2.5">
                            <div className={`w-9 h-9 rounded-xl font-bold flex items-center justify-center text-xs flex-shrink-0 ${
                              st.alerta_outsourcing ? 'bg-rose-100 text-rose-800' :
                              st.riesgo_alto ? 'bg-amber-100 text-amber-800' :
                              'bg-indigo-100 text-indigo-900'
                            }`}>
                              {st.iniciales.replace(/\s+/g, '')}
                            </div>
                            <div>
                              <span className="font-bold text-slate-900 text-sm block">
                                {st.iniciales}
                              </span>
                              <span className="text-[10px] font-mono text-slate-400">
                                {st.id} • Privacidad DUA
                              </span>
                            </div>
                          </div>

                          <div className="text-right">
                            <span className="text-xs font-bold text-slate-800 block">
                              {st.promedio} pts
                            </span>
                            <span className="text-[10px] text-slate-400">
                              {st.iteraciones} iteraciones
                            </span>
                          </div>
                        </div>

                        {/* Alerta de Analítica */}
                        {st.alerta_outsourcing && (
                          <div className="bg-rose-50 border border-rose-200 p-2 rounded-xl text-[11px] text-rose-900 flex items-center gap-1.5 font-semibold">
                            <ShieldAlert className="w-3.5 h-3.5 text-rose-600 flex-shrink-0" />
                            Alerta: Outsourcing Cognitivo detectado
                          </div>
                        )}
                        {st.riesgo_alto && (
                          <div className="bg-amber-50 border border-amber-200 p-2 rounded-xl text-[11px] text-amber-900 flex items-center gap-1.5 font-semibold">
                            <AlertCircle className="w-3.5 h-3.5 text-amber-600 flex-shrink-0" />
                            Alerta: Riesgo Severo de Rezago
                          </div>
                        )}

                        {/* Banner de Instrumentos Faltantes */}
                        {st.instrumentos_faltantes && st.instrumentos_faltantes.length > 0 ? (
                          <div className="bg-[#FAF6EE] border border-amber-200/90 rounded-xl p-2.5 space-y-1 text-[11px]">
                            <span className="font-bold text-amber-950 block">
                              ⚠️ Faltan datos para personalizar DUA:
                            </span>
                            <div className="flex flex-wrap gap-1.5 pt-1">
                              {st.instrumentos_faltantes.map((ins: any) => (
                                <button
                                  key={ins.id}
                                  onClick={() => handleDownload(ins.id)}
                                  className="bg-white hover:bg-amber-100 text-amber-900 border border-amber-300 px-2 py-0.5 rounded text-[10px] font-bold flex items-center gap-1 transition shadow-2xs"
                                  title={ins.motivo}
                                >
                                  <FileDown className="w-3 h-3 text-amber-700" /> {ins.name}
                                </button>
                              ))}
                            </div>
                          </div>
                        ) : (
                          <div className="text-[10px] text-emerald-700 font-semibold flex items-center gap-1">
                            <CheckCheck className="w-3.5 h-3.5" /> Datos de contexto y esfuerzo completos
                          </div>
                        )}

                        {/* Vías DUA Actuales */}
                        <div className="bg-[#FAF8F5] p-2.5 rounded-xl border border-[#E8E3DA] space-y-1.5 text-[11px]">
                          <div>
                            <span className="font-bold text-slate-700 block">1. Compromiso:</span>
                            <p className="text-slate-600 line-clamp-1">{st.principio_1_compromiso}</p>
                          </div>
                          <div>
                            <span className="font-bold text-slate-700 block">2. Representación:</span>
                            <p className="text-slate-600 line-clamp-1">{st.principio_2_representacion}</p>
                          </div>
                          <div>
                            <span className="font-bold text-slate-700 block">3. Acción y Expresión:</span>
                            <p className="text-slate-600 line-clamp-1">{st.principio_3_accion_expresion}</p>
                          </div>
                          {st.tiempo_extendido && (
                            <span className="inline-block bg-blue-50 text-blue-800 border border-blue-200 px-2 py-0.5 rounded text-[10px] font-semibold">
                              +25% Tiempo Extendido
                            </span>
                          )}
                        </div>
                      </div>

                      {/* Botón de Acción */}
                      <button
                        onClick={() => handleOpenDuaModal(st)}
                        className="mt-3 w-full bg-slate-900 hover:bg-slate-800 text-amber-300 font-bold py-2 px-3 rounded-xl text-xs flex items-center justify-center gap-1.5 transition shadow-xs"
                      >
                        <Settings2 className="w-3.5 h-3.5 text-amber-400" />
                        Personalizar Vías DUA
                      </button>
                    </div>
                  ))}
              </div>
            </div>
          )}

          {/* VISTA B: CASOS CON ADECUACIÓN FORMAL (AC) */}
          {subTabAc === 'casos_ac' && (
            <div className="bg-white p-6 rounded-2xl border border-[#E2DDD5] shadow-atelier space-y-4">
              <h3 className="font-editorial font-bold text-slate-900 text-lg flex items-center gap-2">
                <HeartHandshake className="w-5 h-5 text-indigo-700" />
                Adecuaciones Curriculares Formales Registradas
              </h3>

              <div className="space-y-3">
                {(planData?.adaptaciones_curriculares_ac || []).map((ac: any, i: number) => (
                  <div key={i} className="bg-[#FAF8F5] p-4 rounded-xl border border-[#DDD7CD] text-xs space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="font-mono font-bold text-indigo-950 bg-indigo-100 px-2.5 py-0.5 rounded-md border border-indigo-200">
                        Estudiante: {ac.estudiante_iniciales}
                      </span>
                      <span className="text-[11px] text-slate-500">
                        Formatos DUA aplicados
                      </span>
                    </div>
                    <p className="text-slate-800 font-semibold">{ac.diagnostico_necesidad}</p>
                    <div className="bg-white p-2.5 rounded-lg border border-[#E2DDD5] text-slate-600 text-[11px]">
                      <span className="font-bold text-slate-800">Ajustes: </span>
                      {ac.observaciones || 'Flexibilización de formato y tiempos de entrega.'}
                    </div>
                  </div>
                ))}
              </div>

              {/* Formulario para añadir AC */}
              {showAddAc && (
                <div className="bg-indigo-50/70 border border-indigo-200 p-4 rounded-xl space-y-3 text-xs animate-in fade-in">
                  <h4 className="font-bold text-indigo-950">Nueva Adecuación Curricular</h4>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div>
                      <label className="font-bold text-slate-700 block mb-1">Iniciales del Estudiante (Privacidad):</label>
                      <input
                        type="text"
                        placeholder="Ej: E. L."
                        value={newAc.estudiante_iniciales}
                        onChange={(e) => setNewAc({ ...newAc, estudiante_iniciales: e.target.value })}
                        className="w-full p-2 bg-white border border-indigo-200 rounded-lg text-slate-900"
                      />
                    </div>
                    <div>
                      <label className="font-bold text-slate-700 block mb-1">Necesidad / Enfoque DUA:</label>
                      <input
                        type="text"
                        placeholder="Ej: Canal visual preferente, tiempos extendidos"
                        value={newAc.diagnostico_necesidad}
                        onChange={(e) => setNewAc({ ...newAc, diagnostico_necesidad: e.target.value })}
                        className="w-full p-2 bg-white border border-indigo-200 rounded-lg text-slate-900"
                      />
                    </div>
                  </div>
                  <div>
                    <label className="font-bold text-slate-700 block mb-1">Observaciones Metodológicas:</label>
                    <input
                      type="text"
                      placeholder="Ej: Rúbrica con opciones de entrega oral o infografía interactiva."
                      value={newAc.observaciones}
                      onChange={(e) => setNewAc({ ...newAc, observaciones: e.target.value })}
                      className="w-full p-2 bg-white border border-indigo-200 rounded-lg text-slate-900"
                    />
                  </div>
                  <div className="flex justify-end gap-2 pt-2">
                    <button
                      onClick={() => setShowAddAc(false)}
                      className="px-3 py-1.5 bg-slate-200 hover:bg-slate-300 rounded-lg text-slate-700"
                    >
                      Cancelar
                    </button>
                    <button
                      onClick={handleAddAc}
                      className="px-4 py-1.5 bg-indigo-900 hover:bg-indigo-800 text-white font-bold rounded-lg"
                    >
                      Agregar Adaptación
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* MODAL INTERACTIVO DE PERSONALIZACIÓN DUA POR ESTUDIANTE */}
      {isDuaModalOpen && selectedDuaStudent && (
        <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white border border-[#E2DDD5] rounded-3xl max-w-2xl w-full p-6 shadow-2xl space-y-4 max-h-[90vh] overflow-y-auto font-sans-clean text-xs animate-in zoom-in-95">
            <div className="flex items-start justify-between border-b border-[#EFEAE1] pb-3">
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-indigo-900 bg-indigo-100 px-2.5 py-0.5 rounded-full">
                  Diseño Universal para el Aprendizaje (CAST 2024)
                </span>
                <h3 className="text-base font-bold font-editorial text-slate-900 mt-1">
                  Personalización DUA: {selectedDuaStudent.iniciales} ({selectedDuaStudent.id})
                </h3>
              </div>
              <button
                onClick={() => setIsDuaModalOpen(false)}
                className="text-slate-400 hover:text-slate-600 text-lg font-bold px-2 py-1"
              >
                ✕
              </button>
            </div>

            {/* Diagnóstico Breve */}
            <div className="bg-[#FAF8F5] p-3 rounded-xl border border-[#E8E3DA] grid grid-cols-3 gap-2 text-center text-[11px]">
              <div>
                <span className="text-slate-400 block">Promedio:</span>
                <span className="font-bold text-slate-800 text-sm">{selectedDuaStudent.promedio} pts</span>
              </div>
              <div>
                <span className="text-slate-400 block">Sudor Intelectual:</span>
                <span className="font-bold text-slate-800 text-sm">{selectedDuaStudent.iteraciones} iter.</span>
              </div>
              <div>
                <span className="text-slate-400 block">Diagnóstico:</span>
                <span className={`font-bold text-xs ${
                  selectedDuaStudent.alerta_outsourcing ? 'text-rose-700' :
                  selectedDuaStudent.riesgo_alto ? 'text-amber-700' : 'text-emerald-700'
                }`}>
                  {selectedDuaStudent.alerta_outsourcing ? 'Outsourcing' : selectedDuaStudent.riesgo_alto ? 'Riesgo' : 'Regular'}
                </span>
              </div>
            </div>

            {/* Asistente IA para sugerir DUA con Gemini */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 p-2.5 bg-gradient-to-r from-amber-50/90 to-indigo-50/90 border border-amber-200/80 rounded-2xl shadow-2xs">
              <div className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-amber-600 flex-shrink-0" />
                <span className="text-[11px] font-bold text-slate-800">
                  ¿Deseas una propuesta didáctica optimizada para este estudiante?
                </span>
              </div>
              <button
                type="button"
                onClick={handleAiSuggestDua}
                disabled={isSuggestingDua}
                className="flex items-center justify-center gap-1.5 text-xs bg-slate-900 text-amber-300 hover:bg-slate-800 font-bold px-3 py-1.5 rounded-xl transition shadow-xs disabled:opacity-50 cursor-pointer"
              >
                {isSuggestingDua ? (
                  <RefreshCw className="w-3.5 h-3.5 animate-spin text-amber-400" />
                ) : (
                  <Sparkles className="w-3.5 h-3.5 text-amber-400" />
                )}
                {isSuggestingDua ? 'Consultando a Gemini...' : '✨ Sugerir con IA'}
              </button>
            </div>

            {/* Principio 1: Compromiso */}
            <div>
              <label className="font-bold text-slate-800 block mb-1">
                Principio 1: Múltiples Formas de Compromiso (Redes Afectivas):
              </label>
              <select
                value={selectedDuaStudent.principio_1_compromiso}
                onChange={(e) => setSelectedDuaStudent({ ...selectedDuaStudent, principio_1_compromiso: e.target.value })}
                className="w-full p-2 bg-[#FAF8F5] border border-[#DDD7CD] rounded-xl text-slate-900 font-semibold"
              >
                <option value="Elección autónoma de subtema investigativo">Elección autónoma de subtema investigativo</option>
                <option value="Trabajo colaborativo en parejas dialógicas con roles rotativos">Trabajo colaborativo en parejas dialógicas con roles rotativos</option>
                <option value="Metas semanales cortas con retroalimentación formativa inmediata">Metas semanales cortas con retroalimentación formativa inmediata</option>
                <option value="Coloquio socrático dialógico con docente">Coloquio socrático dialógico con docente (Anti-outsourcing)</option>
              </select>
            </div>

            {/* Principio 2: Representación */}
            <div>
              <label className="font-bold text-slate-800 block mb-1">
                Principio 2: Múltiples Formas de Representación (Redes de Reconocimiento):
              </label>
              <select
                value={selectedDuaStudent.principio_2_representacion}
                onChange={(e) => setSelectedDuaStudent({ ...selectedDuaStudent, principio_2_representacion: e.target.value })}
                className="w-full p-2 bg-[#FAF8F5] border border-[#DDD7CD] rounded-xl text-slate-900 font-semibold"
              >
                <option value="Organizadores gráficos, infografías y diagramas conceptuales">Organizadores gráficos, infografías y diagramas conceptuales</option>
                <option value="Lecturas académicas con guías de andamiaje y glosario">Lecturas académicas con guías de andamiaje y glosario</option>
                <option value="Demostraciones audiovisuales, podcasts y modelado en vivo">Demostraciones audiovisuales, podcasts y modelado en vivo</option>
                <option value="Formato dual: texto digital accesible y audio descriptivo">Formato dual: texto digital accesible y audio descriptivo</option>
              </select>
            </div>

            {/* Principio 3: Acción y Expresión */}
            <div>
              <label className="font-bold text-slate-800 block mb-1">
                Principio 3: Múltiples Formas de Acción y Expresión (Redes Estratégicas):
              </label>
              <select
                value={selectedDuaStudent.principio_3_accion_expresion}
                onChange={(e) => setSelectedDuaStudent({ ...selectedDuaStudent, principio_3_accion_expresion: e.target.value })}
                className="w-full p-2 bg-[#FAF8F5] border border-[#DDD7CD] rounded-xl text-slate-900 font-semibold"
              >
                <option value="Defensa oral socrática individual (Triangulación)">Defensa oral socrática individual (Triangulación Socrática)</option>
                <option value="Portafolio digital de evidencias e iteraciones progresivas">Portafolio digital de evidencias e iteraciones progresivas</option>
                <option value="Informe técnico de investigación estándar">Informe técnico de investigación estándar (Formato formal)</option>
                <option value="Infografía científica interactiva o video-ensayo argumentado">Infografía científica interactiva o video-ensayo argumentado</option>
              </select>
            </div>

            {/* Instrumento y Ajustes Adicionales */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
              <div>
                <label className="font-bold text-slate-800 block mb-1">Instrumento Clave Asignado:</label>
                <select
                  value={selectedDuaStudent.instrumento_clave}
                  onChange={(e) => setSelectedDuaStudent({ ...selectedDuaStudent, instrumento_clave: e.target.value })}
                  className="w-full p-2 bg-[#FAF8F5] border border-[#DDD7CD] rounded-xl text-slate-900 font-semibold"
                >
                  <option value="rubrica_cbl">Rúbrica Analítica CBL (4 Niveles)</option>
                  <option value="triangulacion">Guía de Triangulación Socrática</option>
                  <option value="registro_sudor">Registro de Sudor Intelectual</option>
                  <option value="ficha_autorregulacion">Ficha de Autorregulación</option>
                  <option value="micro_quizzes">Micro-quizzes de Nivelación</option>
                </select>
              </div>

              <div className="flex flex-col justify-center space-y-2 pt-3">
                <label className="flex items-center gap-2 font-bold text-slate-700 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={Boolean(selectedDuaStudent.tiempo_extendido)}
                    onChange={(e) => setSelectedDuaStudent({ ...selectedDuaStudent, tiempo_extendido: e.target.checked })}
                    className="rounded border-slate-300 text-indigo-600 focus:ring-indigo-500"
                  />
                  <span>Autorizar Tiempo Extendido (+25%)</span>
                </label>

                <label className="flex items-center gap-2 font-bold text-slate-700 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={Boolean(selectedDuaStudent.evaluacion_fragmentada)}
                    onChange={(e) => setSelectedDuaStudent({ ...selectedDuaStudent, evaluacion_fragmentada: e.target.checked })}
                    className="rounded border-slate-300 text-indigo-600 focus:ring-indigo-500"
                  />
                  <span>Evaluación fragmentada en 2 entregas</span>
                </label>
              </div>
            </div>

            {/* Observaciones */}
            <div>
              <label className="font-bold text-slate-800 block mb-1">Observaciones Pedagógicas:</label>
              <input
                type="text"
                value={selectedDuaStudent.observaciones || ''}
                onChange={(e) => setSelectedDuaStudent({ ...selectedDuaStudent, observaciones: e.target.value })}
                placeholder="Notas de seguimiento del docente..."
                className="w-full p-2 bg-[#FAF8F5] border border-[#DDD7CD] rounded-xl text-slate-900"
              />
            </div>

            {/* Footer Modal */}
            <div className="flex justify-end gap-3 pt-3 border-t border-[#EFEAE1]">
              <button
                onClick={() => setIsDuaModalOpen(false)}
                className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold rounded-xl transition"
              >
                Cancelar
              </button>
              <button
                onClick={handleSaveStudentDua}
                disabled={isSavingDua}
                className="px-5 py-2 bg-indigo-900 hover:bg-indigo-800 text-white font-bold rounded-xl flex items-center gap-2 transition disabled:opacity-50"
              >
                {isSavingDua ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />}
                {isSavingDua ? 'Guardando...' : 'Guardar Ajuste DUA'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* PESTAÑA 3: INTERVENCIONES POR ALERTAS */}
      {activeTab === 'alertas' && (
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-2xl border border-[#E2DDD5] shadow-atelier space-y-5">
            <div className="border-b border-[#EFEAE1] pb-4">
              <h3 className="font-editorial font-bold text-slate-900 text-lg flex items-center gap-2">
                <ShieldAlert className="w-5 h-5 text-rose-600" />
                Intervenciones Pedagógicas basadas en Analítica
              </h3>
              <p className="text-slate-500 text-xs mt-0.5">
                Rutas de re-evaluación y andamiaje asignadas automáticamente según los hallazgos de <strong>/analytics</strong>.
              </p>
            </div>

            <div className="space-y-3">
              {(planData?.alertas_intervencion || []).length > 0 ? (
                planData.alertas_intervencion.map((al: any, i: number) => (
                  <div key={i} className="p-4 rounded-xl border border-rose-200 bg-rose-50/60 flex flex-col md:flex-row items-start md:items-center justify-between gap-3 text-xs">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="font-mono font-bold bg-rose-200 text-rose-900 px-2 py-0.5 rounded text-[10px]">
                          {al.iniciales}
                        </span>
                        <span className="font-bold text-rose-950">{al.alerta}</span>
                      </div>
                      <p className="text-slate-600 text-[11px] leading-relaxed">
                        {al.medida_pedagogica}
                      </p>
                    </div>

                    <button
                      onClick={() => handleDownload(al.instrumento_obligatorio)}
                      className="px-3.5 py-2 bg-rose-700 hover:bg-rose-800 text-white font-bold rounded-xl text-xs flex items-center gap-1.5 flex-shrink-0 transition shadow-xs"
                    >
                      <FileDown className="w-3.5 h-3.5" />
                      Descargar {al.instrumento_nombre}
                    </button>
                  </div>
                ))
              ) : (
                <div className="text-center p-8 bg-[#FAF8F5] rounded-xl border border-slate-200 text-slate-500 italic text-xs">
                  Sin alertas críticas detectadas para esta asignatura. El grupo opera en progresión óptima.
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* PESTAÑA 4: GALERÍA DE LOS 6 INSTRUMENTOS */}
      {activeTab === 'galeria' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {catalog.map((inst: any, idx: number) => (
            <div key={idx} className="bg-white p-5 rounded-2xl border border-[#E2DDD5] shadow-atelier flex flex-col justify-between hover:border-amber-300 transition">
              <div>
                <div className="flex justify-between items-start mb-2">
                  <span className="text-[10px] font-bold uppercase tracking-wider bg-slate-100 text-slate-700 px-2.5 py-0.5 rounded-full">
                    {inst.dimension}
                  </span>
                  <span className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded ${
                    inst.tipo_archivo === 'docx' ? 'bg-blue-100 text-blue-800' : 'bg-emerald-100 text-emerald-800'
                  }`}>
                    .{inst.tipo_archivo}
                  </span>
                </div>

                <h4 className="font-editorial font-bold text-slate-900 text-sm mb-1">
                  {inst.name}
                </h4>
                <span className="text-[11px] font-semibold text-amber-800 block mb-2">
                  {inst.impacto}
                </span>
                <p className="text-slate-600 text-xs leading-relaxed">
                  {inst.descripcion}
                </p>
              </div>

              <div className="pt-4 mt-3 border-t border-[#EFEAE1]">
                <button
                  onClick={() => handleDownload(inst.id)}
                  className="w-full bg-slate-900 hover:bg-slate-800 text-amber-300 font-bold py-2.5 px-3 rounded-xl text-xs flex items-center justify-center gap-1.5 transition shadow-xs"
                >
                  <FileDown className="w-3.5 h-3.5" /> Descargar Instrumento Formal
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* PESTAÑA 5: GENERADOR ASISTIDO DE RÚBRICAS CBL */}
      {activeTab === 'rubricas' && (
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-2xl border border-[#E2DDD5] shadow-atelier space-y-4">
            <h3 className="font-editorial font-bold text-slate-900 text-lg flex items-center gap-2 border-b border-[#EFEAE1] pb-3">
              <Sparkles className="w-5 h-5 text-purple-600" />
              Generador Inteligente de Rúbricas CBL (4 Niveles)
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
              <div>
                <label className="font-bold text-slate-700 block mb-1">Actividad de Evaluación:</label>
                <input
                  type="text"
                  value={rubricRequest.actividad_nombre}
                  onChange={(e) => setRubricRequest({ ...rubricRequest, actividad_nombre: e.target.value })}
                  className="w-full p-2.5 bg-[#FAF8F5] border border-[#DDD7CD] rounded-xl text-slate-900"
                />
              </div>

              <div>
                <label className="font-bold text-slate-700 block mb-1">Competencia / Criterio Clave:</label>
                <input
                  type="text"
                  value={rubricRequest.competencia}
                  onChange={(e) => setRubricRequest({ ...rubricRequest, competencia: e.target.value })}
                  className="w-full p-2.5 bg-[#FAF8F5] border border-[#DDD7CD] rounded-xl text-slate-900"
                />
              </div>
            </div>

            <button
              onClick={handleGenerateRubric}
              disabled={isGeneratingRubric}
              className="bg-slate-900 text-amber-300 hover:bg-slate-800 font-bold px-5 py-2.5 rounded-xl text-xs flex items-center gap-2 transition disabled:opacity-50"
            >
              {isGeneratingRubric ? <RefreshCw className="w-4 h-4 animate-spin text-amber-400" /> : <Sparkles className="w-4 h-4 text-amber-400" />}
              {isGeneratingRubric ? 'Generando Rúbrica con IA...' : 'Generar Rúbrica Analítica'}
            </button>

            {/* Tabla de la Rúbrica Generada */}
            {generatedRubric && (
              <div className="pt-4 space-y-3 animate-in fade-in">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <h4 className="font-bold text-slate-800 text-sm flex items-center gap-2 flex-wrap">
                    <span>Rúbrica Generada: {generatedRubric.actividad}</span>
                    {generatedRubric.motor && (
                      <span className="text-[10px] bg-amber-100 text-amber-900 border border-amber-300 px-2 py-0.5 rounded-full font-mono font-semibold">
                        {generatedRubric.motor}
                      </span>
                    )}
                  </h4>
                  <button
                    onClick={handleExportRubricDocx}
                    disabled={isExportingRubric}
                    className="flex items-center justify-center gap-1.5 text-xs bg-slate-900 text-amber-300 hover:bg-slate-800 font-bold px-3 py-1.5 rounded-xl shadow-xs transition disabled:opacity-50 cursor-pointer"
                  >
                    {isExportingRubric ? (
                      <RefreshCw className="w-3.5 h-3.5 animate-spin text-amber-400" />
                    ) : (
                      <FileDown className="w-3.5 h-3.5 text-amber-400" />
                    )}
                    {isExportingRubric ? 'Generando Word...' : 'Descargar Rúbrica (.docx)'}
                  </button>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs border border-slate-200 rounded-xl overflow-hidden">
                    <thead className="bg-slate-900 text-white font-bold text-[11px]">
                      <tr>
                        <th className="p-3">Dimensión (Peso)</th>
                        <th className="p-3 bg-rose-950">1. Emergente (1-50)</th>
                        <th className="p-3 bg-amber-950">2. En Desarrollo (51-70)</th>
                        <th className="p-3 bg-blue-950">3. Competente (71-85)</th>
                        <th className="p-3 bg-emerald-950">4. Avanzado (86-100)</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-200">
                      {(generatedRubric.criterios || []).map((crit: any, i: number) => (
                        <tr key={i} className="hover:bg-slate-50">
                          <td className="p-3 font-bold text-slate-900 bg-slate-50/70">
                            {crit.dimension} <br />
                            <span className="text-amber-700 text-[10px]">({crit.peso})</span>
                          </td>
                          <td className="p-3 text-slate-700 bg-rose-50/30">{crit.emergente}</td>
                          <td className="p-3 text-slate-700 bg-amber-50/30">{crit.en_desarrollo}</td>
                          <td className="p-3 text-slate-700 bg-blue-50/30">{crit.competente}</td>
                          <td className="p-3 text-slate-700 bg-emerald-50/30">{crit.avanzado}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
