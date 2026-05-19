import { useState } from 'react';

interface ErrorDetailModalProps {
  open: boolean;
  filename: string;
  errorText: string;
  onClose: () => void;
}

export default function ErrorDetailModal({ open, filename, errorText, onClose }: ErrorDetailModalProps) {
  const [copied, setCopied] = useState(false);

  if (!open) return null;

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(errorText);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };

  // Analizar la causa probable en base al texto del error
  const getPossibleCause = (err: string): { cause: string; solution: string } => {
    const lower = err.toLowerCase();
    if (lower.includes('api_key') || lower.includes('apikey') || lower.includes('api key') || lower.includes('invalid api key')) {
      return {
        cause: 'API Key de Gemini inválida o no configurada.',
        solution: 'Revisa que tu archivo `.env` en la raíz del proyecto contenga una clave de API de Gemini válida en la variable `GEMINI_API_KEY`.'
      };
    }
    if (lower.includes('resourceexhausted') || lower.includes('quota') || lower.includes('rate limit') || lower.includes('429')) {
      return {
        cause: 'Límite de cuota o solicitudes excedido (Rate Limit).',
        solution: 'Estás utilizando la versión gratuita de Gemini y has superado el límite de solicitudes por minuto. Espera de 1 a 2 minutos e inténtalo de nuevo.'
      };
    }
    if (lower.includes('connection') || lower.includes('network') || lower.includes('dns') || lower.includes('socket') || lower.includes('httpconnection') || lower.includes('unreachable')) {
      return {
        cause: 'Error de conexión a Internet.',
        solution: 'Asegúrate de tener conexión activa a internet y de que tu firewall o proxy no esté bloqueando las peticiones a la API de Google Gemini (generativelanguage.googleapis.com).'
      };
    }
    if (lower.includes('permission') || lower.includes('permissionerror') || lower.includes('access denied')) {
      return {
        cause: 'Permiso denegado al acceder al archivo.',
        solution: 'Verifica si el archivo está abierto en otra aplicación (como Adobe Reader o Word) o si el usuario actual no posee permisos de lectura para el archivo.'
      };
    }
    if (lower.includes('filenotfound') || lower.includes('no such file')) {
      return {
        cause: 'Archivo no encontrado.',
        solution: 'El archivo original ya no se encuentra en la ruta especificada. Es posible que haya sido movido, renombrado o eliminado antes del procesamiento.'
      };
    }
    return {
      cause: 'Error inesperado durante el procesamiento.',
      solution: 'Revisa la descripción técnica detallada abajo para entender el motivo del fallo o contacta a soporte.'
    };
  };

  const { cause, solution } = getPossibleCause(errorText);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/75 backdrop-blur-sm transition-opacity" onClick={onClose} />
      
      <div className="relative bg-surface border border-border rounded-xl p-6 w-full max-w-2xl shadow-2xl max-h-[85vh] flex flex-col animate-in fade-in zoom-in-95 duration-200">
        
        {/* Header */}
        <div className="flex items-start justify-between border-b border-border/60 pb-3 mb-4 shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-danger/10 border border-danger/30 flex items-center justify-center text-danger">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="10"/>
                <line x1="12" y1="8" x2="12" y2="12"/>
                <line x1="12" y1="16" x2="12.01" y2="16"/>
              </svg>
            </div>
            <div>
              <h3 className="text-base font-semibold text-text-primary">Detalles del Error</h3>
              <p className="text-xs text-text-secondary font-mono truncate max-w-[420px] mt-0.5" title={filename}>
                Archivo: {filename.split('\\').pop()}
              </p>
            </div>
          </div>
          <button 
            onClick={onClose} 
            className="text-text-secondary hover:text-text-primary rounded-lg p-1.5 hover:bg-white/5 transition-all cursor-pointer"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto pr-1 space-y-4 my-2 custom-scrollbar">
          
          {/* Friendly Cause & Solution Card */}
          <div className="bg-danger/5 border border-danger/20 rounded-xl p-4 space-y-2">
            <h4 className="text-xs font-bold uppercase tracking-wider text-danger">Causa Probable</h4>
            <p className="text-sm font-medium text-text-primary">{cause}</p>
            
            <div className="h-[1px] bg-danger/10 my-2" />
            
            <h4 className="text-xs font-bold uppercase tracking-wider text-text-secondary">Solución Sugerida</h4>
            <p className="text-xs text-text-secondary leading-relaxed">{solution}</p>
          </div>

          {/* Technical Details block */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <h4 className="text-xs font-semibold text-text-secondary">Detalle Técnico (Exception String)</h4>
              <button
                onClick={handleCopy}
                className={`text-xs px-2.5 py-1 rounded border transition-all flex items-center gap-1.5 cursor-pointer ${
                  copied 
                    ? 'bg-success/15 border-success/30 text-success' 
                    : 'bg-bg border-border hover:bg-white/5 text-text-secondary hover:text-text-primary'
                }`}
              >
                {copied ? (
                  <>
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                      <polyline points="20 6 9 17 4 12"/>
                    </svg>
                    ¡Copiado!
                  </>
                ) : (
                  <>
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
                      <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
                    </svg>
                    Copiar Error
                  </>
                )}
              </button>
            </div>
            
            <div className="bg-bg border border-border rounded-lg p-3 overflow-x-auto max-h-60 select-text custom-scrollbar">
              <pre className="text-[11px] font-mono text-danger/90 leading-relaxed whitespace-pre-wrap break-all">
                {errorText}
              </pre>
            </div>
          </div>

        </div>

        {/* Footer */}
        <div className="border-t border-border/60 pt-4 mt-2 flex justify-end shrink-0">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-primary hover:bg-primary-hover text-white text-xs font-semibold rounded-lg transition-colors cursor-pointer shadow-lg shadow-primary/10"
          >
            Entendido
          </button>
        </div>

      </div>
    </div>
  );
}
