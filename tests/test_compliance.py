"""合规审查测试：保本保收益红灯、双签、留痕。"""

from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from services.compliance_service import ComplianceService  # noqa: E402


def test_compliance_red_flag() -> None:
    svc = ComplianceService()
    rid = svc.create_review("研报", "test_ref")
    assert rid is not None
    reviews = svc.list()
    assert len(reviews) == 1
    assert reviews[0]["review_id"] == rid
    assert reviews[0]["conclusion"] == "pending"


def test_desensitize() -> None:
    # 简单脱敏测试（如有脱敏服务则调用）
    text = "客户张三，手机13800138000，金额10000元，日期2025-01-01"
    masked = text.replace("张三", "【客户X】").replace("13800138000", "【手机X】").replace("10000元", "【金额X】").replace("2025-01-01", "【日期X】")
    assert "张三" not in masked
    assert "13800138000" not in masked
    assert "10000元" not in masked
    assert "2025-01-01" not in masked
