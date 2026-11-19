"""从 Markdown 文档中批量提取提示词模板，生成 data/prompts.json。

提取规则：
1. 扫描所有 ```...``` / ```markdown ...``` 代码块，每个块视为一条提示词。
2. 跟踪最近的 # / ## / ### 标题作为 category / sub_category。
3. 代码块内若含 "### Role" 或 "## Role"，则以 Role 标题下第一句作为 title；否则取块首非空行前 40 字。
4. 去重、过滤过短（<40 字）的块。
"""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

MD_PATH = Path("doc/提示词与工作流.md")
OUT_PATH = Path("data/prompts.json")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def extract_code_blocks(text: str) -> list[tuple[str, str]]:
    """返回 [(lang, content)]。"""
    pattern = re.compile(r"```(\w*)\n(.*?)```", re.DOTALL)
    return [(m.group(1) or "text", m.group(2).strip()) for m in pattern.finditer(text)]


def section_title_of(line: str) -> str | None:
    m = re.match(r"^(#{1,3})\s+(.+)$", line.strip())
    if m:
        return m.group(2).strip()
    return None


def _strip_markers(s: str) -> str:
    s = re.sub(r"^#{1,6}\s*", "", s)  # 去标题标记
    s = s.strip(" *`>").strip()
    # 去 emoji / 符号
    s = "".join(
        ch for ch in s if unicodedata.category(ch) not in ("So", "Sk") or ch.isalnum()
    )
    return s.strip()


def guess_title(block: str) -> str:
    """尽量从块中提取一条有意义的标题。"""
    lines = block.split("\n")
    # 优先：Role/Identity 标题下的第一行实质内容
    for i, raw in enumerate(lines):
        line = raw.strip()
        if re.match(r"^#{1,6}\s*(Role|Identity|角色)\b", line, re.I):
            # 取下一非空行
            for nxt in lines[i + 1 :]:
                nxt = nxt.strip(" *`>【】").strip()
                if nxt and len(nxt) > 2:
                    return _strip_markers(nxt)[:60]
    # 退回：第一个非标题、非空白、含中文的行
    for raw in lines:
        line = _strip_markers(raw)
        if len(line) > 2 and re.search(r"[一-鿿A-Za-z]", line):
            return line[:60]
    return "未命名提示词"


def main() -> None:
    text = read_text(MD_PATH)
    blocks = extract_code_blocks(text)

    lines = text.split("\n")
    cat_stack: list[str] = []
    results: list[dict] = []
    seen_titles: set[str] = set()

    block_idx = 0
    for line in lines:
        m = re.match(r"^(#{1,3})\s+(.+)$", line.strip())
        if m:
            level = len(m.group(1))
            title = m.group(2).strip()
            if level == 1:
                cat_stack = [title]
            elif level == 2:
                cat_stack = cat_stack[:1] + [title]
            elif level == 3:
                cat_stack = cat_stack[:2] + [title]
            continue

        if line.strip().startswith("```"):
            if block_idx < len(blocks):
                _lang, content = blocks[block_idx]
                block_idx += 1
            else:
                continue
            if len(content) < 40:
                continue
            category = cat_stack[1] if len(cat_stack) > 1 else (cat_stack[0] if cat_stack else "未分类")
            sub_category = cat_stack[2] if len(cat_stack) > 2 else ""
            t = guess_title(content)
            if t in seen_titles:
                continue
            seen_titles.add(t)
            results.append(
                {
                    "id": f"prompt_{len(results)+1:03d}",
                    "title": t,
                    "category": category,
                    "sub_category": sub_category,
                    "description": f"源自文档章节：{category}" + (f" > {sub_category}" if sub_category else ""),
                    "role": "",
                    "parameters": "",
                    "context": "",
                    "workflow": "",
                    "constraints": "",
                    "output_format": "",
                    "tools": "",
                    "full_text": content,
                    "favorite": False,
                }
            )

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"提取 {len(results)} 条提示词 -> {OUT_PATH}")
    for r in results[:12]:
        print(" ", r["id"], r["title"].encode("ascii", "replace").decode(), "|", r["category"], ">", r["sub_category"])


if __name__ == "__main__":
    main()

