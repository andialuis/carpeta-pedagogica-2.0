'use client';

import React, { useState, useEffect } from 'react';
import { Cloud, CloudUpload, Download, ExternalLink, CheckCircle2, AlertCircle, X, Shield, FolderArchive } from 'lucide-react';

interface DriveBackupModalProps {
  isOpen: boolean;
  onClose: () => void;
  subjectName: string;
}

export default function DriveBackupModal({ isOpen, onClose, subjectName }: DriveBackupModalProps) {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [driveStatus, setDriveStatus] = useState<any>(null);

  useEffect(() => {
    if (isOpen) {
      setResult(null);
      setError(null);
      fetchDriveStatus();
    }
  }, [isOpen]);

  const fetchDriveStatus = async () => {
    try {
      const res = await fetch('/api/drive/status');
      if (res.ok) {
        const data = await res.json();
        setDriveStatus(data);
      }
    } catch (e) {
      console.warn('No se pudo verificar estado de Drive:', e);
    }
  };

  const handleCreateBackup = async () => {
    if (!subjectName) return;
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const res = await fetch(`/api/drive/backup-subject/${encodeURIComponent(subjectName)}`, {
        method: 'POST'
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Error al generar el respaldo.');
      }
      setResult(data);
    } catch (err: any) {
      setError(err.message || 'Ocurrió un error inesperado al conectar con Google Drive.');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-xs p-4 animate-in fade-in duration-200">
      <div className="bg-white rounded-3xl shadow-2xl border border-[#DDD7CD] max-w-lg w-full p-6 relative overflow-hidden">
        {/* Cabecera decorativa */}
        <div className="flex items-center justify-between pb-4 border-b border-[#E8E3DA] mb-5">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-blue-50 border border-blue-200 flex items-center justify-center text-blue-600 shadow-2xs">
              <CloudUpload className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="font-editorial text-lg font-bold text-slate-900">
                  Respaldo en Google Drive
                </h3>
                <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-blue-100 text-blue-800 border border-blue-200">
                  Etapa 1
                </span>
              </div>
              <p className="text-xs text-slate-500 font-sans-clean">
                Copia soberana de carpetas originales y estructura revisada (-REV)
              </p>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="text-slate-400 hover:text-slate-700 p-1.5 rounded-xl hover:bg-slate-100 transition cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Info de la materia */}
        <div className="bg-[#FAF8F5] border border-[#E8E3DA] rounded-2xl p-3.5 mb-5">
          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-500 font-medium">Materia seleccionada:</span>
            <span className="font-bold text-slate-900 font-mono">{subjectName || 'No seleccionada'}</span>
          </div>
          <div className="flex items-center justify-between text-xs mt-1.5 pt-1.5 border-t border-[#E8E3DA]">
            <span className="text-slate-500 font-medium">Contenido del respaldo:</span>
            <span className="text-slate-700 font-semibold">Archivos Base + Carpetas -REV preparadas</span>
          </div>
        </div>

        {/* Estado previo / Acción */}
        {!result && !loading && (
          <div className="space-y-4">
            <div className="text-xs text-slate-600 leading-relaxed bg-blue-50/60 border border-blue-200 rounded-2xl p-4">
              <div className="flex items-start gap-2.5">
                <Shield className="w-4 h-4 text-blue-600 shrink-0 mt-0.5" />
                <div>
                  <p className="font-semibold text-blue-950 mb-1">
                    ¿Por qué respaldar al terminar la Etapa 1?
                  </p>
                  <p className="text-blue-900/90 text-[11px] leading-relaxed">
                    La Etapa 1 consolida tus planillas crudas en <code className="bg-blue-100 px-1 py-0.5 rounded text-blue-900">BASE_INTEGRADA.xlsx</code> y organiza la carpeta <code className="bg-blue-100 px-1 py-0.5 rounded text-blue-900">-REV</code>. Subir una copia a Google Drive te garantiza tener un respaldo seguro en la nube ante cualquier falla local.
                  </p>
                </div>
              </div>
            </div>

            {error && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-xl text-xs text-red-700 flex items-center gap-2">
                <AlertCircle className="w-4 h-4 text-red-500 shrink-0" />
                <span>{error}</span>
              </div>
            )}

            <button
              onClick={handleCreateBackup}
              disabled={loading || !subjectName}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3.5 px-4 rounded-2xl transition shadow-sm flex items-center justify-center gap-2 cursor-pointer text-sm"
            >
              <CloudUpload className="w-4 h-4" />
              Generar y Respaldar en Google Drive
            </button>
          </div>
        )}

        {/* Estado de carga */}
        {loading && (
          <div className="py-8 text-center space-y-3">
            <div className="w-10 h-10 border-3 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
            <p className="text-sm font-bold text-slate-800 font-editorial">
              Empaquetando carpetas y preparando respaldo...
            </p>
            <p className="text-xs text-slate-500">
              Comprimiendo archivos originales y estructura REV para {subjectName}
            </p>
          </div>
        )}

        {/* Resultado Exitoso */}
        {result && (
          <div className="space-y-4 animate-in fade-in">
            <div className="bg-emerald-50 border border-emerald-200 rounded-2xl p-4 text-xs text-emerald-950">
              <div className="flex items-start gap-2.5">
                <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0 mt-0.5" />
                <div>
                  <h4 className="font-bold text-emerald-900 mb-1">
                    {result.mode === 'api' 
                      ? '¡Respaldo subido a Google Drive exitosamente!' 
                      : '¡Paquete de respaldo generado con éxito!'}
                  </h4>
                  <p className="text-emerald-800 text-[11px] leading-relaxed">
                    {result.message}
                  </p>
                </div>
              </div>
            </div>

            {/* Ficha técnica del archivo */}
            <div className="bg-[#FAF8F5] border border-[#E8E3DA] p-3.5 rounded-2xl space-y-2 text-xs">
              <div className="flex items-center justify-between">
                <span className="text-slate-500 flex items-center gap-1.5">
                  <FolderArchive className="w-3.5 h-3.5 text-slate-400" /> Archivo generado:
                </span>
                <span className="font-mono font-bold text-slate-800">{result.zip_filename}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-500">Tamaño y archivos:</span>
                <span className="font-semibold text-slate-700">{result.zip_size_mb} MB ({result.archived_files_count} archivos)</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-500">Modalidad:</span>
                <span className="font-semibold text-blue-700 uppercase text-[10px]">
                  {result.mode === 'api' ? '⚡ API Directa OAuth' : '📂 Modo Asistido / Soberano'}
                </span>
              </div>
            </div>

            {/* Botones de acción */}
            <div className="flex flex-col sm:flex-row gap-2.5 pt-2">
              {result.drive_link && result.mode === 'api' && (
                <a
                  href={result.drive_link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-bold py-2.5 px-3 rounded-xl transition text-xs flex items-center justify-center gap-1.5 text-center shadow-xs"
                >
                  <ExternalLink className="w-3.5 h-3.5" />
                  Abrir en Google Drive ↗
                </a>
              )}
              {result.download_url && (
                <a
                  href={result.download_url}
                  download
                  className="flex-1 bg-slate-900 hover:bg-slate-800 text-amber-300 font-bold py-2.5 px-3 rounded-xl transition text-xs flex items-center justify-center gap-1.5 text-center shadow-xs"
                >
                  <Download className="w-3.5 h-3.5 text-amber-400" />
                  Descargar Copia (.zip)
                </a>
              )}
              {result.mode === 'assisted' && (
                <a
                  href="https://drive.google.com"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex-1 bg-blue-50 hover:bg-blue-100 text-blue-800 border border-blue-200 font-bold py-2.5 px-3 rounded-xl transition text-xs flex items-center justify-center gap-1.5 text-center"
                >
                  <ExternalLink className="w-3.5 h-3.5 text-blue-600" />
                  Abrir Google Drive ↗
                </a>
              )}
            </div>
          </div>
        )}

        {/* Pie de modal */}
        <div className="mt-5 pt-3 border-t border-[#E8E3DA] flex items-center justify-between text-[10px] text-slate-400">
          <span>Soberanía y custodia de datos garantizada</span>
          <button 
            onClick={onClose}
            className="text-slate-500 hover:text-slate-800 font-semibold cursor-pointer"
          >
            Cerrar
          </button>
        </div>
      </div>
    </div>
  );
}
