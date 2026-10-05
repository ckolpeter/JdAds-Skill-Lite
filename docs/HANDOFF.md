# JdAds Skill Lite — 桌面開發交接

## 第一輪：唯讀驗收

建議 Codex Desktop：你已驗證可用的 coding 模型，推理強度 High。以此 Repo 為唯一工作目錄，不先增加功能。
讀 AGENTS.md、SKILL.md、references/data-contract.md、profile.json。確認 Python 版本，執行：

```bash
python3 scripts/toolkit.py plan examples/brief.synthetic.json --out-dir output/demo-plan
python3 scripts/toolkit.py validate output/demo-plan/plan.json
python3 scripts/toolkit.py analyze examples/report.csv --meta examples/report.meta.json --out-dir output/demo-report
python3 -m unittest discover -s tests -v
python3 scripts/release_gate.py
```

如果 manifest 不符，先列出 diff 與路徑，不直接重算。不要加入網路、憑證、Runmo、Pro、網站部署或廣告操作。

## 第二輪：一項功能

推薦先取得一份此平台、特定日期與版本的去識別原始報表。新增明確 mapping profile、欄位定義、同口徑 fixture，再做正負回歸。
原始欄位→canonical schema 不得猜測；平台名、行層級、幣別、退款、歸因期間及自然成交範圍不能自動捏造。
小紅書優先驗證 leads/qualified_leads/interactions；抖音／快手優先核對直播間與商品明細去重；其他平台優先核對結算與促銷成本。

## 第三輪：獨立審查

建議 Claude Code 獨立對話，使用可用的高推理模型做唯讀 review。區分腳本、宿主路由、模型產出與真實平台 NOT_RUN。
只能修改此 Repo。先建立 feature branch，再做單一功能；測試、smoke、文件、來源與 schema 一起更新。
核心在 scripts/toolkit.py；China 行為在 scripts/china.py，平台工作流在 profile.json。每包獨立，不引入其他 Repo 的執行依賴。

## 回報格式

Verdict / Files changed / Regression evidence / Risks / NOT_RUN / Next narrow step。
發布前審 diff，再執行 `python3 scripts/release_gate.py --write-manifest`，重新跑 full suite 與 gate。
保持 artifact contract 1.0；破壞性變更必須另外設計版本，不能靜默修改。
