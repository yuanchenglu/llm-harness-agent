# Stage 5：PRD、UX 与研发拆解 v0.1

> 证据状态：研究型 MVP PRD v0.1；不满足生产 PRD 的安全、恢复、验收任务集与发布 Gate。

## MVP 范围

用户在本地仓库运行 CLI，提出阅读/分析任务；Agent 可使用受工作区边界保护的 `read_file` 与 `search` 工具，最多执行固定步数并返回答案及 usage。用户也可运行 protocol/prefix benchmark。

### 必须满足

- API key 仅来自环境变量；
- 路径不能逃逸 workspace；
- thinking tool loop 保留 `reasoning_content`；
- trace 脱敏且默认不提交；
- 网络错误与协议错误可区分；
- Agent 有最大步数停止条件。

### 明确不在本 MVP

模型驱动写文件、shell 执行、自动 Git 提交、多 Agent、GUI、自动 Pro 路由。这些需要权限/回滚/benchmark 后再开放。

## UX

```bash
# 验证 API 与缓存
PYTHONPATH=src python -m deepseek_agent.benchmark all --repeats 2

# 运行只读代码 Agent
PYTHONPATH=src python -m deepseek_agent.cli "解释这个仓库的入口" --workspace .
```

失败时返回结构化 `status/error/step`；成功时返回 `content/usage/step`。

## 研发拆解与验收

| Epic | 状态 | 验收 |
|---|---|---|
| Provider + recorder | 已完成 | live models/chat、脱敏、指纹 |
| Protocol/prefix Harness | 已完成 P0 Pilot | suite 可重复运行，结果不入 Git |
| Read-only Agent loop | 已完成 | tool loop、step limit、workspace boundary |
| Permission + write tools | 后续 | 每类副作用显式审批、diff/rollback |
| Session + checkpoint | 后续 | 中断恢复且 evidence 完整 |
| Router/Pro review | 后续 | 统一真实任务 benchmark 证明收益 |

## 发布 Gate

MVP 是研究/开发预览：单元测试通过、live smoke 通过、无密钥入库、已记录已知限制。它不是生产级自主编码 Agent。
