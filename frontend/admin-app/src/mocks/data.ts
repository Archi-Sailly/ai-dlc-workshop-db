import { OrderStatus } from '../types';
import type { DashboardTable, Order, Menu, Category, Table, OrderHistoryItem } from '../types';

export const mockLoginResponse = {
  access_token: 'mock-jwt-token',
  token_type: 'bearer',
  expires_at: new Date(Date.now() + 16 * 3600000).toISOString(),
  store_id: 'store-1',
  username: 'admin',
  display_name: '관리자',
};

export const mockCategories: Category[] = [
  { id: 'cat-1', store_id: 'store-1', name: '메인', sort_order: 0, created_at: '2026-04-30T09:00:00Z' },
  { id: 'cat-2', store_id: 'store-1', name: '사이드', sort_order: 1, created_at: '2026-04-30T09:00:00Z' },
  { id: 'cat-3', store_id: 'store-1', name: '음료', sort_order: 2, created_at: '2026-04-30T09:00:00Z' },
];

export const mockMenus: Menu[] = [
  { id: 'menu-1', store_id: 'store-1', category_id: 'cat-1', name: '불고기 정식', price: 12000, description: '소불고기와 밥, 반찬 세트', sort_order: 0, is_available: true, created_at: '2026-04-30T09:00:00Z', updated_at: '2026-04-30T09:00:00Z' },
  { id: 'menu-2', store_id: 'store-1', category_id: 'cat-1', name: '김치찌개', price: 9000, description: '돼지고기 김치찌개', sort_order: 1, is_available: true, created_at: '2026-04-30T09:00:00Z', updated_at: '2026-04-30T09:00:00Z' },
  { id: 'menu-3', store_id: 'store-1', category_id: 'cat-1', name: '된장찌개', price: 8000, sort_order: 2, is_available: true, created_at: '2026-04-30T09:00:00Z', updated_at: '2026-04-30T09:00:00Z' },
  { id: 'menu-4', store_id: 'store-1', category_id: 'cat-2', name: '계란말이', price: 5000, sort_order: 0, is_available: true, created_at: '2026-04-30T09:00:00Z', updated_at: '2026-04-30T09:00:00Z' },
  { id: 'menu-5', store_id: 'store-1', category_id: 'cat-2', name: '김치전', price: 6000, sort_order: 1, is_available: true, created_at: '2026-04-30T09:00:00Z', updated_at: '2026-04-30T09:00:00Z' },
  { id: 'menu-6', store_id: 'store-1', category_id: 'cat-3', name: '콜라', price: 2000, sort_order: 0, is_available: true, created_at: '2026-04-30T09:00:00Z', updated_at: '2026-04-30T09:00:00Z' },
  { id: 'menu-7', store_id: 'store-1', category_id: 'cat-3', name: '사이다', price: 2000, sort_order: 1, is_available: true, created_at: '2026-04-30T09:00:00Z', updated_at: '2026-04-30T09:00:00Z' },
];

export const mockTables: Table[] = [
  { id: 'tbl-1', store_id: 'store-1', table_number: 1, is_active: true, created_at: '2026-04-30T09:00:00Z', url: '/store/store-1/table/1' },
  { id: 'tbl-2', store_id: 'store-1', table_number: 2, is_active: true, created_at: '2026-04-30T09:00:00Z', url: '/store/store-1/table/2' },
  { id: 'tbl-3', store_id: 'store-1', table_number: 3, is_active: true, created_at: '2026-04-30T09:00:00Z', url: '/store/store-1/table/3' },
  { id: 'tbl-4', store_id: 'store-1', table_number: 4, is_active: true, created_at: '2026-04-30T09:00:00Z', url: '/store/store-1/table/4' },
  { id: 'tbl-5', store_id: 'store-1', table_number: 5, is_active: true, created_at: '2026-04-30T09:00:00Z', url: '/store/store-1/table/5' },
];

const makeOrder = (id: string, tableId: string, sessionId: string, orderNum: number, status: OrderStatus, items: { menuId: string; name: string; qty: number; price: number }[], minutesAgo: number): Order => ({
  id,
  store_id: 'store-1',
  table_id: tableId,
  session_id: sessionId,
  order_number: orderNum,
  status,
  items: items.map((it, i) => ({
    id: `${id}-item-${i}`,
    menu_id: it.menuId,
    menu_name: it.name,
    quantity: it.qty,
    unit_price: it.price,
    subtotal: it.qty * it.price,
  })),
  total_amount: items.reduce((s, it) => s + it.qty * it.price, 0),
  created_at: new Date(Date.now() - minutesAgo * 60000).toISOString(),
  updated_at: new Date(Date.now() - minutesAgo * 60000).toISOString(),
});

export const mockOrders: Order[] = [
  makeOrder('ord-1', 'tbl-1', 'sess-1', 1001, OrderStatus.PENDING, [
    { menuId: 'menu-1', name: '불고기 정식', qty: 2, price: 12000 },
    { menuId: 'menu-6', name: '콜라', qty: 2, price: 2000 },
  ], 5),
  makeOrder('ord-2', 'tbl-1', 'sess-1', 1002, OrderStatus.ACCEPTED, [
    { menuId: 'menu-4', name: '계란말이', qty: 1, price: 5000 },
  ], 15),
  makeOrder('ord-3', 'tbl-2', 'sess-2', 1003, OrderStatus.PREPARING, [
    { menuId: 'menu-2', name: '김치찌개', qty: 3, price: 9000 },
    { menuId: 'menu-7', name: '사이다', qty: 3, price: 2000 },
  ], 10),
  makeOrder('ord-4', 'tbl-3', 'sess-3', 1004, OrderStatus.COMPLETED, [
    { menuId: 'menu-3', name: '된장찌개', qty: 2, price: 8000 },
  ], 30),
  makeOrder('ord-5', 'tbl-3', 'sess-3', 1005, OrderStatus.PENDING, [
    { menuId: 'menu-5', name: '김치전', qty: 1, price: 6000 },
    { menuId: 'menu-6', name: '콜라', qty: 1, price: 2000 },
  ], 2),
];

export function buildDashboard(orders: Order[]): DashboardTable[] {
  return mockTables.map((t) => {
    const tableOrders = orders.filter((o) => o.table_id === t.id);
    return {
      table_id: t.id,
      table_number: t.table_number,
      total_amount: tableOrders.reduce((s, o) => s + o.total_amount, 0),
      order_count: tableOrders.length,
      latest_orders: tableOrders.slice(-3),
      has_new_order: tableOrders.some((o) => o.status === OrderStatus.PENDING),
    };
  });
}

export function ordersToHistory(orders: Order[]): OrderHistoryItem[] {
  const tableMap = new Map(mockTables.map((t) => [t.id, t.table_number]));
  return orders.map((o) => ({
    id: o.id,
    order_number: o.order_number,
    table_number: tableMap.get(o.table_id) ?? 0,
    status: o.status,
    total_amount: o.total_amount,
    items: o.items,
    created_at: o.created_at,
  }));
}
