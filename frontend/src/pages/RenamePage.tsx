import { useState, useCallback } from 'react';
import { usePyWebView } from '../hooks/usePyWebView';
import { useProgressPoller } from '../hooks/useProgressPoller';
import DropZone from '../components/DropZone';
import ParamRow from '../components/ParamRow';
import FileStatusBadge from '../components/FileStatusBadge';
import Modal from '../components/Modal';
import ErrorDetailModal from '../components/ErrorDetailModal';

export default function RenamePage() {
  const { api } = usePyWebView();
  const [prefix, setPrefix] = useState('');
  const [params, setParams] = useState<string[]>(['Apellido 1', 'Apellido 2', 'Nombre']);
  const [files, setFiles] = useState<string[]>([]);
  const [processing, setProcessing] = useState(false);
  const [statusMap, setStatusMap] = useState<Record<string, { status: string; isError: boolean }>>({});
  const [modal, setModal] = useState<{ open: boolean; title: string; message: string; type: 'info'|'warning'|'error' }>({ open: false, title: '', message: '', type: 'info' });
  const [errorModal, setErrorModal] = useState<{ open: boolean; filename: string; errorText: string }>({ open: false, filename: '', errorText: '' });

  const addParam = () => {
    if (params.length >= 5) {
      setModal({ open: true, title: 'Límite alcanzado', message: 'No se permiten más de 5 parámetros.', type: 'warning' });
      return;
    }
    setParams([...params, '']);
  };

  const removeParam = (idx: number) => {
    setParams(params.filter((_, i) => i !== idx));
  };

  const updateParam = (idx: number, val: string) => {
    const next = [...params];
    next[idx] = val;
    setParams(next);
  };

  const clearList = () => {
    setFiles([]);
    setStatusMap({});
  };

  const handleEvents = useCallback((events: any[]) => {
    const nextMap = { ...statusMap };
    let done = false;
    for (const ev of events) {
      if (ev.type === 'status') {
        nextMap[ev.file] = { status: ev.status, isError: ev.is_error };
      } else if (ev.type === 'rename_done') {
        done = true;
      }
    }
    setStatusMap(nextMap);
    if (done) {
      setProcessing(false);
    }
  }, [statusMap]);

  useProgressPoller(api, handleEvents, processing);

  const start = async () => {
    if (files.length === 0) {
      setModal({ open: true, title: 'Sin archivos', message: 'Por favor, selecciona al menos un archivo.', type: 'warning' });
      return;
    }
    const cleanParams = params.map((p) => p.trim()).filter((p) => p.length > 0);

    // Identificar archivos que ya fueron procesados con éxito
    const completedMap: Record<string, string> = {};
    for (const f of files) {
      const st = statusMap[f];
      if (st && !st.isError && st.status !== 'START') {
        completedMap[f] = st.status; // st.status es la nueva ruta
      }
    }

    setProcessing(true);

    // Si estamos reanudando, conservamos el historial de éxitos y limpiamos errores/esperas
    const nextMap = { ...statusMap };
    for (const f of files) {
      if (!completedMap[f]) {
        delete nextMap[f];
      }
    }
    setStatusMap(nextMap);

    await api.start_rename(files, prefix, cleanParams, completedMap);
  };

  return (
    <div className="flex flex-col h-full p-6 gap-4 overflow-y-auto">
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg overflow-hidden border border-white/10 flex items-center justify-center bg-black/20 shrink-0">
          <img src="/assets/Renombre.jpeg" alt="Renombrar" className="w-full h-full object-cover" />
        </div>
        <h2 className="text-lg font-semibold text-text-primary">Renombrado</h2>
      </div>

      <div className="bg-surface border border-border rounded-xl p-4 space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium text-text-secondary">Parámetros de extracción</span>
          <button
            onClick={addParam}
            disabled={processing || params.length >= 5}
            className="text-xs bg-primary hover:bg-primary-hover text-white px-3 py-1.5 rounded-md transition-colors disabled:opacity-40"
          >
            + Añadir
          </button>
        </div>
        <div className="space-y-2 max-h-40 overflow-y-auto px-1 py-0.5">
          {params.map((p, i) => (
            <ParamRow
              key={i}
              value={p}
              onChange={(v) => updateParam(i, v)}
              onRemove={() => removeParam(i)}
              disabled={processing}
              placeholder={`Parámetro ${i + 1}`}
            />
          ))}
        </div>
      </div>

      <div className="bg-surface border border-border rounded-xl p-4">
        <label className="block text-sm font-medium text-text-secondary mb-1">Prefijo</label>
        <input
          type="text"
          value={prefix}
          onChange={(e) => setPrefix(e.target.value)}
          disabled={processing}
          placeholder="Ej: VTV2026.3"
          className="w-full bg-bg border border-border rounded px-3 py-2 text-sm text-text-primary placeholder:text-text-secondary/50 focus:outline-none focus:ring-1 focus:ring-primary transition-all"
        />
      </div>

      <div className="bg-surface border border-border rounded-xl p-4 flex-1 min-h-0 flex flex-col">
        <span className="text-sm font-medium text-text-secondary mb-2">Archivos PDF</span>
        <div className="flex-1 min-h-0">
          <DropZone files={files} onFilesChange={setFiles} disabled={processing} label="Arrastra archivos PDF aquí">
            {files.length > 0 && (
              <div className="space-y-1 px-1 py-0.5">
                {files.map((f) => {
                  const st = statusMap[f];
                  let badgeStatus: 'idle' | 'processing' | 'done' | 'error' = 'idle';
                  let label = 'Esperando';
                  if (st) {
                    if (st.isError) { badgeStatus = 'error'; label = 'Error'; }
                    else if (st.status === 'START') { badgeStatus = 'processing'; label = 'Procesando...'; }
                    else { badgeStatus = 'done'; label = 'Renombrado'; }
                  }

                  let rowClass = "flex flex-col justify-center rounded px-3 py-2 border transition-all duration-300 gap-1 ";
                  if (badgeStatus === 'idle') {
                    rowClass += "bg-surface/30 border-border/60 text-text-secondary opacity-75";
                  } else if (badgeStatus === 'processing') {
                    rowClass += "bg-amber-500/5 border-amber-500/80 text-amber-500 shadow-[0_0_8px_rgba(245,158,11,0.06)] animate-pulse-slow";
                  } else if (badgeStatus === 'done') {
                    rowClass += "bg-emerald-500/5 border-emerald-500/80 text-emerald-400 shadow-[0_0_8px_rgba(16,185,129,0.06)]";
                  } else if (badgeStatus === 'error') {
                    rowClass += "bg-danger/5 border-danger/80 text-danger shadow-[0_0_8px_rgba(239,68,68,0.06)]";
                  }

                  return (
                    <div key={f} className={rowClass}>
                      <div className="flex items-center justify-between w-full gap-2">
                        <span className="text-xs font-mono truncate max-w-[280px]">{f.split('\\').pop()}</span>
                        <div className="flex items-center gap-2">
                          {badgeStatus === 'error' && (
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                setErrorModal({ open: true, filename: f, errorText: st.status });
                              }}
                              className="text-[10px] text-danger hover:underline hover:text-danger/80 transition-colors font-medium cursor-pointer"
                            >
                              Ver motivo
                            </button>
                          )}
                          <FileStatusBadge status={badgeStatus} label={label} />
                        </div>
                      </div>
                      {badgeStatus === 'error' && st?.status && (
                        <div className="text-[10px] text-danger/80 font-mono mt-0.5 truncate pl-1 opacity-70">
                          {st.status}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </DropZone>
        </div>
      </div>

      <div className="flex items-center gap-3 pt-2">
        <button
          onClick={start}
          disabled={processing || files.length === 0}
          className="flex-1 bg-primary hover:bg-primary-hover text-white text-sm font-semibold py-2.5 rounded-lg transition-colors disabled:opacity-40 flex items-center justify-center gap-2"
        >
          {processing && <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />}
          {processing ? 'Procesando...' : 'Iniciar Procesamiento'}
        </button>
        <button
          onClick={clearList}
          disabled={processing}
          className="px-5 py-2.5 bg-surface border border-border hover:bg-white/5 text-text-secondary text-sm font-medium rounded-lg transition-colors disabled:opacity-40"
        >
          Limpiar
        </button>
      </div>

      <Modal open={modal.open} title={modal.title} message={modal.message} type={modal.type} onClose={() => setModal({ ...modal, open: false })} />
      <ErrorDetailModal
        open={errorModal.open}
        filename={errorModal.filename}
        errorText={errorModal.errorText}
        onClose={() => setErrorModal({ ...errorModal, open: false })}
      />
    </div>
  );
}
