"""
Compute relative widths of Mermaid SVGs and patch the matching
\\includegraphics / \\includesvg commands in .tex files.

The widest SVG gets width=\\textwidth, every other one
width=<w_i / w_max>\\textwidth, so all diagrams share one scale.

Matching is by file name stem: an SVG "diagrams/flow.svg" matches
\\includegraphics[...]{/path/path/flow.pdf}, {figs/flow}, {flow.svg}, ...

Usage:
    python patch_widths.py SVG_DIR TEX_DIR [--dry-run] [--no-backup] [--digits 3]
"""

import argparse
import os
import re
import shutil
import sys
from pathlib import Path

USE_COLOR = sys.stdout.isatty() and "NO_COLOR" not in os.environ
RED = "\033[31m" if USE_COLOR else ""
GREEN = "\033[32m" if USE_COLOR else ""
RESET = "\033[0m" if USE_COLOR else ""


VIEWBOX_RE = re.compile(
    r'viewBox\s*=\s*"\s*[-\d.eE]+[\s,]+[-\d.eE]+[\s,]+([\d.eE]+)[\s,]+([\d.eE]+)'
)
MAXWIDTH_RE = re.compile(r"max-width:\s*([\d.]+)px")
WIDTH_ATTR_RE = re.compile(r'<svg[^>]*\swidth\s*=\s*"([\d.]+)(?:px)?"')

# \includegraphics[opts]{path}  or  \includesvg[opts]{path}
INCLUDE_RE = re.compile(
    r"(?P<cmd>\\include(?:graphics|svg))(?P<star>\*?)\s*"
    r"(?:\[(?P<opts>[^\]]*)\])?\s*"
    r"\{(?P<path>[^}]+)\}"
)


def svg_width(path: Path) -> float | None:
    text = path.read_text(encoding="utf-8", errors="ignore")
    head = text[: text.find(">", text.find("<svg")) + 1] or text[:5000]
    for rx in (VIEWBOX_RE, MAXWIDTH_RE, WIDTH_ATTR_RE):
        m = rx.search(head)
        if m:
            return float(m.group(1))
    return None


def collect_widths(svg_dir: Path) -> dict[str, float]:
    widths = {}
    for f in sorted(svg_dir.rglob("*.svg")):
        w = svg_width(f)
        if w is None:
            print(f"  ! no width found in {f}, skipped", file=sys.stderr)
            continue
        if f.stem in widths:
            print(f"  ! duplicate name {f.stem}, using {f}", file=sys.stderr)
        widths[f.stem] = w
    return widths


def stem_of(include_path: str) -> str:
    name = include_path.strip().replace("\\", "/").rsplit("/", 1)[-1]
    for ext in (".pdf", ".svg", ".png", ".eps", ".pdf_tex"):
        if name.lower().endswith(ext):
            return name[: -len(ext)]
    return name


def new_options(old: str | None, factor: str) -> str:
    """Drop existing width/scale, keep everything else, add the new width."""
    keep = []
    if old:
        for opt in old.split(","):
            key = opt.split("=", 1)[0].strip().lower()
            if opt.strip() and key not in ("width", "scale"):
                keep.append(opt.strip())
    width = r"width=\textwidth" if factor == "1" else rf"width={factor}\textwidth"
    return ",".join([width] + keep)


def patch_tex(tex: Path, factors: dict[str, str], dry: bool, backup: bool):
    src = tex.read_text(encoding="utf-8")
    changes = []

    def repl(m: re.Match) -> str:
        stem = stem_of(m.group("path"))
        if stem not in factors:
            return m.group(0)
        opts = new_options(m.group("opts"), factors[stem])
        new = f"{m.group('cmd')}{m.group('star')}[{opts}]{{{m.group('path')}}}"
        if new != m.group(0):
            changes.append((m.group(0), new))
        return new

    out = INCLUDE_RE.sub(repl, src)
    if changes:
        print(f"\n{tex}")
        for old, new in changes:
            print(f"  {RED}- {old}{RESET}")
            print(f"  {GREEN}+ {new}{RESET}")
        if not dry:
            if backup:
                shutil.copy2(tex, tex.with_suffix(tex.suffix + ".bak"))
            tex.write_text(out, encoding="utf-8")
    return len(changes)


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("svg_dir", type=Path)
    ap.add_argument("tex_dir", type=Path)
    ap.add_argument("--dry-run", action="store_true", help="show changes only")
    ap.add_argument("--no-backup", action="store_true", help="don't write .bak files")
    ap.add_argument("--digits", type=int, default=3, help="decimal places (default 3)")
    args = ap.parse_args()

    widths = collect_widths(args.svg_dir)
    if not widths:
        sys.exit("No usable SVGs found.")
    w_max = max(widths.values())

    factors = {}
    print(f"Widest: {max(widths, key=widths.get)} ({w_max:g}px)\n")
    for stem, w in sorted(widths.items(), key=lambda kv: -kv[1]):
        x = w / w_max
        factors[stem] = "1" if x >= 1 else f"{x:.{args.digits}f}"
        print(f"  {stem:40s} {w:10.1f}px  -> {factors[stem]}")

    total, used = 0, set()
    for tex in sorted(args.tex_dir.rglob("*.tex")):
        n = patch_tex(tex, factors, args.dry_run, not args.no_backup)
        total += n
        if n:
            used.update(s for s in factors if s in tex.read_text(encoding="utf-8"))

    print(f"\n{total} include(s) {'would be ' if args.dry_run else ''}patched.")
    unused = sorted(set(factors) - used)
    if unused:
        print("SVGs not referenced in any .tex or already patched:", ", ".join(unused))


if __name__ == "__main__":
    main()


# python3 mermaid/patch.py mermaid/svg tex/chapters --dry-run
# python3 mermaid/patch.py mermaid/svg tex/chapters
