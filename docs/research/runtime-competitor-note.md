# Runtime Competitor Note

Updated: 2026-06-07

Adjacent desktop agent projects show that LLM harness products should separate UI from runtime, expose runtime events, preserve stable prompts, track usage, and maintain long task state.

Design implications:
- keep UI and runtime separated
- use event streaming for agent execution
- make cache telemetry visible
- avoid generic API wrapper architecture
- prioritize model-native message compilation
- use structured context layout
- add