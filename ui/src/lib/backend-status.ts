export type BackendStatus = 'ok' | 'healthy' | 'degraded' | 'down' | string;

export function isBackendReady(status: BackendStatus | undefined, online = true): boolean {
  if (!online) return false;
  return status === 'ok' || status === 'healthy' || status === 'degraded';
}

export function backendStatusLabel(status: BackendStatus | undefined, online = true): 'Online' | 'Degraded' | 'Offline' {
  if (!online) return 'Offline';
  if (status === 'ok' || status === 'healthy') return 'Online';
  if (status === 'degraded') return 'Degraded';
  return 'Offline';
}
