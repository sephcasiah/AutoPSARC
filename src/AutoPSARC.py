import argparse
import subprocess
import sys
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from contextlib import contextmanager
from typing import Optional, Set

CONFIG_PATH = Path.home() / ".autopsarc_config.json"
MAX_WORKERS = 4
DUMMY_LOCK = contextmanager(lambda: (yield))()

try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False

def load_config() -> dict:
    if CONFIG_PATH.exists():
        with CONFIG_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_config(config: dict) -> None:
    with CONFIG_PATH.open("w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)

def get_psarc_path(config: dict) -> Optional[Path]:
    path = config.get("psarc_path")
    if path and Path(path).exists():
        return Path(path)
    elif (Path(__file__).parent / "PSARC.exe").exists():
        bundled = Path(__file__).parent / "PSARC.exe"
        config["psarc_path"] = str(bundled)
        save_config(config)
        return bundled
    else:
        return None

def load_log_entries(log_path: Path) -> Set[str]:
    if log_path.exists():
        return set(log_path.read_text(encoding="utf-8").splitlines())
    return set()

def extract_single_psarc(psarc_path: Path, extract_dir: Path, psarc_exe: Path, log_path: Optional[Path], log_entries: Set[str], lock, base_input_dir: Path, verbose: bool = False) -> None:
    relative_path = psarc_path.relative_to(base_input_dir).with_suffix('')
    output_dir = extract_dir / relative_path
    output_dir.mkdir(parents=True, exist_ok=True)

    log_entry = str(psarc_path.resolve())
    if log_path and log_entry in log_entries:
        if verbose:
            print(f"Skipping already extracted: {psarc_path}")
        return

    if verbose:
        print(f"Extracting: {psarc_path} -> {output_dir}")

    try:
        result = subprocess.run(
            [
                str(psarc_exe),
                "extract",
                f"--input={psarc_path}",
                f"--to={output_dir}",
                "-y"
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        if log_path:
            with lock:
                with log_path.open("a", encoding="utf-8") as log:
                    log.write(f"{log_entry}\n")
    except subprocess.CalledProcessError as e:
        print(f"Error extracting {psarc_path.name}:")
        print(f"STDOUT:\n{e.stdout.decode(errors='ignore')}")
        print(f"STDERR:\n{e.stderr.decode(errors='ignore')}")

def extract_psarc_files(input_dir: Path, output_dir: Path, psarc_exe: Path, log_mode: bool, verbose: bool, workers: int) -> None:
    log_path = output_dir / "extraction.log" if log_mode else None
    log_entries = load_log_entries(log_path) if log_path else set()

    if log_path:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.touch(exist_ok=True)

    lock = Lock() if log_path else DUMMY_LOCK
    psarc_files = list(input_dir.rglob("*.psarc"))

    iterator = tqdm(psarc_files, desc="Extracting PSARC files") if TQDM_AVAILABLE else psarc_files

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [
            executor.submit(
                extract_single_psarc,
                psarc_file, output_dir, psarc_exe, log_path, log_entries, lock, input_dir, verbose
            )
            for psarc_file in iterator
        ]
        for future in as_completed(futures):
            future.result()

def ensure_tqdm_available() -> bool:
    config = load_config()
    if config.get("tqdm_enabled"):
        return True

    try:
        import tqdm  # noqa: F401
        config["tqdm_enabled"] = True
        save_config(config)
        return True
    except ImportError:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "tqdm"])
            config["tqdm_enabled"] = True
            save_config(config)
            return True
        except Exception:
            config["tqdm_enabled"] = False
            save_config(config)
            print("tqdm not available and could not be installed. Progress bar disabled.")
            return False

def print_full_help():
    print("""
AutoPSARC — Extended Help

Usage:
  --input / -i   : Directory to scan for PSARC files
  --output / -o  : Directory where files will be extracted
  --verbose / -v : Show detailed status updates
  --log / -l     : Enable log mode to skip previously extracted files
  --workers      : Number of parallel threads to use
  --psarc / -p   : Set the path to PSARC.exe (standalone use only)
  --help-full    : Show this help message with examples

Example:
  autopsarc.py -i ./archives -o ./extracted -v -l --workers 6
    """)

def main():
    parser = argparse.ArgumentParser(description="AutoPSARC extraction utility.")
    parser.add_argument("--input", "-i", type=Path, help="Directory to search for PSARC files.")
    parser.add_argument("--output", "-o", type=Path, help="Directory to extract files to.")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output.")
    parser.add_argument("--log", "-l", action="store_true", help="Enable log mode to skip previously extracted files.")
    parser.add_argument("--psarc", "-p", nargs="?", const=True, help="Set the path to PSARC.exe. Must be run standalone.")
    parser.add_argument("--workers", type=int, default=MAX_WORKERS, help="Number of parallel extraction workers.")
    parser.add_argument("--help-full", action="store_true", help="Show detailed help and usage examples.")

    args = parser.parse_args()

    if args.help_full:
        print_full_help()
        return

    config = load_config()

    if args.psarc is not None:
        if args.input or args.output:
            print("--psarc cannot be combined with other arguments.")
            return
        if args.psarc is True:
            path = input("Enter full path to PSARC.exe: ").strip().strip('"')
        else:
            path = str(args.psarc).strip().strip('"')

        if not Path(path).exists():
            print("Provided PSARC.exe path is invalid.")
            return

        config["psarc_path"] = path
        save_config(config)
        print(f"PSARC.exe path saved: {path}")
        return

    psarc_exe = get_psarc_path(config)
    if not psarc_exe:
        print("PSARC.exe not found. Please run with --psarc to set the path.")
        return

    if not args.input or not args.output:
        parser.print_help()
        return

    input_dir = args.input.resolve()
    output_dir = args.output.resolve()

    ensure_tqdm_available()
    extract_psarc_files(input_dir, output_dir, psarc_exe, args.log, args.verbose, args.workers)

if __name__ == "__main__":
    main()
