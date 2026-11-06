"use client";

import * as React from "react";

import { getHealth } from "@/lib/api";
import type { HealthResponse } from "@/lib/types";

interface HealthState {
  health: HealthResponse | null;
  loading: boolean;
  /** True when the backend could not be reached at all. */
  offline: boolean;
  refresh: () => Promise<void>;
}

const HealthContext = React.createContext<HealthState | null>(null);

/** Fetches backend health once and shares it with the header and the brief form. */
export function HealthProvider({ children }: { children: React.ReactNode }) {
  const [health, setHealth] = React.useState<HealthResponse | null>(null);
  const [loading, setLoading] = React.useState(true);
  const [offline, setOffline] = React.useState(false);

  const refresh = React.useCallback(async () => {
    setLoading(true);
    try {
      setHealth(await getHealth());
      setOffline(false);
    } catch {
      setHealth(null);
      setOffline(true);
    } finally {
      setLoading(false);
    }
  }, []);

  React.useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect -- initial fetch on mount
    void refresh();
  }, [refresh]);

  const value = React.useMemo(
    () => ({ health, loading, offline, refresh }),
    [health, loading, offline, refresh],
  );
  return <HealthContext.Provider value={value}>{children}</HealthContext.Provider>;
}

export function useHealth(): HealthState {
  const context = React.useContext(HealthContext);
  if (!context) throw new Error("useHealth must be used inside <HealthProvider>");
  return context;
}
