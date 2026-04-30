import { useEffect, useState } from 'react';
import { useAuthStore } from '../stores/authStore';
import { useDashboardStore } from '../stores/dashboardStore';
import { useToastStore } from '../stores/toastStore';
import { getTables, createTable, completeSession } from '../api/tables';
import ConfirmDialog from '../components/ConfirmDialog';
import type { Table } from '../types';

export default function TableManagePage() {
  const storeId = useAuthStore((s) => s.storeId);
  const resetTable = useDashboardStore((s) => s.resetTable);
  const dashboardTables = useDashboardStore((s) => s.tables);
  const addToast = useToastStore((s) => s.addToast);

  const [tables, setTables] = useState<Table[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [newNumber, setNewNumber] = useState('');
  const [formError, setFormError] = useState('');
  const [completeTarget, setCompleteTarget] = useState<number | null>(null);

  useEffect(() => {
    if (!storeId) return;
    setIsLoading(true);
    getTables(storeId).then(setTables).finally(() => setIsLoading(false));
  }, [storeId]);

  const handleAdd = async () => {
    if (!storeId) return;
    const num = parseInt(newNumber, 10);
    if (!num || num <= 0) { setFormError('유효한 테이블 번호를 입력해주세요.'); return; }
    try {
      const table = await createTable(storeId, num);
      setTables((prev) => [...prev, table].sort((a, b) => a.table_number - b.table_number));
      setNewNumber(''); setShowForm(false); setFormError('');
      addToast({ type: 'success', message: `테이블 ${num}번이 등록되었습니다.` });
    } catch (err: unknown) {
      const status = (err as { response?: { status?: number } }).response?.status;
      setFormError(status === 409 ? '이미 등록된 테이블 번호입니다.' : '테이블 등록에 실패했습니다.');
    }
  };

  const handleComplete = async () => {
    if (!storeId || completeTarget == null) return;
    try {
      await completeSession(storeId, completeTarget);
      resetTable(completeTarget);
      addToast({ type: 'success', message: `테이블 ${completeTarget}번 이용이 완료되었습니다.` });
    } catch { addToast({ type: 'error', message: '이용 완료 처리에 실패했습니다.' }); }
    setCompleteTarget(null);
  };

  const getIncompleteCount = (tableNumber: number) => {
    const dt = dashboardTables.find((t) => t.table_number === tableNumber);
    return dt?.latest_orders.filter((o) => o.status !== 'COMPLETED').length ?? 0;
  };

  const hasActiveSession = (tableNumber: number) => {
    const dt = dashboardTables.find((t) => t.table_number === tableNumber);
    return (dt?.order_count ?? 0) > 0;
  };

  if (isLoading) {
    return <div className="flex h-64 items-center justify-center"><div className="h-10 w-10 animate-spin rounded-full border-4 border-blue-500 border-t-transparent" /></div>;
  }

  const incompleteCount = completeTarget != null ? getIncompleteCount(completeTarget) : 0;

  return (
    <div>
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-xl font-bold text-gray-900 dark:text-white">테이블 관리</h2>
        <button onClick={() => setShowForm(!showForm)} className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700">+ 테이블 추가</button>
      </div>
      {showForm && (
        <div className="mb-4 flex items-center gap-2 rounded-xl border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-800">
          <input type="number" value={newNumber} onChange={(e) => { setNewNumber(e.target.value); setFormError(''); }} placeholder="테이블 번호" min={1} className="w-32 rounded-lg border border-gray-300 px-3 py-2 text-sm dark:border-gray-600 dark:bg-gray-700 dark:text-white" />
          <button onClick={handleAdd} className="rounded-lg bg-green-600 px-4 py-2 text-sm text-white hover:bg-green-700">등록</button>
          {formError && <span className="text-sm text-red-500">{formError}</span>}
        </div>
      )}
      <div className="space-y-2">
        {tables.map((table) => (
          <div key={table.id} className="flex items-center justify-between rounded-xl border border-gray-200 bg-white px-4 py-3 dark:border-gray-700 dark:bg-gray-800">
            <div>
              <span className="font-bold text-gray-900 dark:text-white">테이블 {table.table_number}번</span>
              {table.url && <span className="ml-3 text-xs text-gray-400">{table.url}</span>}
            </div>
            <div className="flex items-center gap-2">
              {hasActiveSession(table.table_number) ? (
                <span className="rounded-full bg-green-100 px-2 py-0.5 text-xs text-green-700 dark:bg-green-900/30 dark:text-green-400">이용 중</span>
              ) : (
                <span className="rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-500 dark:bg-gray-700 dark:text-gray-400">비어있음</span>
              )}
              <button onClick={() => setCompleteTarget(table.table_number)} disabled={!hasActiveSession(table.table_number)} className="rounded-lg border border-gray-300 px-3 py-1.5 text-xs hover:bg-gray-50 disabled:opacity-30 dark:border-gray-600 dark:text-gray-300">이용 완료</button>
            </div>
          </div>
        ))}
        {tables.length === 0 && <p className="py-8 text-center text-gray-500">등록된 테이블이 없습니다.</p>}
      </div>
      <ConfirmDialog isOpen={completeTarget != null} title="이용 완료"
        message={incompleteCount > 0 ? `미완료 주문이 ${incompleteCount}건 있습니다. 계속하시겠습니까?` : `테이블 ${completeTarget}번 이용을 완료하시겠습니까?`}
        confirmText={incompleteCount > 0 ? '계속' : '완료'} confirmVariant={incompleteCount > 0 ? 'warning' : 'primary'}
        onConfirm={handleComplete} onCancel={() => setCompleteTarget(null)} />
    </div>
  );
}
