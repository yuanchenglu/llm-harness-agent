# Research Method and Evidence Calibration

This project distinguishes five kinds of statements:

```text
A0  fixed-commit runtime path plus tests
A1  fixed-commit implementation source, runtime effect not yet verified
A2  official README/docs/config claim
B   engineering inference or proposed design
C   unofficial reverse-engineering/community lead
N   no implementation found in public evidence
```

A module existing is not proof that it is wired into the request path. A product claim is not a benchmark. A benchmark on one task is not a universal law.

## Important Corrections

- “Model gains are linear and Harness gains are exponential” is rhetoric, not a mathematical result.
- Long context creates layout and retrieval challenges, but it is not universally true that more context always makes a model worse.
- CodeWhale is a community project built around DeepSeek models, not an official DeepSeek product.
- CodeWhale wires prefix drift checks for system prompt and tools; its full three-zone request contract is still marked as not wired.
- Trae Agent exposes an Agent loop, trajectory, Docker, MCP, and stateful sequential thinking, but no public multi-candidate generation–pruning–selection runtime was found.
- Reasoning content must not be universally dropped or replayed; behavior depends on provider contract and mode.
- Most chat APIs still require the complete tools field per request. Prompt caching is not the same as a protocol that accepts tool-schema deltas.
- Hermes is valuable as an integrated Agent OS design; claims that it is the only platform with memory, skills, or scheduling should be avoided.

## Writing Standard

Each paper should separate problem definition, observed facts, hypotheses, proposed design, boundary conditions, validation method, and evidence status. Prefer “confirmed in this fixed version” or “awaiting benchmark” over “the only implementation,” “always,” or “proven optimal.”
