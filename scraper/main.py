import os
import json
import requests
import subprocess
import asyncio
from bs4 import BeautifulSoup
from crawl4ai import AsyncWebCrawler

STATE_FILE = "scraper/state.json"
SAVE_FOLDER = "scraper/scraped_data"
MAX_FILES_PER_REPO = 25000
MAX_MB_PER_REPO = 1024  # 1GB max
ARTICLES_PER_DAY = 3    # Scrape 2–3 full articles per day

os.makedirs(SAVE_FOLDER, exist_ok=True)

def load_state():
    with open(STATE_FILE, 'r') as f:
        return json.load(f)

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def get_random_article():
    response = requests.get("https://en.wikipedia.org/wiki/Special:Random", allow_redirects=True)
    return response.url

def extract_clean_text_from_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    content_div = soup.find('div', {'class': 'mw-parser-output'})
    cleaned_paragraphs = []

    if content_div:
        for tag in content_div.find_all(['p', 'h2', 'h3']):
            if tag.name == 'p' and tag.get_text(strip=True) == "":
                continue
            for sup in tag.find_all('sup'):
                sup.decompose()
            for span in tag.find_all('span', class_='mw-editsection'):
                span.decompose()
            for table in tag.find_all('table'):
                table.decompose()

            text = tag.get_text(separator=' ', strip=True)
            if any(x in text.lower() for x in ['track listing', 'references', 'external links', 'see also']):
                continue

            cleaned_paragraphs.append(text)

    return '\n\n'.join(cleaned_paragraphs)

async def scrape_articles():
    state = load_state()
    scraped = []
    total_size_mb = 0
    articles_scraped_today = 0

    async with AsyncWebCrawler() as crawler:
        while articles_scraped_today < ARTICLES_PER_DAY:
            url = get_random_article()
            if url in state['visited_articles']:
                continue
            try:
                result = await crawler.arun(url=url)
                clean_text = extract_clean_text_from_html(result.html)

                if not clean_text.strip():
                    print(f"⚠️ Empty or junk content at {url}, skipping.")
                    continue

                entry = {"url": url, "content": clean_text}
                entry_str = json.dumps(entry)
                entry_size_mb = len(entry_str.encode('utf-8')) / 1_000_000

                scraped.append(entry)
                total_size_mb += entry_size_mb
                state['visited_articles'].append(url)
                articles_scraped_today += 1
            except Exception as e:
                print(f"❌ Failed to scrape {url}: {e}")

    if not scraped:
        print("⚠️ No new articles to save.")
        return

    file_index = state['current_file_number']
    save_path = os.path.join(SAVE_FOLDER, f"scrape_{file_index:05d}.jsonl")

    with open(save_path, 'w', encoding='utf-8') as f:
        for entry in scraped:
            f.write(json.dumps(entry) + '\n')

    state['current_file_number'] += 1
    save_state(state)

    if state['current_file_number'] > MAX_FILES_PER_REPO:
        subprocess.run(["python", "scraper/rotate_repo.py"])

if __name__ == "__main__":
    asyncio.run(scrape_articles())
