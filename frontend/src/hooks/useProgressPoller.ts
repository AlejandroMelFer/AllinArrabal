import { useEffect, useRef } from 'react';

export function useProgressPoller(
  api: any,
  onEvents: (events: any[]) => void,
  active: boolean,
  intervalMs = 500
) {
  const activeRef = useRef(active);
  activeRef.current = active;

  useEffect(() => {
    if (!api || !active) return;
    const timer = setInterval(async () => {
      if (!activeRef.current) return;
      try {
        const events = await api.get_progress_events();
        if (events && events.length > 0) {
          onEvents(events);
        }
      } catch {
        // silently ignore
      }
    }, intervalMs);
    return () => clearInterval(timer);
  }, [api, active, intervalMs, onEvents]);
}
