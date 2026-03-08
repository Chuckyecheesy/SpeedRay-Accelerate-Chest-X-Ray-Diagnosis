# Deploy SpeedRay API on Vultr

SpeedRay backend (FastAPI + PyTorch/TorchXRayVision, Gemini, Cloudinary, etc.) is intended to run on a **Vultr VPS or container**. Vultr’s Serverless Inference product is aimed at LLM inference, not a full HTTP API with a custom PyTorch model.

## Vultr API key (optional)

If you set **`VULTR_API_KEY`** in your `.env` (e.g. for the **speedray-diagnostic-agent** or any Vultr project), you can use it for:

- **Create and manage VPS instances** — Use the [Vultr API](https://www.vultr.com/api/) (e.g. create instance, list instances, destroy) from scripts or CI/CD.
- **Automate deployment** — Script creating an Ubuntu VPS, SSH in, clone the repo, set env vars, and run the API.
- **Terraform / IaC** — Use the Vultr provider with your API key to define VPS and networking in code.

The SpeedRay app itself does **not** read this key at runtime; it is for deployment and infrastructure automation only. Keep `.env` out of version control (it is in `.gitignore`).

## Option 1: VPS (recommended)

1. **Create a Vultr VPS** (e.g. Ubuntu 24.04) with enough RAM for PyTorch (~2GB+ recommended).

2. **Install Python 3.10+** and dependencies:
   ```bash
   sudo apt update && sudo apt install -y python3.10-venv python3-pip
   cd /opt  # or your app dir
   git clone <your-repo> speedray && cd speedray
   python3 -m venv venv && source venv/bin/activate
   pip install -r backend/requirements.txt
   ```

3. **Set environment variables** (see [serverless.yaml](./serverless.yaml) for the full list). Example:
   ```bash
   export SPEEDRAY_CLOUDINARY_CLOUD_NAME=...
   export SPEEDRAY_CLOUDINARY_API_KEY=...
   export SPEEDRAY_CLOUDINARY_API_SECRET=...
   export SPEEDRAY_GEMINI_API_KEY=...
   export SPEEDRAY_ELEVENLABS_API_KEY=...
   export SPEEDRAY_ELEVENLABS_VOICE_ID=...
   # Optional: SPEEDRAY_TORCH_MODEL_TYPE=torchxrayvision (default)
   ```

4. **Run the API** (from repo root; do **not** run from inside `backend/` or imports will fail):
   ```bash
   cd /opt/speedray && source venv/bin/activate && python run_api.py
   ```
   Or with uvicorn directly:
   ```bash
   cd /opt/speedray && source venv/bin/activate && uvicorn backend.api.main:app --host 0.0.0.0 --port 8000
   ```
   For production, use Gunicorn from project root:
   ```bash
   cd /opt/speedray && source venv/bin/activate && gunicorn backend.api.main:app -k uvicorn.workers.UvicornWorker -w 1 -b 0.0.0.0:8000
   ```

5. **Optional:** Put Nginx in front and use Tailscale for secure access (see main [deployment README](../README.md)).

## Option 2: Container (Docker)

1. Build an image that installs `backend/requirements.txt` and sets `WORKDIR` to the **project root** (not `backend/`).
2. Run with `python run_api.py` or `uvicorn backend.api.main:app --host 0.0.0.0 --port 8000`.
3. Pass required env vars via `-e` or a `.env` file.

## Config reference

- **[serverless.yaml](./serverless.yaml)** — Deployment checklist: Python version, handler, start command, and full list of env vars (Cloudinary, Gemini, ElevenLabs, Torch, Backboard, RAG, Solana, Presage, Auth0).

## Idle shutdown (save credits when frontend is not open)

When the frontend is not opened in a browser (localhost or web), no requests hit the API except optional health checks. The backend records **last activity** on any request except `GET /` and `GET /health`. A cron job on the Vultr server can **halt the instance** after idle time so you stop burning credits.

1. **Set on the Vultr server** (e.g. in `.env` or `export` in crontab):
   - `VULTR_API_KEY` — your Vultr API key (same as for deployment).
   - `VULTR_INSTANCE_ID` — this instance’s ID (from Vultr dashboard or `GET https://api.vultr.com/v2/instances`).
   - Optional: `SPEEDRAY_IDLE_THRESHOLD_MINUTES` (default `30`), `SPEEDRAY_ACTIVITY_FILE` (default `./.speedray_last_activity`).

2. **Activity file**: The API writes `.speedray_last_activity` in the **project root** (where you run `python run_api.py`) on every request except `/` and `/health`. So opening the frontend and using the app updates this file; only health checks do not.

3. **Cron** (run from project root, e.g. `/opt/speedray`):
   ```bash
   */15 * * * * cd /opt/speedray && . ./venv/bin/activate && python deployment/vultr/idle_shutdown.py
   ```
   This runs every 15 minutes; if the last activity is older than the threshold (e.g. 30 minutes), the script calls the Vultr API to **halt** this instance. The server powers off and stops burning credits until you **start** it again from the Vultr dashboard (or via API).

4. **Starting again**: In Vultr dashboard → your server → Start. No code or app structure changes; the API and frontend behave the same when the instance is running.

### How to do these (step-by-step)

Do the following **on the Vultr server** (SSH in as your deploy user).

**1. Get your instance ID**

- **Dashboard:** [Vultr → Products](https://my.vultr.com/) → click your SpeedRay server → copy the **Instance ID** from the details.
- **Or via API** (with `VULTR_API_KEY` set on your machine):
  ```bash
  curl -s -H "Authorization: Bearer $VULTR_API_KEY" https://api.vultr.com/v2/instances
  ```
  Find the `id` of the instance that is this server.

**2. Set env vars on the server**

**Option A — In project `.env`:** From project root (e.g. `/opt/speedray`):
```bash
cd /opt/speedray
echo 'VULTR_API_KEY=your_api_key_here' >> .env
echo 'VULTR_INSTANCE_ID=your_instance_id_here' >> .env
```
Replace with your real key and instance ID. Cron does not load `.env` by default, so use the wrapper in step 3 Option A.

**Option B — Export in crontab:** Put the exports directly in the cron line in step 3 Option B so cron sees them.

**3. Add the cron job**

Run `crontab -e` and add **one** of these (change `/opt/speedray` if your repo lives elsewhere).

**Option A — Wrapper script (if you use `.env` for the vars)**  
Create the wrapper once:
```bash
cat > /opt/speedray/deployment/vultr/run_idle_shutdown.sh << 'WRAP'
#!/bin/bash
cd /opt/speedray
set -a; [ -f .env ] && . ./.env; set +a
. ./venv/bin/activate
exec python deployment/vultr/idle_shutdown.py
WRAP
chmod +x /opt/speedray/deployment/vultr/run_idle_shutdown.sh
```
Then in crontab:
```cron
*/15 * * * * /opt/speedray/deployment/vultr/run_idle_shutdown.sh
```

**Option B — Inline exports (no .env needed for idle script)**  
In crontab:
```cron
*/15 * * * * export VULTR_API_KEY='YOUR_KEY' VULTR_INSTANCE_ID='YOUR_INSTANCE_ID'; cd /opt/speedray && . ./venv/bin/activate && python deployment/vultr/idle_shutdown.py
```
Replace `YOUR_KEY` and `YOUR_INSTANCE_ID`. Save and exit the editor.

**4. Start the instance again when needed**

After the instance is halted it is off and not burning compute credits. To use the app again:

1. [Vultr](https://my.vultr.com/) → **Products** → your SpeedRay server → click **Start** (Power On). Wait until status is **Running**.
2. SSH in and start the API (if you don’t use systemd):  
   `cd /opt/speedray && source venv/bin/activate && python run_api.py`  
   Or use your existing Gunicorn/systemd setup.

| What | How |
|------|-----|
| Instance ID | Dashboard → server → Instance ID, or `curl` API `/v2/instances` |
| Set vars | `.env` + wrapper script, or `export` in cron line |
| Cron | `crontab -e` → every 15 min run `idle_shutdown.py` or wrapper |
| Start again | Dashboard → server → **Start**; then start API if needed |

## Notes

- The first request after startup may be slower while the TorchXRayVision model loads.
- For serverless-style scaling, consider offloading the heavy model to a separate inference service and calling it from a lightweight API.
