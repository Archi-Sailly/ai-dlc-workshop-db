import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';
import { useDashboardStore } from '../stores/dashboardStore';
import { useToastStore } from '../stores/toastStore';
import { getTableOrders, updateOrderStatus, deleteOrder } from '../api/orders';
import OrderStatusBadge from '../components/OrderStatusBadge';
import ConfirmDialog from '../components/ConfirmDialog';
import { OrderStatus, type Order } from '../types';
import { format } from 'date-fns';

const nextStatus: Partial<Record<OrderStatus, { status: OrderStatus; label: string }>> = {
  [OrderStatus.PENDING]: { status: OrderStatus.ACCEPTED, label: '접수' },
  [OrderStatus.ACCEPTED]: { status: OrderStatus.PREPARING, label: '준비 시작' },
  [OrderStatus.PREPARING]: { status: OrderStatus.COMPLETED, label: '완료' },
};

export default function TableDetailPage() {
  const { tableNumber } = useParams<{ tableNumber: string }>();
  const navigate = useNavigate();
  const storeId = useAuthStore((s) => s.storeId);
  const dashboardUpdate = useDashboardStore((s) => s.updateOrderStatus);
  const dashboardRemove = useDashboardStore((s) => s.removeOrder);
  const addToast = useToastStore((s) => s.addToast);

  const [orders, setOrders] = useState<Order[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [confirmDialog, setConfirmDialog] = useState<{ type: 'complete' | 'delete'; orderId: string } | null>(null);

  const tableNum = Number(tableNumber);

  useEffect(() => {
    if (!storeId || !tableNumber) return;
    setIsLoading(true);
    getTableOrders(storeId, tableNum)
      .then(setOrders)
      .catch(() => addToast({ type: 'error', message: '주문 목록을 불러올 수 없습니다.' }))
      .finally(() => setIsLoading(false));
  }, [storeId, tableNumber, tableNum, addToast]);

  const doStatusChange = async (orderId: string, newStatus: OrderStatus) => {
    if (!storeId) return;
    const prev = orders.find((o) => o.id === orderId)?.status;
    setOrders((list) => list.map((o) => (o.id === orderId ? { ...o, status: newStatus } : o)));
    try {
      await updateOrderStatus(storeId, orderId, newStatus);
      dashboardUpdate(orderId, newStatus);
      addToast({ type: 'success', message: '주문 상태가 변경되었습니다.' });
    } catch {
      setOrders((list) => list.map((o) => (o.id === orderId ? { ...o, status: prev! } : o)));
      addToast({ type: 'error', message: '상태 변경에 실패했습니다.' });
    }
  };

  const handleStatusChange = (orderId: string, newStatus: OrderStatus) => {
    if (newStatus === OrderStatus.COMPLETED) {
      setConfirmDialog({ type: 'complete', orderId });
    } else {
      doStatusChange(orderId, newStatus);
    }
  };

  const handleDelete = async (reason?: string) => {
    if (!storeId || !confirmDialog) return;
    const orderId = confirmDialog.orderId;
    try {
      await deleteOrder(storeId, orderId, reason);
      setOrders((prev) => prev.filter((o) => o.id !== orderId));
      dashboardRemove(orderId, tableNum);
      addToast({ type: 'success', message: '주문이 삭제되었습니다.' });
    } catch {
      addToast({ type: 'error', message: '주문 삭제에 실패했습니다.' });
    }
    setConfirmDialog(null);
  };

  const totalAmount = orders.reduce((sum, o) => sum + o.total_amount, 0);

  if (isLoading) {
    return <div className="flex h-64 items-center justify-center"><div className="h-10 w-10 animate-spin rounded-full border-4 border-blue-500 border-t-transparent" /></div>;
  }

  return (
    <div>
      <div className="mb-4 flex items-center gap-3">
        <button onClick={() => navigate('/dashboard')} className="rounded-lg border border-gray-300 px-3 py-2 text-sm hover:bg-gray-50 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-700">← 뒤로</button>
        <h2 className="text-xl font-bold text-gray-900 dark:text-white">테이블 {tableNum}번</h2>
        <span className="text-lg font-bold text-blue-600 dark:text-blue-400">₩{totalAmount.toLocaleString()}</span>
      </div>

      <div className="space-y-3">
        {orders.map((order) => {
          const next = nextStatus[order.status];
          const canDelete = order.status === OrderStatus.PENDING || order.status === OrderStatus.ACCEPTED;
          return (
            <div key={order.id} className="rounded-xl border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-800">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium text-gray-500">#{order.order_number}</span>
                  <span className="text-xs text-gray-400">{format(new Date(order.created_at), 'HH:mm')}</span>
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
              <div className="mt-3 flex items-center justify-between border-t border-gray-100 pt-3 dark:border-gray-700">
                <span className="font-bold text-gray-900 dark:text-white">₩{order.total_amount.toLocaleString()}</span>
                <div className="flex gap-2">
                  {canDelete && (
                    <button onClick={() => setConfirmDialog({ type: 'delete', orderId: order.id })} className="rounded-lg border border-red-300 px-3 py-1.5 text-xs text-red-600 hover:bg-red-50 dark:border-red-700 dark:text-red-400">삭제</button>
                  )}
                  {next && (
                    <button onClick={() => handleStatusChange(order.id, next.status)} className="rounded-lg bg-blue-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-blue-700">{next.label}</button>
                  )}
                </div>
              </div>
            </div>
          );
        })}
        {orders.length === 0 && <p className="py-8 text-center text-gray-500">주문이 없습니다.</p>}
      </div>

      <ConfirmDialog isOpen={confirmDialog?.type === 'complete'} title="주문 완료" message="이 주문을 완료 처리하시겠습니까?" confirmText="완료"
        onConfirm={() => { if (confirmDialog) doStatusChange(confirmDialog.orderId, OrderStatus.COMPLETED); setConfirmDialog(null); }}
        onCancel={() => setConfirmDialog(null)} />
      <ConfirmDialog isOpen={confirmDialog?.type === 'delete'} title="주문 삭제" message="이 주문을 삭제하시겠습니까?" confirmText="삭제" confirmVariant="danger" showReasonInput
        onConfirm={handleDelete} onCancel={() => setConfirmDialog(null)} />
    </div>
  );
}
