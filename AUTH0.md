# Auth0 login — run & troubleshoot

## Run the app

1. **Backend** (from project root):
   ```bash
   uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8001
   ```

2. **Frontend** (in another terminal):
   ```bash
   npm run dev
   ```
   Open the URL Vite prints (e.g. **http://localhost:5173** or **http://localhost:3006**).

3. Click **Sign In as Professional** → you should be sent to Auth0, then back to the app.

---

## Option A: Auth0 Application URIs (copy‑paste)

Use the **same port** Vite shows in the terminal (e.g. `3006`). Replace `3006` with your port if different.

**Applications → My App → Settings → Application URIs**

- **Application Login URI** (Initiate login uri): Leave this field **completely empty** (no text, no spaces). Auth0 only accepts HTTPS in this field, so `http://localhost` will cause a validation error. Empty is valid. If the UI won’t save when empty, use a placeholder HTTPS URL you control (e.g. `https://yourdomain.com`) so the format passes; it does not affect local login.

- **Allowed Callback URLs** (one per line):
  ```
  http://localhost:3006/callback
  http://127.0.0.1:3006/callback
  ```

- **Allowed Logout URLs** (one per line):
  ```
  http://localhost:3006
  http://127.0.0.1:3006
  ```

- **Allowed Web Origins** (one per line):
  ```
  http://localhost:3006
  http://127.0.0.1:3006
  ```

Replace `3006` with the port Vite actually shows (e.g. `Local: http://localhost:3006/`). Then click **Save Changes** and open the app at that URL.

---

## If you see "Connection Failed"

- **After clicking Sign In**  
  The port in the browser must match Auth0. Use the URIs above for the port Vite actually uses, and open the app at that URL (e.g. http://localhost:3006).

- **On the first load**  
  Start the frontend with `npm run dev` and open the URL Vite prints.

- **On the Auth0 login page**  
  Disable ad blockers for Auth0, or try another network. Confirm Allowed Callback URLs includes your app’s `/callback` URL for the port you use.
