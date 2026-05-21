import { useEffect, useState } from 'react';
import api from '../../api/axios';

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

  if (loading) return <div className="ds-panel ds-loading">Đang tải dashboard...</div>;
  if (error) return <div className="ds-alert ds-alert-error">{error}</div>;

  const cards = [
    { label: 'Khách hàng', value: data.total_customers },
    { label: 'Nhân viên', value: data.total_staff },
    { label: 'Admin', value: data.total_admins },
    { label: 'Sổ hoạt động', value: data.active_savings_accounts },
    { label: 'Tổng tiền gửi', value: `${Number(data.total_savings_amount || 0).toLocaleString('vi-VN')} VND` },
    { label: 'Chờ duyệt', value: data.pending_transactions },
    { label: 'Gói đang bật', value: data.active_products },
    { label: 'Tài khoản khóa', value: data.locked_accounts },
  ];

  return (
    <div>
      <header className="ds-page-head">
        <div>
          <h2>Dashboard tổng quan</h2>
          <p className="ds-kicker">Ảnh chụp vận hành hệ thống tiết kiệm tại thời điểm hiện tại</p>
        </div>
      </header>

      <section className="ds-grid">
        {cards.map((card, index) => (
          <article
            className="ds-card ds-metric"
            key={card.label}
            style={{ background: index % 3 === 0 ? '#fff' : index % 3 === 1 ? '#fef3c7' : '#fee2e2' }}
          >
            <span>{card.label}</span>
            <strong>{card.value}</strong>
          </article>
        ))}
      </section>
    </div>
  );
}
