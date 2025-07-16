import fitz

doc = fitz.open("my_result.pdf")
for page_number, page in enumerate(doc, start=1):
    blocks = page.get_text("dict")["blocks"]
    for block in blocks:
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                text = span["text"]
                size = span["size"]
                font = span["font"]
                print(f"[Page {page_number}] {text} (size: {size}, font: {font})")
