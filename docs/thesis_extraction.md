# Thesis text extraction

This repository includes a reproducible extraction pipeline for `Ribarik-PhD-Thesis.pdf`.

## Primary (text-layer) pipeline

This path is preferred when the PDF has embedded selectable text.

```bash
make thesis_extract
```

Outputs:

- `data/thesis_text/full_text.txt`
- `data/thesis_text/equation_index.md`

Then validate required sections/terms with:

```bash
make thesis_verify
```

## Offline OCR fallback pipeline (if text extraction is poor)

If `full_text.txt` is sparse, garbled, or missing expected sections, run an OCR pass fully offline and re-extract.

### Expected dependencies

- System packages (Linux):
  - `tesseract-ocr`
  - `ocrmypdf`
  - `ghostscript`
- Python package:
  - `pypdf`

Example dependency install (Debian/Ubuntu):

```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr ocrmypdf ghostscript
python -m pip install pypdf
```

### OCR + extraction workflow

```bash
ocrmypdf --force-ocr --optimize 0 Ribarik-PhD-Thesis.pdf data/thesis_text/Ribarik-PhD-Thesis.ocr.pdf
python tools/extract_thesis_text.py --pdf data/thesis_text/Ribarik-PhD-Thesis.ocr.pdf
python tools/verify_thesis_sections.py
```

Notes:

- `--optimize 0` keeps OCR output deterministic and minimizes lossy recompression side effects.
- The generated `equation_index.md` is heuristic (regex + equation-like line filters). It is intended as a citation aid, not symbolic math parsing.
