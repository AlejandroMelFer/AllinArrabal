import { useState, useEffect, useRef } from 'react';

export function usePyWebView() {
  const [ready, setReady] = useState(false);
  const apiRef = useRef<any>(null);

  useEffect(() => {
    let interval: any;
    const check = () => {
      if ((window as any).pywebview && (window as any).pywebview.api) {
        apiRef.current = (window as any).pywebview.api;
        setReady(true);
        clearInterval(interval);
      }
    };
    interval = setInterval(check, 100);
    check();
    return () => clearInterval(interval);
  }, []);

  return { ready, api: apiRef.current };
}

export function useStrings() {
  const { ready, api } = usePyWebView();
  const [strings, setStrings] = useState<Record<string, string>>({});

  useEffect(() => {
    if (ready && api) {
      api.get_strings().then((s: Record<string, string>) => setStrings(s));
    }
  }, [ready, api]);

  return strings;
}
