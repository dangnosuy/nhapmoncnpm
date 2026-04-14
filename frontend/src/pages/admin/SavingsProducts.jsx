import { useState, useEffect, useCallback } from 'react';
import api from '../../api/axios';

const inputStyle = {
  padding: '8px 12px',
  border: '1px solid #d9d9d9',
  borderRadius: 6,
  fontSize: 14,
  width: '100%',
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

export default function SavingsProducts() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [editId, setEditId] = useState(null);
  const [form, setForm] = useState({ name: '', term_months: 0, interest_rate: 0, min_days_hold: 0, description: '' });
  const [editForm, setEditForm] = useState({});
  const [msg, setMsg] = useState('');

  const fetchProducts = useCallback(() => {
    setLoading(true);
    api.get('/admin/savings-products')
      .then((res) => setProducts(res.data.products))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => { fetchProducts(); }, [fetchProducts]);

  const handleCreate = async (e) => {
    e.preventDefault();
    setMsg('');
    try {
      await api.post('/admin/savings-products', {
        ...form,
        term_months: Number(form.term_months),
        interest_rate: Number(form.interest_rate),
        min_days_hold: Number(form.min_days_hold),
      });
      setMsg('Thêm gói tiết kiệm thành công!');
      setForm({ name: '', term_months: 0, interest_rate: 0, min_days_hold: 0, description: '' });
      setShowCreate(false);
      fetchProducts();
    } catch (err) {
      setMsg(err.response?.data?.message || 'Lỗi!');
    }
  };

  const handleUpdate = async (productId) => {
    try {
      await api.put(`/admin/savings-products/${productId}`, {
        ...editForm,
        term_months: Number(editForm.term_months),
        interest_rate: Number(editForm.interest_rate),
        min_days_hold: Number(editForm.min_days_hold),
      });
      setEditId(null);
      fetchProducts();
    } catch (err) {
      alert(err.response?.data?.message || 'Lỗi!');
    }
  };

  const handleToggle = async (productId) => {
    try {
      await api.put(`/admin/savings-products/${productId}/toggle`);
      fetchProducts();
    } catch (err) {
      alert(err.response?.data?.message || 'Lỗi!');
    }
  };

  const startEdit = (p) => {
    setEditId(p.product_id);
    setEditForm({
      name: p.name,
      term_months: p.term_months,
      interest_rate: p.interest_rate,
      min_days_hold: p.min_days_hold,
      description: p.description || '',
    });
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <h2 style={{ margin: 0 }}>Quản lý Gói Tiết kiệm (QĐ6)</h2>
        <button onClick={() => setShowCreate(!showCreate)} style={btnStyle('#1890ff')}>
          {showCreate ? 'Đóng' : '+ Thêm gói mới'}
        </button>
      </div>

      {msg && (
        <div style={{
          padding: '8px 12px', marginBottom: 12, borderRadius: 6, fontSize: 14,
          background: msg.includes('thành công') ? '#f6ffed' : '#fff2f0',
          border: msg.includes('thành công') ? '1px solid #b7eb8f' : '1px solid #ffccc7',
          color: msg.includes('thành công') ? '#389e0d' : '#cf1322',
        }}>
          {msg}
        </div>
      )}

      {/* Create form */}
      {showCreate && (
        <form onSubmit={handleCreate} style={{
          background: '#fff', padding: 20, borderRadius: 10, marginBottom: 16,
          boxShadow: '0 1px 3px rgba(0,0,0,0.08)',
          display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 12,
        }}>
          <div>
            <label style={{ fontSize: 12, color: '#888' }}>Tên gói *</label>
            <input style={inputStyle} placeholder="VD: 3 tháng" required
              value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
          </div>
          <div>
            <label style={{ fontSize: 12, color: '#888' }}>Kỳ hạn (tháng) *</label>
            <input style={inputStyle} type="number" min="0" required
              value={form.term_months} onChange={(e) => setForm({ ...form, term_months: e.target.value })} />
          </div>
          <div>
            <label style={{ fontSize: 12, color: '#888' }}>Lãi suất (%/năm) *</label>
            <input style={inputStyle} type="number" step="0.01" min="0" required
              value={form.interest_rate} onChange={(e) => setForm({ ...form, interest_rate: e.target.value })} />
          </div>
          <div>
            <label style={{ fontSize: 12, color: '#888' }}>Ngày giữ tối thiểu</label>
            <input style={inputStyle} type="number" min="0"
              value={form.min_days_hold} onChange={(e) => setForm({ ...form, min_days_hold: e.target.value })} />
          </div>
          <div>
            <label style={{ fontSize: 12, color: '#888' }}>Mô tả</label>
            <input style={inputStyle} placeholder="Mô tả gói"
              value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
          </div>
          <div style={{ display: 'flex', alignItems: 'flex-end' }}>
            <button type="submit" style={{ ...btnStyle('#52c41a'), width: '100%', padding: '10px' }}>Thêm</button>
          </div>
        </form>
      )}

      {/* Table */}
      <div style={{ background: '#fff', borderRadius: 10, overflow: 'hidden', boxShadow: '0 1px 3px rgba(0,0,0,0.08)' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 14 }}>
          <thead>
            <tr style={{ background: '#fafafa', textAlign: 'left' }}>
              <th style={{ padding: '12px 16px' }}>ID</th>
              <th style={{ padding: '12px 16px' }}>Tên gói</th>
              <th style={{ padding: '12px 16px' }}>Kỳ hạn (tháng)</th>
              <th style={{ padding: '12px 16px' }}>Lãi suất (%/năm)</th>
              <th style={{ padding: '12px 16px' }}>Ngày giữ tối thiểu</th>
              <th style={{ padding: '12px 16px' }}>Trạng thái</th>
              <th style={{ padding: '12px 16px' }}>Hành động</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={7} style={{ padding: 20, textAlign: 'center' }}>Đang tải...</td></tr>
            ) : products.length === 0 ? (
              <tr><td colSpan={7} style={{ padding: 20, textAlign: 'center', color: '#999' }}>Chưa có gói tiết kiệm nào</td></tr>
            ) : products.map((p) => (
              <tr key={p.product_id} style={{ borderTop: '1px solid #f0f0f0' }}>
                {editId === p.product_id ? (
                  <>
                    <td style={{ padding: '10px 16px' }}>{p.product_id}</td>
                    <td style={{ padding: '10px 16px' }}>
                      <input style={{ ...inputStyle, padding: '4px 8px' }} value={editForm.name}
                        onChange={(e) => setEditForm({ ...editForm, name: e.target.value })} />
                    </td>
                    <td style={{ padding: '10px 16px' }}>
                      <input style={{ ...inputStyle, padding: '4px 8px', width: 80 }} type="number" value={editForm.term_months}
                        onChange={(e) => setEditForm({ ...editForm, term_months: e.target.value })} />
                    </td>
                    <td style={{ padding: '10px 16px' }}>
                      <input style={{ ...inputStyle, padding: '4px 8px', width: 80 }} type="number" step="0.01" value={editForm.interest_rate}
                        onChange={(e) => setEditForm({ ...editForm, interest_rate: e.target.value })} />
                    </td>
                    <td style={{ padding: '10px 16px' }}>
                      <input style={{ ...inputStyle, padding: '4px 8px', width: 80 }} type="number" value={editForm.min_days_hold}
                        onChange={(e) => setEditForm({ ...editForm, min_days_hold: e.target.value })} />
                    </td>
                    <td style={{ padding: '10px 16px' }}>—</td>
                    <td style={{ padding: '10px 16px' }}>
                      <div style={{ display: 'flex', gap: 6 }}>
                        <button style={btnStyle('#52c41a')} onClick={() => handleUpdate(p.product_id)}>Lưu</button>
                        <button style={btnStyle('#999')} onClick={() => setEditId(null)}>Hủy</button>
                      </div>
                    </td>
                  </>
                ) : (
                  <>
                    <td style={{ padding: '10px 16px' }}>{p.product_id}</td>
                    <td style={{ padding: '10px 16px', fontWeight: 500 }}>{p.name}</td>
                    <td style={{ padding: '10px 16px' }}>{p.term_months === 0 ? 'Không kỳ hạn' : `${p.term_months} tháng`}</td>
                    <td style={{ padding: '10px 16px', color: '#1890ff', fontWeight: 600 }}>{p.interest_rate}%</td>
                    <td style={{ padding: '10px 16px' }}>{p.min_days_hold} ngày</td>
                    <td style={{ padding: '10px 16px' }}>
                      <span style={{
                        padding: '2px 10px', borderRadius: 10, fontSize: 12, fontWeight: 600,
                        background: p.is_active ? '#f6ffed' : '#fff2f0',
                        color: p.is_active ? '#389e0d' : '#cf1322',
                      }}>
                        {p.is_active ? 'Hoạt động' : 'Đã tắt'}
                      </span>
                    </td>
                    <td style={{ padding: '10px 16px' }}>
                      <div style={{ display: 'flex', gap: 6 }}>
                        <button style={btnStyle('#1890ff')} onClick={() => startEdit(p)}>Sửa</button>
                        <button style={btnStyle(p.is_active ? '#f5222d' : '#52c41a')} onClick={() => handleToggle(p.product_id)}>
                          {p.is_active ? 'Tắt' : 'Bật'}
                        </button>
                      </div>
                    </td>
                  </>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
