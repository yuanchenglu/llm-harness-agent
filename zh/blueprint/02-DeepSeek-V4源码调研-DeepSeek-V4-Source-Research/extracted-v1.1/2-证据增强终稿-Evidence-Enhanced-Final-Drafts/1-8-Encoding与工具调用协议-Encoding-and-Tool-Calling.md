# 1-8 Encoding与工具调用协议 Encoding and Tool Calling

## 1. V4 不使用传统 Jinja chat template

官方模型卡说明，本次 release 不包含 Jinja-format chat template，而是提供 `encoding` 文件夹，用 Python 脚本演示如何将 OpenAI-compatible messages 编码为模型输入，并解析模型输出。证据：[README Chat Template](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/README.md#L327-L329)。

## 2. Encoding 文档的职责

`encoding/README.md` 明确说明，V4 encoding 处理 multi-turn conversations、tool calling、extended thinking、quick instruction tasks，并提供 `encoding_dsv4.py` 作为自包含参考实现。证据：[Encoding 概览](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/encoding/README.md#L194-L214)。

## 3. thinking / non-thinking

Encoding 文档说明：

- chat mode 下，`</think>` 会放在 `<｜Assistant｜>` 后面，立即关闭 thinking block。
- thinking mode 下，模型会在 `<think>...</think>` 内生成 reasoning。
- `drop_thinking` 默认 True；无 tools 时会剥离早期 assistant reasoning；有 tools 时会自动禁用 drop_thinking，以便保留多步工具推理上下文。

证据：[Encoding tokens and thinking](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/encoding/README.md#L217-L250)。

## 4. Tool calling 使用 DSML

Encoding 文档说明，tools 定义放在 system / developer message 的 `tools` 字段，模型以 `<｜DSML｜tool_calls>`、`<｜DSML｜invoke>`、`<｜DSML｜parameter>` 格式输出工具调用；tool results 会包装在 user messages 中的 `<tool_result>` 标签内，并按对应 tool call 顺序排序。证据：[DSML tool calling](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/encoding/README.md#L251-L293)。

## 5. Reasoning Effort Max

Encoding 文档说明，当 `reasoning_effort="max"` 时，会在 prompt 最前面插入特殊前缀，要求模型最大化 reasoning depth。证据：[Reasoning effort max](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/encoding/README.md#L294-L309)。

## 6. Harness 结论

DeepSeek Agent 需要单独实现 `DeepSeekV4MessageCompiler`，不能只做 generic OpenAI adapter。原因：

1. V4 有专用 encoding。
2. Tool calling 是 DSML。
3. Tool result merge into user message。
4. thinking / max thinking 是协议级格式。
5. reasoning_content 需要 drop / archive / summarize 策略。
