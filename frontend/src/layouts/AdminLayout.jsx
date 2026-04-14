import { NavLink, Outlet, useNavigate } from 'react-router-dom';

const NAV_ITEMS = [
  { to: '/admin', label: 'Dashboard', icon: '📊' },
  { to: '/admin/users', label: 'Quản lý Nhân sự', icon: '👥' },
  { to: '/admin/savings-products', label: 'Gói Tiết kiệm', icon: '💰' },
  { to: '/admin/configs', label: 'Tham số Hệ thống', icon: '⚙️' },
];

export default function AdminLayout() {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    navigate('/login');
  };

  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      {/* Sidebar */}
      <aside style={{
        width: 250,
        background: '#1a1a2e',
        color: '#fff',
        display: 'flex',
        flexDirection: 'column',
      }}>
        <div style={{
          padding: '24px 20px',
          borderBottom: '1px solid rgba(255,255,255,0.1)',
          textAlign: 'center',
        }}>
          <h2 style={{ margin: 0, fontSize: 20, fontWeight: 700 }}>Smart Savings</h2>
          <span style={{ fontSize: 12, opacity: 0.7 }}>Admin Panel</span>
        </div>

        <nav style={{ flex: 1, padding: '12px 0' }}>
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/admin'}
              style={({ isActive }) => ({
                display: 'flex',
                alignItems: 'center',
                gap: 12,
                padding: '12px 20px',
                color: isActive ? '#fff' : 'rgba(255,255,255,0.6)',
                background: isActive ? 'rgba(255,255,255,0.1)' : 'transparent',
                textDecoration: 'none',
                fontSize: 14,
                borderLeft: isActive ? '3px solid #4fc3f7' : '3px solid transparent',
                transition: 'all 0.2s',
              })}
            >
              <span>{item.icon}</span>
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>

        <button
          onClick={handleLogout}
          style={{
            margin: '12px 20px 20px',
            padding: '10px',
            background: 'rgba(255,255,255,0.1)',
            color: '#fff',
            border: '1px solid rgba(255,255,255,0.2)',
            borderRadius: 6,
            cursor: 'pointer',
            fontSize: 14,
          }}
        >
          Đăng xuất
        </button>
      </aside>

      {/* Main content */}
      <main style={{ flex: 1, background: '#f0f2f5', overflow: 'auto' }}>
        <div style={{ padding: 24 }}>
          <Outlet />
        </div>
      </main>
    </div>
  );
}
