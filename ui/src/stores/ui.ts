import { create } from 'zustand';

interface UiState {
  paletteOpen: boolean;
  sidebarOpen: boolean;
  togglePalette(open?: boolean): void;
  toggleSidebar(open?: boolean): void;
}

export const useUiStore = create<UiState>((set) => ({
  paletteOpen: false,
  sidebarOpen: true,
  togglePalette: (open) => set((s) => ({ paletteOpen: open ?? !s.paletteOpen })),
  toggleSidebar: (open) => set((s) => ({ sidebarOpen: open ?? !s.sidebarOpen })),
}));
