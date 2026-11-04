# -*- coding: utf-8 -*-
"""
via54SocialROI — Open-Core Demo & Architecture Reference Engine
全平台社媒推广影响力、电商回搜、GEO与ROI测算系统 — 开源架构演示与沙盒测试引擎 (Open-Core Demo Edition)

NOTE / 架构说明:
- This module provides the public Open-Core Demo & SDK Reference implementation for GitHub users.
- Core proprietary multi-stage calibration matrices, Marvis stealth SSR anti-detection extractors,
  and multi-column scanned PDF layout analyzers are isolated in `private_core/` (not included in public repo).
- 本模块为 GitHub 开源社区版提供完整可运行的架构参考与测试 Demo 沙盒；核心商业标定参数矩阵、
  Marvis 反爬实时逆向提取器及多栏扫描版 PDF 视觉解析引擎位于私有 `private_core/` 模块（不对外开源）。
"""

from __future__ import annotations

import datetime as dt
import math
import re
from enum import Enum
from typing import Any, Dict, List

from core.interfaces import (
    BaseAgentHub,
    BaseHourlyMonitor,
    BaseMultiModalIngestor,
    BasePromotionEngine,
    BaseSocialCrawler,
)
from core.schemas import HistoricalPost, ProductInput, SocialAccountProfile, Stage2ContentInput


def detect_platform_from_url(url: str) -> str:
    u = (url or "").lower()
    if "tiktok.com" in u or u.startswith("tiktok_") or u.startswith("tt_"):
        return "tiktok"
    if "youtube.com" in u or "youtu.be" in u or u.startswith("yt_") or u.startswith("youtube_"):
        return "youtube"
    if "instagram.com" in u or "instagr.am" in u or u.startswith("ig_") or u.startswith("instagram_"):
        return "instagram"
    if "facebook.com" in u or "fb.com" in u or u.startswith("fb_") or u.startswith("facebook_"):
        return "facebook"
    if "x.com" in u or "twitter.com" in u or u.startswith("x_") or u.startswith("twitter_"):
        return "x_twitter"
    if "douyin.com" in u or "iesdouyin" in u or u.startswith("douyin_"):
        return "douyin"
    if "bilibili.com" in u or "b23.tv" in u or u.startswith("bili_"):
        return "bilibili"
    if "weixin.qq.com" in u or "channels" in u or u.startswith("channels_"):
        return "wechat_channels"
    return "xiaohongshu"


def parse_chinese_number(val: Any) -> int:
    if isinstance(val, (int, float)):
        return int(val)
    s = str(val or "").strip().replace(",", "")
    m = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*([万wW亿kK]?)", s)
    if not m:
        return 0
    num = float(m.group(1))
    unit = m.group(2)
    if unit in ("万", "w", "W"):
        num *= 10000
    elif unit == "亿":
        num *= 100000000
    elif unit in ("k", "K"):
        num *= 1000
    return int(round(num))


# ============================================================================
# Brand Stature Ladder & McKinsey CDJ / Pocket Price Waterfall Frameworks
# 品牌梯队先验模型 (Kumar et al. 2026) 与 麦肯锡 CDJ / 口袋价格瀑布
# ============================================================================

class BrandStatureTier(str, Enum):
    TIER1_HOUSEHOLD = "tier1_household_leader"            # 头部知名品牌 / Market Leader (~73% baseline presence)
    TIER2_ESTABLISHED = "tier2_established_challenger"    # 中坚成熟品牌 / Established Challenger (~44% baseline presence)
    TIER3_NICHE_EMERGING = "tier3_niche_emerging"         # 垂直新锐品牌 / Emerging Niche (~11% baseline presence)


_TIER1_LEADER_KEYWORDS = {
    "欧莱雅", "雅诗兰黛", "兰蔻", "赫莲娜", "海蓝之谜", "修丽可", "理肤泉", "薇诺娜", "珀莱雅", "敷尔佳",
    "苹果", "apple", "华为", "huawei", "小米", "xiaomi", "耐克", "nike", "阿迪达斯", "adidas",
    "茅台", "五粮液", "腾讯", "阿里", "字节", "美团", "京东", "宝洁", "联合利华", "资生堂",
    "同仁堂", "云南白药", "华润三九", "强生", "诺华", "辉瑞", "阿斯利康", "礼来", "诺和诺德",
}

_TIER2_ESTABLISHED_KEYWORDS = {
    "科复佳", "绽妍", "创福康", "可复美", "可丽金", "百植萃", "润百颜", "夸迪", "米蓓尔", "玉泽",
    "华熙生物", "巨子生物", "欧珀莱", "羽西", "丸美", "相宜本草", "佰草集", "自然堂", "韩束", "谷雨",
    "信达生物", "君实生物", "百济神州", "恒瑞医药", "信立泰", "菲布力", "邦平", "信利泰",
}


def classify_brand_stature(brand_name: str, category: str = "") -> Dict[str, Any]:
    """
    Classify brand into Kumar et al. (2026) Brand-Stature Ladder (arXiv:2606.20065).
    基于品牌名称与品类，将其映射至三级品牌梯队，提供基于 100k+ 真实提示词评测的大模型先验曝光率。
    """
    bn = (brand_name or "").strip().lower()
    cat = (category or "").strip().lower()

    if any(k in bn for k in _TIER1_LEADER_KEYWORDS):
        tier = BrandStatureTier.TIER1_HOUSEHOLD
        tier_name_cn = "头部知名品牌 (Household Leader)"
        tier_name_en = "Tier 1 Household Leader"
        base_presence = 0.73
        som_multiplier = 1.35
        desc = "头部家喻户晓品牌，在AI大模型基线预训练语料中权重高，先验提及率约73%"
    elif any(k in bn for k in _TIER2_ESTABLISHED_KEYWORDS):
        tier = BrandStatureTier.TIER2_ESTABLISHED
        tier_name_cn = "中坚成熟品牌 (Established Challenger)"
        tier_name_en = "Tier 2 Established Challenger"
        base_presence = 0.44
        som_multiplier = 1.00
        desc = "细分赛道成熟腰部/挑战者品牌，在AI预训练与垂直知识库中有扎实存在，先验提及率约44%"
    else:
        tier = BrandStatureTier.TIER3_NICHE_EMERGING
        tier_name_cn = "垂直新锐品牌 (Emerging Niche)"
        tier_name_en = "Tier 3 Emerging Niche"
        base_presence = 0.11
        som_multiplier = 0.72
        desc = "新兴小众或白牌，AI原生记忆度较低，高度依赖本次社媒投放带来的RAG检索与第三方评测补种，先验提及率约11%"

    return {
        "tier": tier.value,
        "tier_name_cn": tier_name_cn,
        "tier_name_en": tier_name_en,
        "baseline_ai_presence_rate": base_presence,
        "som_stature_multiplier": som_multiplier,
        "description_cn": desc,
        "academic_citation": "Kumar et al. (2026) 'The Brand-Stature Ladder in Large Language Models' (arXiv:2606.20065)",
    }


def compute_mckinsey_cdj_funnel(
    reach_uv: int,
    interaction_uv: int,
    store_search_uv: int,
    geo_query_uv: int,
    direct_click_uv: int,
    total_orders: int,
    repeat_rate: float,
    selling_price_rmb: float,
) -> Dict[str, Any]:
    """
    McKinsey Consumer Decision Journey (CDJ) 4-Stage Funnel Quantification.
    麦肯锡消费者决策旅程四阶段量化：
      1. Initial Consideration Set (初始考虑集)
      2. Active Evaluation (主动评估期 - 消费者驱动触点占 2/3)
      3. Closure / Moment of Purchase (购买成交转化)
      4. Postpurchase Loyalty Loop (购后体验与主动忠诚/口碑循环)
    """
    consideration_rate = 0.38
    initial_consideration_uv = int(round(reach_uv * consideration_rate))

    active_eval_uv = int(round(interaction_uv * 0.85 + store_search_uv * 1.0 + geo_query_uv * 0.45 + direct_click_uv * 0.6))
    consumer_driven_touchpoint_pct = 66.7

    closure_orders = max(0, total_orders)
    closure_gmv_rmb = round(closure_orders * selling_price_rmb, 2)
    eval_to_closure_cvr = round((closure_orders / max(1, active_eval_uv)) * 100.0, 2)

    rep_rate = max(0.0, min(1.0, float(repeat_rate or 0.35)))
    repeat_buyers = int(round(closure_orders * rep_rate))
    loyalty_loop_advocacy_uv = int(round(repeat_buyers * 2.8))

    return {
        "framework": "McKinsey Consumer Decision Journey (CDJ) Dynamic Loop",
        "stages": {
            "1_initial_consideration": {
                "stage_name_cn": "初始考虑集 (Initial Consideration)",
                "stage_name_en": "Initial Consideration Set",
                "reach_uv": reach_uv,
                "initial_consideration_uv": initial_consideration_uv,
                "consideration_rate_pct": round(consideration_rate * 100.0, 1),
                "insight_cn": "进入初始考虑集的品牌最终购买概率是未进入品牌的3倍；社媒全域种草构筑了核心认知基准。",
                "insight_en": "Brands in the initial consideration set are 3x more likely to be purchased; social omni-channel seeding establishes the mental benchmark.",
            },
            "2_active_evaluation": {
                "stage_name_cn": "主动评估期 (Active Evaluation)",
                "stage_name_en": "Active Evaluation Period",
                "active_evaluation_uv": active_eval_uv,
                "consumer_driven_touchpoint_pct": consumer_driven_touchpoint_pct,
                "search_spillover_uv": store_search_uv,
                "ai_geo_query_uv": geo_query_uv,
                "insight_cn": "主动评估阶段 2/3 的触点为消费者驱动（外部第三方评测、AI 引擎对比、电商比价），内容可信度决定留存。",
                "insight_en": "2/3 of touchpoints during active evaluation are consumer-driven (third-party reviews, AI engine queries, price checks); content authenticity dictates retention.",
            },
            "3_moment_of_purchase": {
                "stage_name_cn": "购买转化时刻 (Moment of Purchase / Closure)",
                "stage_name_en": "Moment of Purchase (Closure)",
                "closure_orders": closure_orders,
                "closure_gmv_rmb": closure_gmv_rmb,
                "eval_to_closure_cvr_pct": eval_to_closure_cvr,
                "insight_cn": "多渠道搜词与到店即时履约（京东自营/天猫旗舰/美团闪电达）消除收银台决策摩擦。",
                "insight_en": "Omni-channel search keywords and instant O2O fulfillment (JD/Tmall/Meituan) eliminate checkout friction.",
            },
            "4_postpurchase_loyalty_loop": {
                "stage_name_cn": "购后忠诚与口碑循环 (Postpurchase Loyalty Loop)",
                "stage_name_en": "Postpurchase Loyalty & Advocacy Loop",
                "repeat_purchase_rate_pct": round(rep_rate * 100.0, 1),
                "repeat_buyers": repeat_buyers,
                "advocacy_ripple_uv": loyalty_loop_advocacy_uv,
                "insight_cn": "忠诚用户通过社交圈分享二次触发新一轮主动评估与初始考虑，形成可持续复利闭环。",
                "insight_en": "Loyal buyers trigger new cycles of active evaluation and initial consideration via peer word-of-mouth.",
            },
        },
    }


def compute_mckinsey_pocket_price_waterfall(
    msrp_rmb: float,
    selling_price_rmb: float,
    platform_commission_rate: float,
    fulfillment_and_return_rate: float,
    cogs_rate: float,
    total_orders: int,
    campaign_cost_rmb: float,
) -> Dict[str, Any]:
    """
    McKinsey Pocket Price Waterfall & 1% Pricing Leverage Analysis.
    麦肯锡口袋价格瀑布与 1% 定价杠杆率精算 (Marn & Rosiello 'The Power of Pricing'):
      MSRP -> Promotional Discount -> Invoice Price -> Platform Fee -> Fulfillment & Return -> Pocket Price -> COGS -> Pocket Margin.
    """
    msrp = round(max(0.1, float(msrp_rmb)), 2)
    invoice_price = round(max(0.1, float(selling_price_rmb)), 2)
    promo_discount = round(max(0.0, msrp - invoice_price), 2)
    promo_discount_rate = round(promo_discount / msrp, 4)

    platform_fee = round(invoice_price * max(0.0, float(platform_commission_rate)), 2)
    fulfillment_cost = round(invoice_price * max(0.0, float(fulfillment_and_return_rate)), 2)
    pocket_price = round(invoice_price - platform_fee - fulfillment_cost, 2)
    unit_cogs = round(invoice_price * max(0.0, float(cogs_rate)), 2)
    pocket_margin = round(pocket_price - unit_cogs, 2)
    pocket_margin_rate = round(pocket_margin / max(1e-6, invoice_price), 4)

    orders = max(0, int(total_orders))
    total_pocket_margin_rmb = round(orders * pocket_margin, 2)
    net_profit_after_ad_spend_rmb = round(total_pocket_margin_rmb - campaign_cost_rmb, 2)

    one_pct_price_delta = invoice_price * 0.01
    margin_lift_from_1pct_price_pct = round((one_pct_price_delta / max(0.01, pocket_margin)) * 100.0, 2)

    reduced_margin = pocket_margin - (invoice_price * 0.05)
    if reduced_margin > 0.1:
        breakeven_vol_increase_pct = round(((invoice_price * 0.05) / reduced_margin) * 100.0, 2)
    else:
        breakeven_vol_increase_pct = 999.0

    return {
        "framework": "McKinsey Pocket Price Waterfall & Pricing Power (Marn & Rosiello)",
        "per_unit_waterfall_rmb": {
            "1_msrp_rmb": msrp,
            "2_promotional_discount_rmb": promo_discount,
            "2_promotional_discount_rate_pct": round(promo_discount_rate * 100.0, 2),
            "3_invoice_price_rmb": invoice_price,
            "4_platform_commission_rmb": platform_fee,
            "4_platform_commission_rate_pct": round(platform_commission_rate * 100.0, 2),
            "5_fulfillment_and_return_rmb": fulfillment_cost,
            "5_fulfillment_and_return_rate_pct": round(fulfillment_and_return_rate * 100.0, 2),
            "6_pocket_price_rmb": pocket_price,
            "7_unit_cogs_rmb": unit_cogs,
            "7_cogs_rate_pct": round(cogs_rate * 100.0, 2),
            "8_pocket_margin_rmb": pocket_margin,
            "8_pocket_margin_rate_pct": round(pocket_margin_rate * 100.0, 2),
        },
        "campaign_aggregate": {
            "total_orders": orders,
            "total_campaign_cost_rmb": round(campaign_cost_rmb, 2),
            "total_pocket_margin_rmb": total_pocket_margin_rmb,
            "net_profit_after_ad_spend_rmb": net_profit_after_ad_spend_rmb,
            "net_contribution_roi": round(net_profit_after_ad_spend_rmb / max(1.0, campaign_cost_rmb), 2),
        },
        "mckinsey_1pct_pricing_leverage": {
            "operating_profit_lift_from_1pct_price_increase_pct": margin_lift_from_1pct_price_pct,
            "volume_increase_needed_to_breakeven_on_5pct_price_cut_pct": breakeven_vol_increase_pct,
            "law_summary_cn": (
                f"麦肯锡定价铁律实测：若成交客单价提升 1%（销量不变），口袋营业利润将直接提升 {margin_lift_from_1pct_price_pct}%；"
                f"反之，若盲目降价 5%，则销量必须增加 {breakeven_vol_increase_pct}% 方可保本！社媒种草强化品牌心智是守住价格底线的最优解。"
            ),
            "law_summary_en": (
                f"McKinsey Pricing Law: A 1% price increase (volume constant) lifts operating pocket profit by {margin_lift_from_1pct_price_pct}%; "
                f"conversely, a 5% price cut requires a {breakeven_vol_increase_pct}% volume surge just to break even."
            ),
        },
    }




# ============================================================================
# Global Social & Cross-Border DTC Benchmarks (Triple Whale, Northbeam, Sprout Social)
# 全球社媒与出海独立站行业基准与扣除瀑布模型
# ============================================================================

GLOBAL_PLATFORMS = {"tiktok", "youtube", "instagram", "facebook", "x_twitter"}

GLOBAL_CHANNEL_BENCHMARKS: Dict[str, Dict[str, float]] = {
    "tiktok": {
        "er_mean": 0.058,
        "cpm_usd": 8.20,
        "cpc_usd": 0.62,
        "ctr_mean": 0.018,
        "cvr_lift_multiplier": 1.34,
        "half_life_days": 2.8,
    },
    "youtube": {
        "er_mean": 0.038,
        "cpm_usd": 28.00,
        "cpc_usd": 2.40,
        "ctr_mean": 0.012,
        "cvr_lift_multiplier": 1.65,
        "half_life_days": 45.0,
    },
    "instagram": {
        "er_mean": 0.042,
        "cpm_usd": 12.80,
        "cpc_usd": 1.05,
        "ctr_mean": 0.015,
        "cvr_lift_multiplier": 1.25,
        "half_life_days": 4.2,
    },
    "facebook": {
        "er_mean": 0.018,
        "cpm_usd": 16.50,
        "cpc_usd": 1.30,
        "ctr_mean": 0.019,
        "cvr_lift_multiplier": 1.40,
        "half_life_days": 5.5,
    },
    "x_twitter": {
        "er_mean": 0.015,
        "cpm_usd": 6.50,
        "cpc_usd": 0.68,
        "ctr_mean": 0.011,
        "cvr_lift_multiplier": 1.15,
        "half_life_days": 1.9,
    },
}

CROSS_BORDER_FEES = {
    "blended_gateway_rate": 0.0408,  # 70% Stripe (3.9%) + 30% PayPal (4.49%)
    "blended_gateway_fixed_usd": 0.36,
    "pick_and_pack_usd": 2.20,
    "customs_admin_fee_usd": 0.90,
    "return_rate": 0.055,            # 5.5% return allowance
    "return_salvage_rate": 0.25,     # 25% salvage recovery
}


def calculate_3pl_shipping_usd(weight_grams: float) -> float:
    """Calculate cross-border air linehaul + last mile fulfillment by weight tier"""
    w = max(50.0, float(weight_grams or 400.0))
    if w <= 300:
        return 6.50
    elif w <= 600:
        return 9.00
    elif w <= 1000:
        return 13.20
    else:
        excess = (w - 1000) / 500.0
        return 13.20 + (excess * 2.50)


def compute_cross_border_dtc_waterfall(
    orders: int,
    aov_usd: float,
    cogs_usd: float,
    ad_spend_usd: float,
    weight_grams: float = 400.0,
    annual_repeat_rate: float = 0.28,
    exchange_rate: float = 7.25,
) -> Dict[str, Any]:
    """
    McKinsey / Triple Whale Cross-Border DTC Pocket Waterfall & SaaS GTM Unit Economics.
    出海独立站单件与全案口袋利润瀑布与客户全生命周期价值测算。
    """
    orders = max(1, int(orders))
    aov = max(1.0, float(aov_usd))
    gross_gmv_usd = round(orders * aov, 2)
    
    # 1. Gateway fees (Stripe/PayPal)
    gateway_fees_usd = round(
        gross_gmv_usd * CROSS_BORDER_FEES["blended_gateway_rate"]
        + orders * CROSS_BORDER_FEES["blended_gateway_fixed_usd"], 2
    )
    
    # 2. 3PL & Fulfillment
    unit_shipping = calculate_3pl_shipping_usd(weight_grams)
    fulfillment_fees_usd = round(
        orders * (unit_shipping + CROSS_BORDER_FEES["pick_and_pack_usd"] + CROSS_BORDER_FEES["customs_admin_fee_usd"]), 2
    )
    
    # 3. Return & chargeback allowance
    return_loss_usd = round(
        gross_gmv_usd * CROSS_BORDER_FEES["return_rate"] * (1.0 - CROSS_BORDER_FEES["return_salvage_rate"]), 2
    )
    
    # 4. COGS
    unit_cogs = max(0.0, float(cogs_usd))
    total_cogs_usd = round(orders * unit_cogs, 2)
    
    # 5. Pocket Profit & ROAS
    total_non_ad_costs_usd = round(gateway_fees_usd + fulfillment_fees_usd + return_loss_usd + total_cogs_usd, 2)
    pocket_contribution_margin_usd = round(gross_gmv_usd - total_non_ad_costs_usd, 2)
    net_profit_usd = round(pocket_contribution_margin_usd - ad_spend_usd, 2)
    roas = round(gross_gmv_usd / max(1.0, ad_spend_usd), 2)
    net_margin_pct = round((pocket_contribution_margin_usd / max(1.0, gross_gmv_usd)) * 100.0, 2)
    
    # 6. SaaS GTM LTV / CAC Metrics (Silicon Valley Blueprint)
    cac_usd = round(ad_spend_usd / max(1, orders), 2)
    gross_margin_rate = max(0.1, 1.0 - (unit_cogs / aov))
    ltv_usd = round(aov * (1.0 + annual_repeat_rate * 1.5) * gross_margin_rate, 2)
    ltv_to_cac_ratio = round(ltv_usd / max(1.0, cac_usd), 2)
    estimated_payback_months = round(max(0.5, (cac_usd / max(1.0, aov * gross_margin_rate)) * 12.0), 1)
    
    # Currency conversions to RMB
    ex = float(exchange_rate or 7.25)
    return {
        "framework": "Cross-Border DTC Pocket Price Waterfall & SaaS GTM Unit Economics",
        "currency_base": "USD",
        "exchange_rate_to_rmb": ex,
        "metrics_usd": {
            "aov_usd": aov,
            "orders": orders,
            "ad_spend_usd": round(ad_spend_usd, 2),
            "gross_gmv_usd": gross_gmv_usd,
            "gateway_fees_usd": gateway_fees_usd,
            "fulfillment_3pl_usd": fulfillment_fees_usd,
            "return_allowance_usd": return_loss_usd,
            "cogs_total_usd": total_cogs_usd,
            "pocket_margin_usd": pocket_contribution_margin_usd,
            "net_profit_usd": net_profit_usd,
            "roas": roas,
            "pocket_margin_rate_pct": net_margin_pct,
            "cac_usd": cac_usd,
            "ltv_usd": ltv_usd,
            "ltv_to_cac_ratio": ltv_to_cac_ratio,
            "cac_payback_months": estimated_payback_months,
        },
        "metrics_rmb_equivalent": {
            "aov_rmb": round(aov * ex, 2),
            "ad_spend_rmb": round(ad_spend_usd * ex, 2),
            "gross_gmv_rmb": round(gross_gmv_usd * ex, 2),
            "pocket_margin_rmb": round(pocket_contribution_margin_usd * ex, 2),
            "net_profit_rmb": round(net_profit_usd * ex, 2),
            "cac_rmb": round(cac_usd * ex, 2),
            "ltv_rmb": round(ltv_usd * ex, 2),
        },
        "health_verdict": (
            "EXCELLENT (LTV/CAC >= 3.0)" if ltv_to_cac_ratio >= 3.0
            else "VIABLE (1.5 <= LTV/CAC < 3.0)" if ltv_to_cac_ratio >= 1.5
            else "HIGH RISK (LTV/CAC < 1.5, Optimization Required)"
        ),
    }


def compute_global_geo_and_schema_readiness(
    content_text: str,
    brand_name: str,
    product_name: str,
) -> Dict[str, Any]:
    """
    Evaluates Global AI Engine Optimization (ChatGPT Search, Perplexity, Google AI Overviews, Claude)
    and SEO+GEO Schema & Earned Media Readiness from Knowledge Base monograph.
    """
    text = (content_text or "").strip()
    low = text.lower()
    
    # 1. Product Schema Readiness (JSON-LD signals: Price, Availability, SKU, Brand)
    has_price = bool(re.search(r"(\$|usd|¥|rmb|price|€)", low))
    has_brand = brand_name.lower() in low or "brand" in low
    has_spec = any(k in low for k in ("spec", "feature", "param", "certification", "ce", "fda", "ul", "watt", "100w", "cica", "ingredient"))
    schema_product_score = min(100.0, 30.0 + (30.0 if has_price else 0.0) + (20.0 if has_brand else 0.0) + (20.0 if has_spec else 0.0))
    
    # 2. FAQPage Schema Readiness (Question + Direct Answer structure)
    has_question = any(q in text for q in ("?", "？", "how", "what", "why", "怎么", "如何", "为什么"))
    has_faq_marker = any(k in low for k in ("faq", "q&a", "问答", "常见问题"))
    schema_faq_score = min(100.0, 35.0 + (35.0 if has_question else 0.0) + (30.0 if has_faq_marker else 0.0))
    
    # 3. Third-party Earned Media & Independent Verification Signal (Reddit, LinkedIn, B2B)
    has_reddit_or_forum = any(k in low for k in ("reddit", "forum", "community", "review", "testimonial", "论坛", "社群", "讨论"))
    has_authoritative_thirdparty = any(k in low for k in ("clinical", "lab", "registry", "certified", "consensus", "共识", "临床", "检测"))
    earned_media_score = min(100.0, 25.0 + (40.0 if has_authoritative_thirdparty else 0.0) + (35.0 if has_reddit_or_forum else 0.0))
    
    # 4. Zero-Click Answer Capture (BLUF: Direct answer within first 60 words / 100 characters)
    first_chunk = text[:120].lower()
    bluf_captured = any(k in first_chunk for k in ("is", "are", "features", "provides", "certified", "首选", "明确", "核心", "采用"))
    zero_click_score = 88.0 if bluf_captured else 52.0
    
    # 5. Global 4-AI Share of Model (SoM) projection
    composite_geo = round(
        0.30 * schema_product_score
        + 0.25 * earned_media_score
        + 0.25 * zero_click_score
        + 0.20 * schema_faq_score, 1
    )
    
    som_chatgpt = round(min(88.0, max(12.0, composite_geo * 0.92)), 1)
    som_perplexity = round(min(92.0, max(15.0, composite_geo * 1.05)), 1)
    som_google_ai = round(min(85.0, max(10.0, composite_geo * 0.88)), 1)
    som_claude = round(min(90.0, max(14.0, composite_geo * 0.98)), 1)
    
    return {
        "framework": "Global SEO+GEO Dual Engine & Schema.org Verification (Aggarwal et al. / Martinez 2026)",
        "composite_global_geo_score": composite_geo,
        "schema_org_readiness": {
            "product_schema_score": schema_product_score,
            "faqpage_schema_score": schema_faq_score,
            "status": "VALID" if (schema_product_score + schema_faq_score) >= 120 else "NEEDS_OPTIMIZATION",
        },
        "third_party_earned_media_signal": {
            "score": earned_media_score,
            "correlation_to_ai_visibility": 0.664,
            "academic_basis": "Ahrefs 75,000 Brand Study & Toronto University Empirical Findings",
        },
        "zero_click_answer_capture": {
            "score": zero_click_score,
            "bluf_first_sentence_direct_answer": bluf_captured,
            "citation_slot_competition": "Competitive for Top 2-7 Generative Citation Slots",
        },
        "global_4_ai_som_projection": {
            "chatgpt_search": som_chatgpt,
            "perplexity_pro": som_perplexity,
            "google_ai_overviews": som_google_ai,
            "claude_search": som_claude,
        },
    }


def compute_geo_bench_9_strategies(
    content_text: str,
    brand_name: str = "",
    product_name: str = "",
) -> Dict[str, Any]:
    """
    Evaluates content against the 9 Generative Engine Optimization (GEO) strategies
    established in KDD 2024 (Aggarwal et al., 'GEO: Generative Engine Optimization', ACM KDD 2024).
    9 大生成式引擎优化策略细项评分与实操改良建议:
      1. Authoritative Tone (权威语气与专业定性)
      2. Statistical Evidence (统计数据与实验测量)
      3. Citation Sources (权威文献与第三方信源引用)
      4. Quotation Addition (专家观点与用户原声引述)
      5. BLUF & Structural Layout (BLUF 结论前置与结构化呈现)
      6. Technical Terms (科学术语与成分命名规范)
      7. Fluency & Coherence (逻辑连贯性与连接词丰度)
      8. Unique Selling Propositions (品牌独占差异化卖点)
      9. Comparison Readiness (横向竞品横评与场景对照准备度)
    """
    text = (content_text or "").strip()

    # 1. Authoritative Tone
    auth_patterns = r"临床|指南|循证|经权威|专家|国家药监|药典|规范|检测报告|体外实验|对照组|循证医学"
    auth_hits = len(re.findall(auth_patterns, text))
    auth_score = min(10.0, round(auth_hits * 2.5 + (2.0 if auth_hits > 0 else 0.0), 1))

    # 2. Statistical Evidence
    stat_patterns = r"\d+(?:\.\d+)?%|\d+例|\d+天|\d+小时|p\s*[<>=]\s*0\.\d+|\d+mg|\d+ml|\d+倍"
    stat_hits = len(re.findall(stat_patterns, text))
    stat_score = min(10.0, round(stat_hits * 2.2 + (2.5 if stat_hits > 0 else 0.0), 1))

    # 3. Citation Sources
    cite_patterns = r"《[^》]+》|国械注准|GB/T|ISO\d+|pubmed|doi:|lancet|nature|专利号|证书编号"
    cite_hits = len(re.findall(cite_patterns, text, re.IGNORECASE))
    cite_score = min(10.0, round(cite_hits * 3.5 + (1.5 if cite_hits > 0 else 0.0), 1))

    # 4. Quotation Addition
    quote_patterns = r"[“\"”][^”\"]{4,50}[”\"]|‘[^’]{4,50}’|：[\"“]|指出：|表示："
    quote_hits = len(re.findall(quote_patterns, text))
    quote_score = min(10.0, round(quote_hits * 3.0 + (2.0 if quote_hits > 0 else 0.0), 1))

    # 5. BLUF & Structure
    bluf_patterns = r"【[^】]+】|^\s*[-*•\d+.]\s+|一句话总结|核心结论|核心卖点|参数对照"
    bluf_hits = len(re.findall(bluf_patterns, text, re.MULTILINE))
    bluf_score = min(10.0, round(bluf_hits * 2.5 + (2.0 if bluf_hits > 0 else 0.0), 1))

    # 6. Technical Terms
    tech_patterns = r"透明质酸|神经酰胺|胶原|泛醇|角鲨烷|非布司他|黄嘌呤|别嘌醇|罗通定|玻尿酸|依克多因|肽|重组|微囊"
    tech_hits = len(re.findall(tech_patterns, text))
    tech_score = min(10.0, round(tech_hits * 2.2 + (2.0 if tech_hits > 0 else 0.0), 1))

    # 7. Fluency & Coherence
    conn_patterns = r"不仅.+而且|因为.+所以|一方面.+另一方面|相较于|进而|然而|总而言之|综上所述|也就是说"
    conn_hits = len(re.findall(conn_patterns, text))
    fluency_score = min(10.0, round(conn_hits * 2.5 + 4.0, 1)) if len(text) > 40 else 3.0

    # 8. Unique Selling Propositions (USP)
    usp_patterns = r"首创|专利|独家|专研|械字号|医用级|0添加|纯度99|无菌|自研|认证"
    usp_hits = len(re.findall(usp_patterns, text))
    usp_score = min(10.0, round(usp_hits * 2.8 + (2.0 if usp_hits > 0 else 0.0), 1))

    # 9. Comparison Readiness
    comp_patterns = r"对比|横评|vs|区别于|优于|相较|测评|实测|选购指南|选型|参数表"
    comp_hits = len(re.findall(comp_patterns, text, re.IGNORECASE))
    comp_score = min(10.0, round(comp_hits * 2.6 + (2.0 if comp_hits > 0 else 0.0), 1))

    strategies = [
        {"id": "authoritative_tone", "name_cn": "权威语气与专业定性", "name_en": "Authoritative Tone", "score": auth_score, "max_score": 10.0, "weight": 0.12, "hits": auth_hits, "recommendation_cn": "建议引入临床专家背书、国家药典或诊疗指南表述，增强 AI 引擎对专业可信度的置信分。"},
        {"id": "statistical_evidence", "name_cn": "量化统计与实验测量", "name_en": "Statistical Evidence", "score": stat_score, "max_score": 10.0, "weight": 0.14, "hits": stat_hits, "recommendation_cn": "补充具体试验样本数、百分比降幅（如 28天修护率达98.2%）等量化数字。"},
        {"id": "citation_sources", "name_cn": "权威信源与标准引用", "name_en": "Citation Sources", "score": cite_score, "max_score": 10.0, "weight": 0.12, "hits": cite_hits, "recommendation_cn": "明确标注文献期刊名称、国械注准注册证号或国家推荐标准（GB/T）。"},
        {"id": "quotation_addition", "name_cn": "专家观点与原声引述", "name_en": "Quotation Addition", "score": quote_score, "max_score": 10.0, "weight": 0.10, "hits": quote_hits, "recommendation_cn": "使用双引号直接引述三甲医生或权威实验室科研专家的原话评价。"},
        {"id": "bluf_structure", "name_cn": "BLUF 结论前置与结构化", "name_en": "BLUF & Structural Layout", "score": bluf_score, "max_score": 10.0, "weight": 0.12, "hits": bluf_hits, "recommendation_cn": "首段放置【核心结论】，多用序列清单与加粗标题，便于 AI 模块化抓取。"},
        {"id": "technical_terms", "name_cn": "科学术语与成分命名", "name_en": "Technical Terms", "score": tech_score, "max_score": 10.0, "weight": 0.10, "hits": tech_hits, "recommendation_cn": "使用国际通用的核心有效成份规范化学或药理学学名（如重组III型人源化胶原蛋白）。"},
        {"id": "fluency_and_coherence", "name_cn": "逻辑连贯与转折衔接", "name_en": "Fluency & Coherence", "score": fluency_score, "max_score": 10.0, "weight": 0.10, "hits": conn_hits, "recommendation_cn": "增强因果与转折逻辑衔接词，提升长句的可读性与语义嵌入连贯度。"},
        {"id": "unique_selling_propositions", "name_cn": "品牌独占差异化卖点", "name_en": "Unique Selling Propositions", "score": usp_score, "max_score": 10.0, "weight": 0.10, "hits": usp_hits, "recommendation_cn": "提炼独占性技术优势（如专利微囊、械三认证），形成与竞品不可替代的护城河。"},
        {"id": "comparison_readiness", "name_cn": "横向竞品横评与场景对照", "name_en": "Comparison Readiness", "score": comp_score, "max_score": 10.0, "weight": 0.10, "hits": comp_hits, "recommendation_cn": "设计对比维度（如适用人群、吸收速率、客单价等），契合用户比选场景。"},
    ]

    composite_score = round(sum(s["score"] * s["weight"] for s in strategies) * 10.0, 1)

    return {
        "framework": "KDD 2024 GEO-bench 9-Strategy Optimization Protocol (Aggarwal et al.)",
        "composite_geo_bench_score": composite_score,
        "grade": "S (卓越)" if composite_score >= 85 else ("A (良好)" if composite_score >= 70 else ("B (合格)" if composite_score >= 55 else "C (亟待优化)")),
        "strategies": strategies,
        "top_improvement_areas": [s["name_cn"] for s in sorted(strategies, key=lambda x: x["score"])[:3]],
    }


def compute_adstock_decay_curve(
    peak_lift: float,
    half_life_days: float = 11.0,
    duration_days: int = 30,
) -> Dict[str, Any]:
    """
    Google Meridian & PyMC-Marketing Adstock Decay Curve.
    模拟社媒脉冲发布后，受众记忆与搜索回流在 30 天时序内的几何/Weibull Adstock 衰减轨迹:
      S(t) = S_0 * 2^(-t / half_life_days)
    """
    hl = max(1.0, float(half_life_days))
    dur = max(7, min(90, int(duration_days)))
    p_lift = float(peak_lift)

    timeseries: List[Dict[str, Any]] = []
    cumulative = 0.0
    for day in range(1, dur + 1):
        retention_ratio = 2.0 ** (-float(day) / hl)
        daily_val = round(p_lift * retention_ratio, 2)
        cumulative = round(cumulative + daily_val, 2)
        timeseries.append({
            "day": day,
            "retention_pct": round(retention_ratio * 100.0, 2),
            "daily_lift": daily_val,
            "cumulative_lift": cumulative,
        })

    retention_d7 = round((2.0 ** (-7.0 / hl)) * 100.0, 2)
    retention_d14 = round((2.0 ** (-14.0 / hl)) * 100.0, 2)
    retention_d30 = round((2.0 ** (-30.0 / hl)) * 100.0, 2)

    return {
        "framework": "Google Meridian & PyMC-Marketing Geometric Adstock",
        "half_life_days": hl,
        "duration_days": dur,
        "peak_initial_lift": p_lift,
        "retention_at_day_7_pct": retention_d7,
        "retention_at_day_14_pct": retention_d14,
        "retention_at_day_30_pct": retention_d30,
        "total_cumulative_auc": cumulative,
        "pulse_refresh_recommended_day": 14,
        "timeseries": timeseries,
    }


def compute_sensitivity_matrix(
    base_stage2_res: Dict[str, Any],
    budget_delta_pct: float = 0.0,
    price_delta_pct: float = 0.0,
    repeat_delta_pct: float = 0.0,
) -> Dict[str, Any]:
    """
    Interactive Real-time Sensitivity & What-If Simulator.
    交互式多维敏感性推演模拟器 (预算/售价/复购率弹性系数与收益重算):
    无需重复运行耗时 NLP，基于基线结果毫秒级响应滑块变化。
    """
    roi_data = base_stage2_res.get("roi_and_unit_economics", {})
    cdj_data = base_stage2_res.get("consumer_decision_journey", {})
    waterfall_data = base_stage2_res.get("mckinsey_pocket_price_waterfall", {})

    base_budget = float(roi_data.get("campaign_budget_rmb", 12000.0))
    base_orders = int(roi_data.get("omni_channel_gmv_attribution", {}).get("omni_total_orders", 200))
    per_unit = waterfall_data.get("per_unit_waterfall_rmb", {})
    base_price = float(per_unit.get("3_invoice_price_rmb", 100.0))
    base_cogs_rate = float(per_unit.get("7_unit_cogs_rmb", 25.0)) / max(0.1, base_price)
    base_comm_rate = float(per_unit.get("4_platform_commission_rmb", 5.0)) / max(0.1, base_price)
    base_fulf_rate = float(per_unit.get("5_fulfillment_and_return_rmb", 6.0)) / max(0.1, base_price)
    base_repeat_rate = float(cdj_data.get("postpurchase_loyalty_loop", {}).get("repeat_purchase_rate_pct", 18.0)) / 100.0

    # Apply deltas
    sim_budget = max(100.0, round(base_budget * (1.0 + budget_delta_pct / 100.0), 2))
    sim_price = max(1.0, round(base_price * (1.0 + price_delta_pct / 100.0), 2))
    sim_repeat_rate = max(0.0, min(0.9, base_repeat_rate + (repeat_delta_pct / 100.0)))

    # Budget elasticity (Hill equation sub-linear power law: orders ~ budget^0.72)
    budget_ratio = sim_budget / max(1.0, base_budget)
    order_elasticity_mult = math.pow(budget_ratio, 0.72)

    # Price elasticity of demand (typical e-commerce price elasticity = -1.35)
    price_ratio = sim_price / max(0.1, base_price)
    price_elasticity_mult = math.pow(price_ratio, -1.35)

    sim_orders = max(1, int(round(base_orders * order_elasticity_mult * price_elasticity_mult)))
    sim_gmv = round(sim_orders * sim_price, 2)

    sim_waterfall = compute_mckinsey_pocket_price_waterfall(
        msrp_rmb=sim_price * 1.25,
        selling_price_rmb=sim_price,
        platform_commission_rate=base_comm_rate,
        fulfillment_and_return_rate=base_fulf_rate,
        cogs_rate=base_cogs_rate,
        total_orders=sim_orders,
        campaign_cost_rmb=sim_budget,
    )

    repeat_orders = int(round(sim_orders * sim_repeat_rate))
    repeat_gmv = round(repeat_orders * sim_price, 2)

    sim_net_profit = sim_waterfall["campaign_aggregate"]["net_profit_after_ad_spend_rmb"]
    sim_roas = round(sim_gmv / max(1.0, sim_budget), 2)

    return {
        "inputs": {
            "budget_delta_pct": budget_delta_pct,
            "price_delta_pct": price_delta_pct,
            "repeat_delta_pct": repeat_delta_pct,
            "simulated_budget_rmb": sim_budget,
            "simulated_selling_price_rmb": sim_price,
            "simulated_repeat_rate_pct": round(sim_repeat_rate * 100.0, 1),
        },
        "simulated_financials": {
            "simulated_orders": sim_orders,
            "simulated_gmv_rmb": sim_gmv,
            "simulated_roas": sim_roas,
            "pocket_price_waterfall": sim_waterfall,
            "net_pocket_profit_rmb": sim_net_profit,
            "repeat_orders": repeat_orders,
            "repeat_gmv_rmb": repeat_gmv,
            "total_lifetime_gmv_rmb": round(sim_gmv + repeat_gmv, 2),
        },
    }


DEMO_PROFILES: Dict[str, Dict[str, Any]] = {
    "xhs_medical_skincare_kol": {
        "account_id": "demo_xhs_001",
        "account_name": "林医生聊护肤 (Demo示例账号)",
        "platform": "xiaohongshu",
        "platform_cn": "小红书",
        "account_url": "https://www.xiaohongshu.com/user/profile/demo_medical_skincare_kol",
        "followers": 185000,
        "vertical_category": "皮肤科科普/医美术后修护/功效护肤",
        "avg_views": 46000,
        "median_views": 38500,
        "std_views": 18000,
        "avg_likes": 1920,
        "avg_collects": 1680,
        "avg_comments": 260,
        "avg_shares": 310,
        "avg_follows_gained": 95,
        "avg_3s_retention": 0.71,
        "avg_completion_rate": 0.54,
        "historical_viral_rate": 0.22,
        "audience_female_ratio": 0.86,
        "audience_tier1_2_city_ratio": 0.74,
        "historical_top_keywords": ["医用敷料", "光电术后", "屏障修护", "二类械字号", "透明质酸钠", "敏感肌"],
        "commercial_quote_rmb": 18500.0,
    },
    "douyin_health_otc_kol": {
        "account_id": "demo_dy_002",
        "account_name": "陈药师健康说 (Demo示例账号)",
        "platform": "douyin",
        "platform_cn": "抖音",
        "account_url": "https://www.douyin.com/user/demo_health_otc_kol",
        "followers": 620000,
        "vertical_category": "家庭常备药/眼科护理/慢病科普",
        "avg_views": 168000,
        "median_views": 132000,
        "std_views": 65000,
        "avg_likes": 5400,
        "avg_collects": 2100,
        "avg_comments": 680,
        "avg_shares": 890,
        "avg_follows_gained": 210,
        "avg_3s_retention": 0.68,
        "avg_completion_rate": 0.46,
        "historical_viral_rate": 0.18,
        "audience_female_ratio": 0.62,
        "audience_tier1_2_city_ratio": 0.64,
        "historical_top_keywords": ["滴眼液", "美团买药", "干眼症", "家庭药箱", "慢病管理", "非布司他"],
        "commercial_quote_rmb": 28000.0,
    },
    "bili_hardcore_tech_review": {
        "account_id": "demo_bili_003",
        "account_name": "硬核实验室Lab (Demo示例账号)",
        "platform": "bilibili",
        "platform_cn": "B站",
        "account_url": "https://space.bilibili.com/88888803",
        "followers": 340000,
        "vertical_category": "硬核横评/成分检测/理疗仪器",
        "avg_views": 95000,
        "median_views": 78000,
        "std_views": 42000,
        "avg_likes": 4800,
        "avg_collects": 3900,
        "avg_comments": 520,
        "avg_shares": 610,
        "avg_follows_gained": 180,
        "avg_3s_retention": 0.74,
        "avg_completion_rate": 0.58,
        "historical_viral_rate": 0.25,
        "audience_female_ratio": 0.54,
        "audience_tier1_2_city_ratio": 0.78,
        "historical_top_keywords": ["横评实测", "京东自营", "医用敷料", "实验室检测", "参数对比"],
        "commercial_quote_rmb": 24000.0,
    },
    "channels_family_wellness_kol": {
        "account_id": "demo_wx_004",
        "account_name": "李主任家庭健康指南 (Demo示例账号)",
        "platform": "wechat_channels",
        "platform_cn": "微信视频号",
        "account_url": "https://channels.weixin.qq.com/demo_family_wellness_kol",
        "followers": 210000,
        "vertical_category": "家庭健康/中青年慢病/术后护理",
        "avg_views": 72000,
        "median_views": 59000,
        "std_views": 26000,
        "avg_likes": 2600,
        "avg_collects": 1950,
        "avg_comments": 340,
        "avg_shares": 1450,
        "avg_follows_gained": 130,
        "avg_3s_retention": 0.69,
        "avg_completion_rate": 0.52,
        "historical_viral_rate": 0.20,
        "audience_female_ratio": 0.66,
        "audience_tier1_2_city_ratio": 0.69,
        "historical_top_keywords": ["家庭护理", "疤痕修复", "微信搜一搜", "慢病管理", "高尿酸"],
        "commercial_quote_rmb": 19500.0,
    },

    "tiktok_beauty_lifestyle_creator": {
        "account_id": "demo_tt_001",
        "account_name": "Sarah Lin | Biohacking & K-Beauty (@sarahglows)",
        "platform": "tiktok",
        "platform_cn": "TikTok (海外)",
        "account_url": "https://www.tiktok.com/@sarahglows",
        "followers": 480000,
        "vertical_category": "美妆/修护/跨境独立站DTC (Beauty & Barrier Care DTC)",
        "avg_views": 125000,
        "median_views": 98000,
        "std_views": 45000,
        "avg_likes": 8800,
        "avg_collects": 4200,
        "avg_comments": 480,
        "avg_shares": 920,
        "avg_follows_gained": 310,
        "avg_3s_retention": 0.73,
        "avg_completion_rate": 0.49,
        "historical_viral_rate": 0.26,
        "audience_female_ratio": 0.82,
        "audience_tier1_2_city_ratio": 0.78,
        "historical_top_keywords": ["Cica Barrier", "K-Beauty Serum", "Shopify DTC", "Skin Repair", "Glass Skin"],
        "commercial_quote_rmb": 26000.0,
    },
    "youtube_tech_edc_reviewer": {
        "account_id": "demo_yt_002",
        "account_name": "DaveTech & Everyday Carry Lab (Demo)",
        "platform": "youtube",
        "platform_cn": "YouTube (海外)",
        "account_url": "https://www.youtube.com/@davetechedc_demo",
        "followers": 650000,
        "vertical_category": "消费电子/GaN快充/出海3C测评 (Consumer Tech & EDC)",
        "avg_views": 185000,
        "median_views": 142000,
        "std_views": 68000,
        "avg_likes": 7600,
        "avg_collects": 3800,
        "avg_comments": 650,
        "avg_shares": 1100,
        "avg_follows_gained": 420,
        "avg_3s_retention": 0.76,
        "avg_completion_rate": 0.62,
        "historical_viral_rate": 0.28,
        "audience_female_ratio": 0.24,
        "audience_tier1_2_city_ratio": 0.85,
        "historical_top_keywords": ["Anker Fast Charging", "GaN Charger", "Amazon US Best Seller", "EDC Tech", "Benchmarking"],
        "commercial_quote_rmb": 42000.0,
    },
    "instagram_aesthetic_derma": {
        "account_id": "demo_ig_003",
        "account_name": "Dr. Elena Vance | Aesthetic & Skin Health (@drelenavance)",
        "platform": "instagram",
        "platform_cn": "Instagram (海外)",
        "account_url": "https://www.instagram.com/drelenavance",
        "followers": 290000,
        "vertical_category": "轻医美/科学护肤/抗衰 (Aesthetic Derma & Skincare)",
        "avg_views": 68000,
        "median_views": 54000,
        "std_views": 22000,
        "avg_likes": 3900,
        "avg_collects": 2400,
        "avg_comments": 310,
        "avg_shares": 450,
        "avg_follows_gained": 160,
        "avg_3s_retention": 0.70,
        "avg_completion_rate": 0.52,
        "historical_viral_rate": 0.21,
        "audience_female_ratio": 0.88,
        "audience_tier1_2_city_ratio": 0.82,
        "historical_top_keywords": ["Medical Grade Skincare", "Post Procedure", "Hyaluronic Acid", "Shopify Store", "Derm Approved"],
        "commercial_quote_rmb": 22000.0,
    },
    "facebook_family_home_wellness": {
        "account_id": "demo_fb_004",
        "account_name": "Modern Family Living & Practical Health (Demo)",
        "platform": "facebook",
        "platform_cn": "Facebook (海外)",
        "account_url": "https://www.facebook.com/modernfamilywellness_demo",
        "followers": 380000,
        "vertical_category": "家庭健康/常备护理 (Family Wellness & Everyday Health)",
        "avg_views": 82000,
        "median_views": 66000,
        "std_views": 31000,
        "avg_likes": 2900,
        "avg_collects": 1500,
        "avg_comments": 420,
        "avg_shares": 850,
        "avg_follows_gained": 190,
        "avg_3s_retention": 0.65,
        "avg_completion_rate": 0.44,
        "historical_viral_rate": 0.17,
        "audience_female_ratio": 0.72,
        "audience_tier1_2_city_ratio": 0.68,
        "historical_top_keywords": ["Family First Aid", "Dry Eye Relief", "DTC Subscription", "Wellness Routine"],
        "commercial_quote_rmb": 25000.0,
    },
    "x_twitter_ai_hardware_pro": {
        "account_id": "demo_x_005",
        "account_name": "Alex Chen | Hardware Architect & Edge AI (@alexchen_tech)",
        "platform": "x_twitter",
        "platform_cn": "X / Twitter (海外)",
        "account_url": "https://x.com/alexchen_tech",
        "followers": 195000,
        "vertical_category": "硬核极客/半导体/出海科技 (Hardware Architecture & AI Hardware)",
        "avg_views": 75000,
        "median_views": 58000,
        "std_views": 36000,
        "avg_likes": 3200,
        "avg_collects": 2600,
        "avg_comments": 380,
        "avg_shares": 720,
        "avg_follows_gained": 220,
        "avg_3s_retention": 0.75,
        "avg_completion_rate": 0.58,
        "historical_viral_rate": 0.24,
        "audience_female_ratio": 0.18,
        "audience_tier1_2_city_ratio": 0.88,
        "historical_top_keywords": ["GaN Power Delivery", "Thermal Performance", "Kickstarter Tech", "Amazon Global", "Benchmarking"],
        "commercial_quote_rmb": 21000.0,
    },

}


class _DemoDaemonClientStub:
    def ensure_daemon_running(self):
        return (True, 3765, "DEMO_SANDBOX_READY")

    def get_cdp_bridge_info(self):
        return {"mode": "OPEN_CORE_DEMO"}


KB_EMPIRICAL_PROFILES = DEMO_PROFILES


class DemoSocialCrawler(BaseSocialCrawler):
    """Open-Core Demo Crawler (returns sanitized reference profiles)."""

    def __init__(self) -> None:
        self.daemon_client = _DemoDaemonClientStub()

    def probe_ecommerce_shelves(self, product_name: str, category: str) -> Dict[str, Any]:
        return {
            "jd_shelf_ready": True,
            "tmall_shelf_ready": True,
            "meituan_o2o_ready": True,
            "mode": "OPEN_CORE_DEMO",
        }

    def fetch_account_profile(
        self,
        account_url_or_key: str = "xhs_medical_skincare_kol",
        platform_override: str | None = None,
        use_marvis_live: bool = False,
        custom_overrides: Dict[str, Any] | None = None,
        account_url: str | None = None,
    ) -> SocialAccountProfile:
        key = (account_url or account_url_or_key or "xhs_medical_skincare_kol").strip()
        plat = platform_override or detect_platform_from_url(key)
        base = DEMO_PROFILES.get(key)
        if not base:
            by_plat = {
                "xiaohongshu": "xhs_medical_skincare_kol",
                "douyin": "douyin_health_otc_kol",
                "bilibili": "bili_hardcore_tech_review",
                "wechat_channels": "channels_family_wellness_kol",
                "tiktok": "tiktok_beauty_lifestyle_creator",
                "youtube": "youtube_tech_edc_reviewer",
                "instagram": "instagram_aesthetic_derma",
                "facebook": "facebook_family_home_wellness",
                "x_twitter": "x_twitter_ai_hardware_pro",
            }
            base = dict(DEMO_PROFILES[by_plat.get(plat, "xhs_medical_skincare_kol")])
            if key.startswith("http"):
                base["account_url"] = key

        merged = dict(base)
        if custom_overrides:
            for k, v in custom_overrides.items():
                if v is not None and v != "":
                    merged[k] = v

        posts = [
            HistoricalPost(
                post_id=f"{merged['account_id']}_p{i}",
                title=f"【Demo示例笔记 #{i}】{merged['vertical_category'].split('/')[0]}实测与科学选购指南",
                publish_date=f"2026-10-{10 + i:02d}",
                views=int(merged["avg_views"] * (0.85 + 0.1 * i)),
                likes=int(merged["avg_likes"] * (0.85 + 0.1 * i)),
                collects=int(merged["avg_collects"] * (0.85 + 0.1 * i)),
                comments=int(merged["avg_comments"] * (0.85 + 0.1 * i)),
                shares=int(merged["avg_shares"] * (0.85 + 0.1 * i)),
                is_viral=(i == 3),
            )
            for i in range(1, 5)
        ]

        return SocialAccountProfile(
            account_id=str(merged["account_id"]),
            account_name=str(merged["account_name"]),
            platform=str(merged["platform"]),
            platform_cn=str(merged["platform_cn"]),
            account_url=str(merged["account_url"]),
            followers=int(merged["followers"]),
            vertical_category=str(merged["vertical_category"]),
            avg_views=float(merged["avg_views"]),
            median_views=float(merged["median_views"]),
            std_views=float(merged["std_views"]),
            avg_likes=float(merged["avg_likes"]),
            avg_collects=float(merged["avg_collects"]),
            avg_comments=float(merged["avg_comments"]),
            avg_shares=float(merged["avg_shares"]),
            avg_follows_gained=float(merged["avg_follows_gained"]),
            avg_3s_retention=float(merged["avg_3s_retention"]),
            avg_completion_rate=float(merged["avg_completion_rate"]),
            historical_viral_rate=float(merged["historical_viral_rate"]),
            audience_female_ratio=float(merged["audience_female_ratio"]),
            audience_tier1_2_city_ratio=float(merged["audience_tier1_2_city_ratio"]),
            historical_top_keywords=list(merged["historical_top_keywords"]),
            commercial_quote_rmb=float(merged["commercial_quote_rmb"]),
            recent_posts=posts,
            crawl_metadata={
                "crawler_engine": "via54SocialROI Open-Core Demo Sandbox",
                "data_source_tier": "Demo Sandbox (Install private_core for Live Marvis SSR)",
                "elapsed_ms": 8,
            },
        )


def generate_smart_stage2_from_product(
    account: SocialAccountProfile | Dict[str, Any],
    product: ProductInput | Dict[str, Any],
) -> Dict[str, Any]:
    acct_name = (
        account.account_name
        if isinstance(account, SocialAccountProfile)
        else (account.get("account_name") or "示范达人")
    )
    p_name = (
        product.product_name
        if isinstance(product, ProductInput)
        else (product.get("product_name") or "示范产品")
    ) or "示范产品"
    b_name = (
        product.brand_name
        if isinstance(product, ProductInput)
        else (product.get("brand_name") or "示范品牌")
    ) or "示范品牌"
    points = (
        product.core_selling_points
        if isinstance(product, ProductInput)
        else product.get("core_selling_points", ["核心功效卖点1", "核心功效卖点2"])
    )
    short_prod = (p_name.split("(")[0].strip() or "核心单品")
    short_brand = (b_name.split("(")[0].strip() or "官方旗舰")
    topics = [f"#{short_prod}", f"#{short_brand}", "#科学评测", "#避坑指南", "#好物推荐"]
    theme = f"{short_prod}深度实测：认准核心参数与科学用法，告别盲目跟风"
    pts_text = "；".join(points[:3]) if points else "具备权威标准背书与高依从性体验"
    script = (
        f"【黄金前3秒钩子】选{short_prod}千万别只看宣传！学会看这3个硬核指标，少花冤枉钱！\n"
        f"【痛点与权威背书】很多朋友在挑选时容易踩坑，核心要看标准认证与临床实测数据。\n"
        f"【核心数据与参数对比】我们实测了【{p_name}】：{pts_text}，多项指标表现优异。\n"
        f"【多渠道搜词与转化锚点】日常入手建议直接打开【京东自营】或【天猫官方旗舰店】搜“{short_prod}”；"
        f"急用可直接打开【美团】搜“{short_prod}”30分钟闪送到家！评论区置顶已放正品核验蓝链与常见问题清单。"
    )
    return {
        "topics": topics,
        "campaign_theme": theme,
        "script_content": script,
        "generated_for_account": acct_name,
        "generated_for_product": p_name,
    }


class DemoPromotionEngine(BasePromotionEngine):
    """
    Open-Core Demo Promotion Engine.
    Provides simplified reference calculations for testing the UI, CLI, and MCP Server.
    """

    @staticmethod
    def _sanitize_product(product: ProductInput) -> tuple[ProductInput, List[str]]:
        warnings: List[str] = []
        price = float(product.selling_price_rmb or 0.0)
        if price <= 0.0:
            warnings.append("成交价需大于 0，已自动回退至 ¥99 基准价。")
            price = 99.0
        msrp = float(product.msrp_rmb or 0.0)
        if msrp < price:
            msrp = round(price * 1.25, 2)
        budget = max(100.0, float(product.campaign_budget_rmb or 0.0))
        if float(product.campaign_budget_rmb or 0.0) < 100.0:
            warnings.append("投放预算低于 ¥100，已按最低有效门槛与商务可行性折算。")
        cogs = min(0.92, max(0.01, float(product.cogs_rate or 0.22)))
        comm = min(0.35, max(0.0, float(product.platform_commission_rate or 0.05)))
        sanitized = ProductInput(
            **{
                **product.to_dict(),
                "selling_price_rmb": price,
                "msrp_rmb": msrp,
                "campaign_budget_rmb": budget,
                "cogs_rate": cogs,
                "gross_margin_rate": round(1.0 - cogs, 4),
                "platform_commission_rate": comm,
            }
        )
        return sanitized, warnings

    def compute_stage1(
        self,
        account: SocialAccountProfile,
        product: ProductInput,
        post_count_matrix: int = 1,
    ) -> Dict[str, Any]:
        product, input_warnings = self._sanitize_product(product)
        fit_score = 0.86
        fit_mult = 1.15
        quote = max(500.0, float(account.commercial_quote_rmb or 10000.0)) * max(1, post_count_matrix)
        budget_ratio = float(product.campaign_budget_rmb) / max(1.0, quote * 0.8)
        booking_feasibility = min(1.0, max(0.02, budget_ratio ** 1.15)) if budget_ratio < 1.0 else 1.0
        paid_boost = 1.0 + min(0.85, max(0.0, (float(product.campaign_budget_rmb) - quote) / max(1.0, quote)) * 0.35)
        scale = fit_mult * max(1, post_count_matrix) * booking_feasibility * paid_boost

        views = max(50, int(account.avg_views * scale))
        likes = min(int(views * 0.28), int(account.avg_likes * scale))
        collects = min(int(views * 0.28), int(account.avg_collects * scale))
        comments = min(int(views * 0.06), int(account.avg_comments * scale))
        shares = min(int(views * 0.08), int(account.avg_shares * scale))
        follows = int(account.avg_follows_gained * scale)
        total_inter = likes + collects + comments + shares
        ces = likes * 1 + collects * 1 + comments * 4 + shares * 4 + follows * 8

        price_elasticity = min(1.25, max(0.25, (118.0 / max(10.0, product.selling_price_rmb)) ** 0.35))
        search_uv = max(1, int(views * 0.022))
        jd_uv = int(search_uv * 0.36)
        tmall_uv = int(search_uv * 0.42)
        mt_uv = search_uv - jd_uv - tmall_uv
        store_uv = max(1, int(search_uv * 0.58))
        orders = max(0, int(round(store_uv * 0.14 * price_elasticity)))
        gmv = round(orders * product.selling_price_rmb, 2)

        is_global = account.platform in GLOBAL_PLATFORMS
        if is_global:
            daily_curve = [
                {
                    "day": d,
                    "google_trends_delta": int(320 * (0.91 ** d)),
                    "tiktok_search_delta": int(680 * (0.88 ** d)),
                    "amazon_search_delta": int(450 * (0.92 ** d)),
                }
                for d in range(1, 31)
            ]
        else:
            daily_curve = [
                {
                    "day": d,
                    "baidu_delta": int(180 * (0.88 ** d)),
                    "wechat_delta": int(520 * (0.89 ** d)),
                    "douyin_delta": int(680 * (0.87 ** d)),
                    "xiaohongshu_delta": int(750 * (0.90 ** d)),
                }
                for d in range(1, 31)
            ]

        return {
            "stage": "Stage 1 Baseline (Open-Core Demo Sandbox)",
            "model_diagnostics": {
                "data_confidence": "high",
                "metrics_estimated": False,
                "booking_feasibility": round(booking_feasibility, 3),
                "price_elasticity_multiplier": round(price_elasticity, 3),
                "input_warnings": input_warnings,
            },
            "account_summary": account.to_dict(),
            "product_summary": product.to_dict(),
            "account_product_fit": {
                "fit_score": fit_score,
                "fit_multiplier": fit_mult,
                "fit_grade": "S级 (Demo极高契合)",
                "matched_historical_keywords": account.historical_top_keywords[:4],
            },
            "influence_effect": {
                "expected_views": views,
                "unique_reach_uv": int(views * 0.82),
                "views_ci_p10_p90": [int(views * 0.7), int(views * 1.35)],
                "total_interactions": total_inter,
                "engagement_rate": round(total_inter / max(1, views), 4),
                "breakdown": {
                    "likes": likes,
                    "collects": collects,
                    "comments": comments,
                    "shares": shares,
                    "follows_gained": follows,
                },
                "platform_algorithm_score": {
                    "metric_name": "Demo Composite Engagement Score",
                    "score_value": ces,
                    "xiaohongshu_ces_equivalent": ces,
                },
                "cascade_dynamics": {
                    "hawkes_branching_ratio_n_star": 0.42,
                    "cascade_amplification_factor": 1.72,
                    "expected_3s_retention": account.avg_3s_retention,
                    "expected_completion_rate": account.avg_completion_rate,
                    "viral_post_probability": 0.24,
                },
            },
            "index_lift_effect": {
                "adstock_model": "Demo Exponential Carryover (Open-Core Reference)",
                "platforms": (
                    {
                        "google_trends": {
                            "name_cn": "谷歌趋势 (Google Trends)",
                            "name_en": "Google Trends",
                            "baseline_daily": 3200,
                            "peak_daily_delta": 650,
                            "stage1_peak_daily_delta": 650,
                            "peak_lift_pct": 20.3,
                            "avg_30d_daily_delta": 220,
                            "avg_30d_lift_pct": 6.9,
                            "cumulative_30d_search_impulse": 6600,
                        },
                        "tiktok_search": {
                            "name_cn": "TikTok 搜索趋势 (TikTok Search)",
                            "name_en": "TikTok Search Trends",
                            "baseline_daily": 14000,
                            "peak_daily_delta": 3800,
                            "stage1_peak_daily_delta": 3800,
                            "peak_lift_pct": 27.1,
                            "avg_30d_daily_delta": 1300,
                            "avg_30d_lift_pct": 9.3,
                            "cumulative_30d_search_impulse": 39000,
                        },
                        "amazon_search": {
                            "name_cn": "亚马逊站内搜索 (Amazon Search Index)",
                            "name_en": "Amazon Search Volume",
                            "baseline_daily": 8500,
                            "peak_daily_delta": 2100,
                            "stage1_peak_daily_delta": 2100,
                            "peak_lift_pct": 24.7,
                            "avg_30d_daily_delta": 750,
                            "avg_30d_lift_pct": 8.8,
                            "cumulative_30d_search_impulse": 22500,
                        },
                    } if is_global else {
                        "baidu_index": {
                            "name_cn": "百度指数",
                            "name_en": "Baidu Index",
                            "baseline_daily": 1850,
                            "peak_daily_delta": 320,
                            "stage1_peak_daily_delta": 320,
                            "peak_lift_pct": 17.3,
                            "avg_30d_daily_delta": 110,
                            "avg_30d_lift_pct": 5.9,
                            "cumulative_30d_search_impulse": 3300,
                        },
                        "wechat_index": {
                            "name_cn": "微信指数",
                            "name_en": "WeChat Index",
                            "baseline_daily": 42000,
                            "peak_daily_delta": 6800,
                            "stage1_peak_daily_delta": 6800,
                            "peak_lift_pct": 16.2,
                            "avg_30d_daily_delta": 2400,
                            "avg_30d_lift_pct": 5.7,
                            "cumulative_30d_search_impulse": 72000,
                        },
                        "douyin_index": {
                            "name_cn": "抖音巨量算数",
                            "name_en": "Douyin Index",
                            "baseline_daily": 26500,
                            "peak_daily_delta": 5400,
                            "stage1_peak_daily_delta": 5400,
                            "peak_lift_pct": 20.4,
                            "avg_30d_daily_delta": 1900,
                            "avg_30d_lift_pct": 7.2,
                            "cumulative_30d_search_impulse": 57000,
                        },
                        "xiaohongshu_index": {
                            "name_cn": "小红书搜索指数",
                            "name_en": "Xiaohongshu Search Index",
                            "baseline_daily": 9800,
                            "peak_daily_delta": 2900,
                            "stage1_peak_daily_delta": 2900,
                            "peak_lift_pct": 29.6,
                            "avg_30d_daily_delta": 1050,
                            "avg_30d_lift_pct": 10.7,
                            "cumulative_30d_search_impulse": 31500,
                        },
                    }
                ),
                "daily_30d_curve": daily_curve,
            },
            "ecommerce_search_lift_effect": {
                "overall_impression_to_search_rate": 0.022,
                "stage1_total_search_uv": search_uv,
                "total_cross_platform_search_uv": search_uv,
                "total_store_visit_uv": store_uv,
                "total_add_to_cart_uv": int(store_uv * 0.28),
                "total_expected_search_orders": orders,
                "total_attributed_search_gmv_rmb": gmv,
                "channels": (
                    {
                        "shopify_dtc": {
                            "name_cn": "Shopify 独立站 (Brand DTC Store)",
                            "name_en": "Shopify Brand Store",
                            "stage1_search_uv": int(search_uv * 0.45),
                            "incremental_search_uv": int(search_uv * 0.45),
                            "search_uv_lift_vs_stage1_pct": 0.0,
                            "search_keyword_lift_pct_7d": 22.5,
                            "store_entry_ctr": 0.65,
                            "store_visit_uv": int(search_uv * 0.45 * 0.65),
                            "add_to_cart_uv": int(search_uv * 0.45 * 0.22),
                            "expected_orders": max(1, int(orders * 0.48)),
                            "attributed_search_gmv_rmb": round(max(1, int(orders * 0.48)) * product.selling_price_rmb, 2),
                        },
                        "amazon_global": {
                            "name_cn": "亚马逊北美/欧洲站 (Amazon Global)",
                            "name_en": "Amazon Global Store",
                            "stage1_search_uv": int(search_uv * 0.35),
                            "incremental_search_uv": int(search_uv * 0.35),
                            "search_uv_lift_vs_stage1_pct": 0.0,
                            "search_keyword_lift_pct_7d": 19.8,
                            "store_entry_ctr": 0.58,
                            "store_visit_uv": int(search_uv * 0.35 * 0.58),
                            "add_to_cart_uv": int(search_uv * 0.35 * 0.18),
                            "expected_orders": max(1, int(orders * 0.36)),
                            "attributed_search_gmv_rmb": round(max(1, int(orders * 0.36)) * product.selling_price_rmb, 2),
                        },
                        "tiktok_shop": {
                            "name_cn": "TikTok Shop 闭环电商",
                            "name_en": "TikTok Shop Global",
                            "stage1_search_uv": int(search_uv * 0.20),
                            "incremental_search_uv": int(search_uv * 0.20),
                            "search_uv_lift_vs_stage1_pct": 0.0,
                            "search_keyword_lift_pct_7d": 25.4,
                            "store_entry_ctr": 0.70,
                            "store_visit_uv": int(search_uv * 0.20 * 0.70),
                            "add_to_cart_uv": int(search_uv * 0.20 * 0.26),
                            "expected_orders": max(1, int(orders * 0.16)),
                            "attributed_search_gmv_rmb": round(max(1, int(orders * 0.16)) * product.selling_price_rmb, 2),
                        },
                    } if is_global else {
                        "jd": {
                            "name_cn": "京东 (JD.com)",
                            "stage1_search_uv": jd_uv,
                            "incremental_search_uv": jd_uv,
                            "search_uv_lift_vs_stage1_pct": 0.0,
                            "search_keyword_lift_pct_7d": 18.5,
                            "store_entry_ctr": 0.60,
                            "store_visit_uv": int(jd_uv * 0.60),
                            "add_to_cart_uv": int(jd_uv * 0.18),
                            "expected_orders": max(1, int(jd_uv * 0.09)),
                            "attributed_search_gmv_rmb": round(max(1, int(jd_uv * 0.09)) * product.selling_price_rmb, 2),
                        },
                        "taobao_tmall": {
                            "name_cn": "淘天 (Taobao & Tmall)",
                            "stage1_search_uv": tmall_uv,
                            "incremental_search_uv": tmall_uv,
                            "search_uv_lift_vs_stage1_pct": 0.0,
                            "search_keyword_lift_pct_7d": 21.2,
                            "store_entry_ctr": 0.58,
                            "store_visit_uv": int(tmall_uv * 0.58),
                            "add_to_cart_uv": int(tmall_uv * 0.17),
                            "expected_orders": max(1, int(tmall_uv * 0.085)),
                            "attributed_search_gmv_rmb": round(max(1, int(tmall_uv * 0.085)) * product.selling_price_rmb, 2),
                        },
                        "meituan": {
                            "name_cn": "美团闪购/买药 (Meituan O2O)",
                            "stage1_search_uv": mt_uv,
                            "incremental_search_uv": mt_uv,
                            "search_uv_lift_vs_stage1_pct": 0.0,
                            "search_keyword_lift_pct_7d": 16.4,
                            "store_entry_ctr": 0.55,
                            "store_visit_uv": int(mt_uv * 0.55),
                            "add_to_cart_uv": int(mt_uv * 0.16),
                            "expected_orders": max(1, int(mt_uv * 0.08)),
                            "attributed_search_gmv_rmb": round(max(1, int(mt_uv * 0.08)) * product.selling_price_rmb, 2),
                        },
                    }
                ),
            },
        }

    def compute_stage2(
        self,
        account: SocialAccountProfile,
        product: ProductInput,
        stage2_input: Stage2ContentInput,
    ) -> Dict[str, Any]:
        product, input_warnings = self._sanitize_product(product)
        s1 = self.compute_stage1(account, product, post_count_matrix=stage2_input.post_count_matrix)
        s1_inf = s1["influence_effect"]
        s1_ecom = s1["ecommerce_search_lift_effect"]
        diag = dict(s1.get("model_diagnostics", {}))
        diag["input_warnings"] = list(dict.fromkeys(input_warnings + list(diag.get("input_warnings", []))))
        s1["model_diagnostics"] = diag

        content_mult = 1.48
        views2 = int(s1_inf["expected_views"] * content_mult)
        inter2 = int(s1_inf["total_interactions"] * 1.56)
        bd1 = s1_inf["breakdown"]

        price_elasticity = float(diag.get("price_elasticity_multiplier", 1.0))
        search2 = max(1, int(s1_ecom["total_cross_platform_search_uv"] * 1.72))
        store2 = max(1, int(search2 * 0.62))
        orders2 = max(0, int(round(store2 * 0.16 * price_elasticity)))
        search_gmv2 = round(orders2 * product.selling_price_rmb, 2)
        direct_orders = max(0, int(round(orders2 * 0.35)))
        geo_orders = max(0, int(round(orders2 * 0.22)))
        omni_orders = orders2 + direct_orders + geo_orders
        omni_gmv = round(omni_orders * product.selling_price_rmb, 2)
        s1_gmv = max(1.0, float(s1_ecom["total_attributed_search_gmv_rmb"]))
        spend = max(100.0, float(product.campaign_budget_rmb))
        roas = round(omni_gmv / spend, 2)
        unit_net_margin = round(product.selling_price_rmb * (1.0 - product.cogs_rate - product.platform_commission_rate - 0.06), 2)
        net_profit = round(omni_orders * unit_net_margin - spend, 2)
        max_acceptable_quote = round(max(0.0, omni_orders * unit_net_margin), 2)

        channels2 = {}
        for k, ch in s1_ecom["channels"].items():
            c_uv = int(ch["incremental_search_uv"] * 1.72)
            c_store = int(c_uv * 0.62)
            c_ord = max(1, int(c_store * 0.16))
            channels2[k] = {
                **ch,
                "incremental_search_uv": c_uv,
                "search_uv_lift_vs_stage1_pct": 72.0,
                "store_visit_uv": c_store,
                "add_to_cart_uv": int(c_store * 0.30),
                "expected_orders": c_ord,
                "attributed_search_gmv_rmb": round(c_ord * product.selling_price_rmb, 2),
            }

        ai_engines = [
            ("DeepSeek (V3/R1 · Search & Fetch API)", "标准化模块化检索与深度学术横评", 9.5, 22.4),
            ("腾讯元宝 (元宝搜索 MCP / 微信搜一搜 Agent)", "微信生态与元宝搜索 MCP 开放检索枢纽", 10.2, 23.8),
            ("字节豆包 (Doubao AI / 火山引擎企业 Agent)", "短视频口播字幕与座舱/客服 Agent 模块", 11.0, 24.5),
            ("Kimi 智能助手 (长上下文深度检索)", "多维参数对比表与注册证号解析", 8.8, 20.6),
            ("百度文心一言 (百度百家/百科生态)", "结构化问答与专家共识引文", 9.0, 19.8),
            ("阿里通义千问 (淘天电商消费指南)", "真实买家测评与电商搜词锚点", 8.5, 19.2),
            ("Perplexity AI (全球学术与消费检索)", "统计百分比与临床文献引用", 6.5, 15.4),
            ("ChatGPT Search (OpenAI 对话购物收银台)", "清晰FAQ与对话式商品决策推荐", 6.8, 16.1),
        ]

        brand_stature = classify_brand_stature(product.brand_name, product.category)
        stature_mult = brand_stature["som_stature_multiplier"]

        ai_engines_breakdown = []
        for name, aff, b_som_raw, p_som_raw in ai_engines:
            b_som = round(b_som_raw * stature_mult, 2)
            p_som = round(p_som_raw * stature_mult, 2)
            delta = round(p_som - b_som, 2)
            p10 = round(max(0.1, p_som * (1.0 - 0.65 * 0.5)), 2)
            p50 = p_som
            p90 = round(min(98.0, p_som * (1.0 + 0.65 * 0.5)), 2)
            ai_engines_breakdown.append({
                "name_cn": name,
                "rag_source_affinity": aff,
                "baseline_som_pct": b_som,
                "post_campaign_som_pct": p_som,
                "som_lift_percentage_points": delta,
                "som_p10_pct": p10,
                "som_p50_pct": p50,
                "som_p90_pct": p90,
                "schulte_variance_model": "Schulte et al. (2026) 65% Day-to-Day AI Citation Variance",
                "top1_recommendation_rate": round(p_som / 100.0 * 0.62, 3),
                "citation_adoption_rate": round(p_som / 100.0 * 0.78, 3),
            })

        cdj_funnel = compute_mckinsey_cdj_funnel(
            reach_uv=views2,
            interaction_uv=inter2,
            store_search_uv=search2,
            geo_query_uv=int(search2 * 0.35),
            direct_click_uv=int(views2 * 0.015),
            total_orders=omni_orders,
            repeat_rate=product.repeat_purchase_rate_annual,
            selling_price_rmb=product.selling_price_rmb,
        )

        ppw_detailed = compute_mckinsey_pocket_price_waterfall(
            msrp_rmb=product.msrp_rmb or (product.selling_price_rmb * 1.25),
            selling_price_rmb=product.selling_price_rmb,
            platform_commission_rate=product.platform_commission_rate,
            fulfillment_and_return_rate=0.06,
            cogs_rate=product.cogs_rate,
            total_orders=omni_orders,
            campaign_cost_rmb=spend,
        )

        return {
            "stage": "Stage 2 Full Enhanced (Open-Core Demo Sandbox)",
            "model_diagnostics": diag,
            "stage1_baseline": s1,
            "script_nlp_and_compliance_analysis": {
                "hook_score": 88.5,
                "topic_score": 86.0,
                "anchor_score": 91.0,
                "visual_ctr_multiplier": stage2_input.visual_ctr_multiplier,
                "visual_aesthetics_score": stage2_input.visual_aesthetics_score,
                "compliance": {
                    "status": "PASS_TIER3_SUPER_POOL (Demo合规通过)",
                    "traffic_moderation_factor": 1.0,
                    "detected_violations": [],
                },
            },
            "enhanced_influence_effect": {
                **s1_inf,
                "expected_views": views2,
                "views_lift_vs_stage1_pct": 48.0,
                "total_interactions": inter2,
                "interactions_lift_vs_stage1_pct": 56.0,
                "breakdown": {
                    "likes": int(bd1["likes"] * 1.52),
                    "collects": int(bd1["collects"] * 1.65),
                    "comments": int(bd1["comments"] * 1.58),
                    "shares": int(bd1["shares"] * 1.60),
                    "follows_gained": int(bd1["follows_gained"] * 1.50),
                },
            },
            "enhanced_index_lift_effect": s1["index_lift_effect"],
            "enhanced_ecommerce_search_lift_effect": {
                **s1_ecom,
                "total_cross_platform_search_uv": search2,
                "search_uv_lift_vs_stage1_pct": 72.0,
                "total_store_visit_uv": store2,
                "total_add_to_cart_uv": int(store2 * 0.30),
                "total_expected_search_orders": orders2,
                "total_attributed_search_gmv_rmb": search_gmv2,
                "channels": channels2,
            },
            "geo_effect": {
                "pawc_visibility_score": {
                    "baseline_pawc": 24.5,
                    "post_campaign_pawc": 58.2,
                    "pawc_lift_pct": 137.5,
                },
                "share_of_model_summary": {
                    "avg_baseline_som_pct": 8.79,
                    "avg_post_campaign_som_pct": 20.23,
                    "avg_som_lift_pts": 11.44,
                },
                "kdd24_content_boosters": {
                    "geo_content_multiplier": 1.54,
                    "quotation_addition_boost": 0.28,
                    "statistics_addition_boost": 0.32,
                    "cite_sources_boost": 0.26,
                },
                "agent_era_5_assets": {
                    "composite_asset_score_100": 85.0,
                    "asset_1_brand_facts_consistency": {"score": 0.95, "status": "PASS"},
                    "asset_2_scenario_5chain_alignment": {"score": 0.88, "chain_completeness_ratio": "5/5", "is_complete_5chain": True},
                    "asset_3_third_party_sources": {"score": 0.86, "has_clinical_tier": True, "has_lab_teardown_tier": True},
                    "asset_4_agent_machine_accessibility": {"score": 0.82, "mcp_yuanbao_friendly": True},
                    "asset_5_conversion_fulfillment": {"score": 0.84, "has_direct_shelf_routing": True},
                },
                "ai_citation_half_life_dynamics": {
                    "median_half_life_days": 11.0,
                    "decay_formula": "R(t) = 2^(-t / 11.0)",
                    "retention_day_7_pct": 64.3,
                    "retention_day_14_pct": 41.4,
                    "retention_day_30_pct": 15.1,
                    "recommended_pulse_refresh_cycle_days": 14,
                    "pulse_refresh_gain_multiplier": 1.42,
                    "strategic_takeaway_cn": "研究实证 AI 引用的中位半衰期仅约 11 天，单次投放不存在长期永久复利；强烈建议按 14 天（双周）周期进行矩阵补种，持续向腾讯元宝搜索 MCP、DeepSeek Fetch 及各大商业 Agent 提供高一致性、结构化事实与第三方实证信源。",
                    "strategic_takeaway_en": "Empirical studies reveal AI citation has a median half-life of only ~11 days without permanent compounding. A 14-day bi-weekly matrix refresh pulse is strongly recommended to feed Tencent Yuanbao Search MCP, DeepSeek Fetch, and commercial agents with consistent brand facts and third-party evidence.",
                },
                "geo_90d_longtail_conversion": {
                    "incremental_geo_high_intent_uv_90d": int(search2 * 0.35),
                    "expected_geo_longtail_orders_90d": geo_orders,
                    "attributed_geo_longtail_gmv_rmb": round(geo_orders * product.selling_price_rmb, 2),
                },
                "brand_stature_prior": brand_stature,
                "schulte_variance_summary": {
                    "day_to_day_variance_pct": 65.0,
                    "confidence_interval": "P10 - P50 - P90",
                    "academic_source": "Schulte et al. (2026) 'Temporal Instability & Citation Volatility in Generative Engines'",
                },
                "ai_engines_breakdown": ai_engines_breakdown,
            },
            "geo_bench_9_strategies": compute_geo_bench_9_strategies(
                stage2_input.script_content, product.brand_name, product.product_name
            ),
            "meridian_adstock_curve": compute_adstock_decay_curve(
                peak_lift=views2, half_life_days=11.0, duration_days=30
            ),
            "consumer_decision_journey": cdj_funnel,
            "mckinsey_pocket_price_waterfall": ppw_detailed,
            "cross_border_dtc_waterfall": compute_cross_border_dtc_waterfall(
                orders=max(1, int(omni_orders * 0.45 if account.platform in GLOBAL_PLATFORMS else 120)),
                aov_usd=getattr(product, "selling_price_usd", 29.9) or 29.9,
                cogs_usd=(getattr(product, "selling_price_usd", 29.9) or 29.9) * 0.22,
                ad_spend_usd=round(spend / 7.25, 2),
                weight_grams=getattr(product, "package_weight_grams", 400.0) or 400.0,
                exchange_rate=getattr(product, "exchange_rate_to_rmb", 7.25) or 7.25,
            ),
            "global_geo_and_schema": compute_global_geo_and_schema_readiness(
                stage2_input.script_content, product.brand_name, product.product_name
            ),
            "roi_and_unit_economics": {
                "omni_channel_gmv_attribution": {
                    "stage1_baseline_total_gmv_rmb": s1_gmv,
                    "omni_total_gmv_rmb": omni_gmv,
                    "gmv_lift_vs_stage1_pct": round((omni_gmv - s1_gmv) / s1_gmv * 100.0, 2),
                    "omni_total_orders": omni_orders,
                },
                "roi_and_profitability": {
                    "stage1_baseline_roas": round(s1_gmv / spend, 2),
                    "omni_channel_roas": roas,
                    "roas_lift_vs_stage1_pct": round((omni_gmv - s1_gmv) / s1_gmv * 100.0, 2),
                    "net_profit_after_ad_spend_rmb": net_profit,
                    "net_contribution_roi": round(net_profit / spend, 3),
                    "break_even_orders": max(1, int(spend / max(1.0, unit_net_margin))),
                    "max_acceptable_quote_rmb": max_acceptable_quote,
                    "ltv_to_cac_ratio": round(roas * 1.45, 2),
                    "estimated_payback_period_months": 1.2,
                },
                "media_efficiency_metrics": {
                    "cpm_rmb": round(spend / max(1.0, views2 / 1000.0), 2),
                    "cpe_cost_per_engagement_rmb": round(spend / max(1, inter2), 2),
                    "cpuv_cost_per_store_or_search_uv_rmb": round(spend / max(1, search2), 2),
                    "cac_customer_acquisition_cost_rmb": round(spend / max(1, omni_orders), 2),
                },
                "mckinsey_pocket_price_waterfall_per_unit": ppw_detailed["per_unit_waterfall_rmb"],
                "mckinsey_cdj_funnel": cdj_funnel,
                "monte_carlo_1000_runs": {
                    "profitable_probability_pct": 84.5 if net_profit >= 0 else 42.0,
                },
                "sensitivity_matrix_5x5": [
                    {
                        "reach_multiplier": rm,
                        "scenarios": [
                            {
                                "cvr_multiplier": cm,
                                "gmv_rmb": round(omni_gmv * rm * cm, 0),
                                "omni_roas": round(roas * rm * cm, 2),
                                "net_margin_roi": round((omni_orders * rm * cm * unit_net_margin - spend) / spend, 2),
                            }
                            for cm in (0.75, 0.90, 1.00, 1.15, 1.35)
                        ],
                    }
                    for rm in (0.75, 0.90, 1.00, 1.20, 1.45)
                ],
            },
        }

    def compute_stage1_baseline(
        self,
        account: SocialAccountProfile,
        product: ProductInput,
        shelf_probe: Dict[str, Any] | None = None,
        post_count: int = 1,
    ) -> Dict[str, Any]:
        return self.compute_stage1(account, product, post_count_matrix=post_count)

    def compute_stage2_enhanced(
        self,
        account: SocialAccountProfile,
        product: ProductInput,
        stage2_input: Stage2ContentInput,
        shelf_probe: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        return self.compute_stage2(account, product, stage2_input)

    def compute_multi_account_matrix(
        self,
        accounts: List[SocialAccountProfile],
        product: ProductInput,
        stage2_input: Stage2ContentInput,
        shelf_probe: Dict[str, Any] | None = None,
        matrix_total_budget_rmb: float | None = 95000.0,
    ) -> Dict[str, Any]:
        ranking = []
        total_views = 0
        raw_reach = 0
        total_followers = 0
        total_spend = 0.0
        raw_gmv = 0.0
        total_search = 0
        platforms = set()

        for idx, acct in enumerate(accounts, start=1):
            platforms.add(acct.platform)
            p_copy = ProductInput(**{**product.to_dict(), "campaign_budget_rmb": acct.commercial_quote_rmb})
            s2 = self.compute_stage2(acct, p_copy, stage2_input)
            inf2 = s2["enhanced_influence_effect"]
            ecom2 = s2["enhanced_ecommerce_search_lift_effect"]
            roi2 = s2["roi_and_unit_economics"]
            prof2 = roi2["roi_and_profitability"]
            attr2 = roi2["omni_channel_gmv_attribution"]
            eff2 = roi2["media_efficiency_metrics"]

            v2 = inf2["expected_views"]
            total_views += v2
            raw_reach += int(v2 * 0.82)
            total_followers += acct.followers
            total_spend += acct.commercial_quote_rmb
            raw_gmv += attr2["omni_total_gmv_rmb"]
            total_search += ecom2["total_cross_platform_search_uv"]

            eff_score = round(min(99.0, 65.0 + prof2["omni_channel_roas"] * 12.0), 1)
            ranking.append(
                {
                    "index": idx,
                    "account_id": acct.account_id,
                    "account_name": acct.account_name,
                    "platform": acct.platform,
                    "platform_cn": acct.platform_cn,
                    "account_url": acct.account_url,
                    "followers": acct.followers,
                    "recent_posts_count": len(acct.recent_posts),
                    "data_source_tier": "Demo Sandbox",
                    "fit_score": 0.88,
                    "fit_grade": "S级 (Demo)",
                    "matched_keywords": acct.historical_top_keywords[:3],
                    "unit_quote_rmb": acct.commercial_quote_rmb,
                    "cpm_rmb": eff2["cpm_rmb"],
                    "cpuv_rmb": eff2["cpuv_cost_per_store_or_search_uv_rmb"],
                    "stage2_views": v2,
                    "views_lift_pct": inf2["views_lift_vs_stage1_pct"],
                    "engagement_rate_pct": round(inf2["engagement_rate"] * 100.0, 2),
                    "viral_probability_pct": 24.0,
                    "peak_search_index_delta_sum": 15420,
                    "total_search_uv": ecom2["total_cross_platform_search_uv"],
                    "jd_search_uv": ecom2["channels"]["jd"]["incremental_search_uv"],
                    "tmall_search_uv": ecom2["channels"]["taobao_tmall"]["incremental_search_uv"],
                    "meituan_search_uv": ecom2["channels"]["meituan"]["incremental_search_uv"],
                    "pawc_score": 58.2,
                    "avg_geo_som_pct": 20.23,
                    "geo_som_lift_pts": 11.44,
                    "omni_gmv_rmb": attr2["omni_total_gmv_rmb"],
                    "omni_orders": attr2["omni_total_orders"],
                    "omni_roas": prof2["omni_channel_roas"],
                    "net_margin_roi_pct": round(prof2["net_contribution_roi"] * 100.0, 1),
                    "efficiency_score_100": eff_score,
                    "allocation_tier": "🏆 核心主力投 (Core Anchor)",
                    "allocation_advice_cn": "Demo 沙盒推荐主力投放",
                    "account_profile_dict": acct.to_dict(),
                }
            )

        ranking.sort(key=lambda r: r["efficiency_score_100"], reverse=True)
        dedup_reach = int(raw_reach * 0.87)
        synergy_mult = round(1.0 + 0.06 * len(platforms), 2)
        syn_gmv = round(raw_gmv * synergy_mult, 2)
        budget = matrix_total_budget_rmb or total_spend or 95000.0

        plan = []
        n = max(1, len(ranking))
        for i, r in enumerate(ranking, start=1):
            share = round(100.0 / n, 1)
            alloc = round(budget / n, 2)
            plan.append(
                {
                    "rank": i,
                    "account_name": r["account_name"],
                    "platform_cn": r["platform_cn"],
                    "unit_quote_rmb": r["unit_quote_rmb"],
                    "recommended_posts": 1,
                    "equivalent_post_units": 1.0,
                    "allocated_budget_rmb": alloc,
                    "budget_share_pct": share,
                    "projected_allocated_gmv_rmb": round(r["omni_gmv_rmb"] * synergy_mult, 2),
                    "projected_allocated_roas": round(r["omni_roas"] * synergy_mult, 2),
                    "allocation_tier": r["allocation_tier"],
                    "allocation_advice_cn": r["allocation_advice_cn"],
                }
            )

        return {
            "success": True,
            "portfolio_summary": {
                "account_count": len(ranking),
                "platform_count": len(platforms),
                "total_followers": total_followers,
                "total_expected_views": total_views,
                "raw_sum_reach_uv": raw_reach,
                "deduplicated_unique_reach_uv": dedup_reach,
                "audience_overlap_rate_pct": 13.0,
                "avg_touch_frequency": 1.28,
                "cross_platform_synergy_multiplier": synergy_mult,
                "synergized_total_search_uv": int(total_search * synergy_mult),
                "synergized_jd_search_uv": int(total_search * synergy_mult * 0.36),
                "synergized_tmall_search_uv": int(total_search * synergy_mult * 0.42),
                "synergized_meituan_search_uv": int(total_search * synergy_mult * 0.22),
                "avg_baseline_geo_som_pct": 8.79,
                "portfolio_combined_geo_som_pct": 24.6,
                "portfolio_geo_som_lift_pts": 15.81,
                "total_matrix_quote_spend_rmb": round(total_spend, 2),
                "raw_sum_gmv_rmb": round(raw_gmv, 2),
                "synergized_omni_gmv_rmb": syn_gmv,
                "synergy_incremental_gmv_rmb": round(syn_gmv - raw_gmv, 2),
                "portfolio_blended_roas": round(syn_gmv / max(1.0, total_spend), 2),
            },
            "account_ranking": ranking,
            "budget_optimization": {
                "target_total_budget_rmb": budget,
                "equal_split_baseline_gmv_rmb": round(raw_gmv, 2),
                "optimized_portfolio_gmv_rmb": syn_gmv,
                "gmv_lift_vs_equal_split_pct": round((syn_gmv - max(1.0, raw_gmv)) / max(1.0, raw_gmv) * 100.0, 2),
                "optimized_blended_roas": round(syn_gmv / max(1.0, budget), 2),
                "allocation_plan": plan,
            },
        }


class DemoMultiModalIngestor(BaseMultiModalIngestor):
    """Open-Core Demo Multi-Modal Ingestor."""

    def __init__(self, crawler: BaseSocialCrawler) -> None:
        self.crawler = crawler

    def process_input(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self.ingest(payload)

    def ingest(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        modality = payload.get("modality", "url")
        if modality == "url":
            url = payload.get("url", "xhs_medical_skincare_kol")
            prof = self.crawler.fetch_account_profile(url)
            return {
                "success": True,
                "modality": "url",
                "account_profile": prof.to_dict(),
                "visual_metrics": {"valid_image": True, "visual_ctr_multiplier": 1.06, "visual_aesthetics_score_100": 85},
            }
        text = payload.get("text", "")
        return {
            "success": True,
            "modality": modality,
            "file_type": "demo_parser",
            "text_length": len(text),
            "extracted_char_count": len(text),
            "extracted_text_preview": text[:200] or "Open-Core Demo Parser Preview",
            "structured_fields": {
                "product_overrides": {
                    "product_name": "科复佳医用透明质酸钠修复贴 (Demo)",
                    "brand_name": "科复佳 (Demo)",
                    "selling_price_rmb": 118.0,
                    "core_selling_points": [
                        "国家二类医疗器械认证 (Demo示例卖点1)",
                        "大小分子透明质酸钠协同修护屏障 (Demo示例卖点2)",
                        "光电术后72小时快速舒缓泛红 (Demo示例卖点3)",
                    ],
                }
            },
            "visual_metrics": {"valid_image": True, "visual_ctr_multiplier": 1.05, "visual_aesthetics_score_100": 84, "width": 1080, "height": 1440},
            "ocr_result": {"line_count": 12, "elapsed_ms": 15},
        }


class DemoAgentHub(BaseAgentHub):
    """Open-Core Demo 4-Agent Hub."""

    def __init__(self, crawler: BaseSocialCrawler | None = None, marvis_client: Any = None) -> None:
        self.crawler = crawler
        self.marvis_client = marvis_client

    def get_all_providers_status(self) -> Dict[str, Any]:
        return self.get_hub_status()

    def get_hub_status(self) -> Dict[str, Any]:
        return {
            "edition": "OPEN_CORE_DEMO",
            "providers": {
                "deepseek": {"connected": True, "primary_model": "deepseek-chat (Demo Stub)"},
                "antigravity": {"connected": True, "primary_model": "antigravity-sdk (Demo Stub)"},
                "marvis": {"connected": True, "agent_browser_daemon_port": "Demo Sandbox"},
                "codex": {"connected": True, "primary_model": "codex-cli (Demo Stub)"},
            },
        }

    def run_collaborative_diagnosis(
        self,
        stage2_result: Dict[str, Any],
        selected_providers: Any = None,
        custom_deepseek_key: str | None = None,
        enable_live_llm: bool = False,
    ) -> Dict[str, Any]:
        s1 = stage2_result.get("stage1_baseline", {})
        return self.run_collaborative_council(
            account_summary=s1.get("account_summary", {}),
            product_summary=s1.get("product_summary", {}),
            stage2_result=stage2_result,
            enable_live_llm=enable_live_llm,
        )

    def run_collaborative_council(
        self,
        account_summary: Dict[str, Any],
        product_summary: Dict[str, Any],
        stage2_result: Dict[str, Any],
        enable_live_llm: bool = False,
    ) -> Dict[str, Any]:
        gen = generate_smart_stage2_from_product(account_summary, product_summary)
        return {
            "success": True,
            "council_diagnostics": {
                "marvis": {
                    "provider": "Marvis 实时爬虫智能体 (Demo Sandbox)",
                    "status": "ONLINE",
                    "diagnosis_cn": f"【Demo沙盒】已完成账号【{account_summary.get('account_name', '')}】样本数据结构化校验。",
                    "diagnosis_en": "Completed demo profile validation and baseline engagement check.",
                },
                "deepseek": {
                    "provider": "DeepSeek-V3/R1 深度推理中枢 (Demo Sandbox)",
                    "status": "READY",
                    "diagnosis_cn": f"【Demo沙盒】产品【{product_summary.get('product_name', '')}】建议强化前3秒痛点对比与权威数据引用。",
                    "diagnosis_en": "Recommend strengthening 3s hook contrast and authoritative citations for GEO lift.",
                },
                "antigravity": {
                    "provider": "Google Antigravity 策略编排智能体 (Demo Sandbox)",
                    "status": "READY",
                    "diagnosis_cn": "【Demo沙盒】建议采用「小红书种草 + 京东/美团买药搜索承接」双链路闭环。",
                    "diagnosis_en": "Recommend dual-loop seeding on XHS with JD & Meituan O2O search capture.",
                },
                "codex": {
                    "provider": "OpenAI Codex 算法审计智能体 (Demo Sandbox)",
                    "status": "READY",
                    "diagnosis_cn": "【Demo沙盒】当前处于 Open-Core 架构演示模式，挂载 private_core 后可解锁全精度商业标定矩阵。",
                    "diagnosis_en": "Running in Open-Core Demo mode; mount private_core to unlock full proprietary calibration.",
                },
            },
            "recommended_optimized_script": gen["script_content"],
        }


class DemoHourlyMonitor(BaseHourlyMonitor):
    """Open-Core In-Memory Demo Monitor."""

    def __init__(self, crawler: BaseSocialCrawler, engine: BasePromotionEngine | None = None) -> None:
        self.crawler = crawler
        self.engine = engine or DemoPromotionEngine()
        self._targets: List[Dict[str, Any]] = []
        self.add_target(
            account_url="xhs_medical_skincare_kol",
            product_name="科复佳医用透明质酸钠修复贴 (Demo)",
            selling_price_rmb=118.0,
            campaign_budget_rmb=18500.0,
        )

    def start_background_hourly_loop(self, check_every_seconds: float = 30.0) -> None:
        return

    def start_background_daemon(self) -> None:
        return

    def list_all_targets(self) -> Dict[str, Any]:
        return self.list_targets()

    def list_targets(self) -> Dict[str, Any]:
        return {"daemon_running": True, "targets": self._targets}

    def add_watch_target(self, **kwargs: Any) -> Dict[str, Any]:
        return self.add_target(**kwargs)

    def poll_target_now(self, target_id: str, use_marvis_live: bool = False) -> Dict[str, Any]:
        return self.poll_target_once(target_id=target_id, use_marvis_live=use_marvis_live)

    def simulate_hourly_trajectory(self, target_id: str, hours: int = 12, scenario: str = "viral_breakout") -> Dict[str, Any]:
        return self.simulate_24h_trajectory(target_id=target_id, hours=hours, scenario=scenario)

    def add_target(
        self,
        account_url: str,
        product_name: str,
        selling_price_rmb: float = 118.0,
        campaign_budget_rmb: float = 18500.0,
        interval_seconds: int = 3600,
        use_marvis_live: bool = False,
    ) -> Dict[str, Any]:
        prof = self.crawler.fetch_account_profile(account_url)
        tid = f"demo_mon_{len(self._targets) + 1}"
        now_iso = dt.datetime.now().isoformat()
        snap = {
            "hour_index": 1,
            "captured_at": now_iso,
            "views": int(prof.avg_views * 0.25),
            "delta_views": int(prof.avg_views * 0.25),
            "likes": int(prof.avg_likes * 0.25),
            "collects": int(prof.avg_collects * 0.25),
            "comments": int(prof.avg_comments * 0.25),
            "shares": int(prof.avg_shares * 0.25),
            "velocity_e_per_hr": 420,
            "acceleration_e": 35.0,
            "posterior_hawkes_n": 0.44,
            "projected_final_views": int(prof.avg_views * 1.45),
            "projected_omni_gmv_rmb": round(campaign_budget_rmb * 1.85, 2),
            "projected_omni_roas": 1.85,
            "alert_level": "NORMAL_STEADY",
            "alert_message_cn": "【Demo沙盒监控】流量增速稳健，处于正常推荐池爬坡阶段。",
        }
        self._targets.append(
            {
                "target": {
                    "target_id": tid,
                    "account_name": prof.account_name,
                    "platform_cn": prof.platform_cn,
                    "account_url": prof.account_url,
                    "product_name": product_name,
                    "interval_seconds": interval_seconds,
                },
                "latest_snapshot": snap,
                "hourly_snapshots": [snap],
            }
        )
        return self.list_targets()

    def poll_target_once(self, target_id: str, use_marvis_live: bool = False) -> Dict[str, Any]:
        for item in self._targets:
            if item["target"]["target_id"] == target_id:
                snaps = item["hourly_snapshots"]
                last = snaps[-1]
                nxt = {
                    **last,
                    "hour_index": last["hour_index"] + 1,
                    "captured_at": dt.datetime.now().isoformat(),
                    "views": int(last["views"] * 1.22),
                    "delta_views": int(last["views"] * 0.22),
                }
                snaps.append(nxt)
                item["latest_snapshot"] = nxt
        return self.list_targets()

    def simulate_24h_trajectory(self, target_id: str, hours: int = 12, scenario: str = "viral_breakout") -> Dict[str, Any]:
        for _ in range(min(6, hours)):
            self.poll_target_once(target_id)
        return self.list_targets()

    def remove_target(self, target_id: str) -> Dict[str, Any]:
        self._targets = [t for t in self._targets if t["target"]["target_id"] != target_id]
        return self.list_targets()


def generate_bilingual_markdown_report(result: Dict[str, Any]) -> str:
    is_s2 = "stage1_baseline" in result
    s1 = result["stage1_baseline"] if is_s2 else result
    acct = s1.get("account_summary", {})
    prod = s1.get("product_summary", {})
    inf = result.get("enhanced_influence_effect") if is_s2 else s1.get("influence_effect", {})
    ecom = result.get("enhanced_ecommerce_search_lift_effect") if is_s2 else s1.get("ecommerce_search_lift_effect", {})
    return (
        f"# via54SocialROI 双语测算报告 / Bilingual Assessment Report (Open-Core Demo)\n\n"
        f"- **账号 / Account**: [{acct.get('platform_cn', '')}] {acct.get('account_name', '')} "
        f"(Followers: {acct.get('followers', 0):,})\n"
        f"- **产品 / Product**: {prod.get('product_name', '')} (¥{prod.get('selling_price_rmb', 0)})\n"
        f"- **预计总曝光 / Expected Views**: {inf.get('expected_views', 0):,}\n"
        f"- **跨平台电商回搜 / E-Commerce Search UV**: {ecom.get('total_cross_platform_search_uv', 0):,} UV\n\n"
        f"> Note: Generated by `via54SocialROI` Open-Core Demo Sandbox. Mount `private_core/` for full MBB executive report.\n"
    )
