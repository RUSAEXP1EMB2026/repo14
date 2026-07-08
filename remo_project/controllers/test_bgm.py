import sys
import os
import pygame
import random
import time

# 1. 検索パスの設定：現在地(controllers)から見て一つ上の階層(remo_project)を追加
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 2. 正しいパスからインポート
from controllers import bgm_controller

# テスト用：シミュレーション
def test_bgm_logic():
    print("--- BGM再生テスト開始 ---")
    
    # フォルダ構成確認用デバッグ
    base_dir = os.path.join(os.path.dirname(__file__), '..', 'bgm')
    print(f"確認: BGMフォルダの場所を探しています -> {base_dir}")
    
    # 擬似的なデータを作成
    settings = {}
    sensor_data = {}
    weather_data = {"weather": "Clear"} # 晴れに固定してテスト
    aircon_action = None
    
    # カテゴリ判定
    category = bgm_controller.judge(settings, sensor_data, weather_data, aircon_action)
    print(f"判定されたカテゴリ: {category}")
    
    if category:
        print(f"再生を試みます: {category}...")
        bgm_controller.play(category)
        print("再生コマンド送信完了。音が鳴るか確認してください。")
    else:
        print("カテゴリが判定されませんでした。")

if __name__ == "__main__":
    test_bgm_logic()
    # 再生終了を防ぐため待機
    input("テスト終了するにはEnterを押してください...")