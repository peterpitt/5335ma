
# Backend: 539 scraper + stats
- `scrape_539.py` scrapes public list pages (pilio / lotto-8) and computes:
  1) Top co-occurring trio.
  2) Given that trio appears, the pair that most often appears in the *next draw*.
  3) For each month, the first draw's second number (as displayed order), and its top-2 frequency.

## Local run
```bash
cd backend
python -m venv .venv && . .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python scrape_539.py --out-dir ../web/public
```

JSON files will be written into `web/public`.

## Data source
We parse list pages (HTML). If layout changes, update regex in the script.
