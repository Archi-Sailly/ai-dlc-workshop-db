import { create } from 'zustand';
import type { LoginRequest, LoginResponse, TokenVerifyResponse } from '../types';
import apiClient from '../api/client';

interface AuthState {
  token: string | null;
  storeId: string | null;
  username: string | null;
  displayName: string | null;
  isAuthenticated: boolean;
  expiresAt: string | null;
  isLoading: boolean;
}

interface AuthActions {
  login: (credentials: LoginRequest) => Promise<LoginResponse>;
  logout: () => void;
  initAuth: () => Promise<void>;
}

export const useAuthStore = create<AuthState & AuthActions>((set) => ({
  token: null,
  storeId: null,
  username: null,
  displayName: null,
  isAuthenticated: false,
  expiresAt: null,
  isLoading: true,

  login: async (credentials) => {
    const { data } = await apiClient.post<LoginResponse>('/api/admin/auth/login', credentials);
    localStorage.setItem('admin_access_token', data.access_token);
    set({
      token: data.access_token,
      storeId: data.store_id,
      username: data.username,
      displayName: data.display_name,
      isAuthenticated: true,
      expiresAt: data.expires_at,
    });
    return data;
  },

  logout: () => {
    localStorage.removeItem('admin_access_token');
    set({
      token: null,
      storeId: null,
      username: null,
      displayName: null,
      isAuthenticated: false,
      expiresAt: null,
    });
  },

  initAuth: async () => {
    const token = localStorage.getItem('admin_access_token');
    if (!token) {
      set({ isLoading: false });
      return;
    }
    try {
      const { data } = await apiClient.post<TokenVerifyResponse>('/api/admin/auth/verify');
      if (data.valid && data.store_id) {
        set({
          token,
          storeId: data.store_id,
          username: data.username,
          isAuthenticated: true,
          expiresAt: data.expires_at,
          isLoading: false,
        });
      } else {
        localStorage.removeItem('admin_access_token');
        set({ isLoading: false });
      }
    } catch {
      localStorage.removeItem('admin_access_token');
      set({ isLoading: false });
    }
  },
}));
