# Agent-Readable Document Structure: Stable Summaries, Content Addressing, and On-Demand Reading

> **Evidence level: B (engineering design proposal)**  
> This article corrects the earlier claim that placing core conclusions at the beginning of a file automatically produces full Prefix Cache hits and an 80% token reduction. Document ordering, Harness reading strategy, and Provider Prefix Cache are different layers. Actual benefit depends on whether request assembly preserves a common prefix and whether the Agent reads only the sections it needs. Read [Research Method and Evidence Calibration](../theory/research-method.md) first.

> **Innovation index**: I-05  
> **Series**: [LLM + Harness = Agent](../../README_en.md)  
> **Previous**: [04 Stable Constraints and Compressible History](04-kv-cache-prefix.md)

---

## Abstract

Large project documents commonly serve four responsibilities at once:

- current conclusions;
- decision rationale;
- complete analysis;
- historical discussion and change records.

Reading the entire document for every task causes cost and interference to grow with document size. Reading only a summary can omit critical boundaries and evidence.

A more reliable structure is:

```text
machine-readable metadata
→ current conclusions and decisions
→ Evidence Index
→ topic-oriented body
→ history and appendices
```

The Harness then selects among:

```text
read summary only
read selected sections
fetch original material by Evidence Ref
read the full document when necessary
```

This is first an information-architecture and retrieval design. Provider Prefix Cache benefits are possible only when the assembled request preserves an actual common prefix.

---

## 1. Public Corrections

### 1.1 A stable file prefix is not necessarily a stable API request prefix

Before document content reaches the model, the Harness may prepend:

- a System Prompt;
- Tool Schemas;
- the user question;
- file paths and timestamps;
- Retrieval wrappers;
- fragments from other documents.

Even if the first 500 document tokens remain unchanged, a change in preceding content, order, or serialization may change actual Prefix Cache behavior.

### 1.2 “Append to the end, recompute only the end” has prerequisites

Common-prefix reuse may be observed only when all of the following hold:

```text
same Provider / Model / Endpoint
same serialization
same preceding messages
same document prefix
cache remains valid
Provider exposes observable Prefix Cache behavior
```

A filesystem append operation therefore cannot be equated directly with incremental inference-service computation.

### 1.3 Earlier token-saving arithmetic was inconsistent

Earlier versions stated both:

```text
core conclusions U ≈ 0.3S
```

and “roughly 70% or more than 80% savings.” If only a stable prefix of size `U` is cached and the remaining `D = S-U` is still sent, the theoretical upper bound is closer to `U/S`, not `D/S`. Provider billing, minimum cache blocks, and request wrappers further change the result.

This article therefore no longer states a fixed saving rate without experiments.

### 1.4 The stable zone cannot remain immutable forever

New evidence can overturn a core conclusion. Document design must support:

- versioned updates;
- invalidation of old conclusions;
- supersession relationships between decisions;
- reasons for change;
- clear identification of the current version.

Freezing an incorrect conclusion for cache stability is negative optimization.

---

## 2. Design Goals

An Agent-readable document should optimize all of the following:

| Goal | Meaning |
| --- | --- |
| Fast orientation | State current conclusions and applicable scope near the beginning |
| Traceability | Every strong claim can be traced to a source and Evidence |
| Updatability | Changed conclusions carry versions and supersession relationships |
| Retrievability | Sections have stable IDs, titles, tags, and hashes |
| Selective reading | Summary, section, Artifact, and full-document levels can be loaded separately |
| Verifiable cache | Request Fingerprints, hit/miss data, and cost can be measured |
| Human readability | Machine structure does not destroy basic reading quality |

---

## 3. Recommended Structure

```markdown
---
doc_id: architecture-context-compiler
schema_version: 1
revision: 7
status: active
updated_at: 2026-07-27
supersedes: revision-6
owners: [runtime-team]
tags: [context, cache, evidence]
---

# Context Compiler Architecture
## Current Summary

## Scope and Non-Goals

## Decision Register

## Evidence Index

## Architecture

## Failure Modes

## Validation

## Change Log

## Historical Discussion
```

### 3.1 Current Summary

Answer only:

```text
what is the current conclusion?
what scope does it apply to?
what remains unverified?
what happens next?
```

Do not use marketing language and do not present a historical plan as current fact.

### 3.2 Scope and Non-Goals

State explicitly what the document does not solve so a later Agent does not automatically absorb adjacent requirements into scope.

### 3.3 Decision Register

```yaml
- decision_id: ADR-014
  status: accepted
  statement: Runtime is the single source of truth for the Agent Loop
  rationale_ref: section:architecture/runtime
  evidence_refs:
    - source:runtime-commit-abc
    - test:bridge-integration-22
  supersedes: null
```

### 3.4 Evidence Index

The Evidence Index stores references and summaries only:

```text
source repository / commit
file and line range
experiment manifest
artifact hash
test report
accessed or generated date
limitations
```

Store large originals in external Artifacts or a separate directory and read them on demand.

### 3.5 Historical Discussion

Historical discussion remains valuable but should not enter the active context by default. Each section should state its date, status, and whether it has been superseded.

---

## 4. Stable Section IDs and Content Addressing

Headings may change. Each critical section should therefore have a stable ID:

```html
<a id="decision-runtime-single-loop"></a>
```

or a machine index entry:

```yaml
section_id: decision-runtime-single-loop
heading: Runtime Single Source of Truth
content_hash: sha256:...
revision: 3
```

Uses include:

- precise citation;
- detecting whether a section changed;
- re-embedding only changed sections;
- determining whether an earlier Review is stale;
- generating a stable Retrieval Key.

A hash is not a semantic version. A minor wording change also changes a hash, so retain both Revision and change type.

---

## 5. Reading Strategy

### 5.1 Level 0: Metadata

Used for search and routing:

```text
doc_id
status
revision
tags
updated_at
```

### 5.2 Level 1: Summary + Scope

Used to determine quickly whether the document is relevant.

### 5.3 Level 2: Selected Sections

Load Architecture, Failure Modes, Validation, or other selected sections according to the task.

### 5.4 Level 3: Evidence

Read fixed source, reports, Diffs, or Tests when a conclusion must be proven.

### 5.5 Level 4: Full Document

Appropriate for:

- comprehensive audit;
- broad refactoring;
- a conflict between summary and evidence;
- low Retrieval confidence;
- an explicit user request to read the whole document.

The Harness must record the actual reading level. It must not claim “the document was fully reviewed” after reading only the Summary.

---

## 6. Prompt Assembly and Cache

### 6.1 Deterministic assembly

```text
Stable System Rules
Stable Tool Schema
Document Metadata
Document Summary
Selected Sections
Current User Task
```

Requirements:

- stable ordering;
- normalized newlines and encoding;
- explicit serialization version;
- no random timestamp injected into the stable prefix;
- dynamic information placed in the suffix;
- security updates may deliberately invalidate the prefix.

### 6.2 Fingerprint

```yaml
prompt_layout_version: 2
provider: deepseek
model: deepseek-v4-pro
stable_prefix_hash: sha256:...
document_revision: 7
selected_sections:
  - current-summary
  - decision-runtime-single-loop
```

### 6.3 Telemetry

```text
input tokens
selected document tokens
cache hit/miss tokens
TTFT
total latency
retrieval misses
source citation accuracy
task success
```

Cache and token metrics matter only when task quality does not decline.

---

## 7. Validation Design

Compare three strategies:

```text
A. read the full document every time
B. read only a free-form summary
C. structured Summary + Selected Sections + Evidence on demand
```

The task set should include:

- querying the current conclusion;
- locating boundary conditions;
- tracing evidence for a decision;
- identifying an obsolete conclusion;
- modifying a system according to the document;
- detecting a conflict between summary and body.

Metrics:

```text
answer correctness
current-version accuracy
source citation accuracy
missed constraint rate
input tokens
latency
cache hit/miss
human correction rate
```

Use repeated runs and held-out questions. Do not evaluate only on questions written specifically for the Summary.

---

## 8. Document Quality Gate

Every current document should be checked for:

- current status and date;
- distinction between facts, inferences, and plans;
- Evidence Refs for strong claims;
- broken links;
- references to nonexistent local paths;
- duplicated or conflicting state;
- explicit labels on historical content;
- consistency between Summary and body;
- monotonic Revision updates;
- redaction of Secrets.

Scripts can automatically check metadata, links, JSON, hashes, and state phrases, but semantic consistency still requires Review.

---

## 9. Boundaries and Risks

- a Summary omits detail;
- Retrieval can miss relevant sections;
- excessively fine sectioning can destroy global meaning;
- an oversized Stable Prefix can reduce flexibility;
- cache behavior varies by Provider;
- human-reading and machine-parsing needs can conflict;
- older Agents may not understand new Front Matter;
- content hashes can create meaningless frequent invalidation.

The system must allow full-document fallback, explicit refresh, and manual navigation.

---

## 10. Conclusion

The core of Agent-readable documentation is not “put the TL;DR first and automatically save 80% of tokens.” It is:

1. separate current conclusions, scope, decisions, and evidence;
2. keep historical discussion out of the active working set by default;
3. give sections stable IDs, Revisions, and content hashes;
4. let the Harness read by Metadata, Summary, Section, Evidence, or Full Document levels;
5. use deterministic Prompt Assembly and measure actual Cache behavior;
6. prioritize correctness over prefix stability when new evidence overturns an old conclusion.

Document structure should first serve accurate retrieval and traceable decisions. Prefix Cache is only a possible additional benefit.
