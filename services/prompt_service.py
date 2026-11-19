"""零 Qt 提示词服务层。

纯函数/纯数据层，不导入任何 Qt 模块，可被 headless 测试。
职责：加载结构化提示词数据、按分类/关键词检索、收藏标记。
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Prompt:
    """单条提示词模板。"""

    id: str
    title: str
    category: str          # 一级分类，如“核心框架”、“Agent 架构”、“金融职场”
    sub_category: str      # 二级分类，如“三大范式”、“合规审查”
    description: str       # 一句简介
    role: str = ""         # Role / 角色定义
    parameters: str = ""   # 权重/参数配置
    context: str = ""      # 上下文背景
    workflow: str = ""     # 执行步骤
    constraints: str = ""  # 硬性约束
    output_format: str = ""# 输出样板
    tools: str = ""        # 调用工具
    full_text: str = ""    # 完整 Markdown 正文（用于复制与搜索）
    favorite: bool = False


class PromptService:
    """提示词服务。"""

    def __init__(self, data_path: str = "data/prompts.json") -> None:
        self.data_path = data_path
        self._prompts: dict[str, Prompt] = {}
        self._order: list[str] = []

    # ------------------------------------------------------------------ load
    def load(self) -> list[Prompt]:
        """从 JSON 加载；若文件缺失则回退内置默认数据。"""
        if os.path.exists(self.data_path):
            self._load_from_json(self.data_path)
        else:
            self._load_builtins()
        return list(self.all())

    def _load_from_json(self, path: str) -> None:
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        self._prompts.clear()
        self._order.clear()
        for item in raw:
            p = Prompt(**item)
            self._prompts[p.id] = p
            self._order.append(p.id)

    def _load_builtins(self) -> None:
        """内置少量种子数据，确保无 data 目录时仍可运行演示。"""
        seeds = [
            Prompt(
                id="core.secondary_template",
                title="第二代提示词参数化引导模板",
                category="核心框架",
                sub_category="通用骨架",
                description="金融场景提示词的配置文件结构：Role/Profile/Context/Workflow/Constraints/Output Format。",
                role="【身份、从业年限、核心圈层。越具体，代入感越强】",
                parameters="- 逻辑性：【0.9+】金融分析底线\n- 创造性：【低/中】合规风控压低，策略挖掘适中\n- 批判性思维：【高】尽调反诈必拉满\n- 风险厌恶：【高/低】决策激进与保守开关\n- 简洁性：【高】拒绝废话",
                context="【当下市场环境、具体标的、面临难题、最新数据快照】",
                workflow="1. 【数据清洗/事实核验】\n2. 【多维推理/对标分析】\n3. 【结论输出/风险揭示】",
                constraints="- 格式：必须 Markdown 表格\n- 长度：总计<500 字\n- 禁令：禁止“可能/大概/建议参考”等模糊兜底话术",
                output_format="【给一个理想结构，让 AI 按图索骥】",
                full_text="# 第二代提示词参数化引导模板\n\n## Role\n【身份、从业年限、核心圈层】\n\n## Profile（权重系统 0.0~1.0）\n- 逻辑性：0.9+\n- 创造性：低/中\n- 批判性思维：高\n- 风险厌恶：高/低\n- 简洁性：高\n\n## Context\n【实时上下文】\n\n## Workflow\n1. 数据清洗/事实核验\n2. 多维推理/对标分析\n3. 结论输出/风险揭示\n\n## Constraints\n- 禁用模糊兜底话术\n\n## Output Format\n【结构化样板】",
            ),
            Prompt(
                id="agent.standard_arch",
                title="Agent 四模块标准架构模板",
                category="Agent 架构",
                sub_category="Identity + Tools + Workflow + Constraints",
                description="零代码智能体的标准提示词骨架：Identity/Tools/Workflow/Constraints/Output Format。",
                role="【定义职位、服务对象、核心价值——具体到像真员工】",
                parameters="1. 【插件 A】：当用户询问……时，必须调用\n2. 【插件 B】：需计算/绘图/分析数据时，必须调用\n3. 【知识库 C】：涉及历史数据/内部制度/过往案例时，必须查询",
                context="用户意图与所需工具",
                workflow="Step 1：感知与意图判断 → 分析任务类型 & 所需工具\nStep 2：信息获取 → 调插件/查库，拿原始料\nStep 3：处理与分析 → 去重、清洗、验证\nStep 4：决策与判断 → 给明确结论 + 置信度\nStep 5：输出与交付 → 按指定格式生成报告或执行动作",
                constraints="- 拒答类型：直接荐买卖、预测点位等\n- 必标数据来源，禁编造\n- 信息不足/不确定 → 必须反问用户，禁主观臆测",
                output_format="【定义最终交付物：结构、风格、长度】",
                tools="联网搜索 / 文档阅读器 / 代码解释器 / 知识库",
                full_text="# Agent 四模块标准架构模板\n\n### Identity\n【定义职位、服务对象、核心价值】\n\n### Tools\n你拥有以下工具，严格按规则调用：\n1. 【插件 A】：当用户询问……时，必须调用\n2. 【插件 B】：需计算/绘图/分析数据时，必须调用\n3. 【知识库 C】：涉及历史数据/内部制度/过往案例时，必须查询\n\n### Workflow\nStep 1：感知与意图判断\nStep 2：信息获取\nStep 3：处理与分析\nStep 4：决策与判断\nStep 5：输出与交付\n\n### Constraints\n- 禁编造，必标来源\n- 信息不足必反问\n\n### Output Format\n【结构、风格、长度】",
            ),
            Prompt(
                id="finance.compliance_review",
                title="合规审查智能体（券商合规中台标配）",
                category="三大金融场景",
                sub_category="合规审查",
                description="对外发材料（研报/合同/营销/路演/员工言论）实施事前审查，拥有一票否决权。",
                role="你是 XX 证券 AI 合规审查官，向合规总监汇报。依据《证券法》、《监管条例》及内部《手册》，对外发材料实施事前审查。",
                parameters="- 规则遵从性：1.0（法条为最高准则）\n- 风险零容忍：0.95\n- 细节洞察力：0.9\n- 客户保护倾向：0.85",
                context="待审文件（研报/合同/海报/PPT/社媒发言等）",
                workflow="Step 1：来文分型与清单匹配\nStep 2：关键词扫描与风险初筛（高危/中危/低危）\nStep 3：逻辑一致性深度审查\nStep 4：案例比对与相似度溯源（>80% 强制高亮）\nStep 5：结构化审查报告生成",
                constraints="- 零容忍：涉及承诺保本保收益，直接红灯叫停\n- 全留痕：每次审查结论入档\n- 不背锅：放行权归业务负责人+合规总监双签",
                output_format="### 合规审查报告\n**审查结论**：严重违规 / 一般违规 / 建议修改 / 审核通过\n\n### 问题清单：\n#### ⛔ 严重违规\n**位置**：...\n**原文**：...\n**问题**：...\n**改写**：...",
                tools="文档阅读器 / 合规知识库 / 联网搜索",
                full_text="# 合规审查智能体\n\n## Identity\n你是 XX 证券 AI 合规审查官...\n\n## Workflow\nStep 1：来文分型与清单匹配\nStep 2：关键词扫描与风险初筛\nStep 3：逻辑一致性深度审查\nStep 4：案例比对与相似度溯源\nStep 5：结构化审查报告生成\n\n## Constraints\n- 零容忍：涉及承诺保本保收益，直接红灯叫停\n- 全留痕\n\n## Output Format\n【结构化审查报告】",
            ),
            Prompt(
                id="workflow.stock_alert",
                title="股价异动监控智能体",
                category="工作流编排",
                sub_category="条件判断节点",
                description="监控指定标的异常波动，触发预设条件即时预警，内置决策脑模拟成熟交易者思维。",
                role="你是一名纪律严明的交易哨兵，唯一使命是机械执行预设监控逻辑，不掺杂主观情绪，仅输出标准化信号。",
                parameters="- 涨幅 ≥ 8% → 强势异动\n- 跌幅 ≤ -6% → 弱势风险\n- 量比 ≥ 150% → 放量关注",
                context="目标标的实时价、涨跌幅、量比",
                workflow="1. 数据采集：调用同花顺 i 问财，抓取实时价、涨跌幅、量比。\n2. 规则判断与分流：涨幅≥8%/跌幅≤-6%/量比≥150%/均未触发。\n3. 深度溯源（仅警报触发时）：联网搜索核查公告/新闻；知识库复盘历史波动性格；技术指标多维共振确认。\n4. 报告产出：输出结构化《股价异动分析报告》。",
                constraints="- 不为微小波动叫嚣，只在规则红线被击穿时发声。\n- 报告必含五大板块：【异动类型】【实时数据】【可能原因】【历史对比】【操作建议】",
                output_format="【异动类型】【实时数据】【可能原因】【历史对比】【操作建议】",
                tools="同花顺 i 问财 / 联网搜索 / 知识库",
                full_text="# 股价异动监控智能体\n\n## Identity\n你是一名纪律严明的交易哨兵...\n\n## Workflow\n1. 数据采集\n2. 规则判断与分流\n3. 深度溯源\n4. 报告产出\n\n## Output Format\n【异动类型】【实时数据】【可能原因】【历史对比】【操作建议】",
            ),
            Prompt(
                id="workflow.rebalance",
                title="动态资产再平衡智能体",
                category="工作流编排",
                sub_category="网状工作流",
                description="每周一 9:00 自动唤醒，执行组合体检，按偏离度分级标记并生成调仓建议。",
                role="资产配置架构师，信奉系统化纪律，对抗人性弱点，专注组合动态平衡。",
                parameters="- 偏离度 ≥ 15% → 急需调整\n- 10% ≤ 偏离度 < 15% → 建议调整\n- 偏离度 < 10% → 继续观察",
                context="用户目标、风偏、基准配置；各资产当前市值",
                workflow="Phase 1：组合诊断（读取知识库目标/风偏，拉取市值，算偏离度）。\nPhase 2：分级标记（急需/建议/观察）。\nPhase 3：环境扫描（联网搜索宏观微观环境，修正调整激进度与时机）。\nPhase 4：方案生成（急需→直接下达买卖指令；建议→提供 2-3 套备选方案）。\nPhase 5：报告推送（产出《组合再平衡建议报告》，调用消息推送插件）。",
                constraints="- 单次调仓幅度 ≤ 组合总值 5%。\n- 个股财报前后 3 天禁交易区。\n- 所有建议强制附带风险评估章节。",
                output_format="【组合现状】【偏离度分析】【调整建议】【市场环境分析】【实施注意事项】",
                tools="知识库 / 数据接口 / 联网搜索 / 消息推送",
                full_text="# 动态资产再平衡智能体\n\n## Identity\n资产配置架构师...\n\n## Workflow\nPhase 1：组合诊断\nPhase 2：分级标记\nPhase 3：环境扫描\nPhase 4：方案生成\nPhase 5：报告推送\n\n## Constraints\n- 单次调仓幅度 ≤ 5%\n- 财报前后 3 天禁交易\n\n## Output Format\n【组合现状】【偏离度分析】【调整建议】【市场环境分析】【实施注意事项】",
            ),
        ]
        for p in seeds:
            self._prompts[p.id] = p
            self._order.append(p.id)

    # ------------------------------------------------------------------ query
    def all(self) -> list[Prompt]:
        return [self._prompts[i] for i in self._order]

    def get(self, prompt_id: str) -> Optional[Prompt]:
        return self._prompts.get(prompt_id)

    def by_category(self, category: str) -> list[Prompt]:
        return [p for p in self.all() if p.category == category]

    def categories(self) -> list[str]:
        seen: list[str] = []
        for p in self.all():
            if p.category not in seen:
                seen.append(p.category)
        return seen

    def sub_categories(self, category: str) -> list[str]:
        seen: list[str] = []
        for p in self.by_category(category):
            if p.sub_category not in seen:
                seen.append(p.sub_category)
        return seen

    def search(self, query: str) -> list[Prompt]:
        q = query.lower()
        if not q:
            return self.all()
        result = []
        for p in self.all():
            haystack = " ".join(
                [
                    p.title,
                    p.category,
                    p.sub_category,
                    p.description,
                    p.role,
                    p.full_text,
                ]
            ).lower()
            if q in haystack:
                result.append(p)
        return result

    def favorites(self) -> list[Prompt]:
        return [p for p in self.all() if p.favorite]

    def toggle_favorite(self, prompt_id: str) -> bool:
        p = self._prompts.get(prompt_id)
        if not p:
            return False
        p.favorite = not p.favorite
        return p.favorite

    def save(self, path: Optional[str] = None) -> None:
        target = path or self.data_path
        os.makedirs(os.path.dirname(target) or ".", exist_ok=True)
        data = [
            {
                "id": p.id,
                "title": p.title,
                "category": p.category,
                "sub_category": p.sub_category,
                "description": p.description,
                "role": p.role,
                "parameters": p.parameters,
                "context": p.context,
                "workflow": p.workflow,
                "constraints": p.constraints,
                "output_format": p.output_format,
                "tools": p.tools,
                "full_text": p.full_text,
                "favorite": p.favorite,
            }
            for p in self.all()
        ]
        with open(target, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
