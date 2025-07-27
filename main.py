import requests
from bs4 import BeautifulSoup
import pyttsx3
import time
import re
from urllib.parse import urlparse

def get_wattpad_text(url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        raise Exception(f"Failed to fetch page. Status: {res.status_code}")
    
    soup = BeautifulSoup(res.text, 'html.parser')
    
    text_blocks = soup.find_all('pre')
    if not text_blocks:
        text_blocks = soup.find_all('p')
    
    chapter_text = "\n".join(block.get_text() for block in text_blocks if block.get_text().strip())

    return chapter_text.strip(), soup

def get_next_chapter_url(soup, current_chapter_number):
    # Look for any href that ends in -chapter-{next}
    next_chapter_number = current_chapter_number + 1
    pattern = re.compile(rf'-chapter-{next_chapter_number}$', re.IGNORECASE)

    for a in soup.find_all('a', href=True):
        href = a['href']
        if pattern.search(href):
            if href.startswith('/'):
                href = "https://www.wattpad.com" + href
            return href
    return None

def text_to_speech_combined(text, filename="wattpad_story.wav", voice_name="David", rate=150):
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

def generate_page_url(base_url, page_num):
    parsed = urlparse(base_url)
    path_parts = parsed.path.rstrip('/').split('/')
    if 'page' in path_parts:
        page_index = path_parts.index('page')
        path_parts = path_parts[:page_index]
    if page_num > 1:
        path_parts += ['page', str(page_num)]
    new_path = '/'.join(path_parts)
    return parsed._replace(path=new_path).geturl()

def extract_chapter_number(url):
    match = re.search(r'-chapter-(\d+)', url)
    if match:
        return int(match.group(1))
    return 1  # fallback if not found

def main():
    print("Enter the starting Wattpad chapter URL (preferably page 1 or no page specified):")
    url = input("Starting URL: ").strip()
    original_chapter_num = extract_chapter_number(url)

    max_chapters = input("How many chapters to fetch? (Enter 0 for all available): ").strip()
    try:
        max_chapters = int(max_chapters)
        if max_chapters < 0:
            raise ValueError
    except ValueError:
        print("[!] Invalid number of chapters, defaulting to 1")
        max_chapters = 1

    combined_text = ""
    current_url = url
    chapter_count = 0
    current_chapter_num = original_chapter_num

    while current_url:
        chapter_count += 1
        print(f"[*] Fetching chapter {chapter_count}: {current_url}")

        chapter_text_full = ""
        page_num = 1

        while True:
            page_url = generate_page_url(current_url, page_num)
            print(f"    -> Fetching page {page_num}: {page_url}")
            try:
                page_text, soup = get_wattpad_text(page_url)
                if not page_text:
                    print(f"    [*] No content found on page {page_num}, stopping pagination.")
                    break
                chapter_text_full += "\n" + page_text
            except Exception as e:
                if page_num == 1:
                    print(f"[!] Failed to fetch chapter {chapter_count} first page: {e}")
                    return
                else:
                    print(f"    [*] Error or no more pages at page {page_num}: {e}")
                    break
            page_num += 1
            time.sleep(1)

        if chapter_text_full.strip():
            combined_text += f"\n\n[Chapter {chapter_count}]\n{chapter_text_full.strip()}"
        else:
            print(f"[!] Chapter {chapter_count} had no content. Skipping.")

        if max_chapters != 0 and chapter_count >= max_chapters:
            print("[*] Reached the requested number of chapters.")
            break

        next_url = get_next_chapter_url(soup, current_chapter_num)
        if not next_url:
            print("[*] No more chapters found.")
            break

        current_url = next_url
        current_chapter_num += 1
        time.sleep(2)

    if combined_text.strip():
        print("[*] Converting combined chapters to speech...")
        text_to_speech_combined(combined_text, filename="wattpad_story.wav")
    else:
        print("[!] No text to convert.")

if __name__ == "__main__":
    main()
