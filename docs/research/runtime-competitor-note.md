# Runtime Competitor Note

Updated: 2026-06-07

Adjacent desktop agent projects show that LLM harness products should not be plain API wrappers.

Required lessons:
- separate UI from runtime
- expose agent execution as event streams
- preserve stable prompts
- track usage and cache metrics
- maintain long-task state
- prefer model-native message compilation
- use structured context layout
- add checkpoint-based review
