import argparse
import sys
from pathlib import Path

# Python 3.11以降では標準ライブラリのtomllibを使用
try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib  # Python 3.10以下用のフォールバック

from capture import capture_pages
from image_to_pdf import convert_to_pdf


def load_config(config_path="config.toml"):
    """設定ファイルを読み込む
    
    Args:
        config_path: 設定ファイルのパス
        
    Returns:
        設定辞書
    """
    # デフォルト設定
    default_config = {
        "capture": {
            "wait_time": 5,
            "page_load_wait": 3.0,
            "capture_wait": 0.5,
            "interval": 0.1,
            "default_start_page": 1
        },
        "output": {
            "output_dir": "output",
            "pdf_parent_dir": "output_pdf"
        },
        "image_dpi": 96
    }
    
    if Path(config_path).exists():
        with open(config_path, "rb") as f:
            config = tomllib.load(f)
        # デフォルトとマージ（ネストされた辞書もマージ）
        for key, value in default_config.items():
            if key not in config:
                config[key] = value
            elif isinstance(value, dict) and isinstance(config[key], dict):
                # ネストされた辞書のマージ
                for sub_key, sub_value in value.items():
                    if sub_key not in config[key]:
                        config[key][sub_key] = sub_value
        return config
    else:
        print(f"警告: 設定ファイル '{config_path}' が見つかりません。デフォルト設定を使用します。")
        return default_config


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description="Kindle書籍をPDFに変換するツール",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # キャプチャとPDF変換を一括実行
  python main.py --start-page 1 --end-page 100 --title "書籍タイトル"
  
  # キャプチャのみ実行
  python main.py --capture-only --start-page 1 --end-page 100
  
  # PDF変換のみ実行（既存の画像から）
  python main.py --pdf-only --title "書籍タイトル"
        """
    )
    
    parser.add_argument(
        "--capture-only",
        action="store_true",
        help="キャプチャのみ実行（PDF変換は実行しない）"
    )
    parser.add_argument(
        "--pdf-only",
        action="store_true",
        help="PDF変換のみ実行（キャプチャは実行しない）"
    )
    parser.add_argument(
        "--start-page",
        type=int,
        help="開始ページ番号"
    )
    parser.add_argument(
        "--end-page",
        type=int,
        help="終了ページ番号"
    )
    parser.add_argument(
        "--title",
        type=str,
        help="PDFファイルのタイトル"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config.toml",
        help="設定ファイルのパス（デフォルト: config.toml）"
    )
    
    args = parser.parse_args()
    config = load_config(args.config)
    
    success = True
    
    # キャプチャとPDF変換の両方を実行
    if not args.pdf_only:
        if args.start_page is None or args.end_page is None:
            print("エラー: --start-page と --end-page を指定してください")
            print("使用例: python main.py --start-page 1 --end-page 100 --title \"書籍タイトル\"")
            sys.exit(1)
        
        if args.start_page > args.end_page:
            print("エラー: 開始ページ番号が終了ページ番号より大きいです。")
            sys.exit(1)
        
        print("=" * 60)
        print("キャプチャ処理を開始します")
        print("=" * 60)
        success = capture_pages(args.start_page, args.end_page, config)
        
        if not success:
            print("キャプチャ処理が中断されました。")
            sys.exit(1)
    
    if not args.capture_only:
        if not args.title:
            print("エラー: --title を指定してください")
            print("使用例: python main.py --pdf-only --title \"書籍タイトル\"")
            sys.exit(1)
        
        print("\n" + "=" * 60)
        print("PDF変換処理を開始します")
        print("=" * 60)
        success = convert_to_pdf(args.title, config)
        
        if not success:
            print("PDF変換処理が失敗しました。")
            sys.exit(1)
    
    print("\n" + "=" * 60)
    print("すべての処理が完了しました！")
    print("=" * 60)


if __name__ == "__main__":
    main()
