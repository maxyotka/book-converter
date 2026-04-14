#!/usr/bin/env bash
# Build all books in books/ to build/*.pdf
set -euo pipefail
cd "$(dirname "$0")"
uv run book-converter build books --out-dir build
