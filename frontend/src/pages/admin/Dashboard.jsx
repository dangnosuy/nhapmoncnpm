import { useState, useEffect } from 'react';
import api from '../../api/axios';

const CARD_STYLE = {
  background: '#fff',
  borderRadius: 10,
  padding: '20px 24px',
  boxShadow: '0 1px 3px rgba(0,0,0,0.08)',
  flex: '1 1 220px',
};

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    api.get('/admin/dashboard')
      .then((res) => setData(res.data.data))
      .catch((err) => setError(err.response?.data?.message || 'Lỗi tải dữ liệu'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p>Đang tải...</p>;
  if (error) return <p style={{ color: 'red' }}>{error}</p>;

  const cards = [
    { label: 'Khách hàng', value: data.total_customers, color: '#1890ff' },
    { label: 'Nhân viên', value: data.total_staff, color: '#52c41a' },
    { label: 'Admin', value: data.total_admins, color: '#722ed1' },
    { label: 'Sổ TK đang hoạt động', value: data.active_savings_accounts, color: '#13c2c2' },
    { label: 'Tổng tiền gửi (VND)', value: data.total_savings_amount?.toLocaleString('vi-VN'), color: '#fa8c16' },
    { label: 'Giao dịch chờ duyệt', value: data.pending_transactions, color: '#f5222d' },
    { label: 'Gói TK hoạt động', value: data.active_products, color: '#2f54eb' },
    { label: 'Tài khoản bị khóa', value: data.locked_accounts, color: '#eb2f96' },
  ];

  return (
    <div>
      <h2 style={{ marginTop: 0, marginBottom: 24 }}>Dashboard - Tổng quan</h2>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 16 }}>
        {cards.map((c) => (
          <div key={c.label} style={CARD_STYLE}>
            <div style={{ fontSize: 13, color: '#888', marginBottom: 8 }}>{c.label}</div>
            <div style={{ fontSize: 28, fontWeight: 700, color: c.color }}>{c.value}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
