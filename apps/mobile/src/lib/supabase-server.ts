import { createServerClient, type CookieMethodsServer } from "@supabase/ssr";
import { publicSupabaseConfig } from "@/lib/public-config";
import { serializeSetCookie, type SessionCookie } from "@/lib/session-cookies";

function parseCookies(header: string | null): { name: string; value: string }[] {
  if (!header) {
    return [];
  }
  return header
    .split(";")
    .map((part) => {
      const separator = part.indexOf("=");
      if (separator === -1) {
        return null;
      }
      const name = part.slice(0, separator).trim();
      const rawValue = part.slice(separator + 1).trim();
      if (!name) {
        return null;
      }
      try {
        return { name, value: decodeURIComponent(rawValue) };
      } catch {
        return { name, value: rawValue };
      }
    })
    .filter((cookie): cookie is { name: string; value: string } => cookie !== null);
}

export function createRequestSupabase(cookieHeader: string | null) {
  const { url, publishableKey } = publicSupabaseConfig();
  const setCookies: string[] = [];
  const cookies: CookieMethodsServer = {
    getAll() {
      return parseCookies(cookieHeader);
    },
    setAll(next) {
      setCookies.splice(0, setCookies.length, ...next.map((cookie) => serializeSetCookie(cookie as SessionCookie)));
    },
  };
  return {
    supabase: createServerClient(url, publishableKey, { cookies }),
    setCookieHeaders: () => [...setCookies],
  };
}

export function applySetCookies(headers: Headers, setCookieHeaders: readonly string[]) {
  for (const cookie of setCookieHeaders) {
    headers.append("set-cookie", cookie);
  }
}
