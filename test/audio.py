#audio.py

import pygame
from gtts import gTTS
import time

pygame.mixer.init()


def speak(text):

    try:

        print(f"🗣️ {text}")

        tts = gTTS(
            text=text,
            lang="ja"
        )

        tts.save("announce.mp3")

        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()

        pygame.mixer.music.load(
            "announce.mp3"
        )

        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            time.sleep(0.5)

    except Exception as e:
        print("音声エラー:", e)