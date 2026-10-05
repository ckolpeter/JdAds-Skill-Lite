# JdAds Skill Lite v1.0.0 — 简体中文

[README](../../README.md) · [AI Ads Academy](https://www.ai-ads.academy)

京东商品／全店／新品规划、订单贡献及报表检查

本版仅支持中国大陆 CN／CNY，是离线规划与描述性报表工具。模式名称是本地工作流，不是平台 API 枚举或已验证资格。

复制 templates/brief.json 并填写已知信息，未知值保留 null。广告前订单贡献＝净收入－已知非广告成本。预算分摊只是等额试投情景，不是最佳配置。CSV 仅接受文档规定的标准字段及 metadata，不自动识别平台原始报表。

## Quick start / 快速開始

Python 3.10+; standard library only.

```bash
python3 scripts/toolkit.py plan examples/brief.synthetic.json --out-dir output/demo-plan
python3 scripts/toolkit.py validate output/demo-plan/plan.json
python3 scripts/toolkit.py analyze examples/report.csv --meta examples/report.meta.json --out-dir output/demo-report
python3 -m unittest discover -s tests -v
python3 scripts/release_gate.py
```

不登录、不保存凭证、不连接广告 API、不抓取网站、不自动发布或修改预算。PLAN_READY／ANALYSIS_READY 均需人工审核。未知成本不能当零；毛 GMV、结算收入、利润及增量不可混用。模型可能使用云端，请勿输入原始客户个人信息。

[Data contract](../../references/data-contract.md) · [Sources and verification limits](../../references/official-sources.md) · [Installation](../INSTALLATION.md) · [Development handoff](../HANDOFF.md)

Five-language onboarding only; model routing, generated content, legal compliance and live advertising are not certified. No official platform affiliation. License: Apache-2.0.
