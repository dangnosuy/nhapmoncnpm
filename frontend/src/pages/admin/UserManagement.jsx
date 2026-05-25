import { useState, useEffect, useCallback } from 'react';
import api from '../../api/axios';

const inputStyle = {
  padding: '8px 12px',
  border: '1px solid #d9d9d9',
  borderRadius: 6,
  fontSize: 14,
  boxSizing: 'border-box',
};

const btnStyle = (bg) => ({
  padding: '6px 14px',
  background: bg,
  color: '#fff',
  border: 'none',
  borderRadius: 6,
  cursor: 'pointer',
  fontSize: 13,
});

export default function UserManagement() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({ role: '', status: '', search: '' });
  const [showCreate, setShowCreate] = useState(false);
  const [detailUser, setDetailUser] = useState(null);
  const [form, setForm] = useState({ email: '', password: '', full_name: '', identity_card: '', role: 'STAFF' });
  const [msg, setMsg] = useState('');

  const fetchUsers = useCallback(() => {
    setLoading(true);
    const params = {};
    if (filters.role) params.role = filters.role;
    if (filters.status) params.status = filters.status;
    if (filters.search) params.search = filters.search;

    api.get('/admin/users', { params })
      .then((res) => setUsers(res.data.users))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [filters]);

  useEffect(() => { fetchUsers(); }, [fetchUsers]);

  const handleCreate = async (e) => {
    e.preventDefault();
    setMsg('');
    try {
      await api.post('/admin/users', form);
      setMsg('Tạo tài khoản thành công!');
      setForm({ email: '', password: '', full_name: '', identity_card: '', role: 'STAFF' });
      setShowCreate(false);
      fetchUsers();
    } catch (err) {
      setMsg(err.response?.data?.message || 'Lỗi!');
    }
  };

  const handleChangeRole = async (userId, newRole) => {
    setMsg('');
    try {
      await api.patch(`/admin/users/${userId}`, { role: newRole });
      setMsg('Cập nhật vai trò thành công!');
      fetchUsers();
    } catch (err) {
      setMsg(err.response?.data?.message || 'Lỗi!');
    }
  };

  const handleToggleStatus = async (userId, newStatus) => {
    setMsg('');
    try {
      await api.patch(`/admin/users/${userId}`, { status: newStatus });
      setMsg('Cập nhật trạng thái thành công!');
      fetchUsers();
    } catch (err) {
      setMsg(err.response?.data?.message || 'Lỗi!');
    }
  };

  const handleViewDetail = async (userId) => {
    setMsg('');
    try {
      const res = await api.get(`/admin/users/${userId}`);
      setDetailUser(res.data.user);
    } catch {
      setMsg('Không thể tải thông tin chi tiết!');
    }
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <h2 style={{ margin: 0 }}>Quản lý Nhân sự</h2>
        <button onClick={() => setShowCreate(!showCreate)} style={btnStyle('#1890ff')}>
          {showCreate ? 'Đóng' : '+ Tạo tài khoản'}
        </button>
      </div>

      {msg && (
        <div style={{
          padding: '8px 12px',
          marginBottom: 12,
          borderRadius: 6,
          background: msg.includes('thành công') ? '#f6ffed' : '#fff2f0',
          border: msg.includes('thành công') ? '1px solid #b7eb8f' : '1px solid #ffccc7',
          color: msg.includes('thành công') ? '#389e0d' : '#cf1322',
          fontSize: 14,
        }}>
          {msg}
        </div>
      )}

      {/* Create form */}
      {showCreate && (
        <form onSubmit={handleCreate} style={{
          background: '#fff', padding: 20, borderRadius: 10, marginBottom: 16,
          boxShadow: '0 1px 3px rgba(0,0,0,0.08)',
          display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12,
        }}>
          <input style={inputStyle} placeholder="Email *" type="email" required
            value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
          <input style={inputStyle} placeholder="Mật khẩu *" type="password" required
            value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
          <input style={inputStyle} placeholder="Họ tên *" required
            value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} />
          <input style={inputStyle} placeholder="CMND/CCCD"
            value={form.identity_card} onChange={(e) => setForm({ ...form, identity_card: e.target.value })} />
          <select style={inputStyle} value={form.role}
            onChange={(e) => setForm({ ...form, role: e.target.value })}>
            <option value="STAFF">STAFF</option>
            <option value="ADMIN">ADMIN</option>
            <option value="CUSTOMER">CUSTOMER</option>
          </select>
          <button type="submit" style={btnStyle('#52c41a')}>Tạo</button>
        </form>
      )}

      {/* Filters */}
      <div style={{ display: 'flex', gap: 12, marginBottom: 16 }}>
        <select style={inputStyle} value={filters.role}
          onChange={(e) => setFilters({ ...filters, role: e.target.value })}>
          <option value="">Tất cả Role</option>
          <option value="CUSTOMER">CUSTOMER</option>
          <option value="STAFF">STAFF</option>
          <option value="ADMIN">ADMIN</option>
        </select>
        <select style={inputStyle} value={filters.status}
          onChange={(e) => setFilters({ ...filters, status: e.target.value })}>
          <option value="">Tất cả Status</option>
          <option value="ACTIVE">ACTIVE</option>
          <option value="LOCKED">LOCKED</option>
        </select>
        <input style={{ ...inputStyle, flex: 1 }} placeholder="Tìm kiếm (tên, email, CMND)..."
          value={filters.search} onChange={(e) => setFilters({ ...filters, search: e.target.value })} />
      </div>

      {/* Table */}
      <div style={{ background: '#fff', borderRadius: 10, overflow: 'hidden', boxShadow: '0 1px 3px rgba(0,0,0,0.08)' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 14 }}>
          <thead>
            <tr style={{ background: '#fafafa', textAlign: 'left' }}>
              <th style={{ padding: '12px 16px' }}>ID</th>
              <th style={{ padding: '12px 16px' }}>Họ tên</th>
              <th style={{ padding: '12px 16px' }}>Email</th>
              <th style={{ padding: '12px 16px' }}>CMND</th>
              <th style={{ padding: '12px 16px' }}>Role</th>
              <th style={{ padding: '12px 16px' }}>Status</th>
              <th style={{ padding: '12px 16px' }}>Hành động</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={7} style={{ padding: 20, textAlign: 'center' }}>Đang tải...</td></tr>
            ) : users.length === 0 ? (
              <tr><td colSpan={7} style={{ padding: 20, textAlign: 'center', color: '#999' }}>Không có dữ liệu</td></tr>
            ) : users.map((u) => (
              <tr key={u.user_id} style={{ borderTop: '1px solid #f0f0f0' }}>
                <td style={{ padding: '10px 16px' }}>{u.user_id}</td>
                <td style={{ padding: '10px 16px' }}>{u.full_name}</td>
                <td style={{ padding: '10px 16px' }}>{u.email}</td>
                <td style={{ padding: '10px 16px' }}>{u.identity_card || '—'}</td>
                <td style={{ padding: '10px 16px' }}>
                  <select value={u.role} style={{ ...inputStyle, padding: '4px 8px', fontSize: 12 }}
                    onChange={(e) => handleChangeRole(u.user_id, e.target.value)}>
                    <option value="CUSTOMER">CUSTOMER</option>
                    <option value="STAFF">STAFF</option>
                    <option value="ADMIN">ADMIN</option>
                  </select>
                </td>
                <td style={{ padding: '10px 16px' }}>
                  <span style={{
                    padding: '2px 10px',
                    borderRadius: 10,
                    fontSize: 12,
                    fontWeight: 600,
                    background: u.status === 'ACTIVE' ? '#f6ffed' : '#fff2f0',
                    color: u.status === 'ACTIVE' ? '#389e0d' : '#cf1322',
                  }}>
                    {u.status}
                  </span>
                </td>
                <td style={{ padding: '10px 16px' }}>
                  <div style={{ display: 'flex', gap: 6 }}>
                    <button style={btnStyle('#1890ff')} onClick={() => handleViewDetail(u.user_id)}>
                      Chi tiết
                    </button>
                    <button
                      style={btnStyle(u.status === 'ACTIVE' ? '#f5222d' : '#52c41a')}
                      onClick={() => handleToggleStatus(u.user_id, u.status === 'ACTIVE' ? 'LOCKED' : 'ACTIVE')}
                    >
                      {u.status === 'ACTIVE' ? 'Khóa' : 'Mở khóa'}
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Detail Modal */}
      {detailUser && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center',
          zIndex: 1000,
        }}
          onClick={() => setDetailUser(null)}
        >
          <div style={{
            background: '#fff', borderRadius: 12, padding: 24, width: 500, maxHeight: '80vh', overflow: 'auto',
          }}
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
              <h3 style={{ margin: 0 }}>Chi tiết người dùng</h3>
              <button onClick={() => setDetailUser(null)} style={{ background: 'none', border: 'none', fontSize: 20, cursor: 'pointer' }}>✕</button>
            </div>
            <table style={{ width: '100%', fontSize: 14 }}>
              <tbody>
                {[
                  ['ID', detailUser.user_id],
                  ['Họ tên', detailUser.full_name],
                  ['Email', detailUser.email],
                  ['CMND/CCCD', detailUser.identity_card || '—'],
                  ['Role', detailUser.role],
                  ['Số dư ví', Number(detailUser.wallet_balance).toLocaleString('vi-VN') + ' VND'],
                  ['Trạng thái', detailUser.status],
                  ['Ngày tạo', detailUser.created_at],
                ].map(([k, v]) => (
                  <tr key={k}><td style={{ padding: '6px 0', color: '#888', width: 120 }}>{k}</td><td style={{ padding: '6px 0', fontWeight: 500 }}>{v}</td></tr>
                ))}
              </tbody>
            </table>

            {detailUser.savings_accounts?.length > 0 && (
              <>
                <h4 style={{ marginTop: 20, marginBottom: 10 }}>Sổ tiết kiệm ({detailUser.savings_accounts.length})</h4>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
                  <thead>
                    <tr style={{ background: '#fafafa', textAlign: 'left' }}>
                      <th style={{ padding: 8 }}>Mã sổ</th>
                      <th style={{ padding: 8 }}>Gói</th>
                      <th style={{ padding: 8 }}>Số tiền gốc</th>
                      <th style={{ padding: 8 }}>Trạng thái</th>
                    </tr>
                  </thead>
                  <tbody>
                    {detailUser.savings_accounts.map((s) => (
                      <tr key={s.account_id} style={{ borderTop: '1px solid #f0f0f0' }}>
                        <td style={{ padding: 8 }}>{s.account_id}</td>
                        <td style={{ padding: 8 }}>{s.product_name}</td>
                        <td style={{ padding: 8 }}>{Number(s.principal_balance).toLocaleString('vi-VN')}</td>
                        <td style={{ padding: 8 }}>{s.status}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
