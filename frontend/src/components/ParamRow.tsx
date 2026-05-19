interface ParamRowProps {
  value: string;
  onChange: (v: string) => void;
  onRemove: () => void;
  disabled?: boolean;
  placeholder?: string;
}

export default function ParamRow({ value, onChange, onRemove, disabled, placeholder }: ParamRowProps) {
  return (
    <div className="flex items-center gap-2">
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        placeholder={placeholder || 'Campo...'}
        className="flex-1 bg-surface border border-border rounded px-3 py-2 text-sm text-text-primary placeholder:text-text-secondary/50 focus:outline-none focus:ring-1 focus:ring-primary transition-all"
      />
      <button
        onClick={onRemove}
        disabled={disabled}
        className="w-8 h-8 flex items-center justify-center rounded bg-surface border border-border text-danger hover:bg-danger/10 transition-colors disabled:opacity-30"
      >
        ×
      </button>
    </div>
  );
}
