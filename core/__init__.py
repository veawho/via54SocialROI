# -*- coding: utf-8 -*-
"""
via54SocialROI — Open-Core Base Architecture & Trial Sandbox Loader
公开试用版与基础架构加载器 (Open-Core Trial & Base Architecture Edition):
- 仅包含五层基础架构协议接口 (`core/interfaces.py`, `core/schemas.py`) 与确定性试用沙盒 (`core/demo_engine.py`)。
- 商业完整版专有算法与实时爬虫已独立封装于私有仓库 `veawho/via54SocialROIPro`。
"""

from __future__ import annotations

from core.demo_engine import (
    DemoAgentHub as UnifiedAgentHub,
    DemoHourlyMonitor as HourlyAccountMonitor,
    DemoMultiModalIngestor as MultiModalIngestor,
    DemoPromotionEngine as OmniSocialPromotionEngine,
    DemoSocialCrawler as MarvisSocialCrawler,
    KB_EMPIRICAL_PROFILES,
    detect_platform_from_url,
    generate_bilingual_markdown_report,
    generate_smart_stage2_from_product,
    parse_chinese_number,
)
from core.schemas import ProductInput, SocialAccountProfile, Stage2ContentInput

EDITION = "OPEN_CORE_DEMO"
HAS_PRIVATE_CORE = False

__all__ = [
    "EDITION",
    "HAS_PRIVATE_CORE",
    "OmniSocialPromotionEngine",
    "ProductInput",
    "SocialAccountProfile",
    "Stage2ContentInput",
    "generate_smart_stage2_from_product",
    "MarvisSocialCrawler",
    "KB_EMPIRICAL_PROFILES",
    "detect_platform_from_url",
    "parse_chinese_number",
    "MultiModalIngestor",
    "UnifiedAgentHub",
    "HourlyAccountMonitor",
    "generate_bilingual_markdown_report",
]
