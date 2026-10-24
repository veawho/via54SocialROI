# -*- coding: utf-8 -*-
"""
via54SocialROI — Abstract System Architecture Interfaces (Open-Core SDK)
全平台社媒推广影响力、电商回搜、GEO与ROI测算系统 — 抽象架构接口层

Architecture Layers / 五层架构定义:
1. BaseSocialCrawler: Multi-platform KOL/KOC profile & historical post ingestion interface.
2. BaseMultiModalIngestor: 5-Modal input adapter (URL / Text / Screenshot / File / Image).
3. BasePromotionEngine: Dual-Stage (Stage 1 Baseline -> Stage 2 Enhanced) & Multi-Account Matrix calculator.
4. BaseAgentHub: Multi-Agent (DeepSeek / Antigravity / Marvis / Codex) diagnostic council interface.
5. BaseHourlyMonitor: Recurring post-publication velocity & Hawkes cascade tracking interface.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List

from core.schemas import ProductInput, SocialAccountProfile, Stage2ContentInput


class BaseSocialCrawler(ABC):
    """Layer 1: Social Media Account & Post Ingestion Interface."""

    @abstractmethod
    def fetch_account_profile(
        self,
        account_url_or_key: str,
        platform_override: str | None = None,
        use_marvis_live: bool = False,
        custom_overrides: Dict[str, Any] | None = None,
    ) -> SocialAccountProfile:
        """Resolve a social media URL or preset key into a standardized SocialAccountProfile."""


class BaseMultiModalIngestor(ABC):
    """Layer 2: 5-Modal Unified Ingestion Interface (URL / Text / Screenshot / File / Image)."""

    @abstractmethod
    def ingest(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Parse multi-modal input into structured account, product, and Stage 2 overrides."""


class BasePromotionEngine(ABC):
    """Layer 3: Dual-Stage Social Influence, E-Commerce Spillover, GEO & ROI Calculation Engine."""

    @abstractmethod
    def compute_stage1(
        self,
        account: SocialAccountProfile,
        product: ProductInput,
        post_count_matrix: int = 1,
    ) -> Dict[str, Any]:
        """Stage 1: Compute baseline influence, search index lift, and e-commerce spillover from account + product."""

    @abstractmethod
    def compute_stage2(
        self,
        account: SocialAccountProfile,
        product: ProductInput,
        stage2_input: Stage2ContentInput,
    ) -> Dict[str, Any]:
        """Stage 2: Compute full influence, search index, e-commerce, 8-LLM GEO SoM, and unit economics ROI."""

    @abstractmethod
    def compute_multi_account_matrix(
        self,
        accounts: List[SocialAccountProfile],
        product: ProductInput,
        stage2_input: Stage2ContentInput,
        matrix_total_budget_rmb: float = 0.0,
    ) -> Dict[str, Any]:
        """Compute cross-platform multi-account matrix deduplicated reach, synergy, and optimal budget split."""


class BaseAgentHub(ABC):
    """Layer 4: 4-Agent Collaborative Diagnostic Council Interface."""

    @abstractmethod
    def get_hub_status(self) -> Dict[str, Any]:
        """Return connectivity status of DeepSeek, Antigravity, Marvis, and Codex providers."""

    @abstractmethod
    def run_collaborative_council(
        self,
        account_summary: Dict[str, Any],
        product_summary: Dict[str, Any],
        stage2_result: Dict[str, Any],
        enable_live_llm: bool = False,
    ) -> Dict[str, Any]:
        """Synthesize multi-agent campaign diagnostics and high-GEO script recommendations."""


class BaseHourlyMonitor(ABC):
    """Layer 5: Hourly Recurring Account & Post Velocity Monitor Interface."""

    @abstractmethod
    def list_targets(self) -> Dict[str, Any]:
        """List all monitored social accounts and their hourly velocity snapshots."""
