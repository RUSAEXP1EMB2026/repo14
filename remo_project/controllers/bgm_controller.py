import os
import pygame
import random

# 【ここを修正】現在のファイルの場所を基準に、一つ上の階層の 'bgm' を指定する
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BGM_BASE_DIR = os.path.join(BASE_DIR, "bgm")

# 用途とフォルダ名のマッピング
BGM_FOLDERS = {


    "clear": "clear",
    "rain": "rain",
    "cloudy": "cloudy",
    "wake": "wake"
}
# ...以下省略...
# 現在再生中のカテゴリを記憶しておく変数
_current_category = None

def get_random_bgm(category):
    """指定されたフォルダからランダムに1曲選ぶ"""
    folder_path = os.path.join(BGM_BASE_DIR, BGM_FOLDERS.get(category))
    if not os.path.exists(folder_path):
        return None
    
    files = [f for f in os.listdir(folder_path) if f.endswith(".mp3")]
    return os.path.join(folder_path, random.choice(files)) if files else None

def judge(settings, sensor_data, weather_data, aircon_action):
    """起床および天気による判定"""
    
    # 1. 起床時判定: 最優先でwakeカテゴリを返す
    if aircon_action and aircon_action.get("value") == "wake_preheat":
        return "wake"

    # 2. 在室中かつ起床時以外の天気判定
    weather = weather_data.get("weather")
    if weather == "Clear":
        return "clear"
    if weather in ("Rain", "Drizzle", "Thunderstorm"):
        return "rain"
    if weather == "Clouds":
        return "cloudy"

    return None
def play(category):
    global _current_category

    # 同じなら何もしない
    if _current_category == category and pygame.mixer.music.get_busy():
        return

    bgm_file = get_random_bgm(category)
    if not bgm_file:
        return

    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()

        # ここで確実に新しい曲をロードする
        pygame.mixer.music.stop() # 一旦止めるのがコツ
        pygame.mixer.music.load(bgm_file)
        pygame.mixer.music.play(-1) 
        _current_category = category
    except Exception:
        pass

def stop():
    global _current_category
    if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()
        _current_category = None  