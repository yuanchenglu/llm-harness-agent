# Runtime PRD Update

Updated: 2026-06-07

MVP requirements added after reviewing adjacent desktop agent products.

Must-have requirements:
- desktop shell connects to a local runtime, not directly to model APIs
- runtime exposes task events, tool calls, file changes, approvals, and usage data
- product shows cache hit, cache miss, model route, and estimated cost
- long tasks have goal, plan, todo, checkpoint, and review states
- context construction is owned by the runtime
- model routing supports size and reasoning-effort axes
- risky actions require checkpoint