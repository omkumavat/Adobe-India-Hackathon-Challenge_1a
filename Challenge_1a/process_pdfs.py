import fitz  # PyMuPDF
import json
import os

# Base directory of the script
base_dir = os.path.dirname(os.path.abspath(__file__))

# Input and output folders
input_dir = os.path.join(base_dir, "sample_dataset", "pdfs")
output_dir = os.path.join(base_dir, "sample_dataset", "outputs")
os.makedirs(output_dir, exist_ok=True)

def extract_outline_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    lines = []

    for page_num, page in enumerate(doc, start=1):
        for block in page.get_text("dict")["blocks"]:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                text, sizes = "", []
                for span in line["spans"]:
                    t = span["text"].strip()
                    if not t:
                        continue
                    text += t + " "
                    sizes.append(round(span["size"], 1))
                if text:
                    lines.append({
                        "page": page_num,
                        "text": text.strip(),
                        "size": sum(sizes)/len(sizes)
                    })

    merged = []
    for L in lines:
        if (merged
            and merged[-1]["page"] == L["page"]
            and merged[-1]["size"] == L["size"]):
            merged[-1]["text"] += " " + L["text"]
        else:
            merged.append(L.copy())

    unique_sizes = sorted({round(L["size"],1) for L in merged}, reverse=True)
    level_names = ["Title", "H1", "H2", "H3", "H4"]
    size_to_level = {
        size: level_names[i]
        for i, size in enumerate(unique_sizes[:len(level_names)])
    }

    output = {"title": "", "outline": []}
    seen = set()
    for L in merged:
        lvl = size_to_level.get(round(L["size"], 1))
        key = (L["text"], L["page"])
        if lvl == "Title":
            output["title"] += (L["text"] + " ")
        elif lvl in ("H1", "H2", "H3", "H4") and key not in seen:
            output["outline"].append({
                "level": lvl,
                "text": L["text"],
                "page": L["page"]
            })
            seen.add(key)

    output["title"] = output["title"].strip()
    return output

# === Batch Process PDFs ===
if __name__ == "__main__":
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(".pdf"):
            input_pdf_path = os.path.join(input_dir, filename)
            output_json_path = os.path.join(output_dir, filename.replace(".pdf", ".json"))
            
            print(f"Processing: {filename}")
            try:
                result = extract_outline_from_pdf(input_pdf_path)
                with open(output_json_path, "w", encoding="utf-8") as f:
                    json.dump(result, f, indent=2)
                print(f"Saved: {output_json_path}")
            except Exception as e:
                print(f"Failed: {filename} → {e}")
