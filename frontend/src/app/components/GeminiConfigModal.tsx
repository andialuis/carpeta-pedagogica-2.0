'use client';
import { useState, useEffect } from 'react';
import { Sparkles, Key, CheckCircle2, AlertCircle, X, ExternalLink, Cpu, Loader2 } from 'lucide-react';

interface GeminiConfigModalProps {
  isOpen: boolean;
  onClose: () => void;
  onStatusChange?: () => void;
}

export default function GeminiConfigModal({ isOpen, onClose, onStatusChange }: GeminiConfigModalProps) {
  const [statusData, setStatusData] = useState<{
    configured: boolean;
    status: string;
    message: string;
    masked_key?: string | null;
    model: string;
  } | null>(null);

  const [inputKey, setInputKey] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [feedback, setFeedback] = useState<{ type: 'success' | 'error' | 'info'; text: string } | null>(null);

  useEffect(() => {
    if (isOpen) {
      fetchStatus();
      setFeedback(null);
    }
  }, [isOpen]);

  const fetchStatus = async () => {
    setIsLoading(true);
    try {
      const res = await fetch('/api/settings/gemini-status');
      if (res.ok) {
        const data = await res.json();
        setStatusData(data);
      }
    } catch (e) {
      console.error('Error fetching Gemini status', e);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSaveKey = async () => {
    if (!inputKey.trim()) {
      setFeedback({ type: 'error', text: 'Por favor, ingresa una clave de API válida.' });
      return;
    }

    setIsSaving(true);
    setFeedback(null);

    try {
      const res = await fetch('/api/settings/gemini-key', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ api_key: inputKey.trim() })
      });
      const data = await res.json();

      if (data.success) {
        setFeedback({
          type: 'success',
          text: data.message || '¡Clave validada y conectada exitosamente con Gemini 2.5 Flash!'
        });
        setInputKey('');
        fetchStatus();
        if (onStatusChange) onStatusChange();
      } else {
        setFeedback({
          type: 'error',
          text: data.message || 'No se pudo validar la clave. El motor determinista local sigue activo.'
        });
      }
    } catch (err: any) {
      setFeedback({
        type: 'error',
        text: `Error de comunicación con el servidor: ${err.message}. Operando en motor local.`
      });
    } finally {
      setIsSaving(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-xs p-4 animate-in fade-in duration-200">
      <div className="bg-[#FAF8F5] border border-[#E2DDD5] w-full max-w-lg rounded-2xl shadow-2xl overflow-hidden font-sans-clean flex flex-col max-h-[90vh]">
        {/* Encabezado */}
        <div className="p-5 bg-gradient-to-r from-slate-900 to-indigo-950 text-white flex items-center justify-between border-b border-slate-800">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-amber-400/20 text-amber-400 flex items-center justify-center border border-amber-400/30">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-editorial text-lg font-bold text-white flex items-center gap-2">
                Motor de Inteligencia Artificial
              </h3>
              <p className="text-[11px] text-slate-300 font-medium">
                Gestión de Google Gemini (3.6 Flash) y Contingencia Local
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white p-1.5 rounded-lg hover:bg-slate-800 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6 overflow-y-auto space-y-5">
          {/* Tarjeta de Estado Actual */}
          <div className={`p-4 rounded-xl border flex items-start gap-3.5 ${
            statusData?.configured
              ? 'bg-emerald-50/80 border-emerald-300 text-emerald-950'
              : 'bg-amber-50/80 border-amber-300 text-amber-950'
          }`}>
            <div className="mt-0.5 flex-shrink-0">
              {statusData?.configured ? (
                <CheckCircle2 className="w-5 h-5 text-emerald-600" />
              ) : (
                <Cpu className="w-5 h-5 text-amber-600" />
              )}
            </div>
            <div className="text-xs space-y-1">
              <div className="font-bold flex items-center gap-2">
                <span>
                  {statusData?.configured
                    ? (statusData?.model ? `Gemini (${statusData.model}) Activo` : 'Gemini 3.6 Flash Activo')
                    : 'Modo de Contingencia: Motor Local Activo'}
                </span>
                {statusData?.configured && statusData?.masked_key && (
                  <span className="font-mono text-[10px] bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded-full border border-emerald-300">
                    Clave: {statusData.masked_key}
                  </span>
                )}
              </div>
              <p className="text-slate-600 leading-relaxed">
                {statusData?.message || 'Cargando estado del motor...'}
              </p>
            </div>
          </div>

          {/* Explicación Pedagógica Transparente */}
          <div className="bg-white p-4 rounded-xl border border-[#E8E3DA] text-xs text-slate-600 space-y-2">
            <h4 className="font-bold text-slate-800 flex items-center gap-1.5">
              <Cpu className="w-4 h-4 text-amber-600" />
              ¿Cómo opera el sistema ante fallas o falta de API Key?
            </h4>
            <p className="leading-relaxed">
              La plataforma incluye un <strong>motor determinista y no paramétrico integrado</strong> (Spearman ρ, Asimetría de Fisher, Curtosis, ZDP de Vygotsky). Si no tienes clave o se agotan las cuotas, tus cálculos y diagnósticos <strong>nunca se detienen</strong>.
            </p>
            <p className="leading-relaxed">
              Con una clave de Gemini, obtendrás además <strong>narrativas pedagógicas personalizadas</strong>, detección semántica y prescripciones de intervención en lenguaje natural.
            </p>
          </div>

          {/* Formulario de Configuración de Clave */}
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <label className="text-xs font-bold text-slate-700 flex items-center gap-1.5">
                <Key className="w-3.5 h-3.5 text-slate-500" />
                {statusData?.configured ? 'Actualizar Clave de Gemini' : 'Ingresar Clave de API de Gemini'}
              </label>
              <a
                href="https://aistudio.google.com/app/apikey"
                target="_blank"
                rel="noreferrer"
                className="text-[11px] font-semibold text-amber-700 hover:text-amber-800 flex items-center gap-1 hover:underline"
              >
                Obtener gratis en Google AI Studio <ExternalLink className="w-3 h-3" />
              </a>
            </div>

            <div className="flex gap-2">
              <input
                type="password"
                value={inputKey}
                onChange={(e) => setInputKey(e.target.value)}
                placeholder="AIzaSy..."
                className="flex-1 px-3.5 py-2.5 bg-white border border-[#DDD7CD] rounded-xl text-xs font-mono text-slate-900 focus:outline-none focus:ring-2 focus:ring-amber-500/50 focus:border-amber-500"
              />
              <button
                onClick={handleSaveKey}
                disabled={isSaving || !inputKey.trim()}
                className="px-4 py-2.5 bg-slate-900 text-amber-400 hover:bg-slate-800 font-bold text-xs rounded-xl transition shadow-sm disabled:opacity-50 flex items-center gap-1.5 flex-shrink-0"
              >
                {isSaving ? (
                  <>
                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                    Validando...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-3.5 h-3.5" />
                    Conectar
                  </>
                )}
              </button>
            </div>

            {feedback && (
              <div className={`p-3 rounded-xl border text-xs flex items-start gap-2 ${
                feedback.type === 'success'
                  ? 'bg-emerald-50 border-emerald-300 text-emerald-800'
                  : 'bg-rose-50 border-rose-300 text-rose-800'
              }`}>
                {feedback.type === 'success' ? (
                  <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0 mt-0.5" />
                ) : (
                  <AlertCircle className="w-4 h-4 text-rose-600 flex-shrink-0 mt-0.5" />
                )}
                <span>{feedback.text}</span>
              </div>
            )}
          </div>
        </div>

        {/* Footer Modal */}
        <div className="p-4 bg-slate-50 border-t border-[#E8E3DA] flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 text-xs font-semibold text-slate-700 bg-white border border-[#DDD7CD] rounded-xl hover:bg-slate-100 transition"
          >
            Cerrar
          </button>
        </div>
      </div>
    </div>
  );
}
