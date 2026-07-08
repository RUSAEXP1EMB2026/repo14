import pandas as pd
import time
import datetime
import random
import urllib.parse
import pychromecast

# --- 🎵 天気別のBGMプレイリスト ---
BGM_SUNNY = [
    "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
    "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3"
]

BGM_CLOUDY = [
    "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3",
    "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-4.mp3"
]

BGM_DEFAULT = [
    "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
    "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3",
    "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3"
]

# --- 📊 スプレッドシートの設定 ---
sheet_id = '1RewCrA9d63a8JIxHD_l1_ZW2BiF2SEuRDmOnnXFkxQ8'
url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv'

print("🔍 Wi-Fi内のGoogle Nest Miniを探しています...")
chromecasts, browser = pychromecast.get_chromecasts()

if not chromecasts:
    print("❌ Google Nest Miniが見つかりませんでした。")
    exit()

cast = chromecasts[0]
print(f"🎉 接続先を発見しました: {cast.name}")
cast.wait()
mc = cast.media_controller

print("👀 統合制御システム（LINE連携＋自律判定モード）起動！")

# --- 🔄 状態管理用の変数 ---
current_bgm_status = "OFF"
last_spoken_text = ""
last_motion_time = datetime.datetime.now() 
has_announced_morning = False             
last_checked_date = datetime.date.today()   

# 🔔 【新機能用】LINEのアナウンスが何度も重複して流れないようにするロック
has_announced_line_ready = False

while True:
    try:
        df = pd.read_csv(url, header=None)
        now = datetime.datetime.now()
        
        if now.date() != last_checked_date:
            has_announced_morning = False
            last_checked_date = now.date()

        # --------------------------------------------------
        # 📡 ① スプレッドシートから各データを取得
        # --------------------------------------------------
        bgm_flag = str(df.iloc[0, 2]).strip().upper() if len(df) > 0 and df.shape[1] > 2 else "OFF"
        announce_text = str(df.iloc[1, 2]).strip() if len(df) > 1 and df.shape[1] > 2 else "なし"
        
        # 【新機能】C3マス（2行目, 2列目）からLINEの状態を取得
        line_status = str(df.iloc[2, 2]).strip() if len(df) > 2 and df.shape[1] > 2 else "なし"
        
        alarm_time_str = str(df.iloc[2, 0]).strip() if len(df) > 2 else ""           # A3: 起床時間
        current_temp = float(df.iloc[3, 0]) if len(df) > 3 else 25.0                 # A4: 室温
        current_weather = str(df.iloc[4, 0]).strip() if len(df) > 4 else "不明"        # A5: 天気
        motion_status = str(df.iloc[5, 0]).strip().upper() if len(df) > 5 else "OFF"  # A6: 人感センサ

        # --------------------------------------------------
        # ⏰ ② 起床時アナウンスの判定（自分で計算）
        # --------------------------------------------------
        current_time_str = now.strftime("%H:%M")
        if current_time_str == alarm_time_str and not has_announced_morning:
            announce_text = f"おはようございます。設定時刻の{alarm_time_str}になりました。現在の天気は{current_weather}、室温は{current_temp}度です。"
            has_announced_morning = True 

        # --------------------------------------------------
        # 🔔 ③ 【新機能】LINE設定完了アナウンスの割り込み判定
        # --------------------------------------------------
        # もしシートが「設定完了」になっていて、まだそれを喋っていない場合
        if line_status == "設定完了" and not has_announced_line_ready:
            announce_text = "ラインの設定が完了しました。システムとの連携を開始します。"
            has_announced_line_ready = True # 1回喋ったらロックをかける
            
        # もしLINE側が設定をリセット（「なし」などに戻す）したら、ロックを解除して次の一発に備える
        elif line_status != "設定完了":
            has_announced_line_ready = False

        # --------------------------------------------------
        # 🏃 ④ 人感センサによる「3時間不在」の判定（自分で計算）
        # --------------------------------------------------
        if motion_status == "ON":
            last_motion_time = now 
            
        time_elapsed = (now - last_motion_time).total_seconds()
        if time_elapsed >= 10800: 
            print("💤 不在判定のためBGMをOFFにします")
            bgm_flag = "OFF"

        # --------------------------------------------------
        # 📢 ⑤ 音声アナウンス処理（最優先・LINE通知もここで流れる）
        # --------------------------------------------------
        if announce_text != "なし" and announce_text != "nan" and announce_text != "" and announce_text != last_spoken_text:
            print(f"🗣️ アナウンス放送中: 「{announce_text}」")
            encoded_text = urllib.parse.quote(announce_text)
            tts_url = f"https://translate.google.com/translate_tts?ie=UTF-8&tl=ja&client=tw-ob&q={encoded_text}"
            
            mc.play_media(tts_url, "audio/mp3")
            time.sleep(min(len(announce_text) * 0.4, 6))
            
            last_spoken_text = announce_text
            current_bgm_status = "OFF" # 音楽を一度止まった扱いにして再開させる

        # --------------------------------------------------
        # 🎵 ⑥ BGM（音楽）の制御処理（天気連動）
        # --------------------------------------------------
        elif bgm_flag == "ON" and current_bgm_status == "OFF":
            if "晴れ" in current_weather or "Clear" in current_weather:
                selected_bgm = random.choice(BGM_SUNNY)
                print(f"☀️ 晴れ用のBGMを選びました: {selected_bgm}")
            elif "曇り" in current_weather or "Clouds" in current_weather or "くもり" in current_weather:
                selected_bgm = random.choice(BGM_CLOUDY)
                print(f"☁️ 曇り用のBGMを選びました: {selected_bgm}")
            else:
                selected_bgm = random.choice(BGM_DEFAULT)
                print(f"🎵 通常のBGMを選びました: {selected_bgm}")

            mc.play_media(selected_bgm, "audio/mp3")
            current_bgm_status = "ON"
            
        elif bgm_flag == "OFF" and current_bgm_status == "ON":
            print("🛑 BGM停止")
            mc.stop()
            current_bgm_status = "OFF"

    except Exception as e:
        print(f"エラー発生: {e}")

    time.sleep(5)