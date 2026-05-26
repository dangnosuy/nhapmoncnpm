import { useEffect, useState } from 'react';
import { NavLink, Outlet, useLocation, useNavigate } from 'react-router-dom';

const NAV_ITEMS = [
  { to: '/admin', label: 'Dashboard', code: 'DB' },
  { to: '/admin/users', label: 'Nhân sự', code: 'US' },
  { to: '/admin/savings-products', label: 'Gói tiết kiệm', code: 'SP' },
  { to: '/admin/configs', label: 'Tham số', code: 'CF' },
  { to: '/admin/reports', label: 'Báo cáo BM5', code: 'RP' },
];

export default function AdminLayout() {
  const navigate = useNavigate();
  const location = useLocation();
  const [toast, setToast] = useState(null);
  const [bellActive, setBellActive] = useState(false);

  useEffect(() => {
    const flash = sessionStorage.getItem('flash_message');
    if (!flash) return;
    setToast(flash);
    sessionStorage.removeItem('flash_message');
    const timer = window.setTimeout(() => setToast(null), 6000);
    return () => window.clearTimeout(timer);
  }, [location.pathname]);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) return undefined;

    let retryDelay = 3000;
    let sourceRef = { current: null };

    function connect() {
      const source = new EventSource(`/api/events?token=${encodeURIComponent(token)}`);
      sourceRef.current = source;

      source.addEventListener('ready', () => { retryDelay = 3000; });

      source.addEventListener('savings', (event) => {
        const data = JSON.parse(event.data || '{}');
        setToast(data.message || 'Có cập nhật mới từ hệ thống.');
        setBellActive(true);
        window.setTimeout(() => setBellActive(false), 1600);
        window.dispatchEvent(new CustomEvent('savings-realtime-event', { detail: data }));
      });

      source.onerror = () => {
        source.close();
        sourceRef.current = null;
        window.setTimeout(() => {
          retryDelay = Math.min(retryDelay * 2, 30000);
          connect();
        }, retryDelay);
      };
    }

    connect();

    return () => {
      sourceRef.current?.close();
    };
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    localStorage.removeItem('username');
    navigate('/login');
  };

  return (
    <div className="ds-app">
      {toast && <div className="ds-toast error" role="status">{toast}</div>}
      <aside className="ds-sidebar">
        <div className="ds-brand">
          <h1>QUẢN LÝ SỔ TIẾT KIỆM</h1>
          <span>ADMIN CONTROL ROOM</span>
        </div>

        <nav className="ds-nav" aria-label="Admin navigation">
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/admin'}
              className={({ isActive }) => `ds-nav-link${isActive ? ' active' : ''}`}
            >
              <span className="ds-sidebar-meta">{item.code}</span>
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>

        <div style={{ padding: 16 }}>
          <button
            className={`ds-btn ${bellActive ? 'ds-realtime-pulse' : ''}`}
            type="button"
            title="Thông báo realtime"
            style={{ width: '100%', marginBottom: 12 }}
          >
            !
          </button>
          <button className="ds-btn ds-btn-secondary" style={{ width: '100%' }} onClick={handleLogout}>
            Đăng xuất
          </button>
        </div>
      </aside>

      <main className="ds-main">
        <div className="ds-content">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
