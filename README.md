# WikiScraper

WikiScraper is a GitHub Actions workflow that automatically scrapes Wikipedia articles and pushes the scraped data to designated repositories. It uses Python, Playwright, and other dependencies to collect and manage data efficiently.

---

## Features

- Scrapes Wikipedia articles and stores them in a structured format.
- Automatically pushes scraped data to the correct repository.
- Maintains state using `scraper/state.json` to track visited articles and progress.
- Caches Python dependencies for faster workflow execution.
- Supports manual runs via GitHub Actions `workflow_dispatch`.

---

## Recent Update (2025-08-19)

- **Daily run limit:** The workflow now runs a **random 1–3 times per day**.  
- Uses `state.json` to track daily runs (`runs_today` and `max_runs_today`).  
- If the daily maximum is reached, subsequent runs will automatically skip, ensuring the scraper doesn’t exceed the limit.  

---

## Usage

1. Workflow runs automatically at scheduled times (default: 4 AM, 12 PM, 8 PM UTC).  
2. You can also trigger the workflow manually via GitHub Actions `workflow_dispatch`.  
3. All scraped data is pushed to the target repository as configured in `state.json`.

---

## Requirements

- Python 3.10
- Playwright
- crawl4ai
- requests
- GitHub Actions with a valid `GH_TOKEN` secret
