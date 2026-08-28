# qr-chunky-transfer

Move a file across an air gap as a sequence of QR codes.

`enc.py` reads any file, splits it into fixed-size chunks, base64-encodes
each, and renders every chunk as its own QR code PNG. Display or print the
PNGs on the source machine, capture them on the target (screenshots or
photos), then `dec.py` reads the images back, reassembles the file, and
verifies it byte-for-byte with a sha256 recorded at encode time.

## How it works

- **Chunking.** The payload is cut into 2100-byte chunks (`CS` in
  `enc.py`). Each chunk is emitted as compact JSON `{"i":<index>,
  "d":"<base64>"}` and drawn as a fixed **version-40**, error-correction
  **L** QR code, so every PNG has identical dimensions.
- **Header.** `chunk 00000.png` is a header QR:
  `{"h":1,"name":<original filename>,"size":<bytes>,"sha256":<hex>,
  "n":<chunk count>}`. `dec.py` uses it to know how many chunks to expect,
  what to name the output, and what hash/size to check against.
- **Ordering.** PNGs are named `00000.png`, `00001.png`, … but `dec.py`
  reassembles by the `i` index inside each QR, so filename sort order and
  missing/duplicate captures don't matter.
- **Decoding.** `dec.py` tries `pyzbar` first (most reliable on dense
  codes) and falls back to OpenCV's `QRCodeDetector` if `pyzbar` returns
  nothing for an image and `opencv-python` is installed.
- **Verification.** If any chunk index is missing, or the reassembled
  sha256 / length doesn't match the header, `dec.py` exits non-zero and
  writes nothing.

## Setup (macOS)

`enc.py` needs `qrcode`. `dec.py` needs `pyzbar` + Pillow; `opencv-python`
is optional and only used as a fallback decoder.

```bash
cd qr-chunky-transfer
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install qrcode pyzbar pillow   # add opencv-python for the fallback
brew install zbar   # pyzbar wraps the system libzbar; it must be installed separately
```

### Known issue: `ImportError: Unable to find zbar shared library`

On macOS, Homebrew installs `libzbar` under `/opt/homebrew/lib`, which is
not on the dynamic linker's default search path, so pyzbar can't find it
even though `zbar` is installed. Fix by setting `DYLD_LIBRARY_PATH` when
running Python:

```bash
DYLD_LIBRARY_PATH=/opt/homebrew/lib .venv/bin/python dec.py <input_dir> [output_dir]
```

(On Apple Silicon Homebrew lives at `/opt/homebrew`; on Intel Macs it's
usually `/usr/local`, so use `/usr/local/lib` instead.)

## Usage

Encode any file into QR PNGs:

```bash
.venv/bin/python enc.py <input_file> [output_dir]
```

- `<input_file>`: any file to transfer (required)
- `[output_dir]`: directory for the QR PNGs (default
  `<input_file_name>-qr`); recreated from scratch on each run
- prints `<bytes>B <sha256> -> <output_dir>/ <count> PNGs`

Decode a directory of QR images back into the original file:

```bash
DYLD_LIBRARY_PATH=/opt/homebrew/lib .venv/bin/python dec.py <input_dir> [output_dir]
```

- `<input_dir>`: directory of QR PNGs / screenshots / photos (required);
  every file in it is tried, non-images are skipped
- `[output_dir]`: where to write the reconstructed file (default `.`,
  created if needed); the filename comes from the header QR
- on success prints `OK <path> <bytes>B <sha256>`

Warnings like `_zbar_decode_databar: Assertion "seg->finder >= 0" failed`
during scanning are harmless — zbar attempting other barcode symbologies
on the same image.

## Test

`test.sh` runs a full round trip and checks the result is byte-identical:

```bash
./test.sh [path/to/file]
```

With no argument it zips this repo and tests that. It picks up
`./.venv/bin/python`, creating the venv and installing deps if missing.
Temp files are deleted on pass and kept (path printed) on fail.
