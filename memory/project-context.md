---
name: project-context
description: 当前项目目标、进展、关键决策
metadata: 
  node_type: memory
  type: project
  originSessionId: f059bf44-6297-4478-a64c-5c0cb08c859f
---

# 项目上下文

## 2026-05-29：Skills 体系建设

### 目标
为 QClaw（openclaw）建立完整的 skill 体系，同时升级 Claude Code 的记忆系统。

### 已完成
1. 在 `E:\skills\` 创建了 9 大类 49 个 skill 的目录结构
2. 编写了顶层 `SKILLS.md` 索引文件
3. 从 QClaw 对话中提取了完整的记忆系统设计（memory.md）

### 关键决策
- Skill 格式采用 Claude Code 标准：YAML frontmatter (name + description) + Markdown 正文
- 分类采用数字前缀排序（01-code-dev、02-git 等）
- 记忆系统适配 Claude Code 已有的 calendar/ 和 memory/ 基础设施

### 下一步
- 将 QClaw 记忆系统适配到 Claude Code
- 建立 MEMORY.md → calendar/ 的双向桥接
- 设置记忆维护心跳
