#!/usr/bin/env python3
"""Gera metadata.json no formato do plugin Metadata Extractor (grafo do Perlite)."""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

WIKILINK = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]")
TAG = re.compile(r"(?<!\w)#([a-zA-Z0-9_/-]+)")
FENCE = re.compile(r"```.*?```", re.DOTALL)

DEFAULT_VAULT = Path("/vault")


def strip_fences(text: str) -> str:
    return FENCE.sub("", text)


def collect_notes(vault: Path) -> dict[str, Path]:
    notes: dict[str, Path] = {}
    for path in vault.rglob("*.md"):
        if any(part.startswith(".") for part in path.parts):
            continue
        notes[path.stem] = path
    return notes


def build_metadata(vault: Path) -> list[dict]:
    notes = collect_notes(vault)
    by_name: dict[str, dict] = {}

    for name, path in notes.items():
        rel = path.relative_to(vault).as_posix()
        body = strip_fences(path.read_text(encoding="utf-8"))
        entry: dict = {"fileName": name, "relativePath": rel}

        links = []
        for match in WIKILINK.finditer(body):
            target = match.group(1).strip()
            link = {"link": target}
            target_path = notes.get(Path(target).stem)
            if target_path is not None:
                link["relativePath"] = target_path.relative_to(vault).as_posix()
            if link not in links:
                links.append(link)
        if links:
            entry["links"] = links

        tags = sorted({tag.lower() for tag in TAG.findall(body)})
        if tags:
            entry["tags"] = tags

        by_name[name] = entry

    for entry in by_name.values():
        backlinks = []
        for other in by_name.values():
            for link in other.get("links", []):
                if link.get("relativePath") == entry["relativePath"]:
                    backlinks.append(
                        {
                            "fileName": other["fileName"],
                            "link": entry["fileName"],
                            "relativePath": other["relativePath"],
                        }
                    )
        if backlinks:
            entry["backlinks"] = backlinks

    return list(by_name.values())


def vault_path() -> Path:
    raw = os.environ.get("VAULT_PATH")
    if raw:
        return Path(raw)
    # Fora do container, o script mora em docker/perlite/.
    try:
        return Path(__file__).resolve().parents[2] / "obsidian" / "vaults" / "Pessoal"
    except IndexError:
        return DEFAULT_VAULT


def write_metadata(vault: Path) -> Path:
    out = vault / "metadata.json"
    payload = json.dumps(build_metadata(vault), ensure_ascii=False, indent=2) + "\n"
    if out.exists() and out.read_text(encoding="utf-8") == payload:
        return out
    tmp = out.with_suffix(".json.tmp")
    tmp.write_text(payload, encoding="utf-8")
    tmp.replace(out)
    return out


def main() -> None:
    vault = vault_path()
    print(f"escreveu {write_metadata(vault)}")


if __name__ == "__main__":
    main()
