# SecureBank — Shravan Bali's Integration & Testing Contribution

This is a **starter implementation** based on the responsibilities listed for Shravan Bali in the Phase-II project progress PDF. The PDF describes the architecture and assignments, but it does not contain the team's original source code. Therefore, these files are a reconstructed contribution, not a copy of an existing repository.

## Included
- `config.py`: runtime settings for concurrency mode, scheduler policy, and deadlock scheme
- `monitoring.py`: thread-safe transaction logs, alerts, and waiting-time metrics
- `serializability.py`: execution history, precedence graph, and cycle detection
- `api.py`: FastAPI REST endpoints
- `main.py`: application entry point
- `tests/test_core.py`: tests for history verification and monitoring
- `requirements.txt`: dependencies

## Run locally
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Open `http://127.0.0.1:8000/docs` for the interactive API docs.

## Important integration notes
- This starter uses in-memory data so it can run independently. Connect the endpoints to your team's PostgreSQL transaction manager and scheduler before merging into the main project.
- It provides monitoring/history APIs and a conflict-serializability checker; it does not implement the complete banking database, crash recovery, MVCC, or full dashboard.
- Coordinate API names and data formats with your teammates before merging.
