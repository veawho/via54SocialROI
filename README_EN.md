<div align="center">

# via54SocialROI (English Edition)

> **🌐 Language**: [Bilingual README](./README.md) · [🇨🇳 中文版](./README.zh-CN.md) · **🇺🇸 English**

[![Release](https://img.shields.io/badge/version-v2.7.0-blue.svg)](https://github.com/veawho/via54SocialROI)
[![Edition](https://img.shields.io/badge/Edition-Open--Core%20Trial%20%2B%20Skill%20%2B%20Plugin-10b981.svg)](#architecture--edition-matrix)
[![Agent Skill](https://img.shields.io/badge/Agent%20Skill-via54socialroi-8b5cf6.svg)](./via54socialroi/SKILL.md)
[![Best Client](https://img.shields.io/badge/%E6%9C%80%E4%BD%B3%E7%9B%91%E6%B5%8B%E5%AE%A2%E6%88%B7%E7%AB%AF-%E8%85%BE%E8%AE%AF%20Marvis%20(Best%20Social%20Monitoring%20Agent)-f97316.svg)](#-top-deployment-recommendation-deploy-tencent-marvis-locally)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)

**Omni-Channel Social Media Influence, 30-Day Search Index Lift, E-Commerce Spillover (JD / Tmall / Meituan), 8-LLM Generative Engine Optimization (GEO SoM), McKinsey CDJ Decision Journey & Pocket Price Waterfall Multi-Account Matrix ROI Framework (Base Architecture + Trial Sandbox + Skill & Plugin Edition)**

*Built for **Xiaohongshu (小红书)** · **Douyin (抖音)** · **Bilibili (B站)** · **WeChat Channels (微信视频号)** — Best paired with **Tencent Marvis**.*

</div>

> [!IMPORTANT]
> ### 🏆 Top Deployment Recommendation: Deploy **Tencent Marvis** Locally — **Currently the Best-Tested Social Media Monitoring Agent Client**
> - **Benchmark Verdict**: Across 100+ live integration tests on Xiaohongshu, Douyin, Bilibili, and WeChat Channels, **running Tencent Marvis locally delivers the highest scraping accuracy, steadiest anti-bot bypass, and most reliable SSR state extraction of any social media monitoring agent client tested.**
> - **Why Tencent Marvis**:
>   1. **Unrivaled Social Monitoring**: Embedded `agent-browser` daemon (port `51183`) strips tracking tokens (`wechatWid`, `xsec_token`) and extracts authentic `__INITIAL_STATE__` without captcha blockages;
>   2. **Pre-Bundled Isolated Runtime**: Bundles isolated Python 3.11 and Node.js environments with dynamic multi-version discovery (compatible with `1.60.3000` / `1.60.3300+`), running skills and MCP servers without configuration overhead;
>   3. **Hourly Monitoring Foundation**: Supports 24/7 background inspection with instant daemon wakeups.

---

## 📌 Scientific Foundations & SOTA Marketing Canon Upgrades

`via54SocialROI v2.7.0` integrates rigorous marketing science and 2026 SOTA GEO research:

1. **Brand-Stature Ladder Prior (Kumar et al. 2026)**:
   - Employs empirical Bayesian prior calibration across brand stature tiers: **Household Name (73%)**, **Established Challenger (44%)**, and **Emerging Niche (11%)**.
2. **Stochastic AI Citation Variance (Schulte et al. 2026)**:
   - Models ~65% day-to-day volatility across 8 major AI search engines (DeepSeek, Doubao, Yuanbao, Kimi, ChatGPT, Claude, Perplexity, Gemini) with rigorous **P10 (conservative) - P50 (median) - P90 (optimistic)** confidence interval bands.
3. **McKinsey Consumer Decision Journey (CDJ)**:
   - Replaces linear AIDA funnels with a 4-stage non-linear loop: **Initial Consideration $\to$ Active Evaluation $\to$ Moment of Purchase $\to$ Postpurchase Loyalty Loop**, accurately forecasting repeat order customer lifetime value.
4. **McKinsey Pocket Price Waterfall & 1% Pricing Leverage Law (Marn & Rosiello)**:
   - Deducts promotional discounts, platform commissions, and fulfillment leakage from MSRP to obtain true pocket net margin, and quantifies the exact profit leverage from a 1% price increase.

---

## 🏗️ Architecture & Edition Matrix

| Capability Dimension | 🌍 Open-Core Trial Sandbox (`veawho/via54SocialROI`) | 🔒 Private Full Commercial Edition (`veawho/via54SocialROIPro`) |
| :--- | :--- | :--- |
| **5-Layer System Architecture (`core/interfaces.py`)** | ✅ **Fully Open Source** (Strongly typed contracts & ABCs) | ✅ Identical architecture contract with commercial implementation |
| **Foolproof 3-Step Web Workbench (`static/index.html`)** | ✅ **Fully Open Source** (Plain-language verdict, CDJ, waterfall, GEO bands) | ✅ Identical UI unlocking live anti-bot extraction & full precision |
| **Multi-Account Matrix Board** | ✅ **Fully Open Source** (SVG quadrant chart, comparison table, budget optimizer) | ✅ Activates full Sainsbury overlap matrix & Hill equation solver |
| **Universal Agent Skill (`via54socialroi`) & MCP** | ✅ **Fully Open Source** (Tencent Marvis / Antigravity / Claude Code) | ✅ Direct commercial kernel integration |
| **Underlying Empirical Weights & Marvis SSR Engine** | 🧪 **Deterministic Trial Sandbox (`core/demo_engine.py`)** | 🔒 **Closed-Source Private Isolation (`veawho/via54SocialROIPro`)** |

---

## 🚀 30-Second Quick Start

```bash
# 1. Clone repository
git clone https://github.com/veawho/via54SocialROI.git
cd via54SocialROI

# 2. Check engine edition
python cli.py --info

# 3. Single-account CLI evaluation
python cli.py --preset xhs_kefujia_medical

# 4. Multi-account matrix evaluation
python cli.py --matrix --budget 95000

# 5. Launch Foolproof Web Workbench
python server.py 8765
# Open in browser: http://127.0.0.1:8765
```

---

## 🧪 Running Automated Tests

```bash
python -m unittest discover -s tests -v
```

---

## 📄 License

Open-source portions are licensed under the **[MIT License](./LICENSE)**.
