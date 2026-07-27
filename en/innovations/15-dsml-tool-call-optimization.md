# DSML Encoding-Layer Research: Internal Representation Is Not a Client Protocol

> **Evidence level: A1 + A0 + B**  
> - **A1**: a fixed version of `encoding_dsv4.py` confirms the existence of DSML special tokens, templates, and parameter-encoding logic.  
> - **A0, project API Spike**: the public API returned standard OpenAI-compatible `tool_calls`; the client did not require a DSML parser.  
> - **B**: whether DSML reduces tokens, lowers generation errors, or improves inference efficiency still requires a dedicated benchmark.  
> Read [Research Method and Evidence Calibration](../theory/research-method.md) first.

> **Innovation index**: I-15  
> **Series**: [LLM + Harness = Agent](../../README_en.md)  
> **Related**: [I-14 Reasoning Content Replay Policy](14-reasoning-content-stripping.md) · [I-13 Byte-Stable Prefix](13-byte-stable-prefix-architecture.md)

---

## Abstract

DeepSeek V4 encoding source contains DSML—DeepSeek Markup Language—special tokens and XML-style tool-call templates. This indicates that the model encoding layer may use a specialized representation for tool calls.

A client Harness, however, must follow the actual public API contract. A project API Spike on 2026-07-16 observed:

```text
client sends OpenAI-compatible tools / JSON Schema
→ server performs internal encoding, model generation, and result conversion
→ client receives standard tool_calls
```

The following early conclusions are therefore disproven:

- “Every Agent integrating DeepSeek V4 must implement a DSML parser”;
- “The public API returns raw DSML text”;
- “The client cannot continue using the standard `tool_calls` data structure.”

The most useful DSML research direction is not to bypass the public protocol from the client. It is to understand how internal tool representation may affect server behavior, token usage, error recovery, and future Provider capabilities.

---

## 1. Three Protocol Layers Must Be Separated

### 1.1 Public client protocol

The structure a Harness actually sends and receives, for example:

```json
{
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "get_weather",
        "parameters": {
          "type": "object",
          "properties": {
            "city": {"type": "string"}
          },
          "required": ["city"]
        }
      }
    }
  ]
}
```

Standard response structure:

```json
{
  "tool_calls": [
    {
      "id": "call_xxx",
      "type": "function",
      "function": {
        "name": "get_weather",
        "arguments": "{\"city\":\"Beijing\"}"
      }
    }
  ]
}
```

This is the contract a Provider Adapter must support.

### 1.2 Server request compilation and result conversion

The server may perform:

```text
JSON Schema
→ model-specific Prompt / token representation
→ model output
→ structured parsing
→ standard API Response
```

Clients usually cannot observe this layer and should not infer the full hosted implementation from tokenizer source.

### 1.3 Model encoding layer

DSML templates in `encoding_dsv4.py` belong to model input/output encoding logic. They prove that an internal representation exists, but do not independently prove that:

- a public Endpoint accepts client-submitted DSML;
- a public Endpoint returns raw DSML;
- the hosted service runs exactly the public source version;
- DSML is more token-efficient or reliable than JSON.

---

## 2. What the Source Confirms

### 2.1 DSML special token

The fixed source defines a token similar to:

```python
dsml_token = "｜DSML｜"
```

The tool-call template uses XML-style tags:

```xml
<｜DSML｜tool_calls>
  <｜DSML｜invoke name="get_weather">
    <｜DSML｜parameter name="city" string="true">Beijing</｜DSML｜parameter>
  </｜DSML｜invoke>
</｜DSML｜tool_calls>
```

This supports the A1 conclusion:

> The DeepSeek V4 encoding implementation contains a model-specific structured tool-call representation.

### 2.2 String and non-string parameter distinction

Encoding logic uses `string="true|false"` to distinguish:

- strings represented directly as text;
- numbers, Booleans, arrays, and objects that remain JSON-serialized.

This is an internal type-encoding design. It may reduce string-escaping complexity, but “how many tokens it saves” and “whether it reduces errors” remain B-level inferences.

### 2.3 Encoding and decoding logic

The source contains DSML rendering and parsing code. A complete encoding path must handle:

- tag boundaries;
- tool names;
- parameter names;
- parameter types;
- nested values;
- incomplete output and error recovery.

This proves that a server or local inference stack needs corresponding conversion logic. It does not imply that every API client must reimplement it.

---

## 3. API Spike Corrections

### 3.1 Observed behavior

The project’s fixed Spike records:

```text
input: standard OpenAI-compatible tools
output: standard tool_calls
client: no DSML Parser required
```

The default Provider Adapter should therefore:

1. send standard Tool Schemas supported by the public documentation;
2. read structured `tool_calls`;
3. validate `name`, `arguments`, `id`, and `finish_reason`;
4. handle invalid JSON Arguments explicitly;
5. avoid dependence on private markers inside response text.

### 3.2 Boundaries still unconfirmed

The Spike does not prove that:

- every Endpoint, region, and account behaves identically forever;
- every streaming Tool Call Chunk field remains stable;
- local deployment or low-level inference Endpoints return the same standard structure;
- the future API will never expose an explicit DSML mode;
- internal server conversion has no version differences.

Use a Capability Snapshot rather than freezing one observation as a permanent protocol guarantee.

---

## 4. Correct Implications for a Harness

### 4.1 Provider Contract takes priority

Provider Adapter evidence priority:

```text
observed API behavior
> official API documentation
> official SDK
> model encoding source
> third-party implementation
> engineering inference
```

Encoding source explains behavior and generates experiments. It does not authorize bypassing the public contract.

### 4.2 Separate the internal tool model from Wire Format

Use one Provider-neutral type inside the Runtime:

```typescript
interface ToolCall {
  id: string;
  name: string;
  arguments: unknown;
  rawArguments?: string;
  provider: string;
  protocolVersion: string;
}
```

The Provider Adapter handles:

```text
internal Tool Definition
↔ Provider Request
↔ Provider Response
↔ internal ToolCall
```

If a future Provider exposes DSML, JSON, Protobuf, or another format, the Orchestrator, Policy, and Tool Runtime need not be rewritten.

### 4.3 Never execute model-generated arguments directly

Regardless of whether the server returns JSON or another format:

- verify that the tool name is allowed;
- validate arguments against Schema;
- reject unknown fields or process them under an explicit policy;
- enforce path, permission, and side-effect checks;
- preserve a raw-response Hash and canonicalized arguments;
- create recoverable state on parse failure.

Structured formatting reduces parsing ambiguity; it is not a security guarantee.

### 4.4 Tool Schema stability

For diagnosis and possible Prefix Cache reuse:

- sort tools deterministically;
- use deterministic JSON key serialization;
- fingerprint Schemas;
- increment versions after permission changes or Schema fixes;
- never retain revoked permissions to preserve Cache hits.

---

## 5. Research Questions Requiring Validation

### RQ-1: Public API Wire Contract

Matrix:

```text
Flash / Pro
thinking / non-thinking
stream / non-stream
single / parallel / sequential tools
valid / invalid schema
valid / malformed arguments
```

Record:

- HTTP status;
- Response fields;
- Chunk fields;
- `finish_reason`;
- Tool Call ID;
- error type;
- whether the next turn can continue.

### RQ-2: DSML token efficiency

Only with the same Tokenizer and semantically equivalent representation can the following be compared:

```text
JSON representation token count
DSML representation token count
escaping overhead
schema size
argument size
```

Character counts cannot estimate token counts, and a special-token name alone does not prove efficiency.

### RQ-3: Generation reliability

On a fixed task set, compare:

```text
valid structured-call rate
argument schema pass rate
incorrect tool-name rate
truncated call rate
recovery success rate
```

If the public API converts DSML into standard structures internally, the client can measure only end-to-end outcomes and cannot attribute improvements directly to DSML.

### RQ-4: Local inference versus public API

If local V4 weights or a low-level inference interface become available, independently confirm:

- whether raw DSML is emitted;
- whether an official Parser can be reused;
- Parser error-recovery behavior;
- semantic compatibility with the public API;
- whether a Provider-specific Adapter is required.

Local inference findings do not automatically generalize to the hosted API, or vice versa.

---

## 6. Antipatterns

### 6.1 Deriving the public API directly from encoding source

Incorrect chain:

```text
Tokenizer contains DSML
→ API must accept DSML
→ API must return DSML
→ client must implement a Parser
```

Each step requires independent evidence.

### 6.2 Bypassing the official protocol because a format is “model-native”

Directly concatenating private tokens can cause:

- Endpoint rejection;
- a larger Prompt Injection surface;
- separation between Tool Schema and permission systems;
- incompatibility after SDK/server upgrades;
- more complex debugging, audit, and error handling.

Do not put this on the product main path without an official stable interface and compatibility commitment.

### 6.3 Treating format efficiency as task quality

Even if DSML uses fewer tokens, it does not imply:

- better tool selection;
- more accurate argument semantics;
- safer side effects;
- higher first-pass task completion.

Format metrics and task metrics must remain separate.

---

## 7. Current Implementation Recommendation

```text
default path: OpenAI-compatible Tool API
internal representation: Provider-neutral ToolCall
validation layer: Schema + Policy + Permission + Side-effect classification
telemetry layer: Protocol version + Tool schema fingerprint + Parse errors
experimental path: separate DSML/tokenizer benchmark, outside the default client execution path
```

Recommended Provider Capability record:

```yaml
provider: deepseek
endpoint: <redacted-host-id>
model: deepseek-v4-pro
observed_at: 2026-07-16
request_tools_format: openai-compatible-json-schema
response_tool_calls_format: openai-compatible
dsml_visible_on_wire: false
source_commit: <fixed-commit>
limitations:
  - endpoint/account/time scoped
  - local inference not tested
```

---

## 8. Conclusion

DSML is a model-encoding mechanism worth studying, but the current client architecture conclusion is clear:

1. DSML in the encoding layer does not mean the public API exposes DSML directly;
2. the project API Spike disproved the requirement for a client DSML Parser;
3. a Harness should be built around the public Provider Contract and one internal ToolCall type;
4. DSML token, latency, and generation-reliability benefits require a dedicated benchmark;
5. even with a more structured format, Tool Schema, permissions, arguments, and side effects must still be validated by the Runtime.

Source code generates questions. Wire Evidence determines the client implementation.
