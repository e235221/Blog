#!/usr/bin/env python3
"""
Generate site-ready Markdown articles and manifest from Obsidian-style vault content.

Source structure (within this repository):
  vault/
    posts/    ... original Obsidian Markdown files (with optional YAML front matter)
    assets/   ... image or media files referenced from the posts

Output structure (overwritten on each run):
  posts/              ... sanitized Markdown files served by the static site
  posts/posts.json    ... manifest consumed by scripts/main.js
  assets/blog/        ... copied assets referenced by the generated Markdown
"""

from __future__ import annotations

import ast
import json
import re
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_POSTS_DIR = REPO_ROOT / "vault" / "posts"
SOURCE_ASSETS_DIR = REPO_ROOT / "vault" / "assets"
OUTPUT_POSTS_DIR = REPO_ROOT / "posts"
OUTPUT_ASSETS_DIR = REPO_ROOT / "assets" / "blog"
MANIFEST_PATH = OUTPUT_POSTS_DIR / "posts.json"

IMAGE_EMBED_PATTERN = re.compile(r"!\[\[(.+?)\]\]")
WIKILINK_PATTERN = re.compile(r"\[\[(.+?)\]\]")


@dataclass
class PostMeta:
    title: str
    date: str
    tags: List[str]
    summary: str
    slug: str
    source_path: Path

    @property
    def output_markdown_path(self) -> Path:
        return OUTPUT_POSTS_DIR / f"{self.slug}.md"

    def to_dict(self) -> Dict[str, object]:
        return {
            "title": self.title,
            "date": self.date,
            "tags": self.tags,
            "summary": self.summary,
            "slug": self.slug,
            "contentPath": f"posts/{self.slug}.md",
        }


def load_markdown(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def clean_scalar(value: str) -> str:
    value = value.strip()
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    return value


def split_front_matter(raw: str) -> (Dict[str, object], str):
    lines = raw.splitlines()
    if not lines:
        return {}, raw

    if lines[0].strip() != "---":
        return {}, raw

    fm_lines: List[str] = []
    end_index: Optional[int] = None
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            end_index = idx
            break
        fm_lines.append(lines[idx])

    if end_index is None:
        # Malformed front matter; treat entire document as body
        return {}, raw

    body = "\n".join(lines[end_index + 1 :])
    front_matter: Dict[str, object] = {}

    idx = 0
    while idx < len(fm_lines):
        line = fm_lines[idx]
        if not line.strip() or line.strip().startswith("#"):
            idx += 1
            continue

        if ":" not in line:
            idx += 1
            continue

        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()

        # Handle multi-line list values (YAML style)
        if value == "" and idx + 1 < len(fm_lines) and fm_lines[idx + 1].strip().startswith("-"):
            items = []
            idx += 1
            while idx < len(fm_lines) and fm_lines[idx].strip().startswith("-"):
                items.append(fm_lines[idx].strip()[1:].strip())
                idx += 1
            front_matter[key] = items
            continue

        if value.startswith("[") and value.endswith("]"):
            try:
                parsed = ast.literal_eval(value)
                if isinstance(parsed, list):
                    front_matter[key] = [clean_scalar(str(item).strip()) for item in parsed]
                else:
                    front_matter[key] = clean_scalar(str(parsed))
            except (ValueError, SyntaxError):
                front_matter[key] = [clean_scalar(item.strip()) for item in value.strip("[]").split(",") if item.strip()]
        else:
            front_matter[key] = clean_scalar(value)

        idx += 1

    return front_matter, body


def slug_from_filename(path: Path) -> str:
    slug = path.stem.strip().replace(" ", "-")
    slug = slug.replace("/", "-")
    return slug or "post"


def normalise_tags(raw_tags: object) -> List[str]:
    if isinstance(raw_tags, list):
        return [clean_scalar(str(tag).strip()) for tag in raw_tags if str(tag).strip()]
    if isinstance(raw_tags, str):
        return [clean_scalar(tag.strip()) for tag in raw_tags.split(",") if tag.strip()]
    return []


def replace_obsidian_embeds(body: str) -> str:
    def image_repl(match: re.Match) -> str:
        target = match.group(1)
        parts = [part.strip() for part in target.split("|") if part.strip()]
        filename = parts[0] if parts else "image.png"
        alt_text = Path(filename).stem
        return f"![{alt_text}](assets/blog/{filename})"

    body = IMAGE_EMBED_PATTERN.sub(image_repl, body)

    def link_repl(match: re.Match) -> str:
        target = match.group(1)
        parts = [part.strip() for part in target.split("|") if part.strip()]
        label = parts[-1] if parts else ""
        return label

    body = WIKILINK_PATTERN.sub(link_repl, body)
    return body


def extract_summary(body: str, fallback: str = "") -> str:
    clean = re.sub(r"!\[.*?\]\(.*?\)", "", body)  # remove images
    clean = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", clean)  # links -> text
    paragraphs = [para.strip() for para in clean.split("\n\n") if para.strip()]
    if paragraphs:
        summary = paragraphs[0]
        if len(summary) > 140:
            summary = summary[:137].rstrip() + "..."
        return summary
    return fallback


def ensure_output_dirs() -> None:
    OUTPUT_POSTS_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_ASSETS_DIR.mkdir(parents=True, exist_ok=True)


def clean_output_dirs() -> None:
    if OUTPUT_POSTS_DIR.exists():
        for md_file in OUTPUT_POSTS_DIR.glob("*.md"):
            md_file.unlink()
    if OUTPUT_ASSETS_DIR.exists():
        shutil.rmtree(OUTPUT_ASSETS_DIR)
    OUTPUT_ASSETS_DIR.mkdir(parents=True, exist_ok=True)


def copy_assets() -> None:
    if not SOURCE_ASSETS_DIR.exists():
        return
    for src in SOURCE_ASSETS_DIR.rglob("*"):
        if src.is_dir():
            continue
        relative = src.relative_to(SOURCE_ASSETS_DIR)
        dest = OUTPUT_ASSETS_DIR / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)


def build_post(path: Path) -> Optional[PostMeta]:
    raw = load_markdown(path)
    front_matter, body = split_front_matter(raw)

    title = front_matter.get("title") or path.stem
    date = str(front_matter.get("date") or "")
    tags = normalise_tags(front_matter.get("tags"))
    summary = str(front_matter.get("summary") or "")
    slug = str(front_matter.get("slug") or slug_from_filename(path))

    body = replace_obsidian_embeds(body)
    body = body.replace("assets/images/", "assets/blog/")
    body = body.strip()
    if not summary:
        summary = extract_summary(body)

    if not date:
        # Default to today's date if missing
        date = datetime.today().strftime("%Y-%m-%d")

    meta = PostMeta(
        title=str(title).strip(),
        date=date.strip(),
        tags=tags,
        summary=summary.strip(),
        slug=slug.strip(),
        source_path=path,
    )

    meta.output_markdown_path.write_text(body + ("\n" if not body.endswith("\n") else ""), encoding="utf-8")
    return meta


def sort_posts(posts: List[PostMeta]) -> List[PostMeta]:
    def sort_key(post: PostMeta):
        try:
            return datetime.fromisoformat(post.date)
        except ValueError:
            return datetime.min

    return sorted(posts, key=sort_key, reverse=True)


def main() -> None:
    if not SOURCE_POSTS_DIR.exists():
        raise SystemExit(f"Source directory not found: {SOURCE_POSTS_DIR}")

    ensure_output_dirs()
    clean_output_dirs()
    copy_assets()

    posts: List[PostMeta] = []
    for md_file in sorted(SOURCE_POSTS_DIR.glob("*.md")):
        meta = build_post(md_file)
        if meta:
            posts.append(meta)

    posts = sort_posts(posts)
    manifest_data = [post.to_dict() for post in posts]
    MANIFEST_PATH.write_text(json.dumps(manifest_data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Generated {len(posts)} posts.")


if __name__ == "__main__":
    main()
