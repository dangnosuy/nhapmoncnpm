import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import AdminLayout from './layouts/AdminLayout';
import Login from './pages/Login';
import Dashboard from './pages/admin/Dashboard';
import UserManagement from './pages/admin/UserManagement';
import SavingsProducts from './pages/admin/SavingsProducts';
import SystemConfigs from './pages/admin/SystemConfigs';
import TransactionApprovals from './pages/admin/TransactionApprovals';
import Reports from './pages/admin/Reports';

const ROLE_HOME = { ADMIN: '/admin', STAFF: '/staff/', CUSTOMER: '/client/' };

function redirectForRole(role) {
  return ROLE_HOME[role] || '/login';
}

function ProtectedRoute({ allowedRoles, children }) {
  const token = localStorage.getItem('token');
  const role = localStorage.getItem('role');
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  if (!allowedRoles.includes(role)) {
    sessionStorage.setItem('flash_message', 'Permission denied. Tài khoản không có quyền truy cập trang vừa yêu cầu.');
    const target = redirectForRole(role);
    if (target.endsWith('/')) {
      window.location.replace(target);
      return null;
    }
    return <Navigate to={target} replace />;
  }
  return children;
}

function ExternalRoleRoute({ allowedRole, target }) {
  const token = localStorage.getItem('token');
  const role = localStorage.getItem('role');

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  if (role !== allowedRole) {
    sessionStorage.setItem('flash_message', 'Permission denied. Tài khoản không có quyền truy cập trang vừa yêu cầu.');
    window.location.replace(redirectForRole(role));
    return null;
  }

  window.location.replace(target);
  return null;
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/staff" element={<ExternalRoleRoute allowedRole="STAFF" target="/staff/" />} />
        <Route path="/client" element={<ExternalRoleRoute allowedRole="CUSTOMER" target="/client/" />} />

        {/* Admin routes */}
        <Route
          path="/admin"
          element={
            <ProtectedRoute allowedRoles={['ADMIN']}>
              <AdminLayout />
            </ProtectedRoute>
          }
        >
          <Route index element={<Dashboard />} />
          <Route path="users" element={<UserManagement />} />
          <Route path="transactions" element={<TransactionApprovals />} />
          <Route path="savings-products" element={<SavingsProducts />} />
          <Route path="configs" element={<SystemConfigs />} />
          <Route path="reports" element={<Reports />} />
        </Route>

        <Route path="/" element={<Navigate to="/login" replace />} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
