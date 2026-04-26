import { useCallback, useEffect, useMemo, useState } from 'react';
import api from '../../api/axios';

const inputStyle = {
  padding: '8px 12px',
  border: '1px solid #d9d9d9',
  borderRadius: 6,
  fontSize: 14,
  boxSizing: 'border-box',
};

const btnStyle = (bg, disabled = false) => ({
  padding: '6px 12px',
  background: disabled ? '#d9d9d9' : bg,
  color: '#fff',
  border: 'none',
  borderRadius: 6,
  cursor: disabled ? 'not-allowed' : 'pointer',
  fontSize: 13,
});

const typeMap = {
  DEPOSIT_TO_WALLET: 'Nạp tiền ví',
  WITHDRAW_FROM_WALLET: 'Rút tiền ví',
  OPEN_SAVINGS: 'Mở sổ tiết kiệm',
  CLOSE_SAVINGS: 'Tất toán sổ tiết kiệm',
};

export default function TransactionApprovals() {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('PENDING');
  const [typeFilter, setTypeFilter] = useState('DEPOSIT_TO_WALLET');
  const [processingId, setProcessingId] = useState(null);
  const [msg, setMsg] = useState('');

  const fetchTransactions = useCallback(async () => {
    setLoading(true);
    setMsg('');
    try {
      const params = {};
      if (statusFilter) params.status = statusFilter;
      const res = await api.get('/transactions', { params });
      setTransactions(res.data.transactions || []);
    } catch (err) {
      setMsg(err.response?.data?.message || 'Không thể tải danh sách giao dịch.');
    } finally {
      setLoading(false);
    }
  }, [statusFilter]);

  useEffect(() => {
    fetchTransactions();
  }, [fetchTransactions]);

  const filteredTransactions = useMemo(
    () => transactions.filter((t) => !typeFilter || t.transaction_type === typeFilter),
    [transactions, typeFilter]
  );

  const pendingCount = useMemo(
    () => transactions.filter((t) => t.status === 'PENDING' && t.transaction_type === 'DEPOSIT_TO_WALLET').length,
    [transactions]
  );

  const handleAction = async (transactionId, action) => {
    const actionText = action === 'approve' ? 'duyệt' : 'từ chối';
    const confirmed = window.confirm(`Bạn có chắc muốn ${actionText} giao dịch #${transactionId}?`);
    if (!confirmed) return;

    setProcessingId(transactionId);
    setMsg('');
    try {
      await api.put(`/transactions/${transactionId}/${action}`);
      setMsg(`${action === 'approve' ? 'Duyệt' : 'Từ chối'} giao dịch thành công.`);
      await fetchTransactions();
    } catch (err) {
      setMsg(err.response?.data?.message || `Không thể ${actionText} giao dịch.`);
    } finally {
      setProcessingId(null);
    }
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <div>
          <h2 style={{ margin: 0 }}>Duyệt giao dịch</h2>
          <div style={{ marginTop: 6, color: '#666', fontSize: 13 }}>
            Yêu cầu nạp tiền vào ví đang chờ duyệt: <strong>{pendingCount}</strong>
          </div>
        </div>
        <button onClick={fetchTransactions} style={btnStyle('#1890ff', loading)}>
          {loading ? 'Đang tải...' : 'Làm mới'}
        </button>
      </div>

      {msg && (
        <div
          style={{
            padding: '10px 12px',
            marginBottom: 12,
            borderRadius: 6,
            background: msg.toLowerCase().includes('thành công') ? '#f6ffed' : '#fff2f0',
            border: msg.toLowerCase().includes('thành công') ? '1px solid #b7eb8f' : '1px solid #ffccc7',
            color: msg.toLowerCase().includes('thành công') ? '#389e0d' : '#cf1322',
            fontSize: 14,
          }}
        >
          {msg}
        </div>
      )}

      <div style={{ display: 'flex', gap: 12, marginBottom: 14 }}>
        <select style={inputStyle} value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
          <option value="">Tất cả trạng thái</option>
          <option value="PENDING">PENDING</option>
          <option value="APPROVED">APPROVED</option>
          <option value="REJECTED">REJECTED</option>
        </select>

        <select style={inputStyle} value={typeFilter} onChange={(e) => setTypeFilter(e.target.value)}>
          <option value="">Tất cả loại giao dịch</option>
          <option value="DEPOSIT_TO_WALLET">Nạp tiền ví</option>
          <option value="WITHDRAW_FROM_WALLET">Rút tiền ví</option>
          <option value="OPEN_SAVINGS">Mở sổ tiết kiệm</option>
          <option value="CLOSE_SAVINGS">Tất toán sổ</option>
        </select>
      </div>

      <div style={{ background: '#fff', borderRadius: 10, overflow: 'hidden', boxShadow: '0 1px 3px rgba(0,0,0,0.08)' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 14 }}>
          <thead>
            <tr style={{ background: '#fafafa', textAlign: 'left' }}>
              <th style={{ padding: '12px 16px' }}>Mã GD</th>
              <th style={{ padding: '12px 16px' }}>Khách hàng</th>
              <th style={{ padding: '12px 16px' }}>Số tiền</th>
              <th style={{ padding: '12px 16px' }}>Loại giao dịch</th>
              <th style={{ padding: '12px 16px' }}>Trạng thái</th>
              <th style={{ padding: '12px 16px' }}>Thời gian tạo</th>
              <th style={{ padding: '12px 16px' }}>Hành động</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={7} style={{ padding: 20, textAlign: 'center' }}>Đang tải dữ liệu...</td>
              </tr>
            ) : filteredTransactions.length === 0 ? (
              <tr>
                <td colSpan={7} style={{ padding: 20, textAlign: 'center', color: '#999' }}>Không có giao dịch phù hợp.</td>
              </tr>
            ) : (
              filteredTransactions.map((t) => {
                const isPending = t.status === 'PENDING';
                const isRowProcessing = processingId === t.transaction_id;

                return (
                  <tr key={t.transaction_id} style={{ borderTop: '1px solid #f0f0f0' }}>
                    <td style={{ padding: '10px 16px', fontWeight: 600 }}>#{t.transaction_id}</td>
                    <td style={{ padding: '10px 16px' }}>{t.customer_name}</td>
                    <td style={{ padding: '10px 16px' }}>{Number(t.amount || 0).toLocaleString('vi-VN')} VND</td>
                    <td style={{ padding: '10px 16px' }}>{typeMap[t.transaction_type] || t.transaction_type}</td>
                    <td style={{ padding: '10px 16px' }}>
                      <span
                        style={{
                          padding: '2px 10px',
                          borderRadius: 12,
                          fontSize: 12,
                          fontWeight: 600,
                          background: t.status === 'APPROVED' ? '#f6ffed' : t.status === 'REJECTED' ? '#fff2f0' : '#fffbe6',
                          color: t.status === 'APPROVED' ? '#389e0d' : t.status === 'REJECTED' ? '#cf1322' : '#d48806',
                        }}
                      >
                        {t.status}
                      </span>
                    </td>
                    <td style={{ padding: '10px 16px' }}>{t.created_at}</td>
                    <td style={{ padding: '10px 16px' }}>
                      <div style={{ display: 'flex', gap: 8 }}>
                        <button
                          style={btnStyle('#52c41a', !isPending || isRowProcessing)}
                          disabled={!isPending || isRowProcessing}
                          onClick={() => handleAction(t.transaction_id, 'approve')}
                        >
                          Duyệt
                        </button>
                        <button
                          style={btnStyle('#f5222d', !isPending || isRowProcessing)}
                          disabled={!isPending || isRowProcessing}
                          onClick={() => handleAction(t.transaction_id, 'reject')}
                        >
                          Từ chối
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
