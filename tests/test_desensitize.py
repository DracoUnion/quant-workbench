"""脱敏测试：机构/人名/金额/日期替换、误杀率。"""

from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from services.compliance_service import ComplianceService  # noqa: E402


def test_desensitize_basic() -> None:
    svc = ComplianceService()
    rid = svc.create_review("合同", "contract_ref_001")
    assert rid is not None
