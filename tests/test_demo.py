# -*- coding: utf-8 -*-
"""
via54SocialROI — Public Open-Core Architecture & MCP / CLI Test Suite
验证开源架构演示引擎 (Open-Core Demo)、CLI 命令行、以及 MCP Server 工具协议
"""

from __future__ import annotations

import os
import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.demo_engine import (
    DemoAgentHub,
    DemoHourlyMonitor,
    DemoMultiModalIngestor,
    DemoPromotionEngine,
    DemoSocialCrawler,
    generate_bilingual_markdown_report,
    generate_smart_stage2_from_product,
)
from core.schemas import ProductInput, Stage2ContentInput
from mcp_server import MCP_TOOLS, handle_tool_call


class TestVia54SocialROIOpenCoreDemo(unittest.TestCase):
    def setUp(self) -> None:
        self.crawler = DemoSocialCrawler()
        self.engine = DemoPromotionEngine()
        self.ingestor = DemoMultiModalIngestor(self.crawler)
        self.agent_hub = DemoAgentHub(self.crawler)
        self.monitor = DemoHourlyMonitor(self.crawler, self.engine)

    def test_01_demo_crawler_and_profiles(self) -> None:
        prof = self.crawler.fetch_account_profile("xhs_medical_skincare_kol")
        self.assertEqual(prof.platform, "xiaohongshu")
        self.assertGreater(prof.followers, 10000)
        self.assertGreaterEqual(len(prof.recent_posts), 3)

    def test_02_stage1_and_stage2_monotonic_lift(self) -> None:
        prof = self.crawler.fetch_account_profile("xhs_medical_skincare_kol")
        prod = ProductInput(
            product_name="科复佳医用透明质酸钠修复贴 (Demo)",
            brand_name="科复佳",
            category="医疗器械/医用敷料",
            selling_price_rmb=118.0,
            campaign_budget_rmb=18500.0,
            core_selling_points=["国家二类医疗器械认证", "大小分子透明质酸复配"],
        )
        s1 = self.engine.compute_stage1_baseline(prof, prod)
        gen = generate_smart_stage2_from_product(prof, prod)
        s2_in = Stage2ContentInput(
            topics_hashtags=gen["topics"],
            campaign_theme=gen["campaign_theme"],
            script_content=gen["script_content"],
        )
        s2 = self.engine.compute_stage2_enhanced(prof, prod, s2_in)

        self.assertGreater(
            s2["enhanced_influence_effect"]["expected_views"],
            s1["influence_effect"]["expected_views"],
        )
        self.assertGreater(
            s2["enhanced_ecommerce_search_lift_effect"]["total_cross_platform_search_uv"],
            s1["ecommerce_search_lift_effect"]["total_cross_platform_search_uv"],
        )
        self.assertEqual(len(s2["geo_effect"]["ai_engines_breakdown"]), 8)
        md = generate_bilingual_markdown_report(s2)
        self.assertIn("via54SocialROI", md)

    def test_03_multi_account_matrix_portfolio(self) -> None:
        accounts = [
            self.crawler.fetch_account_profile("xhs_medical_skincare_kol"),
            self.crawler.fetch_account_profile("douyin_health_otc_kol"),
            self.crawler.fetch_account_profile("bili_hardcore_tech_review"),
            self.crawler.fetch_account_profile("channels_family_wellness_kol"),
        ]
        prod = ProductInput(
            product_name="科复佳医用透明质酸钠修复贴 (Demo)",
            brand_name="科复佳",
            category="医疗器械/医用敷料",
            selling_price_rmb=118.0,
            campaign_budget_rmb=18500.0,
        )
        s2_in = Stage2ContentInput(topics_hashtags=["#医用敷料"], campaign_theme="Demo", script_content="Demo")
        matrix = self.engine.compute_multi_account_matrix(accounts, prod, s2_in, matrix_total_budget_rmb=95000.0)
        self.assertTrue(matrix["success"])
        self.assertEqual(matrix["portfolio_summary"]["account_count"], 4)
        self.assertEqual(matrix["portfolio_summary"]["platform_count"], 4)
        self.assertGreater(matrix["portfolio_summary"]["cross_platform_synergy_multiplier"], 1.1)

    def test_04_mcp_server_tools_protocol(self) -> None:
        self.assertEqual(len(MCP_TOOLS), 4)
        presets = handle_tool_call("social_roi_list_presets", {})
        self.assertIn("presets", presets)

        single = handle_tool_call(
            "social_roi_evaluate_single",
            {"product_name": "科复佳医用透明质酸钠修复贴", "selling_price_rmb": 118.0},
        )
        self.assertGreater(single["expected_views"], 0)
        self.assertGreater(single["omni_gmv_rmb"], 0)

        mat = handle_tool_call(
            "social_roi_evaluate_matrix",
            {"product_name": "科复佳医用透明质酸钠修复贴", "matrix_total_budget_rmb": 95000.0},
        )
        self.assertEqual(mat["portfolio_summary"]["account_count"], 4)

    def test_05_cli_execution_in_forced_open_core_demo_mode(self) -> None:
        env = dict(os.environ)
        env["VIA54_FORCE_DEMO_MODE"] = "1"
        proc = subprocess.run(
            [sys.executable, str(REPO_ROOT / "cli.py"), "--info"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=env,
            check=True,
        )
        self.assertIn("OPEN_CORE_DEMO", proc.stdout)
        self.assertIn("腾讯 Marvis", proc.stdout)

    def test_06_skill_and_plugin_morphology_and_no_proprietary_leak(self) -> None:
        import json

        # 1. Verify zero proprietary core files exist in public Trial repo
        forbidden = [
            "private_core",
            "models_core.py",
            "marvis_crawler.py",
            "multimodal_ingest.py",
            "agent_hub.py",
            "hourly_monitor.py",
            "report_generator.py",
        ]
        for fname in forbidden:
            self.assertFalse(
                (REPO_ROOT / fname).exists(),
                f"Proprietary file/folder '{fname}' must not exist in public Trial repository",
            )

        # 2. Verify Skill & Plugin manifests exist and parse cleanly
        self.assertTrue((REPO_ROOT / "via54socialroi" / "SKILL.md").exists())
        self.assertTrue((REPO_ROOT / "plugin" / "index.js").exists())
        self.assertTrue((REPO_ROOT / "plugin" / "index.d.ts").exists())

        pkg = json.loads((REPO_ROOT / "package.json").read_text(encoding="utf-8"))
        self.assertEqual(pkg["name"], "@via54/plugin-social-roi")

        plugin_meta = json.loads((REPO_ROOT / "plugin.json").read_text(encoding="utf-8"))
        self.assertIn("mcpServers", plugin_meta)


if __name__ == "__main__":
    unittest.main(verbosity=2)
