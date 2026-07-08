import os
import random
import pygame

# フォルダのベースパス
BGM_BASE_DIR = "bgm"

# 用途とフォルダ名のマッピング
BGM_FOLDERS = {
    "clear": "clear",
    "rain": "rain",
    "cloudy": "cloudy"
}

def get_random_bgm(category):
    """指定されたフォルダからランダムに1曲選ぶ"""
    folder_path = os.path.join(BGM_BASE_DIR, BGM_FOLDERS.get(category))
    if not os.path.exists(folder_path):
        return None
    
    # mp3ファイルだけをリストアップ
    files = [f for f in os.listdir(folder_path) if f.endswith(".mp3")]
    if not files:
        return None
        
    return os.path.join(folder_path, random.choice(files))

def judge(settings, sensor_data, weather_data, aircon_action):
    """天気による判定（BGMを流すべき条件の時だけカテゴリを返す）"""
    
    # 天気による判定（晴れ・雨・曇りの時だけBGMを流す）
    weather = weather_data.get("weather")
    if weather == "Clear":
        return "clear"
    if weather in ("Rain", "Drizzle", "Thunderstorm"):
        return "rain"
    if weather == "Clouds":
        return "cloudy"

    # それ以外（起床時含む）は何も鳴らさない
    return None

def play(category):
    """指定されたカテゴリの曲をランダムに選んで再生する"""
    bgm_file = get_random_bgm(category)

    if not bgm_file:
        return

    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()

        # 同じ曲が流れていない場合のみロードして再生
        # (すでに流れているならそのままループさせる)
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.load(bgm_file)
            pygame.mixer.music.play(-1) # ループ再生
    
    except Exception:
        pass