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

export default function SystemConfigs() {
  const [configs, setConfigs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [editKey, setEditKey] = useState(null);
  const [form, setForm] = useState({ config_key: '', config_value: '', description: '' });
  const [editForm, setEditForm] = useState({ config_value: '', description: '' });
  const [msg, setMsg] = useState('');

  const fetchConfigs = useCallback(() => {
    setLoading(true);
    api.get('/admin/configs')
      .then((res) => setConfigs(res.data.configs))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => { fetchConfigs(); }, [fetchConfigs]);

  const handleCreate = async (e) => {
    e.preventDefault();
    setMsg('');
    try {
      await api.post('/admin/configs', form);
      setMsg('Thêm tham số thành công!');
      setForm({ config_key: '', config_value: '', description: '' });
      setShowCreate(false);
      fetchConfigs();
    } catch (err) {
      setMsg(err.response?.data?.message || 'Lỗi!');
    }
  };

  const handleUpdate = async (key) => {
    try {
      await api.put(`/admin/configs/${key}`, editForm);
      setEditKey(null);
      fetchConfigs();
    } catch (err) {
      alert(err.response?.data?.message || 'Lỗi!');
    }
  };

  const handleDelete = async (key) => {
    if (!confirm(`Bạn có chắc muốn xóa tham số "${key}"?`)) return;
    try {
      await api.delete(`/admin/configs/${key}`);
      fetchConfigs();
    } catch (err) {
      alert(err.response?.data?.message || 'Lỗi!');
    }
  };

  const startEdit = (c) => {
    setEditKey(c.config_key);
    setEditForm({ config_value: c.config_value, description: c.description || '' });
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <h2 style={{ margin: 0 }}>Tham số Hệ thống (QĐ6)</h2>
        <button onClick={() => setShowCreate(!showCreate)} style={btnStyle('#1890ff')}>
          {showCreate ? 'Đóng' : '+ Thêm tham số'}
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
          display: 'grid', gridTemplateColumns: '1fr 1fr 1fr auto', gap: 12, alignItems: 'end',
        }}>
          <div>
            <label style={{ fontSize: 12, color: '#888' }}>Tên tham số (key) *</label>
            <input style={inputStyle} placeholder="VD: MIN_DEPOSIT_AMOUNT" required
              value={form.config_key} onChange={(e) => setForm({ ...form, config_key: e.target.value })} />
          </div>
          <div>
            <label style={{ fontSize: 12, color: '#888' }}>Giá trị *</label>
            <input style={inputStyle} placeholder="VD: 100000" required
              value={form.config_value} onChange={(e) => setForm({ ...form, config_value: e.target.value })} />
          </div>
          <div>
            <label style={{ fontSize: 12, color: '#888' }}>Mô tả</label>
            <input style={inputStyle} placeholder="Mô tả tham số"
              value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
          </div>
          <button type="submit" style={{ ...btnStyle('#52c41a'), padding: '10px 20px' }}>Thêm</button>
        </form>
      )}

      {/* Table */}
      <div style={{ background: '#fff', borderRadius: 10, overflow: 'hidden', boxShadow: '0 1px 3px rgba(0,0,0,0.08)' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 14 }}>
          <thead>
            <tr style={{ background: '#fafafa', textAlign: 'left' }}>
              <th style={{ padding: '12px 16px' }}>Tham số (Key)</th>
              <th style={{ padding: '12px 16px' }}>Giá trị</th>
              <th style={{ padding: '12px 16px' }}>Mô tả</th>
              <th style={{ padding: '12px 16px' }}>Hành động</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={4} style={{ padding: 20, textAlign: 'center' }}>Đang tải...</td></tr>
            ) : configs.length === 0 ? (
              <tr><td colSpan={4} style={{ padding: 20, textAlign: 'center', color: '#999' }}>Chưa có tham số nào</td></tr>
            ) : configs.map((c) => (
              <tr key={c.config_key} style={{ borderTop: '1px solid #f0f0f0' }}>
                {editKey === c.config_key ? (
                  <>
                    <td style={{ padding: '10px 16px', fontWeight: 600, fontFamily: 'monospace' }}>
                      {c.config_key}
                    </td>
                    <td style={{ padding: '10px 16px' }}>
                      <input style={{ ...inputStyle, padding: '4px 8px' }} value={editForm.config_value}
                        onChange={(e) => setEditForm({ ...editForm, config_value: e.target.value })} />
                    </td>
                    <td style={{ padding: '10px 16px' }}>
                      <input style={{ ...inputStyle, padding: '4px 8px' }} value={editForm.description}
                        onChange={(e) => setEditForm({ ...editForm, description: e.target.value })} />
                    </td>
                    <td style={{ padding: '10px 16px' }}>
                      <div style={{ display: 'flex', gap: 6 }}>
                        <button style={btnStyle('#52c41a')} onClick={() => handleUpdate(c.config_key)}>Lưu</button>
                        <button style={btnStyle('#999')} onClick={() => setEditKey(null)}>Hủy</button>
                      </div>
                    </td>
                  </>
                ) : (
                  <>
                    <td style={{ padding: '10px 16px', fontWeight: 600, fontFamily: 'monospace' }}>
                      {c.config_key}
                    </td>
                    <td style={{ padding: '10px 16px', color: '#1890ff', fontWeight: 500 }}>
                      {c.config_value}
                    </td>
                    <td style={{ padding: '10px 16px', color: '#888' }}>
                      {c.description || '—'}
                    </td>
                    <td style={{ padding: '10px 16px' }}>
                      <div style={{ display: 'flex', gap: 6 }}>
                        <button style={btnStyle('#1890ff')} onClick={() => startEdit(c)}>Sửa</button>
                        <button style={btnStyle('#f5222d')} onClick={() => handleDelete(c.config_key)}>Xóa</button>
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
