#!/usr/bin/env bash
set -euo pipefail

SRC_DIR="../src"

if ! command -v ruff >/dev/null 2>&1; then
  echo "Error: ruff is not installed or not in PATH." >&2
  exit 1
fi

echo "Running Ruff lint (check) on ${SRC_DIR}..."
ruff check "${SRC_DIR}"

echo "Running Ruff format on ${SRC_DIR}..."
ruff format "${SRC_DIR}"

echo "Done."
