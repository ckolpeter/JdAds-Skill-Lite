# JdAds Skill Lite v1.0.0 — English

[README](../../README.md) · [AI Ads Academy](https://www.ai-ads.academy)

JD product, store and new-product planning with order economics and report checks

This release supports mainland China (CN/CNY) only. It provides offline planning and descriptive report analysis. Mode labels are local workflows, not API enums or verified account capabilities.

Copy templates/brief.json and enter known values; keep unknowns null. Pre-ad order contribution equals net revenue minus known non-ad costs. Budget splitting is an equal pilot scenario, not an optimizer. CSV requires the documented canonical header and metadata; raw platform exports are not auto-mapped.

## Quick start / 快速開始

Python 3.10+; standard library only.

```bash
python3 scripts/toolkit.py plan examples/brief.synthetic.json --out-dir output/demo-plan
python3 scripts/toolkit.py validate output/demo-plan/plan.json
python3 scripts/toolkit.py analyze examples/report.csv --meta examples/report.meta.json --out-dir output/demo-report
python3 -m unittest discover -s tests -v
python3 scripts/release_gate.py
```

No sign-in, credentials, ad APIs, scraping, publishing or budget changes. PLAN_READY and ANALYSIS_READY require human review. Missing costs remain unknown. Gross GMV, net settlement, profit and incremental lift are different. The host model may use cloud services; never supply raw customer personal data.

[Data contract](../../references/data-contract.md) · [Sources and verification limits](../../references/official-sources.md) · [Installation](../INSTALLATION.md) · [Development handoff](../HANDOFF.md)

Five-language onboarding only; model routing, generated content, legal compliance and live advertising are not certified. No official platform affiliation. License: Apache-2.0.
