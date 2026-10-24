# via54SocialROI (English Documentation)

> **🌐 Language / 语言**: [🇨🇳 中文 / Bilingual Default](./README.md) | **🇺🇸 English (current)**

[![CI](https://github.com/veawho/via54SocialROI/actions/workflows/ci.yml/badge.svg)](https://github.com/veawho/via54SocialROI/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)

**Omni-Channel Social Media Influence, 30-Day Search Index Lift, E-Commerce Search Spillover (JD.com / Taobao-Tmall / Meituan O2O), 8-LLM Generative Engine Optimization (GEO SoM), and Multi-Account Matrix ROI Framework.**

---

## Overview

`via54SocialROI` provides a 5-layer Open-Core architecture, a Foolproof 3-Step Web Workbench, a universal Agent Skill (`via54socialroi`), and a zero-dependency Stdio Model Context Protocol (MCP) Server for evaluating social media seeding campaigns across **Xiaohongshu**, **Douyin**, **Bilibili**, and **WeChat Channels**.

### Key Architectural Highlights

1. **Dual-Stage Evaluation Pipeline**:
   - **Stage 1 (Baseline)**: Evaluates historical KOL/KOC metrics + product unit economics to project baseline impressions, 30-day search index lift (Baidu, WeChat, Douyin, Xiaohongshu), and cross-platform e-commerce search UV (JD.com, Taobao/Tmall, Meituan).
   - **Stage 2 (Script & Content Enhanced)**: Overlays hashtags, campaign theme, and a 4-section promotion script to compute KDD'24 PAWC visibility, 8-LLM GEO Share of Model (SoM), McKinsey pocket price waterfall, and omni-channel ROAS.
2. **Multi-Account Matrix Portfolio Board**:
   - Side-by-side KOL comparison, deduplicated unique reach, cross-platform synergy multiplier, SVG quadrant bubble chart, and optimal campaign budget allocation.
3. **Open-Core IP Isolation (`core/` vs. `private_core/`)**:
   - The public repository ships with `core/demo_engine.py` (`OPEN_CORE_DEMO`), allowing any developer to run the full Web UI, CLI, and MCP Server out-of-the-box with zero external dependencies.
   - Proprietary empirical calibration matrices, Marvis live stealth SSR extractors, and multi-column scanned PDF layout heuristics are isolated in `private_core/` (excluded via `.gitignore`).

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

## Agent Skill & MCP Server Integration

- **Universal Agent Skill**: Copy [`via54socialroi/SKILL.md`](./via54socialroi/SKILL.md) to your Antigravity, Claude Code, Hermes Agent, OpenClaw, OpenCode, or Codex CLI skills directory.
- **MCP Server**: Point your MCP client to `python /path/to/via54SocialROI/mcp_server.py`.

---

## License

MIT License for the Open-Core SDK, Demo Sandbox, Web UI, Agent Skill, and MCP Server. Proprietary rights reserved for `private_core/`.
