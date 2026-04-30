import type { AxiosResponse, InternalAxiosRequestConfig } from 'axios';
import apiClient from '../api/client';
import { mockLoginResponse, mockOrders, mockTables, mockMenus, mockCategories, buildDashboard, ordersToHistory } from './data';

const delay = (ms: number) => new Promise((r) => setTimeout(r, ms));

let orders = [...mockOrders];
let tables = [...mockTables];
let menus = [...mockMenus];
let nextTableId = 6;

function makeResponse<T>(data: T, status = 200): AxiosResponse<T> {
  return { data, status, statusText: 'OK', headers: {}, config: {} as InternalAxiosRequestConfig };
}

export function setupMockInterceptor() {
  apiClient.interceptors.request.use(async (config) => {
    const url = config.url ?? '';
    const method = config.method?.toUpperCase() ?? 'GET';

    await delay(200 + Math.random() * 300);

    // === AUTH ===
    if (url.includes('/auth/login') && method === 'POST') {
      const body = typeof config.data === 'string' ? JSON.parse(config.data) : config.data;
      if (body.username === 'admin' && body.password === '1234') {
        return Promise.reject({ __mock: true, response: makeResponse(mockLoginResponse) });
      }
      return Promise.reject({ __mock: true, response: makeResponse({ detail: '매장 식별자, 사용자명 또는 비밀번호가 올바르지 않습니다.', remaining_attempts: 4 }, 401) });
    }

    if (url.includes('/auth/verify') && method === 'POST') {
      const token = config.headers?.Authorization;
      if (token) {
        return Promise.reject({ __mock: true, response: makeResponse({ valid: true, store_id: 'store-1', username: 'admin', expires_at: new Date(Date.now() + 16 * 3600000).toISOString() }) });
      }
      return Promise.reject({ __mock: true, response: makeResponse({ detail: 'Unauthorized' }, 401) });
    }

    // === DASHBOARD ===
    if (url.includes('/dashboard') && method === 'GET') {
      return Promise.reject({ __mock: true, response: makeResponse({ tables: buildDashboard(orders) }) });
    }

    // === TABLE ORDERS ===
    const tableOrderMatch = url.match(/\/tables\/([\w-]+)\/orders/);
    if (tableOrderMatch && method === 'GET') {
      const tableId = tableOrderMatch[1];
      // tableId could be table_number or table_id
      const tbl = tables.find((t) => t.id === tableId || String(t.table_number) === tableId);
      const filtered = tbl ? orders.filter((o) => o.table_id === tbl.id) : [];
      return Promise.reject({ __mock: true, response: makeResponse({ orders: filtered }) });
    }

    // === ORDER STATUS ===
    const statusMatch = url.match(/\/orders\/([\w-]+)\/status/);
    if (statusMatch && method === 'PATCH') {
      const orderId = statusMatch[1];
      const body = typeof config.data === 'string' ? JSON.parse(config.data) : config.data;
      orders = orders.map((o) => (o.id === orderId ? { ...o, status: body.status, updated_at: new Date().toISOString() } : o));
      return Promise.reject({ __mock: true, response: makeResponse(orders.find((o) => o.id === orderId)) });
    }

    // === ORDER DELETE ===
    const deleteOrderMatch = url.match(/\/orders\/([\w-]+)$/);
    if (deleteOrderMatch && method === 'DELETE') {
      orders = orders.filter((o) => o.id !== deleteOrderMatch[1]);
      return Promise.reject({ __mock: true, response: makeResponse({ success: true }) });
    }

    // === ORDER HISTORY ===
    if (url.includes('/orders/history') && method === 'GET') {
      const page = Number(config.params?.page ?? 1);
      const size = Number(config.params?.size ?? 20);
      const history = ordersToHistory([...orders].reverse());
      return Promise.reject({
        __mock: true,
        response: makeResponse({
          orders: history.slice((page - 1) * size, page * size),
          total: history.length,
          page,
          size,
          total_pages: Math.ceil(history.length / size) || 1,
        }),
      });
    }

    // === TABLES ===
    if (url.match(/\/tables$/) && method === 'GET') {
      return Promise.reject({ __mock: true, response: makeResponse({ tables }) });
    }

    if (url.match(/\/tables$/) && method === 'POST') {
      const body = typeof config.data === 'string' ? JSON.parse(config.data) : config.data;
      if (tables.some((t) => t.table_number === body.table_number)) {
        return Promise.reject({ __mock: true, response: makeResponse({ detail: '이미 등록된 테이블 번호입니다.' }, 409) });
      }
      const newTable = { id: `tbl-${nextTableId++}`, store_id: 'store-1', table_number: body.table_number, is_active: true, created_at: new Date().toISOString(), url: `/store/store-1/table/${body.table_number}` };
      tables.push(newTable);
      return Promise.reject({ __mock: true, response: makeResponse(newTable, 201) });
    }

    // === SESSION COMPLETE ===
    const completeMatch = url.match(/\/tables\/([\w-]+)\/complete/);
    if (completeMatch && method === 'POST') {
      const tableId = completeMatch[1];
      const tbl = tables.find((t) => t.id === tableId || String(t.table_number) === tableId);
      if (tbl) orders = orders.filter((o) => o.table_id !== tbl.id);
      return Promise.reject({ __mock: true, response: makeResponse({ message: '이용 완료' }) });
    }

    // === MENUS ===
    if (url.match(/\/menus$/) && method === 'GET') {
      return Promise.reject({ __mock: true, response: makeResponse({ menus }) });
    }

    const menuIdMatch = url.match(/\/menus\/([\w-]+)$/);
    if (menuIdMatch && method === 'GET') {
      const menu = menus.find((m) => m.id === menuIdMatch[1]);
      return Promise.reject({ __mock: true, response: makeResponse(menu) });
    }

    if (url.match(/\/menus$/) && method === 'POST') {
      const fd = config.data as FormData;
      const newMenu = {
        id: `menu-${Date.now()}`, store_id: 'store-1', category_id: fd.get('category_id') as string,
        name: fd.get('name') as string, price: Number(fd.get('price')),
        description: (fd.get('description') as string) || undefined,
        sort_order: menus.length, is_available: true,
        created_at: new Date().toISOString(), updated_at: new Date().toISOString(),
      };
      menus.push(newMenu);
      return Promise.reject({ __mock: true, response: makeResponse(newMenu, 201) });
    }

    if (menuIdMatch && method === 'PUT') {
      const fd = config.data as FormData;
      menus = menus.map((m) => m.id === menuIdMatch[1] ? { ...m, name: fd.get('name') as string ?? m.name, price: Number(fd.get('price')) || m.price, updated_at: new Date().toISOString() } : m);
      return Promise.reject({ __mock: true, response: makeResponse(menus.find((m) => m.id === menuIdMatch[1])) });
    }

    if (menuIdMatch && method === 'DELETE') {
      menus = menus.filter((m) => m.id !== menuIdMatch[1]);
      return Promise.reject({ __mock: true, response: makeResponse({ success: true }) });
    }

    if (url.includes('/menus/reorder') && method === 'PATCH') {
      return Promise.reject({ __mock: true, response: makeResponse({ success: true }) });
    }

    // === CATEGORIES ===
    if (url.match(/\/categories/) && method === 'GET') {
      return Promise.reject({ __mock: true, response: makeResponse({ categories: mockCategories }) });
    }

    return config;
  });

  apiClient.interceptors.response.use(
    (response) => response,
    (error) => {
      if (error?.__mock && error.response) {
        const mockResp = error.response;
        if (mockResp.status >= 400) return Promise.reject({ response: mockResp });
        return Promise.resolve(mockResp);
      }
      return Promise.reject(error);
    },
  );
}
