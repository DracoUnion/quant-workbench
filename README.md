# 金融智能体工作台（QuantWorkbench）

对齐架构 `xhs-workbench`：PySide6 + SQLAlchemy 2 + Alembic + Agent 运行时 + 零 Qt 架构层。把 P001—P076 提示词库与 W0—W9 十条工作流落地为可运行、可编排、可留痕、可审计的桌面程序。

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 首次启动（自动建表、播种种子、弹出主窗口）
python -m src
# 或双击运行：python src/main.py

# 3. 运行测试
pytest -q
```

## 目录结构（摘要）

```
src/                    零 Qt 业务层与 UI 层（唯一 PySide6 依赖在 gui/、main_window.py、theme.py）
  common/               AppContext、EventHub（零 Qt）
  core/                 配置、数据库、业务事件总线 EventBus（零 Qt）
  tasks/                TaskManager、InlineExecutor 运行执行器（零 Qt）
  models/               SQLAlchemy 2 ORM 模型（28 张表）
  services/             提示词/工作流/运行/知识库/投研/组合/信号/事件/客户/合规/办公服务
  seed/                 P001-P076 提示词种子、W0-W9 工作流定义
  agents/、tools/、adapters/  Agent 运行时、工具注册与外部适配器（Mock 优先）
  main.py               入口：.env → init_db → seed → QApplication → MainWindow
  main_window.py        左侧导航 + 右侧页面堆栈（13 个页面）
client.py               ApiClient 进程内直连 services，保留 HTTP 接口形状
ws_client.py            EventBus → Qt 信号事件桥
tests/                  test_arch / test_prompt_seed / test_workflow_engine / ...
```

## 验收

- `pytest -q` 全过（架构零 Qt 扫描、P001-P076 种子、W0 DAG/拓扑、内联运行器、合规脱敏等）。
- `alembic -c alembic.ini upgrade head` 一键建表。
- 桌面端强制 `DATABASE_URL=sqlite:///src/data/fin_workbench.db` + `RUN_EXECUTOR=inline`（见 `.env`）。
