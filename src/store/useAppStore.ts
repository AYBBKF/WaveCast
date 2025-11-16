import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { v4 as uuidv4 } from 'uuid';
import { Channel } from '../types';

interface AppState {
  deviceId: string;
  isTrialActive: boolean;
  trialEndDate: number | null;
  isActivated: boolean;
  m3uUrl: string;
  playlist: Channel[];
  setM3uUrl: (url: string) => void;
  setPlaylist: (playlist: Channel[]) => void;
  checkTrialStatus: () => void;
}

const SEVEN_DAYS_IN_MS = 7 * 24 * 60 * 60 * 1000;

export const useAppStore = create<AppState>()(
  persist(
    (set, get) => ({
      deviceId: uuidv4(),
      isTrialActive: true,
      trialEndDate: Date.now() + SEVEN_DAYS_IN_MS,
      isActivated: false,
      m3uUrl: '',
      playlist: [],
      setM3uUrl: (url) => set({ m3uUrl: url }),
      setPlaylist: (playlist) => set({ playlist }),
      checkTrialStatus: () => {
        const { trialEndDate, isActivated } = get();
        if (isActivated) {
          set({ isTrialActive: false });
          return;
        }
        if (trialEndDate && Date.now() > trialEndDate) {
          set({ isTrialActive: false });
        } else {
          set({ isTrialActive: true });
        }
      },
    }),
    {
      name: 'iptv-app-storage',
      storage: createJSONStorage(() => localStorage),
      onRehydrate: (state) => {
        state?.checkTrialStatus();
      }
    }
  )
);

// Initialize deviceId if it's not already in storage
useAppStore.getState();
