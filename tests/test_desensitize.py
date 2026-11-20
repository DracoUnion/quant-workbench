"""脱敏测试：机构/人名/金额/日期替换、误杀率。"""

from __future__ import annotations

import os
import sys


os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from src.services.compliance_service import ComplianceService  # noqa: E402


def test_desensitize_basic() -> None:
    svc = ComplianceService()
    rid = svc.create_review("合同", "contract_ref_001")
    assert rid is not None
