import { useState } from 'react';

interface LoginProps {
  onLoginSuccess: (email: string, role: 'company' | 'guest') => void;
  api: any;
}

export function Login({ onLoginSuccess, api }: LoginProps) {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) return;

    setLoading(true);
    setError(null);

    const emailTrimmed = email.trim();
    if (!emailTrimmed.toLowerCase().endsWith('@arrabalempleo.org')) {
      setError('El correo introducido no tiene acceso corporativo o no es válido. Si no dispones de uno, pulsa "Acceder como invitado" abajo.');
      setLoading(false);
      return;
    }

    try {
      const res = await api?.authenticate_user?.(emailTrimmed);
      if (res && res.success) {
        onLoginSuccess(res.email, res.role);
      } else {
        setError(res?.error || 'Error al validar el correo.');
      }
    } catch (err: any) {
      setError(err?.message || 'Error de conexión con el servidor.');
    } finally {
      setLoading(false);
    }
  };

  const handleGuestAccess = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api?.set_guest_session?.();
      if (res && res.success) {
        onLoginSuccess('guest', 'guest');
      } else {
        setError(res?.error || 'Error al iniciar sesión como invitado.');
      }
    } catch (err: any) {
      setError(err?.message || 'Error al iniciar sesión como invitado.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md px-4">
      <div className="bg-surface border border-border/80 shadow-2xl rounded-2xl p-8 max-w-sm w-full relative overflow-hidden animate-pulse-slow">
        {/* Glowing gradients behind content */}
        <div className="absolute -top-16 -left-16 w-32 h-32 bg-primary/10 rounded-full blur-3xl pointer-events-none"></div>
        <div className="absolute -bottom-16 -right-16 w-32 h-32 bg-success/10 rounded-full blur-3xl pointer-events-none"></div>

        <div className="flex flex-col items-center gap-3.5 mb-6 text-center">
          <div className="w-14 h-14 rounded-2xl bg-black/40 border border-white/10 flex items-center justify-center shadow-inner">
            <img src="/assets/ODF.png" alt="AllinArrabal" className="w-8 h-8 object-contain" />
          </div>
          <div>
            <h2 className="text-xl font-bold tracking-tight text-text-primary">Iniciar Sesión</h2>
            <p className="text-xs text-text-secondary mt-1 max-w-[280px]">
              Introduce tu correo corporativo de Arrabal Empleo o accede de forma gratuita como invitado.
            </p>
          </div>
        </div>

        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label className="block text-[10px] font-bold text-text-secondary mb-1.5 uppercase tracking-wider">
              Correo Electrónico
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              disabled={loading}
              className="w-full bg-black/40 border border-border hover:border-primary/40 focus:border-primary focus:ring-1 focus:ring-primary rounded-xl px-4 py-3 text-sm text-text-primary outline-none transition-all placeholder:text-text-secondary/35"
            />
          </div>

          {error && (
            <div className="text-xs text-danger bg-danger/10 border border-danger/25 rounded-xl p-3 leading-relaxed">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-primary hover:bg-primary-hover disabled:bg-primary/50 text-white rounded-xl py-3 font-semibold text-sm transition-all shadow-lg shadow-primary/15 cursor-pointer flex justify-center items-center gap-2"
          >
            {loading ? 'Accediendo...' : 'Acceder con correo'}
          </button>
        </form>

        <div className="relative flex py-5 items-center justify-center">
          <div className="flex-grow border-t border-border"></div>
          <span className="flex-shrink mx-3 text-text-secondary text-[10px] uppercase tracking-wider font-bold">O también</span>
          <div className="flex-grow border-t border-border"></div>
        </div>

        <button
          onClick={handleGuestAccess}
          disabled={loading}
          className="w-full bg-white/[0.02] hover:bg-white/[0.06] border border-border hover:border-white/10 text-text-primary hover:text-white rounded-xl py-3 font-semibold text-sm transition-all cursor-pointer shadow-sm"
        >
          Acceder como invitado
        </button>
      </div>
    </div>
  );
}
