import fitz  # PyMuPDF
import json
from itertools import groupby

def is_bold(font_name: str) -> bool:
    parts = font_name.replace("-", ",").split(",")
    return any(part.strip().lower() == "bold" for part in parts)

def extract_spans(pdf_path):
    doc = fitz.open(pdf_path)
    all_spans = []

    for page_num, page in enumerate(doc, start=1):
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    text = span["text"].strip()
                    if text:
                        all_spans.append({
                            "text": text,
                            "size": span["size"],
                            "font": span["font"],
                            "x": span["bbox"][0],
                            "y": span["bbox"][1],
                            "page": page_num
                        })
    # Sort spans for reading order (top to bottom, left to right)
    all_spans.sort(key=lambda s: (s['page'], s['y'], s['x']))
    return all_spans

def merge_lines(spans, y_threshold=3.0):
    for span in spans:
        span['y_rounded'] = round(span['y'] / y_threshold) * y_threshold

    merged_lines = []
    for (page, y_val), group in groupby(sorted(spans, key=lambda s: (s['page'], s['y_rounded'], s['x'])),
                                        key=lambda s: (s['page'], s['y_rounded'])):
        group = list(group)
        group.sort(key=lambda s: s['x'])
        line_text = " ".join(s['text'] for s in group)
        merged_lines.append({
            "text": line_text.strip(),
            "size": group[0]['size'],
            "font": group[0]['font'],
            "page": page,
            "y": y_val
        })
    return merged_lines

def merge_multiline_headings(lines, y_gap_threshold=5, x_threshold=10):
    merged = []
    i = 0
    while i < len(lines):
        current = lines[i]
        text = current['text']
        j = i + 1
        while j < len(lines):
            next_line = lines[j]
            same_font = current['font'] == next_line['font']
            same_size = abs(current['size'] - next_line['size']) < 0.5
            close_y = 0 < (next_line['y'] - current['y']) < y_gap_threshold
            close_x = abs(current.get('x', 0) - next_line.get('x', 0)) < x_threshold
            same_page = current['page'] == next_line['page']

            if same_page and same_font and same_size and close_y and close_x:
                text += " " + next_line['text']
                current['y'] = next_line['y']
                j += 1
                i = j
            else:
                break

        current['text'] = text
        merged.append(current)
        i += 1
    return merged

def is_heading_like(text):
    if len(text.split()) > 12:
        return False
    if text.startswith("•") or text.startswith("-"):
        return False
    if text.endswith(":") and len(text.split()) > 5:
        return False
    if text.strip().lower() in ["skills", "experience", "projects"]:
        return True
    return True

def classify_headings(lines):
    title = ""
    outline = []

    # Rank font sizes dynamically
    sizes = sorted({round(line['size'], 1) for line in lines}, reverse=True)
    font_to_level = {}
    if len(sizes) >= 1: font_to_level[sizes[0]] = "TITLE"
    if len(sizes) >= 2: font_to_level[sizes[1]] = "H1"
    if len(sizes) >= 3: font_to_level[sizes[2]] = "H2"
    if len(sizes) >= 4: font_to_level[sizes[3]] = "H3"

    for line in lines:
        text = line["text"].strip()
        size = round(line["size"], 1)
        font = line["font"]
        page = line["page"]

        if not is_heading_like(text):
            continue

        level = font_to_level.get(size)

        if level == "TITLE" and not title:
            title = text
        elif level in ["H1", "H2", "H3"] and is_bold(font):
            outline.append({ "level": level, "text": text, "page": page })
        elif size >= 9 and size <= 11 and is_bold(font):
            print(f"⚠️ Warning: Found bold text without a clear heading level: {text} (size: {size}, font: {font})")
            outline.append({ "level": "H3", "text": text, "page": page })


    return {
        "title": title,
        "outline": outline
    }

def process_pdf_to_outline(pdf_path):
    spans = extract_spans(pdf_path)
    merged_lines = merge_lines(spans)
    full_lines = merge_multiline_headings(merged_lines)
    return classify_headings(full_lines)

# Run the process and dump output to JSON
if __name__ == "__main__":
    pdf_path = "my_result.pdf"
    result = process_pdf_to_outline(pdf_path)

    # Save output to a JSON file
    with open("output.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print("✅ JSON outline saved to output.json")
