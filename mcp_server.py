#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
via54SocialROI — Standard Model Context Protocol (MCP) Server (Zero-Dependency JSON-RPC 2.0 over Stdio)
全平台社媒推广影响力、电商回搜、GEO与ROI测算系统 — 标准 MCP 服务端 (支持 Claude Code / Antigravity / Cursor / DeepSeek Harness)
"""

from __future__ import annotations

import json
import sys
from typing import Any, Dict

from core import (
    EDITION,
    MarvisSocialCrawler,
    OmniSocialPromotionEngine,
    ProductInput,
    Stage2ContentInput,
    generate_smart_stage2_from_product,
)
from server import PRESET_SCENARIOS, build_product_from_dict, build_stage2_from_dict

CRAWLER = MarvisSocialCrawler()
ENGINE = OmniSocialPromotionEngine()

MCP_TOOLS = [
    {
        "name": "social_roi_evaluate_single",
        "description": (
            "Evaluate a social media account (Xiaohongshu/Douyin/Bilibili/WeChat Channels) promoting a product. "
            "Computes Stage 1 baseline & Stage 2 enhanced influence, 30-day search index lift, "
            "cross-platform e-commerce search spillover (JD/Tmall/Meituan), 8-LLM GEO Share of Model (SoM), and Omni-Channel ROI."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "account_url_or_key": {
                    "type": "string",
                    "description": "Social media profile URL or preset key (e.g., xhs_medical_skincare_kol)",
                },
                "product_name": {"type": "string", "description": "Product name to promote"},
                "selling_price_rmb": {"type": "number", "description": "Product invoice selling price in RMB"},
                "campaign_budget_rmb": {"type": "number", "description": "KOL campaign quote / ad spend in RMB"},
            },
            "required": ["product_name", "selling_price_rmb"],
        },
    },
    {
        "name": "social_roi_evaluate_matrix",
        "description": (
            "Run Multi-Account Detection & Matrix Portfolio Analysis across multiple KOL/KOC accounts. "
            "Computes Modified Sainsbury deduplicated reach, cross-platform synergy multiplier, "
            "side-by-side efficiency ranking, and Hill-saturation optimal budget allocation."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "account_keys": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of account URLs or preset keys",
                },
                "product_name": {"type": "string", "description": "Product name"},
                "selling_price_rmb": {"type": "number", "description": "Selling price in RMB"},
                "matrix_total_budget_rmb": {"type": "number", "description": "Total campaign budget in RMB"},
            },
            "required": ["product_name"],
        },
    },
    {
        "name": "social_roi_generate_script",
        "description": "Generate 5 vertical hashtags, campaign theme, and a 4-section high-GEO promotion script for a KOL + Product pair.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "account_name": {"type": "string"},
                "product_name": {"type": "string"},
                "brand_name": {"type": "string"},
                "core_selling_points": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["product_name"],
        },
    },
    {
        "name": "social_roi_list_presets",
        "description": "List built-in cross-platform benchmark scenarios and active engine edition (PRO_PRIVATE_CORE vs OPEN_CORE_DEMO).",
        "inputSchema": {"type": "object", "properties": {}},
    },
]


def handle_tool_call(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    if name == "social_roi_list_presets":
        return {
            "edition": EDITION,
            "presets": list(PRESET_SCENARIOS.keys()),
        }

    if name == "social_roi_generate_script":
        return generate_smart_stage2_from_product(
            account={"account_name": arguments.get("account_name", "示范达人"), "platform": "xiaohongshu"},
            product={
                "product_name": arguments.get("product_name", "示范产品"),
                "brand_name": arguments.get("brand_name", "示范品牌"),
                "core_selling_points": arguments.get("core_selling_points") or ["权威标准认证", "高纯度核心成分", "多渠道正品保障"],
            },
        )

    if name == "social_roi_evaluate_single":
        acct_key = arguments.get("account_url_or_key") or "xhs_medical_skincare_kol"
        prof = CRAWLER.fetch_account_profile(acct_key, use_marvis_live=False)
        price = float(arguments.get("selling_price_rmb") or 118.0)
        budget = float(arguments.get("campaign_budget_rmb") or prof.commercial_quote_rmb or 18500.0)
        prod = ProductInput(
            product_name=str(arguments.get("product_name") or "科复佳医用透明质酸钠修复贴"),
            brand_name=str(arguments.get("brand_name") or "示范品牌"),
            category=str(arguments.get("category") or "医疗健康/品质消费"),
            selling_price_rmb=price,
            msrp_rmb=round(price * 1.25, 2),
            campaign_budget_rmb=budget,
            core_selling_points=["权威临床或行业标准背书", "核心成分协同修护", "京东/淘天/美团多渠道覆盖"],
        )
        gen = generate_smart_stage2_from_product(prof, prod)
        s2 = Stage2ContentInput(
            topics_hashtags=gen["topics"],
            campaign_theme=gen["campaign_theme"],
            script_content=gen["script_content"],
        )
        shelf = CRAWLER.probe_ecommerce_shelves(prod.product_name, prod.category)
        res = ENGINE.compute_stage2_enhanced(prof, prod, s2, shelf_probe=shelf)
        return {
            "edition": EDITION,
            "account": prof.account_name,
            "platform": prof.platform_cn,
            "expected_views": res["enhanced_influence_effect"]["expected_views"],
            "ecommerce_search_uv": res["enhanced_ecommerce_search_lift_effect"]["total_cross_platform_search_uv"],
            "avg_geo_som_pct": res["geo_effect"]["share_of_model_summary"]["avg_post_campaign_som_pct"],
            "omni_gmv_rmb": res["roi_and_unit_economics"]["omni_channel_gmv_attribution"]["omni_total_gmv_rmb"],
            "omni_roas": res["roi_and_unit_economics"]["roi_and_profitability"]["omni_channel_roas"],
            "net_profit_rmb": res["roi_and_unit_economics"]["roi_and_profitability"]["net_profit_after_ad_spend_rmb"],
        }

    if name == "social_roi_evaluate_matrix":
        keys = arguments.get("account_keys") or [
            "xhs_medical_skincare_kol",
            "douyin_health_otc_kol",
            "bili_hardcore_tech_review",
            "channels_family_wellness_kol",
        ]
        profiles = [CRAWLER.fetch_account_profile(k, use_marvis_live=False) for k in keys]
        scen = PRESET_SCENARIOS["xhs_kefujia_medical"]
        prod = build_product_from_dict(scen["product"])
        if arguments.get("product_name"):
            prod.product_name = str(arguments["product_name"])
        if arguments.get("selling_price_rmb"):
            prod.selling_price_rmb = float(arguments["selling_price_rmb"])
        s2 = build_stage2_from_dict(scen["stage2"])
        budget = float(arguments.get("matrix_total_budget_rmb") or 95000.0)
        res = ENGINE.compute_multi_account_matrix(
            accounts=profiles,
            product=prod,
            stage2_input=s2,
            matrix_total_budget_rmb=budget,
        )
        return {
            "edition": EDITION,
            "portfolio_summary": res["portfolio_summary"],
            "top_ranked_account": res["account_ranking"][0] if res["account_ranking"] else None,
            "budget_optimization": res["budget_optimization"],
        }

    raise ValueError(f"Unknown tool: {name}")


def main() -> None:
    for line in sys.stdin:
        raw = line.strip()
        if not raw:
            continue
        try:
            req = json.loads(raw)
        except Exception:
            continue
        req_id = req.get("id")
        method = req.get("method", "")
        params = req.get("params") or {}

        if method == "initialize":
            resp = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "via54-social-roi-mcp", "version": "2.4.0"},
                },
            }
        elif method == "tools/list":
            resp = {"jsonrpc": "2.0", "id": req_id, "result": {"tools": MCP_TOOLS}}
        elif method == "tools/call":
            t_name = params.get("name", "")
            t_args = params.get("arguments") or {}
            try:
                out = handle_tool_call(t_name, t_args)
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {"content": [{"type": "text", "text": json.dumps(out, ensure_ascii=False, indent=2)}]},
                }
            except Exception as e:
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32000, "message": str(e)},
                }
        else:
            if req_id is None:
                continue
            resp = {"jsonrpc": "2.0", "id": req_id, "result": {}}

        sys.stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
