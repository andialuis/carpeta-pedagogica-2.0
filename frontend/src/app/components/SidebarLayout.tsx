'use client';
import { useState, useEffect } from 'react';
import { usePathname } from 'next/navigation';
import AuthButton from './AuthButton';
import GeminiConfigModal from './GeminiConfigModal';
import PedagogicalCopilot from './PedagogicalCopilot';
import { 
  FileSpreadsheet, Bot, BrainCircuit, Activity, 
  BookOpen, PlusCircle, Feather, Award, Compass, Sparkles, Cpu,
  FolderTree, User, Settings, HelpCircle, FileText, CheckSquare
} from 'lucide-react';

export default function SidebarLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const [isGeminiModalOpen, setIsGeminiModalOpen] = useState(false);
  const [geminiStatus, setGeminiStatus] = useState<{ configured: boolean; model: string } | null>(null);

  const checkGeminiStatus = async () => {
    try {
      const res = await fetch('/api/settings/gemini-status', { cache: 'no-store' });
      if (res.ok) {
        const data = await res.json();
        setGeminiStatus(data);
      }
    } catch (e) {
      setGeminiStatus({ configured: false, model: 'motor_local' });
    }
  };

  useEffect(() => {
    checkGeminiStatus();
  }, []);

  // Flujo Pedagógico Secuencial y Lógica de Trabajo
  const workflowItems = [
    { step: '1', name: 'Crear Clase', path: '/', icon: <PlusCircle className="w-4 h-4 text-amber-600" />, badge: 'Inicio' },
    { step: '2', name: 'Planificar', path: '/planificacion', icon: <BrainCircuit className="w-4 h-4" />, badge: 'PDC' },
    { step: '3', name: 'Organizar', path: '/organizar', icon: <FolderTree className="w-4 h-4" />, badge: 'REV' },
    { step: '4', name: 'Flujo de Agentes', path: '/agents', icon: <Bot className="w-4 h-4" />, badge: 'IA' },
    { step: '5', name: 'Tablero de Control', path: '/analytics', icon: <Activity className="w-4 h-4" />, badge: 'Métricas' },
    { step: '6', name: 'Evaluación', path: '/evaluacion', icon: <Award className="w-4 h-4" />, badge: 'DUA' },
  ];

  // Módulos de Gestión y Documentación
  const systemItems = [
    { name: 'Mi Perfil Docente', path: '/perfil', icon: <User className="w-4 h-4" /> },
    { name: 'Administración', path: '/administracion', icon: <Settings className="w-4 h-4" /> },
    { name: 'Manual & Términos', path: '/documentacion', icon: <FileText className="w-4 h-4" /> },
  ];

  return (
    <div className="flex h-screen bg-notebook overflow-hidden font-sans-clean">
      {/* Sidebar Atelier */}
      <aside className="w-64 bg-white/95 backdrop-blur-md border-r border-[#E8E3DA] flex flex-col shadow-atelier z-20">
        {/* Cabecera de Marca Editorial */}
        <div className="p-5 border-b border-[#EFEAE1]">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-slate-900 to-indigo-950 text-amber-400 flex items-center justify-center shadow-md flex-shrink-0 border border-slate-800">
              <Feather className="w-5 h-5" />
            </div>
            <div>
              <h1 className="font-editorial font-bold text-lg text-slate-900 leading-tight">
                Carpeta Pedagógica
              </h1>
              <div className="flex items-center gap-1.5 mt-0.5">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
                <span className="text-[11px] font-medium tracking-wider uppercase text-slate-500">
                  Atelier 2.0 • Humano
                </span>
              </div>
            </div>
          </div>
        </div>
        
        {/* Navegación con Flujo Pedagógico */}
        <nav className="flex-1 p-3.5 space-y-3 overflow-y-auto">
          <div>
            <div className="px-3 pt-1 pb-1.5 text-[10px] font-bold uppercase tracking-widest text-slate-400 flex items-center justify-between">
              <span>Flujo de Trabajo</span>
              <span className="text-[9px] bg-slate-100 text-slate-500 px-1.5 py-0.2 rounded font-mono">1 a 6</span>
            </div>

            <div className="space-y-1">
              {workflowItems.map((item) => {
                const isActive = pathname === item.path;
                return (
                  <a 
                    key={item.path} 
                    href={item.path}
                    className={`flex items-center gap-2.5 px-3 py-2 rounded-xl transition-all duration-200 text-xs font-semibold ${
                      isActive 
                        ? 'bg-slate-900 text-white shadow-sm' 
                        : 'text-slate-600 hover:bg-[#F5F2EC] hover:text-slate-900'
                    }`}
                  >
                    <span className={`w-4 h-4 rounded-full flex items-center justify-center text-[10px] font-mono font-bold ${
                      isActive ? 'bg-amber-400 text-slate-950' : 'bg-slate-100 text-slate-500'
                    }`}>
                      {item.step}
                    </span>
                    <span className={`${isActive ? 'text-amber-400' : ''}`}>
                      {item.icon}
                    </span>
                    <span className="truncate flex-1">{item.name}</span>
                    {isActive ? (
                      <span className="w-1.5 h-1.5 rounded-full bg-amber-400"></span>
                    ) : (
                      <span className="text-[9px] font-medium text-slate-400 bg-slate-50 px-1.5 py-0.5 rounded border border-slate-200/50">
                        {item.badge}
                      </span>
                    )}
                  </a>
                );
              })}
            </div>
          </div>

          <div className="pt-2 border-t border-[#EFEAE1]">
            <div className="px-3 pt-1 pb-1.5 text-[10px] font-bold uppercase tracking-widest text-slate-400">
              Sistema & Soporte
            </div>
            <div className="space-y-1">
              {systemItems.map((item) => {
                const isActive = pathname === item.path;
                return (
                  <a 
                    key={item.path} 
                    href={item.path}
                    className={`flex items-center gap-2.5 px-3 py-2 rounded-xl transition-all duration-200 text-xs font-semibold ${
                      isActive 
                        ? 'bg-slate-900 text-white shadow-sm' 
                        : 'text-slate-600 hover:bg-[#F5F2EC] hover:text-slate-900'
                    }`}
                  >
                    <span className={`${isActive ? 'text-amber-400' : 'text-slate-500'}`}>
                      {item.icon}
                    </span>
                    <span className="truncate flex-1">{item.name}</span>
                    {isActive && (
                      <span className="w-1.5 h-1.5 rounded-full bg-amber-400"></span>
                    )}
                  </a>
                );
              })}
            </div>
          </div>

          <div className="pt-2 px-1">
            <div className="bg-gradient-to-br from-[#F7F4EE] to-[#EFEAE1] p-3 rounded-xl border border-[#E2DDD5] text-center">
              <Compass className="w-4 h-4 text-amber-700 mx-auto mb-1 opacity-80" />
              <p className="font-editorial italic text-[11px] text-slate-700 font-medium leading-snug">
                "Enseñar es un acto de coraje y creación."
              </p>
              <span className="text-[9px] text-slate-400 block mt-0.5">Paulo Freire</span>
            </div>
          </div>
        </nav>

        {/* Estado del Motor de IA & Contingencia */}
        <div className="p-2.5 border-t border-[#EFEAE1] bg-white">
          <button
            onClick={() => setIsGeminiModalOpen(true)}
            className={`w-full flex items-center justify-between p-2 rounded-xl text-left border transition-all text-xs font-semibold ${
              geminiStatus?.configured
                ? 'bg-emerald-50/70 border-emerald-200 text-emerald-900 hover:bg-emerald-100/70'
                : 'bg-amber-50/70 border-amber-200 text-amber-900 hover:bg-amber-100/70'
            }`}
          >
            <div className="flex items-center gap-2">
              <span className="relative flex h-2 w-2">
                <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${geminiStatus?.configured ? 'bg-emerald-400' : 'bg-amber-400'}`}></span>
                <span className={`relative inline-flex rounded-full h-2 w-2 ${geminiStatus?.configured ? 'bg-emerald-500' : 'bg-amber-500'}`}></span>
              </span>
              <div className="flex flex-col">
                <span className="text-[11px] font-bold leading-tight">
                  {geminiStatus?.configured ? (geminiStatus.model?.startsWith('gemini') ? `Gemini (${geminiStatus.model.replace('gemini-', '')})` : 'Gemini Flash') : 'Motor Determinista'}
                </span>
                <span className="text-[9px] text-slate-500 font-normal">
                  {geminiStatus?.configured ? 'IA Generativa Conectada' : 'Contingencia Local Activa'}
                </span>
              </div>
            </div>
            <Sparkles className="w-3.5 h-3.5 text-amber-600 opacity-80" />
          </button>
        </div>

        {/* Footer Usuario & Crédito de Autoría */}
        <div className="p-3 border-t border-[#EFEAE1] bg-slate-50/60 flex flex-col gap-2">
          <AuthButton />
          <div className="text-[10px] text-slate-500 text-center pt-1 border-t border-slate-200/60 leading-tight">
            <span>Creador: <strong className="text-slate-800">Luis Alfredo Andia Valverde</strong></span>
            <a href="mailto:luis.andia.valverde@gmail.com" className="block text-[9px] text-amber-800/90 hover:underline font-mono">
              luis.andia.valverde@gmail.com
            </a>
            <span className="block text-[9px] text-slate-400">Distribución libre no comercial</span>
          </div>
        </div>
      </aside>

      {/* Main Content Area con Textura Cálida */}
      <main className="flex-1 flex flex-col h-screen overflow-hidden">
        <div className="flex-1 overflow-y-auto p-6 md:p-10 relative">
          <div className="max-w-6xl mx-auto w-full">
            {children}
          </div>
        </div>
      </main>

      {/* Modal de Configuración y Transparencia de Gemini */}
      <GeminiConfigModal
        isOpen={isGeminiModalOpen}
        onClose={() => setIsGeminiModalOpen(false)}
        onStatusChange={checkGeminiStatus}
      />

      {/* Copiloto Pedagógico Flotante Global */}
      <PedagogicalCopilot />
    </div>
  );
}
