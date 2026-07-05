import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface SettingsState {
  apiKey: string;
  setApiKey: (key: string) => void;
  simulationMode: boolean;
  setSimulationMode: (mode: boolean) => void;
}

export const useStore = create<SettingsState>()(
  persist(
    (set) => ({
      apiKey: '',
      setApiKey: (key) => set({ apiKey: key }),
      simulationMode: true,
      setSimulationMode: (mode) => set({ simulationMode: mode }),
    }),
    {
      name: 'oasis-settings',
    }
  )
);
