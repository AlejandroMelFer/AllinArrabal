interface FileStatusBadgeProps {
  status?: 'idle' | 'processing' | 'done' | 'error';
  label?: string;
}

export default function FileStatusBadge({ status = 'idle', label }: FileStatusBadgeProps) {
  const map: Record<string, { cls: string; dot: string }> = {
    idle: { cls: 'bg-border/60 text-text-secondary border border-border/20', dot: 'bg-text-secondary' },
    processing: { cls: 'bg-amber-500/15 text-amber-500 border border-amber-500/30 font-semibold', dot: 'bg-amber-500 animate-pulse' },
    done: { cls: 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 font-semibold', dot: 'bg-emerald-400' },
    error: { cls: 'bg-danger/15 text-danger border border-danger/30 font-semibold', dot: 'bg-danger' },
  };
  const s = map[status] || map.idle;
  return (
    <span className={`inline-flex items-center gap-1.5 px-2 py-1 rounded text-[11px] font-medium transition-all ${s.cls}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${s.dot}`} />
      {label || status}
    </span>
  );
}
