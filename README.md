# 📄 PDF Heading Hierarchy Extractor

A Python tool to extract **heading hierarchies (Title, H1, H2...)** from PDFs using **font size and styling characteristics**. Supports multilingual documents using **OCR fallback**, and outputs structured data in **JSON format**.

---

## 📂 Folder Structure

```
.
Challenge_1a/
|
├── sample_dataset/
    ├── pdfs/
    ├── outputs/
├── challenge_1a.py
├── requirements.txt
├── Dockerfile
README.md
```
---

## 🎯 Objective

Extract heading hierarchy (like Title, H1, H2...) from each page of a PDF by analyzing **font size and styling characteristics**. Supports batch processing and multilingual documents (e.g., Hindi, Japanese) using OCR fallback.

---

## 🚀 Features

✅ Extracts Title, H1, H2, H3, etc. from PDFs  
✅ Font-size-based dynamic hierarchy detection  
✅ Supports multilingual documents (e.g., Hindi, Japanese)  
✅ Outputs clean and structured JSON  
✅ Supports batch processing  
✅ Compatible with large documents  
✅ Cross-platform (Windows, Linux, Mac)

---

## 🧠 How It Works

### 🔍 1. PDF Text Extraction

- Utilizes *PyMuPDF (fitz)* to parse PDF structure.
- Extracts block → line → span level data from the PDF.
- For each span:
  - Captures text, font size, font type, page number.
  - Skips empty or whitespace-only spans.

### 📏 2. Line Merging & Font Size Averaging

- Each line is reconstructed by concatenating its spans.
- Average font size is calculated per line.
- Consecutive lines with same font size on the same page are merged to improve heading grouping.

### 🧱 3. Heading Level Detection

- Unique font sizes are sorted in descending order.
- Mapped to levels: Title, H1, H2, H3, H4.
- Line classified based on font size and order in unique sizes.

### 🌐 4. OCR Support (Optional)

- Uses `pdf2image` to convert pages to images.
- Applies `pytesseract` for OCR text extraction.
- Attempts the same font-based grouping if font data can be estimated.

---

## 📐 Architecture

```plaintext
PDF File
   ↓
[PyMuPDF Parser]
   ↓
[Span → Line → Font Extraction]
   ↓
[Font Size Analysis & Merging]
   ↓
[Heading Level Classification]
   ↓
(Optional: OCR Layer)
   ↓
🟢 JSON Output with Headings
{
  "title": "Extracted Title from PDF",
  "outline": [
    {
      "level": "H1",
      "text": "Section Heading",
      "page": 1
    },
    {
      "level": "H2",
      "text": "Subsection Heading",
      "page": 2
    }
  ]
}

```
---

## ▶️ How to Run

- ✅ Build the Docker Image: 
```bash
docker build --platform linux/amd64 -t pdf-processor .
```
- ▶️ Run the Container:
```bash
docker run --rm -v $(pwd)/sample_dataset/pdfs:/app/input:ro -v $(pwd)/sample_dataset/outputs:/app/output --network none pdf-processor
```
- This mounts your local sample_dataset folder into the Docker container so the script can read and write data.
- The processed output will be saved to: sample_dataset/outputs/file.json

The script will:
- Parse the PDFs listed in `file.pdf` from the `sample_dataset/pdfs` folder
- Extract heading hierarchy (like Title, H1, H2...) from each page of a PDF by analyzing **font size and styling characteristics**.
- Generate `file.json` in the same folder as the PDFs

---

## ⚙️ Processing Workflow
This script analyzes PDF documents to automatically extract their hierarchical structure (outline) based on font sizes — identifying probable titles and headings (e.g., Title, H1, H2, etc.) from the content.  

🧾 Input and Output Structure  
Your folder setup should look like:

```bash
sample_dataset/
├── pdfs/              # Folder containing input PDF files
└── outputs/           # Output folder where extracted JSONs will be saved
```

### ⚙️ Step-by-Step Processing  

1️⃣ Setup Paths  
  - Sets the base directory based on the location of the Python script.
  - Defines:
    - input_dir: where the PDFs are located (sample_dataset/pdfs)
    - output_dir: where extracted .json files will be saved (sample_dataset/outputs)
  - Ensures the output folder exists using os.makedirs.

2️⃣ Load and Parse PDF  

For each PDF file in the input folder:  
- Opens the PDF using PyMuPDF
- For each page:
  - Extracts blocks of text
  - For each line in a block:
      - Gathers all spans (text segments with same font properties)
      - Collects:
        - Merged text string
        - Font size (rounded to 1 decimal place)

3️⃣ Merge Similar Lines (Same Page & Font Size)  

- Merges consecutive lines with:
  - Same font size
  - On the same page
- This reduces fragmentation of heading text across spans.

4️⃣ Determine Heading Levels  

 - Collects all unique font sizes from the PDF (rounded)
 - Sorts them descending, assuming larger fonts represent higher-level headings
 - Maps the top N font sizes to:
     - Title, H1, H2, H3, H4 (in that order)

 - Example mapping:  
```bash
{
  24.0: "Title",
  18.0: "H1",
  16.0: "H2",
  14.0: "H3",
  12.0: "H4"
}
```

5️⃣ Extract Outline  

- Iterates through merged lines:  
    - If the line matches the Title font size, it's appended to the final document title.
    - If it matches any H1–H4 level, it's added to the outline array with:
        - level: heading level
        - text: heading content
        - page: page number
- Duplicate entries are avoided using a seen set.

6️⃣ Output Generation   

- For each input PDF, a .json file is created in sample_dataset/outputs/
- Each output file contains:

```bash
{
  "title": "Document Title",
  "outline": [
    {
      "level": "H1",
      "text": "Introduction",
      "page": 1
    },
    {
      "level": "H2",
      "text": "Scope and Goals",
      "page": 2
    }
    ...
  ]
}
```

---

## ✅ Author

Built by [Balaji Saw , Om Kumavat].

---


