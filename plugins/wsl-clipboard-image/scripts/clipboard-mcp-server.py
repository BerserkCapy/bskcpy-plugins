#!/usr/bin/env python3
"""
MCP server: WSL上でWindowsクリップボードの画像をClaude Codeに渡す。
標準入出力でJSON-RPCをやりとりするstdio型MCPサーバー。
"""

import sys
import json
import subprocess
import base64
import os
import logging
import tempfile

log = logging.getLogger(__name__)

PROTOCOL_VERSION = "2024-11-05"
SERVER_INFO = {"name": "wsl-clipboard", "version": "1.0.0"}

TOOLS = [
    {
        "name": "get_clipboard_image",
        "description": (
            "Windowsクリップボードにある最新の画像を取得する。"
            "WSL環境でCtrl+Shift+Vによる画像ペーストが機能しない場合に使用。"
        ),
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
]


def _is_wsl():
    return os.path.exists("/proc/version") and "microsoft" in open("/proc/version").read().lower()


def get_clipboard_image_wsl():
    """PowerShell経由でWindowsクリップボードの画像を取得してbase64で返す。"""
    if not _is_wsl():
        raise RuntimeError("このツールはWSL環境専用です")

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp_path = tmp.name

    # wslpath -w で WSLパス→Windowsパスに変換
    win_path_result = subprocess.run(
        ["wslpath", "-w", tmp_path],
        capture_output=True, text=True
    )
    if win_path_result.returncode != 0:
        os.unlink(tmp_path)
        raise RuntimeError(f"wslpathの実行に失敗: {win_path_result.stderr}")

    win_path = win_path_result.stdout.strip()

    ps_script = (
        "Add-Type -Assembly System.Windows.Forms; "
        f"$img = [System.Windows.Forms.Clipboard]::GetImage(); "
        f"if ($img -eq $null) {{ Write-Error 'NoImage'; exit 1 }} "
        f"$img.Save('{win_path}'); "
        f"Write-Output 'OK'"
    )

    result = subprocess.run(
        ["powershell.exe", "-NonInteractive", "-NoProfile", "-Command", ps_script],
        capture_output=True, text=True
    )

    try:
        if result.returncode != 0 or "OK" not in result.stdout:
            raise RuntimeError("クリップボードに画像がありません")

        with open(tmp_path, "rb") as f:
            image_bytes = f.read()

        if len(image_bytes) == 0:
            raise RuntimeError("クリップボードに画像がありません")

        return base64.b64encode(image_bytes).decode()
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def send(obj):
    sys.stdout.write(json.dumps(obj, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def respond(msg_id, result):
    send({"jsonrpc": "2.0", "id": msg_id, "result": result})


def error_response(msg_id, code, message):
    send({"jsonrpc": "2.0", "id": msg_id, "error": {"code": code, "message": message}})


def handle(req):
    method = req.get("method", "")
    msg_id = req.get("id")
    params = req.get("params", {})

    if method == "initialize":
        respond(msg_id, {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {"tools": {}},
            "serverInfo": SERVER_INFO
        })

    elif method == "tools/list":
        respond(msg_id, {"tools": TOOLS})

    elif method == "tools/call":
        tool_name = params.get("name", "")
        if tool_name == "get_clipboard_image":
            try:
                img_b64 = get_clipboard_image_wsl()
                respond(msg_id, {
                    "content": [
                        {
                            "type": "image",
                            "data": img_b64,
                            "mimeType": "image/png"
                        }
                    ]
                })
            except Exception as e:
                respond(msg_id, {
                    "content": [{"type": "text", "text": f"エラー: {e}"}],
                    "isError": True
                })
        else:
            error_response(msg_id, -32601, f"Unknown tool: {tool_name}")

    elif method == "notifications/initialized":
        pass  # 通知なので返答不要

    elif method == "ping":
        respond(msg_id, {})

    else:
        if msg_id is not None:
            error_response(msg_id, -32601, f"Method not found: {method}")


def main():
    for raw_line in sys.stdin:
        raw_line = raw_line.strip()
        if not raw_line:
            continue
        try:
            req = json.loads(raw_line)
        except json.JSONDecodeError as e:
            log.warning(f"JSON parse error: {e}")
            continue
        try:
            handle(req)
        except Exception as e:
            log.error(f"Unhandled error: {e}", exc_info=True)
            msg_id = req.get("id")
            if msg_id is not None:
                error_response(msg_id, -32603, f"Internal error: {e}")


if __name__ == "__main__":
    main()
