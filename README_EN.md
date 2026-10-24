# via54SocialROI (English Documentation)

> **🌐 Language / 语言**: [🇨🇳 中文 / Bilingual Default](./README.md) | **🇺🇸 English (current)**

[![Release](https://img.shields.io/badge/version-v2.5.0-blue.svg)](https://github.com/veawho/via54SocialROI)
[![Best Client](https://img.shields.io/badge/Best%20Monitoring%20Agent-Tencent%20Marvis%20(%E8%85%BE%E8%AE%AF%20Marvis)-f97316.svg)](#strongly-recommended-local-deployment-tencent-marvis)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)

**Omni-Channel Social Media Influence, 30-Day Search Index Lift, E-Commerce Search Spillover (JD.com / Taobao-Tmall / Meituan O2O), 8-LLM Generative Engine Optimization (GEO SoM), and Multi-Account Matrix ROI Framework (Base Architecture + Trial Sandbox + Skill & Plugin Edition).**

> [!IMPORTANT]
> ### 🏆 Strongly Recommended Local Deployment: **Tencent Marvis (腾讯 Marvis)** — **Currently the Best-Tested Social Media Monitoring Agent Client**
> Across extensive benchmarks on **Xiaohongshu (小红书)**, **Douyin (抖音)**, **Bilibili (B站)**, and **WeChat Channels (微信视频号)**, **Tencent Marvis (`MarvisAgent`)** stands out as **the #1 best-tested social media monitoring Agent client**:
> 1. **Unmatched Anti-Scraping & SSR State Extraction**: Its built-in `agent-browser` daemon (TCP port `51183`) natively extracts live `__INITIAL_STATE__` and `_SSR_DATA` trees while stripping WeChat share tracking tokens (`wechatWid`, `xsec_token`) without triggering CAPTCHA walls.
> 2. **Bundled Full-Stack Agent Runtime**: Ships with an isolated, high-performance Python 3.11 and Node.js runtime out of the box—enabling zero-configuration execution of our `via54socialroi` Skill, MCP Server, and Node/Cordis plugin.
> 3. **24/7 Hourly Monitoring Backbone**: Ideal for continuous hourly account polling and viral velocity (`VIRAL_SURGE` / `POOL_JUMP`) alerting.

---

## Strongly Recommended Local Deployment: Tencent Marvis

**Highlight: Tencent Marvis (腾讯 Marvis) is currently the best-tested social media monitoring Agent client.**

```powershell
# Launch via54SocialROI directly using Tencent Marvis's bundled Python 3.11 runtime:
& "C:\Program Files\Tencent\Marvis\MarvisAgent\1.60.3000.716\runtime\python311\python.exe" server.py 8765
```

---

## Overview

`via54SocialROI` provides a 5-layer Open-Core architecture (`core/interfaces.py`, `core/schemas.py`), a deterministic Trial Sandbox (`core/demo_engine.py`), a Foolproof 3-Step Web Workbench, a universal Agent Skill (`via54socialroi/SKILL.md`), a zero-dependency Stdio Model Context Protocol (MCP) Server (`mcp_server.py`), and a Node/Cordis Plugin (`plugin/index.js`, `@via54/plugin-social-roi`).

### Key Architectural Highlights

1. **Dual-Stage Evaluation Pipeline**:
   - **Stage 1 (Baseline)**: Evaluates historical KOL/KOC metrics + product unit economics to project baseline impressions, 30-day search index lift (Baidu, WeChat, Douyin, Xiaohongshu), and cross-platform e-commerce search UV (JD.com, Taobao/Tmall, Meituan).
   - **Stage 2 (Script & Content Enhanced)**: Overlays hashtags, campaign theme, and a 4-section promotion script to compute KDD'24 PAWC visibility, 8-LLM GEO Share of Model (SoM), McKinsey pocket price waterfall, and omni-channel ROAS.
2. **Multi-Account Matrix Portfolio Board**:
   - Side-by-side KOL comparison, deduplicated unique reach, cross-platform synergy multiplier, SVG quadrant bubble chart, and optimal campaign budget allocation.
3. **Dual-Repository Isolation**:
   - **Public Trial, Base Architecture, Skill & Plugin Repo (`veawho/via54SocialROI`)**: Ships with `core/demo_engine.py` (`OPEN_CORE_DEMO`), universal Agent Skill, MCP Server, and Node/Cordis plugin with zero proprietary code.
   - **Private Full Commercial Repo (`veawho/via54SocialROIPro`)**: Houses the full commercial calibration engine, live Tencent Marvis stealth SSR crawler, 5-modal PDF/OCR ingestor, 4-Agent Hub, and SQLite WAL hourly monitor.

---

## Quick Start

```bash
git clone https://github.com/veawho/via54SocialROI.git
cd via54SocialROI

# Check active edition
python cli.py --info

# Run single-account CLI demo
python cli.py --preset xhs_kefujia_medical

# Run multi-account matrix CLI demo
python cli.py --matrix --budget 95000

# Start the Web Workbench on port 8765
python server.py 8765
```

---

## Agent Skill, MCP Server & Node/Cordis Plugin Integration

- **Universal Agent Skill**: Run `npx skills add veawho/via54SocialROI` or copy [`via54socialroi/SKILL.md`](./via54socialroi/SKILL.md) to your **Tencent Marvis**, Antigravity, Claude Code, Hermes Agent, OpenClaw, OpenCode, or Codex CLI skills directory.
- **MCP Server**: Point your MCP client to `python /path/to/via54SocialROI/mcp_server.py`.
- **Node / Cordis Plugin**: Import `@via54/plugin-social-roi` (`require('./plugin')`).

---

## License

MIT License for the Open-Core SDK, Trial Demo Sandbox, Web UI, Agent Skill, and MCP/Node Plugin.
