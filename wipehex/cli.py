import os
import typer
from wipehex.cleaner import Cleaner

cl = Cleaner()

app = typer.Typer()

@app.command()
def scan(
    path: str = typer.Option(".", "--path", help="Directory to scan"),
    ext: list[str] = typer.Option(None, "--ext", "-e", help="Comma-separated file extensions (e.g. .log,.tmp)"),
    min_size: str = typer.Option("0B", "--min-size", help="Minimum file size, e.g. 10KB, 1.5MB"),
    sort_by: str = typer.Option("size", help="Sort files by type")
):
    """Scan and list potential junk files"""
    ext_list = [e.strip() for e in ext[0].split(",")] if ext else []
    cl.scan_directory(path, ext_list, min_size, sort_by)

@app.command()
def clean(
    path: str = typer.Option(".", "--path", help="Directory to clean"),
    ext: list[str] = typer.Option(None, "--ext", "-e", help="Comma-separated extensions (e.g. .log,.tmp)"),
    min_size: str = typer.Option("0B", "--min-size", help="Minimum file size, e.g. 10KB, 1MB"),
    sort_by: str = typer.Option("size", help="Sort files by 'size', 'date', or 'name'"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Only show files that would be deleted")
):
    """Delete junk files matching given criteria"""
    ext_list = [e.strip() for e in ext[0].split(",")] if ext else []
    files = cl.find_matching_files(path, ext_list, min_size, sort_by)

    if not files:
        typer.echo("✅ No files matched the given criteria.")
        raise typer.Exit()

    if dry_run:
        cl.display_files(files, title="🧹 [Dry Run] Files that would be deleted")
        if typer.confirm("Do you want to delete these files?", default=False):
            cl.delete_files(files)

    else:
        cl.delete_files(files)

@app.command()
def welcome():
    print("Welcome to wipehex!")

if __name__ == "__main__":
    app()    