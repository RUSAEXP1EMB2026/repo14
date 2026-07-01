#コード説明
#スプレッドシートのC1,C2を見て、C1では音楽の制御、C2では音声アナウンスの制御をする。
#C1には'ON'と入力することで音楽を再生でき、'OFF'にすると再生しなくなる。
#C2には'なし'と入力した場合だけ読み上げず、'今日は暑いですね'などと入力した際にはそれを読み上げる。
#もし音楽の再生中にC2に読み上げるテキストが書き込まれた場合、音楽を中断して音声を読み上げ、読み終わると音楽の再生を再開する。



import pandas as pd
import time
import random
import urllib.parse
import pychromecast

# --- 🎵 インターネット上のフリーBGMリスト（ランダム再生用） ---
BGM_PLAYLIST = [
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

print("👀 監視システム（BGM自動復帰モード）起動！")

current_bgm_status = "OFF"
last_spoken_text = "" # 前回喋ったアナウンスを記憶する変数

while True:
    try:
        # シートを最新の状態に読み込む
        df = pd.read_csv(url, header=None)
        
        # ----------------------------------------
        # ① C1マスからBGMフラグを取得
        # ----------------------------------------
        if len(df) > 0 and df.shape[1] > 2:
            bgm_flag = str(df.iloc[0, 2]).strip().upper() # C1マス
        else:
            bgm_flag = "OFF"
            
        # ----------------------------------------
        # ② C2マスからアナウンス文字を取得
        # ----------------------------------------
        if len(df) > 1 and df.shape[1] > 2:
            announce_text = str(df.iloc[1, 2]).strip() # C2マス
        else:
            announce_text = "なし"

        # ----------------------------------------
        # 📢 処理1：音声アナウンス（文字の読み上げ）を最優先
        # ----------------------------------------
        if announce_text != "なし" and announce_text != "nan" and announce_text != "" and announce_text != last_spoken_text:
            print(f"🗣️ 【遠隔アナウンス】「{announce_text}」と屋根裏で読み上げます！")
            
            # Googleのネット上の音声合成URLに文字を埋め込む
            encoded_text = urllib.parse.quote(announce_text)
            tts_url = f"https://translate.google.com/translate_tts?ie=UTF-8&tl=ja&client=tw-ob&q={encoded_text}"
            
            # Nest Miniに喋らせる（これで音楽は一度中断されます）
            mc.play_media(tts_url, "audio/mp3")
            
            # 喋り終わるまで文字数に応じて少し待つ
            time.sleep(min(len(announce_text) * 0.4, 5))
            
            # 💡 ここがポイント！
            # 喋り終わった記憶は残しつつ、「音楽は流れていない状態」にリセットします。
            # こうすることで、次のループ（5秒後）で下のBGM処理が「あ、C1がONなのに音楽止まってるじゃん！」と気づいて自動で再開してくれます。
            last_spoken_text = announce_text
            current_bgm_status = "OFF"

        # ----------------------------------------
        # 🎵 処理2：BGM（音楽）の制御
        # ----------------------------------------
        # C1が「ON」で、まだ音楽が鳴っていない場合（アナウンス終了後もここに入ります！）
        elif bgm_flag == "ON" and current_bgm_status == "OFF":
            selected_bgm = random.choice(BGM_PLAYLIST)
            print(f"🎵 BGMを流します（再開含む）: {selected_bgm}")
            mc.play_media(selected_bgm, "audio/mp3")
            current_bgm_status = "ON"
            
        # C1が「OFF」で、まだ音楽が鳴りっぱなしの場合
        elif bgm_flag == "OFF" and current_bgm_status == "ON":
            print("🛑 BGMがOFFになりました。音楽を止めます。")
            mc.stop()
            current_bgm_status = "OFF"

    except Exception as e:
        print(f"エラー: {e}")

    # 5秒待ってシートを再チェック
    time.sleep(5)