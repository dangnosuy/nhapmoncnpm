from flask import Flask, jsonify
from flask_cors import CORS
from common.auth import auth_bp
from staff.staff import transactions_bp
from admin.admin import admin_bp

app = Flask(__name__)
CORS(app)

app.config['SECRET_KEY'] = 'mot_chuoi_bi_mat_rat_dai_va_kho_doan'

# Đăng ký các Blueprint
app.register_blueprint(auth_bp)
app.register_blueprint(transactions_bp)
app.register_blueprint(admin_bp)


@app.route('/api/ping', methods=['GET'])
def ping():
    return jsonify({'message': 'pong 🏓 – Server đang chạy!'}), 200


if __name__ == '__main__':
    app.run(debug=True, port=5000)
