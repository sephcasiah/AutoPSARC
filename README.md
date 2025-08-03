# AutoPSARC
A lightweight batch tool for extracting PSARC archives from PS3 games. Recursively scans directories, unpacks all .psarc files using PSARC.exe, and preserves original folder structure.

### Note: This program assumes you already have psarc.exe in the working directory, please do not submit issues if you have not done this!


## 🔧 Features

- Recursively scans folders for `.psarc` files
- Uses `PSARC.exe` to extract archive contents
- Preserves original file structure
- Skips already extracted files
- Simple console interface

## 📦 Requirements

- Python 3.7+
- `PSARC.exe` (bundled or placed in the same directory)

> This tool does **not** modify or repackage `.psarc` files. It is read-only and meant for data extraction.

## 🚀 Usage

1. Place `batch_psarc_unpacker.py` and `PSARC.exe` in the same folder.
2. Open a terminal and run:

```bash
python batch_psarc_unpacker.py


⚠️ **Disclaimer**: This project does **not** include or distribute `PSARC.exe` or any other component of the Sony PS3 SDK. That software is proprietary and governed by Sony's licensing terms. You must legally obtain `PSARC.exe` yourself for this tool to function or use an open source alternative.
