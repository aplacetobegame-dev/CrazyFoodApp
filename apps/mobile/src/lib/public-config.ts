const SECRET_MARKERS = ["service_role", "sb_secret_"];

export function publicSupabaseConfig(): { url: string; publishableKey: string } {
  const url = process.env.EXPO_PUBLIC_SUPABASE_URL;
  const publishableKey = process.env.EXPO_PUBLIC_SUPABASE_PUBLISHABLE_KEY;
  if (!url || !publishableKey) {
    throw new Error("Missing EXPO_PUBLIC_SUPABASE_URL or EXPO_PUBLIC_SUPABASE_PUBLISHABLE_KEY");
  }
  if (SECRET_MARKERS.some((marker) => publishableKey.includes(marker))) {
    throw new Error("The client is configured with a secret key");
  }
  return { url, publishableKey };
}
