import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from serializability import HistoryRecorder
from monitoring import log_transaction, get_metrics

def test_serializable_history():
    recorder = HistoryRecorder()
    recorder.record("T1", "A", "R")
    recorder.record("T1", "A", "W")
    recorder.record("T2", "A", "R")
    result = recorder.verify()
    assert result["conflict_serializable"] is True

def test_cycle_is_detected():
    recorder = HistoryRecorder()
    # T1 writes A before T2 reads A => T1 -> T2
    recorder.record("T1", "A", "W")
    recorder.record("T2", "A", "R")
    # T2 writes B before T1 reads B => T2 -> T1
    recorder.record("T2", "B", "W")
    recorder.record("T1", "B", "R")
    result = recorder.verify()
    assert result["conflict_serializable"] is False
    assert result["cycle"]

def test_transaction_log_and_metrics():
    result = log_transaction("TEST-1", "deposit", "SUCCESS", wait_seconds=0.1)
    assert result["transaction_id"] == "TEST-1"
    assert get_metrics()["logged_transactions"] >= 1
