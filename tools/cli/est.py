#!/usr/bin/env python3
"""
Embedded Security Testing - CLI Tool
Educational tool for firmware analysis and manipulation
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.prompt import Prompt, Confirm
    from rich.tree import Tree
    from rich.syntax import Syntax
    from rich.progress import Progress, SpinnerColumn, TextColumn
except ImportError:
    print("Installing required packages...")
    subprocess.run([sys.executable, "-m", "pip", "install", "rich", "-q"])
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.prompt import Prompt, Confirm
    from rich.tree import Tree
    from rich.syntax import Syntax
    from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

# Paths
WORK_DIR = Path("/work")
SAMPLES_DIR = WORK_DIR / "samples"
EXTRACT_DIR = WORK_DIR / "extracted"
BUILD_DIR = WORK_DIR / "build"
SRC_DIR = WORK_DIR / "buildroot" / "src"


def clear_screen():
    console.clear()


def print_banner():
    banner = """
╔═══════════════════════════════════════════════════════════╗
║         Embedded Security Testing - CLI Tool              ║
║              Educational Use Only                         ║
╚═══════════════════════════════════════════════════════════╝"""
    console.print(Panel(banner, style="bold red"))
    console.print("[yellow]Disclaimer:[/yellow] For educational purposes only. The selection of")
    console.print("TP-Link as an example is arbitrary and implies nothing.\n")


def run_command(cmd, capture=True, show_output=False):
    """Run a shell command"""
    try:
        if show_output:
            result = subprocess.run(cmd, shell=True)
            return result.returncode == 0, ""
        else:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.returncode == 0, result.stdout + result.stderr
    except Exception as e:
        return False, str(e)


def list_firmware_files():
    """List available firmware files"""
    files = []
    if SAMPLES_DIR.exists():
        for f in SAMPLES_DIR.iterdir():
            if f.is_file() and f.suffix in ['.bin', '.img', '.fw']:
                files.append(f)
    return files


def select_firmware():
    """Let user select a firmware file"""
    files = list_firmware_files()

    if not files:
        console.print("[red]No firmware files found in samples/[/red]")
        console.print("Place .bin, .img, or .fw files in the samples directory.")
        return None

    table = Table(title="Available Firmware Files")
    table.add_column("#", style="cyan")
    table.add_column("Filename", style="green")
    table.add_column("Size", style="yellow")

    for i, f in enumerate(files, 1):
        size = f.stat().st_size
        size_str = f"{size:,} bytes ({size/1024/1024:.2f} MB)"
        table.add_row(str(i), f.name, size_str)

    console.print(table)

    choice = Prompt.ask("Select firmware", choices=[str(i) for i in range(1, len(files)+1)] + ["0"], default="0")

    if choice == "0":
        return None

    return files[int(choice) - 1]


def analyze_firmware():
    """Analyze firmware file"""
    clear_screen()
    print_banner()
    console.print("[bold cyan]═══ Firmware Analysis ═══[/bold cyan]\n")

    firmware = select_firmware()
    if not firmware:
        return

    console.print(f"\n[bold]Analyzing:[/bold] {firmware.name}\n")

    # File info
    console.print("[bold yellow]── File Information ──[/bold yellow]")
    success, output = run_command(f"file '{firmware}'")
    console.print(output.strip())

    size = firmware.stat().st_size
    console.print(f"Size: {size:,} bytes ({size/1024/1024:.2f} MB)")

    success, output = run_command(f"md5sum '{firmware}'")
    if success:
        console.print(f"MD5: {output.split()[0]}")

    # TP-Link header check
    console.print("\n[bold yellow]── TP-Link Header ──[/bold yellow]")
    success, output = run_command(f"mktplinkfw -i '{firmware}' 2>&1")
    console.print(output.strip() if output.strip() else "[dim]Not a TP-Link firmware or invalid header[/dim]")

    # Binwalk scan
    console.print("\n[bold yellow]── Binwalk Signature Scan ──[/bold yellow]")
    success, output = run_command(f"binwalk '{firmware}'")
    console.print(output.strip())

    Prompt.ask("\nPress Enter to continue")


def extract_firmware():
    """Extract firmware filesystem"""
    clear_screen()
    print_banner()
    console.print("[bold cyan]═══ Extract Firmware ═══[/bold cyan]\n")

    firmware = select_firmware()
    if not firmware:
        return

    # Create extract directory
    extract_name = firmware.stem
    extract_path = EXTRACT_DIR / extract_name

    if extract_path.exists():
        if Confirm.ask(f"[yellow]{extract_name}[/yellow] already extracted. Re-extract?"):
            shutil.rmtree(extract_path)
        else:
            console.print(f"Using existing extraction at: {extract_path}")
            Prompt.ask("\nPress Enter to continue")
            return

    extract_path.mkdir(parents=True, exist_ok=True)

    console.print(f"\n[bold]Extracting:[/bold] {firmware.name}")
    console.print(f"[bold]Output:[/bold] {extract_path}\n")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Extracting with binwalk...", total=None)
        success, output = run_command(f"binwalk --run-as=root -e -C '{extract_path}' '{firmware}'")

    if success:
        # Count extracted files
        file_count = sum(1 for _ in extract_path.rglob('*') if _.is_file())
        console.print(f"\n[green]✓ Extraction complete![/green]")
        console.print(f"  Extracted {file_count} files to {extract_path}")
    else:
        console.print(f"\n[red]✗ Extraction failed[/red]")
        console.print(output)

    Prompt.ask("\nPress Enter to continue")


def browse_files():
    """Browse extracted files"""
    clear_screen()
    print_banner()
    console.print("[bold cyan]═══ Browse Extracted Files ═══[/bold cyan]\n")

    # List extractions
    if not EXTRACT_DIR.exists():
        console.print("[red]No extracted firmware found. Extract a firmware first.[/red]")
        Prompt.ask("\nPress Enter to continue")
        return

    extractions = [d for d in EXTRACT_DIR.iterdir() if d.is_dir()]

    if not extractions:
        console.print("[red]No extracted firmware found. Extract a firmware first.[/red]")
        Prompt.ask("\nPress Enter to continue")
        return

    table = Table(title="Extracted Firmware")
    table.add_column("#", style="cyan")
    table.add_column("Name", style="green")

    for i, d in enumerate(extractions, 1):
        table.add_row(str(i), d.name)

    console.print(table)

    choice = Prompt.ask("Select extraction", choices=[str(i) for i in range(1, len(extractions)+1)] + ["0"], default="0")

    if choice == "0":
        return

    base_path = extractions[int(choice) - 1]
    current_path = base_path

    # File browser loop
    while True:
        clear_screen()
        print_banner()

        rel_path = current_path.relative_to(base_path) if current_path != base_path else Path(".")
        console.print(f"[bold cyan]═══ {base_path.name} ═══[/bold cyan]")
        console.print(f"[dim]Path: /{rel_path}[/dim]\n")

        items = sorted(current_path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))

        table = Table(show_header=True, header_style="bold")
        table.add_column("#", style="cyan", width=4)
        table.add_column("Name", style="white")
        table.add_column("Size", style="yellow", justify="right")
        table.add_column("Type", style="dim")

        # Parent directory
        if current_path != base_path:
            table.add_row("..", "[bold blue]..[/bold blue]", "", "Parent")

        for i, item in enumerate(items, 1):
            if item.is_dir():
                table.add_row(str(i), f"[bold blue]{item.name}/[/bold blue]", "", "Directory")
            else:
                size = item.stat().st_size
                if size < 1024:
                    size_str = f"{size} B"
                elif size < 1024*1024:
                    size_str = f"{size/1024:.1f} KB"
                else:
                    size_str = f"{size/1024/1024:.1f} MB"

                # Get file type
                success, ftype = run_command(f"file -b '{item}' 2>/dev/null | cut -c1-30")
                table.add_row(str(i), item.name, size_str, ftype.strip()[:30])

        console.print(table)
        console.print("\n[dim]Commands: number=select, ..=parent, v=view, h=hexdump, s=strings, q=quit[/dim]")

        cmd = Prompt.ask("Enter command").strip().lower()

        if cmd == "q" or cmd == "0":
            break
        elif cmd == ".." and current_path != base_path:
            current_path = current_path.parent
        elif cmd.isdigit():
            idx = int(cmd) - 1
            if 0 <= idx < len(items):
                selected = items[idx]
                if selected.is_dir():
                    current_path = selected
                else:
                    # View file
                    view_file(selected)
        elif cmd.startswith("v") and len(cmd.split()) > 1:
            idx = int(cmd.split()[1]) - 1
            if 0 <= idx < len(items) and items[idx].is_file():
                view_file(items[idx])
        elif cmd.startswith("h") and len(cmd.split()) > 1:
            idx = int(cmd.split()[1]) - 1
            if 0 <= idx < len(items) and items[idx].is_file():
                view_hexdump(items[idx])
        elif cmd.startswith("s") and len(cmd.split()) > 1:
            idx = int(cmd.split()[1]) - 1
            if 0 <= idx < len(items) and items[idx].is_file():
                view_strings(items[idx])


def view_file(filepath):
    """View file contents"""
    clear_screen()
    console.print(f"[bold cyan]═══ {filepath.name} ═══[/bold cyan]\n")

    # Check if text file
    success, output = run_command(f"file -b '{filepath}'")
    is_text = any(x in output.lower() for x in ['text', 'ascii', 'utf-8', 'script', 'json', 'xml'])

    if is_text:
        try:
            content = filepath.read_text(errors='replace')[:50000]
            # Try to detect language for syntax highlighting
            ext = filepath.suffix.lower()
            lang_map = {'.py': 'python', '.sh': 'bash', '.c': 'c', '.h': 'c',
                       '.js': 'javascript', '.json': 'json', '.xml': 'xml',
                       '.html': 'html', '.css': 'css', '.conf': 'ini', '.cfg': 'ini'}
            lang = lang_map.get(ext, 'text')

            syntax = Syntax(content, lang, theme="monokai", line_numbers=True)
            console.print(syntax)
        except Exception as e:
            console.print(f"[red]Error reading file: {e}[/red]")
    else:
        view_hexdump(filepath)

    Prompt.ask("\nPress Enter to continue")


def view_hexdump(filepath):
    """View hex dump of file"""
    clear_screen()
    console.print(f"[bold cyan]═══ Hexdump: {filepath.name} ═══[/bold cyan]\n")

    success, output = run_command(f"xxd '{filepath}' | head -100")
    console.print(output)

    if filepath.stat().st_size > 1600:
        console.print("[dim]... (showing first 100 lines)[/dim]")

    Prompt.ask("\nPress Enter to continue")


def view_strings(filepath):
    """View strings in file"""
    clear_screen()
    console.print(f"[bold cyan]═══ Strings: {filepath.name} ═══[/bold cyan]\n")

    success, output = run_command(f"strings -n 8 '{filepath}' | head -200")
    console.print(output)

    Prompt.ask("\nPress Enter to continue")


def compile_code():
    """Compile code using buildroot toolchain"""
    clear_screen()
    print_banner()
    console.print("[bold cyan]═══ Cross-Compile for MIPS ═══[/bold cyan]\n")

    if not SRC_DIR.exists():
        console.print(f"[red]Source directory not found: {SRC_DIR}[/red]")
        Prompt.ask("\nPress Enter to continue")
        return

    # List source files
    sources = list(SRC_DIR.glob("*.c"))

    if not sources:
        console.print(f"[yellow]No .c files found in {SRC_DIR}[/yellow]")
        console.print("Place your C source files in the buildroot/src directory.")
        Prompt.ask("\nPress Enter to continue")
        return

    table = Table(title="Source Files")
    table.add_column("#", style="cyan")
    table.add_column("Filename", style="green")

    for i, f in enumerate(sources, 1):
        table.add_row(str(i), f.name)

    console.print(table)

    choice = Prompt.ask("Select file to compile", choices=[str(i) for i in range(1, len(sources)+1)] + ["0"], default="0")

    if choice == "0":
        return

    source = sources[int(choice) - 1]
    output_name = source.stem

    console.print(f"\n[bold]Compiling:[/bold] {source.name}")
    console.print(f"[bold]Output:[/bold] {output_name}\n")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Compiling with MIPS GCC...", total=None)
        success, output = run_command(
            f"mipsel-linux-gnu-gcc -static '{source}' -o '{SRC_DIR}/{output_name}' 2>&1"
        )

    if success:
        console.print(f"\n[green]✓ Compilation successful![/green]")
        success, file_info = run_command(f"file '{SRC_DIR}/{output_name}'")
        console.print(f"[dim]{file_info.strip()}[/dim]")
    else:
        console.print(f"\n[red]✗ Compilation failed[/red]")
        console.print(output)

    Prompt.ask("\nPress Enter to continue")


def rebuild_firmware():
    """Rebuild firmware image"""
    clear_screen()
    print_banner()
    console.print("[bold cyan]═══ Rebuild Firmware Image ═══[/bold cyan]\n")

    console.print("[yellow]This feature rebuilds a modified firmware image.[/yellow]")
    console.print("You need:")
    console.print("  1. An extracted firmware (squashfs-root)")
    console.print("  2. The original firmware for kernel/header\n")

    # Check for extractions with squashfs-root
    if not EXTRACT_DIR.exists():
        console.print("[red]No extracted firmware found.[/red]")
        Prompt.ask("\nPress Enter to continue")
        return

    squashfs_dirs = []
    for d in EXTRACT_DIR.iterdir():
        if d.is_dir():
            for sub in d.rglob("squashfs-root"):
                if sub.is_dir():
                    squashfs_dirs.append(sub)

    if not squashfs_dirs:
        console.print("[red]No squashfs-root directories found in extractions.[/red]")
        Prompt.ask("\nPress Enter to continue")
        return

    table = Table(title="Available Filesystems")
    table.add_column("#", style="cyan")
    table.add_column("Path", style="green")

    for i, d in enumerate(squashfs_dirs, 1):
        table.add_row(str(i), str(d.relative_to(EXTRACT_DIR)))

    console.print(table)

    choice = Prompt.ask("Select filesystem", choices=[str(i) for i in range(1, len(squashfs_dirs)+1)] + ["0"], default="0")

    if choice == "0":
        return

    squashfs_root = squashfs_dirs[int(choice) - 1]

    # Select original firmware
    console.print("\n[bold]Select original firmware for kernel/header:[/bold]")
    firmware = select_firmware()
    if not firmware:
        return

    output_path = BUILD_DIR / f"modified_{firmware.name}"
    BUILD_DIR.mkdir(parents=True, exist_ok=True)

    console.print(f"\n[bold]Building firmware...[/bold]")
    console.print(f"  Filesystem: {squashfs_root}")
    console.print(f"  Original: {firmware}")
    console.print(f"  Output: {output_path}\n")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        # Create squashfs
        task = progress.add_task("Creating squashfs...", total=None)
        squashfs_img = BUILD_DIR / "rootfs.squashfs"
        success, output = run_command(
            f"mksquashfs '{squashfs_root}' '{squashfs_img}' -comp lzma -noappend -all-root 2>&1"
        )

        if not success:
            console.print(f"\n[red]✗ Failed to create squashfs[/red]")
            console.print(output)
            Prompt.ask("\nPress Enter to continue")
            return

        # Extract kernel from original
        progress.update(task, description="Extracting kernel...")
        kernel_img = BUILD_DIR / "kernel.bin"
        run_command(f"dd if='{firmware}' of='{kernel_img}' bs=1 skip=512 count=1048064 2>/dev/null")

        # Try to build with mktplinkfw
        progress.update(task, description="Building firmware image...")
        success, output = run_command(
            f"mktplinkfw -H 0x30200001 -W 0x1 -F 4Mlzma -N 'TP-LINK' -V 'ver. 1.0' "
            f"-k '{kernel_img}' -r '{squashfs_img}' -o '{output_path}' -j -a 0x10000 2>&1"
        )

    if success and output_path.exists():
        console.print(f"\n[green]✓ Firmware built successfully![/green]")
        console.print(f"  Output: {output_path}")
        console.print(f"  Size: {output_path.stat().st_size:,} bytes")

        # Verify
        success, verify = run_command(f"mktplinkfw -i '{output_path}' 2>&1")
        console.print(f"\n[dim]{verify.strip()}[/dim]")
    else:
        console.print(f"\n[red]✗ Firmware build failed[/red]")
        console.print(output)

    Prompt.ask("\nPress Enter to continue")


def main_menu():
    """Main menu"""
    while True:
        clear_screen()
        print_banner()

        table = Table(show_header=False, box=None)
        table.add_column("Option", style="cyan", width=4)
        table.add_column("Description", style="white")

        table.add_row("1", "Analyze Firmware")
        table.add_row("2", "Extract Firmware")
        table.add_row("3", "Browse Extracted Files")
        table.add_row("4", "Cross-Compile (MIPS)")
        table.add_row("5", "Rebuild Firmware")
        table.add_row("", "")
        table.add_row("0", "Exit")

        console.print(table)

        choice = Prompt.ask("\nSelect option", choices=["0", "1", "2", "3", "4", "5"], default="0")

        if choice == "0":
            console.print("\n[dim]Goodbye![/dim]")
            break
        elif choice == "1":
            analyze_firmware()
        elif choice == "2":
            extract_firmware()
        elif choice == "3":
            browse_files()
        elif choice == "4":
            compile_code()
        elif choice == "5":
            rebuild_firmware()


if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        console.print("\n[dim]Interrupted. Goodbye![/dim]")
        sys.exit(0)
