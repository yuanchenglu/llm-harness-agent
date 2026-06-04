# 17-0 六项目源码事实校准方法与证据清单

## 1. 为什么进行本轮复核

此前报告包含大量有价值的架构判断，但存在三个系统性风险：

1. 部分结论只引用 README 或会移动的 `main` 链接，没有固定 commit；
2. “源码存在”“已接入真实运行路径”“产品已完整实现”有时没有严格区分；
3. 个别工程推论被写成源码事实，例如把 Trae 论文中的 test-time scaling 当成开源实现，把 CodeWhale 尚未接入的 three-zone scaffolding 当成完整运行契约。

本轮目标不是否定此前报告，而是建立一份可复现的事实基线，并对所有高影响结论给出：**确认、部分确认、降级为推论、否定、待验证**。

## 2. 固定源码快照

调研日期：2026-06-04。通过 GitHub API 下载官方仓库默认分支 tarball，并以以下 commit 为唯一事实基线：

| 项目 | 官方仓库 / 分支 | 固定 commit | 本地扫描文件数 |
|---|---|---|---:|
| Claude Code | `anthropics/claude-code@main` | [`b67fa4fa2c4f42e9b88a31f31906f3142bc165c5`](https://github.com/anthropics/claude-code/commit/b67fa4fa2c4f42e9b88a31f31906f3142bc165c5) | 203 |
| Codex | `openai/codex@main` | [`16d02ec77c6337ccea02a8c909e05bf3d905f887`](https://github.com/openai/codex/commit/16d02ec77c6337ccea02a8c909e05bf3d905f887) | 4,816 |
| Trae Agent | `bytedance/trae-agent@main` | [`e839e559ac61bdd0e057c375dd1dee391fee797d`](https://github.com/bytedance/trae-agent/commit/e839e559ac61bdd0e057c375dd1dee391fee797d) | 108 |
| Reasonix | `esengine/DeepSeek-Reasonix@main-v2` | [`174d344ec74b826754b46edbf367cd69a26250c0`](https://github.com/esengine/DeepSeek-Reasonix/commit/174d344ec74b826754b46edbf367cd69a26250c0) | 601 |
| Hermes Agent | `NousResearch/hermes-agent@main` | [`d3fab54933c3866d2c7cf5e51dc63e9e494c9f47`](https://github.com/NousResearch/hermes-agent/commit/d3fab54933c3866d2c7cf5e51dc63e9e494c9f47) | 4,698 |
| CodeWhale | `Hmbown/CodeWhale@main` | [`8dff2f7525ead210a01347b48f53ae3f20d094ec`](https://github.com/Hmbown/CodeWhale/commit/8dff2f7525ead210a01347b48f53ae3f20d094ec) | 605 |

> 文件数用于说明扫描规模，不等于逐文件完成度；生成文件、资源、测试和源码均计入。

## 3. 复核规则

### 3.1 证据等级

```text
A0：固定 commit 的真实运行路径 + 测试共同证明
A1：固定 commit 的实现源码证明，但未确认真实调用路径或运行测试
A2：固定 commit 的 README / docs / config 证明
B：基于 A 级事实的工程推论，必须写“推论”
C：非官方逆向、社区镜像或未固定版本线索
N：没有在官方开源源码中找到证据
```

### 3.2 实现成熟度必须分层

```text
存在声明 / 文档
存在类型、函数或模块
存在单元测试
接入真实请求 / turn loop
存在端到端测试
可证明生产成熟
```

不能因为模块名存在就直接跳到“已产品化”或“A 级成熟”。

### 3.3 本轮实际执行

- 扫描六个官方仓库目录与关键源文件；
- 用 `rg` 定位旧报告中的关键符号和声明；
- 阅读 Agent loop、context/compaction、provider、tool、trajectory、prefix cache 等核心实现；
- 核查关键机制是否进入真实调用路径；
- 比对旧报告与当前固定 commit；
- 直接修订误导性总评，并新增校准报告。

## 4. 本轮最重要的纠偏

1. **Claude Code**：官方仓库仍没有完整 engine 源码；任何 engine 内部判断都不能升级为官方源码事实。
2. **Codex**：typed context、turn loop、compaction、approval/sandbox 等结论成立，但仓库高速变化，原报告中的路径和“终版”措辞需要降级。
3. **Trae Agent**：开源源码确有 Agent loop、trajectory、Docker、MCP 和有状态 sequential thinking；**没有发现 generation–pruning–selection / multi-candidate test-time scaling 的开源实现**。
4. **Reasonix**：多数 DeepSeek-native 结论有真实源码支撑；但“最优”“A 级成熟”“可直接迁移”等评分仍是评估，不是源码事实。
5. **Hermes Agent**：tool registry、progressive disclosure、trajectory compression 有真实实现；“tool schema caching 是为模型上下文成本设计”等动机判断应标记为推论。
6. **CodeWhale**：PrefixStabilityManager 已在 turn loop 校验 system prompt + tool catalog；但 `prompt_zones.rs` 的完整 three-zone 结构明确写着 **not yet wired into the request path**，旧报告把两者合并为完整 three-zone contract，属于过度陈述。

## 5. 对后续报告的强制要求

- 所有源码链接固定到 commit SHA，禁止只链接 `main`；
- 每个强结论必须标注 A0/A1/A2/B/C/N；
- “终版”“完整”“直接迁移”“生产级”必须有 E2E 或运行证据；
- docs/README 只能证明产品声明，不能自动证明实现；
- 模块存在只能证明 A1，必须追踪调用方才能声称接入真实 runtime；
- 项目快速变化时，报告标题和状态使用“截至 commit X 的校准版”。
