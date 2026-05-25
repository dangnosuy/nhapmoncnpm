import { useCallback, useEffect, useMemo, useState } from 'react';
import api from '../../api/axios';

const typeMap = {
  TRANSFER_OUT: 'Chuyển khoản đi',
  TRANSFER_IN: 'Chuyển khoản đến',
  OPEN_SAVINGS: 'Mở sổ tiết kiệm',
  DEPOSIT_TO_SAVINGS: 'Gửi thêm vào sổ',
  WITHDRAW_FROM_SAVINGS: 'Rút tiền từ sổ',
  CLOSE_SAVINGS: 'Tất toán sổ',
};

export default function TransactionApprovals() {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('PENDING');
  const [typeFilter, setTypeFilter] = useState('');
  const [processingId, setProcessingId] = useState(null);
  const [confirmAction, setConfirmAction] = useState(null);
  const [msg, setMsg] = useState('');

  const fetchTransactions = useCallback(async () => {
    setLoading(true);
    setMsg('');
    try {
      const params = {};
      if (statusFilter) params.status = statusFilter;
      if (typeFilter) params.transaction_type = typeFilter;
      const res = await api.get('/transactions', { params });
      setTransactions(res.data.transactions || []);
    } catch (err) {
      setMsg(err.response?.data?.message || 'Không thể tải danh sách giao dịch.');
    } finally {
      setLoading(false);
    }
  }, [statusFilter, typeFilter]);

  useEffect(() => {
    fetchTransactions();
  }, [fetchTransactions]);

  const pendingCount = useMemo(
    () => transactions.filter((t) => t.status === 'PENDING').length,
    [transactions]
  );

  const handleAction = async (transactionId, action) => {
    const actionText = action === 'approve' ? 'duyệt' : 'từ chối';

    setProcessingId(transactionId);
    setMsg('');
    try {
      await api.patch(`/transactions/${transactionId}`, {
        status: action === 'approve' ? 'APPROVED' : 'REJECTED',
      });
      setMsg(`${action === 'approve' ? 'Duyệt' : 'Từ chối'} giao dịch thành công.`);
      await fetchTransactions();
    } catch (err) {
      setMsg(err.response?.data?.message || `Không thể ${actionText} giao dịch.`);
    } finally {
      setProcessingId(null);
      setConfirmAction(null);
    }
  };

  const requestAction = (transactionId, action) => {
    const actionText = action === 'approve' ? 'duyệt' : 'từ chối';
    setConfirmAction({ transactionId, action, actionText });
  };

  return (
    <div>
      <header className="ds-page-head">
        <div>
          <h2>Duyệt giao dịch</h2>
          <p className="ds-kicker">Maker-checker queue / đang chờ: {pendingCount}</p>
        </div>
        <button className="ds-btn ds-btn-secondary" onClick={fetchTransactions} disabled={loading}>
          {loading ? 'Đang tải' : 'Làm mới'}
        </button>
      </header>

      {msg && (
        <div className={`ds-alert ${msg.toLowerCase().includes('thành công') ? 'ds-alert-success' : 'ds-alert-error'}`}>
          {msg}
        </div>
      )}

      <div className="ds-toolbar">
        <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} aria-label="Lọc trạng thái">
          <option value="">Tất cả trạng thái</option>
          <option value="PENDING">PENDING</option>
          <option value="APPROVED">APPROVED</option>
          <option value="REJECTED">REJECTED</option>
        </select>

        <select value={typeFilter} onChange={(e) => setTypeFilter(e.target.value)} aria-label="Lọc loại giao dịch">
          <option value="">Tất cả loại giao dịch</option>
          {Object.entries(typeMap).map(([key, label]) => (
            <option value={key} key={key}>{label}</option>
          ))}
        </select>
      </div>

      <div className="ds-panel">
        <table>
          <thead>
            <tr>
              <th>Mã GD</th>
              <th>Khách hàng</th>
              <th>Sổ/Gói</th>
              <th>Số tiền</th>
              <th>Lãi</th>
              <th>Loại giao dịch</th>
              <th>Trạng thái</th>
              <th>Thời gian tạo</th>
              <th>Hành động</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={9} className="ds-loading">Đang tải dữ liệu...</td></tr>
            ) : transactions.length === 0 ? (
              <tr><td colSpan={9} className="ds-empty">Không có giao dịch phù hợp.</td></tr>
            ) : (
              transactions.map((t) => {
                const isPending = t.status === 'PENDING';
                const isRowProcessing = processingId === t.transaction_id;

                return (
                  <tr key={t.transaction_id}>
                    <td><strong>#{t.transaction_id}</strong></td>
                    <td>{t.customer_name}</td>
                    <td>{t.account_id ? `Sổ #${t.account_id}` : t.target_product_name || '-'}</td>
                    <td>{Number(t.amount || 0).toLocaleString('vi-VN')} VND</td>
                    <td>{Number(t.interest_amount || 0).toLocaleString('vi-VN')} VND</td>
                    <td>{typeMap[t.transaction_type] || t.transaction_type}</td>
                    <td><span className={`ds-status ${t.status}`}>{t.status}</span></td>
                    <td>{t.created_at}</td>
                    <td>
                      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                        <button
                          className="ds-btn ds-btn-success"
                          disabled={!isPending || isRowProcessing}
                          onClick={() => requestAction(t.transaction_id, 'approve')}
                        >
                          Duyệt
                        </button>
                        <button
                          className="ds-btn ds-btn-danger"
                          disabled={!isPending || isRowProcessing}
                          onClick={() => requestAction(t.transaction_id, 'reject')}
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

      {confirmAction && (
        <div className="ds-modal-backdrop" role="dialog" aria-modal="true">
          <div className="ds-modal">
            <h3>Xác nhận giao dịch</h3>
            <p>Bạn đang {confirmAction.actionText} giao dịch #{confirmAction.transactionId}. Hành động này sẽ cập nhật dữ liệu ví/sổ nếu được duyệt.</p>
            <div className="ds-modal-actions">
              <button className="ds-btn" onClick={() => setConfirmAction(null)} disabled={!!processingId}>Hủy</button>
              <button
                className={`ds-btn ${confirmAction.action === 'approve' ? 'ds-btn-success' : 'ds-btn-danger'}`}
                onClick={() => handleAction(confirmAction.transactionId, confirmAction.action)}
                disabled={!!processingId}
              >
                {processingId ? 'Đang xử lý' : 'Xác nhận'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
