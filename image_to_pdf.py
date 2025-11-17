import os
import shutil
import traceback
from pathlib import Path
from PIL import Image
from fpdf import FPDF
from tqdm import tqdm


def convert_to_pdf(title, config):
    """画像をPDFに変換
    
    Args:
        title: PDFファイルのタイトル
        config: 設定辞書
        
    Returns:
        成功した場合True、失敗した場合False
    """
    input_dir = config["output"]["output_dir"]
    pdf_parent_dir = config["output"]["pdf_parent_dir"]
    image_dpi = config.get("image_dpi", 96)  # WindowsのデフォルトDPI
    
    # 設定の検証
    if not os.path.isdir(input_dir):
        print(f"エラー: 画像フォルダ '{input_dir}' が見つかりません。")
        print("先に capture.py を実行して、画像を生成してください。")
        return False
    
    # フォルダ準備
    os.makedirs(pdf_parent_dir, exist_ok=True)
    
    # 出力フォルダ作成
    title_specific_output_dir = os.path.join(pdf_parent_dir, title)
    if os.path.exists(title_specific_output_dir):
        shutil.rmtree(title_specific_output_dir)
    os.makedirs(title_specific_output_dir)
    print(f"出力先フォルダを作成しました: {title_specific_output_dir}")
    
    # PDF初期化（サイズは後で各ページで動的に設定）
    pdf = FPDF(unit="mm")
    
    # 画像処理
    images = sorted(f for f in os.listdir(input_dir) if f.endswith(".png"))
    if not images:
        print(f"エラー: '{input_dir}' フォルダにPNG画像が見つかりません。")
        return False
    
    print(f"'{input_dir}' フォルダから {len(images)} 個の画像ファイルを処理します。")
    
    processed_count = 0
    error_count = 0
    
    with tqdm(total=len(images), desc="PDF変換中") as pbar:
        for img_file in images:
            img_path = os.path.join(input_dir, img_file)
            
            if not os.path.exists(img_path):
                print(f"\n警告: ファイルが見つかりません: {img_path}。このファイルはスキップします。")
                pbar.update(1)
                error_count += 1
                continue
            
            try:
                # 画像を読み込む
                img = Image.open(img_path)
                
                # 画像のサイズをmmに変換（DPIを考慮）
                dpi = image_dpi
                if 'dpi' in img.info and img.info['dpi']:
                    # 画像にDPI情報がある場合はそれを使用
                    img_dpi = img.info['dpi']
                    if isinstance(img_dpi, tuple):
                        dpi = img_dpi[0] if img_dpi[0] > 0 else image_dpi
                    elif isinstance(img_dpi, (int, float)) and img_dpi > 0:
                        dpi = img_dpi
                
                # ピクセルをmmに変換（1インチ = 25.4mm）
                page_width_mm = (img.width / dpi) * 25.4
                page_height_mm = (img.height / dpi) * 25.4
                
                # 画像サイズに合わせてPDFページを追加
                pdf.add_page(format=(page_width_mm, page_height_mm))
                
                # 画像を一時ファイルに保存（FPDFが読み込める形式）
                temp_img_path = os.path.join(title_specific_output_dir, f"temp_{img_file}")
                img.save(temp_img_path, "PNG")
                
                # 画像をPDFに追加（ページ全体に配置、余白なし）
                pdf.image(temp_img_path, x=0, y=0, w=page_width_mm, h=page_height_mm)
                
                # 一時ファイルを削除
                if os.path.exists(temp_img_path):
                    os.remove(temp_img_path)
                
                processed_count += 1
                pbar.update(1)
            except Exception as e:
                print(f"\nエラー: '{img_file}' の処理中にエラーが発生しました:")
                print(f"  エラー内容: {e}")
                print(f"  エラータイプ: {type(e).__name__}")
                traceback.print_exc()
                print("このファイルはスキップします。")
                pbar.update(1)
                error_count += 1
                continue
    
    # 処理結果のサマリー表示
    print(f"\n処理サマリー:")
    print(f"  処理成功: {processed_count} ページ")
    print(f"  エラー: {error_count} ページ")
    
    # PDF保存
    if pdf.page_no() > 0:
        pdf_filename = f"{title}.pdf"
        pdf_path = os.path.join(title_specific_output_dir, pdf_filename)
        pdf.output(pdf_path)
        print(f"\n✓ PDF出力完了: {pdf_path}")
        print(f"  総ページ数: {pdf.page_no()} ページ")
        return True
    else:
        print("\n✗ PDFに出力するページがありませんでした。")
        if error_count > 0:
            print(f"  {error_count} 個のファイルでエラーが発生しました。エラーメッセージを確認してください。")
        return False


# 後方互換性のため、直接実行時も動作するようにする
if __name__ == "__main__":
    # Python 3.11以降では標準ライブラリのtomllibを使用
    try:
        import tomllib  # Python 3.11+
    except ImportError:
        import tomli as tomllib  # Python 3.10以下用のフォールバック
    
    # 設定ファイルを読み込む
    config_path = "config.toml"
    default_config = {
        "output": {"output_dir": "output", "pdf_parent_dir": "output_pdf"},
        "image_dpi": 96
    }
    
    if Path(config_path).exists():
        with open(config_path, "rb") as f:
            config = tomllib.load(f)
        # デフォルトとマージ
        for key, value in default_config.items():
            if key not in config:
                config[key] = value
    else:
        config = default_config
    
    # タイトル入力
    title = input("PDFファイルのタイトルを入力してください: ").strip()
    if not title:
        print("エラー: タイトルが入力されていません。処理を中断します。")
        exit()
    
    convert_to_pdf(title, config)
