"""Thread-safe monitoring primitives; wire these into the transaction manager."""
from collections import deque
from datetime import datetime, timezone
from threading import RLock
from typing import Any
from config import get_settings

_lock = RLock()
_logs: deque[dict[str, Any]] = deque(maxlen=5000)
_alerts: deque[dict[str, Any]] = deque(maxlen=1000)
_wait_times: deque[float] = deque(maxlen=5000)

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()

def log_transaction(transaction_id: str, operation: str, status: str,
                    message: str = "", wait_seconds: float | None = None) -> dict:
    record = {
        "timestamp": _now(),
        "transaction_id": transaction_id,
        "operation": operation,
        "status": status,
        "message": message,
    }
    with _lock:
        _logs.append(record)
        if wait_seconds is not None:
            _wait_times.append(max(0.0, float(wait_seconds)))
    return record

def get_logs(limit: int = 100) -> list[dict]:
    with _lock:
        return list(_logs)[-max(1, min(limit, 1000)):][::-1]

def create_low_balance_alert(account_id: str, balance: float) -> dict | None:
    threshold = float(get_settings()["low_balance_threshold"])
    if float(balance) >= threshold:
        return None
    alert = {
        "timestamp": _now(),
        "account_id": str(account_id),
        "balance": float(balance),
        "threshold": threshold,
        "message": f"Account {account_id} is below the configured balance threshold.",
    }
    with _lock:
        # Avoid duplicate active alerts for the same account and balance.
        if any(a["account_id"] == str(account_id) and a["balance"] == float(balance)
               for a in _alerts):
            return None
        _alerts.append(alert)
    return alert

def get_alerts(limit: int = 100) -> list[dict]:
    with _lock:
        return list(_alerts)[-max(1, min(limit, 1000)):][::-1]

def get_metrics() -> dict:
    with _lock:
        waits = list(_wait_times)
        logs = list(_logs)
        alerts_count = len(_alerts)
    successes = sum(1 for item in logs if item["status"].upper() in {"SUCCESS", "COMMITTED"})
    failures = sum(1 for item in logs if item["status"].upper() in {"FAIL", "FAILED", "ABORTED"})
    return {
        "logged_transactions": len(logs),
        "successful_transactions_in_retained_log": successes,
        "failed_transactions_in_retained_log": failures,
        "alerts_retained": alerts_count,
        "average_wait_seconds": round(sum(waits) / len(waits), 6) if waits else 0.0,
        "max_wait_seconds": round(max(waits), 6) if waits else 0.0,
    }
