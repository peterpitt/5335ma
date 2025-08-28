# -*- coding: utf-8 -*-
"""
scrape_539.py — Scrape Taiwan 今彩539 results, compute stats, and write JSON for an iOS app.

Features implemented:
1) Top co-occurring trio across all draws.
2) For the top trio, compute which PAIR most often shows up together in the *next draw* after that trio appears.
3) Intended to run daily Mon–Sat ~22:05 Asia/Taipei (14:05 UTC) via GitHub Actions.
4) For each calendar month, take the FIRST draw of that month and record its "second number" (as shown on the source site
   order — usually already sorted ascending). Then count the most frequent two numbers among those.

Usage:
  python scrape_539.py --out-dir ../web/public --max-pages 200

Notes:
- Sources are HTML list pages; parsing uses heuristics. If they change HTML, update _parse_* functions.
- Timezone: treat dates as Taiwan (UTC+8). We only need date (YYYY-MM-DD), no time.
- This script is idempotent; it rewrites JSON files on each run.
"""
import argparse
import re
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Tuple, Optional

import requests
from bs4 import BeautifulSoup
from itertools import combinations

TAIPEI = timezone(timedelta(hours=8))

# Potential sources (HTML list pages)
SOURCES = [
    # pilio big-font list
    "https://www.pilio.idv.tw/lto539/list539BIG.asp",
    # pilio standard list
    "https://www.pilio.idv.tw/lto539/list.asp",
    # lotto-8 alternative
    "https://www.lotto-8.com/listlto539bbk.asp",
]

def _clean_text(s: str) -> str:
    return re.sub(r'\s+', ' ', s).strip()

def _extract_draws_from_html_pilio(html: str) -> List[Dict[str, Any]]:
    """
    Parse pilio list pages. Lines like:
      開獎日期:2025/08/28   05, 07, 21, 23, 29
      或表格： 2025/08/28 (四) 05, 07, 21, 23, 29
    """
    draws = []
    # Try pattern 1: 開獎日期:YYYY/MM/DD numbers
    for m in re.finditer(r'開獎日期[:：]\s*(\d{4})/(\d{2})/(\d{2}).*?([0-3]?\d(?:\s*,\s*[0-3]?\d){4})', html, flags=re.S):
        y, mm, dd = m.group(1), m.group(2), m.group(3)
        nums_str = m.group(4)
        nums = [int(x) for x in re.findall(r'\d{1,2}', nums_str)]
        nums = sorted(nums)
        d = f"{y}-{mm}-{dd}"
        if len(nums) == 5:
            draws.append({"date": d, "numbers": nums})

    # Try pattern 2: lines like "2025/08/28 (四) 05, 07, 21, 23, 29"
    for m in re.finditer(r'(\d{4})/(\d{2})/(\d{2}).*?\([\u4e00-\u9fa5]\)\s*([0-3]?\d(?:\s*,\s*[0-3]?\d){4})', html):
        y, mm, dd = m.group(1), m.group(2), m.group(3)
        nums = [int(x) for x in re.findall(r'\d{1,2}', m.group(4))]
        nums = sorted(nums)
        d = f"{y}-{mm}-{dd}"
        if len(nums) == 5:
            draws.append({"date": d, "numbers": nums})

    # Try simple table pattern "YYYY MM/DD ... digits"
    for m in re.finditer(r'(\d{4})\s*[/-](\d{2})\s*[/-](\d{2}).*?((?:\d{1,2}\s*,\s*){4}\d{1,2})', html):
        y, mm, dd = m.group(1), m.group(2), m.group(3)
        nums = [int(x) for x in re.findall(r'\d{1,2}', m.group(4))]
        nums = sorted(nums)
        d = f"{y}-{mm}-{dd}"
        if len(nums) == 5:
            draws.append({"date": d, "numbers": nums})

    # Dedup by date
    seen = set()
    out = []
    for dr in draws:
        key = (dr["date"], tuple(dr["numbers"]))
        if key not in seen:
            seen.add(key)
            out.append(dr)
    return out

def _extract_draws_from_html_lotto8(html: str) -> List[Dict[str, Any]]:
    draws = []
    soup = BeautifulSoup(html, "html.parser")
    # Simple approach: find all rows with five numbers separated by comma
    text = soup.get_text(" ", strip=True)
    for m in re.finditer(r'(\d{4})\s*[/-](\d{2})\s*[/-](\d{2}).*?((?:\d{1,2}\s*,\s*){4}\d{1,2})', text):
        y, mm, dd = m.group(1), m.group(2), m.group(3)
        nums = [int(x) for x in re.findall(r'\d{1,2}', m.group(4))]
        nums = sorted(nums)
        d = f"{y}-{mm}-{dd}"
        if len(nums) == 5:
            draws.append({"date": d, "numbers": nums})
    # Dedup
    seen = set()
    out = []
    for dr in draws:
        key = (dr["date"], tuple(dr["numbers"]))
        if key not in seen:
            seen.add(key)
            out.append(dr)
    return out

def fetch_draws(max_pages: int = 200, timeout: int = 20) -> List[Dict[str, Any]]:
    """
    Currently we only pull the first page for each source (they already list recent months).
    If you need multi-page crawl, extend this function.
    """
    all_draws: List[Dict[str, Any]] = []
    sess = requests.Session()
    headers = {"User-Agent": "Mozilla/5.0 (compatible; vibe-539/1.0)"}
    for url in SOURCES:
        try:
            r = sess.get(url, headers=headers, timeout=timeout)
            r.raise_for_status()
            html = r.text
            if "pilio.idv.tw" in url:
                part = _extract_draws_from_html_pilio(html)
            else:
                part = _extract_draws_from_html_lotto8(html)
            all_draws.extend(part)
        except Exception as e:
            print(f"[WARN] fail fetch {url}: {e}")

    # Dedup by date (keep most recent occurrence)
    tmp = {}
    for d in all_draws:
        tmp[d["date"]] = d
    draws = list(tmp.values())
    draws.sort(key=lambda x: x["date"])  # ascending by date
    return draws

def compute_top_trio(draws: List[Dict[str, Any]]) -> Tuple[Tuple[int,int,int], int, List[Tuple[Tuple[int,int,int], int]]]:
    counter = Counter()
    for d in draws:
        for trio in combinations(d["numbers"], 3):
            counter[trio] += 1
    if not counter:
        return ((0,0,0), 0, [])
    top_trio, top_count = counter.most_common(1)[0]
    top5 = counter.most_common(5)
    return top_trio, top_count, top5

def compute_next_pairs_for_trio(draws: List[Dict[str, Any]], trio: Tuple[int,int,int]) -> Tuple[Tuple[int,int], int, List[Tuple[Tuple[int,int], int]]]:
    pair_counter = Counter()
    # Make quick lookup
    for i, d in enumerate(draws[:-1]):
        nums = set(d["numbers"])
        if set(trio).issubset(nums):
            nxt = draws[i+1]["numbers"]
            for p in combinations(nxt, 2):
                pair_counter[tuple(sorted(p))] += 1
    if not pair_counter:
        return ((0,0), 0, [])
    best, cnt = pair_counter.most_common(1)[0]
    top5 = pair_counter.most_common(5)
    return best, cnt, top5

def compute_monthly_first_second_counts(draws: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Group by (year, month). For the earliest draw in that month, take numbers[1] (second in the displayed order).
    Count frequencies across months.
    """
    by_month = defaultdict(list)
    for d in draws:
        dt = datetime.fromisoformat(d["date"])
        key = (dt.year, dt.month)
        by_month[key].append(d)
    # pick first by date
    second_numbers = []
    for key, arr in by_month.items():
        arr_sorted = sorted(arr, key=lambda x: x["date"])
        if arr_sorted:
            nums = arr_sorted[0]["numbers"]
            if len(nums) >= 2:
                second_numbers.append(nums[1])
    c = Counter(second_numbers)
    top2 = [n for n,_ in c.most_common(2)]
    return {"counts": dict(sorted(c.items())), "top2": top2}

def save_json(path: str, data: Any):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default="../web/public", help="Directory to write JSON files")
    ap.add_argument("--max-pages", type=int, default=200)
    args = ap.parse_args()

    draws = fetch_draws(max_pages=args.max_pages)
    if not draws:
        raise SystemExit("No draws parsed from sources. Check network or parsers.")

    top_trio, trio_cnt, top5_trios = compute_top_trio(draws)
    best_pair, pair_cnt, top5_pairs = compute_next_pairs_for_trio(draws, top_trio)
    monthly_sec = compute_monthly_first_second_counts(draws)

    out = {
        "generated_at": datetime.now(TAIPEI).isoformat(),
        "source_urls": SOURCES,
        "num_draws": len(draws),
        "top_trio": {"numbers": list(top_trio), "count": trio_cnt, "top5": [[list(k), v] for k,v in top5_trios]},
        "next_draw_top_pair_given_trio": {"trio": list(top_trio), "pair": list(best_pair), "count": pair_cnt, "top5": [[list(k), v] for k,v in top5_pairs]},
        "monthly_first_draw_second_number": monthly_sec,
    }

    # Ensure out-dir
    import os
    os.makedirs(args.out_dir, exist_ok=True)

    save_json(os.path.join(args.out_dir, "539_stats.json"), out)
    save_json(os.path.join(args.out_dir, "539_draws.json"), {"draws": draws})

    print(f"[OK] Wrote stats to {os.path.join(args.out_dir, '539_stats.json')} and draws to 539_draws.json")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
