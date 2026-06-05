# Stage 6：Fork / 整合 / MVP 实现与交接

> 状态：**只读研究型 MVP 已完成，但完整 Stage 6 未完成。** 已完成 OpenCode 固定 commit 源码 Spike；Fork/Adapter live 集成、生产安全层和真实任务验收仍未完成。

## 已实现

- `src/deepseek_agent/core.py`：配置、raw HTTP Provider、请求指纹、脱敏 recorder、thinking tool-loop、工作区只读工具；
- `src/deepseek_agent/benchmark.py`：协议与 Prefix Cache suite；
- `benchmarks/protocol/tool_loop_matrix.py`：reasoning replay/drop 实测探针；
- `src/deepseek_agent/cli.py`：可运行 CLI；
- `tests/test_core.py`：安全边界、脱敏、统计与序列化测试。

## 为什么不能声称 Fork / 整合完成

当前 MVP 用不足量代码验证了真正的 DeepSeek-specific 风险：silent-ignore 参数、reasoning tool-loop 差异、cache telemetry。此时 Fork 大型 runtime 会扩大变量和维护面。进入生产实现前，应以同一任务集比较“OpenCode adapter”与当前 runtime 的修改量、协议控制力和 trace 完整度，再作 Fork ADR。

## 已知限制

- Prefix Pilot 每 case 仅两次，不能作为稳定性/成本承诺；
- drop reasoning 的单次 200 与官方文档冲突，语义正确性未知；
- 无 streaming TTFT、并发、TTL、Pro、跨日数据；
- MVP 为只读，无写文件/shell/session persistence；
- 当前工具 schema 统一使用 `input`，尚未实现强类型工具注册。

## 下一位 AI 的继续提示词

```text
你正在继续 /workspace/deepseekagent。先阅读：
1. docs/.../03-5-.../18-1-科研严谨性复核与阶段重评-Scientific-Rigor-Audit.md
2. docs/llm-harness-agent/zh/blueprint/stage-gates.json
3. docs/.../07-.../7-1-OpenCode-Adapter-Spike.md
4. docs/.../07-.../7-2-Stage6-完成定义与阻塞项.md

不要提交 API key 或 benchmarks/results。先运行 PYTHONPATH=src python -m unittest discover -s tests -v。
先轮换已暴露的 Key。下一任务只扩大 P0 证据：分别对 Flash/Pro、thinking on/off、3+ 工具轮次运行 replay/drop；加入流式 TTFT、TTL、并发和跨日实验；保存可复算的脱敏 evidence bundle。然后用 20–30 个确定性任务对比当前 runtime 与 OpenCode Adapter。若要开放写文件或 shell，必须先实现 permission policy、diff preview、workspace sandbox、rollback 和对应测试。所有结论区分官方声明、单次观察、重复实验和真实任务 benchmark。
```
