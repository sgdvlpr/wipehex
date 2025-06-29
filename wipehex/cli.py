import typer
from wipehex.cleaner import scan_directory

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
    scan_directory(path, ext_list, min_size, sort_by)

@app.command()
def welcome():
    print("Welcome to wipehex!")

if __name__ == "__main__":
    app()    