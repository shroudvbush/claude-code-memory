#!/usr/bin/env python3
"""
记忆维护检查脚本 —— 检查是否需要执行记忆提炼。

用法（通过 crontab 或手动触发）:
  python3 ~/.claude/scripts/heartbeat-memory.py

逻辑：
  - 如果距离上次提炼超过 3 天 → 提示执行提炼
  - 如果今天还没写日志 → 提示写日志
  - 如果一切正常 → 输出 "MEMORY_OK"

配合 crontab：
  # 每天 10:00 和 18:00 检查一次
  0 10,18 * * * python3 ~/.claude/scripts/heartbeat-memory.py >> ~/.claude/memory-heartbeat.log
"""

import os
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta

HEARTBEAT_STATE = Path(os.path.expanduser("~/.claude/.heartbeat-state.json"))
CALENDAR_ROOT = Path(os.path.expanduser("~/.claude/calendar"))
MEMORY_ROOT = Path(os.path.expanduser("~/.claude/projects/-home-huangshuai/memory"))
TZ = timezone(timedelta(hours=8))  # Asia/Shanghai


def load_state() -> dict:
    if HEARTBEAT_STATE.exists():
        return json.loads(HEARTBEAT_STATE.read_text())
    return {"lastMaintenance": None, "lastDailyLog": None}


def save_state(state: dict):
    HEARTBEAT_STATE.write_text(json.dumps(state, indent=2, ensure_ascii=False))


def days_since(date_str: str | None) -> int:
    if not date_str:
        return 999
    d = datetime.fromisoformat(date_str)
    now = datetime.now(TZ)
    return (now - d).days


def main():
    state = load_state()
    now = datetime.now(TZ)
    today_str = now.strftime("%Y-%m-%d")

    issues = []

    # 检查 1：今天有日志吗？
    today_calendar = CALENDAR_ROOT / today_str / "摘要.md"
    if today_calendar.exists():
        state["lastDailyLog"] = today_str
    else:
        if days_since(state.get("lastDailyLog")) >= 1:
            issues.append(f"⚠️ 今天（{today_str}）还没有工作日志。")

    # 检查 2：3 天以上没提炼？
    if days_since(state.get("lastMaintenance")) >= 3:
        issues.append(
            f"🔧 距上次记忆提炼已有 {days_since(state.get('lastMaintenance'))} 天。"
            f"建议执行：读取最近 3 天的 ~/.claude/calendar/*/摘要.md，"
            f"提炼到 ~/.claude/projects/-home-huangshuai/memory/"
        )

    # 检查 3：MEMORY.md 是否太旧？
    memory_md = MEMORY_ROOT / "MEMORY.md"
    if memory_md.exists():
        mtime = datetime.fromtimestamp(memory_md.stat().st_mtime, tz=TZ)
        if (now - mtime).days >= 7:
            issues.append(f"💡 MEMORY.md 已 { (now - mtime).days } 天未更新。")

    if issues:
        print(f"[{now.strftime('%Y-%m-%d %H:%M')}] 记忆心跳检查发现问题：")
        for issue in issues:
            print(f"  {issue}")
    else:
        print(f"[{now.strftime('%Y-%m-%d %H:%M')}] MEMORY_OK")

    save_state(state)


if __name__ == "__main__":
    main()
