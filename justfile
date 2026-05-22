default:
    just run

run:
    uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8787

dev:
    uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8787
