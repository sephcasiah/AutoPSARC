# AutoPSARC
This is a command-line utility designed to batch extract `.psarc` archive files, typically used in PlayStation 3 game development. It is ideal for modding, reverse engineering, and game asset preservation.

The tool is designed for efficiency, ease of use, and automation. It includes support for parallel processing, persistent configuration, and optional logging to avoid redundant work.

### Note: This program assumes you already have psarc.exe in the working directory or on your PC, please do not submit issues if you have not done this!

---

## Features

- Recursive batch extraction of `.psarc` files from a given input directory
- Multi-threaded extraction using configurable worker count
- Automatic or user-defined path to `PSARC.exe`, saved for future use
- Optional log-based extraction to avoid reprocessing files
- Progress bar integration with optional `tqdm` support
- Persistent configuration stored in the user profile directory

---

## Requirements

- Python 3.10 or newer
- `PSARC.exe` (required for extraction; not bundled with the tool)
- Optional: `tqdm` for progress bar display (installed automatically if missing)

---

## Installation

Install Python dependencies manually (optional):

```bash
pip install tqdm
```
The tool will attempt to install tqdm on its own if it is not available.

## Usage
Step 1: Set the path to PSARC.exe
This must be done once. The path will be saved and reused in future runs.

```bash
AutoPSARC.py --psarc "C:/Path/To/PSARC.exe"
```
Alternatively, if no path is specified, the tool will prompt you for one.

Step 2: Extract PSARC files
```bash
AutoPSARC.py -i ./input_dir -o ./output_dir
```

## Common Options
Argument	Description
-i, --input	Directory to search for .psarc files
-o, --output	Directory where files will be extracted
-v, --verbose	Enables detailed output during extraction
-l, --log	Enables logging mode to skip already extracted files
--workers	Number of concurrent threads (default: 4)

### Example
```bash
AutoPSARC.py -i ./archives -o ./extracted -v -l --workers 6
```

## Advanced
Changing the PSARC path
```bash
AutoPSARC.py --psarc
```
This allows you to enter or update the path to PSARC.exe.

## Extended Help
```bash
AutoPSARC.py --help-full
```
Displays usage examples and additional notes.

## Output Structure
Each .psarc archive is extracted into its own subfolder.

The output folder structure preserves relative paths from the input directory.

## Configuration
The tool uses a config file stored at:

```bash
~/.autopsarc_config.json
```
This file stores the location of PSARC.exe & Whether tqdm is enabled

## Other persistent options
TBD


## Disclaimer
This tool is intended for personal, research, and archival purposes. Ensure you have the legal right to extract and use the contents of .psarc files before proceeding.

> ⚠️ **Disclaimer**: This project does **not** include or distribute `PSARC.exe` or any other component of the Sony PS3 SDK. That software is proprietary and governed by Sony's licensing terms. You must legally obtain `PSARC.exe` yourself for this tool to function or use an open source alternative.
