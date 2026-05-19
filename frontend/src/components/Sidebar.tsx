type Page = 'rename' | 'extract_excel' | 'extract_word';

interface SidebarProps {
  current: Page;
  onNavigate: (page: Page) => void;
}

const icons: Record<Page, string> = {
  rename: '/assets/Renombre.jpeg',
  extract_excel: '/assets/DocToSheet.jpeg',
  extract_word: '/assets/DocToText.jpeg',
};

export default function Sidebar({ current, onNavigate }: SidebarProps) {

  const pages: { id: Page; label: string }[] = [
    { id: 'rename', label: 'Renombrar' },
    { id: 'extract_excel', label: 'Extraer Excel' },
    { id: 'extract_word', label: 'Extraer Word' },
  ];

  return (
    <nav className="w-[76px] bg-sidebar flex flex-col items-center py-4 border-r border-border shrink-0">
      <div className="flex flex-col gap-3 w-full px-2">
        {pages.map((p) => {
          const isActive = current === p.id;
          return (
            <button
              key={p.id}
              onClick={() => onNavigate(p.id)}
              className={[
                'relative flex flex-col items-center justify-center rounded-lg py-2.5 px-1 transition-all duration-150',
                'hover:bg-white/5',
                isActive ? 'text-text-primary' : 'text-text-secondary',
              ].join(' ')}
              title={p.label}
            >
              {isActive && (
                <span className="absolute left-0 top-1/2 -translate-y-1/2 w-[3px] h-6 bg-primary rounded-r-full" />
              )}
              <div 
                className={[
                  "w-11 h-11 rounded-lg overflow-hidden border flex items-center justify-center bg-black/20 transition-all",
                  isActive ? "border-primary/50 ring-1 ring-primary/30 scale-105" : "border-white/10 hover:border-white/20"
                ].join(' ')}
              >
                <img 
                  src={icons[p.id]} 
                  alt={p.label} 
                  className={[
                    'w-full h-full object-cover transition-all duration-150',
                    isActive ? 'opacity-100 saturate-100' : 'opacity-60 saturate-75 hover:opacity-85'
                  ].join(' ')} 
                />
              </div>
              <span className="text-[9px] mt-1.5 leading-none text-center font-medium truncate max-w-full">{p.label}</span>
            </button>
          );
        })}
      </div>
    </nav>
  );
}

