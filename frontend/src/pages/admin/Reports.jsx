import { useCallback, useEffect, useState } from 'react';
import api from '../../api/axios';

export default function Reports() {
  const [dailyDate, setDailyDate] = useState('');
  const [month, setMonth] = useState('');
  const [dailyDateFilter, setDailyDateFilter] = useState('');
  const [monthFilter, setMonthFilter] = useState('');
  const [dailyItems, setDailyItems] = useState([]);
  const [monthlyItems, setMonthlyItems] = useState([]);
  const [msg, setMsg] = useState('');

  const loadDaily = useCallback(async () => {
    setMsg('');
    try {
      const params = dailyDateFilter ? { date: dailyDateFilter } : {};
      const res = await api.get('/reports/daily-activity', { params });
      setDailyItems(res.data.items || []);
    } catch (err) {
      setMsg(err.response?.data?.message || 'Không thể tải báo cáo ngày.');
    }
  }, [dailyDateFilter]);

  const loadMonthly = useCallback(async () => {
    setMsg('');
    try {
      const params = monthFilter ? { month: monthFilter } : {};
      const res = await api.get('/reports/monthly-open-close', { params });
      setMonthlyItems(res.data.items || []);
    } catch (err) {
      setMsg(err.response?.data?.message || 'Không thể tải báo cáo tháng.');
    }
  }, [monthFilter]);

  useEffect(() => {
    const loadReports = () => {
      loadDaily();
      loadMonthly();
    };
    loadReports();
    const intervalId = window.setInterval(loadReports, 12000);
    window.addEventListener('savings-realtime-event', loadReports);
    return () => {
      window.clearInterval(intervalId);
      window.removeEventListener('savings-realtime-event', loadReports);
    };
  }, [loadDaily, loadMonthly]);

  const applyDailyFilter = () => {
    setDailyDateFilter(dailyDate);
  };

  const applyMonthlyFilter = () => {
    setMonthFilter(month);
  };

  return (
    <div>
      <header className="ds-page-head">
        <div>
          <h2>Báo cáo BM5</h2>
          <p className="ds-kicker">Doanh số ngày và mở/đóng sổ theo tháng</p>
        </div>
      </header>

      {msg && <div className="ds-alert ds-alert-error">{msg}</div>}

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, minmax(0, 1fr))', gap: 18 }}>
        <section className="ds-card">
          <h3 className="ds-title" style={{ fontSize: 34 }}>BM5.1</h3>
          <p className="ds-kicker">Doanh số hoạt động ngày</p>
          <div className="ds-toolbar" style={{ marginTop: 16 }}>
            <input type="date" value={dailyDate} onChange={(e) => setDailyDate(e.target.value)} aria-label="Ngày báo cáo" />
            <button className="ds-btn ds-btn-primary" onClick={applyDailyFilter}>Áp dụng lọc</button>
          </div>
          <div className="ds-panel">
            <table>
              <thead><tr><th>Ngày</th><th>Loại tiết kiệm</th><th>Tổng thu</th><th>Tổng chi</th><th>Chênh lệch</th></tr></thead>
              <tbody>
                {dailyItems.length === 0 ? (
                  <tr><td colSpan={5} className="ds-empty">Chưa có dữ liệu.</td></tr>
                ) : dailyItems.map((item) => (
                  <tr key={`${item.date}-${item.product_name}`}>
                    <td>{item.date}</td>
                    <td>{item.product_name}</td>
                    <td>{Number(item.total_in).toLocaleString('vi-VN')} VND</td>
                    <td>{Number(item.total_out).toLocaleString('vi-VN')} VND</td>
                    <td><strong>{Number(item.difference).toLocaleString('vi-VN')} VND</strong></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <section className="ds-card">
          <h3 className="ds-title" style={{ fontSize: 34 }}>BM5.2</h3>
          <p className="ds-kicker">Mở/đóng sổ tháng</p>
          <div className="ds-toolbar" style={{ marginTop: 16 }}>
            <input type="month" value={month} onChange={(e) => setMonth(e.target.value)} aria-label="Tháng báo cáo" />
            <button className="ds-btn ds-btn-primary" onClick={applyMonthlyFilter}>Áp dụng lọc</button>
          </div>
          <div className="ds-panel">
            <table>
              <thead><tr><th>Ngày</th><th>Loại tiết kiệm</th><th>Sổ mở</th><th>Sổ đóng</th><th>Chênh lệch</th></tr></thead>
              <tbody>
                {monthlyItems.length === 0 ? (
                  <tr><td colSpan={5} className="ds-empty">Chưa có dữ liệu.</td></tr>
                ) : monthlyItems.map((item) => (
                  <tr key={`${item.date}-${item.product_name}`}>
                    <td>{item.date}</td>
                    <td>{item.product_name}</td>
                    <td>{item.opened_count}</td>
                    <td>{item.closed_count}</td>
                    <td><strong>{item.difference}</strong></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </div>
  );
}
