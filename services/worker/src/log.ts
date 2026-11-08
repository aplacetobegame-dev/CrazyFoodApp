export function log(event: Record<string, string | number | boolean | null>): void {
  console.log(JSON.stringify({ time: new Date().toISOString(), ...event }));
}
