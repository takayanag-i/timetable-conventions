"""Markdownの機械的に検査できる規約を確かめる。使い方はSKILL.mdが持つ。"""

import os
import re
import subprocess
import sys
import unicodedata as ud
from pathlib import Path

N = lambda s: ud.normalize("NFC", s)

# 制約定義マスタの名称が持つ限定辞。注釈ではなく名前の一部
NAME_QUALIFIERS = {"教員", "講座", "会議", "学級", "教室"}


def markdown_files(root):
    """gitが追跡するMarkdownと、無視していないMarkdownを返す。"""
    r = subprocess.run(
        ["git", "-C", root, "ls-files", "-z", "--cached", "--others",
         "--exclude-standard", "--", "*.md", ":!:.agents/**"],
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        sys.exit(f"doc-lint: {root} でgitが読めない\n  {r.stderr.strip()}")
    return sorted(Path(root) / p for p in r.stdout.split("\0") if p)


def parse(t):
    if not t.startswith("---\n"):
        return None, t
    end = t.find("\n---\n", 3)
    if end < 0:
        return None, t
    return t[4:end], t[end + 5 :]


def listfield(fm, name):
    """フロントマターのリストを読む。値が同じ行に無い場合だけ後続行を辿る。"""
    m = re.search(rf"^{name}:[ \t]*(.*)$", fm, re.M)
    if not m:
        return None
    if m.group(1).strip().startswith("["):
        return []
    items = []
    for line in fm[m.end() :].split("\n"):
        if re.match(r"^\s*-\s+", line):
            items.append(N(line.split("-", 1)[1].strip().strip("\"'")))
        elif line.strip():
            break
    return items


def collect(root, docs_root):
    info, nofm, plain = {}, [], []
    for p in markdown_files(root):
        disp = N(str(p.relative_to(root)))
        text = p.read_text(encoding="utf-8")
        fm, body = parse(text)
        design = docs_root is not None and p.is_relative_to(docs_root) and p.name != "CLAUDE.md"
        if not design:
            plain.append((disp, text))
            continue
        if fm is None:
            nofm.append(disp)
            plain.append((disp, text))
            continue
        info[N(str(p.relative_to(docs_root)))] = dict(
            sot=(re.search(r"^source_of_truth:[ \t]*(\S+)", fm, re.M) or [None, None])[1],
            inp=listfield(fm, "input_documents"),
            out=listfield(fm, "output_documents"),
            body=body,
            text=text,
            disp=disp,
        )
    return info, nofm, plain


def check_graph(info, nofm, issues):
    def resolve(t):
        t = N(t.strip().rstrip("/"))
        if t in info:
            return t
        return t + "/README.md" if t + "/README.md" in info else None

    def covers(cands, me):
        d = os.path.dirname(me)
        return me in cands or d in cands or d + "/README.md" in cands

    for me in nofm:
        issues.append(("フロントマター無し", me, ""))
    for me, d in sorted(info.items()):
        if d["sot"] is None:
            issues.append(("source_of_truth無し", d["disp"], ""))
        for field, other, arrow in (("out", "inp", "output→"), ("inp", "out", "←input")):
            if d[field] is None:
                issues.append(
                    (f"{'output' if field == 'out' else 'input'}_documents無し", d["disp"], "")
                )
                continue
            for tgt in d[field]:
                k = resolve(tgt)
                if k is None:
                    issues.append(("宛先が存在しない", d["disp"], f"{arrow} {tgt}"))
                    continue
                cands = [resolve(x) or N(x.rstrip("/")) for x in (info[k][other] or [])]
                if not covers(cands, me):
                    issues.append(("辺が片側だけ", d["disp"], f"{arrow} {tgt}"))


def check_docs_body(docs_root, info, issues):
    for me, d in sorted(info.items()):
        base = os.path.dirname(me)
        for m in re.finditer(r"\[[^\]]*\]\(([^)#]+?)(?:#[^)]*)?\)", d["body"]):
            t = m.group(1).strip()
            if t.startswith(("http://", "https://", "mailto:")):
                continue
            if not (docs_root / N(os.path.normpath(os.path.join(base, t)))).exists():
                issues.append(("リンク切れ", d["disp"], t))
        for m in re.finditer(r"^.*(TODO|将来|変更予定|旧:|従来).*$", d["body"], re.M):
            issues.append(("確定していない記述", d["disp"], m.group(0).strip()[:60]))


def check_style(disp, text, issues):
    infence = False
    for line in text.split("\n"):
        if line.lstrip().startswith("```"):
            infence = not infence
            continue
        if infence or line.lstrip().startswith("$$"):
            continue
        prose = re.sub(r"`[^`]*`", "", line)
        for m in re.finditer(r"\*\*[^*\n]+\*\*", prose):
            issues.append(("太字", disp, m.group(0)[:40]))
        for m in re.finditer(r"（([^）]{1,40})）", prose):
            if m.group(1) not in NAME_QUALIFIERS:
                issues.append(("括弧注釈", disp, m.group(0)[:40]))


def main(root):
    root = Path(root).resolve()
    docs_root = root if root.name == "docs" else root / "docs"
    if not docs_root.is_dir():
        docs_root = None

    info, nofm, plain = collect(root, docs_root)
    issues = []
    check_graph(info, nofm, issues)
    check_docs_body(docs_root, info, issues)
    for d in sorted(info.values(), key=lambda v: v["disp"]):
        check_style(d["disp"], d["text"], issues)
    for disp, text in plain:
        check_style(disp, text, issues)

    grouped = {}
    for kind, me, detail in issues:
        grouped.setdefault(kind, []).append((me, detail))
    print(f"Markdown {len(info) + len(plain)}件 / 設計文書 {len(info)}件 / 指摘 {len(issues)}件")
    for kind, rows in grouped.items():
        print(f"\n## {kind} {len(rows)}件")
        for me, detail in rows:
            print(f"  {me}  {detail}")
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "docs"))
