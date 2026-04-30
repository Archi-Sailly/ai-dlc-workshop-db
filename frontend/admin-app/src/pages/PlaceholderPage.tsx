import { useLocation } from 'react-router-dom';

export default function PlaceholderPage() {
  const location = useLocation();

  const pageNames: Record<string, string> = {
    '/tables': '테이블 관리',
    '/menus': '메뉴 관리',
    '/orders/history': '주문 내역',
  };

  const name = pageNames[location.pathname] ?? location.pathname;

  return (
    <div className="flex h-64 items-center justify-center">
      <div className="text-center">
        <h2 className="text-xl font-bold text-gray-900 dark:text-white">{name}</h2>
        <p className="mt-2 text-gray-500">이 페이지는 준비 중입니다.</p>
      </div>
    </div>
  );
}
