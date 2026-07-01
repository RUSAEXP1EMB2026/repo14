import pandas as pd
import time
import pygame
from gtts import gTTS

# --- 音楽プレイヤーの初期設定 ---
pygame.mixer.init()

sheet_id = '1RewCrA9d63a8JIxHD_l1_ZW2BiF2SEuRDmOnnXFkxQ8'
url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv'

print("👀 監視＆BGM/アナウンス スタンバイOK！")

# 前回読み上げたテキストを記憶する変数
last_spoken_text = ""

while True:
    try:
        # シートを読み込む
        df = pd.read_csv(url, header=None)
        
        # データの行数をチェックして、安全にセルを取得する
        if len(df) > 0:
            bgm_flag = str(df.iloc[0, 0])
        else:
            bgm_flag = "OFF"
            
        # ★ここが重要！2行目（A2）が存在するかチェックしてから取得する
        if len(df) > 1:
            announce_text = str(df.iloc[1, 0])
        else:
            announce_text = "なし" # 2行目がなければ自動的に「なし」にする
        
        # ----------------------------------------
        # ① アナウンスの処理（最優先）
        # ----------------------------------------
        if announce_text != "なし" and announce_text != "nan" and announce_text != last_spoken_text:
            print(f"🗣️ 【音声合成】「{announce_text}」とアナウンスします！")
            
            tts = gTTS(text=announce_text, lang='ja')
            tts.save("announce.mp3")
            
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
            
            pygame.mixer.music.load("announce.mp3")
            pygame.mixer.music.play()
            
            while pygame.mixer.music.get_busy():
                time.sleep(1)
            
            last_spoken_text = announce_text

        # ----------------------------------------
        # ② BGMの処理
        # ----------------------------------------
        elif not pygame.mixer.music.get_busy():
            if bgm_flag == "ON":
                pygame.mixer.music.load("bgm.mp3")
                pygame.mixer.music.play(-1)
            elif bgm_flag == "OFF":
                pygame.mixer.music.stop()

    except Exception as e:
        print(f"エラー: {e}")

    time.sleep(5)