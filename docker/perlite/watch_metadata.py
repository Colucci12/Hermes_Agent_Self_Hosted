#!/usr/bin/env python3
"""Regenera o grafo do Perlite quando nasce ou muda nota no vault.

Nao usa o Hermes: loop bobo, so olha os .md.
"""
from __future__ import annotations

import os
import time
from pathlib import Path

from build_metadata import vault_path, write_metadata


def notes_fingerprint(vault: Path) -> str:
    rows: list[str] = []
    for path in sorted(vault.rglob("*.md")):
        if any(part.startswith(".") for part in path.parts):
            continue
        stat = path.stat()
        rows.append(f"{path.relative_to(vault)}:{stat.st_mtime_ns}:{stat.st_size}")
    return "\n".join(rows)


def main() -> None:
    vault = vault_path()
    interval = max(2, int(os.environ.get("INTERVAL_SECONDS", "10")))
    last = None
    print(f"olhando {vault} a cada {interval}s")
    while True:
        if not vault.is_dir():
            print(f"vault ainda nao existe: {vault}")
            time.sleep(interval)
            continue
        current = notes_fingerprint(vault)
        if current != last or not (vault / "metadata.json").exists():
            try:
                write_metadata(vault)
                print(f"grafo atualizado ({len(current.splitlines()) if current else 0} notas)")
                last = current
            except Exception as exc:
                print(f"falhou: {exc}")
        time.sleep(interval)


if __name__ == "__main__":
    main()
