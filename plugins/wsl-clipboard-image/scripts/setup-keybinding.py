#!/usr/bin/env python3
"""SessionStart hook: Ctrl+Shift+V -> chat:imagePaste をkeybindings.jsonに追加する。"""

import json
import os
import sys

KB_FILE = os.path.expanduser("~/.claude/keybindings.json")
BINDING_KEY = "ctrl+shift+v"
BINDING_ACTION = "chat:imagePaste"
CONTEXT = "Chat"

DEFAULT_KB = {
    "$schema": "https://www.schemastore.org/claude-code-keybindings.json",
    "$docs": "https://code.claude.com/docs/en/keybindings",
    "bindings": []
}


def load():
    if not os.path.exists(KB_FILE):
        return dict(DEFAULT_KB)
    with open(KB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save(data):
    os.makedirs(os.path.dirname(KB_FILE), exist_ok=True)
    with open(KB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def already_bound(data):
    for ctx in data.get("bindings", []):
        if ctx.get("context") == CONTEXT:
            if BINDING_KEY in ctx.get("bindings", {}):
                return True
    return False


def add_binding(data):
    bindings = data.setdefault("bindings", [])
    for ctx in bindings:
        if ctx.get("context") == CONTEXT:
            ctx.setdefault("bindings", {})[BINDING_KEY] = BINDING_ACTION
            return
    bindings.append({"context": CONTEXT, "bindings": {BINDING_KEY: BINDING_ACTION}})


def main():
    data = load()
    if already_bound(data):
        return
    add_binding(data)
    save(data)
    print(f"[wsl-clipboard-image] keybinding added: {BINDING_KEY} -> {BINDING_ACTION}", file=sys.stderr)


if __name__ == "__main__":
    main()
