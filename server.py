# -*- coding: utf-8 -*-
"""
HTTP REST API & Web Workbench Server for Omni-Channel Social Media Promotion,
E-Commerce Search Lift (JD / Taobao-Tmall / Meituan), GEO & ROI Calculator
全平台社媒推广影响力、指数提升、电商回搜、GEO与ROI综合测算系统 Web 服务端
"""

from __future__ import annotations

import json
import os
import sys
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict
from urllib.parse import urlparse

from core import (
    EDITION,
    HAS_PRIVATE_CORE,
    KB_EMPIRICAL_PROFILES,
    HourlyAccountMonitor,
    MarvisSocialCrawler,
    MultiModalIngestor,
    OmniSocialPromotionEngine,
    ProductInput,
    Stage2ContentInput,
    UnifiedAgentHub,
    generate_bilingual_markdown_report,
    generate_smart_stage2_from_product,
)

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

CRAWLER = MarvisSocialCrawler()
ENGINE = OmniSocialPromotionEngine()
INGESTOR = MultiModalIngestor(crawler=CRAWLER)
AGENT_HUB = UnifiedAgentHub(marvis_client=CRAWLER.daemon_client)
MONITOR = HourlyAccountMonitor(crawler=CRAWLER)
MONITOR.start_background_hourly_loop(check_every_seconds=30.0)

# Preset full campaign scenarios (Stage 1 + Stage 2) grounded in local Knowledge Base
PRESET_SCENARIOS: Dict[str, Dict[str, Any]] = {
    "xhs_kefujia_medical": {
        "preset_id": "xhs_kefujia_medical",
        "title_cn": "案例1：小红书三甲皮肤科医生 × 科复佳二类械字号医用修复贴（光电术后/敏肌）",
        "title_en": "Case 1: Xiaohongshu Derma KOL × Kefujia Class-II Medical Dressing",
        "account_key": "xhs_medical_skincare_kol",
        "account_url": "https://www.xiaohongshu.com/user/profile/64a8b91c000000001203d9f1",
        "product": {
            "product_name": "科复佳医用透明质酸钠修复贴 (Kefujia Class-II Medical Dressing)",
            "brand_name": "科复佳 (Kefujia)",
            "category": "医疗器械/医用敷料/敏肌修护 (Class-II Medical Skincare)",
            "msrp_rmb": 148.0,
            "selling_price_rmb": 118.0,
            "cogs_rate": 0.22,
            "gross_margin_rate": 0.78,
            "platform_commission_rate": 0.05,
            "fulfillment_and_return_rate": 0.08,
            "repeat_purchase_rate_annual": 0.36,
            "Repeat_orders_per_buyer": 2.5,
            "core_selling_points": [
                "国家二类医疗器械认证 (国械注准)",
                "高纯度医用透明质酸钠+重组胶原蛋白协同修护",
                "光电项目术后/换季屏障受损72小时褪红修护",
                "无激素无酒精无香精，三甲医院皮肤科同款"
            ],
            "target_audience": "22-38岁医美术后修护、敏感肌泛红干痒、痘印疤痕护理人群",
            "primary_ecommerce_focus": ["jd", "taobao_tmall", "meituan"],
            "campaign_budget_rmb": 18500.0
        },
        "stage2": {
            "topics_hashtags": ["#医用敷料怎么选", "#光电术后修护", "#二类械字号", "#敏感肌自救指南", "#科复佳修复贴"],
            "campaign_theme": "光子/水光术后黄金72小时科学修护：认准国械注准二类械字号，告别盲目敷面膜反黑烂脸",
            "cdj_stage": "Active Evaluation & Urgent O2O Trigger (主动评估比价 + 痛点即时触发)",
            "script_content": (
                "【黄金前3秒钩子】做完光子嫩肤或换季烂脸，千万别乱敷普通妆字号面膜！十个敷错九个反黑敏感！\n"
                "【痛点与权威背书】《中国皮肤屏障修护临床专家共识》明确指出：医美术后角质层微通道开放，必须使用无菌级国家二类医疗器械敷料。\n"
                "【核心数据与参数对比】我们实测对比了市面5款热门敷料（见01:20对比表）：科复佳医用透明质酸钠修复贴（注册证号：国械注准2023214XXXX）"
                "采用大小分子透明质酸复配，临床观察显示连续敷用72小时，泛红面积下降42.6%，经皮水分流失率（TEWL）降低35.8%，且0香精0酒精0防腐剂。\n"
                "【多渠道搜词与转化锚点】日常囤货直接去【京东自营大药房】或【天猫官方旗舰店】搜“科复佳医用修复贴”，认准盒身蓝白二类械字号标识；"
                "如果刚做完项目急用，直接打开【美团买药】搜“科复佳”，附近药房30分钟闪送到家！评论区置顶已放正品核验蓝链与术后护理FAQ清单。"
            ),
            "post_count_matrix": 1,
            "include_pinned_comment_link": True,
            "account_compliance_track": "official_compliant"
        }
    },
    "douyin_aosi_eyecare_o2o": {
        "preset_id": "douyin_aosi_eyecare_o2o",
        "title_cn": "案例2：抖音眼科主任达人 × 博士伦/奥狮无防腐剂玻璃酸钠滴眼液（美团买药O2O+京东）",
        "title_en": "Case 2: Douyin Ophthalmology KOL × Bausch+Lomb / AOSI Dry Eye Drops (O2O + JD)",
        "account_key": "douyin_health_otc_kol",
        "account_url": "https://www.douyin.com/user/MS4wLjABAAAA8xK9_EyeCare_O2O_Demo",
        "product": {
            "product_name": "奥狮/博士伦 0.3%玻璃酸钠滴眼液单支无防腐剂装 (Bausch+Lomb / AOSI HA Eye Drops)",
            "brand_name": "奥狮 / 博士伦 (AOSI / Bausch+Lomb)",
            "category": "眼科OTC医药/干眼症人工泪液/隐形眼镜护理 (Ophthalmic OTC & Dry Eye)",
            "msrp_rmb": 89.0,
            "selling_price_rmb": 68.0,
            "cogs_rate": 0.24,
            "gross_margin_rate": 0.76,
            "platform_commission_rate": 0.06,
            "fulfillment_and_return_rate": 0.06,
            "repeat_purchase_rate_annual": 0.48,
            "Repeat_orders_per_buyer": 3.2,
            "core_selling_points": [
                "0.3%高浓度玻璃酸钠长效锁水润眼",
                "BFS吹灌封单支次抛不含防腐剂，隐形眼镜/美瞳可直接滴用",
                "缓解熬夜看屏干涩、异物感、术后眼表修护",
                "美团买药24小时同城药房30分钟闪送 + 京东大药房整盒囤货"
            ],
            "target_audience": "20-45岁高频用眼白领、程序员、美瞳佩戴者、干眼症及屈光术后人群",
            "primary_ecommerce_focus": ["meituan", "jd", "taobao_tmall"],
            "campaign_budget_rmb": 42000.0
        },
        "stage2": {
            "topics_hashtags": ["#干眼症自救", "#玻璃酸钠滴眼液", "#人工泪液怎么选", "#美团买药30分钟", "#眼科医生科普"],
            "campaign_theme": "每天盯屏幕10小时眼睛干涩刺痛？眼科主任教你认准无防腐剂0.3%玻璃酸钠，同城30分钟救急",
            "cdj_stage": "Urgent Symptom Trigger & O2O Instant Fulfillment (症状痛点触发 + 即时零售闪购)",
            "script_content": (
                "【黄金前3秒钩子】晚上加班或刚摘下美瞳，眼睛干涩火辣辣像进了沙子？千万别再滴含防腐剂的网红清凉眼药水了！\n"
                "【权威共识与药理】《中国干眼临床诊疗专家共识（2024）》指出：长期使用含苯扎氯铵防腐剂滴眼液会损伤眼表杯状细胞。真正科学的方案是使用不含防腐剂的玻璃酸钠人工泪液。\n"
                "【核心数据对比】实测对比显示（见00:45图表）：0.3%浓度玻璃酸钠单支次抛装，泪膜破裂时间（BUT）延长52.4%，眼表润滑持续时长提升2.1倍，单支独立无菌包装，戴着隐形眼镜也能直接滴。\n"
                "【全渠道搜词锚点】现在眼睛难受急用的朋友，直接打开【美团买药】搜“奥狮玻璃酸钠”或“博士伦玻璃酸钠”，附近药房外卖小哥28分钟送到手！办公室日常囤货去【京东大药房】或【天猫旗舰店】搜同款30支家庭装更划算！"
            ),
            "post_count_matrix": 1,
            "include_pinned_comment_link": True,
            "account_compliance_track": "official_compliant"
        }
    },
    "bili_hardcore_device_review": {
        "preset_id": "bili_hardcore_device_review",
        "title_cn": "案例3：B站百大硬核横评UP主 × 家用红蓝光修护美容仪 & 医用敷料联用套组（京东高客单）",
        "title_en": "Case 3: Bilibili Hardcore Tech UP × Home Phototherapy & Medical Dressing Kit",
        "account_key": "bilibili_tech_health_up",
        "account_url": "https://space.bilibili.com/389120456",
        "product": {
            "product_name": "科复佳医用光子冷敷修护联用礼盒 (Kefujia Pro Repair & Phototherapy Synergy Kit)",
            "brand_name": "科复佳 (Kefujia Pro)",
            "category": "高客单家用健康器械/医用修护套组 (High-AOV Medical Skincare & Device Kit)",
            "msrp_rmb": 499.0,
            "selling_price_rmb": 368.0,
            "cogs_rate": 0.26,
            "gross_margin_rate": 0.74,
            "platform_commission_rate": 0.05,
            "fulfillment_and_return_rate": 0.07,
            "repeat_purchase_rate_annual": 0.30,
            "Repeat_orders_per_buyer": 1.8,
            "core_selling_points": [
                "二类械字号高纯透明质酸钠+重组III型胶原双效矩阵",
                "第三方SGS与三甲临床双盲实测报告背书",
                "28天修护泛红敏感与痘印屏障，参数透明无智商税",
                "B站评论区置顶京东自营旗舰店专属礼盒券"
            ],
            "target_audience": "18-35岁高线城市成分参数党、理性护肤决策者、京东PLUS高客单人群",
            "primary_ecommerce_focus": ["jd", "taobao_tmall"],
            "campaign_budget_rmb": 38000.0
        },
        "stage2": {
            "topics_hashtags": ["#硬核横评", "#医用敷料实测", "#二类械字号", "#京东自营", "#智商税鉴定"],
            "campaign_theme": "【自费2万实验室横评】拆解10款热门医用修复敷料与修护套组：看懂国械注准与透皮率数据再下手",
            "cdj_stage": "Deep Rational Evaluation & Comparison (Messy Middle 深度参数比对)",
            "script_content": (
                "【黄金前3秒钩子】同样叫修护面膜，为什么有的卖19块9其实是普通妆字号糖水，有的却是三甲医院开的二类医疗器械？今天我们把10款热门产品送进实验室测个底朝天！\n"
                "【实验室实测数据】根据《YY/T 1849重组胶原蛋白行业标准》与拉曼光谱透皮检测：科复佳Pro联用套组（国械注准认证）在角质层80微米深度的有效渗透率达到64.2%，连续使用14天皮肤泛红指数（EI值）下降38.9%。\n"
                "【结构化对比表与置顶蓝链】完整10款产品的成分表、分子量分布与单片克重对比表我已经放在视频03:40处（建议截图收藏）。想要直接抄作业的同学，直接点击【评论区置顶京东自营蓝链】，或打开【京东】/【淘宝天猫】搜“科复佳官方旗舰店”领UP主专属内购补贴！"
            ),
            "post_count_matrix": 1,
            "include_pinned_comment_link": True,
            "account_compliance_track": "official_compliant"
        }
    },
    "channels_pharmacist_family": {
        "preset_id": "channels_pharmacist_family",
        "title_cn": "案例4：微信视频号执业药师 × 家庭常备硅酮疤痕凝胶+液体敷料康复箱（私域裂变+元宝GEO）",
        "title_en": "Case 4: WeChat Channels Pharmacist × Family Scar Gel & Liquid Dressing Kit",
        "account_key": "channels_family_wellness_kol",
        "account_url": "https://channels.weixin.qq.com/platform/agency/finder_user_demo_04",
        "product": {
            "product_name": "科复佳医用硅酮疤痕修复凝胶+液体创口贴家庭康复装 (Kefujia Scar Gel & Family Kit)",
            "brand_name": "科复佳 (Kefujia Family Care)",
            "category": "家庭常备二类医疗器械/疤痕与创面护理 (Family Medical Device & Scar Care)",
            "msrp_rmb": 198.0,
            "selling_price_rmb": 158.0,
            "cogs_rate": 0.21,
            "gross_margin_rate": 0.79,
            "platform_commission_rate": 0.05,
            "fulfillment_and_return_rate": 0.06,
            "repeat_purchase_rate_annual": 0.40,
            "Repeat_orders_per_buyer": 2.2,
            "core_selling_points": [
                "国家二类医疗器械医用硅酮凝胶，物理成膜锁水抑制增生",
                "剖腹产/双眼皮/烧烫伤/儿童磕碰擦伤拆线后黄金期适用",
                "温和速干不粘衣物，执业药师家庭药箱推荐",
                "微信搜一搜/京东大药房/美团买药全渠道覆盖"
            ],
            "target_audience": "30-55岁宝妈、术后康复患者、家庭药箱采购决策者",
            "primary_ecommerce_focus": ["jd", "meituan", "taobao_tmall"],
            "campaign_budget_rmb": 26000.0
        },
        "stage2": {
            "topics_hashtags": ["#家庭常备药箱", "#疤痕修复", "#硅酮凝胶", "#术后护理指南", "#执业药师推荐"],
            "campaign_theme": "家里孩子磕碰破皮、宝妈剖腹产术后怎么防留疤？执业药师教你抓住拆线后黄金90天",
            "cdj_stage": "Social Trust Endorsement & Family Repurchase (社交信任背书 + 家庭刚需储备)",
            "script_content": (
                "【黄金前3秒钩子】家里老人做完手术、宝妈剖腹产拆线，或者孩子运动磕碰掉痂后，千万别等疤痕凸起来发红发痒才后悔！\n"
                "【临床权威指南】《中国临床瘢痕防治专家共识》强调：创面愈合脱痂后的前90天是预防增生性瘢痕的黄金期，首选一线方案就是医用硅酮制剂。\n"
                "【实证数据与用法】科复佳医用硅酮疤痕凝胶（国家二类医疗器械），涂抹后30秒形成透气疏水硅氧烷保护膜，临床随访12周显示瘢痕平整度改善率达76.5%，温和水润连儿童娇嫩皮肤都能用。\n"
                "【转发背书与搜索锚点】赶紧点个红心♥转发到‘相亲相爱一家人’群备查！需要备货的朋友直接在【微信搜一搜】、【京东自营大药房】或【美团买药】搜“科复佳硅酮凝胶”，认准二类械字号正品！"
            ),
            "post_count_matrix": 1,
            "include_pinned_comment_link": True,
            "account_compliance_track": "official_compliant"
        }
    }
}


def build_product_from_dict(d: Dict[str, Any]) -> ProductInput:
    base = ProductInput()
    for k, v in (d or {}).items():
        if hasattr(base, k) and v is not None:
            setattr(base, k, v)
    return base


def build_stage2_from_dict(d: Dict[str, Any]) -> Stage2ContentInput:
    base = Stage2ContentInput()
    for k, v in (d or {}).items():
        if hasattr(base, k) and v is not None:
            setattr(base, k, v)
    return base


class CalculatorRequestHandler(BaseHTTPRequestHandler):
    """HTTP Request Handler for the Omni-Channel Social ROI & GEO Engine"""

    def log_message(self, fmt: str, *args: Any) -> None:
        # Keep console output clean
        sys.stderr.write(f"[Server] {self.address_string()} - {fmt % args}\n")

    def _send_json(self, data: Dict[str, Any], status: int = 200) -> None:
        body = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def _read_json_body(self) -> Dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            return {}
        raw = self.rfile.read(length).decode("utf-8", errors="replace")
        return json.loads(raw) if raw.strip() else {}

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path

        if path in ("/", "/index.html"):
            index_file = STATIC_DIR / "index.html"
            if not index_file.exists():
                self._send_json({"error": "index.html not found"}, status=404)
                return
            content = index_file.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return

        if path == "/api/presets":
            ok, port, status = CRAWLER.daemon_client.ensure_daemon_running()
            cdp_info = CRAWLER.daemon_client.get_cdp_bridge_info()
            self._send_json({
                "success": True,
                "marvis_status": {
                    "default_crawler": "Marvis (agent-browser TCP Daemon & marvis-browser-host CDP)",
                    "daemon_ready": ok,
                    "daemon_port": port,
                    "status_code": status,
                    "cdp_bridge_detected": bool(cdp_info),
                },
                "agents_hub_status": AGENT_HUB.get_all_providers_status(),
                "presets": PRESET_SCENARIOS,
                "kb_profiles": KB_EMPIRICAL_PROFILES,
            })
            return

        if path == "/api/agents/status":
            self._send_json({
                "success": True,
                "agents_hub_status": AGENT_HUB.get_all_providers_status(),
            })
            return

        if path == "/api/monitor/list":
            self._send_json({
                "success": True,
                "monitoring": MONITOR.list_all_targets(),
            })
            return

        self._send_json({"error": f"Unknown endpoint: {path}"}, status=404)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        try:
            payload = self._read_json_body()

            if path == "/api/crawl":
                account_url = payload.get("account_url") or payload.get("account_key") or "xhs_medical_skincare_kol"
                platform_override = payload.get("platform_override")
                custom_overrides = payload.get("account_overrides") or {}
                use_marvis_live = bool(payload.get("use_marvis_live", True))

                profile = CRAWLER.fetch_account_profile(
                    account_url=account_url,
                    platform_override=platform_override,
                    custom_overrides=custom_overrides,
                    use_marvis_live=use_marvis_live,
                )
                self._send_json({
                    "success": True,
                    "account_profile": profile.to_dict(),
                })
                return

            if path == "/api/calculate/stage1":
                account_url = payload.get("account_url") or payload.get("account_key") or "xhs_medical_skincare_kol"
                platform_override = payload.get("platform_override")
                account_overrides = payload.get("account_overrides") or {}
                use_marvis_live = bool(payload.get("use_marvis_live", False))
                post_count = int(payload.get("post_count_matrix", 1) or 1)

                profile = CRAWLER.fetch_account_profile(
                    account_url=account_url,
                    platform_override=platform_override,
                    custom_overrides=account_overrides,
                    use_marvis_live=use_marvis_live,
                )
                product = build_product_from_dict(payload.get("product") or {})
                shelf_probe = CRAWLER.probe_ecommerce_shelves(product.product_name, product.category)

                res_stage1 = ENGINE.compute_stage1_baseline(
                    account=profile,
                    product=product,
                    shelf_probe=shelf_probe,
                    post_count=post_count,
                )
                md_report = generate_bilingual_markdown_report(res_stage1)
                self._send_json({
                    "success": True,
                    "result": res_stage1,
                    "markdown_report": md_report,
                })
                return

            if path == "/api/calculate/stage2":
                account_url = payload.get("account_url") or payload.get("account_key") or "xhs_medical_skincare_kol"
                platform_override = payload.get("platform_override")
                account_overrides = payload.get("account_overrides") or {}
                use_marvis_live = bool(payload.get("use_marvis_live", False))

                profile = CRAWLER.fetch_account_profile(
                    account_url=account_url,
                    platform_override=platform_override,
                    custom_overrides=account_overrides,
                    use_marvis_live=use_marvis_live,
                )
                product = build_product_from_dict(payload.get("product") or {})
                stage2 = build_stage2_from_dict(payload.get("stage2") or {})
                shelf_probe = CRAWLER.probe_ecommerce_shelves(product.product_name, product.category)

                res_stage2 = ENGINE.compute_stage2_enhanced(
                    account=profile,
                    product=product,
                    stage2_input=stage2,
                    shelf_probe=shelf_probe,
                )
                council_res = AGENT_HUB.run_collaborative_diagnosis(
                    stage2_result=res_stage2,
                    enable_live_llm=bool(payload.get("enable_live_llm", False)),
                )
                res_stage2["agent_council"] = council_res
                md_report = generate_bilingual_markdown_report(res_stage2)
                self._send_json({
                    "success": True,
                    "result": res_stage2,
                    "markdown_report": md_report,
                })
                return

            if path == "/api/ingest/multimodal":
                ingest_res = INGESTOR.process_input(payload)
                self._send_json(ingest_res)
                return

            if path == "/api/generate/stage2_script":
                account_info = payload.get("account") or payload.get("account_overrides") or {}
                product_info = payload.get("product") or {}
                generated = generate_smart_stage2_from_product(account_info, product_info)
                self._send_json({
                    "success": True,
                    "stage2_generated": generated,
                })
                return

            if path == "/api/calculate/matrix":
                raw_specs = payload.get("accounts") or []
                use_marvis_live = bool(payload.get("use_marvis_live", False))
                profiles = []
                seen_ids = set()

                for item in raw_specs:
                    if isinstance(item, str):
                        u = item.strip()
                        if not u:
                            continue
                        prof = CRAWLER.fetch_account_profile(
                            account_url=u,
                            use_marvis_live=use_marvis_live or u.startswith("http"),
                        )
                    elif isinstance(item, dict):
                        u = str(item.get("account_url") or item.get("account_key") or "").strip()
                        overrides = item.get("custom_overrides") or item.get("account_overrides") or {}
                        prof = CRAWLER.fetch_account_profile(
                            account_url=u or "xhs_medical_skincare_kol",
                            platform_override=item.get("platform_override") or overrides.get("platform"),
                            custom_overrides=overrides,
                            use_marvis_live=bool(item.get("use_marvis_live", False)),
                        )
                    else:
                        continue
                    dedup_key = f"{prof.platform}:{prof.account_name}"
                    if dedup_key not in seen_ids:
                        seen_ids.add(dedup_key)
                        profiles.append(prof)

                if not profiles:
                    # Default matrix: current form account + 4 cross-platform benchmark KOLs
                    cur_url = payload.get("account_url") or "xhs_medical_skincare_kol"
                    cur_prof = CRAWLER.fetch_account_profile(
                        account_url=cur_url,
                        platform_override=payload.get("platform_override"),
                        custom_overrides=payload.get("account_overrides") or {},
                        use_marvis_live=False,
                    )
                    profiles.append(cur_prof)
                    seen_ids.add(f"{cur_prof.platform}:{cur_prof.account_name}")
                    for preset_key in (
                        "xhs_medical_skincare_kol",
                        "douyin_health_otc_kol",
                        "bili_hardcore_tech_review",
                        "channels_family_wellness_kol",
                    ):
                        p_prof = CRAWLER.fetch_account_profile(account_url=preset_key, use_marvis_live=False)
                        d_key = f"{p_prof.platform}:{p_prof.account_name}"
                        if d_key not in seen_ids:
                            seen_ids.add(d_key)
                            profiles.append(p_prof)

                product = build_product_from_dict(payload.get("product") or {})
                stage2 = build_stage2_from_dict(payload.get("stage2") or {})
                shelf_probe = CRAWLER.probe_ecommerce_shelves(product.product_name, product.category)
                matrix_budget = payload.get("matrix_total_budget_rmb")
                matrix_budget_val = float(matrix_budget) if (matrix_budget is not None and str(matrix_budget).strip() != "") else None

                matrix_res = ENGINE.compute_multi_account_matrix(
                    accounts=profiles,
                    product=product,
                    stage2_input=stage2,
                    shelf_probe=shelf_probe,
                    matrix_total_budget_rmb=matrix_budget_val,
                )
                self._send_json(matrix_res)
                return

            if path == "/api/agents/analyze":
                stage2_res = payload.get("stage2_result")
                if not stage2_res:
                    # Run quick stage2 calculation first
                    profile = CRAWLER.fetch_account_profile(
                        account_url=payload.get("account_url") or "xhs_medical_skincare_kol",
                        custom_overrides=payload.get("account_overrides") or {},
                        use_marvis_live=False,
                    )
                    product = build_product_from_dict(payload.get("product") or {})
                    stage2 = build_stage2_from_dict(payload.get("stage2") or {})
                    shelf_probe = CRAWLER.probe_ecommerce_shelves(product.product_name, product.category)
                    stage2_res = ENGINE.compute_stage2_enhanced(profile, product, stage2, shelf_probe)
                council = AGENT_HUB.run_collaborative_diagnosis(
                    stage2_result=stage2_res,
                    selected_providers=payload.get("providers"),
                    custom_deepseek_key=payload.get("deepseek_api_key"),
                    enable_live_llm=bool(payload.get("enable_live_llm", True)),
                )
                self._send_json(council)
                return

            if path == "/api/monitor/add":
                detail = MONITOR.add_watch_target(
                    account_url=payload.get("account_url") or "https://www.xiaohongshu.com/user/profile/64a8b91c000000001203d9f1",
                    product_name=payload.get("product_name") or "科复佳医用透明质酸钠修复贴",
                    selling_price_rmb=float(payload.get("selling_price_rmb") or 118.0),
                    campaign_budget_rmb=float(payload.get("campaign_budget_rmb") or 18500.0),
                    interval_seconds=int(payload.get("interval_seconds") or 3600),
                    use_marvis_live=bool(payload.get("use_marvis_live", True)),
                )
                self._send_json({"success": True, "detail": detail, "monitoring": MONITOR.list_all_targets()})
                return

            if path == "/api/monitor/poll":
                target_id = payload.get("target_id")
                detail = MONITOR.poll_target_now(
                    target_id=target_id,
                    use_marvis_live=bool(payload.get("use_marvis_live", True)),
                )
                self._send_json({"success": True, "detail": detail, "monitoring": MONITOR.list_all_targets()})
                return

            if path == "/api/monitor/simulate24h":
                target_id = payload.get("target_id")
                hours = int(payload.get("hours") or 12)
                scenario = payload.get("scenario") or "viral_breakout"
                detail = MONITOR.simulate_hourly_trajectory(target_id=target_id, hours=hours, scenario=scenario)
                self._send_json({"success": True, "detail": detail, "monitoring": MONITOR.list_all_targets()})
                return

            if path == "/api/monitor/remove":
                target_id = payload.get("target_id")
                mon = MONITOR.remove_target(target_id=target_id)
                self._send_json({"success": True, "monitoring": mon})
                return

            self._send_json({"error": f"Unknown POST endpoint: {path}"}, status=404)
        except Exception as exc:
            traceback.print_exc()
            self._send_json({
                "success": False,
                "error": str(exc),
                "traceback": traceback.format_exc(),
            }, status=500)


def run_server(host: str = "127.0.0.1", port: int = 8765) -> None:
    server = ThreadingHTTPServer((host, port), CalculatorRequestHandler)
    print(f"================================================================================")
    print(f"Omni-Channel Social Media ROI & GEO Calculation Workbench Running!")
    print(f"全平台社媒推广影响力、电商回搜、GEO与ROI综合测算工作台已启动: http://{host}:{port}")
    print(f"Default Crawler: Marvis (agent-browser TCP Daemon & CDP Bridge)")
    print(f"================================================================================")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    port_arg = int(os.environ.get("PORT", "8765"))
    if len(sys.argv) > 1:
        try:
            port_arg = int(sys.argv[1])
        except ValueError:
            pass
    run_server(port=port_arg)
