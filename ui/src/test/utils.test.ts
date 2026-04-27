import { describe, it, expect } from 'vitest';
import { cn, formatDuration, truncate, formatBytes } from '@/lib/utils';

describe('utils', () => {
  it('cn merges classes', () => {
    const flag = false as boolean;
    expect(cn('a', flag && 'b', 'c')).toContain('a');
    expect(cn('px-2', 'px-4')).toBe('px-4');
  });

  it('formatDuration', () => {
    expect(formatDuration(0)).toBe('0:00');
    expect(formatDuration(65)).toBe('1:05');
    expect(formatDuration(-1)).toBe('0:00');
  });

  it('truncate', () => {
    expect(truncate('hello world', 5)).toBe('hell…');
    expect(truncate('short')).toBe('short');
  });

  it('formatBytes', () => {
    expect(formatBytes(0)).toBe('0 B');
    expect(formatBytes(2048)).toBe('2 KB');
  });
});
