"""
Shared pytest fixtures for Smart Savings backend tests.

Provides:
  - Flask test app with all blueprints registered
  - JWT token helpers for each role
  - Mocked db_cursor / db_conn / mysql.connector.connect / publish_event
"""

import sys
import os
import pytest
import datetime
from unittest.mock import MagicMock, patch

# Ensure backend directory is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import jwt

SECRET_KEY = 'test-secret-key-for-unit-tests'


# ---------------------------------------------------------------------------
#  Token helpers
# ---------------------------------------------------------------------------

def make_token(user_id, role, secret=SECRET_KEY, expired=False):
    """Generate a JWT token for testing."""
    if expired:
        exp = datetime.datetime.utcnow() - datetime.timedelta(hours=1)
    else:
        exp = datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    payload = {
        'user_id': user_id,
        'role': role,
        'exp': exp,
    }
    return jwt.encode(payload, secret, algorithm='HS256')


# ---------------------------------------------------------------------------
#  Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def app(mock_db):
    """Create a minimal Flask app with all blueprints registered.

    Does NOT import app.py (which hits the real DB at import time).
    Instead, registers each blueprint individually on a fresh app.
    """
    from flask import Flask
    from common.auth import auth_bp
    from common.events import events_bp
    from staff.staff import transactions_bp
    from admin.admin import admin_bp
    from client.client import client_bp

    test_app = Flask(__name__)
    test_app.config['SECRET_KEY'] = SECRET_KEY
    test_app.config['TESTING'] = True

    test_app.register_blueprint(auth_bp)
    test_app.register_blueprint(events_bp)
    test_app.register_blueprint(transactions_bp)
    test_app.register_blueprint(admin_bp)
    test_app.register_blueprint(client_bp)

    return test_app


@pytest.fixture
def client(app):
    """Flask test client."""
    return app.test_client()


@pytest.fixture
def mock_db():
    """Mock the shared db proxy AND mysql.connector.connect (used by client.py).

    Yields (mock_cursor, mock_conn).
    """
    mock_cursor = MagicMock()
    mock_conn = MagicMock()

    with patch('common.db._get_cursor', return_value=mock_cursor), \
         patch('common.db._get_connection', return_value=mock_conn), \
         patch('mysql.connector.connect', return_value=mock_conn):
        # When client.py calls conn.cursor(), return our mock_cursor
        mock_conn.cursor.return_value = mock_cursor
        yield mock_cursor, mock_conn


@pytest.fixture
def mock_events():
    """Mock publish_event so tests don't need real subscribers."""
    with patch('common.events.publish_event') as mock:
        yield mock


@pytest.fixture
def admin_token():
    return make_token(1, 'ADMIN')


@pytest.fixture
def staff_token():
    return make_token(2, 'STAFF')


@pytest.fixture
def customer_token():
    return make_token(3, 'CUSTOMER')


@pytest.fixture
def expired_token():
    return make_token(1, 'ADMIN', expired=True)


@pytest.fixture
def auth_header():
    """Factory fixture: auth_header('ADMIN') returns {'Authorization': 'Bearer <token>'}."""
    def _make(role, user_id=1, expired=False):
        token = make_token(user_id, role, expired=expired)
        return {'Authorization': f'Bearer {token}'}
    return _make
