---
name: colleague_creator
description: 创建同事的 Persona + Work Skill，支持 PDF/飞书/邮件导入和持续进化
user-invocable: true
---

# 触发条件

当用户说以下任意内容时启动本 Skill：
- `/create-colleague`
- "帮我创建一个同事 skill"
- "我想蒸馏一个同事"
- "新建同事"

当用户对已存在的同事 Skill 说以下内容时，进入进化模式：
- "我有新文件" / "追加文件"
- "这不对" / "他不会这样" / "他应该是"
- `/update-colleague {slug}`

当用户说 `/list-colleagues` 时，列出所有已生成的同事 Skill。

---

# 主流程：创建新同事 Skill

## Step 1：基础信息录入

参考 `prompts/intake.md`，通过对话引导用户填写基础信息。

所有字段均可跳过。对于每个字段，如果用户说"跳过"或"不填"，直接进入下一项。

询问顺序：
1. 同事的姓名或代号（必须，用于生成文件名）
2. 公司 + 职级 + 职位（如"字节 2-1 算法工程师"，可一句话说完）
3. 性别
4. MBTI
5. 个性标签（展示预设选项，可多选，可自定义）
6. 企业文化标签（展示预设选项，可多选）
7. 你对他的主观印象（自由文本，可跳过）

收集完毕后，汇总确认，用户确认后进入 Step 2。

## Step 2：文件导入

提示用户上传原材料，支持：
- PDF 文档（接口文档、技术规范、飞书导出）
- 图片截图
- 飞书消息导出 JSON 文件（提示：飞书 → 消息 → 导出）
- 邮件文本文件（.eml 或 .txt）
- Markdown 文本

处理规则：
- PDF 文件：使用 pdf 工具读取全文
- 图片：使用图像理解读取内容
- JSON 文件（飞书消息）：调用 `tools/feishu_parser.py` 解析，提取目标同事发出的内容
- .eml / .txt（邮件）：调用 `tools/email_parser.py` 解析，提取发件人为目标同事的邮件
- Markdown / 纯文本：直接读取

用户可以说"没有文件"或"跳过"，此时仅凭手动信息生成 Skill。

## Step 3：分析原材料

如果有文件内容，执行两条并行分析线路：

**线路 A（Work Skill 分析）**：
参考 `prompts/work_analyzer.md`，从原材料中提取：
- 负责的系统/业务/文档
- 技术规范与代码风格偏好
- 工作流程（接需求→方案→交付）
- 输出格式偏好
- 积累的知识结论

**线路 B（Persona 分析）**：
参考 `prompts/persona_analyzer.md`，从原材料中提取：
- 表达风格（用词、句式、口头禅）
- 决策模式与判断框架
- 人际行为（对上/对下/对平级）
- 在压力下的行为特征
- 边界与雷区

## Step 4：生成 Skill 文件

参考 `prompts/work_builder.md` 生成 `work.md` 内容。
参考 `prompts/persona_builder.md` 生成 `persona.md` 内容。

向用户展示两个部分的摘要（各 5-8 行），询问是否需要调整。

用户确认后，调用 `tools/skill_writer.py`，写入以下文件：
```
colleagues/{slug}/SKILL.md
colleagues/{slug}/work.md
colleagues/{slug}/persona.md
colleagues/{slug}/meta.json
```

告知用户 Skill 已创建，触发词为 `/{slug}`，工作版 `/{slug}-work`，人格版 `/{slug}-persona`。

---

# 进化模式：追加文件

当用户提供新文件时：
1. 读取新文件内容（同 Step 2 处理方式）
2. 读取现有 `work.md` 和 `persona.md`
3. 参考 `prompts/merger.md`，判断新内容属于 Work 还是 Persona
4. 只追加增量信息，不覆盖已有结论
5. 调用 `tools/version_manager.py` 存档当前版本后写入更新
6. 告知用户更新摘要

---

# 进化模式：对话纠正

当用户说"这不对"/"他应该是"/"他不会这样"时：
1. 参考 `prompts/correction_handler.md`，识别纠正的具体内容
2. 判断属于 Work Skill 还是 Persona 的纠正
3. 生成一条 correction 记录，格式：
   `[场景] 不应该 {错误行为}，应该 {正确行为}`
4. 追加到对应文件的 Correction 层
5. 立即生效

---

# 管理命令

`/list-colleagues`：
列出 `colleagues/` 目录下所有同事，显示姓名、公司职级、版本号、最后更新时间。

`/colleague-rollback {slug} {version}`：
调用 `tools/version_manager.py` 回滚到指定版本。

`/delete-colleague {slug}`：
确认后删除对应目录。
