# JdAds Skill Lite v1.0.0 — 한국어

[README](../../README.md) · [AI Ads Academy](https://www.ai-ads.academy)

JD 상품·스토어·신상품 기획, 주문 수익성 및 보고서 검토

이 버전은 중국 본토(CN/CNY) 전용 오프라인 기획 및 기술 통계 도구입니다. 모드는 로컬 작업 분류이며 API 값이나 확인된 계정 자격이 아닙니다.

templates/brief.json을 복사하고 알려진 값을 입력하세요. 모르는 값은 null로 유지합니다. 광고 전 공헌이익은 순매출에서 비광고 비용을 뺀 값입니다. 균등 예산 배분은 시험 시나리오일 뿐 최적화가 아닙니다. CSV에는 문서의 표준 열과 메타데이터가 필요합니다.

## Quick start / 快速開始

Python 3.10+; standard library only.

```bash
python3 scripts/toolkit.py plan examples/brief.synthetic.json --out-dir output/demo-plan
python3 scripts/toolkit.py validate output/demo-plan/plan.json
python3 scripts/toolkit.py analyze examples/report.csv --meta examples/report.meta.json --out-dir output/demo-report
python3 -m unittest discover -s tests -v
python3 scripts/release_gate.py
```

로그인, 자격 증명 저장, 광고 API, 스크래핑, 게시 또는 예산 변경을 하지 않습니다. 모든 결과는 사람이 검토해야 합니다. 누락 비용을 0으로 처리하지 않으며 GMV, 정산 매출, 이익 및 증분 성과를 구분합니다. 호스트 모델은 클라우드를 사용할 수 있으므로 고객 개인정보를 입력하지 마세요.

[Data contract](../../references/data-contract.md) · [Sources and verification limits](../../references/official-sources.md) · [Installation](../INSTALLATION.md) · [Development handoff](../HANDOFF.md)

Five-language onboarding only; model routing, generated content, legal compliance and live advertising are not certified. No official platform affiliation. License: Apache-2.0.
