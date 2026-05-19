import { usePyWebView } from '../hooks/usePyWebView';

export default function TitleBar() {
  const { api } = usePyWebView();

  return (
    <header
      className="h-10 bg-sidebar border-b border-border flex items-center justify-between px-4 shrink-0 pywebview-drag-region"
      style={{ WebkitAppRegion: 'drag' } as any}
    >
      <div className="flex items-center gap-2 pointer-events-none select-none">
        <img src="/assets/ODF.png" alt="AllinArrabal" className="w-4.5 h-4.5 object-contain opacity-95" />
        <span className="text-sm font-semibold text-text-primary tracking-tight">AllinArrabal</span>
        <span className="text-[10px] text-text-secondary bg-surface px-1.5 py-0.5 rounded border border-border">v2</span>
      </div>
      <div className="flex items-center gap-1" style={{ WebkitAppRegion: 'no-drag' } as any}>
        <button
          onClick={() => api?.minimize_window?.()}
          className="w-8 h-8 flex items-center justify-center rounded hover:bg-white/5 text-text-secondary hover:text-text-primary transition-colors"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
            <line x1="5" y1="12" x2="19" y2="12"/>
          </svg>
        </button>
        <button
          onClick={() => api?.close_window?.()}
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
