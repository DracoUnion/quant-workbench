# 《金融智能体工作台（QuantWorkbench）开发任务书》

> 版本：v1.0  
> 对齐架构：`xhs-workbench`（PySide6 + SQLAlchemy 2 + Alembic + Agent 运行时 + 零 Qt 架构层）  
> 输入资产：P001—P076 提示词库 + W0—W9 十条工作流  
> 目标：把十条工作流落地为可运行、可编排、可留痕、可审计的桌面程序。

---

## 1. 项目目标与范围

### 1.1 目标
1. 将 **P001—P076** 全部沉淀为可版本化的 `PromptTemplate` 种子数据。
2. 将 **W0—W9** 全部沉淀为可执行的 `WorkflowDefinition`，支持 DAG 编排、条件分支、并行、熔断、人工闸门。
3. 提供桌面端 UI：提示词工坊、工作流编排、运行中心、知识库、投研、组合风控、短线信号、事件套利、客户经营、合规、办公自动化。
4. 架构严格对齐 `xhs-workbench`：`src/` 布局、零 Qt 架构层、`AppContext` 装配、`ApiClient` 进程内直连、`ws_client` → Qt signal 事件桥、`services.runs` daemon Thread + 独立 Session、状态机 `pending/running/blocked/done/failed/killed`。
5. 默认 SQLite + inline executor；可选 Postgres + Celery。

### 1.2 非目标（本期不做）
- 不做真实券商交易接口直连；交易类节点只产出“建议指令”，必须人工确认。
- 不做真实 WebSocket 服务；`ws_client.py` 仅订阅 `ws_manager` sink。
- 不做移动端/Web 端。
- 不实现真实向量数据库；知识库检索先用 SQLite FTS + 轻量向量占位接口，预留 `adapters/vector/`。

---

## 2. 架构原则（强制）

| 原则 | 要求 |
|---|---|
| 零 Qt 内核 | `common/ tasks/ core/ models/ services/ agents/ tools/ adapters/` **禁止 import PySide6** |
| 唯一 UI 层 | 仅 `gui/`、`main_window.py`、`widgets.py`、`theme.py` 可 import PySide6 |
| 依赖方向 | `gui → client → services/models/adapters/agents/tools → core/tasks → common`，禁止反向 |
| 形状兼容 | `client.py` 保留 HTTP 接口形状（方法名、入参、返回 dict），底层进程内直连 services |
| 事件双总线 | 业务事件 `core.events.EventBus`（Pydantic DomainEvent）；UI 事件 `common.events.EventHub` |
| 运行权威 | Agent/工作流 run 只走 `services.runs` + `tasks/runs.py`；桌面 `RUN_EXECUTOR=inline` |
| 会话隔离 | 每个 run 独立 SQLAlchemy Session，禁止跨线程共享 Session |
| 配置集中 | `.env` + `core/config.py`（pydantic-settings）；`bootstrap.py` 做 env 副作用 |
| 可测 | `tests/test_arch.py` 强制校验零 Qt 依赖与依赖方向 |

---

## 3. 目录结构（目标态）

```text
fin-workbench/
├─ pyproject.toml + requirements.txt + conftest.py + alembic/ + alembic.ini
├─ src/
│  ├─ __main__.py / main.py          # bootstrap env → init_db → auto_login → MainWindow
│  ├─ bootstrap.py                   # DATA_DIR/DATABASE_URL/RUN_EXECUTOR + build_context()
│  ├─ common/                        # ★ 零 Qt
│  │  ├─ events.py                   # EventHub（UI 事件适配）
│  │  ├─ context.py                  # AppContext（settings/event_hub/tasks/services）
│  │  └─ __init__.py
│  ├─ tasks/                         # ★ 零 Qt
│  │  ├─ task.py                     # Task/TaskState/TaskManager
│  │  ├─ celery_app.py / runs.py     # Celery + inline run 调度
│  │  └─ __init__.py
│  ├─ core/                          # config/database/events(EventBus)/logging/security/ws_manager
│  ├─ models/                        # prompt/workflow/run/knowledge/research/portfolio/
│  │                                 # signal/event/client/compliance/office/platform
│  ├─ services/                      # prompt/workflow/run/knowledge/research/portfolio/
│  │                                 # signal/event/client/compliance/office/auth/seed
│  ├─ agents/                        # runtime + prompts（AgentRuntime，Store/Provider/Sink）
│  ├─ tools/                         # registry + implementations + finance_tools
│  ├─ adapters/                      # llm/openai, search, market_data, doc_parser,
│  │                                 # multimodal, push, vector
│  ├─ client.py                      # ApiClient（进程内直连 services，保留 HTTP 形状）
│  ├─ ws_client.py                   # 订阅 ws_manager sink → Qt signal
│  ├─ main_window.py                 # 侧栏 QListWidget + QStackedWidget
│  ├─ gui/                           # dashboard/prompts/workflows/runs/knowledge/
│  │                                 # research/portfolio/signals/events/clients/
│  │                                 # compliance/office/settings
│  ├─ widgets.py / theme.py / styles.py / styles.qss
│  └─ data/                          # fin_workbench.db + logs（gitignored）
└─ tests/                            # test_scoring / test_tools / test_arch /
                                     # test_workflow_engine / test_prompt_seed /
                                     # test_compliance / test_desensitize
```

---

## 4. 核心抽象与装配

### 4.1 `AppContext`（`common/context.py`）
```python
@dataclass
class AppContext:
    settings: Settings
    event_hub: EventHub
    tasks: TaskManager
    services: ServiceRegistry   # 按域聚合的门面
    run_executor: RunExecutor   # inline / celery
```

### 4.2 `bootstrap.build_context()`
职责：
1. 设置 `DATA_DIR`、`DATABASE_URL=sqlite:///src/data/fin_workbench.db`、`RUN_EXECUTOR=inline`。
2. 构造 `Settings`、`EventHub`、`TaskManager`、`RunExecutor`、`ServiceRegistry`。
3. 返回 `AppContext`。

### 4.3 `ApiClient`（`client.py`）
- 模块级 `get_client()` 单例，进程内直连 `ServiceRegistry`。
- 方法按域分组：`prompt.* workflow.* run.* knowledge.* research.* portfolio.* signal.* event.* client.* compliance.* office.*`。
- 返回 dict（后续可加 `schemas/` Pydantic DTO，列入 TODO）。

### 4.4 事件桥
- `core/events/EventBus`：业务事件（RunStateChanged、NodeFinished、AlertRaised、GateBlocked）。
- `ws_manager`：sink 注册中心。
- `ws_client.py`：订阅 sink，转 `QtSignal` 推送 `gui/`。
- `common/events/EventHub`：UI 任务事件适配（进度、日志、提示）。

### 4.5 运行执行器
- `tasks/runs.py`：`RunExecutor` 接口，`InlineExecutor` 每 run 启 daemon Thread，独立 Session。
- `services/runs.py`：状态机 `pending/running/blocked/done/failed/killed`，checkpoint、review point、event sink、日志留痕。

---

## 5. 数据模型（`models/`）

| 模块 | 表 | 关键字段 |
|---|---|---|
| prompt | `prompt_template` | id, code(P001…), title, category, body, params_json, version |
| prompt | `prompt_version` | prompt_id, version, body, diff, created_at |
| workflow | `workflow_definition` | id, code(W0…W9), name, description, version, status |
| workflow | `workflow_node` | id, workflow_id, node_key, node_type(task/branch/parallel/gate/tool/llm), prompt_code, config_json, order |
| workflow | `workflow_edge` | id, workflow_id, from_node, to_node, condition_json |
| run | `workflow_run` | id, workflow_id, status, trigger_type, input_json, context_json, started_at, ended_at, operator |
| run | `node_run` | id, run_id, node_key, status, input_json, output_json, error, started_at, ended_at |
| run | `run_event` | id, run_id, node_key, event_type, payload_json, created_at |
| run | `artifact` | id, run_id, node_key, artifact_type, title, content, file_path, meta_json |
| knowledge | `knowledge_base` | id, name, domain, description, status |
| knowledge | `knowledge_doc` | id, kb_id, source_type, source_uri, title, raw_text, cleaned_text, tags_json, credibility |
| knowledge | `knowledge_chunk` | id, doc_id, chunk_index, text, tokens, meta_json |
| knowledge | `vector_index_config` | id, kb_id, field_mapping_json, recall_policy_json, dedup_rule_json |
| research | `research_task` | id, type(report/financial/value/cashflow), target, status, run_id |
| research | `financial_statement` | id, company, period, metrics_json, source_page, anomaly_flag |
| portfolio | `portfolio` | id, name, owner, base_currency, risk_level |
| portfolio | `position` | id, portfolio_id, symbol, qty, cost, market_value |
| portfolio | `risk_snapshot` | id, portfolio_id, var, exposure_json, drawdown, level, created_at |
| signal | `signal` | id, source(W5/W6), symbol, signal_type, score, confidence, payload_json, status |
| signal | `alert` | id, signal_id, level(red/orange/yellow/green), title, body, pushed_at, ack_by |
| event | `event_card` | id, event_type, target, decoded_json, history_winrate, risk_json |
| client | `client` | id, name, risk_level, stage, tags_json |
| client | `client_profile` | id, client_id, profile_json, updated_at |
| client | `kyc_review` | id, client_id, result, issues_json, aml_level, reviewer |
| compliance | `compliance_review` | id, doc_type, source_ref, conclusion, issues_json, rewrite_json, reviewer, signed_by |
| office | `weekly_report` | id, owner, period, content_md, status |
| office | `meeting_note` | id, title, time, attendees, decisions_json, actions_json |
| platform | `audit_log` | id, actor, action, target, payload_json, created_at |

> 所有表含 `created_at/updated_at`；关键动作写 `audit_log`。

---

## 6. 服务层（`services/`）

| 服务 | 职责 | 对应工作流 |
|---|---|---|
| `prompt_service` | 模板 CRUD、版本、渲染、参数校验 | W0 |
| `workflow_service` | 定义 CRUD、校验 DAG、发布版本 | W0 |
| `run_service` | 创建 run、调度、状态机、checkpoint、闸门 | 全部 |
| `knowledge_service` | 文档清洗、入库、检索、向量配置 | W0 |
| `research_service` | 财报提取、摘要、质疑、价值筛选、现金流诊断 | W1/W2 |
| `backtest_service` | 回测复盘、驳回审查、归因报告 | W3 |
| `portfolio_service` | 组合、持仓、风险快照、再平衡 | W4 |
| `signal_service` | 题材、异动、阿尔法、早盘/盘中决策板 | W5 |
| `event_service` | 事件卡、供应链、内部人、研报情绪、套利 | W6 |
| `client_service` | 画像、Client-360、KYC、话术 | W7 |
| `compliance_service` | 合规审查、脱敏、交易安全熔断 | W8 |
| `office_service` | 周报、月报、会议纪要、行动项 | W9 |
| `auth_service` / `seed_service` | 登录、种子数据 | 基础 |

---

## 7. 工作流引擎设计

### 7.1 节点类型
| 类型 | 说明 | 执行器 |
|---|---|---|
| `llm` | 调用大模型 + 渲染 prompt | `agents/runtime` |
| `tool` | 调用注册工具（搜索/i问财/代码解释器/文档/多模态/推送） | `tools/registry` |
| `branch` | 条件判断（JSON Logic） | `engine/branch` |
| `parallel` | 并行子节点 | `engine/parallel` |
| `gate` | 人工闸门（blocked 等待确认） | `engine/gate` |
| `transform` | 数据清洗/结构化/脱敏 | `services/…` |
| `notify` | 推送（微信/企微/站内） | `adapters/push` |
| `artifact` | 产出物落库 | `services/run` |

### 7.2 执行语义
- DAG 拓扑排序；`parallel` 节点 fan-out/fan-in。
- 每节点执行前后写 `node_run` + `run_event`。
- `gate` 节点将 run 置 `blocked`，UI 显示待确认；确认后恢复。
- 熔断规则：节点级 `timeout`、`max_retry`、`circuit_breaker`（如可信度<0.3 终止）。
- checkpoint：每节点完成写快照，支持从最近 checkpoint 重跑。

### 7.3 十条工作流种子（`seed/workflows.py`）

| 工作流 | 节点顺序（node_key） | 闸门 |
|---|---|---|
| W0 | identity→prompt→doc_clean→kb_update→vector_cfg→review | review |
| W1 | macro_fetch→cycle→factor→alloc→style→weekly_report | strategy_review |
| W2 | fin_extract→fin_summary→fin_challenge→batch_scan→value_screen→cashflow→research_review | research_review |
| W3 | backtest_review→reject_review→attribution→tech_diag→trend_signal→committee | committee |
| W4 | poll→anomaly→risk_score→risk_report→rebalance→notify | trade_confirm |
| W5 | news_trace→theme_score→lhb→alpha→premarket→intraday→safe_exec | trade_confirm |
| W6 | event_decode→supply_chain→insider→analyst_sentiment→arbitrage→longshort | strategy_review |
| W7 | talk_script→profile→risk_gap→client360→kyc→compliance | compliance_review |
| W8 | doc_classify→keyword_scan→logic_review→case_match→rewrite→signoff；desensitize；safe_trade | double_sign |
| W9 | weekly_draft→value_rewrite→auto_weekly→meeting_note→action_items→publish | self_review |

> 每个节点绑定 `prompt_code`（如 P007）或 `tool_key`，`config_json` 存参数（阈值、模板、输出格式）。

### 7.4 提示词种子（`seed/prompts.py`）
- 按 P001—P076 逐条入库，`code` 即编号，`category` 按工作流归类。
- `params_json` 抽取权重、约束、输出格式为结构化字段，便于 UI 表单渲染。
- 版本化：每次编辑生成 `prompt_version`。

---

## 8. 工具与适配器

### 8.1 工具注册（`tools/registry.py`）
| 工具 key | 实现 | 用于 |
|---|---|---|
| `web_search` | `adapters/search` | 溯源、资讯、供应链 |
| `iwencai` | `adapters/market_data` | 行情、财务、筛选 |
| `code_interpreter` | 沙箱执行 | 指标计算、回测、图表 |
| `doc_reader` | `adapters/doc_parser` | PDF/Word/表格 |
| `multimodal` | `adapters/multimodal` | K线/图表识别 |
| `push` | `adapters/push` | 微信/企微/站内 |
| `vector_search` | `adapters/vector` | 知识库检索 |

### 8.2 适配器（`adapters/`）
- `llm/openai`：统一 Provider 接口，支持 OpenAI 兼容。
- `search`、`market_data`、`doc_parser`、`multimodal`、`push`、`vector` 均定义抽象基类 + 离线 Mock 实现，测试用 Mock。

---

## 9. UI 设计（`gui/`）

### 9.1 主窗口
`main_window.py`：左侧 `QListWidget` 导航 + 右侧 `QStackedWidget`。

### 9.2 页面清单
| 页面 | 目录 | 核心能力 |
|---|---|---|
| 工作台总览 | `gui/dashboard` | 运行中 run、待确认闸门、预警卡片、快捷入口 |
| 提示词工坊 | `gui/prompts` | P001—P076 列表、参数表单、版本 diff、试运行 |
| 工作流编排 | `gui/workflows` | DAG 画布（QGraphicsScene）、节点配置、校验、发布 |
| 运行中心 | `gui/runs` | run 列表、节点时间线、日志、artifact、重跑、终止 |
| 知识库 | `gui/knowledge` | 文档导入、清洗预览、chunk、检索测试、向量配置 |
| 投研 | `gui/research` | 财报提取结果、质疑清单、价值清单、现金流诊断 |
| 组合风控 | `gui/portfolio` | 持仓、风险快照、预警、再平衡建议 |
| 短线信号 | `gui/signals` | 题材简报、龙虎榜、早盘/盘中决策板、阿尔法警报 |
| 事件套利 | `gui/events` | 事件卡、供应链、内部人、研报情绪、套利信号 |
| 客户经营 | `gui/clients` | 画像、Client-360、KYC、话术 |
| 合规 | `gui/compliance` | 审查单、脱敏工具、交易安全熔断状态 |
| 办公自动化 | `gui/office` | 周报、月报、会议纪要、行动项 |
| 设置 | `gui/settings` | 模型、数据源、推送、执行器、日志 |

### 9.3 交互约束
- UI 只调 `ApiClient`，不直接 import services。
- 长任务通过 `ws_client` 订阅事件，避免阻塞主线程。
- `gate` 节点在 UI 显示“待确认”，确认动作走 `client.run.confirm_gate(run_id, node_key, decision)`。

---

## 10. 线程模型

| 线程 | 职责 |
|---|---|
| Qt 主线程 | 窗口/页面/短查询 |
| daemon Thread（`services.runs`） | 工作流 run 执行（inline），独享 Session |
| Q 事件桥（`ws_client` → Qt signal） | 订阅 `ws_manager` sink 推送页面 |
| TaskManager 池（零 Qt） | 通用后台任务（导入、清洗、导出） |
| Celery（可选） | 非桌面部署分布式执行 |

---

## 11. 配置管理

`.env` + `core/config.py`：
- `DATABASE_URL`、`RUN_EXECUTOR`、`LLM_PROVIDER/API_KEY/BASE_URL`、`SEARCH_PROVIDER`、`MARKET_DATA_PROVIDER`、`PUSH_CHANNEL`、`REDIS/CELERY`（可选）。
- 桌面强制 `DATABASE_URL=sqlite:///src/data/fin_workbench.db`、`RUN_EXECUTOR=inline`。
- 日志：`src/data/logs`，按 run_id 分文件。
- 后续补 `gui/settings_store.py`（QSettings）存 UI 偏好。

---

## 12. 迁移与种子

1. Alembic 初始迁移：全部表。
2. `seed_service`：
   - 导入 P001—P076 提示词。
   - 导入 W0—W9 工作流定义与节点/边。
   - 导入工具注册表。
   - 导入演示数据（组合、客户、知识库样例）。
3. `python -m src.seed` 可重复执行（幂等）。

---

## 13. 测试策略

| 测试 | 内容 |
|---|---|
| `test_arch.py` | 零 Qt 依赖扫描；依赖方向；`AppContext` 装配；`TaskManager` 生命周期 |
| `test_prompt_seed.py` | P001—P076 全部入库、code 唯一、参数可解析 |
| `test_workflow_engine.py` | DAG 校验、branch/parallel/gate、状态机、checkpoint、熔断 |
| `test_services_*.py` | 各域服务单元测试（Mock 适配器） |
| `test_compliance.py` | 保本保收益红灯、双签、留痕 |
| `test_desensitize.py` | 机构/人名/金额/日期替换、误杀率 |
| `test_run_inline.py` | inline 执行、独立 Session、事件 sink |
| 离线适配器测试 | 搜索/行情/文档/多模态 Mock |

命令：
```bash
./.venv/Scripts/python.exe -m pytest tests -q
```

---

## 14. 里程碑与交付物

| 里程碑 | 内容 | 交付物 |
|---|---|---|
| M0 骨架 | src 布局、bootstrap、AppContext、TaskManager、EventBus/EventHub、client 空壳、MainWindow 空页 | 可启动空壳 + `test_arch` 通过 |
| M1 底座 W0 | 提示词工坊、工作流编排、运行中心、知识库、种子 P001—P076 + W0 | 可创建并跑通 W0 |
| M2 投研 W1/W2/W3 | 宏观、投研、回测页面与服务 | 跑通 W1/W2/W3，产出报告 |
| M3 交易风控 W4/W5/W6/W8 | 组合风控、短线信号、事件套利、合规安全 | 跑通 W4/W5/W6/W8，闸门与熔断生效 |
| M4 客户办公 W7/W9 | 客户经营、办公自动化 | 跑通 W7/W9 |
| M5 打包验收 | PyInstaller/Nuitka、日志、安装包、验收报告 | 可安装桌面版 + 验收清单 |

---

## 15. 验收标准

1. **架构**：`tests/test_arch.py` 通过；零 Qt 层无 PySide6 import；依赖方向无反向。
2. **种子**：P001—P076 全部入库且可渲染；W0—W9 全部可加载、DAG 校验通过。
3. **运行**：十条工作流各至少一次端到端跑通（Mock 适配器），状态机与 `node_run` 记录完整。
4. **闸门**：W4/W5/W7/W8 的人工闸门触发 `blocked`，确认后恢复。
5. **熔断**：低可信源<0.3 终止；合规保本保收益红灯；交易频率/浮亏/波动三重熔断生效。
6. **留痕**：每次 run 有 `run_event`、`artifact`、`audit_log`；合规审查可双签追溯。
7. **脱敏**：P075 对样例文本替换完整，说明计数准确。
8. **UI**：13 个页面可导航；长任务不阻塞主线程；事件桥推送正常。
9. **配置**：`.env` 切换 SQLite/Postgres、inline/celery 生效。
10. **打包**：生成可执行安装包，首次启动完成 init_db + seed + 登录。

---

## 16. 风险与 TODO

| 风险 | 应对 |
|---|---|
| 工作流节点多、编排复杂 | 先做 W0 引擎 + 3 条样板流，再批量配置 |
| 真实数据源不稳定 | 适配器抽象 + Mock 优先，真实源后接 |
| 向量检索缺失 | 先用 FTS + 预留 `adapters/vector` 接口 |
| 合规边界 | W8 强制人工双签，交易只出建议 |
| 性能 | 大文件/批量任务走 TaskManager，UI 只订阅事件 |
| 后续 TODO | 补 `schemas/` Pydantic DTO；`ServiceFacade` 类；`adapters→clients` 别名；`ui/settings_store.py`；打包 spec |

---

## 17. 开发约定

- 分支：`main` + `feat/w0-engine`、`feat/w1-w2-research`、`feat/w4-w5-risk-signal` 等。
- 提交：`feat(scope): ...`、`fix(scope): ...`、`test(scope): ...`。
- Code Review 必查：零 Qt 依赖、Session 隔离、事件留痕、闸门/熔断、合规措辞。
- 文档同步：`doc/prd.md`、`doc/概要设计.md`、`doc/详细设计.md`、`doc/架构设计.md` 与本任务书保持一致。

---

**结论**：本任务书以 `xhs-workbench` 为骨架，把 P001—P076 与 W0—W9 拆成“提示词资产 + 工作流定义 + 服务/工具/适配器 + UI 页面 + 运行与闸门”五层，按 M0—M5 分阶段交付，验收以“十条流可跑通、闸门熔断生效、全程留痕可审计”为准。