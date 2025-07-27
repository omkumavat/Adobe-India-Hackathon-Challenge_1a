import fitz  # PyMuPDF
import json
import os
from collections import Counter
import re


def parse_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    spans = []
    for page in doc:
        data = page.get_text("dict")
        for block in data["blocks"]:
            for line in block.get("lines", []):
                for span in line["spans"]:
                    spans.append({
                        "text": span["text"].strip(),
                        "font": span["font"],
                        "size": span["size"],
                        "flags": span["flags"],
                        "bbox": span["bbox"],
                        "page": page.number + 1
                    })
    return spans


def most_common_font_size(spans):
    sizes = [span["size"] for span in spans if span["text"]]
    return Counter(sizes).most_common(1)[0][0] if sizes else 12


def is_heading_candidate(span, body_size):
    text = span["text"]
    size = span["size"]
    font = span["font"].lower()
    if not text or len(text.split()) > 15:
        return False
    if size >= body_size + 2:
        return True
    if "bold" in font or "black" in font:
        return True
    if re.match(r"^\d+(\.|\))", text):
        return True
    return False


def assign_heading_level(span, unique_sizes):
    sorted_sizes = sorted(unique_sizes)
    size = span["size"]
    if size >= sorted_sizes[-1]:
        return "H1"
    elif size >= sorted_sizes[max(-2, -len(sorted_sizes))]:
        return "H2"
    else:
        return "H3"


def extract_outline(spans):
    title = None
    headings = []
    body_size = most_common_font_size(spans)
    unique_sizes = sorted({s["size"] for s in spans})

    first_page_spans = [s for s in spans if s["page"] == 1]
    if first_page_spans:
        title_span = max(first_page_spans, key=lambda s: s["size"])
        title = title_span["text"]

    for span in spans:
        if is_heading_candidate(span, body_size):
            level = assign_heading_level(span, unique_sizes)
            headings.append({
                "level": level,
                "text": span["text"],
                "page": span["page"]
            })

    return title, headings


def process_pdf_file(input_path, output_path):
    spans = parse_pdf(input_path)
    title, headings = extract_outline(spans)
    result = {
        "title": title or "Untitled",
        "outline": headings
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
def main():
    input_path = "./file02.pdf"
    output_dir = "./"
    os.makedirs(output_dir, exist_ok=True)

    if os.path.isfile(input_path) and input_path.lower().endswith(".pdf"):
        output_file = os.path.splitext(os.path.basename(input_path))[0] + ".json"
        output_path = os.path.join(output_dir, output_file)
        process_pdf_file(input_path, output_path)
    elif os.path.isdir(input_path):
        for file in os.listdir(input_path):
            if file.lower().endswith(".pdf"):
                full_path = os.path.join(input_path, file)
                output_file = os.path.splitext(file)[0] + ".json"
                output_path = os.path.join(output_dir, output_file)
                process_pdf_file(full_path, output_path)
    else:
        print("Invalid input path. Please provide a valid PDF file or directory.")


if __name__ == "__main__":
    main()