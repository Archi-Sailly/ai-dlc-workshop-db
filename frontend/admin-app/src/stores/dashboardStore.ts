import { create } from 'zustand';
import type { DashboardTable, Order, DashboardResponse } from '../types';
import { SSEConnectionStatus } from '../types';
import apiClient from '../api/client';

interface DashboardState {
  tables: DashboardTable[];
  isLoading: boolean;
  error: string | null;
  sseStatus: SSEConnectionStatus;
  pulsingTables: Set<number>;
}

interface DashboardActions {
  fetchDashboard: (storeId: string) => Promise<void>;
  addNewOrder: (tableNumber: number, order: Order) => void;
  updateOrderStatus: (orderId: string, newStatus: string) => void;
  removeOrder: (orderId: string, tableNumber: number) => void;
  resetTable: (tableNumber: number) => void;
  setSSEStatus: (status: SSEConnectionStatus) => void;
  startPulse: (tableNumber: number) => void;
  stopPulse: (tableNumber: number) => void;
  reset: () => void;
}

export const useDashboardStore = create<DashboardState & DashboardActions>((set, get) => ({
  tables: [],
  isLoading: false,
  error: null,
  sseStatus: SSEConnectionStatus.DISCONNECTED,
  pulsingTables: new Set(),

  fetchDashboard: async (storeId) => {
    set({ isLoading: true, error: null });
    try {
      const { data } = await apiClient.get<DashboardResponse>(`/api/admin/stores/${storeId}/dashboard`);
      const sorted = [...data.tables].sort((a, b) => a.table_number - b.table_number);
      set({ tables: sorted, isLoading: false });
    } catch {
      set({ error: '대시보드 데이터를 불러올 수 없습니다.', isLoading: false });
    }
  },

  addNewOrder: (tableNumber, order) => {
    set((state) => ({
      tables: state.tables.map((t) =>
        t.table_number === tableNumber
          ? {
              ...t,
              latest_orders: [...t.latest_orders, order],
              total_amount: t.total_amount + order.total_amount,
              order_count: t.order_count + 1,
              has_new_order: true,
            }
          : t,
      ),
    }));
    get().startPulse(tableNumber);
    setTimeout(() => get().stopPulse(tableNumber), 5000);
  },

  updateOrderStatus: (orderId, newStatus) => {
    set((state) => ({
      tables: state.tables.map((t) => ({
        ...t,
        latest_orders: t.latest_orders.map((o) =>
          o.id === orderId ? { ...o, status: newStatus as Order['status'] } : o,
        ),
      })),
    }));
  },

  removeOrder: (orderId, tableNumber) => {
    set((state) => ({
      tables: state.tables.map((t) => {
        if (t.table_number !== tableNumber) return t;
        const removed = t.latest_orders.find((o) => o.id === orderId);
        const filtered = t.latest_orders.filter((o) => o.id !== orderId);
        return {
          ...t,
          latest_orders: filtered,
          total_amount: t.total_amount - (removed?.total_amount ?? 0),
          order_count: Math.max(0, t.order_count - 1),
        };
      }),
    }));
  },

  resetTable: (tableNumber) => {
    set((state) => ({
      tables: state.tables.map((t) =>
        t.table_number === tableNumber
          ? { ...t, latest_orders: [], total_amount: 0, order_count: 0, has_new_order: false }
          : t,
      ),
    }));
  },

  setSSEStatus: (status) => set({ sseStatus: status }),

  startPulse: (tableNumber) => {
    set((state) => {
      const next = new Set(state.pulsingTables);
      next.add(tableNumber);
      return { pulsingTables: next };
    });
  },

  stopPulse: (tableNumber) => {
    set((state) => {
      const next = new Set(state.pulsingTables);
      next.delete(tableNumber);
      return { pulsingTables: next };
    });
  },

  reset: () => set({ tables: [], isLoading: false, error: null, pulsingTables: new Set() }),
}));
