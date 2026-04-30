import { Outlet } from 'react-router-dom';
import SideNav from './SideNav';
import Toast from './Toast';
import { useDashboardStore } from '../stores/dashboardStore';
import { useSSE } from '../hooks/useSSE';
import { SSEConnectionStatus } from '../types';

export default function AppLayout() {
  const sseStatus = useDashboardStore((s) => s.sseStatus);

  // SSE 연결 (백엔드 없으면 onerror로 DISCONNECTED 상태 — Mock에서는 무시)
  useSSE();

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
      <SideNav />
      <div className="md:ml-60">
        {/* SSE 연결 끊김 배너 */}
        {sseStatus === SSEConnectionStatus.DISCONNECTED && (
          <div className="bg-red-600 px-4 py-2 text-center text-sm text-white">
            실시간 연결이 끊어졌습니다.
          </div>
        )}
        {sseStatus === SSEConnectionStatus.RECONNECTING && (
          <div className="bg-yellow-500 px-4 py-2 text-center text-sm text-white">
            재연결 중...
          </div>
        )}

        <main className="p-4 md:p-6">
          <Outlet />
        </main>
      </div>
      <Toast />
    </div>
  );
}
