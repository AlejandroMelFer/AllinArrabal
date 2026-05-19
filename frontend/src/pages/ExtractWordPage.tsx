import { useState, useCallback, useEffect } from 'react';
import { usePyWebView } from '../hooks/usePyWebView';
import { useProgressPoller } from '../hooks/useProgressPoller';
import DropZone from '../components/DropZone';
import FileStatusBadge from '../components/FileStatusBadge';
import Modal from '../components/Modal';
import ErrorDetailModal from '../components/ErrorDetailModal';

export default function ExtractWordPage() {
  const { api } = usePyWebView();
  const [templatePath, setTemplatePath] = useState('');
  const [placeholders, setPlaceholders] = useState<string[]>([]);
  const [placeholdersMap, setPlaceholdersMap] = useState<Record<string, any>>({});
  const [regexPlaceholders, setRegexPlaceholders] = useState<string[]>([]);
  const [files, setFiles] = useState<string[]>([]);
  const [processing, setProcessing] = useState(false);
  const [statusMap, setStatusMap] = useState<Record<string, { status: string; isError: boolean }>>({});
  const [extractedRows, setExtractedRows] = useState<any[]>([]);
  const [modal, setModal] = useState<{ open: boolean; title: string; message: string; type: 'info'|'warning'|'error'|'success' }>({ open: false, title: '', message: '', type: 'info' });
  const [errorModal, setErrorModal] = useState<{ open: boolean; filename: string; errorText: string }>({ open: false, filename: '', errorText: '' });
  const [docxDragOver, setDocxDragOver] = useState(false);

  const handleDocxLoaded = useCallback(async (path: string) => {
    if (!path || !api) return;
    setTemplatePath(path);
    try {
      const data = await api.get_placeholders_from_template(path);
      setPlaceholders(data.placeholders || []);
      setPlaceholdersMap(data.placeholders_map || {});
      setRegexPlaceholders(data.regex_placeholders || []);
      setExtractedRows([]);
    } catch (err) {
      console.error("Error loading DOCX placeholders:", err);
    }
  }, [api]);

  const loadTemplate = async () => {
    if (!api) return;
    try {
      const path: string = await api.pick_docx_template();
      if (path) {
        handleDocxLoaded(path);
      }
    } catch (err) {
      console.error("Error picking DOCX template:", err);
    }
  };

  useEffect(() => {
    const handlePyWebViewDrop = (e: Event) => {
      if (processing) return;
      const paths = (e as CustomEvent).detail as string[];
      if (paths && paths.length > 0) {
        // Encontrar si hay un archivo .docx en los archivos arrastrados
        const docxFile = paths.find(p => p.toLowerCase().endsWith('.docx'));
        if (docxFile) {
          handleDocxLoaded(docxFile);
        }
      }
    };
    window.addEventListener('pywebviewfilesdropped', handlePyWebViewDrop);
    return () => {
      window.removeEventListener('pywebviewfilesdropped', handlePyWebViewDrop);
    };
  }, [processing, handleDocxLoaded]);

  const removePlaceholder = (name: string) => {
    const next = placeholders.filter((p) => p !== name);
    setPlaceholders(next);
    const nextMap = { ...placeholdersMap };
    delete nextMap[name];
    setPlaceholdersMap(nextMap);
    const nextRegex = regexPlaceholders.filter((p) => p !== name);
    setRegexPlaceholders(nextRegex);
  };

  const clearAll = () => {
    setTemplatePath('');
    setPlaceholders([]);
    setPlaceholdersMap({});
    setRegexPlaceholders([]);
    setFiles([]);
    setStatusMap({});
    setExtractedRows([]);
  };

  const handleEvents = useCallback((events: any[]) => {
    const nextMap = { ...statusMap };
    let done = false;
    for (const ev of events) {
      if (ev.type === 'status') {
        nextMap[ev.file] = { status: ev.status, isError: ev.is_error };
      } else if (ev.type === 'extract_done') {
        done = true;
      }
    }
    setStatusMap(nextMap);
    if (done) {
      setProcessing(false);
      api.get_extracted_rows().then((rows: any[]) => {
        setExtractedRows(rows);
        api.get_strings().then((s: any) => {
          setModal({ open: true, title: s.info_extract_done_title || 'Extracción completada', message: s.info_extract_done_msg?.replace('{count}', String(rows.length)) || `Se extrajeron ${rows.length} registros.`, type: 'success' });
        });
      });
    }
  }, [statusMap, api]);

  useProgressPoller(api, handleEvents, processing);

  const start = async () => {
    if (files.length === 0) {
      setModal({ open: true, title: 'Sin archivos', message: 'Por favor, añade archivos primero.', type: 'warning' });
      return;
    }
    if (!templatePath) {
      setModal({ open: true, title: 'Sin plantilla', message: 'Carga una plantilla Word primero.', type: 'warning' });
      return;
    }

    // Identificar qué archivos ya fueron procesados de forma exitosa para reanudar
    const completedRows: any[] = [];
    const completedFiles = new Set<string>();
    for (const f of files) {
      const st = statusMap[f];
      if (st && !st.isError && st.status !== 'START') {
        completedFiles.add(f);
        const row = extractedRows.find((r) => r._file_path === f);
        if (row) {
          completedRows.push(row);
        }
      }
    }

    setProcessing(true);

    // Conservar estados exitosos en statusMap y borrar fallidos/pendientes
    const nextMap = { ...statusMap };
    for (const f of files) {
      if (!completedFiles.has(f)) {
        delete nextMap[f];
      }
    }
    setStatusMap(nextMap);

    if (completedRows.length === 0) {
      setExtractedRows([]);
    } else {
      setExtractedRows(completedRows);
    }

    await api.start_extract_word(files, placeholders, completedRows);
  };

  const saveWord = async () => {
    const res = await api.save_word_zip(extractedRows, templatePath, placeholdersMap, regexPlaceholders);
    if (res.success) {
      setModal({ open: true, title: 'Documentos creados', message: `Se generaron ${res.count} documentos.\nGuardado en: ${res.path}`, type: 'success' });
    } else {
      setModal({ open: true, title: 'Error', message: res.error || 'Error desconocido al guardar.', type: 'error' });
    }
  };

  return (
    <div className="flex flex-col h-full p-6 gap-4 overflow-y-auto">
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg overflow-hidden border border-white/10 flex items-center justify-center bg-black/20 shrink-0">
          <img src="/assets/DocToText.jpeg" alt="Extraer Word" className="w-full h-full object-cover" />
        </div>
        <h2 className="text-lg font-semibold text-text-primary">Extracción a Word</h2>
      </div>

      <div className="grid grid-cols-2 gap-4 flex-1 min-h-0">
        {/* Left column: template */}
        <div className="bg-surface border border-border rounded-xl p-4 flex flex-col gap-3 min-h-0">
          <span className="text-sm font-medium text-text-secondary">Plantilla Word</span>
          {!templatePath ? (
            <button
              onClick={loadTemplate}
              onDragOver={(e) => { e.preventDefault(); setDocxDragOver(true); }}
              onDragLeave={() => setDocxDragOver(false)}
              onDrop={(e) => { e.preventDefault(); setDocxDragOver(false); }}
              className={`flex-1 border-2 border-dashed rounded-xl flex flex-col items-center justify-center gap-3 transition-all ${
                docxDragOver
                  ? 'border-primary bg-primary/10 scale-[1.01] shadow-[0_0_15px_rgba(var(--primary-rgb),0.15)]'
                  : 'border-border hover:border-primary hover:bg-primary/5'
              }`}
            >
              <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className={docxDragOver ? 'text-primary animate-bounce' : 'text-text-secondary'}>
                <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/>
                <polyline points="14 2 14 8 20 8"/>
                <path d="M16 13H8M16 17H8"/>
              </svg>
              <p className={`text-sm ${docxDragOver ? 'text-primary font-semibold animate-pulse' : 'text-text-secondary'}`}>
                {docxDragOver ? '¡Suelta la plantilla aquí!' : 'Haz clic o arrastra una plantilla .docx'}
              </p>
            </button>
          ) : (
            <div className="flex-1 flex flex-col gap-3 min-h-0">
              <div className="flex items-center gap-2 text-success">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <polyline points="20 6 9 17 4 12"/>
                </svg>
                <span className="text-sm font-medium truncate">{templatePath.split('\\').pop()}</span>
              </div>
              <div className="flex-1 min-h-0">
                <span className="text-xs text-text-secondary mb-1.5 block">Campos detectados:</span>
                {placeholders.length === 0 ? (
                  <p className="text-xs text-text-secondary italic">No se encontraron campos con formato {'{{campo}}'}</p>
                ) : (
                  <div className="flex flex-wrap gap-2 max-h-[180px] overflow-y-auto pr-1 border border-border/40 rounded-lg p-2 bg-bg/40 custom-scrollbar">
                    {placeholders.map((ph) => (
                      <div key={ph} className="flex items-center gap-1.5 bg-bg border border-border rounded px-2 py-1">
                        <span className="text-xs text-text-primary">{ph}</span>
                        <button
                          onClick={() => removePlaceholder(ph)}
                          disabled={processing}
                          className="text-danger hover:bg-danger/10 rounded w-4 h-4 flex items-center justify-center text-[10px] transition-colors disabled:opacity-30 cursor-pointer"
                        >
                          ×
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>
              <button
                onClick={() => { setTemplatePath(''); setPlaceholders([]); setPlaceholdersMap({}); setRegexPlaceholders([]); }}
                disabled={processing}
                className="self-start text-xs text-danger hover:underline underline-offset-2 cursor-pointer"
              >
                Quitar plantilla
              </button>
            </div>
          )}
        </div>

        {/* Right column: PDFs */}
        <div className="bg-surface border border-border rounded-xl p-4 flex flex-col gap-3 min-h-0">
          <span className="text-sm font-medium text-text-secondary">Archivos PDF</span>
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
                      else { badgeStatus = 'done'; label = 'Extraído'; }
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
      </div>

      <div className="flex items-center gap-3 pt-2">
        <button
          onClick={start}
          disabled={processing || files.length === 0 || !templatePath}
          className="flex-1 bg-primary hover:bg-primary-hover text-white text-sm font-semibold py-2.5 rounded-lg transition-colors disabled:opacity-40 flex items-center justify-center gap-2 cursor-pointer"
        >
          {processing && <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />}
          {processing ? 'Extrayendo...' : 'Comenzar Extracción'}
        </button>
        <button
          onClick={saveWord}
          disabled={processing || extractedRows.length === 0 || !templatePath}
          className="px-5 py-2.5 bg-primary hover:bg-primary-hover text-white text-sm font-semibold rounded-lg transition-colors disabled:opacity-40 shadow-[0_0_10px_rgba(99,102,241,0.15)] cursor-pointer"
        >
          Crear Word
        </button>
        <button
          onClick={clearAll}
          disabled={processing}
          className="px-5 py-2.5 bg-surface border border-border hover:bg-white/5 text-text-secondary text-sm font-medium rounded-lg transition-colors disabled:opacity-40 cursor-pointer"
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
