# -*- coding: utf-8 -*-
"""
via54SocialROI — Public Data Schemas & Domain Models (Open-Core Architecture)
全平台社媒推广影响力、电商回搜、GEO与ROI测算系统 — 公开数据结构与领域模型定义
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List


@dataclass
class HistoricalPost:
    """Single historical post / note snapshot on a social platform."""
    post_id: str
    title: str
    publish_date: str
    views: int
    likes: int
    collects: int
    comments: int
    shares: int
    follows_gained: int = 0
    retention_3s: float = 0.65
    completion_rate: float = 0.45
    keywords: List[str] = field(default_factory=list)
    is_viral: bool = False


@dataclass
class SocialAccountProfile:
    """Standardized social media KOL/KOC account profile across XHS / Douyin / Bilibili / Channels."""
    account_id: str
    account_name: str
    platform: str  # "xiaohongshu" | "douyin" | "bilibili" | "wechat_channels"
    platform_cn: str
    account_url: str
    followers: int
    vertical_category: str
    avg_views: float
    median_views: float
    std_views: float
    avg_likes: float
    avg_collects: float
    avg_comments: float
    avg_shares: float
    avg_follows_gained: float
    avg_3s_retention: float
    avg_completion_rate: float
    historical_viral_rate: float
    audience_female_ratio: float
    audience_tier1_2_city_ratio: float
    historical_top_keywords: List[str]
    commercial_quote_rmb: float
    recent_posts: List[HistoricalPost] = field(default_factory=list)
    crawl_metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ProductInput:
    """Stage 1 product & unit economics input specification."""
    product_name: str = "科复佳医用透明质酸钠修复贴 (Demo)"
    brand_name: str = "科复佳 (Demo)"
    category: str = "医疗器械/医用敷料/敏肌修护"
    selling_price_rmb: float = 118.0
    msrp_rmb: float = 148.0
    cogs_rate: float = 0.25
    gross_margin_rate: float = 0.68
    platform_commission_rate: float = 0.05
    fulfillment_and_return_loss_rate: float = 0.08
    campaign_budget_rmb: float = 15000.0
    core_selling_points: List[str] = field(default_factory=list)
    target_audience: str = "一二线城市22-40岁品质消费与健康管理人群"
    repeat_purchase_rate_annual: float = 0.32
    Repeat_orders_per_buyer: float = 2.2
    brand_baseline_search_daily: Dict[str, int] = field(
        default_factory=lambda: {
            "baidu_index": 1850,
            "wechat_index": 42000,
            "douyin_index": 26500,
            "xiaohongshu_index": 9800,
        }
    )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Stage2ContentInput:
    """Stage 2 content enhancement specification (Hashtags + Campaign Theme + Promotion Script)."""
    topics_hashtags: List[str] = field(default_factory=list)
    campaign_theme: str = ""
    script_content: str = ""
    post_count_matrix: int = 1
    account_compliance_track: str = "official_compliant"
    include_pinned_comment_link: bool = True
    visual_ctr_multiplier: float = 1.0
    visual_aesthetics_score: float = 82.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
