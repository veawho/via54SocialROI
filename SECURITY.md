# Security & IP Isolation Policy / 安全与核心资产隔离策略

## Core IP Protection (`private_core/`)
- All proprietary empirical calibration matrices, Marvis stealth SSR anti-detection extractors, and multi-column scanned PDF layout analyzers are isolated in `private_core/` and excluded via `.gitignore`.
- Before pushing any commit to GitHub, run `python -m unittest discover -s tests -v` and verify `git status` to ensure zero files from `private_core/` or personal tokens (`wechatWid`, `xsec_token`, API keys) are staged.

## Reporting a Vulnerability
Please report security issues via GitHub Issues or directly to `@veawho`.
