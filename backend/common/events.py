import json
import queue
import time
import threading

import jwt
from flask import Blueprint, Response, current_app, request


events_bp = Blueprint("events", __name__)
_subscribers = []
_subscribers_lock = threading.Lock()


def publish_event(event_type, message, roles=None, user_ids=None, payload=None):
    event = {
        "type": event_type,
        "message": message,
        "roles": roles or ["ADMIN", "STAFF", "CUSTOMER"],
        "user_ids": [int(uid) for uid in (user_ids or [])],
        "payload": payload or {},
        "created_at": int(time.time()),
    }

    stale = []
    with _subscribers_lock:
        snapshot = list(_subscribers)

    for subscriber in snapshot:
        if not _event_matches_subscriber(event, subscriber):
            continue
        try:
            subscriber["queue"].put_nowait(event)
        except queue.Full:
            # Queue full: subscriber is too slow, mark stale
            stale.append(subscriber)
        except Exception:
            stale.append(subscriber)

    for subscriber in stale:
        _remove_subscriber(subscriber)


def _event_matches_subscriber(event, subscriber):
    if subscriber["role"] not in event["roles"]:
        return False
    return not event["user_ids"] or subscriber["user_id"] in event["user_ids"]


def _remove_subscriber(subscriber):
    with _subscribers_lock:
        try:
            _subscribers.remove(subscriber)
        except ValueError:
            pass


def _decode_token(token):
    return jwt.decode(
        token,
        current_app.config["SECRET_KEY"],
        algorithms=["HS256"]
    )


@events_bp.route("/api/events", methods=["GET"])
def stream_events():
    token = request.args.get("token", "")
    try:
        payload = _decode_token(token)
    except jwt.ExpiredSignatureError:
        return Response("Token đã hết hạn", status=401)
    except jwt.InvalidTokenError:
        return Response("Token không hợp lệ", status=401)

    subscriber = {
        "user_id": int(payload.get("user_id")),
        "role": payload.get("role"),
        "queue": queue.Queue(maxsize=50),
    }
    with _subscribers_lock:
        _subscribers.append(subscriber)

    def generate():
        # Send retry hint: exponential backoff starts at 3s, max 30s
        yield "retry: 3000\n"
        yield "event: ready\ndata: {}\n\n"
        try:
            while True:
                try:
                    event = subscriber["queue"].get(timeout=25)
                    yield f"event: savings\ndata: {json.dumps(event, ensure_ascii=False)}\n\n"
                except queue.Empty:
                    yield ": keepalive\n\n"
        finally:
            _remove_subscriber(subscriber)

    response = Response(generate(), mimetype="text/event-stream")
    response.headers["Cache-Control"] = "no-cache"
    response.headers["X-Accel-Buffering"] = "no"
    return response
