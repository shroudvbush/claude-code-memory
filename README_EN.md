# Claude Code Memory System

[中文](README.md) | English

A three-layer persistent memory system for Claude Code, inspired by QClaw's memory architecture.

## What It Is

Claude Code has a native memory system (file format, four memory types), but it only defines the **data model** — not the **operational rules**. This project fills that gap:

```
Three-layer memory model:
  Short-term (session context) → Mid-term (calendar logs) → Long-term (MEMORY.md)
                                                                ↑
                                             Distilled every 2-3 days during idle
```

## Project Structure

```
claude-code-memory/
├── CLAUDE-template.md       ← Memory rules to append to ~/.claude/CLAUDE.md
├── memory/                  ← Long-term memory templates
│   ├── MEMORY.md            ← Memory index
│   ├── user-profile.md      ← User profile
│   ├── user-prefs.md        ← User preferences
│   ├── project-context.md   ← Project context
│   ├── feedback-lessons.md  ← Lessons learned
│   └── reference-index.md   ← External references
├── scripts/
│   ├── memory-search.py     ← Keyword + semantic search
│   └── heartbeat-memory.py  ← Memory maintenance heartbeat
├── calendar-skill/
│   └── SKILL.md             ← Calendar skill (mid→long-term bridge)
└── memory.md                ← Full design document
```

## Quick Install

```bash
git clone https://github.com/shroudvbush/claude-code-memory.git
cd claude-code-memory
```

### Step 1: Deploy Memory Rules

Append `CLAUDE-template.md` to your `~/.claude/CLAUDE.md`:

```bash
cat CLAUDE-template.md >> ~/.claude/CLAUDE.md
```

### Step 2: Deploy Long-term Memory Templates

```bash
# Claude Code uses -home-<user> (Linux) or -Users-<user> (macOS) as the project dir
PROJ_DIR=$(echo "$HOME" | sed 's|^/||; s|/|-|g')
mkdir -p ~/.claude/projects/-${PROJ_DIR}/memory/
cp memory/*.md ~/.claude/projects/-${PROJ_DIR}/memory/
```

### Step 3: Deploy Scripts

```bash
mkdir -p ~/.claude/scripts/
cp scripts/*.py ~/.claude/scripts/
```

### Step 4: Deploy Calendar Skill

```bash
mkdir -p ~/.claude/skills/calendar/
cp calendar-skill/SKILL.md ~/.claude/skills/calendar/
```

### Step 5: Verify

```bash
# Check heartbeat
python3 ~/.claude/scripts/heartbeat-memory.py

# Search memory
python3 ~/.claude/scripts/memory-search.py "memory system"
```

## How It Works

### Every Day

Driven by the CLAUDE.md rules, the AI automatically appends important work to `~/.claude/calendar/YYYY-MM-DD/summary.md`.

### Every 2-3 Days

During idle time, the AI reads recent calendar logs and distills valuable information into long-term memory files (user-prefs.md, project-context.md, etc.).

### At Any Time

When you ask "how did we do X before?", the AI performs a four-tier search: summary → full records → long-term memory → semantic search.

## Relationship with Claude Code's Native Memory

| Native System Provides | This Project Adds |
|------------------------|-------------------|
| File format (YAML frontmatter) | Operational rules (when to write, when to maintain) |
| Four memory types | Mid-term log → long-term memory distillation pipeline |
| MEMORY.md index mechanism | Session startup checklist |
| File read/write permissions | Four-tier search + semantic retrieval |
| — | Memory maintenance heartbeat |

## License

MIT
