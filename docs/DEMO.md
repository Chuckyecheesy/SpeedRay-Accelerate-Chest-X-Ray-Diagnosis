# SpeedRay — Demo (Reactiv-ClipKit Lab & Tailscale)

1. **Local:** Set `.env` from `.env.example`; run backend (`uvicorn api.main:app` from backend dir or project root with PYTHONPATH) and frontend (`npm run dev`). Open `/demo`, upload an X-ray, click "Run diagnosis".
2. **Tailscale:** Join the demo Tailscale network; use the server’s Tailscale IP as `VITE_API_BASE` so the frontend talks to the backend over the secure mesh.
3. **ClipKit:** Use the demo layout and ClipKit integration hooks for lab-style demos.
