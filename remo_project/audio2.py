import pandas as pd
import time
import datetime
import random
import urllib.parse
import pychromecast
import os

# --- 🎵 天気別のBGMプレイリスト（自動で正しいURLを組み立てるように修正） ---
# パソコンのIPアドレスとサーバーポートを指定
IP_PORT = "192.168.100.12:8000"

# http.serverを「組み立て」フォルダで開いても「remo_project」で開いても、どちらでも自動対応させます
if os.path.exists("remo_project"):
    # 「組み立て」フォルダ側でサーバーを起動している場合
    BGM_BASE_URL = f"http://{IP_PORT}/remo_project/bgm/"
else:
    # 「remo_project」フォルダの中で直接サーバーを起動している場合
    BGM_BASE_URL = f"http://{IP_PORT}/bgm/"

BGM_SUNNY = [
    f"{BGM_BASE_URL}clear/clear1.mp3",
    f"{BGM_BASE_URL}clear/clear2.mp3",
    f"{BGM_BASE_URL}clear/clear3.mp3",
    f"{BGM_BASE_URL}clear/clear4.mp3",
    f"{BGM_BASE_URL}clear/clear5.mp3"
]

BGM_CLOUDY = [
    f"{BGM_BASE_URL}cloudy/cloudy1.mp3",
    f"{BGM_BASE_URL}cloudy/cloudy2.mp3",
    f"{BGM_BASE_URL}cloudy/cloudy3.mp3",
    f"{BGM_BASE_URL}cloudy/cloudy4.mp3",
    f"{BGM_BASE_URL}cloudy/cloudy5.mp3"
]

BGM_RAIN = [
    f"{BGM_BASE_URL}rain/rain1.mp3",
    f"{BGM_BASE_URL}rain/rain2.mp3",
    f"{BGM_BASE_URL}rain/rain3.mp3",
    f"{BGM_BASE_URL}rain/rain4.mp3",
    f"{BGM_BASE_URL}rain/rain5.mp3"
]

BGM_DEFAULT = BGM_SUNNY  # 天気が不明なときのデフォルト

# --- 📊 スプレッドシートの設定 ---
sheet_id = '1YA5_eNiOeVL7PNGDX3NNqP7eb9whQGqhdd3NHhZjMQ4'
url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv'

print("🔍 Wi-Fi内のGoogle Nest Miniを探しています...")
chromecasts, browser = pychromecast.get_chromecasts()

if not chromecasts:
    print("❌ Google Nest Miniが見つかりませんでした。")
    exit()

# 最初に見つかったデバイス（オフィス）に接続します
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
has_announced_line_ready = False

while True:
    try:
        # スプレッドシートの読み込み
        df = pd.read_csv(url, header=0)
        df.set_index('key', inplace=True)
        
        now = datetime.datetime.now()
        
        if now.date() != last_checked_date:
            has_announced_morning = False
            last_checked_date = now.date()

        # --------------------------------------------------
        # 📡 ① スプレッドシートから各データを取得
        # --------------------------------------------------
        bgm_flag = "OFF"
        if 'bgm_flag' in df.index:
            bgm_flag = str(df.loc['bgm_flag', 'value']).strip().upper()
            
        announce_text = "なし"
        if 'announce_text' in df.index:
            announce_text = str(df.loc['announce_text', 'value']).strip()
        
        line_status = "なし"
        if 'line_status' in df.index:
            line_status = str(df.loc['line_status', 'value']).strip()
        
        alarm_time_str = str(df.loc['wake_time', 'value']).strip() if 'wake_time' in df.index else ""
        
        # 設定シートにまだ無いログ項目はデフォルト値を設定
        current_temp = float(df.loc['current_temp', 'value']) if 'current_temp' in df.index else 25.0
        current_weather = str(df.loc['current_weather', 'value']).strip() if 'current_weather' in df.index else "不明"
        motion_status = str(df.loc['motion_status', 'value']).strip().upper() if 'motion_status' in df.index else "OFF"
        
        absence_threshold_min = 180
        if 'absence_threshold' in df.index:
            try:
                absence_threshold_min = int(df.loc['absence_threshold', 'value'])
            except:
                pass

        # --------------------------------------------------
        # ⏰ ② 起床時アナウンスの判定
        # --------------------------------------------------
        current_time_str = now.strftime("%H:%M")
        if current_time_str == alarm_time_str and not has_announced_morning:
            announce_text = f"おはようございます。設定時刻の{alarm_time_str}になりました。現在の天気は{current_weather}、室温は{current_temp}度です。"
            has_announced_morning = True 

        # --------------------------------------------------
        # 🔔 ③ LINE設定完了アナウンスの割り込み判定
        # --------------------------------------------------
        if line_status == "設定完了" and not has_announced_line_ready:
            announce_text = "ラインの設定が完了しました。システムとの連携を開始します。"
            has_announced_line_ready = True 
            
        elif line_status != "設定完了":
            has_announced_line_ready = False

        # --------------------------------------------------
        # 🏃 ④ 人感センサによる「不在」の判定
        # --------------------------------------------------
        if motion_status == "ON":
            last_motion_time = now 
            
        time_elapsed = (now - last_motion_time).total_seconds()
        if time_elapsed >= (absence_threshold_min * 60): 
            print(f"💤 不在判定（{absence_threshold_min}分経過）のためBGMをOFFにします")
            bgm_flag = "OFF"

        # --------------------------------------------------
        # 📢 ⑤ 音声アナウンス処理
        # --------------------------------------------------
        if announce_text != "なし" and announce_text != "nan" and announce_text != "" and announce_text != last_spoken_text:
            print(f"🗣️ アナウンス放送中: 「{announce_text}」")
            encoded_text = urllib.parse.quote(announce_text)
            tts_url = f"https://translate.google.com/translate_tts?ie=UTF-8&tl=ja&client=tw-ob&q={encoded_text}"
            
            mc.play_media(tts_url, "audio/mp3")
            time.sleep(min(len(announce_text) * 0.4, 6))
            
            last_spoken_text = announce_text
            current_bgm_status = "OFF"

        # --------------------------------------------------
        # 🎵 ⑥ BGM（音楽）の制御処理
        # --------------------------------------------------
        elif bgm_flag == "ON" and current_bgm_status == "OFF":
            # 晴れ判定
            if "晴れ" in current_weather or "Clear" in current_weather:
                selected_bgm = random.choice(BGM_SUNNY)
                print(f"☀️ 晴れ用のBGMを選びました: {selected_bgm}")
            # 曇り判定
            elif "曇り" in current_weather or "Clouds" in current_weather or "くもり" in current_weather:
                selected_bgm = random.choice(BGM_CLOUDY)
                print(f"☁️ 曇り用のBGMを選びました: {selected_bgm}")
            # 雨判定
            elif "雨" in current_weather or "Rain" in current_weather or "あめ" in current_weather:
                selected_bgm = random.choice(BGM_RAIN)
                print(f"☔ 雨用のBGMを選びました: {selected_bgm}")
            # その他・不明時
            else:
                selected_bgm = random.choice(BGM_DEFAULT)
                print(f"🎵 通常のBGMを選びました: {selected_bgm}")

            # スピーカーへ配信URLを渡して再生
            mc.play_media(selected_bgm, "audio/mp3")
            current_bgm_status = "ON"
            
        elif bgm_flag == "OFF" and current_bgm_status == "ON":
            print("🛑 BGM停止")
            mc.stop()
            current_bgm_status = "OFF"

    except Exception as e:
        print(f"エラー発生: {e}")

    time.sleep(5)