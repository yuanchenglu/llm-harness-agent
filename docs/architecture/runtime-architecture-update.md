# Runtime Architecture Update

Updated: 2026-06-07

The harness architecture should absorb the proven desktop-runtime split from adjacent agent projects.

Architecture decisions:
- keep UI out of the agent loop
- run tools, memory, planning, routing, and telemetry in the runtime layer
- expose execution events to the UI through streaming
- make cache metrics a first-class runtime output
- keep context layout in the runtime, not in the UI
- add checkpoint records before risky or irreversible actions
