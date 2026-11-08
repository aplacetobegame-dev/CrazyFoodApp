import { createBrowserClient } from "@supabase/ssr";
import { publicSupabaseConfig } from "@/lib/public-config";

const { url, publishableKey } = publicSupabaseConfig();

export const supabase = createBrowserClient(url, publishableKey);
