# OpenCode Adapter Spike：固定源码审计与集成边界

> 官方仓库：`anomalyco/opencode`；固定 commit：`7f54b1bfb83b57fd3cdab063fe7808f55d49fcfe`（2026-06-04）；证据等级：E1 源码事实。已在该固定快照运行两个 targeted tests：custom DeepSeek interleaved reasoning provider test 与 reasoning details message transform test，均通过；这仍不等于 DeepSeek V4 live adapter 通过。

## 已确认的源码事实

1. OpenCode 支持 `@ai-sdk/openai-compatible` custom provider、`baseURL` 和自定义模型；本仓库提供 `integrations/opencode/opencode.deepseek.example.jsonc`。
2. provider test 明确验证 custom DeepSeek OpenAI-compatible 模型默认使用 `reasoning_content` 作为 interleaved reasoning 字段。
3. `ProviderTransform.message` 对 model id 含 `deepseek` 的 assistant message 补充 reasoning part，并将 interleaved reasoning 映射到 provider-specific field。
4. OpenCode token accounting 已将 cache read/write token 独立归一化，但是否能准确读取 DeepSeek V4 的两个 cache usage 字段仍需 live adapter 验证。
5. native runtime 只直接支持 provider id 为 `openai`、`anthropic` 或 `opencode*`；自定义 `deepseek-direct` 会落到 AI SDK runtime，而不是 native runtime。

## 与 DeepSeek V4 官方协议的差异风险

DeepSeek V4 官方文档称：无工具调用的历史 reasoning 可忽略；发生工具调用时必须回传。OpenCode 当前 DeepSeek transform 更保守地为所有 assistant messages 提供 reasoning 字段。该策略可能兼容协议，但对 Prefix Cache、输入 token 与真实语义的影响尚未验证。

## Spike 结论

- **可配置性：通过（E1）**；
- **reasoning field 源码适配：通过（E1 + 固定快照 targeted tests）**；
- **V4 Flash/Pro live tool-loop：未验证**；
- **DeepSeek cache telemetry 完整性：未验证**；
- **Prefix layout 控制力：未验证**；
- **是否 Fork：暂不决定**。先运行统一真实任务与协议矩阵，再比较 OpenCode Adapter 与小型自研 runtime。

因此，这次 Spike 不能写成“OpenCode 整合完成”，只能证明它是 Stage 6 的有效候选底座。
