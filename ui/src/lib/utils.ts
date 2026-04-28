import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDuration(seconds: number): string {
  if (!Number.isFinite(seconds) || seconds < 0) return '0:00';
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}:${s.toString().padStart(2, '0')}`;
}

export function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
}

export function truncate(text: string, max = 80): string {
  return text.length <= max ? text : text.slice(0, max - 1) + '…';
}

export function audioExtensionFromBlob(blob: Blob, fallback = 'wav'): string {
  const type = (blob.type || '').toLowerCase();
  if (type.includes('audio/wav') || type.includes('audio/x-wav') || type.includes('audio/wave')) return 'wav';
  if (type.includes('audio/mpeg') || type.includes('audio/mp3')) return 'mp3';
  if (type.includes('audio/flac') || type.includes('audio/x-flac')) return 'flac';
  if (type.includes('audio/ogg')) return 'ogg';
  return fallback;
}

export function downloadBlob(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

export function uid(): string {
  return crypto.randomUUID();
}

export function sleep(ms: number): Promise<void> {
  return new Promise((r) => setTimeout(r, ms));
}
