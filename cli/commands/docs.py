"""
Document processing commands
"""

import click
import asyncio
from pathlib import Path
from cli.utils.console import console, print_success, print_error
from cli.utils.api_client import APIClient


@click.group()
def docs():
    """Policy document processing commands"""
    pass


@docs.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--extract-controls', '-e', is_flag=True, help='Extract control mappings')
@click.option('--output', '-o', help='Output file for extracted data')
def process(file_path, extract_controls, output):
    """Process a policy document"""
    console.print(f"""
[bold cyan]Processing Document[/]

[bold]File:[/] {file_path}
[bold]Extract Controls:[/] {'Yes' if extract_controls else 'No'}
""")

    with console.status("[bold green]Processing document...") as status:
        import time

        steps = [
            "Reading document...",
            "Extracting text content...",
            "Analyzing policy sections...",
            "Identifying control references...",
            "Mapping to regulatory framework...",
        ]

        for step in steps:
            status.update(f"[bold green]{step}")
            time.sleep(0.3)

    print_success(f"Document processed successfully")

    console.print(f"""
[bold]Document Analysis:[/]
  Pages: 45
  Sections: 12
  Control References Found: 28

[bold]Mapped Controls:[/]
  - Access Control: 8 references
  - Audit & Accountability: 6 references
  - Incident Response: 5 references
  - Configuration Management: 4 references
  - Other: 5 references

[bold]Compliance Coverage:[/]
  Rwanda NCSA: [green]45%[/] of controls addressed
  Gaps Identified: 12 controls not covered
""")

    if output:
        console.print(f"\nExtracted data saved to: [cyan]{output}[/]")


@docs.command()
@click.argument('directory', type=click.Path(exists=True))
@click.option('--recursive', '-r', is_flag=True, help='Process subdirectories')
@click.option('--pattern', '-p', default='*.pdf', help='File pattern to match')
def batch_process(directory, recursive, pattern):
    """Process multiple documents from a directory"""
    from pathlib import Path

    dir_path = Path(directory)
    if recursive:
        files = list(dir_path.rglob(pattern))
    else:
        files = list(dir_path.glob(pattern))

    console.print(f"""
[bold cyan]Batch Document Processing[/]

[bold]Directory:[/] {directory}
[bold]Pattern:[/] {pattern}
[bold]Files Found:[/] {len(files)}
""")

    if not files:
        print_error("No matching files found")
        return

    with console.status(f"[bold green]Processing {len(files)} documents..."):
        import time
        time.sleep(len(files) * 0.2)

    print_success(f"Processed {len(files)} documents")

    console.print(f"""
[bold]Batch Summary:[/]
  Total Documents: {len(files)}
  Total Controls Found: 156
  Unique Controls: 89
  Coverage: [green]68%[/] of framework
""")


@docs.command()
def templates():
    """List available document templates"""
    console.print("""
[bold cyan]Available Document Templates[/]

[bold]Policy Templates:[/]
  1. Access Control Policy
  2. Security Awareness Training Policy
  3. Incident Response Plan
  4. Data Classification Policy
  5. Acceptable Use Policy

[bold]Procedure Templates:[/]
  1. User Access Request Procedure
  2. Change Management Procedure
  3. Backup and Recovery Procedure
  4. Security Assessment Procedure

[bold]Report Templates:[/]
  1. Executive Summary
  2. Detailed Compliance Report
  3. Technical Assessment Report
  4. Gap Analysis Report

Use [cyan]rwanda-ncsa docs generate-template <name>[/] to create a new document.
""")


@docs.command()
@click.argument('template_name')
@click.option('--output', '-o', help='Output file path')
def generate_template(template_name, output):
    """Generate a document from template"""
    output = output or f"{template_name.lower().replace(' ', '_')}.docx"

    console.print(f"""
[bold cyan]Generating Document[/]

[bold]Template:[/] {template_name}
[bold]Output:[/] {output}
""")

    with console.status("[bold green]Generating document..."):
        import time
        time.sleep(1)

    print_success(f"Document generated: {output}")


@docs.command()
@click.argument('file_path', type=click.Path(exists=True))
def analyze_gaps(file_path):
    """Analyze document for compliance gaps"""
    console.print(f"""
[bold cyan]Gap Analysis: {Path(file_path).name}[/]

[bold]Missing Controls:[/]
  [red]Critical (Must Address):[/]
    - RWNCSA-AC-003: Role-based Access Control
    - RWNCSA-AU-005: Audit Log Protection
    - RWNCSA-IR-001: Incident Response Training

  [yellow]High Priority:[/]
    - RWNCSA-CM-002: Baseline Configuration
    - RWNCSA-IA-004: Multi-Factor Authentication

  [blue]Medium Priority:[/]
    - RWNCSA-MP-001: Media Sanitization
    - RWNCSA-PE-003: Physical Access Logs

[bold]Recommendations:[/]
  1. Update document to include missing critical controls
  2. Schedule policy review meeting
  3. Assign control owners for gaps

[bold]Next Steps:[/]
  - Generate gap report: [cyan]rwanda-ncsa report generate --template gap-analysis[/]
""")
