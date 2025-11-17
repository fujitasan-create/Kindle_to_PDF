# Kindle to PDF

Kindleアプリ（ブラウザでも可能)の画面を自動キャプチャしてPDFに変換するツールです。

## 機能

- Kindleアプリの画面を自動でキャプチャ
- キャプチャした画像をPDFに変換
- 画像サイズに合わせたPDFページサイズの自動調整
- ページ読み込み待機機能（読み込み完了を待ってからキャプチャ）

## 必要な環境

- Python 3.11以上
- [uv](https://github.com/astral-sh/uv)（パッケージ管理ツール）
- Windows（pyautoguiを使用）

## インストール

1. このリポジトリをクローンまたはダウンロード
2. プロジェクトディレクトリに移動
3. 依存関係をインストール（uvが自動で仮想環境を作成します）

```bash
uv sync
```

## 使い方

### 基本的な使い方

1. Kindleアプリを開き、変換したい書籍を表示
2. 1ページ目を表示した状態で準備
3. 以下のコマンドを実行：

```bash
uv run python main.py --start-page 1 --end-page 10 --title "書籍タイトル"
```

### コマンドオプション

#### キャプチャとPDF変換を一括実行（推奨）

```bash
uv run python main.py --start-page 1 --end-page 100 --title "書籍タイトル"
```

#### キャプチャのみ実行

```bash
uv run python main.py --capture-only --start-page 1 --end-page 100
```

#### PDF変換のみ実行（既存の画像から）

```bash
uv run python main.py --pdf-only --title "書籍タイトル"
```

### パラメータ説明

- `--start-page N`: 開始ページ番号
- `--end-page N`: 終了ページ番号
- `--title "タイトル"`: PDFファイルのタイトル
- `--capture-only`: キャプチャのみ実行（PDF変換は実行しない）
- `--pdf-only`: PDF変換のみ実行（キャプチャは実行しない）

## 設定

`config.toml`ファイルで設定を変更できます。

```toml
[capture]
# キャプチャ開始前の待機時間（秒）
wait_time = 5
# ページをめくった後の待機時間（秒）
page_load_wait = 3.0
# キャプチャ前の追加待機時間（秒）
capture_wait = 0.5

# 画像のDPI（解像度）設定
# Windowsのスクリーンショットは通常96 DPI、Macは72 DPI
image_dpi = 96

[output]
# 出力ディレクトリ
output_dir = "output"
pdf_parent_dir = "output_pdf"
```

### 設定項目の説明

- `wait_time`: キャプチャ開始前の待機時間（Kindleウィンドウを最前面にする時間）
- `page_load_wait`: ページをめくった後の待機時間（ページが読み込まれるまで待機）
- `capture_wait`: キャプチャ前の追加待機時間（ページが完全に表示されるまで待機）
- `image_dpi`: 画像のDPI設定（PDFページサイズの計算に使用）

## 実行手順の詳細

1. **Kindleアプリの準備**
   - Kindleアプリを開く
   - 変換したい書籍を開く
   - 1ページ目を表示

2. **コマンド実行**
   - ターミナルでコマンドを実行
   - 5秒の待機時間中にKindleウィンドウを最前面にする

3. **自動処理**
   - 自動でページをキャプチャ
   - 各ページの読み込みを待機
   - キャプチャ完了後、自動でPDFに変換

4. **出力**
   - PDFファイルは `output_pdf/タイトル/タイトル.pdf` に保存されます

## トラブルシューティング

### ページが読み込まれる前にキャプチャされる

`config.toml`の`page_load_wait`を増やしてください：

```toml
page_load_wait = 5.0  # より長く待機
```

### インポートエラーが表示される（VS Codeのリンター警告）

VS Codeでインポートエラーが表示される場合、以下を確認してください：

1. **VS Codeの設定確認**
   - `.vscode/settings.json`が作成されているか確認
   - Pythonインタープリターが仮想環境（`.venv`）を指しているか確認

2. **手動でインタープリターを設定**
   - VS Codeで `Ctrl+Shift+P` → "Python: Select Interpreter"
   - `.venv/Scripts/python.exe` を選択

3. **実行時の確認**
   - リンターの警告は実行には影響しません
   - 実際に実行してみて、エラーが出ないか確認：

```bash
# 依存関係がインストールされているか確認
uv sync

# 仮想環境で実行
uv run python main.py --help
```

**注意**: Python 3.11以降では`tomllib`が標準ライブラリに含まれているため、`tomli`パッケージは不要です。

### PDFのページサイズが合わない

`config.toml`の`image_dpi`を調整してください：

- Windows: 通常96 DPI
- Mac: 通常72 DPI
- 高解像度ディスプレイ: 144 DPIや192 DPIの場合もあります

## ファイル構成

```
Kindle_to_pdf/
├── capture.py          # 画面キャプチャスクリプト
├── image_to_pdf.py     # PDF変換スクリプト
├── main.py             # メインスクリプト
├── config.toml         # 設定ファイル
├── pyproject.toml      # プロジェクト設定
├── output/             # キャプチャした画像（自動生成）
└── output_pdf/         # 生成されたPDF（自動生成）
```

## 注意事項

- Kindleアプリが最前面にある必要があります
- キャプチャ中はマウスやキーボードの操作を避けてください
- 途中で中断する場合は `Ctrl+C` を押してください
- 生成されたPDFは画像のみで、テキスト検索はできません

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。

