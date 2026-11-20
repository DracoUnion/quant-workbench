"""初始迁移：全部业务表。

对齐任务书第 5 节数据模型：prompt/workflow/run/knowledge/research/portfolio/
signal/event/client/compliance/office/platform 全部表。
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ---------- prompt ----------
    op.create_table(
        "prompt_template",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False, comment="模板编号 P001…P076"),
        sa.Column("title", sa.String(length=200), nullable=False, comment="模板标题"),
        sa.Column("category", sa.String(length=64), nullable=False, comment="一级分类"),
        sa.Column("sub_category", sa.String(length=64), server_default="", nullable=False, comment="二级分类"),
        sa.Column("body", sa.Text(), nullable=False, comment="提示词正文 Markdown"),
        sa.Column("params_json", sa.JSON(), server_default="{}", nullable=False, comment="结构化参数"),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False, comment="模板版本号"),
    )
    op.create_index("ix_prompt_template_code", "prompt_template", ["code"], unique=True)

    op.create_table(
        "prompt_version",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("prompt_id", sa.Integer(), nullable=False, comment="版本所属模板"),
        sa.Column("version", sa.Integer(), nullable=False, comment="版本号"),
        sa.Column("body", sa.Text(), nullable=False, comment="该版本的正文"),
        sa.Column("diff", sa.Text(), nullable=True, comment="与上一版本的差异"),
        sa.ForeignKeyConstraint(["prompt_id"], ["prompt_template.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_prompt_version_prompt_id", "prompt_version", ["prompt_id"])

    # ---------- workflow ----------
    op.create_table(
        "workflow_definition",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("code", sa.String(length=16), nullable=False, comment="工作流编号 W0…W9"),
        sa.Column("name", sa.String(length=128), nullable=False, comment="工作流名称"),
        sa.Column("description", sa.Text(), server_default="", nullable=False, comment="描述"),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False, comment="版本号"),
        sa.Column("status", sa.String(length=16), server_default="draft", nullable=False, comment="draft/published/archived"),
        sa.Column("config_json", sa.JSON(), server_default="{}", nullable=False, comment="全局参数"),
    )
    op.create_index("ix_workflow_definition_code", "workflow_definition", ["code"], unique=True)

    op.create_table(
        "workflow_node",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("workflow_id", sa.Integer(), nullable=False, index=True, comment="所属工作流"),
        sa.Column("node_key", sa.String(length=64), nullable=False, index=True, comment="节点唯一标识"),
        sa.Column("node_type", sa.String(length=32), nullable=False, comment="节点类型 llm/tool/branch/parallel/gate/…"),
        sa.Column("prompt_code", sa.String(length=64), nullable=True, comment="绑定的提示词编号 P001…"),
        sa.Column("tool_key", sa.String(length=64), nullable=True, comment="工具 key"),
        sa.Column("config_json", sa.JSON(), server_default="{}", nullable=False, comment="节点参数"),
        sa.Column("order", sa.Integer(), server_default="0", nullable=False, comment="执行顺序"),
        sa.ForeignKeyConstraint(["workflow_id"], ["workflow_definition.id"], ondelete="CASCADE"),
    )

    op.create_table(
        "workflow_edge",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("workflow_id", sa.Integer(), nullable=False, index=True, comment="所属工作流"),
        sa.Column("from_node", sa.String(length=64), nullable=False, index=True, comment="源节点 key"),
        sa.Column("to_node", sa.String(length=64), nullable=False, index=True, comment="目标节点 key"),
        sa.Column("condition_json", sa.JSON(), server_default="{}", nullable=False, comment="分支条件（JSON Logic）"),
        sa.ForeignKeyConstraint(["workflow_id"], ["workflow_definition.id"], ondelete="CASCADE"),
    )

    # ---------- run ----------
    op.create_table(
        "workflow_run",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("workflow_id", sa.Integer(), nullable=False, index=True, comment="所属工作流"),
        sa.Column("status", sa.String(length=16), server_default="pending", nullable=False, index=True, comment="pending/running/blocked/done/failed/killed"),
        sa.Column("trigger_type", sa.String(length=32), server_default="manual", nullable=False, comment="手动/定时/事件/外部API"),
        sa.Column("input_json", sa.JSON(), server_default="{}", nullable=False, comment="运行输入参数"),
        sa.Column("context_json", sa.JSON(), server_default="{}", nullable=False, comment="运行上下文"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True, comment="开始时间"),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True, comment="结束时间"),
        sa.Column("operator", sa.String(length=64), nullable=True, comment="操作人"),
        sa.ForeignKeyConstraint(["workflow_id"], ["workflow_definition.id"], ondelete="CASCADE"),
    )

    op.create_table(
        "node_run",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("run_id", sa.Integer(), nullable=False, index=True, comment="所属运行"),
        sa.Column("node_key", sa.String(length=64), nullable=False, index=True, comment="节点 key"),
        sa.Column("node_type", sa.String(length=32), nullable=True, comment="节点类型"),
        sa.Column("status", sa.String(length=16), server_default="pending", nullable=False, index=True, comment="节点状态"),
        sa.Column("input_json", sa.JSON(), server_default="{}", nullable=False, comment="节点输入"),
        sa.Column("output_json", sa.JSON(), server_default="{}", nullable=False, comment="节点输出"),
        sa.Column("error", sa.Text(), nullable=True, comment="错误信息"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True, comment="开始时间"),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True, comment="结束时间"),
        sa.ForeignKeyConstraint(["run_id"], ["workflow_run.id"], ondelete="CASCADE"),
    )

    op.create_table(
        "run_event",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("run_id", sa.Integer(), nullable=False, index=True, comment="所属运行"),
        sa.Column("node_key", sa.String(length=64), nullable=True, index=True, comment="触发事件的节点 key"),
        sa.Column("event_type", sa.String(length=64), nullable=False, index=True, comment="事件类型"),
        sa.Column("payload_json", sa.JSON(), server_default="{}", nullable=False, comment="事件载荷"),
        sa.ForeignKeyConstraint(["run_id"], ["workflow_run.id"], ondelete="CASCADE"),
    )

    op.create_table(
        "artifact",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("run_id", sa.Integer(), nullable=False, index=True, comment="所属运行"),
        sa.Column("node_key", sa.String(length=64), nullable=True, index=True, comment="产出节点 key"),
        sa.Column("artifact_type", sa.String(length=32), nullable=False, comment="产出物类型"),
        sa.Column("title", sa.String(length=200), nullable=False, comment="产出物标题"),
        sa.Column("content", sa.Text(), nullable=True, comment="产出物内容"),
        sa.Column("file_path", sa.String(length=512), nullable=True, comment="产出物文件路径"),
        sa.Column("meta_json", sa.JSON(), server_default="{}", nullable=False, comment="元数据"),
        sa.ForeignKeyConstraint(["run_id"], ["workflow_run.id"], ondelete="CASCADE"),
    )

    # ---------- knowledge ----------
    op.create_table(
        "knowledge_base",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False, comment="知识库名称"),
        sa.Column("domain", sa.String(length=64), nullable=False, comment="领域"),
        sa.Column("description", sa.Text(), server_default="", nullable=False, comment="描述"),
        sa.Column("status", sa.String(length=16), server_default="draft", nullable=False, comment="状态"),
    )
    op.create_table(
        "knowledge_doc",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("kb_id", sa.Integer(), nullable=False, index=True, comment="所属知识库"),
        sa.Column("source_type", sa.String(length=32), nullable=False, comment="来源类型"),
        sa.Column("source_uri", sa.String(length=512), nullable=False, comment="来源 URI"),
        sa.Column("title", sa.String(length=200), nullable=False, comment="标题"),
        sa.Column("raw_text", sa.Text(), nullable=True, comment="原始文本"),
        sa.Column("cleaned_text", sa.Text(), nullable=True, comment="清洗后文本"),
        sa.Column("tags_json", sa.JSON(), server_default="{}", nullable=False, comment="标签"),
        sa.Column("credibility", sa.Float(), server_default="1.0", nullable=False, comment="可信度"),
        sa.ForeignKeyConstraint(["kb_id"], ["knowledge_base.id"], ondelete="CASCADE"),
    )
    op.create_table(
        "knowledge_chunk",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("doc_id", sa.Integer(), nullable=False, index=True, comment="所属文档"),
        sa.Column("chunk_index", sa.Integer(), nullable=False, comment="分片序号"),
        sa.Column("text", sa.Text(), nullable=False, comment="分片文本"),
        sa.Column("tokens", sa.Integer(), nullable=True, comment="token 数"),
        sa.Column("meta_json", sa.JSON(), server_default="{}", nullable=False, comment="元数据"),
        sa.ForeignKeyConstraint(["doc_id"], ["knowledge_doc.id"], ondelete="CASCADE"),
    )
    op.create_table(
        "vector_index_config",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("kb_id", sa.Integer(), nullable=False, index=True, comment="所属知识库"),
        sa.Column("field_mapping_json", sa.JSON(), server_default="{}", nullable=False, comment="字段映射"),
        sa.Column("recall_policy_json", sa.JSON(), server_default="{}", nullable=False, comment="召回策略"),
        sa.Column("dedup_rule_json", sa.JSON(), server_default="{}", nullable=False, comment="去重规则"),
        sa.ForeignKeyConstraint(["kb_id"], ["knowledge_base.id"], ondelete="CASCADE"),
    )

    # ---------- research ----------
    op.create_table(
        "research_task",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("type", sa.String(length=32), nullable=False, comment="report/financial/value/cashflow"),
        sa.Column("target", sa.String(length=200), nullable=False, comment="目标标的"),
        sa.Column("status", sa.String(length=16), server_default="pending", nullable=False, comment="任务状态"),
        sa.Column("run_id", sa.Integer(), nullable=True, index=True, comment="关联运行"),
        sa.ForeignKeyConstraint(["run_id"], ["workflow_run.id"], ondelete="SET NULL"),
    )
    op.create_table(
        "financial_statement",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("company", sa.String(length=200), nullable=False, comment="公司"),
        sa.Column("period", sa.String(length=32), nullable=False, comment="期间"),
        sa.Column("metrics_json", sa.JSON(), server_default="{}", nullable=False, comment="财务指标"),
        sa.Column("source_page", sa.String(length=512), nullable=True, comment="来源页"),
        sa.Column("anomaly_flag", sa.Boolean(), server_default="0", nullable=False, comment="异常标记"),
    )

    # ---------- portfolio ----------
    op.create_table(
        "portfolio",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False, comment="组合名称"),
        sa.Column("owner", sa.String(length=128), nullable=False, comment="所有者"),
        sa.Column("base_currency", sa.String(length=16), server_default="CNY", nullable=False, comment="基础币种"),
        sa.Column("risk_level", sa.String(length=16), server_default="medium", nullable=False, comment="风险等级"),
    )
    op.create_table(
        "position",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("portfolio_id", sa.Integer(), nullable=False, index=True, comment="所属组合"),
        sa.Column("symbol", sa.String(length=32), nullable=False, comment="证券代码"),
        sa.Column("qty", sa.Numeric(18, 6), server_default="0", nullable=False, comment="持仓数量"),
        sa.Column("cost", sa.Numeric(18, 6), server_default="0", nullable=False, comment="成本"),
        sa.Column("market_value", sa.Numeric(18, 6), server_default="0", nullable=False, comment="市值"),
        sa.ForeignKeyConstraint(["portfolio_id"], ["portfolio.id"], ondelete="CASCADE"),
    )
    op.create_table(
        "risk_snapshot",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("portfolio_id", sa.Integer(), nullable=False, index=True, comment="所属组合"),
        sa.Column("var", sa.Numeric(18, 6), server_default="0", nullable=False, comment="VaR"),
        sa.Column("exposure_json", sa.JSON(), server_default="{}", nullable=False, comment="敞口"),
        sa.Column("drawdown", sa.Numeric(18, 6), server_default="0", nullable=False, comment="回撤"),
        sa.Column("level", sa.String(length=16), server_default="green", nullable=False, comment="风险等级"),
        sa.ForeignKeyConstraint(["portfolio_id"], ["portfolio.id"], ondelete="CASCADE"),
    )

    # ---------- signal / event ----------
    op.create_table(
        "signal",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("source", sa.String(length=16), nullable=False, comment="来源 W5/W6"),
        sa.Column("symbol", sa.String(length=32), nullable=False, comment="证券代码"),
        sa.Column("signal_type", sa.String(length=32), nullable=False, comment="信号类型"),
        sa.Column("score", sa.Numeric(6, 3), server_default="0", nullable=False, comment="评分"),
        sa.Column("confidence", sa.Numeric(6, 3), server_default="0", nullable=False, comment="置信度"),
        sa.Column("payload_json", sa.JSON(), server_default="{}", nullable=False, comment="载荷"),
        sa.Column("status", sa.String(length=16), server_default="active", nullable=False, comment="状态"),
    )
    op.create_table(
        "alert",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("signal_id", sa.Integer(), nullable=False, index=True, comment="关联信号"),
        sa.Column("level", sa.String(length=16), nullable=False, comment="red/orange/yellow/green"),
        sa.Column("title", sa.String(length=200), nullable=False, comment="标题"),
        sa.Column("body", sa.Text(), nullable=True, comment="正文"),
        sa.Column("pushed_at", sa.DateTime(timezone=True), nullable=True, comment="推送时间"),
        sa.Column("ack_by", sa.String(length=128), nullable=True, comment="确认人"),
        sa.ForeignKeyConstraint(["signal_id"], ["signal.id"], ondelete="CASCADE"),
    )
    op.create_table(
        "event_card",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False, comment="事件类型"),
        sa.Column("target", sa.String(length=200), nullable=False, comment="目标"),
        sa.Column("decoded_json", sa.JSON(), server_default="{}", nullable=False, comment="解码结果"),
        sa.Column("history_winrate", sa.Float(), server_default="0", nullable=False, comment="历史胜率"),
        sa.Column("risk_json", sa.JSON(), server_default="{}", nullable=False, comment="风险JSON"),
    )

    # ---------- client ----------
    op.create_table(
        "client",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False, comment="客户姓名"),
        sa.Column("risk_level", sa.String(length=16), nullable=False, comment="风险等级"),
        sa.Column("stage", sa.String(length=32), nullable=False, comment="客户阶段"),
        sa.Column("tags_json", sa.JSON(), server_default="{}", nullable=False, comment="标签"),
    )
    op.create_table(
        "client_profile",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("client_id", sa.Integer(), nullable=False, index=True, comment="客户ID"),
        sa.Column("profile_json", sa.JSON(), server_default="{}", nullable=False, comment="画像JSON"),
        sa.ForeignKeyConstraint(["client_id"], ["client.id"], ondelete="CASCADE"),
    )
    op.create_table(
        "kyc_review",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("client_id", sa.Integer(), nullable=False, index=True, comment="客户ID"),
        sa.Column("result", sa.String(length=32), nullable=False, comment="审核结果"),
        sa.Column("issues_json", sa.JSON(), server_default="{}", nullable=False, comment="问题列表"),
        sa.Column("aml_level", sa.String(length=16), nullable=True, comment="AML等级"),
        sa.Column("reviewer", sa.String(length=128), nullable=True, comment="审核人"),
        sa.ForeignKeyConstraint(["client_id"], ["client.id"], ondelete="CASCADE"),
    )

    # ---------- compliance ----------
    op.create_table(
        "compliance_review",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("doc_type", sa.String(length=32), nullable=False, comment="文档类型"),
        sa.Column("source_ref", sa.String(length=200), nullable=False, comment="来源引用"),
        sa.Column("conclusion", sa.String(length=32), server_default="pending", nullable=False, comment="审查结论"),
        sa.Column("issues_json", sa.JSON(), server_default="{}", nullable=False, comment="问题列表"),
        sa.Column("rewrite_json", sa.JSON(), server_default="{}", nullable=False, comment="改写建议"),
        sa.Column("reviewer", sa.String(length=128), nullable=True, comment="审查人"),
        sa.Column("signed_by", sa.String(length=128), nullable=True, comment="双签人"),
    )

    # ---------- office ----------
    op.create_table(
        "weekly_report",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("owner", sa.String(length=128), nullable=False, comment="所有者"),
        sa.Column("period", sa.String(length=32), nullable=False, comment="期间"),
        sa.Column("content_md", sa.Text(), nullable=True, comment="Markdown 内容"),
        sa.Column("status", sa.String(length=16), server_default="draft", nullable=False, comment="状态"),
    )
    op.create_table(
        "meeting_note",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False, comment="标题"),
        sa.Column("time", sa.DateTime(timezone=True), nullable=True, comment="会议时间"),
        sa.Column("attendees", sa.String(length=512), nullable=True, comment="与会人员"),
        sa.Column("decisions_json", sa.JSON(), server_default="{}", nullable=False, comment="决议"),
        sa.Column("actions_json", sa.JSON(), server_default="{}", nullable=False, comment="行动项"),
    )

    # ---------- platform ----------
    op.create_table(
        "audit_log",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("actor", sa.String(length=128), nullable=True, comment="操作者"),
        sa.Column("action", sa.String(length=64), nullable=False, comment="动作"),
        sa.Column("target", sa.String(length=200), nullable=True, comment="目标"),
        sa.Column("payload_json", sa.JSON(), server_default="{}", nullable=False, comment="载荷"),
    )


def downgrade() -> None:
    op.drop_table("audit_log")
    op.drop_table("meeting_note")
    op.drop_table("weekly_report")
    op.drop_table("compliance_review")
    op.drop_table("kyc_review")
    op.drop_table("client_profile")
    op.drop_table("client")
    op.drop_table("event_card")
    op.drop_table("alert")
    op.drop_table("signal")
    op.drop_table("risk_snapshot")
    op.drop_table("position")
    op.drop_table("portfolio")
    op.drop_table("financial_statement")
    op.drop_table("research_task")
    op.drop_table("vector_index_config")
    op.drop_table("knowledge_chunk")
    op.drop_table("knowledge_doc")
    op.drop_table("knowledge_base")
    op.drop_table("artifact")
    op.drop_table("run_event")
    op.drop_table("node_run")
    op.drop_table("workflow_run")
    op.drop_table("workflow_edge")
    op.drop_table("workflow_node")
    op.drop_index("ix_workflow_definition_code", table_name="workflow_definition")
    op.drop_table("workflow_definition")
    op.drop_index("ix_prompt_version_prompt_id", table_name="prompt_version")
    op.drop_table("prompt_version")
    op.drop_index("ix_prompt_template_code", table_name="prompt_template")
    op.drop_table("prompt_template")
