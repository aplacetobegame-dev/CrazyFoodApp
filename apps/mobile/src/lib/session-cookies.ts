export type SessionCookie = {
  name: string;
  value: string;
  options?: {
    domain?: string;
    expires?: Date;
    httpOnly?: boolean;
    maxAge?: number;
    path?: string;
    sameSite?: boolean | "lax" | "strict" | "none";
    secure?: boolean;
  };
};

function sameSiteLabel(value: NonNullable<SessionCookie["options"]>["sameSite"]): string | null {
  if (value === true || value === "strict") return "Strict";
  if (value === "lax") return "Lax";
  if (value === "none") return "None";
  return null;
}

export function serializeSetCookie(cookie: SessionCookie): string {
  const parts = [`${cookie.name}=${encodeURIComponent(cookie.value)}`];
  const options = cookie.options;
  if (!options) return parts[0] ?? "";
  if (options.maxAge !== undefined) parts.push(`Max-Age=${Math.trunc(options.maxAge)}`);
  if (options.domain) parts.push(`Domain=${options.domain}`);
  if (options.path) parts.push(`Path=${options.path}`);
  if (options.expires) parts.push(`Expires=${options.expires.toUTCString()}`);
  if (options.httpOnly) parts.push("HttpOnly");
  if (options.secure) parts.push("Secure");
  const sameSite = sameSiteLabel(options.sameSite);
  if (sameSite) parts.push(`SameSite=${sameSite}`);
  return parts.join("; ");
}
