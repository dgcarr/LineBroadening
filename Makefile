.PHONY: thesis_extract thesis_verify

thesis_extract:
	python -m pip install --quiet pypdf
	python tools/extract_thesis_text.py

thesis_verify:
	python tools/verify_thesis_sections.py
