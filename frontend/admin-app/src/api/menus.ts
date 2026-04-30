import apiClient from './client';
import type { Menu, Category } from '../types';

export async function getMenus(storeId: string, categoryId?: string) {
  const { data } = await apiClient.get<{ menus: Menu[] }>(`/api/admin/stores/${storeId}/menus`, {
    params: categoryId ? { category_id: categoryId } : undefined,
  });
  return data.menus;
}

export async function getMenu(storeId: string, menuId: string) {
  const { data } = await apiClient.get<Menu>(`/api/admin/stores/${storeId}/menus/${menuId}`);
  return data;
}

export async function createMenu(storeId: string, formData: FormData) {
  const { data } = await apiClient.post<Menu>(`/api/admin/stores/${storeId}/menus`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
}

export async function updateMenu(storeId: string, menuId: string, formData: FormData) {
  const { data } = await apiClient.put<Menu>(`/api/admin/stores/${storeId}/menus/${menuId}`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
}

export async function deleteMenu(storeId: string, menuId: string) {
  await apiClient.delete(`/api/admin/stores/${storeId}/menus/${menuId}`);
}

export async function reorderMenus(storeId: string, menuOrders: { menu_id: string; sort_order: number }[]) {
  await apiClient.patch(`/api/admin/stores/${storeId}/menus/reorder`, { menu_orders: menuOrders });
}

export async function getCategories(storeId: string) {
  const { data } = await apiClient.get<{ categories: Category[] }>(`/api/admin/stores/${storeId}/categories`);
  return data.categories;
}

export async function createCategory(storeId: string, name: string) {
  const { data } = await apiClient.post<Category>(`/api/admin/stores/${storeId}/categories`, { name });
  return data;
}
