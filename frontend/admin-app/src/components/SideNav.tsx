import { NavLink } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';
import { useState } from 'react';

const navItems = [
  { to: '/dashboard', label: '📊 대시보드' },
  { to: '/tables', label: '🪑 테이블 관리' },
  { to: '/menus', label: '🍽️ 메뉴 관리' },
  { to: '/orders/history', label: '📋 주문 내역' },
];

export default function SideNav() {
  const { username, logout } = useAuthStore();
  const [open, setOpen] = useState(false);

  return (
    <>
      <button
        className="fixed top-3 left-3 z-50 rounded-md bg-gray-800 p-2 text-white md:hidden"
        onClick={() => setOpen(!open)}
        aria-label="메뉴 열기"
      >
        ☰
      </button>

      {open && <div className="fixed inset-0 z-40 bg-black/50 md:hidden" onClick={() => setOpen(false)} />}

      <aside
        className={`fixed top-0 left-0 z-40 flex h-full w-60 flex-col bg-gray-900 text-white transition-transform md:translate-x-0 ${
          open ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="border-b border-gray-700 p-4">
          <h1 className="text-lg font-bold">테이블오더</h1>
          {username && <p className="mt-1 text-sm text-gray-400">{username}</p>}
        </div>

        <nav className="flex-1 space-y-1 p-3">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              onClick={() => setOpen(false)}
              className={({ isActive }) =>
                `block rounded-lg px-3 py-2.5 text-sm transition-colors ${
                  isActive ? 'bg-blue-600 text-white' : 'text-gray-300 hover:bg-gray-800'
                }`
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="border-t border-gray-700 p-3">
          <button
            onClick={logout}
            className="w-full rounded-lg px-3 py-2.5 text-left text-sm text-gray-300 hover:bg-gray-800"
          >
            🚪 로그아웃
          </button>
        </div>
      </aside>
    </>
  );
}
