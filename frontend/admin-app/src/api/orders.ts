import apiClient from './client';
import type { Order, OrderHistoryResponse } from '../types';

export async function getTableOrders(storeId: string, tableNumber: number) {
  const { data } = await apiClient.get<{ orders: Order[]; total: number }>(
    `/api/admin/stores/${storeId}/tables/${tableNumber}/orders`,
  );
  return data.orders;
}

export async function updateOrderStatus(storeId: string, orderId: string, status: string) {
  const { data } = await apiClient.patch<Order>(
    `/api/admin/stores/${storeId}/orders/${orderId}/status`,
    { status },
  );
  return data;
}

export async function deleteOrder(storeId: string, orderId: string, reason?: string) {
  await apiClient.delete(`/api/admin/stores/${storeId}/orders/${orderId}`, {
    data: reason ? { reason } : undefined,
  });
}

export async function getOrderHistory(
  storeId: string,
  params: { table_number?: number; date_from?: string; date_to?: string; page: number; size: number },
) {
  const { data } = await apiClient.get<OrderHistoryResponse>(
    `/api/admin/stores/${storeId}/orders/history`,
    { params },
  );
  return data;
}
