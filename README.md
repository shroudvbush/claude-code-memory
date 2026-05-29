# Claude Code Memory System

为 Claude Code 构建的三层持续性记忆系统，灵感来源于 QClaw 的记忆架构。

## 是什么

Claude Code 原生有记忆系统（文件格式、四种记忆类型），但它只定义了**数据模型**，不包含**操作规则**。本项目补齐了缺失的部分：

```
三层记忆模型：
  短期（会话上下文）→ 中期（日历日志）→ 长期（MEMORY.md）
                                          ↑
                           每 2-3 天空闲时自动提炼
```

## 项目结构

```
claude-code-memory/
├── CLAUDE-template.md       ← 追加到 ~/.claude/CLAUDE.md 的记忆规则
├── memory/                  ← 长期记忆模板（放入 ~/.claude/.../memory/）
│   ├── MEMORY.md            ← 记忆索引
│   ├── user-profile.md      ← 用户画像
│   ├── user-prefs.md        ← 用户偏好
│   ├── project-context.md   ← 项目上下文
│   ├── feedback-lessons.md  ← 踩坑教训
│   └── reference-index.md   ← 外部资源索引
├── scripts/
│   ├── memory-search.py     ← 关键词 + 语义搜索
│   └── heartbeat-memory.py  ← 记忆维护心跳检查
├── calendar-skill/
│   └── SKILL.md             ← 日历 skill（桥接中期→长期记忆）
└── memory.md                ← 完整设计文档
```

## 快速安装

```bash
git clone https://github.com/shroudvbush/claude-code-memory.git
cd claude-code-memory
```

### Step 1：部署记忆规则

将 `CLAUDE-template.md` 的内容追加到 `~/.claude/CLAUDE.md`：

```bash
cat CLAUDE-template.md >> ~/.claude/CLAUDE.md
```

### Step 2：部署长期记忆模板

```bash
mkdir -p ~/.claude/projects/-home-$(whoami)/memory/
cp memory/*.md ~/.claude/projects/-home-$(whoami)/memory/
```

### Step 3：部署脚本

```bash
mkdir -p ~/.claude/scripts/
cp scripts/*.py ~/.claude/scripts/
```

### Step 4：部署日历 skill

```bash
mkdir -p ~/.claude/skills/calendar/
cp calendar-skill/SKILL.md ~/.claude/skills/calendar/
```

### Step 5：验证

```bash
# 检查心跳
python3 ~/.claude/scripts/heartbeat-memory.py

# 搜索记忆
python3 ~/.claude/scripts/memory-search.py "记忆系统"
```

## 工作原理

### 每天

AI 在 CLAUDE.md 规则驱动下，自动将重要工作追加到 `~/.claude/calendar/YYYY-MM-DD/摘要.md`。

### 每 2-3 天

AI 在空闲时读取近期日历日志，提炼有价值的信息到长期记忆文件（user-prefs.md、project-context.md 等）。

### 任意时刻

用户问"之前怎么做的"时，AI 执行四级搜索：摘要 → 完整记录 → 长期记忆 → 语义搜索。

## 与 Claude Code 原生记忆的关系

| 原生系统提供 | 本项目补充 |
|-------------|-----------|
| 文件格式（YAML frontmatter） | 操作规则（何时写、何时维护） |
| 四种记忆类型 | 中期日志→长期记忆的提炼管道 |
| MEMORY.md 索引机制 | 会话启动检查清单 |
| 文件读写权限 | 四级搜索 + 语义检索 |
| — | 记忆维护心跳 |

## License

MIT
