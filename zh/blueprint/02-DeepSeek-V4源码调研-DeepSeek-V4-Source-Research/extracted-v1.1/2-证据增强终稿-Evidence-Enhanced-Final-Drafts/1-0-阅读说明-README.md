# DeepSeek V4 源代码调研终版包 Final Source Research Package

> 版本：v1.0  
> 日期：2026-06-04  
> 范围：DeepSeek V4 Flash / Pro 的官方模型卡、官方 Hugging Face 源代码、官方配置、官方 encoding、官方 inference kernel、DeepSeek 官方 API 文档。  
> 语言：正文统一使用简体中文。  
> 文件命名：`序号-简体中文-English.md`。

---

## 0. 本包修订目标

本包是对前面 DeepSeek V4 调研文档的“证据版重整”。

修订重点：

1. 每个核心论点旁边补充官方来源链接。
2. 优先使用官方源码、官方模型卡、官方 API Docs。
3. 对无法从官方源码直接证明的内容，明确标注为“推论”。
4. 不把 Stage 1 的模型侧调研误当成最终 Harness 架构。
5. 文件按顺序重命名为“序号-简体中文-English.md”。

---

## 1. 文件清单

```text
1-0-阅读说明-README.md
1-1-资料定位与证据规范-Source-Map-and-Evidence-Standard.md
1-2-配置差异与模型规模-Config-Diff-and-Model-Scale.md
1-3-模型结构总览-Model-Architecture-Map.md
1-4-长上下文机制-Hybrid-Attention-and-Long-Context.md
1-5-MoE与专家路由-MoE-and-Expert-Routing.md
1-6-mHC超连接机制-mHC-Hyper-Connections.md
1-7-FP4-FP8与Kernel推理效率-Quantization-and-Kernels.md
1-8-Encoding与工具调用协议-Encoding-and-Tool-Calling.md
1-9-API缓存与成本模型-API-Cache-and-Cost-Model.md
1-10-物理特性总清单与Harness启示-Physical-Traits-and-Harness-Implications.md
1-11-证据索引-Evidence-Index.md
```

---

## 2. 证据等级

| 等级 | 含义 | 是否可作为架构依据 |
|---|---|---|
| S0 | 官方源码 / 官方 config 直接确认 | 是 |
| S1 | 官方模型卡 / 官方 API 文档直接确认 | 是 |
| A | 官方技术报告确认 | 是 |
| B | 可信第三方资料 | 仅作辅助 |
| C | 工程推论 | 必须标注，不单独作为最终依据 |

---

## 3. 最关键的官方来源入口

- DeepSeek V4 官方模型卡：[DeepSeek-V4-Pro README / Model Card](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/README.md#L214-L222)
- DeepSeek V4 Pro 配置：[DeepSeek-V4-Pro config.json](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/config.json#L206-L245)
- DeepSeek V4 Flash 配置：[DeepSeek-V4-Flash config.json](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash/blob/main/config.json#L203-L242)
- 模型结构源码：[inference/model.py](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/inference/model.py#L1470-L1472)
- Kernel 源码：[inference/kernel.py](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/inference/kernel.py#L921-L938)
- Encoding 文档：[encoding/README.md](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/encoding/README.md#L194-L214)
- API 价格与模型能力：[DeepSeek Models & Pricing](https://api-docs.deepseek.com/quick_start/pricing#L47-L64)
- API Context Caching：[DeepSeek Context Caching](https://api-docs.deepseek.com/guides/kv_cache#L44-L57)

---

## 4. 本包的边界

本包只处理 DeepSeek V4 源码调研。  
Claude Code、Codex、Trae、Reasonix、Hermes、CodeWhale 的竞品调研属于下一阶段，不混入本包。
