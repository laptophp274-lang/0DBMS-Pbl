"""REST API routes for SecureBank integration and monitoring."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from config import get_settings, update_settings
from monitoring import (
    log_transaction, get_logs, get_alerts, get_metrics, create_low_balance_alert
)
from serializability import history_recorder

router = APIRouter()

class TransactionLogRequest(BaseModel):
    transaction_id: str
    operation: str
    status: str
    message: str = ""
    wait_seconds: float | None = Field(default=None, ge=0)

class HistoryRequest(BaseModel):
    transaction_id: str
    item: str
    operation: str = Field(description="R for read, W for write")

class AlertRequest(BaseModel):
    account_id: str
    balance: float

class ConfigRequest(BaseModel):
    concurrency_mode: str | None = None
    scheduling_policy: str | None = None
    deadlock_scheme: str | None = None
    low_balance_threshold: float | None = Field(default=None, ge=0)
    worker_count: int | None = Field(default=None, ge=1)

@router.get("/api/health")
def health():
    return {"status": "ok", "service": "SecureBank"}

@router.get("/api/config")
def read_config():
    return get_settings()

@router.put("/api/config")
def write_config(payload: ConfigRequest):
    changes = {k: v for k, v in payload.model_dump().items() if v is not None}
    try:
        return update_settings(**changes)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

@router.post("/api/logs")
def add_log(payload: TransactionLogRequest):
    return log_transaction(**payload.model_dump())

@router.get("/api/logs")
def read_logs(limit: int = 100):
    return {"logs": get_logs(limit)}

@router.get("/api/alerts")
def read_alerts(limit: int = 100):
    return {"alerts": get_alerts(limit)}

@router.post("/api/alerts/check")
def check_alert(payload: AlertRequest):
    alert = create_low_balance_alert(payload.account_id, payload.balance)
    return {"created": alert is not None, "alert": alert}

@router.get("/api/metrics")
def metrics():
    return get_metrics()

@router.post("/api/history")
def record_history(payload: HistoryRequest):
    try:
        return history_recorder.record(
            payload.transaction_id, payload.item, payload.operation.upper()
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

@router.get("/api/history")
def read_history():
    return {"history": history_recorder.get_history()}

@router.get("/api/serializability")
def verify_serializability():
    return history_recorder.verify()

@router.delete("/api/history")
def clear_history():
    history_recorder.clear()
    return {"cleared": True}
