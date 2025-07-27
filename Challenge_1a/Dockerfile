FROM python:3.10-slim-bullseye

WORKDIR /app

COPY . .

RUN apt-get update && apt-get upgrade -y && pip install --no-cache-dir pymupdf && apt-get clean && rm -rf /var/lib/apt/lists/*

CMD ["python", "process_pdfs.py"]
