#!/usr/bin/env python3
"""Verify expected thesis terms/equation markers exist in extracted artifacts."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REQUIRED_PHRASES = [
    "krivoglaz",
    "wilkens",
    "contrast factor",
    "hexagonal anisotropy",
    "mwp",
    "cmwp",
]


REQUIRED_EQUATION_MARKERS = [
    "(2.",
    "(3.",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--full-text",
        type=Path,
        default=Path("data/thesis_text/full_text.txt"),
        help="Extracted thesis text file.",
    )
    parser.add_argument(
        "--equation-index",
        type=Path,
        default=Path("data/thesis_text/equation_index.md"),
        help="Generated equation index markdown.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if not args.full_text.exists():
        print(f"ERROR: Missing {args.full_text}. Run tools/extract_thesis_text.py first.")
        return 2
    if not args.equation_index.exists():
        print(f"ERROR: Missing {args.equation_index}. Run tools/extract_thesis_text.py first.")
        return 2

    full_text = args.full_text.read_text(encoding="utf-8").lower()
    eq_text = args.equation_index.read_text(encoding="utf-8").lower()

    missing_phrases = [p for p in REQUIRED_PHRASES if p not in full_text]
    missing_eq_markers = [m for m in REQUIRED_EQUATION_MARKERS if m not in eq_text]

    if missing_phrases or missing_eq_markers:
        if missing_phrases:
            print("Missing phrases:")
            for phrase in missing_phrases:
                print(f"  - {phrase}")
        if missing_eq_markers:
            print("Missing equation markers:")
            for marker in missing_eq_markers:
                print(f"  - {marker}")
        return 1

    print("Verification passed: required phrases and equation markers are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
