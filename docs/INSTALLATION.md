# 安裝與明確使用

Python 3.10+。先 clone 此 Repo，或解壓完整套件中的 `jdads-skill-lite`。開啟資料夾並要求 Agent 讀 SKILL.md 即可明確使用工作流；不代表自動路由已測。

專案層級安装位置請依宿主確認。Codex 常用 `.agents/skills/jdads-skill-lite`；Claude Code 常用 `.claude/skills/jdads-skill-lite`。不要把既有安裝直接覆蓋。

```bash
python3 scripts/install_skill.py --destination /absolute/project/.agents/skills/jdads-skill-lite
# 確認 dry-run 後才執行：
python3 scripts/install_skill.py --destination /absolute/project/.agents/skills/jdads-skill-lite --apply
```

使用專案真實路徑取代 `/absolute/project`。第一條預設 dry-run。目的地存在、名稱不符或使用 symlink 會拒絕。
在宿主新對話明確指定 Skill，跑一份合成例子，再依 evals/manual-cases.md 測試平台路由。

官方宿主說明（2026-10-05 查閱）：https://developers.openai.com/codex/skills/ 與 https://code.claude.com/docs/en/skills 。
尚未驗證使用者桌面安裝、模型路由、模型輸出品質及 Windows。五語文件不保證各語言輸出品質。
