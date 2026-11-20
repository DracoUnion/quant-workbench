"""演示数据：组合、客户、知识库样例。"""

from __future__ import annotations

from ..services.portfolio_service import PortfolioService
from ..services.client_service import ClientService
from ..services.knowledge_service import KnowledgeService


def seed_demo() -> None:
    """导入演示数据（幂等）。"""
    portfolio_service = PortfolioService()
    client_service = ClientService()
    knowledge_service = KnowledgeService()

    # 演示组合
    pid = portfolio_service.create("老王核心组合", "老王", base_currency="CNY", risk_level="medium")
    print(f"[seed] 组合已创建：{pid}")

    # 演示客户
    cid = client_service.create("张三", risk_level="medium", stage="active")
    print(f"[seed] 客户已创建：{cid}")

    # 演示知识库
    kid = knowledge_service.create_kb("半导体行业库", domain="半导体", description="半导体行业研报与政策")
    print(f"[seed] 知识库已创建：{kid}")
    did = knowledge_service.ingest_doc(kid, "pdf", "研报/半导体2026.pdf", "半导体2026年研报", "半导体行业2026年发展迅速...")
    print(f"[seed] 文档已入库：{did}")


if __name__ == "__main__":
    seed_demo()
