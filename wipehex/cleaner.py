from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.text import Text
import humanize
import re
import typer

def scan_directory(path: str, extensions: list[str], min_size: str, sort_by: str):
    console = Console()
    table = Table(title=f"📁 Scan Results: {path}")

    table.add_column("File Name", style="bold cyan")
    table.add_column("Size")
    table.add_column("Modified")
    table.add_column("Type", style="magenta")
    table.add_column("Path", overflow="fold")

    min_size_bytes = parse_size(min_size)

    path_obj = Path(path).expanduser().resolve()
    files = []

    for file in path_obj.rglob("*"):
        if file.is_file():
            size_bytes = file.stat().st_size
            if size_bytes < min_size_bytes:
                continue
            if extensions and file.suffix not in extensions:
                continue
            files.append({
                "name": file.name,
                "path": str(file),
                "size_bytes": size_bytes,
                "modified": datetime.fromtimestamp(file.stat().st_mtime),
                "type": file.suffix or "unknown"
            })
    
    # Sorting
    files.sort(key=lambda f: (
        f["size_bytes"] if sort_by == "size"
        else f["modified"] if sort_by == "date"
        else f["name"].lower()
    ), reverse=True)

    for f in files:
        table.add_row(
            f["name"],
            humanize.naturalsize(f["size_bytes"]),
            f["modified"].strftime("%Y-%m-%d %H:%M"),
            f["type"],
            f["path"]
        
        )
    if files:
        console.print(table)
    else:
        console.print(Text("No matching files found.", style="bold yellow"))

def parse_size(size_str: str) -> int:
    # Remove leading/trainling spaces, convert to uppercase to standardize 
    size_str = size_str.strip().upper()

    # Match number + optional decimal + optional unit (B, KB, GB, TB)
    match = re.match(r"(\d+(\.\.d+)?)([KMGT]?B)?", size_str)

    if not match:
        raise typer.BadParameter("Invalid size format")

    number = float(match.group(1))  # The numeric part (e.g., 1.5)
    unit = match.group(3) or "B"    # The unit (e.g., KB), default to bytes ("B") if missing

    multiplier = {
        "B": 1,
        "KB": 1024,
        "MB": 1024 ** 2,
        "GB": 1024 ** 3,
        "TB": 1024 ** 4
    }[unit]

    # Multiply number by the unit's multiplier and return as int bytes
    return int(number * multiplier)

# Define extensions that are considered "junk"
JUNK_EZTENSIONS = [".log", ".tmp", ".bak",".old", ".~"]

# Find junk files using pathlib
def find_junk(directory=".") -> list[Path]:
    directory = Path(directory)
    return [f for f in directory.rglob("*") if f.suffix in JUNK_EZTENSIONS and f.is_file()]

# Delete junk files
def delete_junk(files: list[Path]):
    for f in files:
        try:
            f.unlink()
        except Exception as e:
            print(f'Failed to delete {f}: {e}')
