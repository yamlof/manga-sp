
import sys
import argparse
import os
import time
from pprint import pprint


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def show_help():
    """Show usage information"""
    print("""
    
Usage:
  python3 run.py [manga_name]
  python3 run.py --link [manga_name]

Examples:
  python3 run.py Frieren
  python3 run.py "One Piece"
  
  Don't do:
  python3 run.py Solo Levelling

If no manga name is provided, you'll be prompted to enter one.
""")


def run_manga_scraper():
    """Main manga scraper function"""
    try:
        # Import required modules (assuming they're in your src directory)
        sys.path.append('src')
        from main import search_manga, get_manga_info, download_chapters
        import inquirer

    except ImportError as e:
        print(f"❌ Failed to import required modules: {e}")
        print("Make sure you're in the manga-sp directory and all dependencies are installed.")
        return

    parser = argparse.ArgumentParser(description="Downloads manga pages")
    parser.add_argument('--name', type=str, default=None, help="Bane of the manga to search")
    parser.add_argument('manga_name', nargs='?', help="Manga name (alternative to --link)")

    args = parser.parse_args()

    # Get manga query from either --link flag or positional argument
    manga_query = args.link or args.manga_name

    if not manga_query:
        manga_query = input("🔍 Enter manga name to search: ").strip()

    if not manga_query:
        print("❗ Please provide a manga name")
        return

    try:
        print(f"🔍 Searching for: {manga_query}")

        # Step 1: Search for manga
        manga_data = search_manga(manga_query)
        if not manga_data:
            print("⚠️ No manga found for the given query.")
            return

        # Step 2: Prepare choices for inquirer
        choices = [f"{i['title']}" for i in manga_data]


        sys.stdout.flush()
        clear_screen()
        print(f"📚 Found {len(choices)} manga(s)")
        time.sleep(0.1)

        # Step 3: Ask user to choose a manga
        question = [
            inquirer.List(
                'selection',
                message='Choose a manga',
                choices=choices,
                carousel=True  # optional: allows circular scrolling
            )
        ]
        answer = inquirer.prompt(question)
        pprint(answer)

        if not answer:
            print("❌ No manga selected.")
            return

        # Step 4: Find selected manga info
        selected_index = choices.index(answer['selection'])
        selected_manga = manga_data[selected_index]

        print(f"📖 Getting info for: {selected_manga['title']}")
        manga_info = get_manga_info(selected_manga['manga_url'])

        # Step 5: Download chapters
        print(f"⬇️ Starting download...")
        download_chapters(manga_info.chapters, manga_info.title)
        print("✅ Download completed!")

    except KeyboardInterrupt:
        print("\n⏹️ Cancelled by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] in ["-h", "--help"]:
        show_help()
    else:
        run_manga_scraper()