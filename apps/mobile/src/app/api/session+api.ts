import { createRequestSupabase } from "@/lib/supabase-server";

export async function GET(request: Request): Promise<Response> {
  const supabase = createRequestSupabase(request.headers.get("cookie"));
  const { data, error } = await supabase.auth.getUser();
  if (error || !data.user) {
    return Response.json({ email: null });
  }
  return Response.json({ email: data.user.email ?? null });
}
