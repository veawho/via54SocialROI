---
name: via54socialroi
description: Predict omni-channel social media campaign influence, 30-day search index lift, e-commerce search spillover (JD/Taobao-Tmall/Meituan), 8-LLM Generative Engine Optimization (GEO SoM), and multi-account matrix ROI across Xiaohongshu, Douyin, Bilibili, and WeChat Channels.
license: MIT
compatibility:
  - antigravity
  - claude-code
  - hermes-agent
  - openclaw
  - opencode
  - codex-cli
metadata:
  author: veawho
  version: 2.4.0
  repository: https://github.com/veawho/via54SocialROI
---

# via54socialroi — Omni-Channel Social ROI, E-Commerce Spillover & GEO Skill

> **中文注释**: `via54socialroi` 是面向小红书、抖音、B站、微信视频号四端种草投放的投前精算与多账号矩阵选号 Skill。支持一键评估单账号或跨平台多账号组合的曝光量、四大平台搜索指数脉冲、三大电商（京东/淘天/美团买药）回搜进店 UV、8 大生成式 AI 搜索引擎（DeepSeek/豆包/元宝/Kimi 等）GEO 推荐声量份额（SoM）及全域 ROI。

## When to Trigger

Activate `via54socialroi` when the user asks to:
1. Evaluate a social media KOL/KOC account (Xiaohongshu, Douyin, Bilibili, WeChat Channels) for promoting a specific product.
2. Estimate cross-platform e-commerce search spillover (JD.com, Taobao/Tmall, Meituan O2O) or 8-LLM GEO citation visibility from social seeding.
3. Compare multiple candidate KOL accounts side-by-side (`Multi-Account Matrix`) and optimize total campaign budget allocation.
4. Generate high-converting, KDD'24 GEO-optimized promotion scripts and hashtags tailored to a product and blogger profile.

> **中文注释**: 当用户提出“帮我算一下投这个小红书/抖音博主能带多少货”、“对比几个账号哪个性价比高”、“生成高 GEO 转化种草脚本”或“测算京东/淘宝/美团回搜 ROI”时立即触发本 Skill。

## Quick Commands (CLI & Web Workbench)

```bash
# 1. Inspect active engine edition (PRO_PRIVATE_CORE vs OPEN_CORE_DEMO)
python cli.py --info

# 2. Run single-account Stage 1 -> Stage 2 full evaluation
python cli.py --account xhs_medical_skincare_kol --product "科复佳医用透明质酸钠修复贴" --price 118 --budget 18500

# 3. Run cross-platform Multi-Account Matrix PK & optimal budget split
python cli.py --matrix --budget 95000

# 4. Launch the Foolproof 3-Step Web Workbench UI on port 8765
python server.py 8765
```

> **中文注释**: 仓库内置双模加载器（`core/__init__.py`）：公开克隆默认运行 `OPEN_CORE_DEMO` 架构演示沙盒；本机存在私有核心目录 `private_core/` 时自动挂载 `PRO_PRIVATE_CORE` 商业全精度标定引擎。

## Decision Matrix

| Scenario | Command / Endpoint | Key Output Metrics |
|---|---|---|
| Single KOL Quick Verdict | `python cli.py --account <key> --product <name> --price <rmb> --budget <rmb>` | Expected Views, JD/Tmall/Meituan Search UV, 8-LLM GEO SoM, Omni GMV & ROAS |
| Multi-Account Matrix PK | `python cli.py --matrix --budget <total_rmb>` | Sainsbury Deduplicated Reach, Cross-Platform Synergy, Efficiency Ranking, Budget Split |
| Script & Hashtag Synthesis | `POST /api/generate/stage2_script` | 5 Vertical Hashtags, Campaign Theme, 4-Section Hook+Citation+Anchor Script |
| MCP Server Integration | `python mcp_server.py` | Exposes `social_roi_evaluate_single`, `social_roi_evaluate_matrix`, `social_roi_generate_script` |

> **中文注释**: 单号评估看 `social_roi_evaluate_single`，多号比价与分钱看 `social_roi_evaluate_matrix`，自动写种草脚本看 `social_roi_generate_script`。

## Common Pitfalls

1. **Live Iron Rule (铁律 #1)**: Every conclusion MUST be backed by at least 2 live tool outputs (`python cli.py --info`, `curl -s http://127.0.0.1:8765/api/presets`, or `python -m unittest discover -s tests`). Never guess ROI metrics from memory without executing the engine.
2. **Core IP Isolation**: Never commit or upload `private_core/` or `*_pro.py` files to public Git remotes. Always verify with `git status --ignored` before pushing.
3. **Budget Lock**: When evaluating custom campaign budgets, pass `--budget <rmb>` explicitly so the KOL's default rate card does not overwrite user-specified spend.

> **中文注释**: 铁律第一条：任何投前测算结论必须通过真实执行 `cli.py` 或 REST API 获取输出，严禁凭空臆造数字；提交 GitHub 前必须确认 `private_core/` 处于 `.gitignore` 保护下。

## Verification Checklist

- [ ] `python cli.py --info` returns valid JSON with `"project": "via54SocialROI"`.
- [ ] `python cli.py --matrix --budget 95000` outputs ranked KOL portfolio and budget allocation plan.
- [ ] `python -m unittest discover -s tests -v` passes 100% of unit and MCP protocol checks.
