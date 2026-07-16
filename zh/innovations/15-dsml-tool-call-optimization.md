# DSML 工具调用格式优化：当模型用自己的语言定义工具

> **证据说明：** 本文基于 DeepSeek V4 Flash/Pro 固定源码分析（encoding_dsv4.py）和 OpenAI 函数调用协议公开文档。所有对照以源码签出状态为准；DSML 对 tokenizer 效率、推理速度和 Harness 适配成本的影响属于待验证推论。请先阅读 [研究方法与事实校准](../theory/research-method.md)。

> 创新索引: I-15
> **LLM + Harness = Agent** · 第 15 篇
> 系列: [LLM + Harness = Agent](../../README.md)
> 关联: [I-14 Reasoning Content Stripping](14-reasoning-content-stripping.md) · [I-13 Byte-Stable Prefix 架构](13-byte-stable-prefix-architecture.md)

---

## 问题：JSON 不是模型的原生语言

OpenAI 定义函数调用（Function Calling）时做了一个自然的选择：用 JSON。JSON 是 Web 时代的通用数据格式，每门语言都有解析器，工具定义和参数传递都用它。Anthropic 跟进。Google 跟进。整个行业跟进。

这个选择在工程上合情合理。但在模型内部，它意味着：

```
模型必须先理解 JSON schema（人类设计的序列化格式）
→ 然后在推理过程中生成符合 schema 的 JSON 字符串
→ 再确保 JSON 语法完全正确（一个逗号错误就导致解析失败）
→ 同时 JSON 的大括号、引号、逗号在 tokenization 时消耗额外 token
```

这是人类迁就机器的格式，不是机器最擅长的格式。

DeepSeek V4 做了一个不同的选择。

---

## 行业默认：JSON 函数调用格式

几乎所有主流 LLM 的工具调用格式都基于 JSON：

| 模型/平台 | 工具调用格式 | 参数传递 | 工具结果格式 |
|-----------|-------------|---------|-------------|
| **OpenAI** | JSON `function_call` / `tool_calls` 数组 | JSON `arguments` 字符串 | JSON `tool` role message |
| **Anthropic** | XML `<function_calls>` 内含 JSON | JSON 参数对象 | `<function_results>` 内含 JSON |
| **Google Gemini** | JSON `functionCall` 对象 | JSON `args` 对象 | JSON `functionResponse` |
| **DeepSeek V3** | 兼容 OpenAI JSON 格式 | JSON `arguments` | JSON `tool` role |
| **DeepSeek V4** | **DSML**（XML 风格，`｜DSML｜` 标记）| DSML `<parameter>` 标签 | `<tool_result>` 标签 |

在此之前的 DeepSeek V3，采用的是与 OpenAI 兼容的 JSON 函数调用格式。V4 是第一个全面转向 DSML 的版本。

OpenAI 的方案是通用标准，跨模型移植成本最低；Anthropic 用 XML 包装 JSON，在人类可读性和结构化之间做了一个折中；DeepSeek V4 的 DSML 则是完全不同的方向——它把工具调用的编码和解码**嵌入到模型的 tokenizer 层面**。

---

## 关键洞察：DSML 是 tokenizer 原生的工具调用语言

### DSML 是什么

DSML（DeepSeek Markup Language）不是标准 XML。它的核心是一个特殊的 Unicode token `｜DSML｜`（全角竖线 + DSML + 全角竖线），直接编码在 DeepSeek V4 的 tokenizer 词表中：

```python
# encoding_dsv4.py L21
dsml_token = "｜DSML｜"
```

基于这个 token，整个工具调用协议用一套 XML 风格的模板定义：

```python
# encoding_dsv4.py L52-57
tool_call_template: str = (
    "<{dsml_token}invoke name=\"{name}\">\n{arguments}\n</{dsml_token}invoke>"
)
tool_calls_template = (
    "<{dsml_token}{tc_block_name}>\n{tool_calls}\n</{dsml_token}{tc_block_name}>"
)
tool_calls_block_name: str = "tool_calls"
```

实际生成的工具调用块格式如下：

```xml
<｜DSML｜tool_calls>
<｜DSML｜invoke name="get_weather">
<｜DSML｜parameter name="city" string="true">北京</｜DSML｜parameter>
<｜DSML｜parameter name="days" string="false">7</｜DSML｜parameter>
</｜DSML｜invoke>
</｜DSML｜tool_calls>
```

### 核心创新：`string="true|false"` 类型区分

DSML 最独特的设计是参数标签上的 `string` 属性：

```python
# encoding_dsv4.py L139-166
def encode_arguments_to_dsml(tool_call: Dict[str, str]) -> str:
    p_dsml_template = (
        '<{dsml_token}parameter name="{key}" string="{is_str}">'
        '{value}</{dsml_token}parameter>'
    )
    for k, v in arguments.items():
        is_str = "true" if isinstance(v, str) else "false"
        value = v if isinstance(v, str) else to_json(v)
```

这意味着：

| 参数类型 | `string` 属性 | 值的编码方式 | token 影响 |
|---------|-------------|------------|-----------|
| 字符串 | `string="true"` | 原始文本，**不包引号** | 节省 JSON 的 `"..."` 转义开销 |
| 数字、布尔、数组、对象 | `string="false"` | JSON 序列化 | 与 OpenAI 相同 |

这个设计很精妙。字符串参数直接内嵌——不需要 JSON 的两层引号转义。对于工具调用中常见的大量字符串参数（文件名、搜索词、代码片段），这避免了 `\"` 转义链，减少了 token 数量，同时也降低了模型生成有效转义字符串的难度。

解码端也对应处理：

```python
# encoding_dsv4.py L169-186
def decode_dsml_to_arguments(tool_name: str, tool_args: Dict[str, Tuple[str, str]]) -> Dict[str, str]:
    def _decode_value(key: str, value: str, string: str):
        if string == "true":
            value = to_json(value)  # 将原始字符串重新 JSON 序列化
        return f"{to_json(key)}: {value}"

    tool_args_json = "{" + ", ".join([_decode_value(k, v, string=is_str) for k, (v, is_str) in tool_args.items()]) + "}"
    return dict(name=tool_name, arguments=tool_args_json)
```

---

## 分析：DSML 对 Agent Harness 意味着什么

### 1. 解析层的根本变化

OpenAI JSON 格式的解析路径：

```
模型输出 → JSON 字符串 → json.loads() → Python dict
```

DSML 格式的解析路径：

```
模型输出 → XML 风格文本 → 正则/SAX 解析 → 提取参数和 string 属性 → 按类型解码 → Python dict
```

`json.loads()` 是库函数调用，一行代码。DSML 解析需要实现完整的标记化解析器。`encoding_dsv4.py` 中的解析逻辑（`parse_message_from_completion_text` 和相关函数）超过 100 行，包含正则匹配、状态机遍历、字符串分割和错误恢复。

**对 Harness 的影响**（置信度：大概率 95%）：

- 任何接入 DeepSeek V4 的 Agent 都必须实现 DSML 解析器
- 不能假定 `json.loads()` 能处理模型输出——parse 失败率比 JSON 格式高一个数量级
- 错误处理逻辑更复杂：JSON 错误是语法错误，DSML 错误可能是标记缺失、嵌套错误、属性解析错误

### 2. tokenizer 层面的效率优势（待验证推论）

`｜DSML｜` 作为单个 token 而非三个字符 `"f"`, `"u"`, `"n"`，意味着：

```
OpenAI 格式: {"function": {"name": "get_weather"}}
→ tokenized: [, ", f, u, n, c, t, i, o, n, ", :,  , {, ...  (约 15-20 tokens)

DSML 格式: <｜DSML｜invoke name="get_weather">
→ tokenized: <, ｜DSML｜, invoke,  name, =, ", get_weather, ", >  (约 8-10 tokens)
```

`｜DSML｜` 标记作为一个整体被 tokenizer 识别，每个标记和属性名在词表中都有固定位置。这带来两个潜在优势：
- **更少的 token 消耗**：相同的语义信息用更少的 token 表示
- **更稳定的 KV Cache**：工具定义块的 token 序列高度可预测，prefix caching 命中率更高

> **证据等级：B**（工程推论，未经专用 benchmark 验证）。需要 DeepSeek tokenizer 的具体词表分析和 token 计数对比才能确认。详见下文"验证路径"。

### 3. 工具 Schema 表示的重新思考

OpenAI 的工具 Schema 用 JSON Schema 描述：

```json
{
  "type": "function",
  "function": {
    "name": "get_weather",
    "parameters": {
      "type": "object",
      "properties": {
        "city": {"type": "string"}
      }
    }
  }
}
```

在 DSML 模型中，工具定义同样可以用 DSML 格式发送——模型训练时就以 DSML 格式理解和生成工具调用。这意味着：

**Harness 有两种选择**：

1. **发送 JSON Schema + 接收 DSML**：当前 DeepSeek API 的实际做法——输入 accept JSON 工具定义，输出返回 DSML。Harness 只需实现 DSML 解码端。

2. **发送 DSML 格式 + 接收 DSML**：理论最优方案——Harness 将工具定义也编码为 DSML 发送。但 API 是否接受取决于 endpoint 实现。

> **证据等级：A1**（源码确认：`render_message` 中包含 `tool_call_template` 工具定义的注入逻辑；但 API endpoint 是否同时接受 DSML 和 JSON 输入缺乏公开文档确认）。

### 4. 与 I-13 Byte-Stable Prefix 的交叉影响

I-13 提出将工具 Schema 稳定排序以最大化 prefix cache 命中率。DSML 将这一约束提升了一个层面：

- JSON 格式中，`{"type":"function","function":{"name":"x"}}` 和 `{"function":{"name":"x"},"type":"function"}` 语义等价但 token 序列不同——必须排序
- DSML 格式中，`<｜DSML｜invoke name="x">` 的 `<parameter>` 顺序仍然影响 token 序列——同样需要稳定排序

但 DSML 的标签结构天然比 JSON 更严格：XML 风格的开始和结束标签限制了结构变化的空间，减少了因 key 顺序不一致导致的 prefix cache 失效。

---

## DSML 全景对比表

| 维度 | OpenAI JSON | Anthropic XML+JSON | DeepSeek V4 DSML |
|------|-----------|-------------------|-----------------|
| 核心语法 | JSON 对象/数组 | XML 包装 + JSON 内容 | ｜DSML｜ 标记 + XML 风格 |
| 标记 token | 无（JSON 关键字按字符拆分） | `<function_calls>` 按字符拆分 | `｜DSML｜` 为独立 token |
| 字符串参数 | `"\"value\""`（两层转义） | `"\"value\""`（同 OpenAI） | `string="true">value<`（零转义） |
| 类型系统 | JSON 类型隐式 | JSON 类型隐式 | `string="true/false"` 显式声明 |
| 解析复杂度 | `json.loads()` 一行 | XML 解析 + JSON 解析 | 自定义正则/状态机 ~100 行 |
| 跨模型可移植性 | 最好（行业标准） | 好（Anthropic 生态） | 差（仅 DeepSeek V4） |
| Prefix Cache 友好度 | 中（key 顺序敏感） | 中（同左） | 高（标签结构受限，标记 token 固定） |
| 证据等级 | A0 | A0 | A1（源码确认） |

---

## 验证路径

以下验证可提升证据等级到 A0：

### 实验 1：Token 效率对比

```
工具：DeepSeek V4 tokenizer + tiktoken
输入：相同的 5 函数工具集，200 个典型工具调用
对比：
  A. JSON 格式 → token count
  B. DSML 格式 → token count
预期结论：DSML 格式 token 数量更少（估计差距 15-30%）
```

### 实验 2：Prefix Cache 命中率

```
工具：DeepSeek V4 API，100 轮工具调用 session
对比：
  A. Harness 发送 JSON 工具 Schema，随机 key 顺序 vs 稳定排序
  B. DSML 格式工具 Schema，同样做稳定排序
预期结论：DSML 组 prefix cache 命中率更高，delta 随工具数增加而扩大
```

### 实验 3：解析鲁棒性

```
工具：1000 个真实模型生成的工具调用
对比：
  A. json.loads() 直接解析（期望 JSON 输出时）
  B. encoding_dsv4.parse* 解析（DSML 格式输出时）
预期结论：DSML 解析错误率在模型输出格式正确时与 JSON 相当；在模型产生"接近正确但语法错误"的输出时，DSML 的恢复能力取决于实现质量
```

### 实验 4：Harness 适配成本

```
任务：为一个开源 Agent 框架（如 Reasonix/Hermes）编写 V4 DSML 解析适配器
测量：代码行数、测试用例数、集成时间
基准：V3/OpenAI JSON provider 实现
预期结论：适配成本 ~200 行 Go/Python（含错误处理），测试 ~300 行
```

---

## 结论：DSML 是 tokenizer 优先的架构选择——代价是生态可移植性

DSML 代表的不是"另一种序列化格式"，而是一种架构立场：

> **如果一个模型既是工具调用的生产者又是消费者，且训练时已经将特定 token 序列化进 tokenizer，那么使用一个为人类互操作性设计的格式（JSON）可能是次优的。**

DeepSeek V4 选择了 tokenizer 原生格式：`｜DSML｜` 作为词表 token，`string="true|false"` 消除字符串转义，XML 风格标签提供结构约束。这些设计在 token 效率、prefix cache 命中率、字符串处理简洁性上可能有显著优势——代价是放弃了 OpenAI JSON 生态的即插即用。

对 Agent Harness 设计者而言，这意味着：

1. **任何支持 DeepSeek V4 的 Harness 都需要专门的 DSML 解析器**，不能复用 OpenAI provider 的 `json.loads()` 路径
2. **工具 Schema 的发送格式**是开放问题——API endpoint 的输入格式仍在 JSON Schema 和 DSML 之间过渡，Harness 应该支持两种输入格式并测试哪种更优
3. **DSML 的 `string` 类型属性**是一个值得借鉴的设计——即使在 JSON 格式中，显式类型声明也可能减少模型的类型猜测错误
4. **DSML 验证**是下一个需要固定 commit + 可复现实验来将本文证据等级从 B/推论提升到 A0/实测的话题

当前证据状态：**A1 for format implementation, B for efficiency claims**。DSML 的存在和实现方式已由 `encoding_dsv4.py` 源码确认（Flash 和 Pro 版本实现一致）；token 效率和 cache 优势是工程推论，需要 tokenizer 级别的 benchmark 校准。

---

*本文基于 DeepSeek V4 Flash/Pro `encoding/encoding_dsv4.py`（744 行，两个版本 diff 完全一致）和 OpenAI Function Calling 协议文档的固定 commit 分析。OpenAI/Anthropic/Google 工具调用格式基于官方 API 文档。*

> 下一篇: [I-16 Quick Instruction 路由](16-quick-instruction-routing.md)
