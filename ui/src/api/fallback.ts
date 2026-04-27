export function parseBooleanEnv(value: unknown, defaultValue = false): boolean {
  if (typeof value !== 'string') return defaultValue;
  const normalized = value.trim().toLowerCase();
  if (normalized === 'true' || normalized === '1' || normalized === 'yes') return true;
  if (normalized === 'false' || normalized === '0' || normalized === 'no') return false;
  return defaultValue;
}

export function isCooldownActive(key: string, now: () => number = Date.now): boolean {
  try {
    const raw = window.localStorage.getItem(key);
    const until = Number(raw);
    if (!raw || !Number.isFinite(until)) return false;
    if (now() > until) {
      window.localStorage.removeItem(key);
      return false;
    }
    return true;
  } catch {
    return false;
  }
}

export function markCooldown(key: string, ttlMs: number, now: () => number = Date.now): void {
  try {
    window.localStorage.setItem(key, String(now() + ttlMs));
  } catch {
    // Ignore storage failures (private mode, quota, etc).
  }
}

export function getErrorStatus(error: unknown): number | undefined {
  const direct = Number((error as { status?: unknown })?.status);
  if (Number.isFinite(direct)) return direct;
  const nested = Number((error as { response?: { status?: unknown } })?.response?.status);
  if (Number.isFinite(nested)) return nested;
  return undefined;
}

export function isEndpointUnavailableStatus(status: number | undefined): boolean {
  return status === 404 || status === 405;
}