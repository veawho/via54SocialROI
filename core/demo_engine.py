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
import re
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
    acct_name = account.account_name if isinstance(account, SocialAccountProfile) else account.get("account_name", "示范达人")
    p_name = product.product_name if isinstance(product, ProductInput) else product.get("product_name", "示范产品")
    b_name = product.brand_name if isinstance(product, ProductInput) else product.get("brand_name", "示范品牌")
    points = (
        product.core_selling_points
        if isinstance(product, ProductInput)
        else product.get("core_selling_points", ["核心功效卖点1", "核心功效卖点2"])
    )
    short_prod = p_name.split("(")[0].strip()
    topics = [f"#{short_prod}", f"#{b_name.split('(')[0].strip()}", "#科学评测", "#避坑指南", "#好物推荐"]
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

    def compute_stage1(
        self,
        account: SocialAccountProfile,
        product: ProductInput,
        post_count_matrix: int = 1,
    ) -> Dict[str, Any]:
        fit_score = 0.86
        fit_mult = 1.15
        views = int(account.avg_views * fit_mult * max(1, post_count_matrix))
        likes = int(account.avg_likes * fit_mult * max(1, post_count_matrix))
        collects = int(account.avg_collects * fit_mult * max(1, post_count_matrix))
        comments = int(account.avg_comments * fit_mult * max(1, post_count_matrix))
        shares = int(account.avg_shares * fit_mult * max(1, post_count_matrix))
        follows = int(account.avg_follows_gained * fit_mult * max(1, post_count_matrix))
        total_inter = likes + collects + comments + shares
        ces = likes * 1 + collects * 1 + comments * 4 + shares * 4 + follows * 8

        search_uv = int(views * 0.022)
        jd_uv = int(search_uv * 0.36)
        tmall_uv = int(search_uv * 0.42)
        mt_uv = search_uv - jd_uv - tmall_uv
        store_uv = int(search_uv * 0.58)
        orders = max(1, int(store_uv * 0.14))
        gmv = round(orders * product.selling_price_rmb, 2)

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
                "platforms": {
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
                },
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
                "channels": {
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
                },
            },
        }

    def compute_stage2(
        self,
        account: SocialAccountProfile,
        product: ProductInput,
        stage2_input: Stage2ContentInput,
    ) -> Dict[str, Any]:
        s1 = self.compute_stage1(account, product, post_count_matrix=stage2_input.post_count_matrix)
        s1_inf = s1["influence_effect"]
        s1_ecom = s1["ecommerce_search_lift_effect"]

        content_mult = 1.48
        views2 = int(s1_inf["expected_views"] * content_mult)
        inter2 = int(s1_inf["total_interactions"] * 1.56)
        bd1 = s1_inf["breakdown"]

        search2 = int(s1_ecom["total_cross_platform_search_uv"] * 1.72)
        store2 = int(search2 * 0.62)
        orders2 = max(2, int(store2 * 0.16))
        search_gmv2 = round(orders2 * product.selling_price_rmb, 2)
        direct_orders = max(1, int(orders2 * 0.35))
        geo_orders = max(1, int(orders2 * 0.22))
        omni_orders = orders2 + direct_orders + geo_orders
        omni_gmv = round(omni_orders * product.selling_price_rmb, 2)
        s1_gmv = max(1.0, float(s1_ecom["total_attributed_search_gmv_rmb"]))
        spend = max(1.0, float(product.campaign_budget_rmb))
        roas = round(omni_gmv / spend, 2)
        unit_net_margin = round(product.selling_price_rmb * (1.0 - product.cogs_rate - product.platform_commission_rate - 0.06), 2)
        net_profit = round(omni_orders * unit_net_margin - spend, 2)

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
            ("DeepSeek (V3/R1 联网搜索)", "高权重中文长文与测评结构", 9.5, 22.4),
            ("腾讯元宝 (微信公众号/视频号生态)", "微信生态与权威科普信源", 10.2, 23.8),
            ("字节豆包 (抖音/头条百科全网检索)", "短视频口播字幕与高赞评论", 11.0, 24.5),
            ("Kimi 智能助手 (长上下文深度检索)", "多维参数对比表与注册证号", 8.8, 20.6),
            ("百度文心一言 (百度百家/百科生态)", "结构化问答与专家共识引文", 9.0, 19.8),
            ("阿里通义千问 (淘天电商消费指南)", "真实买家测评与电商搜词锚点", 8.5, 19.2),
            ("Perplexity AI (全球学术与消费检索)", "统计百分比与临床文献引用", 6.5, 15.4),
            ("ChatGPT Search (OpenAI 实时联网)", "清晰FAQ与权威品牌实体", 6.8, 16.1),
        ]

        return {
            "stage": "Stage 2 Full Enhanced (Open-Core Demo Sandbox)",
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
                "geo_90d_longtail_conversion": {
                    "incremental_geo_high_intent_uv_90d": int(search2 * 0.35),
                    "expected_geo_longtail_orders_90d": geo_orders,
                    "attributed_geo_longtail_gmv_rmb": round(geo_orders * product.selling_price_rmb, 2),
                },
                "ai_engines_breakdown": [
                    {
                        "name_cn": name,
                        "rag_source_affinity": aff,
                        "baseline_som_pct": b_som,
                        "post_campaign_som_pct": p_som,
                        "som_lift_percentage_points": round(p_som - b_som, 2),
                        "top1_recommendation_rate": round(p_som / 100.0 * 0.62, 3),
                        "citation_adoption_rate": round(p_som / 100.0 * 0.78, 3),
                    }
                    for name, aff, b_som, p_som in ai_engines
                ],
            },
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
                    "ltv_to_cac_ratio": round(roas * 1.45, 2),
                    "estimated_payback_period_months": 1.2,
                },
                "media_efficiency_metrics": {
                    "cpm_rmb": round(spend / max(1.0, views2 / 1000.0), 2),
                    "cpe_cost_per_engagement_rmb": round(spend / max(1, inter2), 2),
                    "cpuv_cost_per_store_or_search_uv_rmb": round(spend / max(1, search2), 2),
                    "cac_customer_acquisition_cost_rmb": round(spend / max(1, omni_orders), 2),
                },
                "mckinsey_pocket_price_waterfall_per_unit": {
                    "msrp_rmb": product.msrp_rmb or round(product.selling_price_rmb * 1.25, 2),
                    "promotional_discount_rmb": round((product.msrp_rmb or product.selling_price_rmb * 1.25) - product.selling_price_rmb, 2),
                    "invoice_selling_price_rmb": product.selling_price_rmb,
                    "platform_commission_rmb": round(product.selling_price_rmb * product.platform_commission_rate, 2),
                    "fulfillment_and_return_loss_rmb": round(product.selling_price_rmb * 0.06, 2),
                    "pocket_price_rmb": round(product.selling_price_rmb * (1.0 - product.platform_commission_rate - 0.06), 2),
                    "unit_cogs_rmb": round(product.selling_price_rmb * product.cogs_rate, 2),
                    "unit_net_contribution_margin_rmb": unit_net_margin,
                    "unit_net_contribution_margin_pct": round(unit_net_margin / max(1.0, product.selling_price_rmb) * 100.0, 1),
                },
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
