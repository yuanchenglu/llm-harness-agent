# Paper Full Content Extractor & Translator
# Run this script to download and save paper content

import urllib.request
import re
import os
import time
import json

BASE_DIR = "/Volumes/Doc/Code/deepseekagent/docs/llm-harness-agent/papers"
PDF_DIR = os.path.join(BASE_DIR, "pdf")
PDF_ZH_DIR = os.path.join(BASE_DIR, "pdf-zh")
os.makedirs(PDF_DIR, exist_ok=True)
os.makedirs(PDF_ZH_DIR, exist_ok=True)

def fetch_arxiv_html(arxiv_id, html_path, timeout=120):
    """Fetch full text from arXiv HTML version"""
    url = f"https://arxiv.org/html/{arxiv_id}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            html = response.read().decode('utf-8')
        # Strip HTML tags to get plain text
        text = re.sub(r'<[^>]+>', ' ', html)
        text = re.sub(r'\s+', ' ', text).strip()
        # Remove references section noise (arXiv references at bottom)
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(text)
        return len(text)
    except Exception as e:
        return f"Error: {e}"

def fetch_nature_html(url, html_path, timeout=120):
    """Fetch full text from Nature/Springer HTML"""
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml'
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            html = response.read().decode('utf-8')
        text = re.sub(r'<[^>]+>', ' ', html)
        text = re.sub(r'\s+', ' ', text).strip()
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(text)
        return len(text)
    except Exception as e:
        return f"Error: {e}"

# Papers to download: (id, source_type, url/arxiv_id, filename)
papers = [
    # A Class - Core Harness Theory
    ("A2-AIOS", "arxiv", "2403.16971"),
    ("A3-Wang-Survey", "arxiv", "2308.11432"),
    ("A4-Xi-Survey", "arxiv", "2309.07864"),
    ("A5-MultiAgent-Survey", "arxiv", "2412.17481"),  # newer version
    
    # B Class - Foundational
    ("B1-ReAct", "arxiv", "2210.03629"),
    ("B2-Generative-Agents", "arxiv", "2304.03442"),
    ("B3-Toolformer", "arxiv", "2302.04761"),
    ("B4-Reflexion", "arxiv", "2303.11366"),
    ("B5-Tree-of-Thoughts", "arxiv", "2305.10601"),
    ("B6-HuggingGPT", "arxiv", "2303.17580"),
    ("B7-AgentBench", "arxiv", "2308.03688"),
    
    # C Class - Frameworks
    ("C1-ToolLLM", "arxiv", "2307.16789"),
    ("C2-MetaGPT", "arxiv", "2308.00352"),
    ("C3-OpenHands", "arxiv", "2407.16741"),
    
    # D Class - Memory
    ("D1-Memory-Survey", "arxiv", "2404.13501"),
    ("D2-MemAgent", "arxiv", "2507.02259"),
]

print(f"Starting download of {len(papers)} papers...\n")

for pid, ptype, src in papers:
    txt_path = os.path.join(PDF_DIR, f"{pid}.txt")
    if os.path.exists(txt_path):
        size_kb = os.path.getsize(txt_path) / 1024
        print(f"  [{pid}] Already exists ({size_kb:.0f} KB), skipping")
        continue
    
    print(f"\n  [{pid}] Fetching {ptype}:{src}...")
    if ptype == "arxiv":
        result = fetch_arxiv_html(src, txt_path)
    else:
        result = fetch_nature_html(src, txt_path)
    
    if isinstance(result, int):
        print(f"  [{pid}] Saved: {result} chars ({result/1024:.0f} KB)")
    else:
        print(f"  [{pid}] Failed: {result}")
    
    time.sleep(2)  # Be polite

print("\n=== Download Summary ===")
for pid, _, _ in papers:
    txt_path = os.path.join(PDF_DIR, f"{pid}.txt")
    if os.path.exists(txt_path):
        size_kb = os.path.getsize(txt_path) / 1024
        print(f"  {pid}: {size_kb:.0f} KB")
    else:
        print(f"  {pid}: MISSING")
