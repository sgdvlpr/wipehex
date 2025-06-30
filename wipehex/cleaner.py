from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.text import Text
import humanize
import re
import os
import typer

class Cleaner:
    def scan_directory(self, path: str, extensions: list[str], min_size_str: str, sort_by: str):
        files = self.find_matching_files(path, extensions, min_size_str, sort_by)
        self.display_files(files)
    
    def find_matching_files(self, path, extensions, min_size_str, sort_by):
        min_size_bytes = self.parse_size(min_size_str)
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

        return files
    
    def display_files(self, files, title="📁 Scan Results"):
        console = Console()
        table = Table(title=title)

        table.add_column("File Name", style="bold cyan")
        table.add_column("Size")
        table.add_column("Modified")
        table.add_column("Type", style="magenta")
        table.add_column("Path", overflow="fold")

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
            console.print("No matching files found.")
    
    def parse_size(self, size_str: str) -> int:
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

    def delete_files(self, files):
        for f in files:
            try:
                os.remove(f["path"])
                typer.echo(f"🗑️ Deleted: {f['path']}")
            except Exception as e:
                typer.echo(f"⚠️ Failed to delete {f['path']}: {e}")
        typer.echo(f"\n✅ Deleted {len(files)} file(s).")