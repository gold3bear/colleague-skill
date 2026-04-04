# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

**同事.skill** — 将真实同事蒸馏成 AI Skill 的工具。输入同事的聊天记录、文档等原材料，生成一个能替他工作的 AI分身。

遵循 [AgentSkills](https://agentskills.io) 标准，整个仓库就是一个 Skill 目录。

## 目录结构

```
colleague-skill/
├── SKILL.md              # Skill 入口（Skill 标准 frontmatter）
├── prompts/              # Prompt 模板
│   ├── intake.md         #   基础信息录入（3 个问题）
│   ├── work_analyzer.md  #   工作能力提取
│   ├── persona_analyzer.md #  性格行为提取
│   ├── work_builder.md   #   work.md 生成模板
│   ├── persona_builder.md #   persona.md 五层结构模板
│   ├── merger.md         #   增量 merge 逻辑
│   └── correction_handler.md # 对话纠正处理
├── tools/                # Python 数据采集工具
│   ├── feishu_auto_collector.py  # 飞书全自动采集（群聊/私聊/文档）
│   ├── feishu_browser.py         # 飞书浏览器方案（需登录态）
│   ├── feishu_mcp_client.py      # 飞书 MCP 方案
│   ├── feishu_parser.py         # 飞书 JSON 导出解析
│   ├── dingtalk_auto_collector.py # 钉钉采集
│   ├── slack_auto_collector.py   # Slack 采集
│   ├── email_parser.py          # 邮件解析
│   ├── zsxq_browser_v2.py      # 知识星球浏览器采集
│   ├── scrape_wechat.py         # 微信公众号批量采集
│   ├── collect_jianshu.py       # 简书文章采集
│   ├── batch_scrape_jianshu.py  # 简书批量采集
│   ├── analyze_posts.py         # 数据质量分析
│   ├── extract_insights.py      # 核心观点提取
│   ├── extract_key_posts.py     # 关键帖子提取
│   ├── skill_writer.py          # Skill 文件管理
│   └── version_manager.py       # 版本存档与回滚
├── colleagues/           # 生成的同事 Skill（每个 {slug}/ 下有 SKILL.md, work.md, persona.md, meta.json）
├── docs/PRD.md
└── requirements.txt
```

## 常用命令

```bash
# 安装依赖
pip3 install -r requirements.txt

# 列出已创建的同事
python3 tools/skill_writer.py --action list --base-dir ./colleagues

# 版本回滚
python3 tools/version_manager.py --action rollback --slug {slug} --version {version} --base-dir ./colleagues

# 删除同事
rm -rf colleagues/{slug}
```

## 生成的同事 Skill 结构

每个同事 Skill 包含：

| 文件 | 内容 |
|------|------|
| `SKILL.md` | 完整 Skill（PART A 工作能力 + PART B 人物性格） |
| `work.md` | 技术规范、工作流程、经验知识 |
| `persona.md` | 5 层性格结构（硬规则 → 身份 → 表达风格 → 决策模式 → 人际行为） |
| `meta.json` | 元信息（姓名、slug、版本、标签） |
| `versions/` | 历史版本存档 |
| `knowledge/` | 原始导入材料 |

## 数据采集工具

| 工具 | 用途 | 前置条件 |
|------|------|---------|
| `feishu_auto_collector.py` | 飞书群聊/私聊/文档采集 | App ID/Secret + (私聊需要) OAuth 授权 |
| `feishu_browser.py` | 飞书文档浏览器方案 | 本机 Chrome + Playwright |
| `feishu_mcp_client.py` | 飞书 MCP 方案 | App ID/Secret |
| `dingtalk_auto_collector.py` | 钉钉采集 | DingTalk 开放平台配置 |
| `slack_auto_collector.py` | Slack 采集 | Slack Bot Token |
| `email_parser.py` | 邮件 .eml/.mbox 解析 | 无 |

## 触发词

在 Claude Code 中使用：
- `/create-colleague` — 创建新同事 Skill
- `/list-colleagues` — 列出所有同事
- `/{slug}` — 调用完整同事 Skill
- `/{slug}-work` — 仅工作能力
- `/{slug}-persona` — 仅人物性格
- `/colleague-rollback {slug} {version}` — 回滚
- `/delete-colleague {slug}` — 删除

## 关键执行规则

1. **Skill 目录即仓库根目录**：写入 `colleagues/{slug}/` 时用项目目录作为 base-dir
2. **环境变量**：`${CLAUDE_SKILL_DIR}` 指向 skill 根目录（`~/.claude/skills/colleague-skill` 或 `.claude/skills/colleague-skill`）
3. **Python 工具调用**：统一用 `python3 ${CLAUDE_SKILL_DIR}/tools/xxx.py`
4. **灵活 API 调用**：collector 脚本跑不通时，直接写 Python 脚本调飞书/钉钉 API
