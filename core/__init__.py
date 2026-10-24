# -*- coding: utf-8 -*-
"""
via54SocialROI — Smart Dual-Tier Architecture Loader (Private Pro Core vs Open-Core Demo)
动态双模架构加载器：
- 当本机存在私有核心目录 `private_core/`（且未强制开启 Demo 模式）时，自动挂载商业完整版算法引擎 (`PRO_PRIVATE_CORE`)；
- 当从 GitHub 克隆公开仓库（不含 `private_core/`）时，自动无缝回退至开源架构演示与沙盒测试引擎 (`OPEN_CORE_DEMO`)。
"""

from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
PRIVATE_CORE_DIR = REPO_ROOT / "private_core"


def _load_private_module(module_alias: str, pro_filename: str) -> Any:
    file_path = PRIVATE_CORE_DIR / pro_filename
    spec = importlib.util.spec_from_file_location(module_alias, str(file_path))
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load spec for {file_path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_alias] = mod
    spec.loader.exec_module(mod)
    return mod


FORCE_DEMO = os.environ.get("VIA54_FORCE_DEMO_MODE", "0").strip() == "1"
HAS_PRIVATE_CORE = (PRIVATE_CORE_DIR / "models_core_pro.py").exists() and not FORCE_DEMO

if HAS_PRIVATE_CORE:
    EDITION = "PRO_PRIVATE_CORE"
    _crawler_mod = _load_private_module("marvis_crawler", "marvis_crawler_pro.py")
    _models_mod = _load_private_module("models_core", "models_core_pro.py")
    _ingest_mod = _load_private_module("multimodal_ingest", "multimodal_ingest_pro.py")
    _agent_mod = _load_private_module("agent_hub", "agent_hub_pro.py")
    _monitor_mod = _load_private_module("hourly_monitor", "hourly_monitor_pro.py")
    _report_mod = _load_private_module("report_generator", "report_generator_pro.py")

    OmniSocialPromotionEngine = _models_mod.OmniSocialPromotionEngine
    ProductInput = _models_mod.ProductInput
    SocialAccountProfile = _models_mod.SocialAccountProfile
    Stage2ContentInput = _models_mod.Stage2ContentInput
    generate_smart_stage2_from_product = _models_mod.generate_smart_stage2_from_product
    MarvisSocialCrawler = _crawler_mod.MarvisSocialCrawler
    KB_EMPIRICAL_PROFILES = _crawler_mod.KB_EMPIRICAL_PROFILES
    detect_platform_from_url = _crawler_mod.detect_platform_from_url
    parse_chinese_number = _crawler_mod.parse_chinese_number
    MultiModalIngestor = _ingest_mod.MultiModalIngestor
    UnifiedAgentHub = _agent_mod.UnifiedAgentHub
    HourlyAccountMonitor = _monitor_mod.HourlyAccountMonitor
    generate_bilingual_markdown_report = _report_mod.generate_bilingual_markdown_report
else:
    EDITION = "OPEN_CORE_DEMO"
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

__all__ = [
    "EDITION",
    "HAS_PRIVATE_CORE",
    "OmniSocialPromotionEngine",
    "ProductInput",
    "SocialAccountProfile",
    "Stage2ContentInput",
    "generate_smart_stage2_from_product",
    "MarvisSocialCrawler",
    "detect_platform_from_url",
    "parse_chinese_number",
    "MultiModalIngestor",
    "UnifiedAgentHub",
    "HourlyAccountMonitor",
    "generate_bilingual_markdown_report",
]
