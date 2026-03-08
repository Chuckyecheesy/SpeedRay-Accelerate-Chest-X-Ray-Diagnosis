#!/usr/bin/env python3
"""Test the diagnostic summary component (deterministic report from top finding).

Run from project root:
  python test_diagnostic_summary.py              # unit-style tests
  python test_diagnostic_summary.py --api        # require server on :8000, hit POST /report/diagnostic-summary
"""

import argparse
import json
import sys
from pathlib import Path

root = Path(__file__).resolve().parent
sys.path.insert(0, str(root))


def test_unit():
    """Test get_diagnostic_summary() directly (no server)."""
    from backend.ai_agents.diagnostic_summary import get_diagnostic_summary

    cases = [
        {
            "filename": "atelectasis.jpeg",
            "top_critical": {"name": "Atelectasis", "score": 0.58, "risk": "Moderate"},
        },
        {
            "filename": "pneumothorax.jpeg",
            "top_critical": {"name": "Pneumothorax", "score": 0.72, "risk": "High"},
        },
        {
            "filename": "mass.jpeg",
            "top_critical": {"name": "Mass", "score": 0.45, "risk": "Low"},
        },
        {
            "filename": "unknown.jpeg",
            "top_critical": {"name": "Pleural Thickening", "score": 0.5, "risk": "Low"},
        },
    ]

    print("Unit tests: get_diagnostic_summary()\n")
    for i, inp in enumerate(cases, 1):
        out = get_diagnostic_summary(inp["filename"], inp["top_critical"])
        assert "top_finding" in out and "risk" in out and "explanation" in out and "recommended_next_steps" in out
        print(f"--- Case {i}: {inp['top_critical']['name']} ---")
        print(json.dumps(out, indent=2))
        print()
    print("All unit checks passed.\n")


def test_api(base_url: str = "http://localhost:8000"):
    """Call POST /report/diagnostic-summary (server must be running)."""
    try:
        import urllib.request
    except ImportError:
        import urllib.request  # noqa

    url = f"{base_url.rstrip('/')}/report/diagnostic-summary"
    body = json.dumps({
        "filename": "edema.jpg",
        "top_critical": {"name": "Edema", "score": 0.65, "risk": "High"},
    }).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            print("API test: POST /report/diagnostic-summary\n")
            print(json.dumps(data, indent=2))
            assert "top_finding" in data and "risk" in data
            print("\nAPI check passed.")
    except urllib.error.URLError as e:
        print(f"Cannot reach {url}: {e}")
        print("Start the backend first: cd backend && uvicorn api.main:app --reload")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Test diagnostic summary component")
    parser.add_argument("--api", action="store_true", help="Test via API (server must be on :8000)")
    parser.add_argument("--base-url", default="http://localhost:8000", help="API base URL (default: http://localhost:8000)")
    args = parser.parse_args()

    test_unit()
    if args.api:
        test_api(args.base_url)


if __name__ == "__main__":
    main()
