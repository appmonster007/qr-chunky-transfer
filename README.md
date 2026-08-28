# qr-chunky-transfer

Quick scripts to transfer data between air-gapped systems through visual mode.

`enc.py` splits a file into chunks and renders each as a QR code image (for
airgapped transfer). `dec.py` scans a directory of those QR code images and
reassembles the original file, verifying integrity via sha256.

## Setup (macOS)

`dec.py` needs one of two QR-decoding backends. `pyzbar` + Pillow is the
more reliable one — OpenCV's built-in QR detector frequently fails to read
these images (especially high chunk-count / dense QR codes).

```bash
cd qr-chunky-transfer
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install qrcode pyzbar pillow
brew install zbar   # pyzbar wraps the system libzbar; it must be installed separately
```

### Known issue: `ImportError: Unable to find zbar shared library`

On macOS, Homebrew installs `libzbar` under `/opt/homebrew/lib`, which is
not on the dynamic linker's default search path, so pyzbar can't find it
even though `zbar` is installed. Fix by setting `DYLD_LIBRARY_PATH` when
running Python:

```bash
DYLD_LIBRARY_PATH=/opt/homebrew/lib .venv/bin/python dec.py <input_dir> <output_dir>
```

(On Apple Silicon Homebrew lives at `/opt/homebrew`; on Intel Macs it's
usually `/usr/local`, so use `/usr/local/lib` instead.)

## Usage

Encode any file into QR images:

```bash
.venv/bin/python enc.py <input_file> [output_dir]
```

- `<input_file>`: any file to transfer (required)
- `[output_dir]`: directory for the QR PNGs (default `<input_file_stem>-qr`)

Decode a directory of QR images back into the original file:

```bash
DYLD_LIBRARY_PATH=/opt/homebrew/lib .venv/bin/python dec.py <input_dir> [output_dir]
```

- `<input_dir>`: directory of QR code screenshots/images (required)
- `[output_dir]`: where to write the reconstructed file (default `.`); the
  original filename is taken from the QR header

On success, prints `OK <path> <bytes>B sha256=<hash>`. Warnings like
`_zbar_decode_databar: Assertion "seg->finder >= 0" failed` during
scanning are harmless — zbar attempting to decode unrelated barcode
symbologies from the same image.
