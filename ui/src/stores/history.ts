import { create } from 'zustand';
import { immer } from 'zustand/middleware/immer';
import { get as idbGet, set as idbSet, del as idbDel, keys as idbKeys } from 'idb-keyval';
import type { HistoryItem } from '@/types/api';
import { config } from '@/lib/config';

const KEY_PREFIX = 'history:';

interface HistoryState {
  items: HistoryItem[];
  loaded: boolean;
  load(): Promise<void>;
  add(item: HistoryItem): Promise<void>;
  remove(id: string): Promise<void>;
  clear(): Promise<void>;
}

export const useHistoryStore = create<HistoryState>()(
  immer((set, get) => ({
    items: [],
    loaded: false,
    load: async () => {
      if (get().loaded) return;
      const allKeys = (await idbKeys()) as string[];
      const histKeys = allKeys.filter((k) => typeof k === 'string' && k.startsWith(KEY_PREFIX));
      const items: HistoryItem[] = [];
      for (const k of histKeys) {
        const v = await idbGet<HistoryItem>(k);
        if (v) items.push(v);
      }
      items.sort((a, b) => b.createdAt - a.createdAt);
      set((s) => {
        s.items = items.slice(0, config.audio.maxHistorySize);
        s.loaded = true;
      });
    },
    add: async (item) => {
      await idbSet(`${KEY_PREFIX}${item.id}`, item);
      set((s) => {
        s.items.unshift(item);
        if (s.items.length > config.audio.maxHistorySize) {
          const removed = s.items.splice(config.audio.maxHistorySize);
          for (const r of removed) void idbDel(`${KEY_PREFIX}${r.id}`);
        }
      });
    },
    remove: async (id) => {
      await idbDel(`${KEY_PREFIX}${id}`);
      set((s) => {
        s.items = s.items.filter((i) => i.id !== id);
      });
    },
    clear: async () => {
      const allKeys = (await idbKeys()) as string[];
      for (const k of allKeys) if (typeof k === 'string' && k.startsWith(KEY_PREFIX)) await idbDel(k);
      set((s) => void (s.items = []));
    },
  })),
);
