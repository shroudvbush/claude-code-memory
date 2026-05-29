#!/usr/bin/env python3
"""
语义记忆搜索工具 —— Claude Code 记忆系统的检索增强。

用途：对 calendar/ 日志和 memory/ 长期记忆做语义搜索。
使用 grep 先做关键词匹配（快），可选 chromadb 做语义搜索（准）。

用法:
  # 关键词搜索（默认，不需要额外依赖）
  python3 ~/.claude/scripts/memory-search.py "关键词"

  # 语义搜索（需要 pip install chromadb sentence-transformers）
  python3 ~/.claude/scripts/memory-search.py --semantic "模糊描述"
"""

import sys
import os
import json
import subprocess
from pathlib import Path
from datetime import datetime

CALENDAR_ROOT = Path(os.path.expanduser("~/.claude/calendar"))
MEMORY_ROOT = Path(os.path.expanduser("~/.claude/projects/-home-huangshuai/memory"))
CHROMA_DB = Path(os.path.expanduser("~/.claude/.chroma_db"))


def grep_search(query: str, paths: list[Path], max_results: int = 10) -> list[dict]:
    """关键词搜索（快速，零依赖）."""
    results = []
    for search_path in paths:
        if not search_path.exists():
            continue
        try:
            cmd = ["grep", "-rnl", query, str(search_path)]
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if proc.returncode == 0:
                for line in proc.stdout.strip().split("\n"):
                    if line:
                        results.append({"source": line, "method": "grep"})
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

    return results[:max_results]


def grep_with_context(query: str, filepath: str, context_lines: int = 2) -> str:
    """获取匹配行的上下文."""
    try:
        cmd = ["grep", "-n", "-C", str(context_lines), query, filepath]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        return proc.stdout.strip() if proc.returncode == 0 else ""
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return ""


def semantic_search(query: str, max_results: int = 5) -> list[dict]:
    """语义搜索（需要 chromadb + sentence-transformers）."""
    try:
        import chromadb
        from chromadb.utils import embedding_functions
    except ImportError:
        return [{
            "source": "ERROR",
            "text": "语义搜索需要 chromadb 和 sentence-transformers。请运行: pip install chromadb sentence-transformers",
            "score": 0
        }]

    # 扫描文件
    files = []
    for f in MEMORY_ROOT.glob("*.md"):
        files.append(f)
    for f in CALENDAR_ROOT.glob("*/.md"):
        files.append(f)
    for f in CALENDAR_ROOT.glob("*/*/*.md"):
        files.append(f)

    if not files:
        return []

    # 构建/更新索引
    client = chromadb.PersistentClient(path=str(CHROMA_DB))
    try:
        ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
    except Exception:
        return [{
            "source": "ERROR",
            "text": "模型下载失败。首次使用需要联网下载 all-MiniLM-L6-v2（约 80MB）。",
            "score": 0
        }]

    collection = client.get_or_create_collection(
        name="claude-memory",
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"}
    )

    # 增量索引：只添加新文件或已修改的文件
    existing = set()
    try:
        existing = {m["source"] for m in collection.get()["metadatas"]}
    except Exception:
        pass  # 空集合

    new_files = [f for f in files if str(f) not in existing]
    if new_files:
        docs, metadatas, ids = [], [], []
        for f in new_files:
            try:
                content = f.read_text(encoding="utf-8")
            except Exception:
                continue
            # 按段落切分
            for i, para in enumerate(content.split("\n\n")):
                para = para.strip()
                if len(para) > 50:  # 跳过太短的段落
                    docs.append(para)
                    metadatas.append({"source": str(f), "chunk": i})
                    ids.append(f"{f.name}_{i}")
        if docs:
            collection.add(documents=docs, metadatas=metadatas, ids=ids)

    # 搜索
    results = collection.query(query_texts=[query], n_results=max_results)
    hits = []
    for i in range(len(results["documents"][0])):
        score = 1 - results["distances"][0][i]  # cosine distance → similarity
        if score > 0.3:  # 只返回相关度 > 0.3 的结果
            hits.append({
                "score": round(score, 2),
                "source": results["metadatas"][0][i]["source"],
                "text": results["documents"][0][i][:500]
            })

    return hits


def main():
    use_semantic = "--semantic" in sys.argv
    query = " ".join(arg for arg in sys.argv[1:] if arg != "--semantic")

    if not query:
        print("Usage: python3 memory-search.py [--semantic] 'search query'")
        sys.exit(1)

    search_paths = [
        CALENDAR_ROOT,  # ~/.claude/calendar/
        MEMORY_ROOT,    # ~/.claude/projects/.../memory/
    ]

    if use_semantic:
        print(f"=== 语义搜索: {query} ===\n")
        results = semantic_search(query)
        if not results:
            print("无结果。尝试用关键词搜索: 去掉 --semantic 参数")
        for r in results:
            if r["source"] == "ERROR":
                print(r["text"])
                continue
            print(f"[{r['score']}] {r['source']}")
            print(f"    {r['text'][:300]}")
            print()
    else:
        print(f"=== 关键词搜索: {query} ===\n")
        results = grep_search(query, search_paths)
        if not results:
            print("无结果。尝试：")
            print("  1. 换一个关键词")
            print("  2. 用 --semantic 做语义搜索（如果已安装 chromadb）")
            return

        for r in results:
            source = r["source"]
            print(f"📄 {source}")
            ctx = grep_with_context(query, source)
            if ctx:
                # 截取最相关的一段
                lines = ctx.split("\n")
                if len(lines) > 8:
                    print("\n".join(lines[:8]))
                    print(f"    ... (共 {len(lines)} 行匹配)")
                else:
                    print(ctx)
            print()


if __name__ == "__main__":
    main()
