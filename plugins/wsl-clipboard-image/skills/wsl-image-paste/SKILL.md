---
name: wsl-image-paste
description: WSL上のClaude Codeでクリップボード画像をペーストする方法を提示する。ユーザーがスクリーンショット・画像をClaude Codeに貼り付けようとしている場合に自動適用。
---

# WSL クリップボード画像ペースト

## Ctrl+Shift+V の使い方

このプラグインが SessionStart フックで `ctrl+shift+v` → `chat:imagePaste` のキーバインドを自動設定する。

**手順:**
1. Windowsで画像をコピー（スクリーンショット含む）
2. Claude Codeのチャット入力欄にフォーカス
3. `Ctrl+Shift+V` を押す

## ネイティブペーストが動かない場合（WSL固有の問題）

Windows Terminalがキー入力を横取りするケースでは `chat:imagePaste` が機能しないことがある。
その場合はMCPツール経由でクリップボード画像を取得する。

**MCPツール利用手順:**
1. Windowsでコピーしたい画像をクリップボードにコピー
2. Claude Codeに「クリップボードの画像を使って」または「get_clipboard_image を呼んで」と入力
3. Claude が `wsl-clipboard` MCP サーバーの `get_clipboard_image` ツールを呼び出す
4. PowerShell 経由でWindowsクリップボードから画像を取得してClaude Codeに渡す

## 技術的な仕組み

- `chat:imagePaste`: Claude Code 組み込みの画像ペーストアクション
- `get_clipboard_image` MCP ツール: `powershell.exe` で `System.Windows.Forms.Clipboard::GetImage()` を実行し、一時ファイルに保存後 base64 エンコードして返す
- `wslpath -w` で WSL パス ↔ Windows パスを変換

## 動作要件

- WSL2 環境
- `powershell.exe` が WSL から実行可能（デフォルトで可能）
- `wslpath` コマンド（WSL2 デフォルトで利用可能）
