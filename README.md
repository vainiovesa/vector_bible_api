# Vector Bible API

## Run

Set environment variables in a local `.env` file, then run:

```bash
docker compose up --build
```

The API will be available on `http://localhost:8000`.

## Import scripts

```bash
docker compose run --rm app python scripts/import_fi_1776.py
docker compose run --rm app python scripts/import_en_kjv.py
```
