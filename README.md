# LifeStack

LifeStack is a mobile-first productivity companion that blends a weekly calendar, gym tracker, daily log, and project journal into one cohesive stack. It ships with a FastAPI backend, a React + Vite frontend, installable PWA assets, and local-first caching.

## Getting started

### Prerequisites
- Python 3.11+
- Node.js 18+
- npm

### Installation
```bash
make install
```
If `make` is unavailable (for example on Windows), run the install steps manually:
```bash
pip install -r server/requirements.txt
npm --prefix web install
```

### Running the dev stack
```bash
make dev
```
The command starts the FastAPI server on `http://localhost:8000` and the Vite dev server on `http://localhost:5173`.

On platforms without `make`, launch the stack via the helper script:
```bash
python scripts/dev.py
```
Use `CTRL+C` to stop both processes.

### Seeding demo data
```bash
make seed
```
Without `make` run the seed script from the `server/` directory:
```bash
cd server
python -m app.seed
```

### Tests
```bash
make test
```

### Environment variables
- `LIFESTACK_DATABASE_URL` (default: `sqlite:///./lifstack.db`)
- `LIFESTACK_JWT_SECRET` – secret used for token signing
- `LIFESTACK_UPLOAD_DIR` (default: `uploads`)

### File layout
```
server/   FastAPI app, SQLModel models, tests
web/      React + Vite frontend with TailwindCSS
uploads/  Media uploads (created automatically)
```

### API highlights
- CRUD routes for tasks, task templates, daily logs, exercises, workouts, PRs, projects, project updates, workout sets, and media uploads.
- `/quick-capture` accepts tasks, log entries, workout sets, and project updates.
- `/tasks/expand-recurring` expands simple BYDAY recurrence rules.
- `/dashboard/overview?week=YYYY-WW` summarises completion, workouts, PRs, and streaks.
- `/search` offers unified search with context and status filters.
- `/export.json` and `/export.csv` return zipped exports per entity.
- `/uploads` handles validated image uploads to `/uploads`.
- `/backup` and `/restore` handle SQLite snapshots.

### PWA & local-first notes
- The frontend registers a service worker (`public/service-worker.js`) with offline caching and background sync for queued API writes.
- IndexedDB caching (`useIndexedDBCache`) keeps recent data locally for offline read access.

## Backup & restore
- `POST /backup` streams the current SQLite database.
- `POST /restore` accepts an uploaded SQLite file and replaces the database after validation.

## Replit
If using Replit, set the environment variables above, run `make install`, and then `make dev` inside the shell. Open the exposed web server to preview the app.
