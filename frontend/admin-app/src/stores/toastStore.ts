import { create } from 'zustand';
import type { ToastMessage } from '../types';

interface ToastState {
  messages: ToastMessage[];
  addToast: (msg: Omit<ToastMessage, 'id'>) => void;
  removeToast: (id: string) => void;
}

let toastId = 0;

export const useToastStore = create<ToastState>((set) => ({
  messages: [],

  addToast: (msg) => {
    const id = String(++toastId);
    const duration = msg.duration ?? (msg.type === 'error' ? 5000 : 3000);
    set((state) => ({
      messages: [...state.messages.slice(-2), { ...msg, id }],
    }));
    setTimeout(() => {
      set((state) => ({ messages: state.messages.filter((m) => m.id !== id) }));
    }, duration);
  },

  removeToast: (id) => {
    set((state) => ({ messages: state.messages.filter((m) => m.id !== id) }));
  },
}));
