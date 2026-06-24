#!/usr/bin/env python3
"""
feature_runner.py — Initialize a new feature in an existing app.

Usage:
    python3 feature_runner.py --app <slug> --name "Feature Name" --description "Feature description"
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# ─── Constants ────────────────────────────────────────────────────────────────
WORKSPACE = Path("/home/moises/workspace")
GSD_HUB = WORKSPACE / "gsd-hub"
DATA_FILE = GSD_HUB / "data" / "provisioned_apps.json"

PHASES = [
    "RESEARCH",
    "BUSINESS_VALIDATION",
    "ARCHITECTURE",
    "UX_DESIGN",
    "PLAN",
    "EXECUTE",
    "UX_REVIEW",
    "TEST",
    "VERIFY",
    "DEPLOY",
]


# ─── Helpers ──────────────────────────────────────────────────────────────────
def slug_to_feature_slug(name: str) -> str:
    """Convert a feature name to a URL-safe slug."""
    return name.lower().replace(" ", "-").replace("_", "-")


# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Initialize a new feature in an existing app.",
    )
    parser.add_argument(
        "--app", required=True,
        help="App slug (must exist in provisioned_apps.json)",
    )
    parser.add_argument(
        "--name", required=True,
        help="Feature display name",
    )
    parser.add_argument(
        "--description", required=True,
        help="Feature description",
    )
    args = parser.parse_args()

    # 1. Read provisioned_apps.json to find the app entry
    if not DATA_FILE.exists():
        print(f"❌ Data file not found: {DATA_FILE}")
        sys.exit(1)

    try:
        with open(DATA_FILE, "r") as f:
            apps = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"❌ Failed to read {DATA_FILE}: {e}")
        sys.exit(1)

    if not isinstance(apps, list):
        apps = [apps]

    app_entry = None
    for entry in apps:
        if entry.get("slug") == args.app:
            app_entry = entry
            break

    if not app_entry:
        print(f"❌ App '{args.app}' not found in {DATA_FILE}")
        sys.exit(1)

    # Derive local path from slug (same convention as provision_app.py)
    local_path = WORKSPACE / args.app
    if not local_path.exists():
        print(f"❌ App directory not found: {local_path}")
        sys.exit(1)

    # 2. Read pipeline-status.json from the app's .planning/
    pipeline_path = local_path / ".planning" / "pipeline-status.json"
    if not pipeline_path.exists():
        print(f"❌ pipeline-status.json not found at {pipeline_path}")
        print("   Make sure the app has been provisioned with Step 7 (init .planning/).")
        sys.exit(1)

    try:
        with open(pipeline_path, "r") as f:
            pipeline = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"❌ Failed to read pipeline-status.json: {e}")
        sys.exit(1)

    # 3. Check if a feature is already in progress
    active_feature = pipeline.get("active_feature")
    if active_feature is not None:
        print(f"❌ Feature '{active_feature['name']}' is already in progress. "
              f"Complete it first.")
        sys.exit(1)

    # 4. Generate next feature ID
    deployed_count = len(pipeline.get("deployed_features", []))
    queued_count = len(pipeline.get("queued_features", []))
    next_num = deployed_count + queued_count + 1
    feature_id = f"{next_num:02d}"
    feature_slug = slug_to_feature_slug(args.name)

    # 5. Create feature directory inside .planning/features/
    features_dir = local_path / ".planning" / "features"
    feature_dir = features_dir / f"{feature_id}-{feature_slug}"
    feature_dir.mkdir(parents=True, exist_ok=True)
    print(f"   ✅ Created feature directory: {feature_dir}")

    # 6. Create empty tasks/ subdir inside the feature dir
    tasks_dir = feature_dir / "tasks"
    tasks_dir.mkdir(exist_ok=True)
    print(f"   ✅ Created tasks/ directory")

    # 7. Build active feature object
    now = datetime.now(timezone.utc).isoformat()
    phases = []
    for phase_name in PHASES:
        is_current = phase_name == "RESEARCH"
        phases.append({
            "name": phase_name,
            "status": "in_progress" if is_current else "pending",
            "started_at": now if is_current else None,
            "completed_at": None,
            "duration_sec": None,
            "result": None,
            "ux_score": None,
        })

    new_active_feature = {
        "id": feature_id,
        "name": args.name,
        "description": args.description,
        "started_at": now,
        "current_phase": "RESEARCH",
        "phases": phases,
        "tasks": [],
        "rework_count": 0,
        "ux_score": None,
    }

    # 8. Update pipeline-status.json
    pipeline["active_feature"] = new_active_feature
    pipeline["updated_at"] = now

    # Write updated JSON back
    with open(pipeline_path, "w") as f:
        json.dump(pipeline, f, indent=2)
        f.write("\n")

    # 10. Print summary
    print(f"\n🚀 Feature initialized: {args.name} [{feature_id}]")
    print(f"   App:       {args.app}")
    print(f"   ID:        {feature_id}")
    print(f"   Slug:      {feature_slug}")
    print(f"   Directory: {feature_dir}")
    print(f"   Phase:     RESEARCH (in_progress)")
    print(f"   Started:   {now}")
    print(f"\n✅ Feature '{args.name}' initialized successfully.")


if __name__ == "__main__":
    main()
