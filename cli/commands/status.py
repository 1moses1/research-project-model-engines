"""
Status command
"""

import asyncio
from cli.utils.console import console, print_engines_status
from cli.utils.api_client import APIClient


def show_status():
    """Show system status and running engines"""
    console.print("[bold cyan]Rwanda NCSA Compliance Auditor Status[/]\n")

    client = APIClient()

    # Check each engine
    engines = [
        {"id": "ENGINE 1", "name": "Log Collector", "port": 8001},
        {"id": "ENGINE 2", "name": "Document Processor", "port": 8002},
        {"id": "ENGINE 3", "name": "XGBoost Classifier", "port": 8003},
        {"id": "ENGINE 4", "name": "Decision Engine", "port": 8004},
        {"id": "ENGINE 5", "name": "Web UI", "port": 8005},
        {"id": "ENGINE 6", "name": "Report Generator", "port": 8006},
        {"id": "ENGINE 7", "name": "Auth Engine", "port": 8007},
    ]

    console.print("[bold]Checking engine status...[/]\n")

    for engine in engines:
        try:
            # Try to connect
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', engine['port']))
            sock.close()

            engine['status'] = 'running' if result == 0 else 'stopped'
        except Exception:
            engine['status'] = 'stopped'

    print_engines_status(engines)

    # Summary
    running = sum(1 for e in engines if e['status'] == 'running')
    total = len(engines)

    console.print(f"""
[bold]Summary:[/]
  Running: [green]{running}[/] / {total} engines
  Status: {'[green]All systems operational[/]' if running == total else f'[yellow]{total - running} engines offline[/]'}

[bold]Quick Commands:[/]
  Start all: [cyan]rwanda-ncsa start --all[/]
  Stop all:  [cyan]rwanda-ncsa stop --all[/]
  Logs:      [cyan]rwanda-ncsa daemon logs -f[/]
""")
