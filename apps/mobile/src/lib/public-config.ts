const SECRET_MARKERS = ["service_role", "sb_secret_"];

export function publicSupabaseProblem(): string | null {
  const url = process.env.EXPO_PUBLIC_SUPABASE_URL;
  const publishableKey = process.env.EXPO_PUBLIC_SUPABASE_PUBLISHABLE_KEY;
  if (!url || !publishableKey) {
    return "Missing EXPO_PUBLIC_SUPABASE_URL or EXPO_PUBLIC_SUPABASE_PUBLISHABLE_KEY. Add them to apps/mobile/.env.local.";
  }
  if (SECRET_MARKERS.some((marker) => publishableKey.includes(marker))) {
    return "The client is configured with a secret key. Use the publishable key.";
  }
  return null;
}

export function publicSupabaseConfig(): { url: string; publishableKey: string } {
  const problem = publicSupabaseProblem();
  if (problem) {
    throw new Error(problem);
  }
  return {
    url: process.env.EXPO_PUBLIC_SUPABASE_URL ?? "",
    publishableKey: process.env.EXPO_PUBLIC_SUPABASE_PUBLISHABLE_KEY ?? "",
  };
}
