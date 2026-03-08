# Tailscale setup for SpeedRay secure demo

1. Install Tailscale on the demo server and on client machines.
2. Create an ACL that allows demo users to reach the SpeedRay app (e.g. tag:demo).
3. Use the Tailscale IP of the server for VITE_API_BASE in the frontend when on the demo network.

See `acl.example.json` for a sample ACL.
