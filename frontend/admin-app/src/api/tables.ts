import apiClient from './client';
import type { Table } from '../types';

export async function getTables(storeId: string) {
  const { data } = await apiClient.get<{ tables: Table[] }>(`/api/admin/stores/${storeId}/tables`);
  return data.tables;
}

export async function createTable(storeId: string, tableNumber: number) {
  const { data } = await apiClient.post<Table>(`/api/admin/stores/${storeId}/tables`, {
    table_number: tableNumber,
  });
  return data;
}

export async function completeSession(storeId: string, tableNumber: number) {
  const { data } = await apiClient.post(`/api/admin/stores/${storeId}/tables/${tableNumber}/complete`);
  return data;
}
