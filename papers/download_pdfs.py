#!/usr/bin/env python3
"""
Download full PDF + text for all LLM+Harness=Agent papers.
Usage: python3 download_pdfs.py
"""

import urllib.request
import urllib.error
import re
import os
import time
import ssl

BASE_DIR = "/Volumes/Doc/Code/deepseekagent/docs/llm-harness-agent/papers"
PDF_DIR = os.path.join(BASE_DIR, "pdf")
os.makedirs(PDF_DIR, exist_ok=True)

# Disable SSL verification for stubborn hosts
ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'

def download_url(url, output_path, max_timeout=300):
    """Download a URL to a file with retries."""
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
            with urllib.request.urlopen(req, timeout=max_timeout) as resp:
                data = resp.read()
                with open(output_path, 'wb') as f:
                    f.write(data)
                return len(data)
        except Exception as e:
            if attempt < 2:
                wait = 10 * (attempt + 1)
                print(f"    Retry {attempt+1} after {wait}s: {e}")
                time.sleep(wait)
            else:
                raise e

def download_pdf(arxiv_id, filename_prefix):
    """Download PDF from arXiv."""
    pdf_path = os.path.join(PDF_DIR, f"{filename_prefix}.pdf")
    if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 50000:
        print(f"  {filename_prefix}.pdf already exists ({os.path.getsize(pdf_path)//1024} KB)")
        return True
    
    pdf_url = f"https://arxiv.org/pdf/{arxiv_id}"
    print(f"  Downloading PDF: {pdf_url}")
    try:
        size = download_url(pdf_url, pdf_path)
        if size and size > 10000:
            print(f"  -> Saved: {size//1024} KB")
            return True
        else:
            print(f"  -> File too small ({size} bytes), removing")
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
            return False
    except Exception as e:
        print(f"  -> Failed: {e}")
        return False

def download_html_text(arxiv_id, filename_prefix):
    """Download HTML version as text."""
    txt_path = os.path.join(PDF_DIR, f"{filename_prefix}.txt")
    if os.path.exists(txt_path) and os.path.getsize(txt_path) > 5000:
        print(f"  {filename_prefix}.txt already exists ({os.path.getsize(txt_path)//1024} KB)")
        return True
    
    # Try different HTML version URLs
    html_urls = [
        f"https://arxiv.org/html/{arxiv_id}v1",
        f"https://arxiv.org/html/{arxiv_id}",
    ]
    
    for html_url in html_urls:
        try:
            req = urllib.request.Request(html_url, headers={'User-Agent': USER_AGENT})
            with urllib.request.urlopen(req, timeout=60) as resp:
                html = resp.read().decode('utf-8')
            # Strip HTML to get plain text
            text = re.sub(r'<[^>]+>', ' ', html)
            text = re.sub(r'\s+', ' ', text).strip()
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(text)
            print(f"  -> Text saved: {len(text)} chars")
            return True
        except urllib.error.HTTPError as e:
            if e.code == 404:
                continue  # Try next URL
        except Exception as e:
            print(f"  HTML failed: {e}")
            continue
    
    # If HTML fails, try extracting text from PDF
    pdf_path = os.path.join(PDF_DIR, f"{filename_prefix}.pdf")
    if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 10000:
        print(f"  HTML not available, will extract from PDF later")
        return False
    
    return False

def download_nature(url, filename_prefix):
    """Download Nature/Springer paper HTML."""
    txt_path = os.path.join(PDF_DIR, f"{filename_prefix}.txt")
    pdf_path = os.path.join(PDF_DIR, f"{filename_prefix}.pdf")
    
    # Try to get HTML text
    if not (os.path.exists(txt_path) and os.path.getsize(txt_path) > 5000):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
            with urllib.request.urlopen(req, timeout=60) as resp:
                html = resp.read().decode('utf-8')
            text = re.sub(r'<[^>]+>', ' ', html)
            text = re.sub(r'\s+', ' ', text).strip()
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(text)
            print(f"  -> Text saved: {len(text)} chars")
        except Exception as e:
            print(f"  Text failed: {e}")
    
    # Try to get PDF (Nature usually provides a PDF download link)
    pdf_url = url.replace('/article/', '/pdf/')
    if not (os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 50000):
        try:
            print(f"  Trying PDF: {pdf_url}")
            size = download_url(pdf_url, pdf_path)
            if size and size > 10000:
                print(f"  -> PDF saved: {size//1024} KB")
        except Exception as e:
            print(f"  PDF failed: {e}")


# ============================================================
# Paper definitions
# ============================================================
papers = [
    # A Class - Core Harness Theory
    ("A2-AIOS", "arxiv", "2403.16971"),
    ("A3-Wang-Survey", "arxiv", "2308.11432"),
    ("A4-Xi-Survey", "arxiv", "2309.07864"),
    ("A5-MultiAgent-Survey", "arxiv", "2412.17481"),
    
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

# Non-arxiv papers
nature_papers = [
    ("A1-Agent-Harness-Survey", "https://www.preprints.org/manuscript/202604.0428"),
    ("E1-Coscientist-Nature", "https://www.nature.com/articles/s41586-023-06792-0"),
    ("E2-ChemCrow-NatMachIntell", "https://www.nature.com/articles/s42256-024-00832-8"),
]

print("=" * 60)
print("DOWNLOADING ARXIV PAPERS (PDF + Text)")
print("=" * 60)

for pid, ptype, src in papers:
    print(f"\n[{pid}]")
    
    # Step 1: Download PDF
    pdf_ok = download_pdf(src, pid)
    
    # Step 2: Download HTML text
    download_html_text(src, pid)
    
    time.sleep(2)

print("\n" + "=" * 60)
print("DOWNLOADING NATURE / PREPRINTS PAPERS")
print("=" * 60)

for pid, url in nature_papers:
    print(f"\n[{pid}]")
    download_nature(url, pid)
    time.sleep(3)

print("\n" + "=" * 60)
print("FINAL SUMMARY")
print("=" * 60)

total_size = 0
for f in sorted(os.listdir(PDF_DIR)):
    fpath = os.path.join(PDF_DIR, f)
    size = os.path.getsize(fpath)
    total_size += size
    ftype = "PDF" if f.endswith(".pdf") else "TXT"
    icon = "✅" if size > 10000 else "⚠️"
    print(f"  {icon} {f:40s} {ftype:3s} {size//1024:6d} KB")

print(f"\nTotal: {total_size//1024//1024} MB in {len(os.listdir(PDF_DIR))} files")
