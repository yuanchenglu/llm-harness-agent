# DSML Tool-Call Format Optimization: When the Model Defines Tools in Its Own Language

> **Evidence note:** This paper is based on fixed-source analysis of DeepSeek V4 Flash/Pro (`encoding_dsv4.py`) and public documentation of the OpenAI function-calling protocol. All comparisons are anchored to the checked-out source state; DSML's impact on tokenizer efficiency, inference speed, and Harness adaptation cost remains an unvalidated inference. Read [Research Method and Evidence Calibration](../theory/research-method.md) first.

> Innovation Index: I-15
> **LLM + Harness = Agent** · Part 15
> Series: [LLM + Harness = Agent](../../README.md)
> Related: [I-14 Reasoning Content Stripping](14-reasoning-content-stripping.md) · [I-13 Byte-Stable Prefix Architecture](13-byte-stable-prefix-architecture.md)

---

## Problem: JSON Is Not the Model's Native Language

When OpenAI defined Function Calling, it made a natural choice: JSON. JSON is the universal data format of the web era; every language has a parser; tool definitions and parameter passing all use it. Anthropic followed. Google followed. The entire industry followed.

That choice is entirely reasonable from an engineering standpoint. But inside the model, it means:

```
The model must first understand the JSON schema (a serialization format designed by humans)
→ Then generate a JSON string conforming to that schema during inference
→ Then ensure the JSON syntax is perfectly correct (one missing comma breaks parsing)
→ And the braces, quotes, and commas of JSON all consume extra tokens during tokenization
```

This is a format where humans accommodate machines, not a format machines are best at.

DeepSeek V4 made a different choice.

---

## Industry Default: JSON Function-Calling Format

Nearly every mainstream LLM's tool-calling format is based on JSON:

| Model / Platform | Tool-Call Format | Parameter Passing | Tool-Result Format |
|-----------|-------------|---------|-------------|
| **OpenAI** | JSON `function_call` / `tool_calls` array | JSON `arguments` string | JSON `tool` role message |
| **Anthropic** | XML `<function_calls>` wrapping JSON | JSON parameter object | `<function_results>` wrapping JSON |
| **Google Gemini** | JSON `functionCall` object | JSON `args` object | JSON `functionResponse` |
| **DeepSeek V3** | OpenAI-compatible JSON format | JSON `arguments` | JSON `tool` role |
| **DeepSeek V4** | **DSML** (XML-style with `｜DSML｜` markers) | DSML `<parameter>` tags | `<tool_result>` tags |

Prior DeepSeek V3 used the OpenAI-compatible JSON function-calling format. V4 is the first version to fully switch to DSML.

OpenAI's format is the universal standard with the lowest cross-model porting cost; Anthropic wraps JSON in XML as a compromise between human readability and structure; DeepSeek V4's DSML takes an entirely different direction — it **embeds tool-call encoding and decoding at the model's tokenizer level**.

---

## Key Insight: DSML Is a Tokenizer-Native Tool-Calling Language

### What Is DSML

DSML (DeepSeek Markup Language) is not standard XML. At its core is a special Unicode token `｜DSML｜` (full-width vertical bar + DSML + full-width vertical bar), directly encoded in DeepSeek V4's tokenizer vocabulary:

```python
# encoding_dsv4.py L21
dsml_token = "｜DSML｜"
```

Around this token, the entire tool-call protocol is defined with a set of XML-style templates:

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

The actual generated tool-call block looks like:

```xml
<｜DSML｜tool_calls>
<｜DSML｜invoke name="get_weather">
<｜DSML｜parameter name="city" string="true">Beijing</｜DSML｜parameter>
<｜DSML｜parameter name="days" string="false">7</｜DSML｜parameter>
</｜DSML｜invoke>
</｜DSML｜tool_calls>
```

### Core Innovation: The `string="true|false"` Type Distinction

DSML's most distinctive design is the `string` attribute on parameter tags:

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

This means:

| Parameter Type | `string` Attribute | Value Encoding | Token Impact |
|---------|-------------|------------|-----------|
| String | `string="true"` | Raw text, **no surrounding quotes** | Saves JSON's `"..."` escaping overhead |
| Number, Boolean, Array, Object | `string="false"` | JSON serialization | Identical to OpenAI |

This design is clever. String parameters are embedded directly — no need for JSON's double-layer quote escaping. For the numerous string parameters common in tool calls (filenames, search terms, code snippets), this avoids the `\"` escape chain, reduces token count, and lowers the difficulty for the model of generating valid escaped strings.

The decoding side mirrors this:

```python
# encoding_dsv4.py L169-186
def decode_dsml_to_arguments(tool_name: str, tool_args: Dict[str, Tuple[str, str]]) -> Dict[str, str]:
    def _decode_value(key: str, value: str, string: str):
        if string == "true":
            value = to_json(value)  # Re-serialize the raw string to JSON
        return f"{to_json(key)}: {value}"

    tool_args_json = "{" + ", ".join([_decode_value(k, v, string=is_str) for k, (v, is_str) in tool_args.items()]) + "}"
    return dict(name=tool_name, arguments=tool_args_json)
```

---

## Analysis: What DSML Means for Agent Harness

### 1. A Fundamental Change at the Parsing Layer

The OpenAI JSON-format parsing path:

```
Model output → JSON string → json.loads() → Python dict
```

The DSML-format parsing path:

```
Model output → XML-style text → regex/SAX parsing → extract parameters and string attributes → decode by type → Python dict
```

`json.loads()` is a library call, one line of code. DSML parsing requires implementing a full tokenizing parser. The parsing logic in `encoding_dsv4.py` (`parse_message_from_completion_text` and related functions) exceeds 100 lines, including regex matching, state-machine traversal, string splitting, and error recovery.

**Impact on Harness** (confidence: 95% likely):

- Any Agent connecting to DeepSeek V4 must implement a DSML parser
- You cannot assume `json.loads()` can handle model output — the parse failure rate is an order of magnitude higher than with JSON
- Error handling is more complex: JSON errors are syntax errors; DSML errors can be missing tags, nesting errors, or attribute-parsing errors

### 2. Tokenizer-Level Efficiency Advantage (unvalidated inference)

With `｜DSML｜` as a single token rather than three characters `"f"`, `"u"`, `"n"`:

```
OpenAI format: {"function": {"name": "get_weather"}}
→ tokenized: [, ", f, u, n, c, t, i, o, n, ", :,  , {, ...  (~15-20 tokens)

DSML format: <｜DSML｜invoke name="get_weather">
→ tokenized: <, ｜DSML｜, invoke,  name, =, ", get_weather, ", >  (~8-10 tokens)
```

The `｜DSML｜` marker is recognized as a whole by the tokenizer, and each marker and attribute name has a fixed position in the vocabulary. This brings two potential advantages:
- **Fewer tokens consumed**: the same semantic information expressed with fewer tokens
- **More stable KV Cache**: the token sequence of tool-definition blocks is highly predictable, leading to higher prefix-caching hit rates

> **Evidence level: B** (engineering inference, not validated by a dedicated benchmark). Specific vocabulary analysis and token-count comparison using the DeepSeek tokenizer are required to confirm. See "Validation Path" below.

### 3. Rethinking Tool Schema Representation

OpenAI tool schemas are described with JSON Schema:

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

In DSML models, tool definitions can likewise be sent in DSML format — the model was trained to understand and generate tool calls in DSML. This means:

**The Harness has two choices:**

1. **Send JSON Schema + receive DSML**: the current DeepSeek API approach — accept JSON tool definitions on input, return DSML on output. The Harness only needs to implement the DSML decoding side.

2. **Send DSML format + receive DSML**: theoretically optimal — the Harness encodes tool definitions in DSML as well. But whether the API accepts this depends on the endpoint implementation.

> **Evidence level: A1** (source confirmed: `render_message` includes injection logic for `tool_call_template` tool definitions; but whether the API endpoint accepts both DSML and JSON input lacks public documentation confirmation).

### 4. Cross-Effect with I-13 Byte-Stable Prefix

I-13 proposes stable sorting of tool schemas to maximize prefix-cache hit rate. DSML raises this constraint one level higher:

- In JSON format, `{"type":"function","function":{"name":"x"}}` and `{"function":{"name":"x"},"type":"function"}` are semantically equivalent but produce different token sequences — stable ordering is mandatory
- In DSML format, the `<parameter>` order inside `<｜DSML｜invoke name="x">` still affects the token sequence — stable ordering is still required

But DSML's tag structure is inherently stricter than JSON: XML-style open/close tags limit the space of structural variation, reducing prefix-cache misses caused by inconsistent key ordering.

---

## DSML Comparative Table

| Dimension | OpenAI JSON | Anthropic XML+JSON | DeepSeek V4 DSML |
|------|-----------|-------------------|-----------------|
| Core syntax | JSON objects/arrays | XML wrapper + JSON content | ｜DSML｜ markers + XML-style |
| Marker token | None (JSON keywords split character-by-character) | `<function_calls>` split character-by-character | `｜DSML｜` as a standalone token |
| String parameters | `"\"value\""` (double escaping) | `"\"value\""` (same as OpenAI) | `string="true">value<` (zero escaping) |
| Type system | JSON types implicit | JSON types implicit | `string="true/false"` explicit declaration |
| Parsing complexity | `json.loads()` one-liner | XML parsing + JSON parsing | Custom regex/state machine ~100 lines |
| Cross-model portability | Best (industry standard) | Good (Anthropic ecosystem) | Poor (DeepSeek V4 only) |
| Prefix Cache friendliness | Medium (key-order sensitive) | Medium (same) | High (constrained tag structure, fixed marker token) |
| Evidence level | A0 | A0 | A1 (source confirmed) |

---

## Validation Path

The following validations would raise the evidence level to A0:

### Experiment 1: Token Efficiency Comparison

```
Tools: DeepSeek V4 tokenizer + tiktoken
Input: same 5-function tool set, 200 typical tool calls
Compare:
  A. JSON format → token count
  B. DSML format → token count
Expected conclusion: DSML uses fewer tokens (estimated gap 15-30%)
```

### Experiment 2: Prefix Cache Hit Rate

```
Tools: DeepSeek V4 API, 100-turn tool-calling session
Compare:
  A. Harness sends JSON tool schemas, random key order vs. stable ordering
  B. DSML-format tool schemas, also stably ordered
Expected conclusion: DSML group has higher prefix-cache hit rate, delta grows with tool count
```

### Experiment 3: Parsing Robustness

```
Tools: 1000 real model-generated tool calls
Compare:
  A. json.loads() direct parsing (when JSON output expected)
  B. encoding_dsv4.parse* parsing (when DSML output expected)
Expected conclusion: DSML parse error rate is comparable to JSON when model output format is correct; when the model produces "close but syntactically wrong" output, DSML's recovery capability depends on implementation quality
```

### Experiment 4: Harness Adaptation Cost

```
Task: write a V4 DSML parsing adapter for an open-source Agent framework (e.g. Reasonix/Hermes)
Measure: lines of code, test case count, integration time
Baseline: V3/OpenAI JSON provider implementation
Expected conclusion: ~200 lines of Go/Python to adapt (including error handling), ~300 lines of tests
```

---

## Conclusion: DSML Is a Tokenizer-First Architectural Choice — At the Cost of Ecosystem Portability

DSML does not represent "just another serialization format." It represents an architectural position:

> **If a model is both producer and consumer of tool calls, and specific tokens were serialized into the tokenizer during training, using a format designed for human interoperability (JSON) may be suboptimal.**

DeepSeek V4 chose a tokenizer-native format: `｜DSML｜` as a vocabulary token, `string="true|false"` eliminating string escaping, XML-style tags providing structural constraints. These designs may yield significant advantages in token efficiency, prefix-cache hit rate, and string-handling simplicity — at the cost of giving up the plug-and-play of the OpenAI JSON ecosystem.

For Agent Harness designers, this means:

1. **Any Harness supporting DeepSeek V4 needs a dedicated DSML parser**, and cannot reuse the OpenAI provider's `json.loads()` path
2. **The sending format for tool schemas** is an open question — the API endpoint input format is still transitioning between JSON Schema and DSML; the Harness should support both input formats and test which is better
3. **DSML's `string` type attribute** is a design worth borrowing — even in JSON format, explicit type declarations may reduce the model's type-guessing errors
4. **DSML validation** is the next topic requiring a fixed commit + reproducible experiments to raise this paper's evidence level from B/inference to A0/measured

Current evidence status: **A1 for format implementation, B for efficiency claims**. DSML's existence and implementation are confirmed by the `encoding_dsv4.py` source (identical across Flash and Pro); token efficiency and cache advantages are engineering inferences requiring tokenizer-level benchmark calibration.

---

*This article is based on fixed-commit analysis of DeepSeek V4 Flash/Pro `encoding/encoding_dsv4.py` (744 lines, identical diff across both versions) and the OpenAI Function Calling protocol documentation. OpenAI/Anthropic/Google tool-calling formats are based on official API documentation.*

> Next: [I-16 Quick Instruction Routing](16-quick-instruction-routing.md)
