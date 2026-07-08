import argparse
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from controllers import bgm_controller


def main():
    parser = argparse.ArgumentParser(description="Test BGM playback.")
    parser.add_argument("command", choices=("list", "play", "stop"))
    parser.add_argument("category", nargs="?", choices=sorted(bgm_controller.BGM_FOLDERS))
    args = parser.parse_args()

    if args.command == "list":
        for category in sorted(bgm_controller.BGM_FOLDERS):
            folder = bgm_controller.BGM_BASE_DIR / bgm_controller.BGM_FOLDERS[category]
            count = len(list(folder.glob("*.mp3"))) if folder.exists() else 0
            print(f"{category}: {count} files")
        return

    if args.command == "play":
        if not args.category:
            parser.error("play requires a category.")
        print(bgm_controller.play(args.category))
        return

    if args.command == "stop":
        print(bgm_controller.stop())


if __name__ == "__main__":
    main()
