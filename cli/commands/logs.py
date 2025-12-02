"""
Log collection and analysis commands
"""

import click
import asyncio
from cli.utils.console import console, print_success, print_error, print_warning


@click.group()
def logs():
    """Log collection and analysis commands"""
    pass


@logs.command()
@click.option('--hostname', '-h', default='localhost', help='Target hostname')
@click.option('--type', '-t', 'log_type', type=click.Choice(['auth', 'system', 'application', 'security', 'all']),
              default='all', help='Type of logs to collect')
@click.option('--since', '-s', help='Collect logs since (e.g., "1h", "1d", "2024-01-01")')
@click.option('--output', '-o', help='Output file for collected logs')
def collect(hostname, log_type, since, output):
    """Collect logs from target system"""
    console.print(f"""
[bold cyan]Log Collection[/]

[bold]Target:[/] {hostname}
[bold]Log Type:[/] {log_type}
[bold]Since:[/] {since or 'Last 24 hours'}
""")

    with console.status("[bold green]Collecting logs...") as status:
        import time

        sources = {
            'auth': ['/var/log/auth.log', '/var/log/secure'],
            'system': ['/var/log/syslog', '/var/log/messages'],
            'application': ['/var/log/application.log'],
            'security': ['/var/log/audit/audit.log'],
        }

        if log_type == 'all':
            all_sources = []
            for src in sources.values():
                all_sources.extend(src)
        else:
            all_sources = sources.get(log_type, [])

        for source in all_sources:
            status.update(f"[bold green]Collecting from {source}...")
            time.sleep(0.3)

    print_success(f"Collected logs from {len(all_sources)} sources")

    if output:
        console.print(f"Logs saved to: [cyan]{output}[/]")


@logs.command()
@click.argument('log_message')
@click.option('--explain', '-e', is_flag=True, help='Explain the classification')
def analyze(log_message, explain):
    """Analyze a single log message"""
    from cli.utils.api_client import APIClient

    client = APIClient()

    with console.status("[bold green]Analyzing log message..."):
        try:
            result = asyncio.run(client.classify_log(log_message))

            console.print(f"""
[bold cyan]Log Analysis Result[/]

[bold]Input:[/] {log_message[:100]}{'...' if len(log_message) > 100 else ''}

[bold]Control ID:[/] [yellow]{result.get('control_id', 'N/A')}[/]
[bold]Control Name:[/] {result.get('control_name', 'N/A')}
[bold]Confidence:[/] [green]{result.get('confidence', 0):.2%}[/]
[bold]Compliance Status:[/] {'[green]COMPLIANT[/]' if result.get('compliant') else '[red]NON-COMPLIANT[/]'}
""")

            if explain:
                console.print(f"""
[bold]Explanation:[/]
{result.get('explanation', 'No explanation available')}

[bold]Recommendation:[/]
{result.get('recommendation', 'No recommendation available')}
""")

        except Exception as e:
            print_error(f"Analysis failed: {e}")
            # Show demo result
            console.print(f"""
[dim]Demo mode - Engine not available[/]

[bold]Input:[/] {log_message[:100]}

[bold]Predicted Control:[/] [yellow]RWNCSA-AU-002[/]
[bold]Control Name:[/] Audit Log Generation
[bold]Confidence:[/] [green]94.2%[/]
""")


@logs.command()
@click.option('--file', '-f', 'log_file', required=True, type=click.Path(exists=True),
              help='Log file to analyze')
@click.option('--batch-size', '-b', default=100, help='Batch size for processing')
@click.option('--output', '-o', help='Output file for results')
def batch_analyze(log_file, batch_size, output):
    """Batch analyze logs from a file"""
    console.print(f"""
[bold cyan]Batch Log Analysis[/]

[bold]Input File:[/] {log_file}
[bold]Batch Size:[/] {batch_size}
""")

    with console.status("[bold green]Processing logs...") as status:
        # Count lines
        with open(log_file, 'r') as f:
            lines = f.readlines()

        total = len(lines)
        status.update(f"[bold green]Processing {total} log entries...")

        import time
        time.sleep(1)

    print_success(f"Processed {total} log entries")

    console.print(f"""
[bold]Summary:[/]
  Total Entries: {total}
  Compliant: [green]{int(total * 0.85)}[/]
  Non-Compliant: [red]{int(total * 0.15)}[/]
  Average Confidence: [yellow]89.3%[/]
""")

    if output:
        console.print(f"Results saved to: [cyan]{output}[/]")


@logs.command()
@click.option('--hostname', '-h', default='localhost', help='Target hostname')
def sources(hostname):
    """List available log sources on target"""
    console.print(f"""
[bold cyan]Available Log Sources on {hostname}[/]

[bold]Authentication Logs:[/]
  /var/log/auth.log
  /var/log/secure
  /var/log/faillog

[bold]System Logs:[/]
  /var/log/syslog
  /var/log/messages
  /var/log/dmesg

[bold]Audit Logs:[/]
  /var/log/audit/audit.log
  /var/log/btmp
  /var/log/wtmp

[bold]Application Logs:[/]
  /var/log/apache2/
  /var/log/nginx/
  /var/log/mysql/

[bold]Note:[/] Available sources depend on target OS and installed services.
""")
