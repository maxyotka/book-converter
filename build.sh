#!/usr/bin/env bash
set -euo pipefail

SOURCE="Sotnikov_Venya-Puhov_3_Rusalka-Poisk.PM79RA.456797.fb2.zip"
BUILD_DIR="build"

echo "==> Parsing FB2..."
uv run python -m src.fb2_to_typst "$SOURCE" "$BUILD_DIR"

echo "==> Compiling PDF with Typst..."
typst compile "$BUILD_DIR/book.typ" "$BUILD_DIR/Rusalka-Poisk.pdf" --root . --font-path src/fonts

echo "==> Done: $BUILD_DIR/Rusalka-Poisk.pdf"
ls -lh "$BUILD_DIR/Rusalka-Poisk.pdf"
