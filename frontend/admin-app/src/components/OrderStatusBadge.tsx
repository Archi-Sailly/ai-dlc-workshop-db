import { OrderStatus } from '../types';

const statusConfig: Record<OrderStatus, { label: string; className: string }> = {
  [OrderStatus.PENDING]: { label: '대기중', className: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400' },
  [OrderStatus.ACCEPTED]: { label: '접수', className: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400' },
  [OrderStatus.PREPARING]: { label: '준비중', className: 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400' },
  [OrderStatus.COMPLETED]: { label: '완료', className: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400' },
};

export default function OrderStatusBadge({ status }: { status: OrderStatus }) {
  const config = statusConfig[status];
  return (
    <span className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-medium ${config.className}`}>
      {config.label}
    </span>
  );
}
