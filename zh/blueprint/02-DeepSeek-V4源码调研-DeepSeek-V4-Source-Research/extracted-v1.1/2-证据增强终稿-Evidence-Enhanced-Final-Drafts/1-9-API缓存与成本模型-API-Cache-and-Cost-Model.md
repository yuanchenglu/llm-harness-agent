# 1-9 API缓存与成本模型 API Cache and Cost Model

## 1. 官方模型与价格

DeepSeek API 官方 Models & Pricing 页面列出 `deepseek-v4-flash` 与 `deepseek-v4-pro`，支持 non-thinking / thinking modes、1M context、最大输出 384K、JSON、Tool Calls、Prefix Completion，FIM 仅 non-thinking，并列出 cache hit / cache miss / output token 价格。证据：[Models & Pricing](https://api-docs.deepseek.com/quick_start/pricing#L47-L64)。

## 2. Context Caching 机制

官方 Context Caching 文档说明，DeepSeek API 的硬盘 context caching 默认开启；如果后续请求与之前请求有 overlapping prefixes，重叠部分会从 cache 获取并计为 cache hit。证据：[Context caching 默认开启](https://api-docs.deepseek.com/guides/kv_cache#L44-L57)。

## 3. Cache hit 规则

官方文档说明，cache hit 要求对应 prefix 已经被持久化；由于 Sliding Window Attention 机制，每个 cached prefix 是独立完整单元，后续请求只有完整匹配 cache prefix unit 才能命中。证据：[Cache hit rules](https://api-docs.deepseek.com/guides/kv_cache#L44-L57)。

## 4. Usage 字段

官方文档说明，API response 的 usage 中增加了：

```text
prompt_cache_hit_tokens
prompt_cache_miss_tokens
```

证据：[Cache hit status fields](https://api-docs.deepseek.com/guides/kv_cache#L101-L107)。

## 5. Harness 结论

DeepSeek Agent 的成本面板不能只显示 total tokens，必须显示：

```text
cache_hit_tokens
cache_miss_tokens
output_tokens
thinking mode
model route
tool loop count
estimated marginal cost
```

同时，系统 prefix、tool schema、memory/skill index 必须 byte-stable，否则会破坏 cache 命中。
