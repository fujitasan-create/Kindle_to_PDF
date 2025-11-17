import pyautogui
import time
import os
import shutil
from pathlib import Path
from tqdm import tqdm


def capture_pages(start_page, end_page, config):
    """ページをキャプチャする
    
    Args:
        start_page: 開始ページ番号
        end_page: 終了ページ番号
        config: 設定辞書
    """
    output_dir = config["output"]["output_dir"]
    
    # フォルダ初期化
    if os.path.exists(output_dir):
        print(f"既存のフォルダ '{output_dir}' を初期化します。")
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)
    
    wait_time = config["capture"]["wait_time"]
    page_load_wait = config["capture"].get("page_load_wait", 3.0)
    capture_wait = config["capture"].get("capture_wait", 0.5)
    total_pages = end_page - start_page + 1
    
    print(f"{wait_time}秒後に開始します。Kindleを最前面にしてください。")
    print(f"ページ {start_page} から {end_page} まで ({total_pages}ページ) をキャプチャします。")
    print(f"各ページの読み込み待機時間: {page_load_wait}秒")
    time.sleep(wait_time)
    
    try:
        with tqdm(total=total_pages, desc="キャプチャ中") as pbar:
            for page in range(start_page, end_page + 1):
                # 最初のページは既に表示されているので、2ページ目以降はページをめくる
                if page > start_page:
                    pyautogui.press("right")  # 次ページ
                    # ページが読み込まれるまで待機
                    time.sleep(page_load_wait)
                
                # キャプチャ前の追加待機（ページが完全に表示されるまで）
                time.sleep(capture_wait)
                
                # スクリーンショットを取得
                filename = os.path.join(output_dir, f"{page:04d}.png")
                image = pyautogui.screenshot()
                image.save(filename)
                pbar.set_postfix({"現在": f"ページ{page}"})
                pbar.update(1)
    except KeyboardInterrupt:
        print(f"\nキャプチャ中断されました。")
        print(f"現在までに {page - start_page} ページをキャプチャしました。")
        return False
    
    print(f"\nキャプチャ完了: {total_pages} ページを保存しました。")
    return True


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
        "output": {"output_dir": "output"},
        "capture": {"wait_time": 5, "page_load_wait": 3.0, "capture_wait": 0.5, "interval": 0.1}
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
    
    # ページ番号の入力
    start_page = int(input("開始ページ番号を入力: "))
    end_page = int(input("終了ページ番号を入力（途中終了もOK）: "))
    
    capture_pages(start_page, end_page, config)
