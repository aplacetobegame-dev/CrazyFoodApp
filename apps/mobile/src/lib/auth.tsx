import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import { AppState, Platform } from "react-native";
import type { Session } from "@supabase/supabase-js";
import { getSupabase } from "@/lib/client";

type AuthContextValue = {
  ready: boolean;
  session: Session | null;
  signOut: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const supabase = getSupabase();
  const [session, setSession] = useState<Session | null>(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    let active = true;
    const { data } = supabase.auth.onAuthStateChange((_event, nextSession) => {
      setSession(nextSession);
      setReady(true);
    });

    async function load() {
      try {
        const { data: sessionData, error: sessionError } = await supabase.auth.getSession();
        if (!active) return;
        const stored = sessionError ? null : sessionData.session;
        if (!stored) {
          setSession(null);
          return;
        }
        const { data: userData, error: userError } = await supabase.auth.getUser();
        if (!active) return;
        if (userData.user) {
          setSession(stored);
          return;
        }
        const offline = userError?.message.toLowerCase().includes("fetch") || userError?.status === 0;
        if (offline) {
          setSession(stored);
          return;
        }
        await supabase.auth.signOut({ scope: "local" });
        if (active) setSession(null);
      } catch {
        if (active) setSession(null);
      } finally {
        if (active) setReady(true);
      }
    }

    void load();
    return () => {
      active = false;
      data.subscription.unsubscribe();
    };
  }, [supabase]);

  useEffect(() => {
    if (Platform.OS === "web") {
      return;
    }
    const subscription = AppState.addEventListener("change", (state) => {
      if (state === "active") {
        void supabase.auth.startAutoRefresh();
        return;
      }
      void supabase.auth.stopAutoRefresh();
    });
    return () => subscription.remove();
  }, [supabase]);

  const value = useMemo<AuthContextValue>(
    () => ({
      ready,
      session,
      signOut: async () => {
        await supabase.auth.signOut();
      },
    }),
    [ready, session, supabase],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const value = useContext(AuthContext);
  if (!value) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return value;
}
