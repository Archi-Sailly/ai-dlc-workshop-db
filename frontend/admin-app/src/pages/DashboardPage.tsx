import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';
import { useDashboardStore } from '../stores/dashboardStore';
import { OrderStatus } from '../types';

export default function DashboardPage() {
  const navigate = useNavigate();
  const storeId = useAuthStore((s) => s.storeId);
  const { tables, isLoading, error, fetchDashboard, pulsingTables } = useDashboardStore();

  useEffect(() => {
    if (storeId) fetchDashboard(storeId);
  }, [storeId, fetchDashboard]);

  if (isLoading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-blue-500 border-t-transparent" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex h-64 flex-col items-center justify-center gap-3">
        <p className="text-red-500">{error}</p>
        <button onClick={() => storeId && fetchDashboard(storeId)} className="rounded-lg bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700">재시도</button>
      </div>
    );
  }

  return (
    <div>
      <h2 className="mb-4 text-xl font-bold text-gray-900 dark:text-white">주문 대시보드</h2>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        {tables.map((table) => {
          const isPulsing = pulsingTables.has(table.table_number);
          const pendingCount = table.latest_orders.filter((o) => o.status === OrderStatus.PENDING).length;

          return (
            <button
              key={table.table_number}
              onClick={() => navigate(`/dashboard/table/${table.table_number}`)}
              className={`relative rounded-xl border p-4 text-left shadow-sm transition-all hover:shadow-md dark:border-gray-700 dark:bg-gray-800 ${
                isPulsing ? 'animate-pulse border-orange-400 bg-orange-50 dark:bg-orange-900/20' : 'border-gray-200 bg-white'
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="text-lg font-bold text-gray-900 dark:text-white">테이블 {table.table_number}</span>
                {pendingCount > 0 && (
                  <span className="rounded-full bg-red-500 px-2 py-0.5 text-xs font-medium text-white">{pendingCount}</span>
                )}
              </div>
              <p className="mt-2 text-2xl font-bold text-blue-600 dark:text-blue-400">₩{table.total_amount.toLocaleString()}</p>
              {table.latest_orders.length > 0 ? (
                <p className="mt-1 truncate text-sm text-gray-500 dark:text-gray-400">
                  {table.latest_orders[table.latest_orders.length - 1]?.items.slice(0, 2).map((i) => i.menu_name).join(', ')}
                </p>
              ) : (
                <p className="mt-1 text-sm text-gray-400">주문 없음</p>
              )}
              <p className="mt-2 text-xs text-gray-400">주문 {table.order_count}건</p>
            </button>
          );
        })}
      </div>
      {tables.length === 0 && <p className="mt-8 text-center text-gray-500">등록된 테이블이 없습니다.</p>}
    </div>
  );
}
