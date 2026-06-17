.PHONY: build up down logs clean test

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

clean:
	docker-compose down -v
	rm -rf backend/src/__pycache__
	rm -rf .uv .venv

test:
	uv run pytest

run backend:
	uv run uvicorn main:app --host 127.0.0.1 --port 8000 --reload

run frontend:
	uv run streamlit run frontend/app.py