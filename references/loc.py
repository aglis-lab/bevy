#!/usr/bin/env python3
"""Lines-of-code (LOC) counter tailored for the Bevy workspace."""

import argparse
import os
import sys

RUST_EXTENSIONS = (".rs",)
SHADER_EXTENSIONS = (".wesl", ".wgsl")

WORKSPACE_SECTIONS = [
    ("src", "src"),
    ("crates", "crates"),
    ("examples", "examples"),
    ("benches", "benches"),
    ("tests", "tests"),
    ("tests-integration", "tests-integration"),
    ("tools", "tools"),
]

SHADER_SECTIONS = [
    ("crates", "crates"),
    ("assets", "assets"),
    ("constants", "constants"),
]

IGNORED_DIRS = {
    ".git",
    ".idea",
    ".vscode",
    ".claude",
    "build",
    "target",
}


_LINE_COUNT_CACHE = {}


def count_code_lines(file_path):
    """Count non-empty, non-comment lines of code (supports nested /* */ and strings)."""
    cached = _LINE_COUNT_CACHE.get(file_path)
    if cached is not None:
        return cached

    total_loc = 0
    block_comment_depth = 0

    with open(file_path, "r", encoding="utf-8", errors="replace") as file:
        for raw_line in file:
            line = raw_line.strip()
            if not line:
                continue

            if block_comment_depth == 0:
                if line.startswith("//"):
                    continue
                if "/*" not in line and "//" not in line:
                    total_loc += 1
                    continue

            i = 0
            n = len(line)
            has_code = False
            in_string = False

            while i < n:
                if block_comment_depth > 0:
                    if line.startswith("/*", i):
                        block_comment_depth += 1
                        i += 2
                    elif line.startswith("*/", i):
                        block_comment_depth -= 1
                        i += 2
                    else:
                        i += 1
                    continue

                if in_string:
                    if line[i] == "\\" and i + 1 < n:
                        i += 2
                        continue
                    if line[i] == '"':
                        in_string = False
                    i += 1
                    continue

                if line.startswith("//", i):
                    break

                if line.startswith("/*", i):
                    block_comment_depth += 1
                    i += 2
                    continue

                if line[i] == '"':
                    in_string = True
                    has_code = True
                    i += 1
                    continue

                if not line[i].isspace():
                    has_code = True
                i += 1

            if has_code:
                total_loc += 1

    _LINE_COUNT_CACHE[file_path] = total_loc
    return total_loc


def collect_files(folder, extensions):
    discovered = []
    if not os.path.isdir(folder):
        return discovered

    for root, dirs, files in os.walk(folder):
        dirs[:] = sorted(d for d in dirs if d not in IGNORED_DIRS)
        for filename in sorted(files):
            if filename.endswith(extensions):
                discovered.append(os.path.realpath(os.path.join(root, filename)))
    return discovered


def count_section_rows(repo_root, sections, extensions, warn_missing=False):
    rows = []
    seen_files = {}

    for label, rel_path in sections:
        full_path = os.path.normpath(os.path.join(repo_root, rel_path))
        if not os.path.isdir(full_path):
            if warn_missing:
                print(f"warning: missing folder, skipped: {rel_path}", file=sys.stderr)
            continue

        files = collect_files(full_path, extensions)
        section_loc = 0
        for file_path in files:
            if file_path not in seen_files:
                seen_files[file_path] = count_code_lines(file_path)
            section_loc += seen_files[file_path]

        rows.append((label, section_loc, len(files)))

    total_loc = sum(seen_files.values())
    total_files = len(seen_files)
    return total_loc, total_files, rows


def discover_subdirectories(repo_root, parent_rel_path):
    parent_dir = os.path.join(repo_root, parent_rel_path)
    if not os.path.isdir(parent_dir):
        return []

    sections = []
    for entry in sorted(os.listdir(parent_dir)):
        if entry in IGNORED_DIRS or entry.startswith("."):
            continue
        rel_path = os.path.join(parent_rel_path, entry)
        if os.path.isdir(os.path.join(repo_root, rel_path)):
            sections.append((entry, rel_path))
    return sections


def sort_rows(rows, sort_by):
    if sort_by == "name":
        return sorted(rows, key=lambda r: r[0])
    if sort_by == "files":
        return sorted(rows, key=lambda r: (-r[2], -r[1], r[0]))
    return sorted(rows, key=lambda r: (-r[1], -r[2], r[0]))


def print_report(title, total_loc, total_files, rows, label_header="Path"):
    if not rows:
        print(f"{title}: no matching files found")
        return

    formatted_rows = [
        (label, f"{loc:,}", f"{file_count:,}") for label, loc, file_count in rows
    ]
    total_loc_str = f"{total_loc:,}"
    total_files_str = f"{total_files:,}"

    path_col_width = max(
        len(label_header), len("TOTAL"), *(len(label) for label, _, _ in formatted_rows)
    )
    loc_col_width = max(
        len("LOC"),
        *(len(loc_str) for _, loc_str, _ in formatted_rows),
        len(total_loc_str),
    )
    files_col_width = max(
        len("Files"),
        *(len(files_str) for _, _, files_str in formatted_rows),
        len(total_files_str),
    )

    border = (
        f"+-{'-' * path_col_width}-+-{'-' * loc_col_width}-+-{'-' * files_col_width}-+"
    )

    print(f"{title}")
    print(border)
    print(
        f"| {label_header.ljust(path_col_width)} | {'LOC'.rjust(loc_col_width)} | {'Files'.rjust(files_col_width)} |"
    )
    print(border)
    for label, loc_str, files_str in formatted_rows:
        print(
            f"| {label.ljust(path_col_width)} | {loc_str.rjust(loc_col_width)} | {files_str.rjust(files_col_width)} |"
        )
    print(border)
    print(
        f"| {'TOTAL'.ljust(path_col_width)} | {total_loc_str.rjust(loc_col_width)} | {total_files_str.rjust(files_col_width)} |"
    )
    print(border)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Count lines of code across the Bevy workspace."
    )
    parser.add_argument(
        "filters",
        nargs="*",
        help="Optional crate names, substrings, or relative paths to inspect (e.g. bevy_ecs render examples).",
    )
    parser.add_argument(
        "--sort",
        choices=("loc", "files", "name"),
        default="loc",
        help="Sort order for breakdown tables (default: loc).",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=None,
        help="Limit the crates breakdown table to the top N crates.",
    )
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="Only show workspace-level summaries (skip per-crate breakdown).",
    )
    parser.add_argument(
        "--rust-only",
        action="store_true",
        help="Only count Rust (.rs) files.",
    )
    parser.add_argument(
        "--shaders-only",
        action="store_true",
        help="Only count shader (.wesl, .wgsl) files.",
    )
    return parser.parse_args()


def resolve_filter_sections(repo_root, filters, crate_sections):
    matched = []
    seen_paths = set()

    for item in filters:
        normalized = item.strip("/")
        direct_path = os.path.join(repo_root, normalized)
        if os.path.isdir(direct_path):
            if normalized not in seen_paths:
                seen_paths.add(normalized)
                matched.append((normalized, normalized))
            continue

        matches = [
            (name, rel_path)
            for name, rel_path in crate_sections
            if item.lower() in name.lower()
        ]
        if matches:
            for name, rel_path in matches:
                if rel_path not in seen_paths:
                    seen_paths.add(rel_path)
                    matched.append((name, rel_path))
        else:
            print(f"warning: no crate or directory matched '{item}'", file=sys.stderr)

    return matched


def main():
    args = parse_args()
    if args.rust_only and args.shaders_only:
        print(
            "error: --rust-only and --shaders-only cannot be used together",
            file=sys.stderr,
        )
        sys.exit(2)

    repo_root = os.path.dirname(os.path.abspath(__file__))
    include_rust = not args.shaders_only
    include_shaders = not args.rust_only
    crate_sections = discover_subdirectories(repo_root, "crates")

    overall_loc = 0
    overall_files = 0

    if args.filters:
        target_sections = resolve_filter_sections(
            repo_root, args.filters, crate_sections
        )
        if not target_sections:
            sys.exit(1)

        if include_rust:
            rust_loc, rust_files, rust_rows = count_section_rows(
                repo_root, target_sections, RUST_EXTENSIONS
            )
            rust_rows = sort_rows(rust_rows, args.sort)
            print()
            print_report(
                "Filtered Rust (.rs) report",
                rust_loc,
                rust_files,
                rust_rows,
                label_header="Target",
            )
            overall_loc += rust_loc
            overall_files += rust_files

        if include_shaders:
            shader_loc, shader_files, shader_rows = count_section_rows(
                repo_root, target_sections, SHADER_EXTENSIONS
            )
            shader_rows = [
                row for row in sort_rows(shader_rows, args.sort) if row[2] > 0
            ]
            if shader_rows:
                print()
                print_report(
                    "Filtered Shaders (.wesl, .wgsl) report",
                    shader_loc,
                    shader_files,
                    shader_rows,
                    label_header="Target",
                )
                overall_loc += shader_loc
                overall_files += shader_files
    else:
        if include_rust:
            ws_loc, ws_files, ws_rows = count_section_rows(
                repo_root, WORKSPACE_SECTIONS, RUST_EXTENSIONS
            )
            ws_rows = sort_rows(ws_rows, args.sort)
            print()
            print_report("Bevy Workspace (Rust .rs)", ws_loc, ws_files, ws_rows)
            overall_loc += ws_loc
            overall_files += ws_files

            if not args.summary_only and crate_sections:
                crates_loc, crates_files, crate_rows = count_section_rows(
                    repo_root, crate_sections, RUST_EXTENSIONS
                )
                crate_rows = sort_rows(crate_rows, args.sort)
                title = "Bevy Crates (Rust .rs)"
                if args.top is not None and args.top > 0:
                    crate_rows = crate_rows[: args.top]
                    title = f"Bevy Crates (Top {args.top}, Rust .rs)"
                print()
                print_report(
                    title, crates_loc, crates_files, crate_rows, label_header="Crate"
                )

        if include_shaders:
            shader_loc, shader_files, shader_rows = count_section_rows(
                repo_root, SHADER_SECTIONS, SHADER_EXTENSIONS
            )
            shader_rows = [
                row for row in sort_rows(shader_rows, args.sort) if row[2] > 0
            ]
            print()
            print_report(
                "Bevy Shaders (.wesl, .wgsl)", shader_loc, shader_files, shader_rows
            )
            overall_loc += shader_loc
            overall_files += shader_files

    print()
    print("=" * 56)
    print(f"Overall total LOC   : {overall_loc:,}")
    print(f"Overall total files : {overall_files:,}")
    print("=" * 56)


if __name__ == "__main__":
    main()
