# Changelog / 版本变更记录

## [v2.8.0] - 2026-11-04 (REA 重构与工业级产品体验升级 / REA Architecture & UX Polish)
- **KDD 2024 GEO-bench 9-Strategy Content Evaluator**: Integrated compute_geo_bench_9_strategies scoring content against 9 empirical citation levers (Authoritative tone, Stats, Citations, Quotations, BLUF structure, Technical terms, Fluency, USPs, Comparison readiness) with 0-100 composite score and actionable suggestions.
- **Google Meridian Adstock 30-Day Half-Life Decay Curve**: Integrated compute_adstock_decay_curve with (t) = S_0 \cdot 2^{-t / 11}$, cumulative AUC calculation, and bi-weekly content refresh guidance.
- **Interactive Sensitivity & What-If Simulation Drawer**: Added #interactiveSensitivityBox in Tab 5 with dynamic sliders for budget, price, and repeat purchase rates, calling /api/simulate/sensitivity for millisecond-level KPI updates.
- **Excel-Grade CSV (BOM-encoded \ufeff), JSON & PDF Print Exports**: Added POST /api/export/csv, POST /api/export/json, and executive print CSS styling.
- **12/12 Automated Tests Passed**: Expanded 	ests/test_demo.py from 10 to 12 tests, verifying 9-strategy GEO-bench, Meridian adstock decay, interactive sensitivity, and CSV exports (100% PASS).
- **Benchmark REA Alignment**: Synthesized best patterns from NanmiCoder/MediaCrawler, google/meridian, pymc-marketing, and KDD 2024 GEO-bench.

## [v2.7.0] - 2026-11-04
- **Kumar et al. (2026) Brand-Stature Ladder Prior**: Embedded empirical bayesian baseline priors across Household Name (73%), Established Challenger (44%), and Emerging Niche (11%) tiers into open-core demo engine and UI.
- **Schulte et al. (2026) Stochastic AI Citation Variance**: Embedded 65% day-to-day volatility modeling and computed 8-LLM GEO P10 / P50 / P90 confidence interval bands.
- **McKinsey Consumer Decision Journey (CDJ) 4-Stage Funnel**: Embedded 4-stage non-linear decision loop (Initial Consideration $\to$ Active Evaluation $\to$ Moment of Purchase / Closure $\to$ Postpurchase Loyalty Loop) with repeat order GMV multiplier.
- **McKinsey Pocket Price Waterfall & 1% Pricing Leverage Law**: Embedded Marn & Rosiello waterfall leakage deduction (MSRP $\to$ Promotional Discount $\to$ Platform Commission $\to$ Fulfillment/Return $\to$ Net Pocket Price) and real-time 1% pricing leverage multiplier calculation.
- **Dynamic Tencent Marvis Version Detection**: Fully auto-detects `1.60.3300.765+` directory layout and node runtime without hardcoded version strings.
- **10/10 Automated Tests Passed**: Complete verification of demo math, schema contracts, MCP protocol, and leak-free IP protection.

## [v2.4.0] - 2026-10-24
- **Foolproof 3-Step Web Workbench (`static/index.html`)**: Progressive disclosure UI with One-Glance Plain-Language Decision Verdict Card (`#foolproofVerdictCard`) and Simple/Expert mode toggle.
- **Multi-Account Matrix Portfolio Board**: Cross-platform KOL comparison, Sainsbury deduplicated reach, cross-platform synergy multiplier, quadrant SVG bubble chart, and optimal budget allocator.
- **Open-Core Dual-Tier Loader (`core/__init__.py`)**: Seamless runtime switching between `PRO_PRIVATE_CORE` (local private core) and `OPEN_CORE_DEMO` (public GitHub sandbox).
- **Universal Agent Skill & MCP Server**: Added `via54socialroi/SKILL.md`, `mcp_server.py`, `cli.py`, and `plugin.json`.
