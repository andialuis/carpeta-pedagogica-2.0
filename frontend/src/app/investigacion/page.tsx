'use client';
import { useState, useEffect } from 'react';
import { RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ReferenceLine } from 'recharts';
import { FlaskConical, Brain, Target, TrendingUp, AlertCircle, Download, FileSpreadsheet, FileText, Sparkles, ChevronRight, RefreshCw, Users, BookOpen, Check, Copy } from 'lucide-react';

type SubjectRecord = { name: string; code: string; asignatura: string; group: string; year: string|number; period: string; has_insights: boolean; has_base_limpia: boolean; };
type SubjectsIndex = { by_group: Record<string, SubjectRecord[]>; by_code: Record<string, { code: string; asignatura: string; groups: SubjectRecord[] }>; all: SubjectRecord[]; };
type Hypothesis = { hipotesis_nula: string; hipotesis_alternativa: string; pregunta_investigacion: string; metricas_recomendadas: string[]; diseno_metodologico: string; advertencias: string[]; interpretacion_esperada: string; };
type SubjectMetrics = { name: string; display_name: string; code: string; asignatura: string; group: string; year: string|number; promedio: number|null; desviacion_estandar: number|null; pct_aprobados: number|null; n_riesgo_abandono: number|null; pct_asistencia: number|null; sudor_intelectual_promedio: number|null; deltas: Record<string,number>; z_scores: Record<string,number>; rankings: Record<string,number>; data_source: string; };
type ComparisonResult = { subjects: SubjectMetrics[]; global_stats: Record<string,any>; active_metrics: string[]; correlations: Record<string,number>; best_overall: string|null; worst_overall: string|null; n_compared: number; errors: string[]; };

const METRIC_LABELS: Record<string,string> = { promedio:'Promedio', desviacion_estandar:'Desv. Std', pct_aprobados:'% Aprobados', n_riesgo_abandono:'N Riesgo', pct_asistencia:'% Asistencia', sudor_intelectual_promedio:'Sudor Intelectual' };
const COLORS = ['#1A3A5C','#D4A017','#2D6A4F','#8B2FC9','#C0392B','#16A085'];
const semaforo = (val: number|null, key: string): string => {
  if (val === null) return 'bg-slate-100 text-slate-400';
  if (key === 'promedio' || key === 'pct_aprobados') return val >= 80 ? 'bg-emerald-100 text-emerald-800' : val >= 60 ? 'bg-amber-100 text-amber-800' : 'bg-rose-100 text-rose-800';
  if (key === 'n_riesgo_abandono') return val === 0 ? 'bg-emerald-100 text-emerald-800' : val <= 2 ? 'bg-amber-100 text-amber-800' : 'bg-rose-100 text-rose-800';
  if (key === 'pct_asistencia') return val >= 85 ? 'bg-emerald-100 text-emerald-800' : val >= 70 ? 'bg-amber-100 text-amber-800' : 'bg-rose-100 text-rose-800';
  return 'bg-slate-100 text-slate-700';
};
const fmt = (v: number|null, d=1) => v !== null ? v.toFixed(d) : 'N/A';
const RESEARCH_LINES = [
  { id:'rendimiento_asignaturas', label:'Rendimiento entre asignaturas', eje:'A', icon:'📊', metricas:['promedio','desviacion_estandar','pct_aprobados','n_riesgo_abandono'] },
  { id:'efecto_docente_cohorte', label:'Efecto docente/metodología entre cohortes', eje:'B', icon:'📈', metricas:['promedio','pct_aprobados','sudor_intelectual_promedio','n_riesgo_abandono'] },
  { id:'engagement_vs_rendimiento', label:'Engagement vs. rendimiento', eje:'A', icon:'🔥', metricas:['promedio','sudor_intelectual_promedio','pct_aprobados'] },
  { id:'asistencia_vs_aprobacion', label:'Asistencia y riesgo de abandono', eje:'A', icon:'📋', metricas:['pct_asistencia','pct_aprobados','n_riesgo_abandono'] },
  { id:'equidad_varianza', label:'Equidad y dispersión del aprendizaje', eje:'A', icon:'⚖️', metricas:['desviacion_estandar','promedio','pct_aprobados'] },
  { id:'personalizado', label:'Línea personalizada (IA asistida)', eje:'A/B', icon:'✨', metricas:[] },
];

export default function InvestigacionPage() {
  const [index, setIndex] = useState<SubjectsIndex|null>(null);
  const [selectedAxis, setSelectedAxis] = useState<'A'|'B'>('A');
  const [selectedGroup, setSelectedGroup] = useState<string>('');
  const [selectedCode, setSelectedCode] = useState<string>('');
  const [selectedSubjects, setSelectedSubjects] = useState<SubjectRecord[]>([]);
  const [researchLineId, setResearchLineId] = useState('rendimiento_asignaturas');
  const [customQuestion, setCustomQuestion] = useState('');
  const [hypothesis, setHypothesis] = useState<Hypothesis|null>(null);
  const [hypothesisMotor, setHypothesisMotor] = useState('');
  const [isSetupLoading, setIsSetupLoading] = useState(false);
  const [comparison, setComparison] = useState<ComparisonResult|null>(null);
  const [isCompareLoading, setIsCompareLoading] = useState(false);
  const [narrative, setNarrative] = useState('');
  const [narrativeMotor, setNarrativeMotor] = useState('');
  const [isNarrativeLoading, setIsNarrativeLoading] = useState(false);
  const [isExporting, setIsExporting] = useState<'xlsx'|'docx'|null>(null);
  const [copiedNarrative, setCopiedNarrative] = useState(false);
  const [activeStep, setActiveStep] = useState<1|2|3|4>(1);

  useEffect(() => { fetchIndex(); }, []);

  const fetchIndex = async () => {
    try {
      const res = await fetch('/api/research/subjects-index', { cache: 'no-store' });
      const data: SubjectsIndex = await res.json();
      setIndex(data);
      const groups = Object.keys(data.by_group);
      const codes = Object.keys(data.by_code);
      if (groups.length > 0) setSelectedGroup(groups[0]);
      if (codes.length > 0) setSelectedCode(codes[0]);
    } catch (e) { console.error('Error cargando indice', e); }
  };

  const availableSubjects: SubjectRecord[] = (() => {
    if (!index) return [];
    if (selectedAxis === 'A') return index.by_group[selectedGroup] || [];
    return index.by_code[selectedCode]?.groups || [];
  })();

  const toggleSubject = (s: SubjectRecord) => {
    setSelectedSubjects(prev => prev.some(x => x.name === s.name) ? prev.filter(x => x.name !== s.name) : [...prev, s]);
    setComparison(null); setNarrative(''); setHypothesis(null);
  };
  const selectAll = () => { setSelectedSubjects(availableSubjects); setComparison(null); setNarrative(''); };
  const clearAll = () => { setSelectedSubjects([]); setComparison(null); setNarrative(''); setHypothesis(null); };
  const activeLine = RESEARCH_LINES.find(l => l.id === researchLineId);

  const handleSetupHypothesis = async () => {
    if (selectedSubjects.length < 2) return alert('Selecciona al menos 2 asignaturas/grupos.');
    setIsSetupLoading(true);
    try {
      const res = await fetch('/api/research/setup-hypothesis', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ research_line_id: researchLineId, selected_subjects: selectedSubjects, custom_question: customQuestion }) });
      const data = await res.json();
      setHypothesis(data.hypothesis); setHypothesisMotor(data.motor); setActiveStep(2);
    } catch (e) { console.error('Error setup hipotesis', e); }
    setIsSetupLoading(false);
  };

  const handleCompare = async () => {
    if (selectedSubjects.length < 2) return;
    setIsCompareLoading(true);
    try {
      const focusMetrics = hypothesis?.metricas_recomendadas?.length ? hypothesis.metricas_recomendadas : activeLine?.metricas || null;
      const res = await fetch('/api/research/compare', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ subject_names: selectedSubjects.map(s=>s.name), focus_metrics: focusMetrics }) });
      const data: ComparisonResult = await res.json();
      setComparison(data); setActiveStep(3);
    } catch (e) { console.error('Error comparacion', e); }
    setIsCompareLoading(false);
  };

  const handleNarrative = async () => {
    if (!comparison || !hypothesis) return;
    setIsNarrativeLoading(true);
    try {
      const res = await fetch('/api/research/narrative', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ subject_names: selectedSubjects.map(s=>s.name), hypothesis, focus_metrics: comparison.active_metrics, teacher_name: 'Docente Investigador' }) });
      const data = await res.json();
      setNarrative(data.narrative); setNarrativeMotor(data.motor); setActiveStep(4);
    } catch (e) { console.error('Error narrativo', e); }
    setIsNarrativeLoading(false);
  };

  const handleExport = async (format: 'xlsx'|'docx') => {
    if (!comparison || !hypothesis) return;
    setIsExporting(format);
    try {
      const res = await fetch(`/api/research/export/${format}`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ subject_names: selectedSubjects.map(s=>s.name), hypothesis, narrative, focus_metrics: comparison.active_metrics, teacher_name: 'Docente Investigador' }) });
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a'); a.href = url;
      a.download = format === 'xlsx' ? 'Investigacion_Comparativa.xlsx' : 'Informe_Investigacion.docx';
      a.click(); window.URL.revokeObjectURL(url);
    } catch (e) { console.error('Error exportando', e); }
    setIsExporting(null);
  };

  const radarData = (() => {
    if (!comparison) return [];
    return comparison.active_metrics.filter(k => k !== 'n_riesgo_abandono').map(key => {
      const point: any = { metric: METRIC_LABELS[key] || key };
      comparison.subjects.forEach(s => {
        const label = s.asignatura || s.display_name;
        const gs = comparison.global_stats[key];
        const val = s[key as keyof SubjectMetrics] as number|null;
        if (val !== null && gs && gs.max) point[label] = Math.max(0, Math.round((val / gs.max) * 100));
      });
      return point;
    });
  })();

  const barData = (comparison?.subjects || []).map((s, i) => ({
    name: `${s.code || (s.asignatura||'').slice(0,8)} ${s.group ? '('+s.group+')' : ''}`.trim(),
    promedio: s.promedio, pct_aprobados: s.pct_aprobados, fill: COLORS[i % COLORS.length],
  }));
  const globalMean = comparison?.global_stats?.promedio?.mean;
  const steps = [
    { n:1, label:'Configurar investigación', icon:<Target className="w-3.5 h-3.5"/> },
    { n:2, label:'Hipótesis con IA', icon:<Brain className="w-3.5 h-3.5"/> },
    { n:3, label:'Comparar métricas', icon:<TrendingUp className="w-3.5 h-3.5"/> },
    { n:4, label:'Informe y exportar', icon:<Download className="w-3.5 h-3.5"/> },
  ];

  return (
    <div className="text-slate-800 pb-16 font-sans-clean">
      <header className="mb-8 border-b border-[#E8E3DA] pb-5">
        <div className="flex items-center gap-2 mb-1">
          <span className="text-[10px] font-bold tracking-widest uppercase text-violet-800 bg-violet-100/80 px-2.5 py-0.5 rounded-full border border-violet-300">Investigación Educativa</span>
          <span className="text-[10px] font-medium text-slate-400">• Análisis Cruzado de Asignaturas y Grupos</span>
        </div>
        <h1 className="text-3xl font-bold font-editorial text-slate-900 flex items-center gap-3">
          <FlaskConical className="w-8 h-8 text-violet-700" /> Centro de Investigación Comparativa
        </h1>
        <p className="text-slate-500 text-sm mt-0.5 font-medium">Compara métricas entre asignaturas (Eje A) o entre grupos/cohortes (Eje B) con hipótesis asistida por IA y evidencia exportable</p>
      </header>

      <div className="flex items-center gap-0 mb-8 overflow-x-auto pb-2">
        {steps.map((step, i) => (
          <div key={step.n} className="flex items-center">
            <button onClick={() => { if (step.n <= activeStep) setActiveStep(step.n as any); }} className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition cursor-pointer ${activeStep===step.n ? 'bg-violet-900 text-white shadow' : step.n < activeStep ? 'bg-violet-100 text-violet-800 hover:bg-violet-200' : 'bg-slate-50 text-slate-400 border border-slate-200'}`}>
              <span className={`w-4 h-4 rounded-full flex items-center justify-center text-[9px] font-mono font-bold ${activeStep===step.n ? 'bg-violet-400 text-violet-950' : step.n < activeStep ? 'bg-violet-300 text-violet-900' : 'bg-slate-200 text-slate-500'}`}>{step.n}</span>
              {step.icon}<span className="hidden sm:inline ml-1">{step.label}</span>
            </button>
            {i < 3 && <ChevronRight className="w-3 h-3 text-slate-300 mx-0.5 flex-shrink-0" />}
          </div>
        ))}
      </div>

      {/* PASO 1 */}
      {activeStep === 1 && (
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-3xl shadow-atelier border border-[#E2DDD5]">
            <h2 className="text-sm font-bold text-slate-900 mb-4 flex items-center gap-2"><Users className="w-4 h-4 text-violet-700" /> Eje de Análisis</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <button onClick={() => { setSelectedAxis('A'); setSelectedSubjects([]); setComparison(null); }} className={`p-4 rounded-2xl border text-left transition cursor-pointer ${selectedAxis==='A' ? 'bg-violet-50 border-violet-400 ring-2 ring-violet-300/40' : 'bg-[#FAF8F5] border-[#E8E3DA] hover:border-slate-300'}`}>
                <p className="font-bold text-violet-900 text-sm mb-1">Eje A — Mismo grupo, distintas asignaturas</p>
                <p className="text-[11px] text-slate-600">¿Cómo rinde el Grupo 2026 en FIS301 vs INV101 vs QUIM101? Detecta brechas curriculares o de enseñanza.</p>
              </button>
              <button onClick={() => { setSelectedAxis('B'); setSelectedSubjects([]); setComparison(null); }} className={`p-4 rounded-2xl border text-left transition cursor-pointer ${selectedAxis==='B' ? 'bg-amber-50 border-amber-400 ring-2 ring-amber-300/40' : 'bg-[#FAF8F5] border-[#E8E3DA] hover:border-slate-300'}`}>
                <p className="font-bold text-amber-900 text-sm mb-1">Eje B — Misma asignatura, distintos grupos</p>
                <p className="text-[11px] text-slate-600">¿Rindió mejor el Grupo 2025 o el Grupo 2026 en INV101? Evalúa impacto de cambios pedagógicos.</p>
              </button>
            </div>
          </div>

          <div className="bg-white p-6 rounded-3xl shadow-atelier border border-[#E2DDD5]">
            <h2 className="text-sm font-bold text-slate-900 mb-4 flex items-center gap-2"><BookOpen className="w-4 h-4 text-violet-700" />{selectedAxis==='A' ? 'Seleccionar Grupo' : 'Seleccionar Asignatura (Código)'}</h2>
            {selectedAxis==='A' && index && (
              <div className="mb-4 flex items-center gap-3 flex-wrap">
                <label className="text-xs font-semibold text-slate-600">Grupo / Cohorte:</label>
                <select value={selectedGroup} onChange={e => { setSelectedGroup(e.target.value); setSelectedSubjects([]); setComparison(null); }} className="bg-[#FAF8F5] border border-[#DDD7CD] text-slate-900 text-xs rounded-lg p-2 font-bold focus:ring-violet-500">
                  {Object.keys(index.by_group||{}).map(g => <option key={g} value={g}>{g}</option>)}
                </select>
                {Object.keys(index.by_group||{}).length === 0 && <span className="text-xs text-slate-400">Sin grupos detectados.</span>}
              </div>
            )}
            {selectedAxis==='B' && index && (
              <div className="mb-4 flex items-center gap-3 flex-wrap">
                <label className="text-xs font-semibold text-slate-600">Asignatura (Código):</label>
                <select value={selectedCode} onChange={e => { setSelectedCode(e.target.value); setSelectedSubjects([]); setComparison(null); }} className="bg-[#FAF8F5] border border-[#DDD7CD] text-slate-900 text-xs rounded-lg p-2 font-bold focus:ring-violet-500">
                  {Object.keys(index.by_code||{}).map(c => <option key={c} value={c}>{c} — {index.by_code[c].asignatura}</option>)}
                </select>
              </div>
            )}
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-semibold text-slate-600">{availableSubjects.length} asignatura(s) disponibles:</span>
              <div className="flex gap-2">
                <button onClick={selectAll} className="text-[10px] font-semibold text-violet-700 hover:underline cursor-pointer">Seleccionar todas</button>
                <span className="text-slate-300">|</span>
                <button onClick={clearAll} className="text-[10px] font-semibold text-rose-600 hover:underline cursor-pointer">Limpiar</button>
              </div>
            </div>
            {availableSubjects.length === 0 ? (
              <div className="text-center py-8 text-slate-400 text-xs"><FlaskConical className="w-8 h-8 mx-auto mb-2 opacity-30" />{selectedAxis==='A' ? 'Sin asignaturas en este grupo. Crea asignaturas con el mismo campo Grupo.' : 'Sin grupos múltiples para esta asignatura.'}</div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                {availableSubjects.map(s => {
                  const isSel = selectedSubjects.some(x => x.name===s.name);
                  return (
                    <button key={s.name} onClick={() => toggleSubject(s)} className={`p-3 rounded-xl border text-left transition cursor-pointer flex items-center gap-3 ${isSel ? 'bg-violet-50 border-violet-400 ring-1 ring-violet-300' : 'bg-[#FAF8F5] border-[#E8E3DA] hover:border-slate-300'}`}>
                      <div className={`w-4 h-4 rounded border flex items-center justify-center flex-shrink-0 ${isSel ? 'bg-violet-700 border-violet-700' : 'border-slate-300'}`}>{isSel && <Check className="w-2.5 h-2.5 text-white" />}</div>
                      <div className="min-w-0">
                        <div className="flex items-center gap-1.5 flex-wrap">
                          {s.code && <span className="text-[10px] font-mono font-bold bg-slate-900 text-amber-400 px-1.5 py-0.5 rounded">{s.code}</span>}
                          {s.group && <span className="text-[10px] font-medium bg-violet-100 text-violet-800 px-1.5 py-0.5 rounded">👥 {s.group}</span>}
                          {s.year && <span className="text-[10px] text-slate-400">{s.year}</span>}
                        </div>
                        <p className="text-xs font-semibold text-slate-800 mt-0.5 truncate">{s.asignatura||s.name}</p>
                        <div className="flex items-center gap-2 mt-0.5">
                          {s.has_insights && <span className="text-[9px] bg-emerald-100 text-emerald-700 px-1 rounded">Etapa 3 OK</span>}
                          {s.has_base_limpia && <span className="text-[9px] bg-blue-100 text-blue-700 px-1 rounded">Base Limpia</span>}
                          {!s.has_insights && !s.has_base_limpia && <span className="text-[9px] bg-amber-100 text-amber-700 px-1 rounded">Datos ejemplo</span>}
                        </div>
                      </div>
                    </button>
                  );
                })}
              </div>
            )}
            {selectedSubjects.length > 0 && <div className="mt-3 p-2.5 bg-violet-50 rounded-xl border border-violet-200 text-xs font-semibold text-violet-800">✓ {selectedSubjects.length} seleccionadas para comparar</div>}
          </div>

          <div className="bg-white p-6 rounded-3xl shadow-atelier border border-[#E2DDD5]">
            <h2 className="text-sm font-bold text-slate-900 mb-4 flex items-center gap-2"><Brain className="w-4 h-4 text-violet-700" /> Línea de Investigación</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2 mb-4">
              {RESEARCH_LINES.map(l => (
                <button key={l.id} onClick={() => setResearchLineId(l.id)} className={`p-3 rounded-xl border text-left transition cursor-pointer ${researchLineId===l.id ? 'bg-violet-50 border-violet-400 ring-1 ring-violet-300' : 'bg-[#FAF8F5] border-[#E8E3DA] hover:border-slate-300'}`}>
                  <span className="text-base">{l.icon}</span><p className="text-xs font-semibold text-slate-900 mt-1">{l.label}</p>
                  <span className="text-[9px] bg-slate-100 text-slate-500 px-1.5 py-0.5 rounded font-mono">Eje {l.eje}</span>
                </button>
              ))}
            </div>
            {researchLineId==='personalizado' && (
              <div className="mt-3">
                <label className="text-xs font-semibold text-slate-700 block mb-1">Describe tu pregunta de investigación:</label>
                <textarea value={customQuestion} onChange={e => setCustomQuestion(e.target.value)} rows={3} placeholder="Ej: Los grupos con retroalimentacion DUA obtuvieron mayor tasa de aprobacion?" className="w-full text-xs bg-[#FAF8F5] border border-[#DDD7CD] rounded-xl p-3 focus:ring-violet-500 outline-none resize-none" />
              </div>
            )}
            <button onClick={handleSetupHypothesis} disabled={selectedSubjects.length<2||isSetupLoading} className="mt-4 w-full flex items-center justify-center gap-2 bg-violet-900 hover:bg-violet-800 text-white font-bold px-6 py-3 rounded-2xl text-sm transition shadow-md disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer">
              {isSetupLoading ? <><RefreshCw className="w-4 h-4 animate-spin" /> Consultando IA...</> : <><Sparkles className="w-4 h-4 text-violet-300" /> Formalizar Hipótesis con IA</>}
            </button>
            {selectedSubjects.length<2 && <p className="text-xs text-slate-400 text-center mt-2">Selecciona al menos 2 asignaturas/grupos para continuar.</p>}
          </div>
        </div>
      )}

      {/* PASO 2 */}
      {activeStep === 2 && hypothesis && (
        <div className="bg-white p-6 rounded-3xl shadow-atelier border border-[#E2DDD5] space-y-4">
          <div className="flex items-start justify-between">
            <h2 className="text-sm font-bold text-slate-900 flex items-center gap-2"><Brain className="w-4 h-4 text-violet-700" /> Marco de Investigación Generado</h2>
            <span className={`text-[9px] font-bold px-2 py-0.5 rounded-full border ${hypothesisMotor==='gemini' ? 'bg-emerald-50 border-emerald-300 text-emerald-700' : 'bg-amber-50 border-amber-300 text-amber-700'}`}>{hypothesisMotor==='gemini' ? 'Gemini IA' : 'Motor Local'}</span>
          </div>
          <div className="p-4 bg-violet-50 rounded-2xl border border-violet-200">
            <p className="text-[10px] font-bold uppercase tracking-wider text-violet-600 mb-1">Pregunta de Investigación</p>
            <p className="text-sm font-medium text-slate-900 italic">&ldquo;{hypothesis.pregunta_investigacion}&rdquo;</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div className="p-3 bg-slate-50 rounded-xl border border-slate-200"><p className="text-[10px] font-bold uppercase text-slate-400 mb-1">H₀ (Nula)</p><p className="text-xs text-slate-700">{hypothesis.hipotesis_nula}</p></div>
            <div className="p-3 bg-violet-50/80 rounded-xl border border-violet-200"><p className="text-[10px] font-bold uppercase text-violet-600 mb-1">H₁ (Alternativa)</p><p className="text-xs text-slate-800 font-medium">{hypothesis.hipotesis_alternativa}</p></div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div className="p-3 bg-slate-50 rounded-xl border border-slate-200"><p className="text-[10px] font-bold uppercase text-slate-400 mb-1.5">Diseño Metodológico</p><p className="text-xs text-slate-700">{hypothesis.diseno_metodologico}</p></div>
            <div className="p-3 bg-slate-50 rounded-xl border border-slate-200"><p className="text-[10px] font-bold uppercase text-slate-400 mb-1.5">Métricas Recomendadas</p><div className="flex flex-wrap gap-1">{(hypothesis.metricas_recomendadas||[]).map(m => <span key={m} className="text-[10px] bg-violet-100 text-violet-800 font-semibold px-2 py-0.5 rounded-full">{METRIC_LABELS[m]||m}</span>)}</div></div>
          </div>
          {hypothesis.advertencias?.length > 0 && (
            <div className="p-3 bg-amber-50 rounded-xl border border-amber-200">
              <p className="text-[10px] font-bold uppercase text-amber-700 mb-1.5 flex items-center gap-1"><AlertCircle className="w-3 h-3" /> Limitaciones</p>
              {hypothesis.advertencias.map((a,i) => <p key={i} className="text-xs text-amber-800">• {a}</p>)}
            </div>
          )}
          {hypothesis.interpretacion_esperada && (
            <div className="p-3 bg-emerald-50 rounded-xl border border-emerald-200"><p className="text-[10px] font-bold uppercase text-emerald-700 mb-1">Resultado que confirmaría H₁</p><p className="text-xs text-emerald-800">{hypothesis.interpretacion_esperada}</p></div>
          )}
          <div className="flex gap-3 mt-2">
            <button onClick={() => setActiveStep(1)} className="flex-1 flex items-center justify-center gap-2 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold px-4 py-2.5 rounded-2xl text-xs transition cursor-pointer">← Volver</button>
            <button onClick={handleCompare} disabled={isCompareLoading} className="flex-1 flex items-center justify-center gap-2 bg-violet-900 hover:bg-violet-800 text-white font-bold px-6 py-2.5 rounded-2xl text-xs transition shadow cursor-pointer disabled:opacity-40">
              {isCompareLoading ? <><RefreshCw className="w-3.5 h-3.5 animate-spin" /> Comparando...</> : <><TrendingUp className="w-3.5 h-3.5" /> Comparar Métricas →</>}
            </button>
          </div>
        </div>
      )}

      {/* PASO 3 */}
      {activeStep === 3 && comparison && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {comparison.best_overall && <div className="p-4 bg-emerald-50 rounded-2xl border border-emerald-200"><p className="text-[10px] font-bold uppercase text-emerald-600 mb-1">🏆 Mayor Rendimiento</p><p className="text-sm font-bold text-emerald-900">{comparison.subjects.find(s=>s.name===comparison.best_overall)?.asignatura||comparison.best_overall}</p><p className="text-xs text-emerald-700 mt-0.5">Promedio: {fmt(comparison.subjects.find(s=>s.name===comparison.best_overall)?.promedio??null)}</p></div>}
            {comparison.worst_overall && comparison.worst_overall!==comparison.best_overall && <div className="p-4 bg-rose-50 rounded-2xl border border-rose-200"><p className="text-[10px] font-bold uppercase text-rose-600 mb-1">⚠️ Menor Rendimiento</p><p className="text-sm font-bold text-rose-900">{comparison.subjects.find(s=>s.name===comparison.worst_overall)?.asignatura||comparison.worst_overall}</p><p className="text-xs text-rose-700 mt-0.5">Promedio: {fmt(comparison.subjects.find(s=>s.name===comparison.worst_overall)?.promedio??null)}</p></div>}
            {comparison.global_stats?.promedio && <div className="p-4 bg-violet-50 rounded-2xl border border-violet-200"><p className="text-[10px] font-bold uppercase text-violet-600 mb-1">📊 Media Global</p><p className="text-2xl font-bold font-editorial text-violet-900">{fmt(comparison.global_stats.promedio.mean)}</p><p className="text-xs text-violet-700 mt-0.5">σ = {fmt(comparison.global_stats.promedio.std)} | {fmt(comparison.global_stats.promedio.min)}–{fmt(comparison.global_stats.promedio.max)}</p></div>}
          </div>

          <div className="bg-white p-6 rounded-3xl shadow-atelier border border-[#E2DDD5]">
            <h2 className="text-sm font-bold text-slate-900 mb-4">Tabla Comparativa</h2>
            <div className="overflow-x-auto">
              <table className="w-full text-xs">
                <thead><tr className="bg-slate-900 text-white">
                  <th className="px-3 py-2.5 text-left rounded-l-xl">Asignatura / Grupo</th>
                  {comparison.active_metrics.map(k => <th key={k} className="px-3 py-2.5 text-center whitespace-nowrap">{METRIC_LABELS[k]||k}</th>)}
                  <th className="px-3 py-2.5 text-center rounded-r-xl">Δ Media</th>
                </tr></thead>
                <tbody>
                  {comparison.subjects.map((s,i) => (
                    <tr key={s.name} className={i%2===0 ? 'bg-[#FAF8F5]' : 'bg-white'}>
                      <td className="px-3 py-2 font-medium text-slate-800">
                        <div className="flex items-center gap-1.5">{s.code && <span className="font-mono font-bold text-[9px] bg-slate-900 text-amber-400 px-1.5 py-0.5 rounded">{s.code}</span>}<span>{s.asignatura||s.display_name}</span></div>
                        {s.group && <span className="text-[9px] text-slate-400">👥 {s.group} {s.year}</span>}
                      </td>
                      {comparison.active_metrics.map(k => { const val = s[k as keyof SubjectMetrics] as number|null; return <td key={k} className="px-3 py-2 text-center"><span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${semaforo(val,k)}`}>{val!==null ? (k.includes('pct') ? val+'%' : val) : 'N/A'}</span></td>; })}
                      <td className="px-3 py-2 text-center">{s.deltas?.promedio!==undefined ? <span className={`text-[10px] font-bold ${s.deltas.promedio>=0 ? 'text-emerald-700' : 'text-rose-700'}`}>{s.deltas.promedio>=0?'+':''}{s.deltas.promedio.toFixed(1)}</span> : 'N/A'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {radarData.length>0 && (
              <div className="bg-white p-6 rounded-3xl shadow-atelier border border-[#E2DDD5]">
                <h3 className="text-xs font-bold uppercase text-slate-700 mb-4">Radar Comparativo (normalizado)</h3>
                <ResponsiveContainer width="100%" height={260}>
                  <RadarChart data={radarData}>
                    <PolarGrid stroke="#E2DDD5" /><PolarAngleAxis dataKey="metric" tick={{fontSize:9,fill:'#64748b'}} /><PolarRadiusAxis angle={30} domain={[0,100]} tick={{fontSize:8}} />
                    {comparison.subjects.map((s,i) => { const label=s.asignatura||s.display_name; return <Radar key={s.name} name={label} dataKey={label} stroke={COLORS[i]} fill={COLORS[i]} fillOpacity={0.15} strokeWidth={2} />; })}
                    <Legend iconSize={8} iconType="line" wrapperStyle={{fontSize:'10px'}} /><Tooltip formatter={(v:any)=>`${v}%`} />
                  </RadarChart>
                </ResponsiveContainer>
              </div>
            )}
            {barData.length>0 && (
              <div className="bg-white p-6 rounded-3xl shadow-atelier border border-[#E2DDD5]">
                <h3 className="text-xs font-bold uppercase text-slate-700 mb-4">Promedios y % Aprobados</h3>
                <ResponsiveContainer width="100%" height={260}>
                  <BarChart data={barData} margin={{top:5,right:10,left:0,bottom:20}}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#F5F2EC" /><XAxis dataKey="name" tick={{fontSize:9}} angle={-30} textAnchor="end" /><YAxis domain={[0,100]} tick={{fontSize:9}} />
                    <Tooltip formatter={(v:any)=>[typeof v==='number'?v.toFixed(1):v,'']} /><Legend iconSize={8} wrapperStyle={{fontSize:'10px'}} />
                    {globalMean && <ReferenceLine y={globalMean} stroke="#8B5CF6" strokeDasharray="5 3" label={{value:`Media: ${globalMean.toFixed(1)}`,position:'right',fontSize:9,fill:'#7C3AED'}} />}
                    <Bar dataKey="promedio" name="Promedio" fill="#1A3A5C" radius={[4,4,0,0]} />
                    <Bar dataKey="pct_aprobados" name="% Aprobados" fill="#D4A017" radius={[4,4,0,0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>

          {Object.keys(comparison.correlations||{}).length>0 && (
            <div className="bg-white p-6 rounded-3xl shadow-atelier border border-[#E2DDD5]">
              <h3 className="text-xs font-bold uppercase text-slate-700 mb-3">Correlaciones de Pearson</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                {Object.entries(comparison.correlations).map(([pair,r]) => {
                  const label=pair.replace(/_vs_/g,' ↔ ').replace(/_/g,' ');
                  const str=Math.abs(r)>=0.7?'fuerte':Math.abs(r)>=0.4?'moderada':'débil';
                  const colClass=r>=0.4?'bg-emerald-50 border-emerald-200 text-emerald-700':r<=-0.4?'bg-rose-50 border-rose-200 text-rose-700':'bg-slate-50 border-slate-200 text-slate-700';
                  return <div key={pair} className={`p-3 rounded-xl border flex items-center justify-between ${colClass}`}><span className="text-xs text-slate-700">{label}</span><span className="text-xs font-bold font-mono">r = {r.toFixed(3)} ({str})</span></div>;
                })}
              </div>
            </div>
          )}

          <div className="flex gap-3">
            <button onClick={() => setActiveStep(2)} className="flex items-center gap-2 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold px-4 py-2.5 rounded-2xl text-xs transition cursor-pointer">← Hipótesis</button>
            <button onClick={handleNarrative} disabled={isNarrativeLoading} className="flex-1 flex items-center justify-center gap-2 bg-violet-900 hover:bg-violet-800 text-white font-bold px-6 py-2.5 rounded-2xl text-sm transition shadow cursor-pointer disabled:opacity-40">
              {isNarrativeLoading ? <><RefreshCw className="w-4 h-4 animate-spin" /> Generando informe...</> : <><Sparkles className="w-4 h-4 text-violet-300" /> Generar Informe con IA →</>}
            </button>
          </div>
        </div>
      )}

      {/* PASO 4 */}
      {activeStep === 4 && narrative && (
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-3xl shadow-atelier border border-[#E2DDD5]">
            <div className="flex items-start justify-between mb-4">
              <h2 className="text-sm font-bold text-slate-900 flex items-center gap-2"><FileText className="w-4 h-4 text-violet-700" /> Informe de Investigación</h2>
              <div className="flex items-center gap-2">
                <span className={`text-[9px] font-bold px-2 py-0.5 rounded-full border ${narrativeMotor==='gemini' ? 'bg-emerald-50 border-emerald-300 text-emerald-700' : 'bg-amber-50 border-amber-300 text-amber-700'}`}>{narrativeMotor==='gemini' ? 'Gemini' : 'Motor Local'}</span>
                <button onClick={() => { navigator.clipboard.writeText(narrative); setCopiedNarrative(true); setTimeout(()=>setCopiedNarrative(false),2000); }} className="flex items-center gap-1 text-[10px] font-semibold text-slate-500 hover:text-slate-700 cursor-pointer">
                  {copiedNarrative ? <><Check className="w-3 h-3 text-emerald-600" /> Copiado</> : <><Copy className="w-3 h-3" /> Copiar</>}
                </button>
              </div>
            </div>
            <div className="bg-[#FAF8F5] rounded-2xl border border-[#E8E3DA] p-5 max-h-[500px] overflow-y-auto">
              {narrative.split('\n').map((line,i) => {
                if (/^\d+\./.test(line.trim())) return <h4 key={i} className="font-bold text-slate-900 mt-4 mb-1 text-sm">{line}</h4>;
                if (line.trim().startsWith('-')||line.trim().startsWith('•')) return <p key={i} className="ml-3 text-xs">• {line.replace(/^[-•]\s*/,'')}</p>;
                if (line.trim()) return <p key={i} className="text-xs mb-1">{line}</p>;
                return <br key={i} />;
              })}
            </div>
          </div>

          <div className="bg-white p-6 rounded-3xl shadow-atelier border border-[#E2DDD5]">
            <h2 className="text-sm font-bold text-slate-900 mb-4 flex items-center gap-2"><Download className="w-4 h-4 text-violet-700" /> Exportar Evidencia Objetiva</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-5 bg-[#FAF8F5] rounded-2xl border border-[#E8E3DA] flex flex-col justify-between">
                <div>
                  <div className="flex items-center gap-2 mb-2"><FileSpreadsheet className="w-5 h-5 text-emerald-700" /><h3 className="font-bold text-slate-900 text-sm">Planilla Excel</h3></div>
                  <p className="text-xs text-slate-600 mb-4 leading-relaxed">Evidencia objetiva tabulada: datos comparativos, correlaciones, estadísticas globales e informe narrativo en hojas separadas. Apta para anexo de investigación.</p>
                </div>
                <button onClick={() => handleExport('xlsx')} disabled={isExporting!==null} className="w-full flex items-center justify-center gap-2 bg-emerald-700 hover:bg-emerald-800 text-white font-bold px-4 py-2.5 rounded-xl text-xs transition cursor-pointer disabled:opacity-40">
                  {isExporting==='xlsx' ? <><RefreshCw className="w-3.5 h-3.5 animate-spin" /> Generando...</> : <><FileSpreadsheet className="w-3.5 h-3.5" /> Descargar Excel (.xlsx)</>}
                </button>
              </div>
              <div className="p-5 bg-[#FAF8F5] rounded-2xl border border-[#E8E3DA] flex flex-col justify-between">
                <div>
                  <div className="flex items-center gap-2 mb-2"><FileText className="w-5 h-5 text-violet-700" /><h3 className="font-bold text-slate-900 text-sm">Informe Word</h3></div>
                  <p className="text-xs text-slate-600 mb-4 leading-relaxed">Informe formal de investigación con portada, hipótesis, tabla de datos, análisis IA y correlaciones. Formato ISO 21001:2018.</p>
                </div>
                <button onClick={() => handleExport('docx')} disabled={isExporting!==null} className="w-full flex items-center justify-center gap-2 bg-violet-900 hover:bg-violet-800 text-white font-bold px-4 py-2.5 rounded-xl text-xs transition cursor-pointer disabled:opacity-40">
                  {isExporting==='docx' ? <><RefreshCw className="w-3.5 h-3.5 animate-spin" /> Generando...</> : <><FileText className="w-3.5 h-3.5" /> Descargar Word (.docx)</>}
                </button>
              </div>
            </div>
          </div>

          <div className="flex gap-3">
            <button onClick={() => setActiveStep(3)} className="flex items-center gap-2 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold px-4 py-2.5 rounded-2xl text-xs transition cursor-pointer">← Métricas</button>
            <button onClick={() => { setActiveStep(1); setSelectedSubjects([]); setHypothesis(null); setComparison(null); setNarrative(''); }} className="flex items-center gap-2 bg-violet-50 hover:bg-violet-100 text-violet-800 border border-violet-200 font-bold px-4 py-2.5 rounded-2xl text-xs transition cursor-pointer"><FlaskConical className="w-3.5 h-3.5" /> Nueva Investigación</button>
          </div>
        </div>
      )}

      {!index && <div className="text-center py-20 text-slate-400"><RefreshCw className="w-8 h-8 mx-auto mb-3 animate-spin opacity-30" /><p className="text-sm">Cargando índice de asignaturas...</p></div>}
    </div>
  );
}
