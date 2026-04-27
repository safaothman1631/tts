import { config } from '@/lib/config';

export type StreamEvent =
  | { type: 'meta'; sampleRate: number; format: string }
  | { type: 'chunk'; bytes: ArrayBuffer; index: number }
  | { type: 'progress'; ratio: number }
  | { type: 'done'; durationSeconds: number }
  | { type: 'error'; message: string };

export interface StreamHandle {
  close(): void;
  readonly socket: WebSocket;
}

/**
 * Open a WebSocket synthesis stream.
 * Handler receives typed events; binary frames are surfaced as 'chunk'.
 */
export function streamSynthesize(
  payload: Record<string, unknown>,
  onEvent: (e: StreamEvent) => void,
): StreamHandle {
  const url = `${config.wsBaseUrl}/synthesize`;
  const socket = new WebSocket(url);
  socket.binaryType = 'arraybuffer';
  let chunkIndex = 0;

  socket.addEventListener('open', () => {
    socket.send(JSON.stringify(payload));
  });

  socket.addEventListener('message', (ev) => {
    if (typeof ev.data === 'string') {
      try {
        const msg = JSON.parse(ev.data);
        if (msg.type === 'meta') {
          onEvent({ type: 'meta', sampleRate: msg.sampleRate ?? 22050, format: msg.format ?? 'wav' });
        } else if (msg.type === 'progress') {
          onEvent({ type: 'progress', ratio: Number(msg.ratio) || 0 });
        } else if (msg.type === 'done') {
          onEvent({ type: 'done', durationSeconds: Number(msg.durationSeconds) || 0 });
        } else if (msg.type === 'error') {
          onEvent({ type: 'error', message: String(msg.message ?? 'stream error') });
        }
      } catch {
        /* ignore malformed text */
      }
    } else {
      onEvent({ type: 'chunk', bytes: ev.data as ArrayBuffer, index: chunkIndex++ });
    }
  });

  socket.addEventListener('error', () => onEvent({ type: 'error', message: 'WebSocket error' }));

  return {
    socket,
    close: () => socket.readyState <= 1 && socket.close(),
  };
}
