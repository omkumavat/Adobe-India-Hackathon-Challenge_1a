import os
import json
import re
import fitz  # PyMuPDF
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def clean_text(text):
    text = text.replace('\n', ' ') 
    text = re.sub(r'•||▪|–|-|–|—|\*|●', ' ', text) 
    text = re.sub(r'\bo\b', '', text)  
    text = re.sub(r'\s+', ' ', text).strip() 
    return text

def extract_sections_from_pdf(pdf_path):
    """
    Extract sections by identifying the largest-font heading per page and full page text.
    """
    doc = fitz.open(pdf_path)
    sections = []
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        data = page.get_text("dict")
        spans = []
        for block in data.get("blocks", []):
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    text = span.get("text", "").strip()
                    if not text:
                        continue
                    spans.append({
                        "text": text,
                        "size": span.get("size", 0),
                        "font": span.get("font", "").lower()
                    })
        if not spans:
            continue
        # Choose the span with the maximum font size as the section title (H1)
        heading_span = max(spans, key=lambda s: s["size"])
        heading = heading_span["text"]
        # Full page text
        full_text = page.get_text().strip()
        sections.append({
            "document": os.path.basename(pdf_path),
            "page": page_num + 1,
            "title": heading,
            "text": full_text
        })
    return sections


def summarize_section(text, max_sent=2):
    text = clean_text(text)
    sentences = re.split(r'(?<=[.!?])\s+', text)
    sentences = [s for s in sentences if s]
    if len(sentences) <= max_sent:
        return " ".join(sentences)
    vec = TfidfVectorizer(stop_words='english', norm=None)
    X = vec.fit_transform(sentences)
    scores = X.sum(axis=1).A1
    top_idx = sorted(range(len(scores)), key=lambda i: -scores[i])[:max_sent]
    top_idx.sort()
    return ". ".join(sentences[i].rstrip(".") for i in top_idx) + "."

def process_collection(collection_path):
    input_path = os.path.join(collection_path, "challenge1b_input.json")
    output_path = os.path.join(collection_path, "challenge1b_output.json")
    pdf_dir = os.path.join(collection_path, "PDFs")

    with open(input_path, 'r', encoding='utf-8') as f:
        cfg = json.load(f)
    persona = cfg['persona']['role']
    task = cfg['job_to_be_done']['task']
    documents = [d['filename'] for d in cfg['documents']]
    query = f"{persona} {task}"

    # print(f"[DEBUG] Persona: {persona}, Task: {task}, Query: {query}")
    # print(f"[DEBUG] Found {len(documents)} documents")
    
    all_secs = []
    for fname in documents:
        path = os.path.join(pdf_dir, fname)
        if os.path.exists(path):
            all_secs.extend(extract_sections_from_pdf(path))

    texts = [s['text'] for s in all_secs]
    if not texts:
        return
    vec = TfidfVectorizer(stop_words='english')
    tfidf = vec.fit_transform(texts)
    qvec = vec.transform([query])
    sims = cosine_similarity(tfidf, qvec).flatten()

    # Best section per document
    best = {}
    for i, sec in enumerate(all_secs):
        doc = sec['document']
        if doc not in best or sims[i] > best[doc][0]:
            best[doc] = (sims[i], i)
    # Select top 5 documents
    top = sorted(best.values(), key=lambda x: -x[0])[:5]

    extracted = []
    analysis = []
    for rank, (_, idx) in enumerate(top, start=1):
        sec = all_secs[idx]
        extracted.append({
            'document': sec['document'],
            'section_title': sec['title'],
            'importance_rank': rank,
            'page_number': sec['page']
        })
        refined = summarize_section(sec['text'])
        analysis.append({
            'document': sec['document'],
            'refined_text': refined,
            'page_number': sec['page']
        })

    out = {
        'metadata': {
            'input_documents': documents,
            'persona': persona,
            'job_to_be_done': task,
            'processing_timestamp': datetime.now().isoformat()
        },
        'extracted_sections': extracted,
        'subsection_analysis': analysis
    }
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(f"[✓] Wrote: {output_path}")


def main():
    collection_path = "D:\Adobe-India-Hackathon-ConnectingTheDots\Python Codes\Python Codes\Collection_3" 
    if os.path.isdir(collection_path) and os.path.exists(os.path.join(collection_path, 'challenge1b_input.json')):
        print(f"Processing: {collection_path}")
        process_collection(collection_path)
    else:
        print(f"[ERROR] Folder or input JSON not found at: {collection_path}")


if __name__ == '__main__':
    main()
