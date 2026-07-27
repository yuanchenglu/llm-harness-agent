#!/usr/bin/env python3
"""Validate repository status, canonical research articles, and local links.

The verifier intentionally uses only the Python standard library so it can run
in a clean GitHub Actions environment without dependency installation.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
GATES_PATH = ROOT / "zh" / "blueprint" / "stage-gates.json"
SCHEMA_PATH = ROOT / "schemas" / "stage-gates.schema.json"
STATUS_PATH = ROOT / "STATUS.md"
INNOVATIONS_DIR = ROOT / "zh" / "innovations"

PUBLIC_STATUS_DOCS = [
    ROOT / "README.md",
    ROOT / "README_en.md",
    ROOT / "STATUS.md",
    ROOT / "zh" / "blueprint" / "README.md",
    ROOT / "zh" / "prd-tech-plan" / "README.md",
    ROOT / "zh" / "prd-tech-plan" / "04-roadmap-and-release-gates.md",
    ROOT / "zh" / "prd-tech-plan" / "07-plan-assets" / "README.md",
]

CANONICAL_INNOVATIONS = [
    "01-agent-immune-system.md",
    "02-bidirectional-agent.md",
    "03-attention-budget.md",
    "04-kv-cache-prefix.md",
    "05-document-kv-cache.md",
    "06-okr-planstep-cascade.md",
    "07-review-switching.md",
    "08-scope-creep.md",
    "09-skills-self-evolution.md",
    "10-intent-routing.md",
    "11-checkpoint-review.md",
    "12-memory-granularity.md",
    "13-byte-stable-prefix-architecture.md",
    "14-reasoning-content-stripping.md",
    "15-dsml-tool-call-optimization.md",
    "16-quick-instruction-routing.md",
    "17-reasoning-effort-control.md",
    "18-latest-reminder-injection.md",
]

FORBIDDEN_CURRENT_CLAIMS = {
    "当前没有最早未完成项": "Use the machine-readable earliest_incomplete_stage value.",
    "Earliest incomplete stage 是 `null`": "Use the machine-readable earliest_incomplete_stage value.",
    "Stage 6 status 是 `completed`": "Separate research MVP status from release status.",
    "`production_release_gate` 已关闭": "A verified release requires immutable external evidence.",
    "production release gate 已关闭": "A verified release requires immutable external evidence.",
    "生产 Release Gate 已关闭": "A verified release requires immutable external evidence.",
}

MARKDOWN_LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")


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


def normalize_link_target(raw_target: str) -> str:
    target = raw_target.strip()
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1]
    return unquote(target.split("#", 1)[0].split("?", 1)[0])


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
        passed_items = stage.get("passed", [])
        status = stage.get("status")
        if not isinstance(open_items, list):
            fail(errors, f"Stage {stage_id} open must be an array")
            continue
        if not isinstance(passed_items, list):
            fail(errors, f"Stage {stage_id} passed must be an array")
            continue
        if status == "completed" and open_items:
            fail(errors, f"Stage {stage_id} is completed but still has open items")
        if set(open_items) & set(passed_items):
            fail(errors, f"Stage {stage_id} has items in both passed and open")
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
    elif data.get("earliest_incomplete_stage") is None:
        fail(errors, "An unverified release must keep an explicit incomplete stage")


def iter_current_docs() -> list[Path]:
    article_paths = [INNOVATIONS_DIR / name for name in CANONICAL_INNOVATIONS]
    return PUBLIC_STATUS_DOCS + article_paths


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

    english_readme = (ROOT / "README_en.md").read_text(encoding="utf-8")
    if "current canonical versions" not in english_readme:
        fail(errors, "README_en.md must state that current Chinese innovation articles are canonical")

    stale_english_links = [
        normalize_link_target(raw_target)
        for raw_target in MARKDOWN_LINK_RE.findall(english_readme)
        if normalize_link_target(raw_target).startswith("en/innovations/")
    ]
    if stale_english_links:
        fail(
            errors,
            "README_en.md must not link readers to stale English innovation articles: "
            + ", ".join(sorted(set(stale_english_links))),
        )


def validate_innovations(errors: list[str]) -> None:
    for name in CANONICAL_INNOVATIONS:
        path = INNOVATIONS_DIR / name
        if not path.exists():
            fail(errors, f"Missing canonical innovation article: {path.relative_to(ROOT)}")
            continue
        text = path.read_text(encoding="utf-8")
        if "证据等级" not in text:
            fail(errors, f"{path.relative_to(ROOT)} must declare an evidence level")
        if "研究方法与事实校准" not in text:
            fail(errors, f"{path.relative_to(ROOT)} must link the research method")
        if "系列" not in text or "README.md" not in text:
            fail(errors, f"{path.relative_to(ROOT)} must link the canonical series entry")


def validate_local_links(errors: list[str]) -> None:
    for path in iter_current_docs():
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for raw_target in MARKDOWN_LINK_RE.findall(text):
            target = normalize_link_target(raw_target)
            if not target:
                continue
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            destination = (path.parent / target).resolve()
            try:
                destination.relative_to(ROOT.resolve())
            except ValueError:
                fail(errors, f"{path.relative_to(ROOT)} links outside repository: {raw_target}")
                continue
            if not destination.exists():
                fail(errors, f"Broken local link in {path.relative_to(ROOT)}: {raw_target}")


def main() -> int:
    errors: list[str] = []
    if not SCHEMA_PATH.exists():
        fail(errors, f"Missing schema: {SCHEMA_PATH.relative_to(ROOT)}")
    else:
        load_json(SCHEMA_PATH, errors)

    data = load_json(GATES_PATH, errors)
    if data:
        validate_gate_structure(data, errors)
        validate_release_evidence(data, errors)
    validate_public_docs(errors)
    validate_innovations(errors)
    validate_local_links(errors)

    if errors:
        print("Documentation integrity verification failed:", file=sys.stderr)
        for index, error in enumerate(errors, start=1):
            print(f"{index}. {error}", file=sys.stderr)
        return 1

    print("Documentation integrity verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
