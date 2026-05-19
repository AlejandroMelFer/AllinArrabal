interface ModalProps {
  open: boolean;
  title?: string;
  message: string;
  type?: 'info' | 'warning' | 'error' | 'success';
  onClose: () => void;
}

const icons: Record<string, string> = {
  info: 'text-primary',
  warning: 'text-yellow-400',
  error: 'text-danger',
  success: 'text-success',
};

export default function Modal({ open, title, message, type = 'info', onClose }: ModalProps) {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} />
      <div className="relative bg-surface border border-border rounded-xl p-6 w-full max-w-sm mx-4 shadow-xl">
        <div className="flex items-center gap-3 mb-3">
          <div className={`w-8 h-8 rounded-full bg-bg border border-border flex items-center justify-center ${icons[type]}`}>
            {type === 'error' ? '!' : type === 'success' ? '✓' : type === 'warning' ? '⚠' : 'ℹ'}
          </div>
          <h3 className="text-sm font-semibold text-text-primary">{title || 'Notificación'}</h3>
        </div>
        <p className="text-sm text-text-secondary whitespace-pre-wrap">{message}</p>
        <div className="mt-5 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-primary hover:bg-primary-hover text-white text-sm font-medium rounded-lg transition-colors"
          >
            Aceptar
          </button>
        </div>
      </div>
    </div>
  );
}
