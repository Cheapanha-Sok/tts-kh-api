# Sound AI Khmer

A Text-to-Speech (TTS) API that synthesizes spoken Khmer audio for monetary amounts (KHR/USD), built with FastAPI and an ONNX TTS model. Results are cached (PostgreSQL + Redis) so repeated amount/currency requests don't re-run inference.

## Tech stack

- **API**: FastAPI + Uvicorn/Gunicorn
- **Inference**: ONNX Runtime (CPU)
- **Text processing**: `python-crfsuite` (Khmer word segmentation), a custom phonemizer (`lexicon.tsv` + `model.fst`), `espeak`
- **Cache/DB**: PostgreSQL (SQLAlchemy + Alembic migrations), Redis
- **Packaging**: [uv](https://docs.astral.sh/uv/)
- **Python**: 3.12

## Prerequisites

- Python 3.12
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- `espeak` (system package, required by the phonemizer)
  ```bash
  sudo apt-get install espeak
  ```
- Access to a PostgreSQL instance and a Redis instance (locally, via Docker, or a remote dev instance)
- The TTS ONNX model file (`tts.onnx`) — this is **not committed to the repo**; it's pulled from the model registry during CI/CD. Get it from your team/registry and place it locally (see below).

## 1. Clone and install dependencies

```bash
git clone https://gitlab.igtech.asia/ig/si/tdc/sound-ai/sound-ai-khmer.git
cd sound-ai-khmer
uv sync
```

This creates a `.venv/` and installs everything pinned in `uv.lock`.

## 2. Add the TTS model file

The app loads the model from the path in `MODEL_PATH` (default `src/tts_model/tts.onnx`). Create the folder and drop the model file in:

```bash
mkdir -p src/tts_model
cp /path/to/tts.onnx src/tts_model/tts.onnx
```

## 3. Configure environment variables

Settings are loaded via `pydantic-settings` from a file named `.env.<ENVIRONMENT>` (see `src/setting.py`), where `ENVIRONMENT` defaults to `development`. This repo ships `.env.development` and `.env.staging` templates — update `.env.development` with credentials that point at your local/dev PostgreSQL and Redis:

```env
# Redis Connection Properties
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# Postgres Connection Properties
POSTGRES_USER=postgres
POSTGRES_HOST=localhost
POSTGRES_PASSWORD=
POSTGRES_DB=sound_box_cache
POSTGRES_PORT=5432

# Model path
MODEL_PATH=src/tts_model/tts.onnx
```

> The committed `.env*` files contain placeholder/shared dev values — replace the host/password with your own local services rather than pointing at a shared environment, and never commit real secrets.

If you don't already have PostgreSQL/Redis running locally, the quickest way is Docker:

```bash
docker run -d --name pg-sound-ai -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=sound_box_cache -p 5432:5432 postgres:16
docker run -d --name redis-sound-ai -p 6379:6379 redis:7
```

## 4. Run database migrations

The `ids_cache_kh` table (used for caching generated audio ids by amount/currency) is managed by Alembic:

```bash
uv run alembic upgrade head
```

> Note: `alembic.ini` has a hardcoded `sqlalchemy.url` fallback pointing at a shared dev DB — `env.py` under `migration/` is what actually wires up the connection at runtime, so make sure it reads your `.env.development` settings (via `src/db/config.py`) rather than relying on that fallback.

## 5. Run the app locally

For local development with auto-reload:

```bash
uv run uvicorn app:app --reload --host 0.0.0.0 --port 8080
```

Or using the production-style entrypoint (`start.sh`, Gunicorn + Uvicorn workers):

```bash
./start.sh
```

The API has no `/docs` (Swagger is disabled), so verify it's up by hitting the synthesize endpoint directly.

## 6. Try it out

```bash
curl "http://localhost:8080/api/v1/synthesize?amount=1500&ccy=KHR" -o audio.mp3
```

Supported `ccy` values: `KHR`, `USD`. This returns an `audio/mpeg` (MP3) attachment.

## Running with Docker Compose (multi-instance + nginx)

`docker-compose.yml` runs two app replicas behind an nginx reverse proxy (`nginx.conf`) and expects a pre-built image plus a `.env` with `registry`, `repo`, `base_image_name`, and `env` set. This mirrors the staging/production deployment (see `.gitlab-ci.yml`) more than a typical local dev loop — prefer the steps above for day-to-day local development. To build the image yourself:

```bash
docker build --build-arg MODEL_FILE=/path/to/tts.onnx -t sound-ai-khmer:local .
```

## Project structure

```
app.py                 # FastAPI app, lifespan (loads the ONNX model), exception handlers
main.py                # placeholder entrypoint
start.sh               # production-style launch (gunicorn + uvicorn workers)
src/
  apis/synthesize.py    # GET /api/v1/synthesize
  db/                    # SQLAlchemy engine/session + ids cache queries
  redis_client/          # Redis connection wrapper
  models/                # SQLAlchemy models (ids cache)
  khmercut/               # Khmer word segmentation (CRF model)
  phonimizer/             # Grapheme-to-phoneme (lexicon + FST model)
  texts/                  # Number normalization & text cleaners
  tts.py                  # ONNX TTS wrapper
  setting.py              # pydantic-settings config loader
migration/               # Alembic migrations
```

## Troubleshooting

- **Model fails to load on startup**: confirm `MODEL_PATH` points to an existing `.onnx` file relative to the project root.
- **`espeak` errors from the phonemizer**: install the `espeak` system package (see Prerequisites).
- **DB/Redis connection errors on startup**: double-check `.env.development` values match a reachable PostgreSQL/Redis instance, and that migrations have been applied.
