import requests
from bs4 import BeautifulSoup
import pyttsx3
import os
import re
import time

def get_wattpad_text(url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        raise Exception(f"Failed to fetch page. Status: {res.status_code}")
    
    soup = BeautifulSoup(res.text, 'html.parser')
    text_blocks = soup.find_all('pre') or soup.find_all('p')
    chapter_text = "\n".join(block.get_text() for block in text_blocks if block.get_text().strip())
    
    if not chapter_text:
        raise Exception("Could not extract text. Wattpad layout may have changed.")
    
    return chapter_text

def text_to_speech_combined(text, filename="story.wav", voice_name="David", rate=150):
    engine = pyttsx3.init()
    engine.setProperty('rate', rate)

    voices = engine.getProperty('voices')
    for voice in voices:
        if voice_name.lower() in voice.name.lower():
            engine.setProperty('voice', voice.id)
            break
    else:
        raise Exception(f"Voice '{voice_name}' not found on your system.")

    print(f"[*] Using voice: {voice.name} at rate {rate}")
    engine.save_to_file(text, filename)
    engine.runAndWait()
    print(f"[✓] Saved combined audio to {filename}")

def extract_base_url_and_chapter(url):
    match = re.search(r"(.*-chapter-)(\d+)", url)
    if not match:
        raise ValueError("URL must end with '-chapter-N'")
    base, start_num = match.groups()
    return base, int(start_num)

def main():
    print("Do you want to:")
    print("1. Paste your own text")
    print("2. Use a Wattpad URL")

    choice = input("Enter 1 or 2: ").strip()

    combined_text = ""
    if choice == '1':
        print("\nPaste your custom text below. Type 'END' on a new line to finish:")
        lines = []
        while True:
            line = input()
            if line.strip().upper() == "END":
                break
            lines.append(line)
        if lines:
            combined_text = "\n".join(lines)
        else:
            print("[!] No text entered. Exiting.")
            return

    elif choice == '2':
        url = input("Enter starting Wattpad chapter URL (must end in '-chapter-N'): ").strip()
        try:
            base_url, start_chapter = extract_base_url_and_chapter(url)
        except ValueError as ve:
            print(f"[!] {ve}")
            return

        num_chapters = input("How many chapters do you want to fetch (including this one)? ").strip()
        try:
            num_chapters = int(num_chapters)
        except ValueError:
            print("[!] Invalid number of chapters.")
            return

        for i in range(num_chapters):
            chapter_url = f"{base_url}{start_chapter + i}"
            print(f"[*] Fetching chapter {start_chapter + i}: {chapter_url}")
            try:
                chapter_text = get_wattpad_text(chapter_url)
                combined_text += f"\n\n[Chapter {start_chapter + i}]\n{chapter_text}"
                time.sleep(1.5)  # Be polite to Wattpad
            except Exception as e:
                print(f"[!] Failed to fetch chapter {start_chapter + i}: {e}")
                combined_text += f"\n\n[Chapter {start_chapter + i} not available]\n"

    else:
        print("[!] Invalid choice.")
        return

    output_filename = "wattpad_story.wav"
    print("[*] Converting to speech...")
    text_to_speech_combined(combined_text, filename=output_filename)

if __name__ == "__main__":
    main()
