import { useEffect, useRef, useCallback } from 'react';
import { fetchEventSource } from '@microsoft/fetch-event-source';
import { useDashboardStore } from '../stores/dashboardStore';
import { useAuthStore } from '../stores/authStore';
import { SSEConnectionStatus, SSEEventType } from '../types';

const MAX_RETRY_INTERVAL = 30000;

export function useSSE() {
  const storeId = useAuthStore((s) => s.storeId);
  const token = useAuthStore((s) => s.token);
  const setSSEStatus = useDashboardStore((s) => s.setSSEStatus);
  const addNewOrder = useDashboardStore((s) => s.addNewOrder);
  const updateOrderStatus = useDashboardStore((s) => s.updateOrderStatus);
  const removeOrder = useDashboardStore((s) => s.removeOrder);
  const resetTable = useDashboardStore((s) => s.resetTable);
  const fetchDashboard = useDashboardStore((s) => s.fetchDashboard);
  const abortRef = useRef<AbortController | null>(null);

  const connect = useCallback(() => {
    if (!storeId || !token) return;

    abortRef.current?.abort();
    const ctrl = new AbortController();
    abortRef.current = ctrl;

    let retryInterval = 1000;
    const baseUrl = import.meta.env.VITE_API_BASE_URL || '';
    const url = `${baseUrl}/api/sse/stores/${storeId}/orders`;

    fetchEventSource(url, {
      headers: { Authorization: `Bearer ${token}` },
      signal: ctrl.signal,

      async onopen() {
        setSSEStatus(SSEConnectionStatus.CONNECTED);
        retryInterval = 1000;
        await fetchDashboard(storeId);
      },

      onmessage(event) {
        if (!event.data) return;
        try {
          const parsed = JSON.parse(event.data);
          const eventType = event.event || parsed.event_type;

          switch (eventType) {
            case SSEEventType.ORDER_CREATED:
              addNewOrder(parsed.table_number ?? parsed.data?.table_number, parsed.data ?? parsed);
              break;
            case SSEEventType.ORDER_STATUS_CHANGED:
              updateOrderStatus(
                parsed.data?.order_id ?? parsed.order_id,
                parsed.data?.new_status ?? parsed.new_status,
              );
              break;
            case SSEEventType.ORDER_DELETED:
              removeOrder(
                parsed.data?.order_id ?? parsed.order_id,
                parsed.table_number ?? parsed.data?.table_number,
              );
              break;
            case SSEEventType.SESSION_COMPLETED:
              resetTable(parsed.table_number ?? parsed.data?.table_number);
              break;
          }
        } catch {
          // 파싱 실패 무시
        }
      },

      onerror() {
        setSSEStatus(SSEConnectionStatus.RECONNECTING);
        retryInterval = Math.min(retryInterval * 2, MAX_RETRY_INTERVAL);
      },

      onclose() {
        setSSEStatus(SSEConnectionStatus.DISCONNECTED);
      },
    });
  }, [storeId, token, setSSEStatus, addNewOrder, updateOrderStatus, removeOrder, resetTable, fetchDashboard]);

  const disconnect = useCallback(() => {
    abortRef.current?.abort();
    setSSEStatus(SSEConnectionStatus.DISCONNECTED);
  }, [setSSEStatus]);

  useEffect(() => {
    connect();
    return () => disconnect();
  }, [connect, disconnect]);
}
