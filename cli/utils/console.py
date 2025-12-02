"""
Console utilities with Rich for beautiful terminal output
"""

from rich.console import Console
from rich.theme import Theme
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box

# Custom theme for Rwanda NCSA
custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "red bold",
    "success": "green bold",
    "highlight": "magenta",
    "title": "bold blue",
    "subtitle": "dim",
    "engine": "bold cyan",
    "control": "yellow",
    "compliant": "green",
    "non_compliant": "red",
})

console = Console(theme=custom_theme)


def print_banner():
    """Print the application banner"""
    banner = """
[bold blue]╔═══════════════════════════════════════════════════════════════════════════════╗[/]
[bold blue]║[/]                                                                               [bold blue]║[/]
[bold blue]║[/]   [bold cyan]██████╗ ██╗    ██╗ █████╗ ███╗   ██╗██████╗  █████╗     [/]                [bold blue]║[/]
[bold blue]║[/]   [bold cyan]██╔══██╗██║    ██║██╔══██╗████╗  ██║██╔══██╗██╔══██╗    [/]                [bold blue]║[/]
[bold blue]║[/]   [bold cyan]██████╔╝██║ █╗ ██║███████║██╔██╗ ██║██║  ██║███████║    [/]                [bold blue]║[/]
[bold blue]║[/]   [bold cyan]██╔══██╗██║███╗██║██╔══██║██║╚██╗██║██║  ██║██╔══██║    [/]                [bold blue]║[/]
[bold blue]║[/]   [bold cyan]██║  ██║╚███╔███╔╝██║  ██║██║ ╚████║██████╔╝██║  ██║    [/]                [bold blue]║[/]
[bold blue]║[/]   [bold cyan]╚═╝  ╚═╝ ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝  ╚═══╝╚═════╝ ╚═╝  ╚═╝    [/]                [bold blue]║[/]
[bold blue]║[/]                                                                               [bold blue]║[/]
[bold blue]║[/]   [bold white]NCSA Compliance Auditor[/]                                                   [bold blue]║[/]
[bold blue]║[/]   [dim]National Cyber Security Authority - Republic of Rwanda[/]                    [bold blue]║[/]
[bold blue]║[/]                                                                               [bold blue]║[/]
[bold blue]║[/]   [bold green]v1.0.0[/] | [dim]196 Controls (169 Rwanda NCSA + 27 NIST SP 800-53)[/]              [bold blue]║[/]
[bold blue]║[/]                                                                               [bold blue]║[/]
[bold blue]╚═══════════════════════════════════════════════════════════════════════════════╝[/]
"""
    console.print(banner)


def print_success(message: str):
    """Print success message"""
    console.print(f"[success]✓[/] {message}")


def print_error(message: str):
    """Print error message"""
    console.print(f"[error]✗[/] {message}")


def print_warning(message: str):
    """Print warning message"""
    console.print(f"[warning]⚠[/] {message}")


def print_info(message: str):
    """Print info message"""
    console.print(f"[info]ℹ[/] {message}")


def create_table(title: str, columns: list, rows: list) -> Table:
    """Create a styled table"""
    table = Table(title=title, box=box.ROUNDED, header_style="bold cyan")

    for col in columns:
        table.add_column(col)

    for row in rows:
        table.add_row(*[str(cell) for cell in row])

    return table


def create_progress():
    """Create a progress bar with spinner"""
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    )


def print_engines_status(engines: list):
    """Print engines status table"""
    table = Table(title="Engine Status", box=box.ROUNDED, header_style="bold cyan")
    table.add_column("Engine", style="engine")
    table.add_column("Name")
    table.add_column("Port")
    table.add_column("Status")

    for engine in engines:
        status_color = "green" if engine.get("status") == "running" else "red"
        table.add_row(
            engine.get("id", ""),
            engine.get("name", ""),
            str(engine.get("port", "")),
            f"[{status_color}]{engine.get('status', 'unknown')}[/]"
        )

    console.print(table)


def print_compliance_result(result: dict):
    """Print compliance classification result"""
    panel = Panel(
        f"""
[bold]Control ID:[/] [control]{result.get('control_id', 'N/A')}[/]
[bold]Control Name:[/] {result.get('control_name', 'N/A')}
[bold]Confidence:[/] {result.get('confidence', 0):.2%}
[bold]Status:[/] [{'compliant' if result.get('compliant') else 'non_compliant'}]{'COMPLIANT' if result.get('compliant') else 'NON-COMPLIANT'}[/]

[bold]Recommendation:[/]
{result.get('recommendation', 'No recommendation available')}
""",
        title="[bold]Classification Result[/]",
        border_style="cyan"
    )
    console.print(panel)
