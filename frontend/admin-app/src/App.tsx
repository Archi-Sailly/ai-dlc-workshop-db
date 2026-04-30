import { Routes, Route, Navigate } from 'react-router-dom';
import { useEffect } from 'react';
import { useAuthStore } from './stores/authStore';
import ProtectedRoute from './components/ProtectedRoute';
import AppLayout from './components/AppLayout';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import TableDetailPage from './pages/TableDetailPage';
import TableManagePage from './pages/TableManagePage';
import MenuManagePage from './pages/MenuManagePage';
import MenuFormPage from './pages/MenuFormPage';
import OrderHistoryPage from './pages/OrderHistoryPage';

export default function App() {
  const initAuth = useAuthStore((s) => s.initAuth);

  useEffect(() => {
    initAuth();
  }, [initAuth]);

  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        element={
          <ProtectedRoute>
            <AppLayout />
          </ProtectedRoute>
        }
      >
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/dashboard/table/:tableNumber" element={<TableDetailPage />} />
        <Route path="/tables" element={<TableManagePage />} />
        <Route path="/menus" element={<MenuManagePage />} />
        <Route path="/menus/new" element={<MenuFormPage />} />
        <Route path="/menus/:menuId/edit" element={<MenuFormPage />} />
        <Route path="/orders/history" element={<OrderHistoryPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}
