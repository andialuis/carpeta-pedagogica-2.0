'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { 
  BookPlus, ArrowLeft, CheckCircle2, GraduationCap, 
  Calendar, Clock, School, User, Layers, Info, Sparkles 
} from 'lucide-react';

export default function NuevaMateriaPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [createdSubject, setCreatedSubject] = useState<string>('');

  const [formData, setFormData] = useState({
    name: '',
    code: '',
    group: 'Grupo 1',
    system: 'superior', // regular, superior, tecnico, otro
    level: 'pregrado', // kinder, primaria, secundaria, pregrado, postgrado, tecnico_medio, tecnico_superior
    duration: 'semestral', // mensual, bimestral, trimestral, semestral, anual, modular
    year: new Date().getFullYear(),
    period: '1',
    teacher: '',
    description: '',
    create_sample_data: true
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target;
    if (type === 'checkbox') {
      const checked = (e.target as HTMLInputElement).checked;
      setFormData(prev => ({ ...prev, [name]: checked }));
    } else {
      setFormData(prev => ({ ...prev, [name]: value }));
    }
  };

  const handleSystemChange = (system: string) => {
    let defaultLevel = 'pregrado';
    if (system === 'regular') defaultLevel = 'secundaria';
    if (system === 'tecnico') defaultLevel = 'tecnico_superior';
    if (system === 'superior') defaultLevel = 'pregrado';
    setFormData(prev => ({ ...prev, system, level: defaultLevel }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.name.trim()) {
      alert('Por favor introduce el nombre de la asignatura.');
      return;
    }

    setLoading(true);
    try {
      const res = await fetch('/api/subjects/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      const data = await res.json();
      if (res.ok && data.success) {
        setSuccess(true);
        setCreatedSubject(data.subject_name);
      } else {
        alert(data.detail || 'Ocurrió un error al crear la asignatura.');
      }
    } catch (err) {
      alert('Error al conectar con el servidor.');
    }
    setLoading(false);
  };

  return (
    <div className="text-slate-800 pb-12 font-sans-clean">
      <header className="mb-8 flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-[#E8E3DA] pb-5">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-[10px] font-bold tracking-widest uppercase text-amber-800 bg-amber-100/80 px-2.5 py-0.5 rounded-full border border-amber-300">
              Diseño Curricular
            </span>
            <span className="text-[10px] font-medium text-slate-400">• Estructura & Metadatos</span>
          </div>
          <h1 className="text-3xl font-bold font-editorial text-slate-900 flex items-center gap-3">
            <BookPlus className="w-8 h-8 text-amber-700" />
            Configurar Nueva Asignatura
          </h1>
          <p className="text-slate-500 text-sm mt-0.5 font-medium">
            Crea la estructura pedagógica, asigna el grupo/cohorte y dataset inicial para cualquier nivel educativo
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button 
            type="button" 
            onClick={() => router.push('/')}
            className="text-xs bg-white text-slate-700 hover:bg-slate-50 font-semibold px-3.5 py-2.5 rounded-xl border border-[#D5CFC5] flex items-center gap-1.5 transition shadow-xs"
          >
            <ArrowLeft className="w-3.5 h-3.5" /> Volver al Inicio
          </button>
        </div>
      </header>

      <main className="max-w-4xl mx-auto">
        {success ? (
          <div className="bg-white rounded-2xl p-8 border border-[#E2DDD5] shadow-atelier text-center">
            <div className="w-16 h-16 bg-emerald-100 text-emerald-700 rounded-full flex items-center justify-center mx-auto mb-4 border border-emerald-200">
              <CheckCircle2 className="w-10 h-10" />
            </div>
            <h2 className="text-2xl font-bold text-slate-900 mb-2">¡Asignatura Creada Exitosamente!</h2>
            <p className="text-slate-600 mb-6 font-medium">
              Se ha creado el espacio de trabajo para: <strong className="text-indigo-700">{createdSubject}</strong> con sus carpetas analíticas y manifiesto.
            </p>
            <div className="flex flex-wrap gap-3 justify-center">
              <button
                onClick={() => router.push(`/planificacion?subject=${encodeURIComponent(createdSubject)}`)}
                className="bg-amber-700 hover:bg-amber-800 text-white font-bold px-5 py-3 rounded-xl transition flex items-center justify-center gap-2 shadow-xs text-xs cursor-pointer"
              >
                Paso 2: Diseñar Plan Curricular →
              </button>
              <button
                onClick={() => router.push(`/organizar?subject=${encodeURIComponent(createdSubject)}`)}
                className="bg-slate-900 hover:bg-slate-800 text-amber-300 font-bold px-5 py-3 rounded-xl transition flex items-center justify-center gap-2 shadow-xs text-xs cursor-pointer"
              >
                Paso 3: Ver Expediente REV →
              </button>
              <button
                onClick={() => router.push(`/agents?subject=${encodeURIComponent(createdSubject)}`)}
                className="bg-indigo-900 hover:bg-indigo-800 text-white font-bold px-5 py-3 rounded-xl transition flex items-center justify-center gap-2 shadow-xs text-xs cursor-pointer"
              >
                <Sparkles className="w-4 h-4 text-amber-400" /> Paso 4: Flujo de Agentes
              </button>
              <button
                onClick={() => {
                  setSuccess(false);
                  setFormData({
                    name: '',
                    code: '',
                    group: 'Grupo 1',
                    system: 'superior',
                    level: 'pregrado',
                    duration: 'semestral',
                    year: new Date().getFullYear(),
                    period: '1',
                    teacher: '',
                    description: '',
                    create_sample_data: true
                  });
                }}
                className="bg-[#FAF8F5] text-slate-700 border border-[#DDD7CD] font-medium px-4 py-3 rounded-xl hover:bg-[#F2EDE5] transition text-xs cursor-pointer"
              >
                + Crear Otra
              </button>
            </div>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="bg-white rounded-2xl p-8 border border-[#E2DDD5] shadow-atelier space-y-8">
            {/* 1. Información General */}
            <section className="space-y-4">
              <h2 className="text-lg font-bold font-editorial text-slate-900 flex items-center gap-2 border-b border-[#EFEAE1] pb-2">
                <GraduationCap className="w-5 h-5 text-amber-700" />
                1. Información Básica de la Asignatura
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="md:col-span-2">
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">Nombre de la Asignatura *</label>
                  <input
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleChange}
                    placeholder="Ej. Introducción a la Investigación, Cálculo I, Biología..."
                    required
                    className="w-full bg-[#FAF8F5] border border-[#DDD7CD] rounded-xl p-2.5 text-slate-900 text-sm focus:ring-2 focus:ring-amber-500 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">Código / Sigla</label>
                  <input
                    type="text"
                    name="code"
                    value={formData.code}
                    onChange={handleChange}
                    placeholder="Ej. INV101, MAT201..."
                    className="w-full bg-[#FAF8F5] border border-[#DDD7CD] rounded-xl p-2.5 text-slate-900 text-sm focus:ring-2 focus:ring-amber-500 focus:outline-none"
                  />
                </div>
              </div>

              {/* Grupo / Cohorte y Previsualización Oficial */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
                    Grupo / Paralelo / Cohorte
                  </label>
                  <input
                    type="text"
                    name="group"
                    value={formData.group}
                    onChange={handleChange}
                    placeholder="Ej. Grupo 1, Grupo 2, 2026, Paralelo A..."
                    className="w-full bg-[#FAF8F5] border border-[#DDD7CD] rounded-xl p-2.5 text-slate-900 text-sm focus:ring-2 focus:ring-amber-500 focus:outline-none"
                  />
                  <p className="text-[10px] text-slate-400 mt-1">
                    Permite gestionar múltiples grupos de la misma asignatura (ej. INV101 Grupo 2026 y Grupo 2) con notas y expedientes independientes.
                  </p>
                </div>

                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
                    Identificador Oficial del Expediente
                  </label>
                  <div className="bg-[#FAF8F5] border border-[#DDD7CD] rounded-xl p-2.5 flex items-center min-h-[42px]">
                    <span className="font-mono text-xs font-bold text-indigo-950">
                      {formData.code ? `${formData.code.trim()} - ` : ''}
                      {formData.name.trim() || 'Nombre Asignatura'}
                      {formData.group ? ` (${formData.group.trim()})` : ''}
                    </span>
                  </div>
                  <p className="text-[10px] text-slate-400 mt-1">
                    Nombre de la carpeta de trabajo y encabezado oficial en documentos ISO 21001.
                  </p>
                </div>
              </div>
            </section>

            {/* 2. Sistema Educativo y Nivel */}
            <section className="space-y-4">
              <h2 className="text-lg font-bold font-editorial text-slate-900 flex items-center gap-2 border-b border-[#EFEAE1] pb-2">
                <School className="w-5 h-5 text-amber-700" />
                2. Sistema Educativo y Nivel
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-2">Subsistema Educativo</label>
                  <div className="grid grid-cols-3 gap-2">
                    {[
                      { id: 'superior', label: 'Superior / Univ.' },
                      { id: 'regular', label: 'Regular (Colegio)' },
                      { id: 'tecnico', label: 'Técnico / Instituto' }
                    ].map(sys => (
                      <button
                        key={sys.id}
                        type="button"
                        onClick={() => handleSystemChange(sys.id)}
                        className={`py-2 px-3 text-xs font-semibold rounded-xl border transition ${
                          formData.system === sys.id 
                            ? 'bg-slate-900 text-amber-300 border-slate-900 shadow-xs' 
                            : 'bg-[#FAF8F5] text-slate-700 border-[#DDD7CD] hover:bg-[#F2EDE5]'
                        }`}
                      >
                        {sys.label}
                      </button>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">Nivel Específico</label>
                  <select
                    name="level"
                    value={formData.level}
                    onChange={handleChange}
                    className="w-full bg-[#FAF8F5] border border-[#DDD7CD] rounded-xl p-2.5 text-slate-900 text-sm focus:ring-2 focus:ring-amber-500 focus:outline-none font-medium"
                  >
                    {formData.system === 'regular' && (
                      <>
                        <option value="kinder">Educación Inicial (Kinder / Pre-kinder)</option>
                        <option value="primaria">Educación Primaria</option>
                        <option value="secundaria">Educación Secundaria</option>
                      </>
                    )}
                    {formData.system === 'superior' && (
                      <>
                        <option value="pregrado">Educación Superior (Pregrado / Licenciatura / Ingeniería)</option>
                        <option value="postgrado">Postgrado (Maestría / Diplomado / Doctorado)</option>
                        <option value="educacion_continua">Educación Continua / Cursos de Extensión</option>
                      </>
                    )}
                    {formData.system === 'tecnico' && (
                      <>
                        <option value="tecnico_medio">Técnico Medio / Bachillerato Técnico</option>
                        <option value="tecnico_superior">Técnico Superior</option>
                      </>
                    )}
                  </select>
                </div>
              </div>
            </section>

            {/* 3. Temporalidad y Ciclo */}
            <section className="space-y-4">
              <h2 className="text-lg font-bold font-editorial text-slate-900 flex items-center gap-2 border-b border-[#EFEAE1] pb-2">
                <Clock className="w-5 h-5 text-amber-700" />
                3. Temporalidad y Calendario
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">Modalidad de Tiempo</label>
                  <select
                    name="duration"
                    value={formData.duration}
                    onChange={handleChange}
                    className="w-full bg-[#FAF8F5] border border-[#DDD7CD] rounded-xl p-2.5 text-slate-900 text-sm focus:ring-2 focus:ring-amber-500 focus:outline-none font-medium"
                  >
                    <option value="mensual">Mensual (1 mes / Modular intensivo)</option>
                    <option value="bimestral">Bimestral (2 meses)</option>
                    <option value="trimestral">Trimestral (3 meses)</option>
                    <option value="semestral">Semestral (4 a 6 meses)</option>
                    <option value="anual">Anual (Año lectivo completo)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">Año Académico</label>
                  <input
                    type="number"
                    name="year"
                    value={formData.year}
                    onChange={handleChange}
                    min="2020"
                    max="2035"
                    className="w-full bg-[#FAF8F5] border border-[#DDD7CD] rounded-xl p-2.5 text-slate-900 text-sm focus:ring-2 focus:ring-amber-500 focus:outline-none font-medium"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">Período / Semestre</label>
                  <input
                    type="text"
                    name="period"
                    value={formData.period}
                    onChange={handleChange}
                    placeholder="Ej. 1, 2, I-2025, Módulo 2..."
                    className="w-full bg-[#FAF8F5] border border-[#DDD7CD] rounded-xl p-2.5 text-slate-900 text-sm focus:ring-2 focus:ring-amber-500 focus:outline-none font-medium"
                  />
                </div>
              </div>
            </section>

            {/* 4. Datos del Docente y Opciones */}
            <section className="space-y-4">
              <h2 className="text-lg font-bold font-editorial text-slate-900 flex items-center gap-2 border-b border-[#EFEAE1] pb-2">
                <User className="w-5 h-5 text-amber-700" />
                4. Docente y Opciones Analíticas
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">Docente Responsable</label>
                  <input
                    type="text"
                    name="teacher"
                    value={formData.teacher}
                    onChange={handleChange}
                    placeholder="Nombre del docente o tutor..."
                    className="w-full bg-[#FAF8F5] border border-[#DDD7CD] rounded-xl p-2.5 text-slate-900 text-sm focus:ring-2 focus:ring-amber-500 focus:outline-none"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">Descripción / Observaciones</label>
                  <input
                    type="text"
                    name="description"
                    value={formData.description}
                    onChange={handleChange}
                    placeholder="Detalles sobre el grupo o metodología..."
                    className="w-full bg-[#FAF8F5] border border-[#DDD7CD] rounded-xl p-2.5 text-slate-900 text-sm focus:ring-2 focus:ring-amber-500 focus:outline-none"
                  />
                </div>
              </div>

              <div className="bg-[#FAF6EE] border border-amber-200 rounded-xl p-4 flex items-start gap-3 mt-4">
                <input
                  type="checkbox"
                  id="create_sample_data"
                  name="create_sample_data"
                  checked={formData.create_sample_data}
                  onChange={handleChange}
                  className="mt-1 h-4 w-4 text-amber-600 focus:ring-amber-500 border-[#DDD7CD] rounded cursor-pointer"
                />
                <label htmlFor="create_sample_data" className="text-xs text-amber-950 cursor-pointer leading-relaxed">
                  <strong className="block font-bold text-amber-900 mb-0.5">Generar dataset inicial listo para las 4 etapas</strong>
                  Crea automáticamente las plantillas de Matrícula, Notas, Asistencia y Registro de Sudor Intelectual en la carpeta para que puedas correr el flujo de agentes de inmediato.
                </label>
              </div>
            </section>

            <div className="pt-4 flex gap-4">
              <button
                type="submit"
                disabled={loading}
                className="flex-1 bg-slate-900 text-amber-300 font-bold py-3.5 px-6 rounded-xl hover:bg-slate-800 transition flex items-center justify-center gap-2 shadow-sm disabled:opacity-50"
              >
                {loading ? 'Creando Estructura de la Asignatura...' : '✓ Crear y Configurar Asignatura'}
              </button>
              <button
                type="button"
                onClick={() => router.push('/')}
                className="bg-[#F2EDE5] text-slate-700 font-semibold py-3.5 px-6 rounded-xl hover:bg-[#E8E3DA] transition"
              >
                Cancelar
              </button>
            </div>
          </form>
        )}
      </main>
    </div>
  );
}
