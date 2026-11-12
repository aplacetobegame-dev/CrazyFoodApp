import { createBrowserClient } from "@supabase/ssr";
import type { SupabaseClient } from "@supabase/supabase-js";
import { publicSupabaseConfig } from "@/lib/public-config";

let supabase: SupabaseClient | undefined;

export function getSupabase() {
  if (!supabase) {
    const { url, publishableKey } = publicSupabaseConfig();
    supabase = createBrowserClient(url, publishableKey);
  }

  return supabase;
}
