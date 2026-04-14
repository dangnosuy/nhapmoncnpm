import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import AdminLayout from './layouts/AdminLayout';
import Login from './pages/Login';
import Dashboard from './pages/admin/Dashboard';
import UserManagement from './pages/admin/UserManagement';
import SavingsProducts from './pages/admin/SavingsProducts';
import SystemConfigs from './pages/admin/SystemConfigs';

function ProtectedRoute({ allowedRoles, children }) {
  const token = localStorage.getItem('token');
  const role = localStorage.getItem('role');
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  if (!allowedRoles.includes(role)) {
    const redirectMap = { ADMIN: '/admin', STAFF: '/staff', CUSTOMER: '/user' };
    return <Navigate to={redirectMap[role] || '/login'} replace />;
  }
  return children;
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />

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
          <Route path="savings-products" element={<SavingsProducts />} />
          <Route path="configs" element={<SystemConfigs />} />
        </Route>

        {/* Staff routes - placeholder */}
        {/* <Route path="/staff" element={<ProtectedRoute allowedRoles={['STAFF']}><StaffLayout /></ProtectedRoute>}>
          ...
        </Route> */}

        {/* User routes - placeholder */}
        {/* <Route path="/user" element={<ProtectedRoute allowedRoles={['CUSTOMER']}><UserLayout /></ProtectedRoute>}>
          ...
        </Route> */}

        <Route path="/" element={<Navigate to="/login" replace />} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
