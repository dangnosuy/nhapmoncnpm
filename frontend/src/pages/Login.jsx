import { useEffect, useState } from 'react';
import api from '../api/axios';

const ROLE_HOME = { ADMIN: '/admin', STAFF: '/staff/', CUSTOMER: '/client/' };

function goToRoleHome(role) {
  const target = ROLE_HOME[role] || '/login';
  window.location.assign(target);
}

export default function Login() {
  const [mode, setMode] = useState('login');
  const [toast, setToast] = useState(null);
  const [loading, setLoading] = useState(false);
  const [loginForm, setLoginForm] = useState({ email: '', password: '' });
  const [registerForm, setRegisterForm] = useState({
    full_name: '',
    identity_card: '',
    email: '',
    password: '',
    confirm_password: '',
  });

  useEffect(() => {
    const flash = sessionStorage.getItem('flash_message');
    if (flash) {
      setToast({ type: 'error', message: flash });
      sessionStorage.removeItem('flash_message');
    }
  }, []);

  const showToast = (type, message) => {
    setToast({ type, message });
    window.setTimeout(() => setToast(null), 3200);
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const res = await api.post('/auth/login', loginForm);
      const { token, role, message } = res.data;
      localStorage.setItem('token', token);
      localStorage.setItem('role', role);
      localStorage.setItem('username', loginForm.email);
      localStorage.setItem(`${role.toLowerCase()}_token`, token);
      showToast('success', message || 'Đăng nhập thành công.');
      window.setTimeout(() => goToRoleHome(role), 450);
    } catch (err) {
      showToast('error', err.response?.data?.message || 'Đăng nhập thất bại!');
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    if (registerForm.password !== registerForm.confirm_password) {
      showToast('error', 'Mật khẩu xác nhận không khớp.');
      return;
    }

    setLoading(true);
    try {
      const res = await api.post('/auth/register', {
        email: registerForm.email,
        password: registerForm.password,
        full_name: registerForm.full_name,
        identity_card: registerForm.identity_card,
      });
      showToast('success', res.data.message || 'Đăng ký thành công.');
      setLoginForm({ email: registerForm.email, password: '' });
      setRegisterForm({ full_name: '', identity_card: '', email: '', password: '', confirm_password: '' });
      setMode('login');
    } catch (err) {
      showToast('error', err.response?.data?.message || 'Đăng ký thất bại!');
    } finally {
      setLoading(false);
    }
  };

  const updateLogin = (field, value) => setLoginForm((prev) => ({ ...prev, [field]: value }));
  const updateRegister = (field, value) => setRegisterForm((prev) => ({ ...prev, [field]: value }));

  return (
    <div className="ds-login">
      {toast && (
        <div className={`ds-toast ${toast.type === 'success' ? 'success' : 'error'}`} role="status">
          {toast.message}
        </div>
      )}

      <section className="ds-login-hero">
        <p className="ds-kicker" style={{ color: '#111827', marginBottom: 14 }}>QUẢN LÝ SỔ TIẾT KIỆM</p>
        <h1>Nền tảng tiết kiệm số.</h1>
        <p>
          Một cổng đăng nhập cho khách hàng, nhân viên và quản trị viên. Hệ thống tự mở đúng phân hệ theo vai trò tài khoản.
        </p>
        <div className="ds-login-strip">
          <span>RESTful API</span>
          <span>Role-based access</span>
          <span>10.000.000 VND welcome bonus</span>
        </div>
      </section>

      <section className="ds-login-panel">
        <div className="ds-card ds-login-card">
          <div className="ds-login-tabs" role="tablist" aria-label="Auth mode">
            <button
              type="button"
              className={mode === 'login' ? 'active' : ''}
              onClick={() => setMode('login')}
            >
              Đăng nhập
            </button>
            <button
              type="button"
              className={mode === 'register' ? 'active' : ''}
              onClick={() => setMode('register')}
            >
              Đăng ký khách hàng
            </button>
          </div>

          {mode === 'login' ? (
            <form onSubmit={handleLogin}>
              <h2>Đăng nhập</h2>
              <p className="ds-kicker">ADMIN, STAFF hoặc CUSTOMER</p>

              <div className="ds-field">
                <label>Email</label>
                <input
                  type="email"
                  value={loginForm.email}
                  onChange={(e) => updateLogin('email', e.target.value)}
                  required
                  placeholder="email@example.com"
                />
              </div>

              <div className="ds-field">
                <label>Mật khẩu</label>
                <input
                  type="password"
                  value={loginForm.password}
                  onChange={(e) => updateLogin('password', e.target.value)}
                  required
                  placeholder="Nhập mật khẩu"
                />
              </div>

              <button className="ds-btn ds-btn-primary" type="submit" disabled={loading} style={{ width: '100%', marginTop: 22 }}>
                {loading ? 'Đang xử lý' : 'Đăng nhập'}
              </button>
            </form>
          ) : (
            <form onSubmit={handleRegister}>
              <h2>Tạo tài khoản</h2>
              <p className="ds-kicker">Khách hàng mới được tặng 10.000.000 VND</p>

              <div className="ds-field">
                <label>Họ và tên</label>
                <input value={registerForm.full_name} onChange={(e) => updateRegister('full_name', e.target.value)} required />
              </div>
              <div className="ds-field">
                <label>CMND/CCCD</label>
                <input value={registerForm.identity_card} onChange={(e) => updateRegister('identity_card', e.target.value)} required />
              </div>
              <div className="ds-field">
                <label>Email</label>
                <input type="email" value={registerForm.email} onChange={(e) => updateRegister('email', e.target.value)} required />
              </div>
              <div className="ds-field ds-field-pair">
                <div>
                  <label>Mật khẩu</label>
                  <input type="password" value={registerForm.password} onChange={(e) => updateRegister('password', e.target.value)} required />
                </div>
                <div>
                  <label>Xác nhận</label>
                  <input type="password" value={registerForm.confirm_password} onChange={(e) => updateRegister('confirm_password', e.target.value)} required />
                </div>
              </div>

              <button className="ds-btn ds-btn-primary" type="submit" disabled={loading} style={{ width: '100%', marginTop: 22 }}>
                {loading ? 'Đang tạo tài khoản' : 'Đăng ký'}
              </button>
            </form>
          )}
        </div>
      </section>
    </div>
  );
}
