# Smart Savings — Chạy project trên local

Mô tả ngắn: backend bằng Flask (API) và frontend bằng React + Vite (admin SPA). Cơ sở dữ liệu MySQL được khởi tạo bởi `smart_savings.sql`.

**Yêu cầu**:
- Python 3.10+ (hoặc 3.8+)
- Node.js 18+ và npm
- MySQL server (local)

**Tổng quan**
- Backend: [backend/app.py](backend/app.py#L1) — Flask app, register các blueprint API, tạo schema/rows mặc định khi khởi động.
- Frontend: [frontend/package.json](frontend/package.json#L1) — Vite + React app (admin).
- DB schema + seed: [smart_savings.sql](smart_savings.sql#L1).

---

## Cấu hình môi trường (tuỳ chọn)
- Biến môi trường có thể dùng để ghi đè cấu hình mặc định:
  - `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` — kết nối MySQL (xem `backend/common/db.py`).
  - `SECRET_KEY` — secret Flask; mặc định có giá trị dùng cho dev.
  - `DEFAULT_ADMIN_EMAIL`, `DEFAULT_ADMIN_PASSWORD`, `DEFAULT_STAFF_EMAIL`, `DEFAULT_STAFF_PASSWORD` — tài khoản khởi tạo.

## Bước 1 — Chuẩn bị MySQL
1. Khởi động MySQL server.
2. Import file schema & seed (file sẽ tạo database `modern_savings_db` và user `smart_savings`):

```bash
mysql -u root -p < smart_savings.sql
```

Ghi chú: file `smart_savings.sql` tạo user `smart_savings`@`localhost` với mật khẩu `SmartSavings@2026!` và gán quyền trên DB `modern_savings_db`. Nếu bạn không có quyền root trên MySQL, chỉnh `DB_USER`/`DB_PASSWORD` trong biến môi trường hoặc trong MySQL trước.

## Bước 2 — Chạy backend (Flask)
1. Tạo virtualenv và cài dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Chạy server:

```bash
cd backend
python app.py
```

Server mặc định chạy trên `http://localhost:5000` và có endpoint kiểm tra `/api/ping`.

Vì sao: backend cần kết nối tới MySQL; `app.py` chứa logic đảm bảo các cột/giá trị cấu trúc tồn tại và khởi tạo tài khoản mặc định (admin/staff) khi server khởi động — thuận tiện cho môi trường dev.

## Bước 3 — Chạy frontend (admin)
1. Cài npm dependencies và chạy dev server:

```bash
cd frontend
npm install
npm run dev
```

Frontend dev server mặc định ở `http://localhost:5173` (xem output `vite`). Frontend gọi API qua `/api/*` (vite dev server có proxy trong cấu hình ghi nhận trong repo nếu cần); nếu gặp lỗi CORS, backend đã bật CORS trong `app.py`.

## Lưu ý vận hành và debug (tại sao làm như vậy)
- Tự động tạo schema/columns và seed khi backend khởi động giúp tránh bước migration phức tạp cho mục đích học tập/demo.
- `DB_CONFIG` trong `backend/common/db.py` hỗ trợ override bằng biến môi trường để tiện chuyển giữa local và production.
- `smart_savings.sql` dùng mật khẩu rõ ràng để dễ demo; đổi mật khẩu cho môi trường thực tế.
- Blueprints tách module giúp tổ chức route theo vai trò (`admin`, `staff`, `client`). Giữ logic nhỏ trong các blueprint giúp dễ bảo trì.

## Kiểm tra nhanh
- Kiểm tra backend chạy: `curl http://localhost:5000/api/ping` → trả về JSON `{'message': 'pong 🏓 – Server đang chạy!'}`.
- Kiểm tra DB: kết nối tới `modern_savings_db` và xem nội dung `users`, `savings_products`, `system_configs`.

## Gợi ý cải tiến (từ review nhanh)
- Thêm file `.env.example` để biểu diễn biến môi trường cần thiết.
- Thêm script `make` hoặc `bin/setup.sh` tự động hóa các bước: tạo venv, cài depend, import schema.
- Không commit mật khẩu hay secrets. Đổi mật khẩu DB trong `smart_savings.sql` trước khi chia sẻ rộng.
- Thêm README tiếng Việt/Anh ở repo (đã thêm file này).

---

Nếu bạn muốn, tôi có thể: thêm file `.env.example`, script `setup.sh`, hoặc viết hướng dẫn ngắn cho deploy Docker.
