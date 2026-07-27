#!/usr/bin/env python3
"""Validate repository stage state and public status documents.

This verifier intentionally uses only the Python standard library so it can run
in a clean GitHub Actions environment without installing dependencies.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
GATES_PATH = ROOT / "zh" / "blueprint" / "stage-gates.json"
STATUS_PATH = ROOT / "STATUS.md"
PUBLIC_STATUS_DOCS = [
    ROOT / "README.md",
    ROOT / "STATUS.md",
    ROOT / "zh" / "prd-tech-plan" / "README.md",
    ROOT / "zh" / "prd-tech-plan" / "04-roadmap-and-release-gates.md",
]

FORBIDDEN_CURRENT_CLAIMS = {
    "当前没有最早未完成项": "Use the machine-readable earliest_incomplete_stage value.",
    "Earliest incomplete stage 是 `null`": "Use the machine-readable earliest_incomplete_stage value.",
    "Stage 6 status 是 `completed`": "Stage 6 research MVP and product release status must be separated.",
    "`production_release_gate` 已关闭": "A verified release requires immutable external evidence.",
    "production release gate 已关闭": "A verified release requires immutable external evidence.",
    "生产 Release Gate 已关闭": "A verified release requires immutable external evidence.",
}


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def load_json(path: Path, errors: list[str]) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(errors, f"Missing file: {path.relative_to(ROOT)}")
    except json.JSONDecodeError as exc:
        fail(errors, f"Invalid JSON in {path.relative_to(ROOT)}: {exc}")
    return {}


def validate_gate_structure(data: dict[str, Any], errors: list[str]) -> None:
    required = {
        "schema_version",
        "assessed_at",
        "repository_scope",
        "truth_source",
        "earliest_incomplete_stage",
        "stages",
        "product_release",
    }
    missing = sorted(required - data.keys())
    if missing:
        fail(errors, f"stage-gates.json missing keys: {', '.join(missing)}")
        return

    if data.get("schema_version") != "3.0":
        fail(errors, "stage-gates.json schema_version must be 3.0")

    stages = data.get("stages")
    if not isinstance(stages, dict) or not stages:
        fail(errors, "stage-gates.json stages must be a non-empty object")
        return

    incomplete: list[str] = []
    for stage_id, stage in stages.items():
        if not isinstance(stage, dict):
            fail(errors, f"Stage {stage_id} must be an object")
            continue
        for key in ("name", "status", "passed", "open"):
            if key not in stage:
                fail(errors, f"Stage {stage_id} missing {key}")
        open_items = stage.get("open", [])
        status = stage.get("status")
        if not isinstance(open_items, list):
            fail(errors, f"Stage {stage_id} open must be an array")
            continue
        if status == "completed" and open_items:
            fail(errors, f"Stage {stage_id} is completed but still has open items")
        if status != "completed" or open_items:
            incomplete.append(stage_id)

    earliest = data.get("earliest_incomplete_stage")
    if incomplete and earliest is None:
        fail(errors, "earliest_incomplete_stage cannot be null while stages remain incomplete")
    if not incomplete and earliest is not None:
        fail(errors, "earliest_incomplete_stage must be null when every stage is completed")


def validate_release_evidence(data: dict[str, Any], errors: list[str]) -> None:
    release = data.get("product_release")
    if not isinstance(release, dict):
        fail(errors, "product_release must be an object")
        return

    required_keys = {
        "status",
        "reason",
        "required_external_evidence",
        "evidence",
    }
    missing = sorted(required_keys - release.keys())
    if missing:
        fail(errors, f"product_release missing keys: {', '.join(missing)}")
        return

    status = release.get("status")
    required_types = release.get("required_external_evidence", [])
    evidence = release.get("evidence", [])
    if not isinstance(required_types, list) or not all(isinstance(x, str) for x in required_types):
        fail(errors, "required_external_evidence must be an array of strings")
        return
    if not isinstance(evidence, list):
        fail(errors, "product_release evidence must be an array")
        return

    evidence_types = {
        item.get("type")
        for item in evidence
        if isinstance(item, dict) and isinstance(item.get("type"), str)
    }

    if status == "verified_released":
        missing_evidence = sorted(set(required_types) - evidence_types)
        if missing_evidence:
            fail(
                errors,
                "verified_released is missing required evidence: "
                + ", ".join(missing_evidence),
            )
        if data.get("earliest_incomplete_stage") is not None:
            fail(errors, "verified_released requires earliest_incomplete_stage=null")
    else:
        if data.get("earliest_incomplete_stage") is None:
            fail(errors, "An unverified release must keep an explicit incomplete stage")


def validate_public_docs(errors: list[str]) -> None:
    for path in PUBLIC_STATUS_DOCS:
        if not path.exists():
            fail(errors, f"Missing public status document: {path.relative_to(ROOT)}")
            continue
        text = path.read_text(encoding="utf-8")
        for phrase, guidance in FORBIDDEN_CURRENT_CLAIMS.items():
            if phrase in text:
                fail(
                    errors,
                    f"{path.relative_to(ROOT)} contains stale current-state claim "
                    f"{phrase!r}. {guidance}",
                )

    status_text = STATUS_PATH.read_text(encoding="utf-8") if STATUS_PATH.exists() else ""
    if "stage-gates.json" not in status_text:
        fail(errors, "STATUS.md must link to stage-gates.json")


def main() -> int:
    errors: list[str] = []
    data = load_json(GATES_PATH, errors)
    if data:
        validate_gate_structure(data, errors)
        validate_release_evidence(data, errors)
    validate_public_docs(errors)

    if errors:
        print("Documentation state verification failed:", file=sys.stderr)
        for index, error in enumerate(errors, start=1):
            print(f"{index}. {error}", file=sys.stderr)
        return 1

    print("Documentation state verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
