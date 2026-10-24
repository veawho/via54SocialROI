#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
via54SocialROI — Command Line Interface (CLI) for Developers & AI Agents
全平台社媒推广影响力、电商回搜、GEO与ROI测算系统 — 命令行工具 (支持单号测算 / 多账号矩阵PK / 脚本生成)

Usage Examples / 调用示例:
  python cli.py --info
  python cli.py --preset xhs_kefujia_medical
  python cli.py --matrix --budget 95000
  python cli.py --account xhs_medical_skincare_kol --product "科复佳医用修复贴" --price 118 --budget 18500
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict

from core import (
    EDITION,
    HAS_PRIVATE_CORE,
    MarvisSocialCrawler,
    OmniSocialPromotionEngine,
    ProductInput,
    Stage2ContentInput,
    generate_smart_stage2_from_product,
)
from server import PRESET_SCENARIOS, build_product_from_dict, build_stage2_from_dict


def run_cli() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    parser = argparse.ArgumentParser(
        prog="via54SocialROI",
        description="Omni-Channel Social Media ROI, E-Commerce Search Spillover & 8-LLM GEO Calculator CLI",
    )
    parser.add_argument("--info", action="store_true", help="Show active engine edition (PRO_PRIVATE_CORE vs OPEN_CORE_DEMO)")
    parser.add_argument("--preset", type=str, default="", help="Run a built-in preset scenario (e.g., xhs_kefujia_medical)")
    parser.add_argument("--matrix", action="store_true", help="Run cross-platform multi-account matrix portfolio analysis")
    parser.add_argument("--account", type=str, default="xhs_medical_skincare_kol", help="Account URL or preset key")
    parser.add_argument("--product", type=str, default="科复佳医用透明质酸钠修复贴", help="Product name")
    parser.add_argument("--brand", type=str, default="科复佳", help="Brand name")
    parser.add_argument("--category", type=str, default="医疗器械/医用敷料/敏肌修护", help="Product category")
    parser.add_argument("--price", type=float, default=118.0, help="Selling price (RMB)")
    parser.add_argument("--budget", type=float, default=18500.0, help="Campaign budget (RMB)")
    parser.add_argument("--json", action="store_true", help="Output raw JSON payload")
    args = parser.parse_args()

    crawler = MarvisSocialCrawler()
    engine = OmniSocialPromotionEngine()

    if args.info:
        info = {
            "project": "via54SocialROI",
            "edition": EDITION,
            "has_private_core": HAS_PRIVATE_CORE,
            "recommended_social_monitoring_client": "Tencent Marvis (腾讯 Marvis — 当前测试最好的社交媒体监测 Agent 客户端 / Currently the Best-Tested Social Media Monitoring Agent Client)",
            "available_presets": list(PRESET_SCENARIOS.keys()),
        }
        print(json.dumps(info, ensure_ascii=False, indent=2))
        return 0

    if args.matrix:
        scenario = PRESET_SCENARIOS["xhs_kefujia_medical"]
        product = build_product_from_dict(scenario["product"])
        stage2 = build_stage2_from_dict(scenario["stage2"])
        accounts = [
            crawler.fetch_account_profile("xhs_medical_skincare_kol", use_marvis_live=False),
            crawler.fetch_account_profile("douyin_health_otc_kol", use_marvis_live=False),
            crawler.fetch_account_profile("bili_hardcore_tech_review", use_marvis_live=False),
            crawler.fetch_account_profile("channels_family_wellness_kol", use_marvis_live=False),
        ]
        total_b = args.budget if args.budget != 18500.0 else 95000.0
        res = engine.compute_multi_account_matrix(
            accounts=accounts,
            product=product,
            stage2_input=stage2,
            matrix_total_budget_rmb=total_b,
        )
        if args.json:
            print(json.dumps(res, ensure_ascii=False, indent=2))
        else:
            ps = res["portfolio_summary"]
            opt = res["budget_optimization"]
            top = res["account_ranking"][0]
            print(f"=== [via54SocialROI | {EDITION}] 多账号矩阵检测看板 / Multi-Account Matrix ===")
            print(f"检测账号数: {ps['account_count']} (覆盖 {ps['platform_count']} 大平台) | 跨平台协同乘数: {ps['cross_platform_synergy_multiplier']}x")
            print(f"去重净触达: {ps['deduplicated_unique_reach_uv']:,} UV | 三大电商协同回搜: {ps['synergized_total_search_uv']:,} UV")
            print(f"矩阵全域总GMV: ¥{ps['synergized_omni_gmv_rmb']:,.2f} (综合ROAS: {ps['portfolio_blended_roas']}x)")
            print(f"综合性价比第1名: [{top['platform_cn']}] {top['account_name']} (效能分 {top['efficiency_score_100']} | ROAS {top['omni_roas']}x)")
            print(f"AI预算寻优增益: 较平均分配提升 +{opt['gmv_lift_vs_equal_split_pct']}% GMV")
        return 0

    if args.preset and args.preset in PRESET_SCENARIOS:
        scen = PRESET_SCENARIOS[args.preset]
        prof = crawler.fetch_account_profile(scen["account_key"], use_marvis_live=False)
        product = build_product_from_dict(scen["product"])
        stage2 = build_stage2_from_dict(scen["stage2"])
    else:
        prof = crawler.fetch_account_profile(args.account, use_marvis_live=False)
        product = ProductInput(
            product_name=args.product,
            brand_name=args.brand,
            category=args.category,
            selling_price_rmb=args.price,
            msrp_rmb=round(args.price * 1.25, 2),
            campaign_budget_rmb=args.budget,
            core_selling_points=["权威资质认证与临床验证", "高纯度核心成分协同起效", "多渠道正品保障与高复购口碑"],
        )
        gen = generate_smart_stage2_from_product(prof, product)
        stage2 = Stage2ContentInput(
            topics_hashtags=gen["topics"],
            campaign_theme=gen["campaign_theme"],
            script_content=gen["script_content"],
        )

    shelf = crawler.probe_ecommerce_shelves(product.product_name, product.category)
    res2 = engine.compute_stage2_enhanced(prof, product, stage2, shelf_probe=shelf)

    if args.json:
        print(json.dumps(res2, ensure_ascii=False, indent=2))
    else:
        inf2 = res2["enhanced_influence_effect"]
        ecom2 = res2["enhanced_ecommerce_search_lift_effect"]
        geo2 = res2["geo_effect"]["share_of_model_summary"]
        roi2 = res2["roi_and_unit_economics"]
        attr2 = roi2["omni_channel_gmv_attribution"]
        prof2 = roi2["roi_and_profitability"]
        print(f"=== [via54SocialROI | {EDITION}] 单账号投前决策摘要 / Single-Account Verdict ===")
        print(f"博主账号: [{prof.platform_cn}] {prof.account_name} (粉丝: {prof.followers:,})")
        print(f"推广产品: {product.product_name} (成交价: ¥{product.selling_price_rmb} | 预算: ¥{product.campaign_budget_rmb:,.0f})")
        print(f"预计曝光: {inf2['expected_views']:,} (+{inf2['views_lift_vs_stage1_pct']}% vs S1) | 总互动: {inf2['total_interactions']:,}")
        print(f"电商回搜: {ecom2['total_cross_platform_search_uv']:,} UV (进店 {ecom2['total_store_visit_uv']:,} UV)")
        print(f"GEO 声量: 8大AI引擎平均 SoM {geo2['avg_post_campaign_som_pct']}% (+{geo2['avg_som_lift_pts']} pts)")
        print(f"全域GMV : ¥{attr2['omni_total_gmv_rmb']:,.2f} ({attr2['omni_total_orders']} 单) | 全域ROAS: {prof2['omni_channel_roas']}x | 净利: ¥{prof2['net_profit_after_ad_spend_rmb']:,.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(run_cli())
