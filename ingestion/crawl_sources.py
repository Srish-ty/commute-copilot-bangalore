from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "sample_data" / "commute_context.crawled.json"


def refresh_commute_context() -> Path:
    """Demo-safe crawler placeholder.

    For the hackathon MVP, live crawling should happen before the demo, not in the
    agent response path. Replace these seeds with Elastic Open Crawler output or
    lightweight requests-based crawls as credentials and source permissions allow.
    """
    now = datetime.now(timezone.utc).isoformat()
    records = [
        {
            "id": "crawl-bmtc-peak-note",
            "title": "BMTC peak-hour buffer",
            "content": "BMTC buses on central corridors can need an extra 10 to 20 minute buffer during evening peak.",
            "source_url": "sample://crawler/bmtc-peak-note",
            "area": "Central Bengaluru",
            "category": "bmtc",
            "created_at": now,
        },
        {
            "id": "crawl-cbd-event-buffer",
            "title": "CBD event buffer",
            "content": "When events occur near MG Road, Cubbon Park, or Church Street, prefer metro for predictable arrival.",
            "source_url": "sample://crawler/cbd-event-buffer",
            "area": "MG Road",
            "category": "event",
            "created_at": now,
        },
    ]
    OUTPUT.write_text(json.dumps(records, indent=2), encoding="utf-8")
    return OUTPUT


if __name__ == "__main__":
    print(f"wrote: {refresh_commute_context()}")
