import { useCallback, useState, useEffect } from 'react';
import { usePyWebView } from '../hooks/usePyWebView';

interface DropZoneProps {
  files: string[];
  onFilesChange: (files: string[]) => void;
  label?: string;
  disabled?: boolean;
  children?: React.ReactNode;
}

export default function DropZone({ files, onFilesChange, label, disabled, children }: DropZoneProps) {
  const [dragOver, setDragOver] = useState(false);
  const { api } = usePyWebView();

  useEffect(() => {
    const handlePyWebViewDrop = (e: Event) => {
      if (disabled) return;
      const paths = (e as CustomEvent).detail as string[];
      if (paths && paths.length > 0) {
        // Filtrar por PDF si la etiqueta indica que es para PDFs
        const lowerLabel = (label || '').toLowerCase();
        let filtered = paths;
        if (lowerLabel.includes('pdf')) {
          filtered = paths.filter(p => p.toLowerCase().endsWith('.pdf'));
        }
        if (filtered.length > 0) {
          const merged = [...new Set([...files, ...filtered])];
          onFilesChange(merged);
        }
      }
    };
    window.addEventListener('pywebviewfilesdropped', handlePyWebViewDrop);
    return () => {
      window.removeEventListener('pywebviewfilesdropped', handlePyWebViewDrop);
    };
  }, [files, onFilesChange, disabled, label]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    if (disabled) return;
    setDragOver(true);
  }, [disabled]);

  const handleDragLeave = useCallback(() => {
    if (disabled) return;
    setDragOver(false);
  }, [disabled]);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    if (disabled) return;
    setDragOver(false);
    
    const dropped = Array.from(e.dataTransfer.files)
      .map((f) => (f as any).path)
      .filter((p): p is string => !!p);
      
    if (dropped.length > 0) {
      const merged = [...new Set([...files, ...dropped])];
      onFilesChange(merged);
    }
  }, [files, onFilesChange, disabled]);

  const handlePick = async () => {
    if (disabled || !api) return;
    const picked: string[] = await api.pick_pdf_files();
    if (picked && picked.length > 0) {
      const merged = [...new Set([...files, ...picked])];
      onFilesChange(merged);
    }
  };

  return (
    <div
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      className={[
        'relative rounded-xl border-2 border-dashed transition-all duration-150 w-full h-full flex flex-col',
        files.length > 0 ? 'p-3' : 'p-6 items-center justify-center min-h-[140px]',
        dragOver ? 'border-primary bg-primary/5' : 'border-border bg-surface',
        disabled ? 'border-border bg-surface/80' : '',
      ].join(' ')}
    >
      {files.length === 0 ? (
        <>
          <div className="text-text-secondary">
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
              <polyline points="17 8 12 3 7 8"/>
              <line x1="12" y1="3" x2="12" y2="15"/>
            </svg>
          </div>
          <p className="text-sm text-text-secondary text-center mt-2">
            {label || 'Arrastra archivos aquí'}
          </p>
          <button
            onClick={handlePick}
            disabled={disabled}
            className="text-primary hover:text-primary-hover transition-colors underline underline-offset-2 text-xs mt-1 cursor-pointer disabled:opacity-40 disabled:no-underline"
          >
            o haz clic para explorar
          </button>
        </>
      ) : (
        <div className="w-full flex flex-col flex-1 min-h-0">
          <div className="flex items-center justify-between mb-2 px-1 shrink-0">
            <span className="text-xs text-text-secondary font-medium">{files.length} archivo(s) cargado(s)</span>
            <div className="flex gap-2">
              <button
                onClick={handlePick}
                disabled={disabled}
                className="text-xs text-primary hover:text-primary-hover transition-colors underline cursor-pointer disabled:opacity-30 disabled:no-underline disabled:cursor-not-allowed"
              >
                añadir más
              </button>
              <span className="text-border">|</span>
              <button
                onClick={() => onFilesChange([])}
                disabled={disabled}
                className="text-xs text-danger hover:text-danger/80 transition-colors cursor-pointer disabled:opacity-30 disabled:cursor-not-allowed"
              >
                vaciar
              </button>
            </div>
          </div>
          <div className="flex-1 min-h-0 overflow-y-auto custom-scrollbar">
            {children || (
              <div className="space-y-1 pr-1 custom-scrollbar">
                {files.map((f) => (
                  <div key={f} className="flex items-center justify-between bg-bg rounded px-3 py-2 border border-border">
                    <span className="text-xs font-mono text-text-primary truncate max-w-[280px]">{f.split('\\').pop()}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
