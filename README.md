# 📄 PDF Heading Hierarchy Extractor

A Python tool to extract **heading hierarchies (Title, H1, H2...)** from PDFs using **font size and styling characteristics**. Supports multilingual documents using **OCR fallback**, and outputs structured data in **JSON format**.

---

## 📚 Table of Contents

- [🎯 Objective](#-objective)
- [🚀 Features](#-features)
- [🧠 How It Works](#-how-it-works)
- [📐 Architecture](#-architecture)
- [📦 JSON Output Format](#-json-output-format)
- [🔧 Installation](#-installation)
- [🛠 Usage](#-usage)
- [💡 Use Cases](#-use-cases)
- [📸 Demo](#-demo)
- [📂 File Structure](#-file-structure)
- [📑 License](#-license)
- [👨‍💻 Author](#-author)

---

## 🎯 Objective

Extract heading hierarchy (like Title, H1, H2...) from each page of a PDF by analyzing **font size and styling characteristics**. Supports batch processing and multilingual documents (e.g., Hindi, Japanese) using OCR fallback.

---

## 🚀 Features

✅ Extracts Title, H1, H2, H3, etc. from PDFs  
✅ Font-size-based dynamic hierarchy detection  
✅ Supports multilingual documents (e.g., Hindi, Japanese)  
✅ OCR fallback for scanned or image-based PDFs  
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
