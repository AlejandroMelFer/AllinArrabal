import { usePyWebView } from '../hooks/usePyWebView';
import { useState, useEffect, useCallback } from 'react';

export default function TitleBar() {
  const { api } = usePyWebView();
  const [isMaximized, setIsMaximized] = useState(false);

  const refreshMaximizedState = useCallback(async () => {
    try {
      const result = await (api as any)?.is_maximized?.();
      if (result !== undefined) setIsMaximized(result);
    } catch {
    }
  }, [api]);

  useEffect(() => {
    refreshMaximizedState();
    const interval = setInterval(refreshMaximizedState, 500);
    return () => clearInterval(interval);
  }, [refreshMaximizedState]);

  const handleMaximize = async () => {
    await (api as any)?.toggle_maximize_window?.();
    setTimeout(refreshMaximizedState, 80);
  };

  return (
    <header
      className="h-10 bg-sidebar border-b border-border flex items-center justify-between px-4 shrink-0 pywebview-drag-region"
      style={{ WebkitAppRegion: 'drag' } as any}
      onDoubleClick={handleMaximize}
    >
      <div className="flex items-center gap-2 pointer-events-none select-none">
        <img src="/assets/ODF.png" alt="AllinArrabal" className="w-4.5 h-4.5 object-contain opacity-95" />
        <span className="text-sm font-semibold text-text-primary tracking-tight">AllinArrabal</span>
      </div>
      <div className="flex items-center gap-1" style={{ WebkitAppRegion: 'no-drag' } as any}>
        <button
          onClick={() => api?.minimize_window?.()}
          title="Minimizar"
          className="w-8 h-8 flex items-center justify-center rounded hover:bg-white/5 text-text-secondary hover:text-text-primary transition-colors"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
            <line x1="5" y1="12" x2="19" y2="12"/>
          </svg>
        </button>

        <button
          onClick={handleMaximize}
          title={isMaximized ? 'Restaurar' : 'Maximizar'}
          className="w-8 h-8 flex items-center justify-center rounded hover:bg-white/5 text-text-secondary hover:text-text-primary transition-colors"
        >
          {isMaximized ? (
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <rect x="8" y="2" width="14" height="14" rx="1"/>
              <path d="M2 8h6v14h14v-6"/>
            </svg>
          ) : (
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <rect x="3" y="3" width="18" height="18" rx="1"/>
            </svg>
          )}
        </button>

        <button
          onClick={() => api?.close_window?.()}
          title="Cerrar"
          className="w-8 h-8 flex items-center justify-center rounded hover:bg-danger/20 text-text-secondary hover:text-danger transition-colors"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
            <line x1="18" y1="6" x2="6" y2="18"/>
            <line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </button>
      </div>
    </header>
  );
}
