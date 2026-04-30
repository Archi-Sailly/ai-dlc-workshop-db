import { useEffect, useState } from 'react';
import { useAuthStore } from '../stores/authStore';
import { useToastStore } from '../stores/toastStore';
import { getTables } from '../api/tables';
import OrderStatusBadge from '../components/OrderStatusBadge';
import type { Table, OrderHistoryItem, OrderHistoryResponse } from '../types';
import { format } from 'date-fns';
import apiClient from '../api/client';

export default function OrderHistoryPage() {
  const storeId = useAuthStore((s) => s.storeId);
  const addToast = useToastStore((s) => s.addToast);

  const [result, setResult] = useState<OrderHistoryResponse | null>(null);
  const [tables, setTables] = useState<Table[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filters, setFilters] = useState({ table_number: undefined as number | undefined, date_from: '', date_to: '', page: 1, size: 20 });

  useEffect(() => { if (storeId) getTables(storeId).then(setTables); }, [storeId]);

  useEffect(() => {
    if (!storeId) return;
    setIsLoading(true);
    apiClient.get<OrderHistoryResponse>(`/api/admin/stores/${storeId}/orders/history`, {
      params: { table_number: filters.table_number, date_from: filters.date_from || undefined, date_to: filters.date_to || undefined, page: filters.page, size: filters.size },
    })
      .then(({ data }) => setResult(data))
      .catch(() => addToast({ type: 'error', message: '주문 내역을 불러올 수 없습니다.' }))
      .finally(() => setIsLoading(false));
  }, [storeId, filters, addToast]);

  return (
    <div>
      <h2 className="mb-4 text-xl font-bold text-gray-900 dark:text-white">주문 내역</h2>
      <div className="mb-4 flex flex-wrap items-center gap-3 rounded-xl border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-800">
        <select value={filters.table_number ?? ''} onChange={(e) => setFilters({ ...filters, table_number: e.target.value ? Number(e.target.value) : undefined, page: 1 })} className="rounded-lg border border-gray-300 px-3 py-2 text-sm dark:border-gray-600 dark:bg-gray-700 dark:text-white">
          <option value="">전체 테이블</option>
          {tables.map((t) => <option key={t.id} value={t.table_number}>테이블 {t.table_number}</option>)}
        </select>
        <input type="date" value={filters.date_from} onChange={(e) => setFilters({ ...filters, date_from: e.target.value, page: 1 })} className="rounded-lg border border-gray-300 px-3 py-2 text-sm dark:border-gray-600 dark:bg-gray-700 dark:text-white" />
        <span className="text-gray-400">~</span>
        <input type="date" value={filters.date_to} onChange={(e) => setFilters({ ...filters, date_to: e.target.value, page: 1 })} className="rounded-lg border border-gray-300 px-3 py-2 text-sm dark:border-gray-600 dark:bg-gray-700 dark:text-white" />
        <button onClick={() => setFilters({ table_number: undefined, date_from: '', date_to: '', page: 1, size: 20 })} className="text-sm text-blue-600 hover:underline dark:text-blue-400">초기화</button>
      </div>

      {isLoading ? (
        <div className="flex h-32 items-center justify-center"><div className="h-10 w-10 animate-spin rounded-full border-4 border-blue-500 border-t-transparent" /></div>
      ) : (
        <>
          <div className="space-y-3">
            {result?.orders.map((order: OrderHistoryItem) => (
              <div key={order.id} className="rounded-xl border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-800">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium text-gray-500">#{order.order_number}</span>
                    <span className="rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-600 dark:bg-gray-700 dark:text-gray-400">테이블 {order.table_number}</span>
                    <span className="text-xs text-gray-400">{format(new Date(order.created_at), 'yyyy-MM-dd HH:mm')}</span>
                  </div>
                  <OrderStatusBadge status={order.status} />
                </div>
                <div className="mt-2 space-y-1">
                  {order.items.map((item) => (
                    <div key={item.id} className="flex justify-between text-sm">
                      <span className="text-gray-700 dark:text-gray-300">{item.menu_name} × {item.quantity}</span>
                      <span className="text-gray-500">₩{item.subtotal.toLocaleString()}</span>
                    </div>
                  ))}
                </div>
                <div className="mt-2 text-right font-bold text-gray-900 dark:text-white">₩{order.total_amount.toLocaleString()}</div>
              </div>
            ))}
            {result?.orders.length === 0 && <p className="py-8 text-center text-gray-500">주문 내역이 없습니다.</p>}
          </div>
          {result && result.total_pages > 1 && (
            <div className="mt-4 flex items-center justify-center gap-2">
              <button onClick={() => setFilters({ ...filters, page: filters.page - 1 })} disabled={filters.page <= 1} className="rounded-lg border border-gray-300 px-3 py-1.5 text-sm disabled:opacity-30 dark:border-gray-600 dark:text-gray-300">이전</button>
              <span className="text-sm text-gray-600 dark:text-gray-400">{filters.page} / {result.total_pages} (총 {result.total}건)</span>
              <button onClick={() => setFilters({ ...filters, page: filters.page + 1 })} disabled={filters.page >= result.total_pages} className="rounded-lg border border-gray-300 px-3 py-1.5 text-sm disabled:opacity-30 dark:border-gray-600 dark:text-gray-300">다음</button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
