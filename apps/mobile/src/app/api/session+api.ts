import { isUiPreview } from "@/lib/app-mode";
import { applySetCookies, createRequestSupabase } from "@/lib/supabase-server";

export async function GET(request: Request): Promise<Response> {
  if (isUiPreview) {
    return Response.json({ email: null });
  }
  const { supabase, setCookieHeaders } = createRequestSupabase(request.headers.get("cookie"));
  const { data, error } = await supabase.auth.getUser();
  const headers = new Headers();
  applySetCookies(headers, setCookieHeaders());
  if (error || !data.user) {
    return Response.json({ email: null }, { headers });
  }
  return Response.json({ email: data.user.email ?? null }, { headers });
}
