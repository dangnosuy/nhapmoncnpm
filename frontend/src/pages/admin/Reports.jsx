import { useState } from 'react';
import api from '../../api/axios';

export default function Reports() {
  const today = new Date().toISOString().slice(0, 10);
  const currentMonth = new Date().toISOString().slice(0, 7);
  const [dailyDate, setDailyDate] = useState(today);
  const [month, setMonth] = useState(currentMonth);
  const [dailyItems, setDailyItems] = useState([]);
  const [monthlyItems, setMonthlyItems] = useState([]);
  const [msg, setMsg] = useState('');

  const loadDaily = async () => {
    setMsg('');
    try {
      const res = await api.get('/reports/daily-activity', { params: { date: dailyDate } });
      setDailyItems(res.data.items || []);
    } catch (err) {
      setMsg(err.response?.data?.message || 'Không thể tải báo cáo ngày.');
    }
  };

  const loadMonthly = async () => {
    setMsg('');
    try {
      const res = await api.get('/reports/monthly-open-close', { params: { month } });
      setMonthlyItems(res.data.items || []);
    } catch (err) {
      setMsg(err.response?.data?.message || 'Không thể tải báo cáo tháng.');
    }
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
            <button className="ds-btn ds-btn-primary" onClick={loadDaily}>Tải báo cáo</button>
          </div>
          <div className="ds-panel">
            <table>
              <thead><tr><th>Loại tiết kiệm</th><th>Tổng thu</th><th>Tổng chi</th><th>Chênh lệch</th></tr></thead>
              <tbody>
                {dailyItems.length === 0 ? (
                  <tr><td colSpan={4} className="ds-empty">Chưa có dữ liệu.</td></tr>
                ) : dailyItems.map((item) => (
                  <tr key={item.product_name}>
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
            <button className="ds-btn ds-btn-primary" onClick={loadMonthly}>Tải báo cáo</button>
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
