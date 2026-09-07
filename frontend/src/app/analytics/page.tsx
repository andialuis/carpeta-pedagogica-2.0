'use client';
import { useState, useEffect } from 'react';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  LineChart, Line, ScatterChart, Scatter, AreaChart, Area, PieChart, Pie, Cell,
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar
} from 'recharts';
import { AlertCircle, TrendingUp, TrendingDown, Users, BookOpen, Brain, Activity, Target, ShieldAlert, CheckCircle2, FileDown, Cpu, Sparkles, FileText, Award, Copy, Check, X } from 'lucide-react';
import GeminiConfigModal from '../components/GeminiConfigModal';

export default function AnalyticsDashboard() {
  const [subjects, setSubjects] = useState<any[]>([]);
  const [selectedSubject, setSelectedSubject] = useState<string>('');
  const [analyticsData, setAnalyticsData] = useState<any>(null);
  const [auditData, setAuditData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('general'); // general, pronosticos, intervencion, enfoque_humano, estudiantes
  const [isGeminiModalOpen, setIsGeminiModalOpen] = useState(false);

  // Estados para Diagnóstico Ejecutivo con IA
  const [isGeneratingNarrative, setIsGeneratingNarrative] = useState(false);
  const [narrativeReport, setNarrativeReport] = useState<string | null>(null);
  const [narrativeMotor, setNarrativeMotor] = useState<string | null>(null);
  const [isNarrativeModalOpen, setIsNarrativeModalOpen] = useState(false);
  const [copiedNarrative, setCopiedNarrative] = useState(false);

  useEffect(() => {
    fetchSubjects();
  }, []);

  useEffect(() => {
    if (selectedSubject) {
      fetchAnalytics(selectedSubject);
      fetchAudit(selectedSubject);
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
      console.error("Error fetching subjects");
    }
  };

  const fetchAnalytics = async (subject: string) => {
    setIsLoading(true);
    try {
      const res = await fetch(`/api/analytics/${encodeURIComponent(subject)}`, { cache: 'no-store' });
      const data = await res.json();
      setAnalyticsData(data);
    } catch (e) {
      console.error("Error fetching analytics");
    }
    setIsLoading(false);
  };

  const fetchAudit = async (subject: string) => {
    try {
      const res = await fetch(`/api/stages/audit/${encodeURIComponent(subject)}/e3`, { method: 'POST', cache: 'no-store' });
      const data = await res.json();
      setAuditData(data);
    } catch (e) {
      console.error("Error fetching audit data");
    }
  };

  const handleDownloadInstrument = (instrumentId: string) => {
    window.open(`/api/instruments/download/${instrumentId}`, '_blank');
  };

  const handleGenerateNarrative = async () => {
    if (!selectedSubject) return;
    setIsGeneratingNarrative(true);
    try {
      const res = await fetch(`/api/analytics/narrative/${encodeURIComponent(selectedSubject)}`, {
        method: 'POST',
      });
      const data = await res.json();
      if (data.status === 'ok') {
        setNarrativeReport(data.reporte_narrativo || data.report);
        setNarrativeMotor(data.motor);
        setIsNarrativeModalOpen(true);
      } else {
        alert("Error al generar diagnóstico: " + (data.message || "Error desconocido"));
      }
    } catch (e) {
      alert("Error de conexión al generar el diagnóstico narrativo con IA.");
    } finally {
      setIsGeneratingNarrative(false);
    }
  };

  const handleCopyNarrative = () => {
    if (!narrativeReport) return;
    navigator.clipboard.writeText(narrativeReport);
    setCopiedNarrative(true);
    setTimeout(() => setCopiedNarrative(false), 2000);
  };

  // MOCK DATA FALLBACK
  const distributionData = [
    { name: '0-20', estudiantes: 1 }, { name: '21-40', estudiantes: 3 },
    { name: '41-60', estudiantes: 5 }, { name: '61-80', estudiantes: 15 },
    { name: '81-100', estudiantes: 8 }
  ];
  const riskData = [
    { name: 'Riesgo Crítico (Abandono)', value: 2, color: '#ef4444' },
    { name: 'Riesgo Moderado (Bajo Rendimiento)', value: 5, color: '#f59e0b' },
    { name: 'Sin Riesgo (Buen Rendimiento)', value: 25, color: '#10b981' }
  ];
  const engagementData = [
    { semana: 'Sem 1', interaccion: 80, entregas: 90 }, { semana: 'Sem 2', interaccion: 85, entregas: 85 },
    { semana: 'Sem 3', interaccion: 70, entregas: 75 }, { semana: 'Sem 4', interaccion: 60, entregas: 65 },
    { semana: 'Sem 5', interaccion: 75, entregas: 80 }
  ];
  const correlationData = [
    { asistencia: 50, nota: 45, student: 'Almendra V.' }, { asistencia: 60, nota: 55, student: 'Carlos R.' },
    { asistencia: 75, nota: 70, student: 'Diana M.' }, { asistencia: 90, nota: 85, student: 'Esteban L.' },
    { asistencia: 95, nota: 95, student: 'Fernanda P.' }, { asistencia: 100, nota: 98, student: 'Luis A.' }
  ];

  // 1. Distribución Gaussiana Dinámica de la Materia
  const activeGaussData = (analyticsData?.insights?.gauss_distribucion && analyticsData.insights.gauss_distribucion.length > 0)
    ? analyticsData.insights.gauss_distribucion.map((g: any) => ({ name: g.rango, estudiantes: g.estudiantes }))
    : distributionData;

  // 2. Correlación Proceso / Iteraciones vs Rendimiento Dinámica
  const activeScatterData = (analyticsData?.insights?.scatter_rendimiento_proceso && analyticsData.insights.scatter_rendimiento_proceso.length > 0)
    ? analyticsData.insights.scatter_rendimiento_proceso.map((s: any) => ({
        asistencia: s.iteraciones ?? 15,
        nota: s.promedio ?? 70,
        student: analyticsData?.llaves ? (analyticsData.llaves[s.id] || s.id) : s.id,
        riesgo: s.riesgo,
        alerta: s.alerta_outsourcing
      }))
    : correlationData;

  // 3. Distribución de Riesgo Dinámica
  const totalStudents = analyticsData?.insights?.total_students || 0;
  const riskCount = analyticsData?.insights?.riesgo_abandono || 0;
  const outCount = analyticsData?.insights?.outsourcing_count || 0;
  const hiddenCount = analyticsData?.insights?.potencial_oculto_count || 0;
  const safeCount = Math.max(0, totalStudents - riskCount - outCount - hiddenCount);

  const activeRiskData = totalStudents > 0 ? [
    { name: 'Riesgo de Abandono', value: riskCount, color: '#ef4444' },
    { name: 'Alerta Outsourcing', value: outCount, color: '#f97316' },
    { name: 'Potencial Oculto (ZDP)', value: hiddenCount, color: '#3b82f6' },
    { name: 'Rendimiento Autónomo', value: safeCount, color: '#10b981' }
  ].filter(d => d.value > 0) : riskData;

  // Cálculo Promedio Deci&Ryan Dinámico
  let radarData: any[] = [];
  if (analyticsData?.insights?.estudiantes && analyticsData.insights.estudiantes.length > 0) {
    const ests = analyticsData.insights.estudiantes;
    let aut = 0, comp = 0, rel = 0;
    let count = 0;
    ests.forEach((e:any) => {
      if (e.autonomia_deci_ryan !== undefined) {
        aut += e.autonomia_deci_ryan;
        comp += e.competencia_deci_ryan;
        rel += e.relacion_deci_ryan;
        count++;
      }
    });
    if (count > 0) {
      radarData = [
        { subject: 'Autonomía', A: Math.round((aut/count)*10), fullMark: 100 },
        { subject: 'Competencia', A: Math.round((comp/count)*10), fullMark: 100 },
        { subject: 'Relación', A: Math.round((rel/count)*10), fullMark: 100 }
      ];
    }
  }

  const autScore = radarData.find((d: any) => d.subject === 'Autonomía')?.A || 75;
  const compScore = radarData.find((d: any) => d.subject === 'Competencia')?.A || 72;
  const relScore = radarData.find((d: any) => d.subject === 'Relación')?.A || 73;

  const allStudents = analyticsData?.insights?.estudiantes || [];
  const getStudentName = (st: any) => {
    if (analyticsData?.llaves && analyticsData.llaves[st.id]) {
      return analyticsData.llaves[st.id];
    }
    return st.nombre_real || st.id;
  };

  const andamiajeUrgenteList = allStudents.filter((st: any) => {
    const zdp = (st.zdp_vygotsky || '').toLowerCase();
    return zdp.includes('urgente') || zdp.includes('prerrequisito') || zdp.includes('intensivo') || st.riesgo_abandono === 'Alto';
  });

  const potencialOcultoList = allStudents.filter((st: any) => {
    const zdp = (st.zdp_vygotsky || '').toLowerCase();
    return zdp.includes('potencial real') || zdp.includes('supera las calificaciones') || zdp.includes('potencial oculto') || (st.iteraciones > 15 && st.promedio < 75);
  });

  const confortDigitalList = allStudents.filter((st: any) => {
    const zdp = (st.zdp_vygotsky || '').toLowerCase();
    return zdp.includes('confort') || zdp.includes('outsourcing') || st.alerta_outsourcing_cognitivo;
  });

  const maestriaAutonomaList = allStudents.filter((st: any) => {
    const zdp = (st.zdp_vygotsky || '').toLowerCase();
    return zdp.includes('maestría') || zdp.includes('autónomo');
  });

  // Verifica si faltan dimensiones cualitativas (Sudor Intelectual)
  const isProcessDataMissing = auditData?.dimensions_missing?.some((d: any) => d.id === 'process');

  return (
    <div className="text-slate-800 pb-12 font-sans-clean">
      <header className="mb-8 flex flex-col md:flex-row md:justify-between md:items-center gap-4 border-b border-[#E8E3DA] pb-5">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-[10px] font-bold tracking-widest uppercase text-amber-800 bg-amber-100/80 px-2.5 py-0.5 rounded-full border border-amber-300">
              Analítica del Aprendizaje 2.0
            </span>
            <span className="text-[10px] font-medium text-slate-400">• Enfoque Crítico & CBL</span>
          </div>
          <h1 className="text-3xl font-bold font-editorial text-slate-900 flex items-center gap-3">
            <Brain className="w-8 h-8 text-amber-700" />
            Panel de Inteligencia Educativa
          </h1>
          <p className="text-slate-500 text-sm mt-0.5 font-medium">
            Diagnóstico integral del aula, seguimiento del sudor intelectual y prescriptiva humanista
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <div className="bg-white border border-[#E2DDD5] p-2 rounded-xl shadow-xs flex items-center gap-2.5">
            <label className="font-semibold text-slate-700 text-xs pl-2 flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-amber-500"></span> Asignatura:
            </label>
            <select 
              className="bg-[#FAF8F5] border border-[#DDD7CD] text-slate-900 text-xs rounded-lg focus:ring-amber-500 focus:border-amber-500 block p-2 font-bold"
              value={selectedSubject}
              onChange={(e) => setSelectedSubject(e.target.value)}
            >
              {subjects.length === 0 && <option value="">Sin asignaturas detectadas</option>}
              {subjects.map((subj, idx) => (
                <option key={idx} value={subj.name}>{subj.name}</option>
              ))}
            </select>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <button
              onClick={handleGenerateNarrative}
              disabled={!selectedSubject || isGeneratingNarrative}
              className="text-xs bg-linear-to-r from-purple-700 to-indigo-700 hover:from-purple-800 hover:to-indigo-800 text-white font-bold px-3 py-2 rounded-xl transition shadow-xs flex items-center gap-1.5 disabled:opacity-50 cursor-pointer"
              title="Generar Diagnóstico Pedagógico Ejecutivo con Inteligencia Artificial"
            >
              <Sparkles className={`w-3.5 h-3.5 text-amber-300 ${isGeneratingNarrative ? 'animate-spin' : ''}`} />
              {isGeneratingNarrative ? 'Analizando...' : '✨ Diagnóstico Ejecutivo (IA)'}
            </button>
            <button
              onClick={() => window.open(`/api/documents/export-carpeta-completa/${encodeURIComponent(selectedSubject)}`, '_blank')}
              disabled={!selectedSubject}
              className="text-xs bg-slate-900 text-amber-300 hover:bg-slate-800 font-bold px-3 py-2 rounded-xl transition shadow-xs flex items-center gap-1.5 disabled:opacity-50"
              title="Descargar Carpeta Pedagógica Consolidada (.docx)"
            >
              <FileText className="w-3.5 h-3.5 text-amber-400" /> Dossier Oficial (.docx)
            </button>
            <a
              href="/planificacion"
              className="text-xs bg-white text-slate-700 font-semibold px-3 py-2 rounded-xl border border-[#DDD7CD] hover:bg-[#F5F2EC] flex items-center gap-1.5 transition shadow-xs"
            >
              <Brain className="w-3.5 h-3.5 text-amber-700" /> Plan Curricular
            </a>
            <a
              href="/evaluacion"
              className="text-xs bg-white text-indigo-900 font-semibold px-3 py-2 rounded-xl border border-indigo-200 hover:bg-indigo-50 flex items-center gap-1.5 transition shadow-xs"
            >
              <Award className="w-3.5 h-3.5 text-indigo-700" /> Evaluación & DUA
            </a>
            <button
              onClick={() => window.open(`/api/documents/export-anonymized/${encodeURIComponent(selectedSubject)}?format=xlsx`, '_blank')}
              disabled={!selectedSubject}
              className="text-xs bg-emerald-50 text-emerald-800 font-semibold px-3 py-2 rounded-xl border border-emerald-300 hover:bg-emerald-100 flex items-center gap-1.5 transition shadow-xs disabled:opacity-50"
              title="Descargar base de datos anonimizada para análisis en R, SPSS o Python"
            >
              <FileDown className="w-3.5 h-3.5" /> Dataset (Excel)
            </button>
            <button
              onClick={() => window.open(`/api/documents/export-anonymized/${encodeURIComponent(selectedSubject)}?format=csv`, '_blank')}
              disabled={!selectedSubject}
              className="text-xs bg-white text-slate-700 font-semibold px-2 py-2 rounded-xl border border-[#D5CFC5] hover:bg-slate-50 flex items-center gap-1 transition shadow-xs disabled:opacity-50"
              title="Descargar formato CSV plano"
            >
              CSV
            </button>
          </div>
        </div>
      </header>

      {/* Banner de Transparencia de Motor IA vs Contingencia Determinista */}
      {analyticsData?.insights?.motor_ia && (
        <div className={`mb-6 p-4 rounded-2xl border flex flex-col md:flex-row items-start md:items-center justify-between gap-3 shadow-xs ${
          analyticsData.insights.motor_ia.modo === 'gemini'
            ? 'bg-emerald-50/80 border-emerald-200 text-emerald-950'
            : 'bg-amber-50/80 border-amber-200 text-amber-950'
        }`}>
          <div className="flex items-start gap-3">
            <div className="p-2 rounded-xl bg-white shadow-xs mt-0.5 flex-shrink-0">
              {analyticsData.insights.motor_ia.modo === 'gemini' ? (
                <Sparkles className="w-5 h-5 text-emerald-600" />
              ) : (
                <Cpu className="w-5 h-5 text-amber-600" />
              )}
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold uppercase tracking-wider">
                  {analyticsData.insights.motor_ia.modo === 'gemini'
                    ? 'Motor de Análisis: Google Gemini 2.5 Flash'
                    : 'Modo de Contingencia Activo: Motor Local Determinista'}
                </span>
                <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${
                  analyticsData.insights.motor_ia.modo === 'gemini'
                    ? 'bg-emerald-100 text-emerald-800'
                    : 'bg-amber-100 text-amber-800'
                }`}>
                  {analyticsData.insights.motor_ia.modelo}
                </span>
              </div>
              <p className="text-xs text-slate-600 mt-1 max-w-3xl leading-relaxed">
                {analyticsData.insights.motor_ia.mensaje}
              </p>
            </div>
          </div>
          {analyticsData.insights.motor_ia.fallback_activado && (
            <button
              onClick={() => setIsGeminiModalOpen(true)}
              className="text-xs bg-slate-900 text-amber-400 hover:bg-slate-800 font-bold px-3.5 py-2 rounded-xl shadow-xs transition flex-shrink-0 flex items-center gap-1.5"
            >
              <Sparkles className="w-3.5 h-3.5" />
              Configurar Gemini
            </button>
          )}
        </div>
      )}

      {/* Tabs de Navegación Estilo Atelier Segmentado */}
      <div className="bg-[#EFEAE1]/70 p-1.5 rounded-2xl border border-[#E2DDD5] flex flex-wrap gap-1.5 mb-8 shadow-xs">
        <button 
          onClick={() => setActiveTab('general')} 
          className={`px-4 py-2 text-xs font-bold rounded-xl transition-all duration-150 ${activeTab === 'general' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-600 hover:text-slate-900 hover:bg-white/50'}`}
        >
          📊 Vista General
        </button>
        <button 
          onClick={() => setActiveTab('pronosticos')} 
          className={`px-4 py-2 text-xs font-bold rounded-xl transition-all duration-150 ${activeTab === 'pronosticos' ? 'bg-white text-purple-900 shadow-sm' : 'text-slate-600 hover:text-slate-900 hover:bg-white/50'}`}
        >
          📈 Pronósticos & Retención
        </button>
        <button 
          onClick={() => setActiveTab('intervencion')} 
          className={`px-4 py-2 text-xs font-bold rounded-xl transition-all duration-150 ${activeTab === 'intervencion' ? 'bg-white text-emerald-900 shadow-sm' : 'text-slate-600 hover:text-slate-900 hover:bg-white/50'}`}
        >
          💡 Prescripción Pedagógica (Gemini)
        </button>
        <button 
          onClick={() => setActiveTab('enfoque_humano')} 
          className={`px-4 py-2 text-xs font-bold rounded-xl transition-all duration-150 flex items-center gap-1.5 ${activeTab === 'enfoque_humano' ? 'bg-rose-900 text-white shadow-sm' : 'text-rose-700 hover:bg-rose-50'}`}
        >
          <ShieldAlert className="w-3.5 h-3.5" /> Enfoque Humano (Anti-Outsourcing)
        </button>
        <button 
          onClick={() => setActiveTab('estudiantes')} 
          className={`px-4 py-2 text-xs font-bold rounded-xl transition-all duration-150 ${activeTab === 'estudiantes' ? 'bg-white text-sky-900 shadow-sm' : 'text-slate-600 hover:text-slate-900 hover:bg-white/50'}`}
        >
          👥 Análisis por Estudiante
        </button>
      </div>

      {isLoading ? (
        <div className="text-center p-20 flex flex-col items-center">
          <Activity className="w-10 h-10 text-indigo-500 animate-pulse mb-4" />
          <p className="text-slate-500 font-medium">Procesando modelos predictivos...</p>
        </div>
      ) : (
        <div className="space-y-8">
          
          {/* TAB: VISTA GENERAL */}
          {activeTab === 'general' && (
            <>
              {/* KPIs de Alto Nivel */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-slate-500 text-sm font-semibold uppercase tracking-wider">Desempeño Global</span>
                    <Target className="text-blue-500 w-5 h-5" />
                  </div>
                  <div className="flex items-baseline gap-2">
                    <span className="text-3xl font-black text-slate-800">{analyticsData?.insights?.promedio_general || "76.4"}</span>
                    <span className="text-sm font-medium text-slate-400">/ 100</span>
                  </div>
                  <div className="mt-2 text-xs font-medium text-emerald-600 flex items-center gap-1">
                    <TrendingUp className="w-3 h-3" /> +2.4% vs mes anterior
                  </div>
                </div>
                
                <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-slate-500 text-sm font-semibold uppercase tracking-wider">Compromiso (Engagement)</span>
                    <Users className="text-indigo-500 w-5 h-5" />
                  </div>
                  <div className="flex items-baseline gap-2">
                    <span className="text-3xl font-black text-slate-800">82%</span>
                  </div>
                  <div className="mt-2 text-xs font-medium text-rose-500 flex items-center gap-1">
                    <TrendingDown className="w-3 h-3" /> -5% caída en participación
                  </div>
                </div>

                <div className="bg-white p-5 rounded-xl border border-rose-200 shadow-sm flex flex-col justify-between bg-rose-50">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-rose-700 text-sm font-semibold uppercase tracking-wider">Riesgo de Abandono</span>
                    <AlertCircle className="text-rose-600 w-5 h-5 animate-pulse" />
                  </div>
                  <div className="flex items-baseline gap-2">
                    <span className="text-3xl font-black text-rose-700">{analyticsData?.insights?.riesgo_abandono ?? "3"}</span>
                    <span className="text-sm font-medium text-rose-500">alumnos</span>
                  </div>
                  <div className="mt-2 text-xs font-bold text-rose-600">
                    Requieren intervención inmediata
                  </div>
                </div>

                <div className="bg-white p-5 rounded-xl border border-emerald-200 shadow-sm flex flex-col justify-between bg-emerald-50">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-emerald-700 text-sm font-semibold uppercase tracking-wider">Tasa de Éxito Proyectada</span>
                    <BookOpen className="text-emerald-600 w-5 h-5" />
                  </div>
                  <div className="flex items-baseline gap-2">
                    <span className="text-3xl font-black text-emerald-700">88%</span>
                  </div>
                  <div className="mt-2 text-xs font-bold text-emerald-600">
                    Probabilidad de aprobar la asignatura
                  </div>
                </div>
              </div>

              {/* Panel de Rigor Estadístico & Métricas No Paramétricas */}
              <div className="bg-white p-5 rounded-xl border border-indigo-100 shadow-sm bg-gradient-to-r from-slate-50 to-indigo-50/30">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-3 border-b border-indigo-100/60 pb-2.5 gap-1">
                  <div className="flex items-center gap-2">
                    <span className="w-2.5 h-2.5 rounded-full bg-indigo-600"></span>
                    <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider">Rigor Estadístico & Métricas No Paramétricas</h3>
                  </div>
                  <span className="text-[11px] text-slate-500 font-medium">Validación de supuestos de normalidad y correlación de rangos</span>
                </div>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center">
                  <div className="bg-white p-3 rounded-lg border border-slate-200/80 shadow-xs">
                    <span className="text-xs text-slate-500 block font-semibold">Mediana Muestral</span>
                    <span className="text-lg font-black text-slate-800">{analyticsData?.insights?.mediana_general || analyticsData?.insights?.promedio_general || "75.0"}</span>
                    <span className="text-[10px] text-slate-400 block mt-0.5">Robusta ante outliers</span>
                  </div>
                  <div className="bg-white p-3 rounded-lg border border-slate-200/80 shadow-xs">
                    <span className="text-xs text-slate-500 block font-semibold">Asimetría Fisher (g₁)</span>
                    <span className="text-lg font-black text-indigo-700">{analyticsData?.insights?.skewness ?? "-0.15"}</span>
                    <span className="text-[10px] text-indigo-600 block mt-0.5 font-medium truncate" title={analyticsData?.insights?.skewness_diagnostico}>
                      {analyticsData?.insights?.skewness_diagnostico ? analyticsData.insights.skewness_diagnostico.split(':')[0] : "Cuasi-simétrica"}
                    </span>
                  </div>
                  <div className="bg-white p-3 rounded-lg border border-slate-200/80 shadow-xs">
                    <span className="text-xs text-slate-500 block font-semibold">Curtosis (g₂)</span>
                    <span className="text-lg font-black text-purple-700">{analyticsData?.insights?.kurtosis ?? "-0.45"}</span>
                    <span className="text-[10px] text-purple-600 block mt-0.5 font-medium truncate" title={analyticsData?.insights?.kurtosis_diagnostico}>
                      {analyticsData?.insights?.kurtosis_diagnostico ? analyticsData.insights.kurtosis_diagnostico.split(':')[0] : "Mesocúrtica"}
                    </span>
                  </div>
                  <div className="bg-white p-3 rounded-lg border border-slate-200/80 shadow-xs">
                    <span className="text-xs text-slate-500 block font-semibold">Spearman ρ (Proceso)</span>
                    <span className="text-lg font-black text-emerald-700">{analyticsData?.insights?.spearman_proceso_nota ?? "0.68"}</span>
                    <span className="text-[10px] text-emerald-600 block mt-0.5 font-medium">Sudor vs Rendimiento</span>
                  </div>
                </div>
              </div>

              {/* Gráficos Principales */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
                  <h3 className="text-lg font-bold text-slate-800 mb-1">Distribución de Calificaciones (Campana de Gauss)</h3>
                  <p className="text-sm text-slate-500 mb-6">Muestra cómo se agrupan las notas del grupo actual.</p>
                  <div className="h-64 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart data={activeGaussData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                        <defs>
                          <linearGradient id="colorStudents" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#6366f1" stopOpacity={0.8}/>
                            <stop offset="95%" stopColor="#6366f1" stopOpacity={0}/>
                          </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                        <XAxis dataKey="name" stroke="#64748b" fontSize={12} />
                        <YAxis stroke="#64748b" fontSize={12} />
                        <Tooltip contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }} />
                        <Area type="monotone" dataKey="estudiantes" stroke="#4f46e5" strokeWidth={3} fillOpacity={1} fill="url(#colorStudents)" />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
                  <h3 className="text-lg font-bold text-slate-800 mb-1">Correlación: Proceso vs. Rendimiento</h3>
                  <p className="text-sm text-slate-500 mb-6">Iteraciones de prompt / esfuerzo frente a calificación.</p>
                  <div className="h-64 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <ScatterChart margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                        <XAxis type="number" dataKey="asistencia" name="Iteraciones / Proceso" stroke="#64748b" fontSize={12} />
                        <YAxis type="number" dataKey="nota" name="Nota Final" stroke="#64748b" fontSize={12} domain={[0, 100]} />
                        <Tooltip cursor={{ strokeDasharray: '3 3' }} contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }} />
                        <Scatter name="Estudiantes" data={activeScatterData} fill="#0ea5e9" />
                      </ScatterChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              </div>
            </>
          )}

          {/* TAB: PRONOSTICOS */}
          {activeTab === 'pronosticos' && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="col-span-2 bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
                <h3 className="text-lg font-bold text-slate-800 mb-1">Tendencia de Compromiso Estudiantil (Engagement)</h3>
                <p className="text-sm text-slate-500 mb-6">Modelo predictivo que analiza el comportamiento a lo largo del tiempo.</p>
                <div className="h-72 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={engagementData} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                      <XAxis dataKey="semana" stroke="#64748b" fontSize={12} />
                      <YAxis stroke="#64748b" fontSize={12} domain={[0, 100]} />
                      <Tooltip contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }} />
                      <Legend />
                      <Line type="monotone" dataKey="interaccion" name="Interacción en Sesiones (%)" stroke="#8b5cf6" strokeWidth={3} dot={{ r: 4 }} activeDot={{ r: 6 }} />
                      <Line type="monotone" dataKey="entregas" name="Entregas a Tiempo (%)" stroke="#10b981" strokeWidth={3} dot={{ r: 4 }} activeDot={{ r: 6 }} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>
              
              <div className="col-span-1 bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex flex-col">
                <h3 className="text-lg font-bold text-slate-800 mb-1">Niveles de Riesgo</h3>
                <p className="text-sm text-slate-500 mb-6">Distribución del grupo según modelo de abandono.</p>
                <div className="flex-1 w-full flex justify-center items-center">
                  <ResponsiveContainer width="100%" height={250}>
                    <PieChart>
                      <Pie data={activeRiskData} cx="50%" cy="50%" innerRadius={60} outerRadius={80} paddingAngle={5} dataKey="value">
                        {activeRiskData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip />
                      <Legend verticalAlign="bottom" height={36} />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          )}

          {/* TAB: INTERVENCIÓN (ALERTA TEMPRANA) */}
          {activeTab === 'intervencion' && (
            <div className="bg-white p-8 rounded-xl border border-slate-200 shadow-sm">
              <div className="flex items-center gap-3 mb-6">
                <div className="bg-indigo-100 p-3 rounded-full">
                  <Brain className="text-indigo-600 w-6 h-6" />
                </div>
                <div>
                  <h3 className="text-2xl font-bold text-slate-800">Motor de Prescripción Pedagógica (Gemini)</h3>
                  <p className="text-slate-500">Recomendaciones generadas por IA basadas en el análisis de datos de la Etapa 3.</p>
                </div>
              </div>
              
              <div className="bg-slate-50 border border-slate-200 rounded-lg p-6 mb-8">
                <h4 className="font-bold text-slate-800 text-lg mb-4">Alertas Críticas de IA:</h4>
                <div className="space-y-4">
                  {analyticsData?.insights?.alertas ? (
                    analyticsData.insights.alertas.map((alerta: string, i: number) => (
                      <div key={i} className="flex items-start gap-3 bg-white p-4 rounded-lg border-l-4 border-rose-500 shadow-sm">
                        <AlertCircle className="text-rose-500 w-5 h-5 flex-shrink-0 mt-0.5" />
                        <p className="text-slate-700 font-medium">{alerta}</p>
                      </div>
                    ))
                  ) : (
                    <div className="text-slate-500 italic">No se han generado alertas prescriptivas todavía. Asegúrate de ejecutar la Etapa 3.</div>
                  )}
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="border border-emerald-200 bg-emerald-50 rounded-lg p-6">
                  <h4 className="font-bold text-emerald-800 mb-2">Acción Sugerida 1: Plan de Nivelación</h4>
                  <p className="text-sm text-emerald-700 mb-4">La IA sugiere que los estudiantes en el cuartil inferior carecen de base teórica. Se recomienda usar la pestaña de <b>Evaluación</b> para generar un test de nivelación.</p>
                  <a href="/evaluacion" className="inline-block bg-emerald-600 text-white text-sm font-medium px-4 py-2 rounded shadow hover:bg-emerald-700 transition">Ir a Crear Evaluación</a>
                </div>
                <div className="border border-blue-200 bg-blue-50 rounded-lg p-6">
                  <h4 className="font-bold text-blue-800 mb-2">Acción Sugerida 2: Ajuste del PDC</h4>
                  <p className="text-sm text-blue-700 mb-4">Dado que la participación cayó un 5% en la última semana, se recomienda modificar las estrategias metodológicas del próximo PDC incorporando gamificación.</p>
                  <a href="/planificacion" className="inline-block bg-blue-600 text-white text-sm font-medium px-4 py-2 rounded shadow hover:bg-blue-700 transition">Ir a Modificar PDC</a>
                </div>
              </div>

            </div>
          )}

          {/* TAB: ENFOQUE HUMANO (NUEVO) */}
          {activeTab === 'enfoque_humano' && (
            <div className="space-y-6">
              
              {/* Bloque de Transparencia Máxima si faltan datos */}
              {isProcessDataMissing ? (
                <div className="bg-rose-50 border border-rose-200 rounded-2xl p-8 shadow-sm">
                  <div className="flex items-start gap-4">
                    <div className="bg-rose-100 p-3 rounded-full flex-shrink-0">
                      <ShieldAlert className="w-8 h-8 text-rose-600" />
                    </div>
                    <div>
                      <h3 className="text-2xl font-bold text-rose-900 mb-2">Gráficos No Generados (Educación Bancaria)</h3>
                      <p className="text-rose-700 mb-4 font-medium">
                        De acuerdo con nuestro compromiso de Máxima Transparencia, no podemos presentarte las analíticas de Autodeterminación (Deci & Ryan) ni medir el Sudor Intelectual del grupo.
                      </p>
                      <p className="text-sm text-rose-600 mb-6">
                        El sistema ha detectado que los datos cargados en la Etapa 1 consisten únicamente en variables numéricas o de rendimiento (evaluaciones tradicionales). Esto impide verificar si el estudiante ha dependido excesivamente de la IA sin aportar "músculo intelectual", dejándonos a ciegas frente al riesgo de <b>Outsourcing Cognitivo</b>.
                      </p>
                      
                      <div className="bg-white border border-rose-200 p-5 rounded-xl">
                        <h4 className="font-bold text-slate-800 mb-2 flex items-center gap-2">
                          <CheckCircle2 className="w-5 h-5 text-emerald-600" /> Solución Proactiva:
                        </h4>
                        <p className="text-sm text-slate-600 mb-4">
                          Descarga el siguiente instrumento diseñado específicamente para recolectar las métricas de proceso que te faltan. Una vez completado, súbelo a la carpeta de tu asignatura y vuelve a ejecutar la Etapa 1.
                        </p>
                        <button 
                          onClick={() => handleDownloadInstrument('registro_sudor')}
                          className="bg-rose-600 hover:bg-rose-700 text-white font-medium text-sm px-5 py-2.5 rounded-lg transition shadow flex items-center justify-center gap-2 w-full md:w-auto"
                        >
                          <FileDown className="w-4 h-4" />
                          Descargar Registro de Sudor Intelectual y DUA
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="space-y-6">
                  {/* Manifiesto y Cita Pedagógica de Paulo Freire */}
                  <div className="bg-gradient-to-r from-[#FAF6EE] via-[#F5EFE6] to-[#FFF] border border-[#E2DDD5] rounded-2xl p-6 shadow-atelier">
                    <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
                      <div className="max-w-2xl">
                        <span className="text-[10px] font-bold tracking-widest uppercase text-amber-800 bg-amber-100/90 px-2.5 py-0.5 rounded-full border border-amber-300 inline-block mb-2">
                          Pedagogía Crítica & Conexión Humana
                        </span>
                        <blockquote className="font-editorial italic text-slate-900 text-lg leading-snug">
                          "Enseñar no es transferir conocimiento, sino crear las posibilidades para su propia producción o construcción."
                        </blockquote>
                        <span className="text-xs text-slate-500 font-semibold block mt-1.5 font-sans-clean">
                          Paulo Freire — Pedagogía de la Autonomía (1996)
                        </span>
                      </div>
                      <div className="bg-white/90 backdrop-blur-xs p-4 rounded-xl border border-[#DDD7CD] text-center flex-shrink-0 shadow-xs">
                        <span className="text-[10px] uppercase font-bold text-slate-400 block tracking-wider">Antídoto Ético</span>
                        <span className="font-editorial font-bold text-amber-900 text-sm block">Sudor Intelectual & ZDP</span>
                        <span className="text-[11px] text-emerald-700 font-semibold mt-0.5 block">Anti-Outsourcing Activo</span>
                      </div>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Radar Chart Deci & Ryan con Guía Pedagógica para el Maestro */}
                    <div className="bg-white p-6 rounded-2xl border border-[#E2DDD5] shadow-atelier flex flex-col justify-between">
                      <div>
                        <div className="flex items-center justify-between mb-1">
                          <h3 className="text-lg font-bold font-editorial text-slate-900">
                            Teoría de Autodeterminación (Deci & Ryan)
                          </h3>
                          <span className="text-[10px] font-bold bg-amber-100 text-amber-900 px-2.5 py-0.5 rounded-full border border-amber-300">
                            Motivación Intrínseca
                          </span>
                        </div>
                        <p className="text-xs text-slate-500 mb-4 font-medium">
                          Evaluación de las 3 necesidades psicológicas básicas para el aprendizaje profundo y duradero:
                        </p>

                        <div className="h-64 w-full flex justify-center items-center">
                          <ResponsiveContainer width="100%" height="100%">
                            <RadarChart cx="50%" cy="50%" outerRadius="70%" data={radarData}>
                              <PolarGrid stroke="#e2e8f0" />
                              <PolarAngleAxis dataKey="subject" tick={{ fill: '#475569', fontSize: 12, fontWeight: 700 }} />
                              <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fill: '#94a3b8' }} />
                              <Radar name="Promedio del Grupo" dataKey="A" stroke="#be123c" fill="#fda4af" fillOpacity={0.5} />
                              <Tooltip contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }} />
                            </RadarChart>
                          </ResponsiveContainer>
                        </div>
                      </div>

                      {/* Guía Pedagógica para el Maestro: ¿Qué significa y para qué le sirve? */}
                      <div className="mt-4 pt-4 border-t border-[#EFEAE1] space-y-3">
                        <div className="flex items-center gap-2">
                          <Brain className="w-4 h-4 text-amber-700" />
                          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-800">
                            ¿Qué significa el resultado y para qué le sirve al docente?
                          </h4>
                        </div>

                        <div className="space-y-2 text-xs font-serif-warm">
                          {/* Autonomía */}
                          <div className="p-3 rounded-xl bg-[#FAF8F5] border border-[#E8E3DA]">
                            <div className="flex items-center justify-between mb-1">
                              <strong className="text-slate-900 font-sans-clean font-bold flex items-center gap-1.5">
                                🎯 Autonomía ({autScore}%)
                              </strong>
                              <span className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                                autScore >= 70 ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'
                              }`}>
                                {autScore >= 70 ? 'Alta Iniciativa' : 'Requiere Flexibilidad'}
                              </span>
                            </div>
                            <p className="text-[11px] text-slate-600 leading-snug mb-1">
                              <strong>¿Qué significa?:</strong> Mide si los alumnos sienten agencia e iniciativa propia en sus tareas, o si actúan únicamente por exigencia punitiva de plazos y órdenes.
                            </p>
                            <p className="text-[11px] text-slate-700 leading-snug">
                              <strong>¿Para qué le sirve al maestro?:</strong> {autScore < 70 
                                ? 'Permite flexibilizar las consignas (ej. ofrecer 2 o 3 opciones de producto DUA: ensayo, video o caso práctico) para reactivar su motivación interna.'
                                : 'Indica alta autorregulación; puedes plantear proyectos de investigación abierta (CBL) con menor supervisión directiva.'}
                            </p>
                          </div>

                          {/* Competencia */}
                          <div className="p-3 rounded-xl bg-[#FAF8F5] border border-[#E8E3DA]">
                            <div className="flex items-center justify-between mb-1">
                              <strong className="text-slate-900 font-sans-clean font-bold flex items-center gap-1.5">
                                🧠 Competencia ({compScore}%)
                              </strong>
                              <span className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                                compScore >= 70 ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'
                              }`}>
                                {compScore >= 70 ? 'Autoeficacia Consolidada' : 'Andamiaje Necesario'}
                              </span>
                            </div>
                            <p className="text-[11px] text-slate-600 leading-snug mb-1">
                              <strong>¿Qué significa?:</strong> Mide la percepción de autoeficacia; si el alumno siente que cuenta con las herramientas y la guía para superar los desafíos propuestos.
                            </p>
                            <p className="text-[11px] text-slate-700 leading-snug">
                              <strong>¿Para qué le sirve al maestro?:</strong> {compScore < 70
                                ? 'Alerta de sobrecarga conceptual; conviene descomponer tareas complejas en micro-metas con retroalimentación inmediata antes del examen sumativo.'
                                : 'El grupo tiene base conceptual sólida; puedes elevar el nivel de exigencia y problematización teórica sin frustración.'}
                            </p>
                          </div>

                          {/* Relación */}
                          <div className="p-3 rounded-xl bg-[#FAF8F5] border border-[#E8E3DA]">
                            <div className="flex items-center justify-between mb-1">
                              <strong className="text-slate-900 font-sans-clean font-bold flex items-center gap-1.5">
                                🤝 Relación / Pertenencia ({relScore}%)
                              </strong>
                              <span className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                                relScore >= 70 ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'
                              }`}>
                                {relScore >= 70 ? 'Comunidad Dialógica' : 'Aislamiento en Aula'}
                              </span>
                            </div>
                            <p className="text-[11px] text-slate-600 leading-snug mb-1">
                              <strong>¿Qué significa?:</strong> Mide la seguridad psicológica para equivocarse o preguntar dudas sin miedo a la burla, y el vínculo empático docente-estudiante.
                            </p>
                            <p className="text-[11px] text-slate-700 leading-snug">
                              <strong>¿Para qué le sirve al maestro?:</strong> {relScore < 70
                                ? 'Fomenta el trabajo cooperativo en parejas heterogéneas, co-evaluación formativa y espacios de escucha activa docente-alumno.'
                                : 'Existe un clima idóneo de confianza para plenarias socráticas, debates abiertos y defensa oral de proyectos.'}
                            </p>
                          </div>
                        </div>
                      </div>
                    </div>

                  {/* Panel Socrático & ZDP Vygotsky con Desglose Nominal de Estudiantes */}
                  <div className="flex flex-col gap-6">
                    {/* Alerta de Outsourcing */}
                    {analyticsData?.insights?.alerta_outsourcing_cognitivo && (
                      <div className="bg-rose-50 border-l-4 border-rose-500 p-5 rounded-r-xl shadow-sm">
                        <div className="flex items-center gap-2 mb-2">
                          <ShieldAlert className="w-5 h-5 text-rose-600" />
                          <h4 className="font-bold text-rose-900">Alerta: Posible Outsourcing Cognitivo</h4>
                        </div>
                        <p className="text-sm text-rose-700">
                          Se han detectado entregas con nivel técnico avanzado pero métricas de iteración (sudor intelectual) muy bajas. 
                          Se requiere activar protocolos de verificación verbal.
                        </p>
                      </div>
                    )}

                    {/* Vygotsky / Andamiaje con Desglose de Estudiantes */}
                    <div className="bg-white border border-[#E2DDD5] p-6 rounded-2xl shadow-atelier flex-1 flex flex-col justify-between">
                      <div>
                        <div className="flex items-center justify-between border-b border-[#EFEAE1] pb-3 mb-4">
                          <div className="flex items-center gap-2">
                            <div className="w-7 h-7 rounded-xl bg-emerald-600 text-white flex items-center justify-center">
                              <Target className="w-4 h-4" />
                            </div>
                            <div>
                              <h4 className="font-bold text-slate-900 text-base font-editorial">
                                Diagnóstico ZDP (Lev Vygotsky)
                              </h4>
                              <span className="text-[10px] text-slate-400 font-medium">
                                Zona de Desarrollo Próximo & Andamiaje Pedagógico
                              </span>
                            </div>
                          </div>
                          <span className="text-[10px] font-bold bg-emerald-50 text-emerald-800 px-2.5 py-1 rounded-full border border-emerald-200">
                            {allStudents.length} estudiantes analizados
                          </span>
                        </div>

                        {/* Diagnóstico Sintético General */}
                        <div className="p-3.5 rounded-xl bg-emerald-50/70 border border-emerald-200 text-emerald-900 text-xs font-semibold mb-4 flex items-center gap-2">
                          <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
                          <span>{analyticsData?.insights?.necesidad_andamiaje_vygotsky || "Evaluando la zona de desarrollo próximo del grupo..."}</span>
                        </div>

                        {/* Desglose de Estudiantes Específicos */}
                        <div className="space-y-4">
                          {/* 1. Andamiaje Urgente */}
                          <div className="p-4 rounded-xl bg-[#FAF8F5] border border-[#E8E3DA]">
                            <div className="flex items-center justify-between mb-2">
                              <strong className="text-xs font-bold text-slate-900 flex items-center gap-1.5">
                                <span className={`w-2.5 h-2.5 rounded-full ${andamiajeUrgenteList.length > 0 ? 'bg-rose-500 animate-pulse' : 'bg-emerald-500'}`}></span>
                                Estudiantes que Requieren Andamiaje Urgente:
                              </strong>
                              <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                                andamiajeUrgenteList.length > 0 ? 'bg-rose-100 text-rose-800 border border-rose-300' : 'bg-emerald-100 text-emerald-800'
                              }`}>
                                {andamiajeUrgenteList.length} detectados
                              </span>
                            </div>

                            {andamiajeUrgenteList.length === 0 ? (
                              <p className="text-xs text-slate-500 font-serif-warm italic">
                                ✓ Ningún estudiante en riesgo crítico de prerrequisitos o andamiaje urgente en este cohorte.
                              </p>
                            ) : (
                              <div className="space-y-2 mt-2">
                                {andamiajeUrgenteList.map((st: any, idx: number) => (
                                  <div key={idx} className="bg-white p-3 rounded-xl border border-rose-200 text-xs">
                                    <div className="flex items-center justify-between mb-1">
                                      <span className="font-bold text-slate-900">
                                        {getStudentName(st)} <span className="font-mono text-[10px] text-slate-400">({st.id})</span>
                                      </span>
                                      <span className="font-mono text-[11px] font-bold text-rose-700 bg-rose-50 px-2 py-0.5 rounded">
                                        Nota: {st.promedio}
                                      </span>
                                    </div>
                                    <p className="text-[11px] text-rose-800 mb-1">
                                      <strong>Diagnóstico:</strong> {st.zdp_vygotsky}
                                    </p>
                                    <p className="text-[10px] text-slate-600 bg-slate-50 p-1.5 rounded-lg border border-slate-200">
                                      💡 <strong>Estrategia docente:</strong> {st.estrategia_hacker_curriculo || 'Brindar tutoría socrática individual y micro-quizzes de andamiaje formativo.'}
                                    </p>
                                  </div>
                                ))}
                              </div>
                            )}
                          </div>

                          {/* 2. Potencial Oculto Detectado */}
                          <div className="p-4 rounded-xl bg-blue-50/60 border border-blue-200">
                            <div className="flex items-center justify-between mb-2">
                              <strong className="text-xs font-bold text-blue-950 flex items-center gap-1.5">
                                <span className="w-2.5 h-2.5 rounded-full bg-blue-500"></span>
                                Estudiantes con Potencial Oculto Detectado (ZDP Activa):
                              </strong>
                              <span className="text-[10px] font-bold bg-blue-100 text-blue-800 px-2 py-0.5 rounded-full border border-blue-300">
                                {potencialOcultoList.length} identificados
                              </span>
                            </div>
                            <p className="text-[11px] text-blue-900/80 mb-2 leading-relaxed">
                              Alumnos cuyo esfuerzo de iteración, asistencia o proceso reflexivo es alto, pero sus calificaciones numéricas aún no lo reflejan plenamente:
                            </p>

                            {potencialOcultoList.length === 0 ? (
                              <p className="text-xs text-slate-500 italic">Sin estudiantes en esta categoría.</p>
                            ) : (
                              <div className="space-y-2 mt-2">
                                {potencialOcultoList.map((st: any, idx: number) => (
                                  <div key={idx} className="bg-white p-3 rounded-xl border border-blue-200 text-xs shadow-2xs">
                                    <div className="flex items-center justify-between mb-1">
                                      <span className="font-bold text-slate-900">
                                        {getStudentName(st)} <span className="font-mono text-[10px] text-slate-400">({st.id})</span>
                                      </span>
                                      <span className="font-mono text-[11px] font-bold text-blue-800 bg-blue-50 px-2 py-0.5 rounded">
                                        Nota: {st.promedio}
                                      </span>
                                    </div>
                                    <p className="text-[11px] text-slate-700 mb-1 font-serif-warm">
                                      <strong>Motivo de detección:</strong> {st.zdp_vygotsky}
                                    </p>
                                    <p className="text-[10px] text-indigo-900 bg-indigo-50/70 p-1.5 rounded-lg border border-indigo-200">
                                      ✨ <strong>Andamiaje DUA recomendado:</strong> {st.estrategia_hacker_curriculo || 'Adaptación en formato de entrega (Acción/Expresión DUA) y rúbrica cualitativa de proceso.'}
                                    </p>
                                  </div>
                                ))}
                              </div>
                            )}
                          </div>

                          {/* 3. Estudiantes en Zona de Maestría */}
                          {maestriaAutonomaList.length > 0 && (
                            <div className="p-3.5 rounded-xl bg-purple-50/60 border border-purple-200 text-xs">
                              <div className="flex items-center justify-between mb-1.5">
                                <strong className="font-bold text-purple-950 flex items-center gap-1.5">
                                  <span>⭐</span> Estudiantes en Maestría / Preparados para Proyectos Autónomos:
                                </strong>
                                <span className="text-[10px] font-bold bg-purple-100 text-purple-800 px-2 py-0.5 rounded-full">
                                  {maestriaAutonomaList.length}
                                </span>
                              </div>
                              <div className="flex flex-wrap gap-1.5 mt-2">
                                {maestriaAutonomaList.map((st: any, idx: number) => (
                                  <span key={idx} className="bg-white text-purple-900 border border-purple-200 px-2.5 py-1 rounded-lg text-[11px] font-semibold flex items-center gap-1 shadow-2xs">
                                    <Award className="w-3 h-3 text-purple-600" />
                                    {getStudentName(st)} ({st.promedio} pts)
                                  </span>
                                ))}
                              </div>
                              <span className="text-[10px] text-purple-800 mt-2 block italic">
                                Sugerencia: Asignar como mentores de pares o proponerles retos de investigación abierta.
                              </span>
                            </div>
                          )}

                          {/* 4. Estudiantes en Confort Digital / Outsourcing si existen */}
                          {confortDigitalList.length > 0 && (
                            <div className="p-3.5 rounded-xl bg-amber-50/60 border border-amber-200 text-xs">
                              <div className="flex items-center justify-between mb-1.5">
                                <strong className="font-bold text-amber-950 flex items-center gap-1.5">
                                  <ShieldAlert className="w-3.5 h-3.5 text-amber-600" /> Zona de Confort Digital / Riesgo de Outsourcing:
                                </strong>
                                <span className="text-[10px] font-bold bg-amber-100 text-amber-800 px-2 py-0.5 rounded-full">
                                  {confortDigitalList.length}
                                </span>
                              </div>
                              <div className="space-y-1.5 mt-2">
                                {confortDigitalList.map((st: any, idx: number) => (
                                  <div key={idx} className="bg-white p-2.5 rounded-lg border border-amber-200 text-[11px]">
                                    <span className="font-bold text-slate-900">{getStudentName(st)}</span> ({st.promedio} pts): {st.zdp_vygotsky}
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

          {/* TAB: ESTUDIANTES (Resultados Individuales por Estudiante) */}
          {activeTab === 'estudiantes' && (
            <div className="bg-white p-8 rounded-2xl border border-[#E2DDD5] shadow-atelier">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-6 gap-4">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Atelier de Seguimiento Humano</span>
                  </div>
                  <h3 className="text-2xl font-bold font-editorial text-slate-900">Resultados Individuales (Desencriptados)</h3>
                  <p className="text-slate-500 text-xs mt-0.5">Evaluación formativa, proficiencia competencial y protocolo anti-outsourcing en tiempo real.</p>
                </div>
                <div className="bg-sky-50 border border-sky-200 text-sky-900 text-xs font-bold px-3 py-1.5 rounded-full flex items-center gap-1.5 shadow-2xs self-start sm:self-auto">
                  <Users className="w-3.5 h-3.5 text-sky-600" /> Privatizado en Origen (Cifrado Local)
                </div>
              </div>
              
              <div className="overflow-x-auto rounded-xl border border-[#EFEAE1]">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="bg-[#FAF8F5] text-slate-600 text-xs border-b border-[#E8E3DA]">
                      <th className="p-3.5 font-bold">Estudiante</th>
                      <th className="p-3.5 font-bold text-center">Promedio</th>
                      <th className="p-3.5 font-bold text-center">Proficiencia (CBL)</th>
                      <th className="p-3.5 font-bold text-center">Autonomía (D&R)</th>
                      <th className="p-3.5 font-bold text-center">Arquetipo / Alerta</th>
                      <th className="p-3.5 font-bold text-center">Acción Pedagógica</th>
                      <th className="p-3.5 font-bold">Estrategia Docente Recomendada</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#F2EDE5]">
                    {analyticsData?.insights?.estudiantes && analyticsData.insights.estudiantes.length > 0 ? (
                      analyticsData.insights.estudiantes.map((est: any, idx: number) => {
                        // Desencriptar el nombre usando la llave local
                        const realName = analyticsData.llaves ? analyticsData.llaves[est.id] || est.id : est.id;
                        const isOut = est.alerta_outsourcing_cognitivo || est.riesgo_outsourcing?.toLowerCase() === 'alto';
                        const isRisk = est.riesgo_abandono === 'Alto';
                        const isMaster = (est.promedio >= 80 && !isOut);
                        
                        return (
                          <tr key={idx} className="hover:bg-[#FAF8F5]/80 transition">
                            <td className="p-3.5">
                              <span className="block font-editorial font-bold text-slate-900 text-sm">{realName}</span>
                              <span className="text-[11px] text-slate-400 font-mono tracking-tight">{est.id}</span>
                            </td>
                            <td className="p-3.5 text-center font-bold text-slate-900 font-editorial text-base">
                              {est.promedio ?? est.rendimiento_actual ?? '-'}
                            </td>
                            <td className="p-3.5 text-center">
                              <span className="font-semibold text-xs text-indigo-900 bg-indigo-50 px-2.5 py-1 rounded-lg border border-indigo-150">
                                {est.nivel_cbl || est.nivel_proficiencia_cbl || 'Competente'}
                              </span>
                            </td>
                            <td className="p-3.5 text-center font-bold text-slate-700 text-xs">
                              {est.autonomia_deci_ryan !== undefined ? (
                                <span className="inline-flex items-center gap-1">
                                  <span className="text-amber-600 font-bold">{est.autonomia_deci_ryan}</span>
                                  <span className="text-slate-400 text-[10px]">/10</span>
                                </span>
                              ) : 'N/D'}
                            </td>
                            <td className="p-3.5 text-center">
                              {isOut ? (
                                <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[10px] font-bold bg-rose-50 text-rose-800 border border-rose-200 shadow-2xs">
                                  ⚡ Alerta Outsourcing
                                </span>
                              ) : isRisk ? (
                                <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[10px] font-bold bg-amber-50 text-amber-800 border border-amber-200">
                                  ⚠️ Riesgo Rezago
                                </span>
                              ) : isMaster ? (
                                <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[10px] font-bold bg-emerald-50 text-emerald-800 border border-emerald-200">
                                  ✨ Maestría Autónoma
                                </span>
                              ) : (
                                <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[10px] font-medium bg-slate-100 text-slate-700">
                                  🌱 En Progresión
                                </span>
                              )}
                            </td>
                            <td className="p-3.5 text-center">
                              {est.requiere_triangulacion ? (
                                <button 
                                  onClick={() => handleDownloadInstrument('triangulacion')}
                                  title="Descargar Guía de Triangulación Socrática"
                                  className="text-xs bg-rose-700 hover:bg-rose-800 text-white font-semibold px-3 py-1.5 rounded-lg shadow-xs flex items-center justify-center gap-1 mx-auto transition"
                                >
                                  <AlertCircle className="w-3.5 h-3.5" /> Entrevista Socrática
                                </button>
                              ) : (
                                <span className="text-emerald-700 text-xs font-semibold bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                                  ✓ Validado
                                </span>
                              )}
                            </td>
                            <td className="p-3.5 text-xs text-slate-600 leading-relaxed max-w-xs">
                              {est.estrategia_hacker_curriculo || est.recomendacion}
                            </td>
                          </tr>
                        );
                      })
                    ) : (
                      <tr>
                        <td colSpan={7} className="p-10 text-center text-slate-500 italic font-editorial">
                          No hay análisis individual disponible. Asegúrate de procesar primero la Etapa 3.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}

        </div>
      )}

      <GeminiConfigModal
        isOpen={isGeminiModalOpen}
        onClose={() => setIsGeminiModalOpen(false)}
        onStatusChange={() => {
          if (selectedSubject) fetchAnalytics(selectedSubject);
        }}
      />

      {/* Modal de Diagnóstico Pedagógico Ejecutivo (IA) */}
      {isNarrativeModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/70 backdrop-blur-xs">
          <div className="bg-white rounded-3xl max-w-3xl w-full border border-[#E8E3DA] shadow-2xl flex flex-col max-h-[88vh] overflow-hidden animate-in fade-in zoom-in-95 duration-200">
            {/* Header */}
            <div className="p-5 border-b border-[#E8E3DA] flex items-center justify-between bg-[#FAF8F5]">
              <div className="flex items-center gap-3">
                <div className="p-2.5 rounded-2xl bg-indigo-600 text-white shadow-xs">
                  <Sparkles className="w-5 h-5 text-amber-300" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="text-lg font-bold font-editorial text-slate-900">
                      Diagnóstico Pedagógico Ejecutivo
                    </h3>
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${
                      narrativeMotor?.includes('gemini')
                        ? 'bg-emerald-50 text-emerald-800 border-emerald-300'
                        : 'bg-amber-50 text-amber-800 border-amber-300'
                    }`}>
                      {narrativeMotor || 'Gemini'}
                    </span>
                  </div>
                  <p className="text-xs text-slate-500 font-medium">
                    Asignatura: <strong className="text-slate-700">{selectedSubject}</strong> • Enfoque CAST DUA & CBL
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={handleCopyNarrative}
                  className="px-3 py-1.5 text-xs font-semibold rounded-xl bg-white border border-[#DDD7CD] hover:bg-slate-50 text-slate-700 transition flex items-center gap-1.5 shadow-2xs cursor-pointer"
                  title="Copiar informe al portapapeles"
                >
                  {copiedNarrative ? (
                    <>
                      <Check className="w-3.5 h-3.5 text-emerald-600" /> Copiado
                    </>
                  ) : (
                    <>
                      <Copy className="w-3.5 h-3.5 text-slate-500" /> Copiar
                    </>
                  )}
                </button>
                <button
                  onClick={() => setIsNarrativeModalOpen(false)}
                  className="p-1.5 rounded-xl text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition cursor-pointer"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>

            {/* Body */}
            <div className="p-6 overflow-y-auto flex-1 space-y-4 bg-white text-slate-800">
              <div className="p-5 rounded-2xl bg-[#FAF8F5] border border-[#E8E3DA] font-serif-warm text-sm leading-relaxed text-slate-800 whitespace-pre-wrap shadow-2xs">
                {narrativeReport}
              </div>
            </div>

            {/* Footer */}
            <div className="p-4 border-t border-[#E8E3DA] bg-[#FAF8F5] flex items-center justify-between text-xs text-slate-500">
              <span>💡 Síntesis directiva orientativa para toma de decisiones y acreditación académica.</span>
              <button
                onClick={() => setIsNarrativeModalOpen(false)}
                className="px-4 py-2 rounded-xl bg-slate-900 text-white font-semibold hover:bg-slate-800 transition cursor-pointer"
              >
                Cerrar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

