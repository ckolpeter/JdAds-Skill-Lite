# JdAds Skill Lite v1.0.0 — 日本語

[README](../../README.md) · [AI Ads Academy](https://www.ai-ads.academy)

京東の商品・店舗・新商品企画、注文採算とレポート確認

本版は中国本土（CN/CNY）専用のオフライン企画・記述的レポート分析ツールです。モード名はローカル作業分類であり、API値や確認済み利用資格ではありません。

templates/brief.json をコピーし、既知の値を記入します。不明値は null のままにします。広告前貢献利益は純収入から非広告費用を引いた値です。予算配分は均等試算であり最適化ではありません。CSV は指定列とメタデータが必要で、元のプラットフォーム出力を自動変換しません。

## Quick start / 快速開始

Python 3.10+; standard library only.

```bash
python3 scripts/toolkit.py plan examples/brief.synthetic.json --out-dir output/demo-plan
python3 scripts/toolkit.py validate output/demo-plan/plan.json
python3 scripts/toolkit.py analyze examples/report.csv --meta examples/report.meta.json --out-dir output/demo-report
python3 -m unittest discover -s tests -v
python3 scripts/release_gate.py
```

ログイン、認証情報保存、広告API、スクレイピング、公開、予算変更は行いません。すべて人間の確認が必要です。不明な費用をゼロにしません。GMV、精算収入、利益、増分効果を区別します。ホストモデルはクラウドを利用する場合があります。顧客個人情報を入力しないでください。

[Data contract](../../references/data-contract.md) · [Sources and verification limits](../../references/official-sources.md) · [Installation](../INSTALLATION.md) · [Development handoff](../HANDOFF.md)

Five-language onboarding only; model routing, generated content, legal compliance and live advertising are not certified. No official platform affiliation. License: Apache-2.0.
