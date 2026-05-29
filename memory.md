# QClaw 记忆系统全解析 —— Claude Code 适配指南

> 读完这个文件，你就能在 Claude Code 里复现 QClaw 级别的持续记忆能力。

---

## 一、架构总览

QClaw 的记忆系统是一个**三层架构**，每层的角色和生命周期不同：

```
┌─────────────────────────────────────────────────────┐
│                    记忆三层模型                       │
├──────────────┬──────────────────┬───────────────────┤
│  短期记忆     │  中期记忆         │  长期记忆          │
│  会话上下文   │  memory/日日志    │  MEMORY.md         │
│  存活：本次会话 │ 存活：永久文件     │  存活：永久精华     │
│  容量：context │ 内容：原始记录     │  内容：提炼后知识    │
│  窗口         │ 粒度：每天追加     │  粒度：持续精炼     │
└──────────────┴──────────────────┴───────────────────┘
       +                      +
  HEARTBEAT.md              LCM（压缩历史）
  定时主动巡检              超长对话自动压缩+可检索
```

---

## 二、文件结构布局

在 Claude Code 中创建如下目录结构（路径可自定义，此处以 `~/claude/memory-system/` 为例）：

```
~/claude/memory-system/
├── CLAUDE.md              ← 记忆系统的规则指令（核心！启动时自动加载）
├── MEMORY.md              ← 长期记忆文件（精华，人手维护+AI辅助）
├── HEARTBEAT.md           ← 定时任务清单（AI主动巡检的驱动力）
├── TOOLS.md               ← 环境配置笔记（SSH、摄像头、偏好等）
├── memory/                ← 每日日志目录
│   ├── 2026-05-29.md
│   ├── 2026-05-30.md
│   └── heartbeat-state.json  ← 心跳巡检状态追踪
├── memory-search/         ← 语义搜索实现（可选，提升检索能力）
│   ├── search.py          ← Python 脚本：chromadb 语义搜索
│   └── requirements.txt   ← 依赖：chromadb, sentence-transformers
└── compact.py             ← 对话压缩脚本（可选，用于超长对话）
```

---

## 三、CLAUDE.md 核心指令

将以下内容写入 `~/claude/memory-system/CLAUDE.md`。

Claude Code 启动时会自动读取此文件，效果等同于 QClaw 的 `AGENTS.md` 注入。

```markdown
# CLAUDE.md — Memory System Rules

## Session Startup

Every session, you wake up fresh. These files are your continuity bridge:

- Current dir: `~/claude/memory-system/`
- `MEMORY.md` — your long-term curated memories
- `memory/YYYY-MM-DD.md` — raw daily logs of what happened
- `HEARTBEAT.md` — proactive task list for periodic checks

## Memory Layer Rules

### MEMORY.md — Long-term Memory

- Write significant events, decisions, opinions, lessons learned
- This is curated wisdom — not raw logs
- Review every few days: read recent daily files, distill into MEMORY.md
- Remove outdated info

### memory/YYYY-MM-DD.md — Daily Logs

- After every significant piece of work, append to today's log
- Format: timestamp + what happened + key decisions + outputs
- NEVER overwrite existing entries — only append
- Create the file if it doesn't exist

### Write It Down — No Mental Notes!

- "I'll remember this" is a lie. You won't.
- When someone says "remember this" → write to today's log
- When you learn a lesson → update MEMORY.md or add to CLAUDE.md
- When you make a mistake → document it so future-you doesn't repeat it

## Proactive Behavior (Heartbeat System)

When you're idle and have nothing pressing, proactively:

1. Read `HEARTBEAT.md`
2. Execute any scheduled tasks
3. Update `memory/heartbeat-state.json` with timestamps of last checks
4. If >8h since last human contact and something important happened → reach out
5. 23:00-08:00 → stay quiet unless urgent

### heartbeat-state.json Format

```json
{
  "lastChecks": {
    "email": 1717000000,
    "calendar": 1716990000,
    "memory-review": 1716980000
  }
}
```

### Memory Maintenance (During Idle Time)

Every 2-3 days during idle:
1. Read recent `memory/YYYY-MM-DD.md` files
2. Distill key insights into MEMORY.md
3. Remove stale info from MEMORY.md

## Semantic Memory Search

Before answering questions about "what did we do...", "have I ever...", etc:

1. Run `python memory-search/search.py "user's question"`
2. Read the top-matched daily log and MEMORY.md excerpts
3. Answer based on evidence, not guesses

## Red Lines

- Don't exfiltrate private data. Ever.
- Don't run destructive commands without asking.
- In group chats: don't share private memory. Be a participant, not a proxy.
- When in doubt, ask.
```

---

## 四、MEMORY.md 格式规范

```markdown
# 长期记忆

## 2026-05-28：记忆系统启用

今天在 Claude Code 中建立了三层记忆系统：
- CLAUDE.md 作为启动规则加载完毕
- memory/ 目录创建完成
- 语义搜索用的 chromadb 已初始化

## [日期]：[主题]

[详细描述事件、决策、洞见]
- 做了什么
- 为什么这么做
- 学到了什么
- 下次要注意什么
```

### 写入时机
- 项目关键决策
- 学到的重要教训
- 用户偏好/习惯
- 长期项目状态更新

### 维护周期
- 每 2-3 天空闲时读取近期 `memory/` 文件，提炼精华写入
- 删除已过时的信息

---

## 五、每日日志格式规范

`memory/YYYY-MM-DD.md`：

```markdown
# 2026-05-29 日志

## 10:30 - 讨论了XX项目的架构方案
- 决定使用微服务架构
- 关键考量：团队规模、部署复杂度
- 输出物：docs/architecture-v2.md

## 14:00 - 修复了登录模块的Bug
- 问题：OAuth token 过期未刷新
- 修复：添加了自动延期逻辑
- PR: #2341

## 18:00 - 会话结束
- 待办：明天继续配置CI/CD流水线
```

### 规则
- **只追加，不覆盖**
- 至少记录：时间、做了什么、关键决策
- 情绪/偏好/灵感也可以记（"这个设计模式很不错，应该推广"）

---

## 六、HEARTBEAT.md —— 主动巡检系统

这是让 AI **不只是被动等待用户消息**，而是主动做事的关键机制。

### 文件格式

```markdown
# HEARTBEAT 巡检任务

## 定时任务（每天 3-4 次）

- [ ] 检查邮件（Gmail API / 客户端）
- [ ] 检查日历（接下来 24h 的日程）
- [ ] 天气预警（如果有户外活动）
- [ ] 项目状态检查（git status 是否有未提交变更）
- [ ] 新闻/社交提及（可选）

## 每 2-3 天

- [ ] 记忆维护：读 memory/*.md → 更新 MEMORY.md
- [ ] 清理过期提醒
- [ ] 备份重要文件

## 每周

- [ ] 周报总结
- [ ] 项目进展回顾
```

### Claude Code 中如何实现心跳

Claude Code 本身不会主动推送消息，但你可以：

#### 方案 A：操作系统 crontab（推荐）

在 macOS/Linux 上：

```bash
# 每 30 分钟触发一次 Claude Code 巡检
*/30 * * * * cd ~/claude/memory-system && claude -p "Heartbeat check: read HEARTBEAT.md, execute any pending tasks, update heartbeat-state.json. Reply with summary." --output-format text
```

在 Windows 上，使用 Task Scheduler 或 PowerShell 脚本：

```powershell
# heartbeat.ps1
cd ~/claude/memory-system
$prompt = "Heartbeat check: read HEARTBEAT.md, execute pending tasks, update memory/heartbeat-state.json. Reply with summary or HEARTBEAT_OK."
claude -p $prompt --output-format text | Out-File "memory/heartbeat-$(Get-Date -Format 'yyyyMMdd-HHmmss').log"
```

#### 方案 B：Claude Code Hooks（内置）

Claude Code 支持 `hooks` 配置，在空闲时自动执行特定指令：

```json
// ~/.claude/settings.json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "",
        "hooks": [...]
      }
    ]
  }
}
```

#### 方案 C：外部触发的简单 HTTP 回调

```python
# cron 调用这个脚本
import subprocess, os
os.chdir(os.path.expanduser("~/claude/memory-system"))
prompt = "Heartbeat check. Read HEARTBEAT.md. Execute tasks. Reply briefly."
result = subprocess.run(["claude", "-p", prompt, "--output-format", "text"], capture_output=True, text=True)
with open(f"memory/heartbeat-{datetime.now():%Y%m%d-%H%M}.log", "w") as f:
    f.write(result.stdout)
```

---

## 七、语义记忆搜索（chromadb 实现）

QClaw 的 `memory_search` 工具对 MEMORY.md + memory/*.md 做语义搜索。
Claude Code 中用 chromadb 可以复现。

### 安装依赖

```bash
pip install chromadb sentence-transformers
```

### search.py

```python
#!/usr/bin/env python3
"""
语义记忆搜索工具 —— QClaw memory_search 的 Claude Code 等价实现。
每次运行都会重建索引，确保最新文件被索引。
"""
import sys
import os
from pathlib import Path
import chromadb
from chromadb.utils import embedding_functions

MEMORY_ROOT = Path(os.environ.get("MEMORY_ROOT", os.path.expanduser("~/claude/memory-system")))
DB_PATH = MEMORY_ROOT / ".chroma_db"

def chunk_file(filepath: Path, max_chunk_chars: int = 1000) -> list[dict]:
    """将文件拆分为可索引的片段。"""
    chunks = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception:
        return chunks

    # 按段落自然切分
    paragraphs = content.split("\n\n")
    current_chunk = ""
    for para in paragraphs:
        if len(current_chunk) + len(para) < max_chunk_chars:
            current_chunk += "\n\n" + para if current_chunk else para
        else:
            if current_chunk.strip():
                chunks.append({"text": current_chunk.strip(), "source": str(filepath)})
            current_chunk = para
    if current_chunk.strip():
        chunks.append({"text": current_chunk.strip(), "source": str(filepath)})
    return chunks

def build_index():
    """扫描所有记忆文件，构建 chromadb 索引。"""
    # 清理旧索引
    if DB_PATH.exists():
        import shutil
        shutil.rmtree(str(DB_PATH))

    client = chromadb.PersistentClient(path=str(DB_PATH))

    # 使用 sentence-transformers 做 embedding（免费，本地运行）
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"  # 80MB，速度快，效果好
    )

    collection = client.get_or_create_collection(
        name="memory",
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"}
    )

    # 扫描文件
    files = []
    for f in MEMORY_ROOT.glob("MEMORY.md"):
        files.append(f)
    for f in MEMORY_ROOT.glob("memory/*.md"):
        files.append(f)

    docs, metadatas, ids = [], [], []
    for f in files:
        for i, chunk in enumerate(chunk_file(f)):
            docs.append(chunk["text"])
            metadatas.append({"source": chunk["source"], "chunk": i})
            ids.append(f"{f.name}_{i}")

    if docs:
        collection.add(documents=docs, metadatas=metadatas, ids=ids)
        print(f"Indexed {len(docs)} chunks from {len(files)} files", file=sys.stderr)
    return collection

def search(query: str, top_k: int = 5) -> list[dict]:
    """语义搜索记忆。"""
    collection = build_index()
    results = collection.query(query_texts=[query], n_results=top_k)

    hits = []
    for i in range(len(results["documents"][0])):
        hits.append({
            "score": 1 - results["distances"][0][i],  # cosine distance → similarity
            "source": results["metadatas"][0][i]["source"],
            "text": results["documents"][0][i][:500]  # 截断显示
        })

    return hits

def main():
    if len(sys.argv) < 2:
        print("Usage: python search.py 'search query'")
        sys.exit(1)

    query = sys.argv[1]
    results = search(query)

    for r in results:
        print(f"[{r['score']:.2f}] {r['source']}")
        print(f"    {r['text'][:200]}")
        print()

if __name__ == "__main__":
    main()
```

### 使用方式

```bash
# 搜索记忆
python memory-search/search.py "上次讨论的那个架构方案"
# 输出:
# [0.92] ~/claude/memory-system/memory/2026-05-29.md
#     10:30 - 讨论了XX项目的架构方案...
# [0.85] ~/claude/memory-system/MEMORY.md
#     决定使用微服务架构...
```

### Claude Code 中的集成

在 CLAUDE.md 中加上这条规则，AI 会在回答"之前的事"前自动搜索：

```
Before answering any question about past work or decisions, run:
  python memory-search/search.py "user's exact question"
Then answer based on the search results. If no results found, say so — don't guess.
```

---

## 八、对话压缩（LCM 等价方案）

QClaw 的 LCM（Lossless Context Management）在对话超长时自动压缩旧内容，
并建立可检索的索引。这是最难复现的部分，但可以做简化版。

### 方案 A：手动触发（最简单）

当对话太长时，让 AI 执行压缩指令：

```
你: /compact
AI: [自动摘要当前对话] → 写入 memory/compact-2026-05-29-001.md
    [清除上下文中的旧消息，保留摘要]
```

CLAUDE.md 规则：

```
When the conversation exceeds ~80% of context limit:
1. Summarize the conversation so far into a compact note
2. Save to memory/compact-YYYY-MM-DD-NNN.md
3. Include: key decisions, open questions, current task, relevant code paths
4. NOTE: 这需要 Claude Code 支持 /compact 命令或手动触发
```

### 方案 B：自动检测 + 压缩

在 `memory-search/search.py` 旁边加一个 `compact.py`：

```python
#!/usr/bin/env python3
"""
对话压缩脚本。输入原始对话文本，输出结构化摘要。
"""
import sys
import json
from datetime import datetime

def estimate_tokens(text: str) -> int:
    """粗略估计 token 数（英文 1 token ≈ 4 chars, 中文 1 token ≈ 2 chars）"""
    return len(text) // 3

def main():
    conversation = sys.stdin.read()
    token_count = estimate_tokens(conversation)

    print(f"Conversation tokens: ~{token_count}")
    print(f"Context limit: ~200,000 (Claude 3.5 Sonnet)")

    # 生成压缩模板
    prompt = f"""Summarize the following conversation into a dense, retrievable note.
Include: key topics, decisions made, open questions, current task, code paths touched.

Conversation ({token_count} est. tokens):
---
{conversation}
---

Output format:
## Compact Note — {datetime.now():%Y-%m-%d %H:%M}
### Topics
- ...
### Decisions
- ...
### Open Questions
- ...
### Current Task
- ...
### Code Touched
- ..."""

    # 输出给 Claude Code 执行
    print("\n--- COMPRESSION PROMPT ---")
    print(prompt[:500] + "...")

if __name__ == "__main__":
    main()
```

### 压缩历史的检索

压缩后的文件存在 `memory/compact-*.md`，会被 `search.py` 自动索引，
所以后续对话中提及之前的内容，语义搜索就能找到。

---

## 九、定时任务系统（Cron）

QClaw 有内置的 cron 系统。在 Claude Code 中，你有一个更简单但等效的方案。

### crontab 配置（macOS/Linux）

```bash
# 编辑 crontab
crontab -e

# 每天早上 9:00 日报提醒
0 9 * * * cd ~/claude/memory-system && claude -p "Good morning. Check today's calendar, pending tasks from yesterday's log, and any urgent emails. Give a 3-bullet summary." --output-format text | mail -s "Morning Brief" you@email.com

# 每天下午 18:00 日报总结
0 18 * * * cd ~/claude/memory-system && claude -p "End of day summary. Review today's memory/YYYY-MM-DD.md, list accomplishments, and flag anything not done for tomorrow." --output-format text >> memory/daily-summaries.md

# 每周一 9:00 周报
0 9 * * 1 cd ~/claude/memory-system && claude -p "Generate a weekly summary from this week's daily logs. List: top 3 accomplishments, open items, next week priorities." --output-format text >> memory/weekly-summaries.md

# 每 30 分钟心跳
*/30 * * * * cd ~/claude/memory-system && claude -p "Heartbeat. Read HEARTBEAT.md, check email/calendar for urgent items. Reply briefly or HEARTBEAT_OK." --output-format text >> memory/heartbeat-log.md
```

### Windows Task Scheduler 等效

```powershell
# 创建计划任务：每 30 分钟心跳
$action = New-ScheduledTaskAction -Execute "claude" -Argument '-p "Heartbeat check. Read HEARTBEAT.md. Reply briefly." --output-format text' -WorkingDirectory "$env:USERPROFILE\claude\memory-system"
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 30) -RepetitionDuration ([TimeSpan]::MaxValue)
Register-ScheduledTask -TaskName "ClaudeHeartbeat" -Action $action -Trigger $trigger -Description "Claude Code proactive heartbeat"
```

---

## 十、完整工作流示例

### 会话开始

```
用户: 继续做昨天的功能
AI:
  1. 读取 memory/YYYY-MM-DD.md（今天 + 昨天）
  2. 读取 MEMORY.md（长期上下文）
  3. 如果有待办 → 立即继续
  4. 如果没有 → 语义搜索 "昨天的功能"
  5. 回复: "昨天我们做到了XX，今天继续YY。"
```

### 会话中间（记录）

```
用户: 把登录接口改成JWT
AI: [实现中...]
    [完成后追加到 memory/2026-05-29.md]:
    "14:30 - 将登录接口从 session 改为 JWT
     原因：需要支持跨域、移动端
     改动：auth/login.ts, middleware/auth.ts
     注意：刷新 token 逻辑待实现"
```

### 会话结束

```
AI: "今天完成了登录JWT改造和API文档更新。
     已记录到 memory/2026-05-29.md。
     明天继续：token 刷新逻辑 + 单元测试。"
```

### 维护日（每 2-3 天一次）

```
AI [空闲时]:
  1. 读取 memory/2026-05-27.md ~ 2026-05-29.md
  2. 识别关键事件和教训
  3. 更新 MEMORY.md:
     "登录系统已迁移到JWT。教训：session跨域很麻烦，新项目直接JWT。"
  4. 清理 MEMORY.md 过时信息
```

---

## 十一、从零搭建清单

按顺序执行，15 分钟内完成基础设置：

### Step 1：创建目录结构

```bash
mkdir -p ~/claude/memory-system/memory
mkdir -p ~/claude/memory-system/memory-search
cd ~/claude/memory-system
```

### Step 2：创建 CLAUDE.md

把第三章的内容写入 `~/claude/memory-system/CLAUDE.md`

### Step 3：初始化 MEMORY.md

```bash
echo "# 长期记忆\n\n## $(date +%Y-%m-%d)：记忆系统初始化\n\n三层记忆系统已建立：\n- CLAUDE.md 启动时自动加载\n- memory/ 目录用于每日日志\n- MEMORY.md 用于长期精华\n- chromadb 语义搜索已就绪" > MEMORY.md
```

### Step 4：初始化 HEARTBEAT.md

把第六章的心跳任务模板写入 `HEARTBEAT.md`

### Step 5：安装搜索依赖

```bash
pip install chromadb sentence-transformers
```

### Step 6：创建 search.py

把第七章的 Python 脚本写入 `memory-search/search.py`

### Step 7：（可选）设置 crontab 心跳

把第九章的 crontab 配置加入系统

### Step 8：验证

```bash
# 启动 Claude Code 并指定工作目录
cd ~/claude/memory-system && claude

# 提问测试
你: "我们之前讨论过什么？"
AI: [应该自动搜索并回复]
```

---

## 十二、与 QClaw 原版的差异对照

| 功能 | QClaw 原版 | Claude Code 等效方案 | 差距 |
|---------|-----------|-------------------|------|
| **启动上下文注入** | AGENTS.md 自动注入 | CLAUDE.md 自动加载 | ✅ 一致 |
| **每日日志** | memory/YYYY-MM-DD.md | 同上 | ✅ 一致 |
| **长期记忆** | MEMORY.md | 同上 | ✅ 一致 |
| **语义搜索** | memory_search 工具（内置） | chromadb + search.py | ⚠️ 需手动调脚本 |
| **对话压缩** | LCM 自动压缩+索引 | 手动 /compact 或 compact.py | ❌ 无自动压缩 |
| **心跳巡检** | HEARTBEAT.md + 定时 poll | crontab + claude CLI | ⚠️ 需外挂 cron |
| **定时任务** | cron 工具（内置） | 系统 crontab | ⚠️ 需额外配置 |
| **跨会话消息** | sessions_send 工具 | 不可用 | ❌ 不可复现 |
| **群聊记忆隔离** | 按 session 区分 | 需手动控制 | ⚠️ 需约定 |

### 不可复现的功能（接受代价）

- **LCM 自动压缩**：QClaw 的压缩索引系统是二进制的，Claude Code 中没有。用 `memory/compact-*.md` + search.py 索引是简化替代。
- **跨会话消息推送**：QClaw 的 `sessions_send` 可以主动给不同会话发消息。Claude Code 不行。

### 可超越的功能

- **语义搜索质量**：chromadb + sentence-transformers 的本地 embedding 质量比 QClaw 的内置搜索更好（QClaw 的 `memory_search` 是轻量级实现）。
- **搜索扩展性**：可轻松扩展到搜索本地文档、笔记、代码仓库等。

---

## 十三、进阶优化

### 1. 扩展搜索范围

修改 search.py 的扫描路径，加入笔记、文档：

```python
for f in MEMORY_ROOT.glob("MEMORY.md"):
    files.append(f)
for f in MEMORY_ROOT.glob("memory/*.md"):
    files.append(f)
# 扩展：加入 Obsidian 笔记
for f in Path("~/Documents/Obsidian").glob("*.md"):
    files.append(f)
```

### 2. 持久化索引（避免每次重建）

修改 search.py 为增量更新模式：

```python
# 改为：检查文件 mtime，只更新变动的文件
def build_index_incremental(collection):
    existing = {m["source"] for m in collection.get()["metadatas"]}
    # 只添加新文件或 mtime 更新的文件
    ...
```

### 3. 多项目记忆隔离

在不同项目的 CLAUDE.md 中指定不同的 MEMORY_ROOT：

```bash
# 项目 A
MEMORY_ROOT=~/projects/project-a/.memory

# 项目 B
MEMORY_ROOT=~/projects/project-b/.memory
```

---

## 总结：核心要记住的五件事

1. **CLAUDE.md 是发动机** — 把记忆系统的规则写进去，启动时自动加载
2. **每天写日志** — 追加到 memory/YYYY-MM-DD.md，永不过期
3. **定期提炼精华** — 每 2-3 天从日志中提取关键信息到 MEMORY.md
4. **语义搜索兜底** — 之前的细节记不清？chromadb 帮你搜
5. **心跳保持活跃** — 用 crontab 让 AI 不只是被动等待

照这个方案实现，Claude Code 的记忆能力可以接近 QClaw 的 80%，在搜索质量上甚至可能超越。
