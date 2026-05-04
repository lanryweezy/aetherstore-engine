import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';

interface SapiensMeasurements {
  height: number;
  chest: number;
  waist: number;
  hips: number;
}
interface UserState {
  measurements: SapiensMeasurements;
  selectedProduct: any | null;
  isPhotorealMode: boolean;
  activeMaterial: string;
  telemetry: any | null;
  remoteUsers: Record<string, any>; // Track other players

  // Actions
  setMeasurements: (m: SapiensMeasurements) => void;
  updateMeasurement: (key: keyof SapiensMeasurements, val: number) => void;
  setSelectedProduct: (p: any) => void;
  setPhotorealMode: (val: boolean) => void;
  setActiveMaterial: (m: string) => void;
  setTelemetry: (t: any) => void;
  updateRemoteUser: (id: string, state: any) => void;
  removeRemoteUser: (id: string) => void;
  resetMeasurements: () => void;
}

export const useStore = create<UserState>()(
  persist(
    (set) => ({
      measurements: {
        height: 175,
        chest: 95,
        waist: 80,
        hips: 95
      },
      selectedProduct: null,
      isPhotorealMode: false,
      activeMaterial: 'silk',
      telemetry: null,
      remoteUsers: {},

      setMeasurements: (measurements) => set({ measurements }),

      updateMeasurement: (key, val) => set((state) => ({
        measurements: { ...state.measurements, [key]: val }
      })),

      setSelectedProduct: (selectedProduct) => set({ selectedProduct }),

      setPhotorealMode: (isPhotorealMode) => set({ isPhotorealMode }),

      setActiveMaterial: (activeMaterial) => set({ activeMaterial }),

      setTelemetry: (telemetry) => set({ telemetry }),

      updateRemoteUser: (id, state) => set((s) => ({
          remoteUsers: { ...s.remoteUsers, [id]: state }
      })),

      removeRemoteUser: (id) => set((s) => {
          const newUsers = { ...s.remoteUsers };
          delete newUsers[id];
          return { remoteUsers: newUsers };
      }),

      resetMeasurements: () => set({
...

        measurements: { height: 175, chest: 95, waist: 80, hips: 95 }
      })
    }),
    {
      name: 'aetherstore-user-session',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({ 
        measurements: state.measurements,
        isPhotorealMode: state.isPhotorealMode,
        activeMaterial: state.activeMaterial
      }), // Only persist critical user data
    }
  )
);
