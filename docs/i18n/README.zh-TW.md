# JdAds Skill Lite v1.0.0 — 繁體中文

[README](../../README.md) · [AI Ads Academy](https://www.ai-ads.academy)

京東商品／全店／新品規劃、訂單貢獻及報表檢查

本版僅支援中國大陸 CN／CNY，為離線規劃與描述性報表工具。模式名稱是本地工作流，不是平台 API 枚舉或已核驗資格。

複製 templates/brief.json 並填寫已知資料，未知值保留 null。廣告前訂單貢獻＝淨收入－已知非廣告成本。試投預算為等額會計情境，不是最佳配置。CSV 只接受文件列出的標準欄位及 metadata，不自動辨識原始平台報表。

## Quick start / 快速開始

Python 3.10+; standard library only.

```bash
python3 scripts/toolkit.py plan examples/brief.synthetic.json --out-dir output/demo-plan
python3 scripts/toolkit.py validate output/demo-plan/plan.json
python3 scripts/toolkit.py analyze examples/report.csv --meta examples/report.meta.json --out-dir output/demo-report
python3 -m unittest discover -s tests -v
python3 scripts/release_gate.py
```

不登入、不保存憑證、不連廣告 API、不爬網站、不自動發布或改預算。PLAN_READY／ANALYSIS_READY 均需要人工審查。缺漏成本維持未知；毛 GMV、結算營收、利潤與增量不可混用。模型可能使用雲端，請勿輸入原始客戶個資。

[Data contract](../../references/data-contract.md) · [Sources and verification limits](../../references/official-sources.md) · [Installation](../INSTALLATION.md) · [Development handoff](../HANDOFF.md)

Five-language onboarding only; model routing, generated content, legal compliance and live advertising are not certified. No official platform affiliation. License: Apache-2.0.
