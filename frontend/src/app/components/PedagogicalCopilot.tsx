'use client';
import { useState, useEffect, useRef } from 'react';
import { Sparkles, X, Send, Bot, User, RefreshCw } from 'lucide-react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export default function PedagogicalCopilot() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: '¡Hola, docente! Soy tu **Copiloto Pedagógico**. Estoy aquí para orientarte en diseño curricular por competencias (CBL), diseño universal para el aprendizaje (DUA marco CAST) y prevención del outsourcing cognitivo. ¿En qué te puedo apoyar hoy?'
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentSubject, setCurrentSubject] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const subjParam = params.get('subject');
    if (subjParam) {
      setCurrentSubject(subjParam);
    } else {
      fetch('/api/documents/pending')
        .then(res => res.json())
        .then(data => {
          if (data.subjects && data.subjects.length > 0) {
            setCurrentSubject(data.subjects[0].name);
          }
        })
        .catch(() => {});
    }
  }, []);

  useEffect(() => {
    if (isOpen) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isOpen]);

  const quickPrompts = [
    '¿Cómo evalúo el sudor intelectual en una entrega?',
    'Diseña 3 preguntas socráticas anti-outsourcing',
    'Sugiéreme adaptaciones DUA para rezago',
    '¿Cómo andamiar la formulación de hipótesis?'
  ];

  const handleSendMessage = async (textToSend?: string) => {
    const text = (textToSend || inputMessage).trim();
    if (!text || isLoading) return;

    const newHistory = [...messages, { role: 'user' as const, content: text }];
    setMessages(newHistory);
    setInputMessage('');
    setIsLoading(true);

    try {
      const res = await fetch('/api/copilot/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          subject_name: currentSubject,
          message: text,
          history: newHistory
        })
      });

      const data = await res.json();
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: data.reply || 'No se pudo obtener respuesta del copiloto.'
        }
      ]);
    } catch (e) {
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: 'Ocurrió un error al conectar con el copiloto. El sistema determinista local sigue activo.'
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed bottom-6 right-6 z-50 font-sans-clean">
      {/* Botón Flotante */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="group flex items-center gap-2.5 px-4 py-3 bg-slate-900 text-white rounded-full shadow-2xl hover:bg-slate-800 transition-all duration-300 border border-amber-400/40 hover:scale-105 active:scale-95 cursor-pointer"
          title="Abrir Copiloto Pedagógico con Gemini"
        >
          <span className="relative flex h-3 w-3">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-3 w-3 bg-amber-400"></span>
          </span>
          <Sparkles className="w-4 h-4 text-amber-300 group-hover:rotate-12 transition-transform" />
          <span className="font-bold text-xs tracking-wide text-slate-100">Copiloto Pedagógico</span>
          <span className="text-[10px] bg-amber-400/20 text-amber-300 px-1.5 py-0.5 rounded font-mono font-semibold border border-amber-400/30">
            Gemini
          </span>
        </button>
      )}

      {/* Ventana de Chat Flotante */}
      {isOpen && (
        <div className="w-80 sm:w-96 h-[520px] bg-white border border-[#DDD7CD] rounded-2xl shadow-2xl flex flex-col overflow-hidden animate-in fade-in slide-in-from-bottom-6 duration-200">
          {/* Header */}
          <div className="px-4 py-3 bg-slate-900 text-white flex items-center justify-between border-b border-slate-800">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-lg bg-amber-400/20 text-amber-400 flex items-center justify-center border border-amber-400/30">
                <Sparkles className="w-4 h-4" />
              </div>
              <div>
                <h4 className="font-bold text-xs flex items-center gap-1.5">
                  Copiloto Pedagógico
                  <span className="text-[9px] bg-emerald-500/20 text-emerald-300 px-1.5 py-0.2 rounded border border-emerald-500/30 font-mono">
                    En vivo
                  </span>
                </h4>
                <p className="text-[10px] text-slate-400 truncate max-w-[200px]">
                  {currentSubject ? `Curso: ${currentSubject}` : 'Mentor Curricular & DUA'}
                </p>
              </div>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800 transition cursor-pointer"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Área de Mensajes */}
          <div className="flex-1 overflow-y-auto p-3.5 space-y-3 bg-[#FAF8F5]/60 text-xs">
            {messages.map((m, idx) => (
              <div
                key={idx}
                className={`flex gap-2.5 ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {m.role === 'assistant' && (
                  <div className="w-6 h-6 rounded-full bg-slate-900 text-amber-400 flex-shrink-0 flex items-center justify-center mt-0.5 shadow-xs">
                    <Bot className="w-3.5 h-3.5" />
                  </div>
                )}
                <div
                  className={`max-w-[82%] px-3.5 py-2.5 rounded-2xl text-xs leading-relaxed whitespace-pre-wrap ${
                    m.role === 'user'
                      ? 'bg-slate-900 text-white rounded-tr-xs shadow-xs'
                      : 'bg-white border border-[#E8E3DA] text-slate-800 rounded-tl-xs shadow-2xs font-serif-warm prose prose-xs max-w-none'
                  }`}
                >
                  {m.content}
                </div>
                {m.role === 'user' && (
                  <div className="w-6 h-6 rounded-full bg-amber-500 text-white flex-shrink-0 flex items-center justify-center mt-0.5 shadow-xs">
                    <User className="w-3.5 h-3.5" />
                  </div>
                )}
              </div>
            ))}

            {isLoading && (
              <div className="flex gap-2.5 justify-start items-center text-slate-500 italic text-[11px]">
                <div className="w-6 h-6 rounded-full bg-slate-900 text-amber-400 flex-shrink-0 flex items-center justify-center">
                  <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                </div>
                <span className="bg-white border border-[#E8E3DA] px-3 py-1.5 rounded-xl shadow-2xs">
                  El copiloto está pensando...
                </span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Prompts Rápidos (Chips) */}
          <div className="px-3 py-2 bg-white border-t border-[#EFEAE1] flex gap-1.5 overflow-x-auto no-scrollbar">
            {quickPrompts.map((qp, i) => (
              <button
                key={i}
                onClick={() => handleSendMessage(qp)}
                disabled={isLoading}
                className="whitespace-nowrap text-[10px] bg-[#FAF8F5] hover:bg-slate-100 text-slate-700 border border-[#DDD7CD] px-2.5 py-1 rounded-full transition disabled:opacity-50 hover:border-slate-400 cursor-pointer"
              >
                💡 {qp}
              </button>
            ))}
          </div>

          {/* Input */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSendMessage();
            }}
            className="p-2.5 bg-white border-t border-[#E8E3DA] flex items-center gap-2"
          >
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder="Pregúntale al Copiloto Pedagógico..."
              disabled={isLoading}
              className="flex-1 px-3 py-2 bg-[#FAF8F5] border border-[#DDD7CD] rounded-xl text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-slate-900"
            />
            <button
              type="submit"
              disabled={!inputMessage.trim() || isLoading}
              className="w-8 h-8 rounded-xl bg-slate-900 text-amber-400 flex items-center justify-center hover:bg-slate-800 disabled:opacity-40 disabled:cursor-not-allowed transition cursor-pointer"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
        </div>
      )}
    </div>
  );
}
