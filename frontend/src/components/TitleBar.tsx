import { usePyWebView } from '../hooks/usePyWebView';
import { useState, useEffect, useCallback, useRef } from 'react';

interface TitleBarProps {
  isLoggedIn: boolean;
  userEmail: string | null;
  authType: 'company' | 'guest' | null;
  onLogout: () => void;
  onLoginClick: () => void;
}

export default function TitleBar({ isLoggedIn, userEmail, authType, onLogout, onLoginClick }: TitleBarProps) {
  const { api } = usePyWebView();
  const [isMaximized, setIsMaximized] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown on outside click
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setMenuOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

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
        {/* User indicator status pill */}
        <div className="relative mr-2" ref={dropdownRef}>
          <button
            onClick={() => {
              if (isLoggedIn) {
                setMenuOpen(!menuOpen);
              } else {
                onLoginClick();
              }
            }}
            title={isLoggedIn ? 'Ver detalles de usuario' : 'Iniciar Sesión'}
            className="flex items-center gap-2 px-2.5 py-1 rounded-full border border-border hover:border-white/10 bg-black/25 hover:bg-white/5 transition-all text-[11px] font-medium cursor-pointer"
          >
            <span className={`w-2 h-2 rounded-full ${isLoggedIn ? 'bg-success' : 'bg-danger'} shadow-sm`} />
            <span className="text-text-secondary select-none">
              {isLoggedIn ? (authType === 'company' ? 'Empresa' : 'Invitado') : 'Desconectado'}
            </span>
          </button>

          {/* User details dropdown */}
          {isLoggedIn && menuOpen && (
            <div className="absolute right-0 mt-2 w-56 bg-surface border border-border shadow-2xl rounded-xl p-3.5 z-50 flex flex-col gap-3 animate-pulse-slow">
              <div className="flex flex-col gap-1 border-b border-border pb-2.5">
                <span className="text-[9px] text-text-secondary uppercase tracking-wider font-bold">Usuario activo</span>
                <span className="text-xs font-semibold text-text-primary truncate animate-pulse" title={userEmail || ''}>
                  {authType === 'company' ? userEmail : 'Sesión de Invitado'}
                </span>
                <span className="text-[10px] text-text-secondary mt-1 flex items-center gap-1.5 font-medium">
                  <span className="w-1.5 h-1.5 rounded-full bg-success" />
                  {authType === 'company' ? 'IA de Pago' : 'IA Gratuita'}
                </span>
              </div>
              <button
                onClick={() => {
                  setMenuOpen(false);
                  onLogout();
                }}
                className="w-full bg-danger/10 hover:bg-danger/20 text-danger border border-danger/25 hover:border-danger/40 rounded-lg py-1.5 text-xs font-bold transition-all cursor-pointer text-center"
              >
                Cerrar sesión
              </button>
            </div>
          )}
        </div>

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
