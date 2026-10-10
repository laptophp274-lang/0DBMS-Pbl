"""Runtime configuration for SecureBank."""
from dataclasses import dataclass, asdict
from threading import RLock
from typing import Literal

ConcurrencyMode = Literal["NAIVE", "2PL", "OPTIMISTIC", "MVCC"]
SchedulingPolicy = Literal["FCFS", "PRIORITY", "SJF"]
DeadlockScheme = Literal["DETECT_TIMEOUT", "WAIT_DIE", "WOUND_WAIT"]

@dataclass
class Settings:
    concurrency_mode: ConcurrencyMode = "2PL"
    scheduling_policy: SchedulingPolicy = "FCFS"
    deadlock_scheme: DeadlockScheme = "DETECT_TIMEOUT"
    low_balance_threshold: float = 500.0
    worker_count: int = 4

_settings = Settings()
_lock = RLock()

def get_settings() -> dict:
    with _lock:
        return asdict(_settings)

def update_settings(**changes) -> dict:
    """Update only known settings; validate enum-like fields."""
    allowed = set(asdict(_settings))
    unknown = set(changes) - allowed
    if unknown:
        raise ValueError(f"Unknown setting(s): {', '.join(sorted(unknown))}")

    choices = {
        "concurrency_mode": {"NAIVE", "2PL", "OPTIMISTIC", "MVCC"},
        "scheduling_policy": {"FCFS", "PRIORITY", "SJF"},
        "deadlock_scheme": {"DETECT_TIMEOUT", "WAIT_DIE", "WOUND_WAIT"},
    }
    with _lock:
        for key, value in changes.items():
            if key in choices and value not in choices[key]:
                raise ValueError(f"Invalid {key}: {value}")
            if key == "low_balance_threshold" and float(value) < 0:
                raise ValueError("low_balance_threshold cannot be negative")
            if key == "worker_count" and int(value) < 1:
                raise ValueError("worker_count must be at least 1")
            setattr(_settings, key, value)
        return asdict(_settings)
