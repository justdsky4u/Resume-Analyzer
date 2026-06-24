# AI Decision Intelligence — Scaffold

This workspace contains a starter scaffold for a combined Electron (desktop) + React (web) + FastAPI (backend) application.

Quick start (Windows):

1) Backend (Python)

```powershell
cd "c:\Users\DELL\AI Data Analizer\app-backend"
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
python -m uvicorn app_back:app --reload --host 127.0.0.1 --port 8000
```

1) Frontend (React + Vite)

```powershell
cd "c:\Users\DELL\AI Data Analizer\app-frontend"
npm install
npm run dev
```

1) Electron (desktop)

```powershell
cd "c:\Users\DELL\AI Data Analizer\electron-app"
npm install
npm run start
```

Notes:

- The frontend expects the backend at `http://127.0.0.1:8000` and the dev server at port 5173.
- This scaffold is minimal; next steps: add data cleaning, profiling, visualization modules, and authentication.

Electron production (serve built frontend):

1) Build frontend

```powershell
cd "c:\Users\DELL\AI Data Analizer\app-frontend"
npm run build
```

1) Start Electron in production mode (it will load the built files)

```powershell
cd "c:\Users\DELL\AI Data Analizer\electron-app"
npm install
npm run prod
```

Note: `npm run prod` sets `ELECTRON_PROD=1` so Electron loads `app-frontend/dist/index.html`. Use your preferred packager (electron-builder, electron-forge) to create distributables.

Analyze endpoint examples:

JSON payload example (POST to `/analyze`):

```powershell
curl -X POST http://127.0.0.1:8000/analyze -H "Content-Type: application/json" -d "{\"data\":[{\"a\":1,\"b\":2},{\"a\":2,\"b\":3}]}"
```

File upload example (CSV) to `/analyze_file`:

```powershell
curl -X POST http://127.0.0.1:8000/analyze_file -F "file=@data.csv"
```

Result payload additions:

- `risks`: detected red flags and unstable data indicators.
- `opportunities`: growth, optimization, and modeling signals.
- `visualization_blueprint`: chart recommendations for line, bar, heatmap, and pie views.

Deploying the backend to Render

1) Create a new web service on Render and connect it to this GitHub repository.
2) Use `app-backend/render.yaml` as the service definition.
3) Set the Render build command to:

```bash
pip install -r requirements.txt
```

4) Set the Render start command to:

```bash
uvicorn app_back:app --host 0.0.0.0 --port $PORT
```

5) Optionally set `ALLOWED_ORIGINS` to your deployed frontend domain(s), for example:

```bash
https://your-frontend.vercel.app
```

6) If you need a quick open CORS policy, leave `ALLOWED_ORIGINS` unset and the backend will allow local dev plus all origins.

Deploying the frontend to Vercel

1) Connect Vercel to this GitHub repository.
2) Use the existing `vercel.json` config in the repo.
3) In Vercel project settings, add an environment variable:

- `VITE_API_URL` = `https://your-backend.onrender.com`

4) Deploy the frontend. The app will use `VITE_API_URL` in production and fall back to `http://127.0.0.1:8000` for local testing.

Install backend extras (Windows):

```powershell
cd "c:\Users\DELL\AI Data Analizer\app-backend"
.\.venv\Scripts\pip install -r requirements.txt
```
