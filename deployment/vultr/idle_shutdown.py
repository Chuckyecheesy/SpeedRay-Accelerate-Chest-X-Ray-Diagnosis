#!/usr/bin/env python3
"""
Idle shutdown for SpeedRay on Vultr: halt the instance when the frontend/API
has had no activity (no requests except / and /health) for IDLE_THRESHOLD_MINUTES.

Run from project root on the Vultr server via cron, e.g. every 15 minutes:
  */15 * * * * cd /opt/speedray && /opt/speedray/venv/bin/python deployment/vultr/idle_shutdown.py

Requires: VULTR_API_KEY, VULTR_INSTANCE_ID in environment.
Optional: SPEEDRAY_ACTIVITY_FILE (default: ./.speedray_last_activity),
          SPEEDRAY_IDLE_THRESHOLD_MINUTES (default: 30).
"""

import os
import sys

try:
    import requests
except ImportError:
    print("idle_shutdown: requests not installed; pip install requests", file=sys.stderr)
    sys.exit(1)

VULTR_HALT_URL = "https://api.vultr.com/v2/instances/halt"
DEFAULT_ACTIVITY_FILE = ".speedray_last_activity"
DEFAULT_IDLE_MINUTES = 30


def main() -> int:
    api_key = os.environ.get("VULTR_API_KEY", "").strip()
    instance_id = os.environ.get("VULTR_INSTANCE_ID", "").strip()
    if not api_key or not instance_id:
        print("idle_shutdown: set VULTR_API_KEY and VULTR_INSTANCE_ID", file=sys.stderr)
        return 1

    activity_file = os.environ.get("SPEEDRAY_ACTIVITY_FILE", DEFAULT_ACTIVITY_FILE)
    if not os.path.isabs(activity_file):
        activity_file = os.path.join(os.getcwd(), activity_file)
    idle_minutes = int(os.environ.get("SPEEDRAY_IDLE_THRESHOLD_MINUTES", str(DEFAULT_IDLE_MINUTES)))

    try:
        with open(activity_file, "r") as f:
            last_ts = int(f.read().strip())
    except (FileNotFoundError, ValueError, OSError):
        last_ts = 0

    import time as _time
    now = int(_time.time())
    idle_seconds = now - last_ts
    threshold_seconds = idle_minutes * 60

    if idle_seconds < threshold_seconds:
        return 0  # still active, do nothing

    resp = requests.post(
        VULTR_HALT_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={"instance_ids": [instance_id]},
        timeout=30,
    )
    if resp.status_code == 200:
        print("idle_shutdown: instance halted (idle {:.0f} min).".format(idle_seconds / 60))
        return 0
    print("idle_shutdown: halt failed: {} {}".format(resp.status_code, resp.text), file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
