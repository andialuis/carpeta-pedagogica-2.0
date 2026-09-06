'use client';
import { useState, useEffect } from 'react';
import { 
  User, Mail, School, BookOpen, Award, Save, 
  CheckCircle2, ShieldCheck, HeartHandshake, Sparkles, Brain
} from 'lucide-react';

export default function UserProfilePage() {
  const [profile, setProfile] = useState({
    nombre: '',
    titulo: '',
    institucion: '',
    email: '',
    bio: '',
    marco_predeterminado: 'cbl_cast',
    sensibilidad_outsourcing: 'normal',
    tolerancia_rezago: 'estricta',
  });
  const [isSaving, setIsSaving] = useState(false);
  const [savedSuccess, setSavedSuccess] = useState(false);

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const res = await fetch('/api/user/profile');
      if (res.ok) {
        const data = await res.json();
        setProfile({
          nombre: data.nombre || 'Luis Alfredo Andia Valverde',
          titulo: data.titulo || 'Docente e Investigador Educativo',
          institucion: data.institucion || 'Universidad / Comunidad Académica',
          email: data.email || 'luis.andia.valverde@gmail.com',
          bio: data.bio || 'Creador y desarrollador de Carpeta Pedagógica 2.0. Docente comprometido con el Aprendizaje Basado en Competencias (CBL), el Diseño Universal para el Aprendizaje (DUA marco CAST 2024) y la pedagogía crítica contra el outsourcing cognitivo.',
          marco_predeterminado: data.marco_predeterminado || 'cbl_cast',
          sensibilidad_outsourcing: data.sensibilidad_outsourcing || 'normal',
          tolerancia_rezago: data.tolerancia_rezago || 'estricta',
        });
      }
    } catch (e) {
      console.error("Error al cargar perfil");
    }
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    try {
      const res = await fetch('/api/user/profile', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(profile),
      });
      if (res.ok) {
        setSavedSuccess(true);
        setTimeout(() => setSavedSuccess(false), 3000);
      }
    } catch (e) {
      alert("Error al guardar el perfil");
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="text-slate-800 pb-16 font-sans-clean max-w-4xl mx-auto">
      {/* Header */}
      <header className="mb-8 border-b border-[#E8E3DA] pb-5">
        <div className="flex items-center gap-2 mb-1">
          <span className="text-[10px] font-bold tracking-widest uppercase text-amber-800 bg-amber-100/80 px-2.5 py-0.5 rounded-full border border-amber-300">
            Identidad Docente
          </span>
          <span className="text-[10px] font-medium text-slate-400">• Atelier Pedagógico Personal</span>
        </div>
        <h1 className="text-3xl font-bold font-editorial text-slate-900 flex items-center gap-3">
          <User className="w-8 h-8 text-amber-700" />
          Perfil del Docente / Usuario
        </h1>
        <p className="text-slate-500 text-sm mt-0.5">
          Configura tus datos académicos, firma de dossiers institucionales y preferencias pedagógicas
        </p>
      </header>

      <form onSubmit={handleSave} className="space-y-6">
        {/* Tarjeta de Identificación */}
        <div className="bg-white p-6 sm:p-8 rounded-3xl shadow-atelier border border-[#E2DDD5]">
          <div className="flex items-center gap-4 border-b border-[#EFEAE1] pb-5 mb-6">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-slate-900 to-indigo-950 text-amber-300 flex items-center justify-center font-editorial font-bold text-2xl shadow-md border border-slate-800 flex-shrink-0">
              {profile.nombre ? profile.nombre.charAt(0).toUpperCase() : 'D'}
            </div>
            <div>
              <h2 className="text-xl font-bold font-editorial text-slate-900">
                {profile.nombre || 'Nombre del Docente'}
              </h2>
              <p className="text-xs text-slate-500 font-medium">
                {profile.titulo || 'Cargo Académico'} • {profile.institucion || 'Institución'}
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-5 text-xs">
            <div>
              <label className="font-bold text-slate-700 block mb-1.5">Nombre Completo del Docente:</label>
              <input
                type="text"
                value={profile.nombre}
                onChange={(e) => setProfile({ ...profile, nombre: e.target.value })}
                placeholder="Ej. Dr. Ricardo Morales"
                className="w-full bg-[#FAF8F5] border border-[#DDD7CD] rounded-xl p-3 text-slate-900 font-semibold focus:ring-amber-500 focus:border-amber-500"
                required
              />
            </div>

            <div>
              <label className="font-bold text-slate-700 block mb-1.5">Título / Cargo Académico:</label>
              <input
                type="text"
                value={profile.titulo}
                onChange={(e) => setProfile({ ...profile, titulo: e.target.value })}
                placeholder="Ej. Catedrático de Metodología de la Investigación"
                className="w-full bg-[#FAF8F5] border border-[#DDD7CD] rounded-xl p-3 text-slate-900 font-semibold focus:ring-amber-500 focus:border-amber-500"
              />
            </div>

            <div>
              <label className="font-bold text-slate-700 block mb-1.5">Institución Educativa / Universidad:</label>
              <input
                type="text"
                value={profile.institucion}
                onChange={(e) => setProfile({ ...profile, institucion: e.target.value })}
                placeholder="Ej. Universidad Mayor de San Andrés"
                className="w-full bg-[#FAF8F5] border border-[#DDD7CD] rounded-xl p-3 text-slate-900 font-semibold focus:ring-amber-500 focus:border-amber-500"
              />
            </div>

            <div>
              <label className="font-bold text-slate-700 block mb-1.5">Correo Electrónico Institucional:</label>
              <input
                type="email"
                value={profile.email}
                onChange={(e) => setProfile({ ...profile, email: e.target.value })}
                placeholder="docente@universidad.edu"
                className="w-full bg-[#FAF8F5] border border-[#DDD7CD] rounded-xl p-3 text-slate-900 font-semibold focus:ring-amber-500 focus:border-amber-500"
              />
            </div>

            <div className="sm:col-span-2">
              <label className="font-bold text-slate-700 block mb-1.5">Biografía y Enfoque Pedagógico:</label>
              <textarea
                rows={3}
                value={profile.bio}
                onChange={(e) => setProfile({ ...profile, bio: e.target.value })}
                placeholder="Describe brevemente tu filosofía didáctica, áreas de investigación o valores pedagógicos..."
                className="w-full bg-[#FAF8F5] border border-[#DDD7CD] rounded-xl p-3 text-slate-900 font-medium focus:ring-amber-500 focus:border-amber-500 leading-relaxed font-serif-warm"
              />
            </div>
          </div>
        </div>

        {/* Tarjeta de Preferencias Pedagógicas y Filosofía del Aula */}
        <div className="bg-white p-6 sm:p-8 rounded-3xl shadow-atelier border border-[#E2DDD5]">
          <h3 className="text-lg font-bold font-editorial text-slate-900 mb-2 flex items-center gap-2">
            <Brain className="w-5 h-5 text-amber-700" />
            Preferencias de Analítica & Vigilancia Epistémica
          </h3>
          <p className="text-xs text-slate-500 mb-5 font-medium">
            Personaliza cómo el copiloto y los motores de IA evalúan el esfuerzo y andamian el aprendizaje:
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
            <div className="p-4 rounded-2xl bg-[#FAF8F5] border border-[#E8E3DA]">
              <label className="font-bold text-slate-800 block mb-1.5">Marco Curricular:</label>
              <select
                value={profile.marco_predeterminado}
                onChange={(e) => setProfile({ ...profile, marco_predeterminado: e.target.value })}
                className="w-full bg-white border border-[#DDD7CD] rounded-xl p-2.5 font-bold text-slate-900"
              >
                <option value="cbl_cast">CBL + DUA (CAST 2024)</option>
                <option value="freire_critico">Pedagogía Crítica (Freire)</option>
                <option value="tradicional">Normativa Institucional Clásica</option>
              </select>
              <span className="text-[10px] text-slate-500 block mt-1.5">
                Prioriza competencias auténticas y formatos múltiples.
              </span>
            </div>

            <div className="p-4 rounded-2xl bg-[#FAF8F5] border border-[#E8E3DA]">
              <label className="font-bold text-slate-800 block mb-1.5">Alerta de Outsourcing:</label>
              <select
                value={profile.sensibilidad_outsourcing}
                onChange={(e) => setProfile({ ...profile, sensibilidad_outsourcing: e.target.value })}
                className="w-full bg-white border border-[#DDD7CD] rounded-xl p-2.5 font-bold text-slate-900"
              >
                <option value="alta">Alta (Estricta con Prompts)</option>
                <option value="normal">Equilibrada (Recomendada)</option>
                <option value="relajada">Flexible (Solo Casos Extremos)</option>
              </select>
              <span className="text-[10px] text-slate-500 block mt-1.5">
                Detecta alta nota con nulo sudor intelectual.
              </span>
            </div>

            <div className="p-4 rounded-2xl bg-[#FAF8F5] border border-[#E8E3DA]">
              <label className="font-bold text-slate-800 block mb-1.5">Acompañamiento DUA:</label>
              <select
                value={profile.tolerancia_rezago}
                onChange={(e) => setProfile({ ...profile, tolerancia_rezago: e.target.value })}
                className="w-full bg-white border border-[#DDD7CD] rounded-xl p-2.5 font-bold text-slate-900"
              >
                <option value="estricta">Inmediato (Desde Semana 1)</option>
                <option value="media">Hito 2 (Evaluación Parcial)</option>
              </select>
              <span className="text-[10px] text-slate-500 block mt-1.5">
                Prescribe micro-quizzes y andamiajes tempranos.
              </span>
            </div>
          </div>
        </div>

        {/* Tarjeta de Reconocimiento y Licencia */}
        <div className="bg-gradient-to-br from-[#FAF8F5] to-[#EFEAE1] p-6 rounded-3xl border border-[#E2DDD5] text-xs">
          <div className="flex items-center gap-2 mb-2">
            <ShieldCheck className="w-5 h-5 text-amber-700" />
            <h4 className="font-bold font-editorial text-slate-900 text-sm">
              Autoría & Términos de Licenciamiento
            </h4>
          </div>
          <p className="text-slate-600 leading-relaxed mb-3">
            Esta plataforma web fue concebida, desarrollada e integrada por <strong className="text-slate-900">Luis Alfredo Andia Valverde</strong> (<a href="mailto:luis.andia.valverde@gmail.com" className="text-amber-800 underline font-mono">luis.andia.valverde@gmail.com</a>) como una herramienta de soberanía pedagógica y analítica del aprendizaje humanista.
          </p>
          <div className="bg-white/90 p-3.5 rounded-2xl border border-[#E2DDD5] text-slate-700 flex items-center justify-between">
            <span>Licencia: <strong>Uso y Distribución Libre sin Beneficio Comercial (CC BY-NC 4.0)</strong></span>
            <span className="text-[10px] bg-emerald-100 text-emerald-900 px-2.5 py-0.5 rounded-full font-bold">
              Personal Edition v1.0
            </span>
          </div>
        </div>

        {/* Botón de Guardar */}
        <div className="flex items-center justify-between pt-2">
          {savedSuccess ? (
            <span className="text-xs font-bold text-emerald-700 bg-emerald-50 border border-emerald-300 px-4 py-2 rounded-xl flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4" /> ¡Perfil guardado exitosamente!
            </span>
          ) : (
            <span className="text-xs text-slate-400">Tus cambios se reflejarán en los dossiers oficiales exportados.</span>
          )}

          <button
            type="submit"
            disabled={isSaving}
            className="bg-slate-900 hover:bg-slate-800 text-amber-300 font-bold px-6 py-3 rounded-2xl transition shadow-xs flex items-center gap-2 text-xs cursor-pointer disabled:opacity-50"
          >
            <Save className="w-4 h-4 text-amber-400" />
            {isSaving ? 'Guardando...' : 'Guardar Preferencias de Perfil'}
          </button>
        </div>
      </form>
    </div>
  );
}
