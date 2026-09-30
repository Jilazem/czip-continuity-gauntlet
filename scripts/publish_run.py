#!/usr/bin/env python3
"""Make a shareable copy of one synthetic run while hiding its local endpoint.

The original files are left untouched. Review the generated copy before
publishing; only the endpoint is redacted automatically.
"""

import argparse
import hashlib
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="run directory created by bench.py")
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    source_json = args.source / "results.json"
    source_report = args.source / "report.md"
    raw = source_json.read_bytes()
    record = json.loads(raw)
    old_endpoint = record["endpoint"]
    if not old_endpoint:
        raise ValueError("run has no endpoint to redact")
    original_hash = hashlib.sha256(raw).hexdigest()
    record["endpoint"] = "local endpoint (redacted)"
    record["publication"] = {
        "redacted_fields": ["endpoint"],
        "local_source_results_sha256": original_hash,
        "note": "Only the endpoint was redacted from this synthetic run copy.",
    }
    args.destination.mkdir(parents=True, exist_ok=True)
    public_json = args.destination / "results.json"
    public_json.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n",
                           encoding="utf-8")
    report = source_report.read_text(encoding="utf-8")
    if old_endpoint not in report:
        raise ValueError("endpoint not found in Markdown report")
    report = report.replace(old_endpoint, "local endpoint (redacted)")
    marker = "# Czip Continuity Gauntlet — Run Report\n"
    if marker not in report:
        raise ValueError("unexpected Markdown report title")
    report = report.replace(marker, marker + "\n*Public copy: local endpoint redacted; "
                            f"original results.json SHA-256 `{original_hash}`.*\n", 1)
    (args.destination / "report.md").write_text(report, encoding="utf-8")
    print(f"Wrote {public_json} and report.md; original SHA-256 {original_hash}")


if __name__ == "__main__":
    main()
