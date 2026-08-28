#!/bin/sh
# Round-trip test: <file> -> enc.py (QR PNGs) -> dec.py -> compare.
#
# Usage: ./test.sh [path/to/file]
#   with an arg : encodes/decodes that exact file
#   no arg      : builds a zip of this repo and tests that
#
# On success the temp files are deleted; on failure they are kept for debugging.
set -eu

REPO=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
WORK=$(mktemp -d "${TMPDIR:-/tmp}/qrtest.XXXXXX")
OK=0
cleanup() {
  if [ "$OK" -eq 1 ]; then
    rm -rf "$WORK"
  else
    echo "FAIL: artifacts kept at $WORK"
  fi
}
trap cleanup EXIT

# --- pick a Python with the deps, bootstrapping a .venv if needed ---------------
PY="$REPO/.venv/bin/python"
[ -x "$PY" ] || PY=python3
if ! "$PY" -c 'import qrcode,pyzbar,PIL' 2>/dev/null; then
  echo "deps missing; creating $REPO/.venv ..."
  python3 -m venv "$REPO/.venv"
  PY="$REPO/.venv/bin/python"
  "$PY" -m pip -q install --upgrade pip
  "$PY" -m pip -q install qrcode pyzbar pillow
fi
"$PY" -c 'import qrcode,pyzbar,PIL' 2>/dev/null || {
  echo "pyzbar import still failing - is libzbar installed? (brew install zbar)"
  exit 1
}

# --- pyzbar needs libzbar on the loader path (Homebrew is off it) --------------
for d in /opt/homebrew/lib /usr/local/lib; do
  [ -d "$d" ] && { export DYLD_LIBRARY_PATH="$d${DYLD_LIBRARY_PATH:+:$DYLD_LIBRARY_PATH}"; break; }
done

# --- 1. obtain the source file ------------------------------------------------
if [ "$#" -ge 1 ]; then
  [ -f "$1" ] || { echo "no such file: $1"; exit 1; }
  NAME=$(basename -- "$1")
  cp -- "$1" "$WORK/$NAME"
  SRC="$WORK/$NAME"
  echo "using provided file: $1"
else
  NAME=src.zip
  SRC="$WORK/$NAME"
  FILES=$(cd "$REPO" && git ls-files 2>/dev/null | grep -v '^test\.sh$' || true)
  [ -n "$FILES" ] || FILES="enc.py dec.py README.md LICENSE .gitignore"
  ( cd "$REPO" && zip -q -X "$SRC" $FILES )
  echo "built repo zip: $SRC"
fi
SRC_SHA=$(shasum -a 256 "$SRC" | awk '{print $1}')
echo "source   : $NAME  $(wc -c < "$SRC" | tr -d ' ')B  sha256=$SRC_SHA"

# --- 2. encode to QR PNGs ----------------------------------------------------
"$PY" "$REPO/enc.py" "$SRC" "$WORK/qr"
echo "encoded  : $(ls "$WORK/qr" | wc -l | tr -d ' ') PNGs -> $WORK/qr"

# --- 3. decode back --------------------------------------------------------
"$PY" "$REPO/dec.py" "$WORK/qr" "$WORK/out"
OUT="$WORK/out/$NAME"
[ -f "$OUT" ] || { echo "decode produced no $OUT"; exit 1; }
OUT_SHA=$(shasum -a 256 "$OUT" | awk '{print $1}')

# --- 4. verify -----------------------------------------------------------
echo
echo "original : $SRC_SHA"
echo "decoded  : $OUT_SHA"
if cmp -s "$SRC" "$OUT" && [ "$SRC_SHA" = "$OUT_SHA" ]; then
  echo "RESULT: PASS - round trip is byte-identical"
  OK=1
  exit 0
else
  echo "RESULT: FAIL - decoded file differs from original"
  exit 1
fi
