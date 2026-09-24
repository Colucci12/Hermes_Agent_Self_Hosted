#!/usr/bin/env python3
"""Ajustes de boot no volume /opt/data (nao vai para o Git).

- memory.provider: holographic no config.yaml
- OBSIDIAN_VAULT_PATH no .env do Hermes — e o que a skill oficial le
  (${HERMES_HOME}/.env). O compose tambem expoe a mesma variavel.
"""
from __future__ import annotations

import os
import re
from pathlib import Path

CONFIG = Path("/opt/data/config.yaml")
ENV_FILE = Path("/opt/data/.env")
PROVIDER_LINE = "  provider: holographic"
VAULT_KEY = "OBSIDIAN_VAULT_PATH"


def ensure(text: str) -> str:
    if re.search(r"(?m)^memory:\n(?:  .*\n)*?  provider: holographic\s*$", text):
        return text

    def replace_block(match: re.Match[str]) -> str:
        block = match.group(0)
        if re.search(r"(?m)^  provider:", block):
            return re.sub(r"(?m)^  provider:.*$", PROVIDER_LINE, block, count=1)
        return block.replace("memory:\n", f"memory:\n{PROVIDER_LINE}\n", 1)

    updated, count = re.subn(r"(?ms)^memory:\n(?:  .*\n)*", replace_block, text, count=1)
    if count:
        return updated
    suffix = "" if text.endswith("\n") or not text else "\n"
    return text + suffix + f"\nmemory:\n{PROVIDER_LINE}\n"


def ensure_obsidian_env() -> None:
    path = os.environ.get(VAULT_KEY, "").strip()
    if not path:
        print("obsidian: OBSIDIAN_VAULT_PATH vazio, nao grava")
        return

    ENV_FILE.parent.mkdir(parents=True, exist_ok=True)
    text = ENV_FILE.read_text(encoding="utf-8") if ENV_FILE.exists() else ""
    line = f"{VAULT_KEY}={path}"
    if re.search(rf"(?m)^{VAULT_KEY}=", text):
        new = re.sub(rf"(?m)^{VAULT_KEY}=.*$", line, text, count=1)
    else:
        suffix = "" if not text or text.endswith("\n") else "\n"
        new = text + suffix + "\n# Skill obsidian (HERMES_HOME/.env)\n" + line + "\n"

    if new != text:
        ENV_FILE.write_text(new, encoding="utf-8")
        print(f"obsidian: gravou {line} no .env")
    else:
        print(f"obsidian: {line} ja estava no .env")


def main() -> None:
    CONFIG.parent.mkdir(parents=True, exist_ok=True)
    current = CONFIG.read_text(encoding="utf-8") if CONFIG.exists() else ""
    new = ensure(current)
    if new != current:
        CONFIG.write_text(new, encoding="utf-8")
        print("holographic: gravou memory.provider no config.yaml")
    else:
        print("holographic: ja estava ligado")
    ensure_obsidian_env()


if __name__ == "__main__":
    main()
