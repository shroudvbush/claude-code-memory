---
name: feedback-lessons
description: 从成功和失败中提炼的经验法则
metadata: 
  node_type: memory
  type: feedback
  originSessionId: f059bf44-6297-4478-a64c-5c0cb08c859f
---

# 踩坑教训

## 2026-05-29：Claude Code 自动更新问题

**教训：** 生产工具需要锁定版本。

**Why:** Claude Code 从 2.1.150 自动更新到 2.1.156，导致行为变化。

**How to apply:** 新装 CLI 工具后立即检查自动更新机制，必要时锁定：
- 环境变量：`CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=true`
- 文件权限：`chmod 555` 锁定二进制

## 2026-05-29：GitHub 直连 100% 不可用

**教训：** 国内环境所有 GitHub 操作必须先走代理。

**How to apply:** 任何涉及 github.com 域名的操作，先触发 github-accel skill。

## 2026-05-29：日历自动保存截断

**教训：** 自动脚本不能有隐式长度限制。

**Why:** auto-save.py 设置了 40 行截断，导致长对话丢失。

**How to apply:** 自动保存脚本不做内容截断，完整保存。
