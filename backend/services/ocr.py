"""
Layer 1: pypdf native text extraction (fast, lossless)
Layer 2: pytesseract + pdf2image (scanned PDFs)
Layer 3: Claude Vision API (complex layouts, tables, handwritten)
Layer 4: BeautifulSoup (URL scraping)

Decision logic: try native → if avg_chars/page < 100 → tesseract →
if result < 200 chars → Claude Vision
"""
import anthropic, base64, pytesseract
from pathlib import Path
from pdf2image import convert_from_path
from pypdf import PdfReader
from PIL import Image
import httpx, io
from bs4 import BeautifulSoup

client = anthropic.Anthropic()

async def extract(file_path=None, url=None, source_type='pdf') -> str:
    if url:
        return _scrape_url(url)
    if source_type == 'pdf' and file_path:
        text, ok = _native_pdf(file_path)
        if ok: return text
        tess = _tesseract_pdf(file_path)
        if len(tess.strip()) > 200: return tess
        return await _claude_vision(file_path, 'application/pdf')
    if source_type in ('png','jpg','jpeg','webp') and file_path:
        tess = pytesseract.image_to_string(Image.open(file_path))
        if len(tess.strip()) > 100: return tess
        mt = {'png':'image/png','jpg':'image/jpeg','jpeg':'image/jpeg','webp':'image/webp'}
        return await _claude_vision(file_path, mt[source_type])
    if source_type in ('md','txt') and file_path:
        return Path(file_path).read_text()
    if source_type in ('xlsx','xls') and file_path:
        import pandas as pd
        dfs = pd.read_excel(file_path, sheet_name=None)
        return '\n\n'.join([f"## {sn}\n{df.to_string(index=False)}" for sn,df in dfs.items()])
    if source_type == 'docx' and file_path:
        from docx import Document
        return '\n'.join([p.text for p in Document(file_path).paragraphs])
    return ''

def _native_pdf(path):
    reader = PdfReader(path)
    text = ''.join(p.extract_text() or '' for p in reader.pages)
    avg = len(text) / max(len(reader.pages), 1)
    return text, avg > 100

def _tesseract_pdf(path):
    images = convert_from_path(path, dpi=300)
    return '\n'.join(pytesseract.image_to_string(img) for img in images)

async def _claude_vision(path, media_type):
    data = base64.standard_b64encode(Path(path).read_bytes()).decode()
    msg = client.messages.create(
        model="claude-3-5-sonnet-20241022", max_tokens=4096,
        messages=[{"role":"user","content":[
            {"type":"image","source":{"type":"base64","media_type":media_type,"data":data}},
            {"type":"text","text":"""Extract ALL text from this syllabus document.
Preserve: course codes, course names, CO codes and full descriptions, module topics, credits, semester info.
Return clean text with markdown structure. No commentary."""}
        ]}]
    )
    return msg.content[0].text

def _scrape_url(url):
    headers = {'User-Agent':'Mozilla/5.0 SyllabusMapper/1.0'}
    resp = httpx.get(url, headers=headers, timeout=30, follow_redirects=True)
    soup = BeautifulSoup(resp.text, 'html.parser')
    for t in soup(['nav','footer','script','style','header','aside','ads']): t.decompose()
    return soup.get_text(separator='\n', strip=True)
