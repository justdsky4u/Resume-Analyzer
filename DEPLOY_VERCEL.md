# Deploy frontend to Vercel (static hosting)

This project is a monorepo. The frontend is located in `app-frontend` and builds to `dist/` using Vite.

Steps to deploy the frontend to Vercel (recommended):

1. Commit your repo and push to GitHub:

```bash
git add .
git commit -m "Prepare for Vercel deployment"
git push origin main
```

2. Sign in to Vercel and import the GitHub repository.

3. When configuring the project in Vercel:
   - Set the root to the repository root (default). The provided `vercel.json` file will instruct Vercel to build `app-frontend/package.json` using `@vercel/static-build` and serve the `dist` output.
   - Build command: `npm run build` (Vercel will run this inside `app-frontend` because of `vercel.json`).
   - Output directory: `dist`.

4. (Optional) If your backend is hosted elsewhere (e.g., Render, Railway, or a cloud VM), create a Vercel Environment Variable named `VITE_API_URL` (or `REACT_APP_API_URL`) pointing to the public backend URL. Configure the frontend to read that env variable when performing API calls.

5. Trigger a deployment; the frontend will be served from a Vercel URL.

# Notes on backend

- Vercel's static hosting is ideal for the frontend. The `app-backend` FastAPI service is not configured as a Vercel serverless function here.
- You can host `app-backend` on a Python-capable host (Render, Railway, Fly.io, Heroku, or a VPS) and set the publicly reachable URL in Vercel env vars.
