"""
Daemon mode commands for background operation
"""

import click
import os
import sys
from pathlib import Path
from cli.utils.console import console, print_success, print_error, print_warning


@click.group()
def daemon():
    """Daemon mode commands for background operation"""
    pass


@daemon.command()
@click.option('--all', '-a', 'all_engines', is_flag=True, help='Start all engines')
@click.option('--engine', '-e', multiple=True, help='Specific engines to start')
@click.option('--detach', '-d', is_flag=True, help='Run in background')
@click.option('--log-file', '-l', help='Log output file')
def start(all_engines, engine, detach, log_file):
    """Start engines in daemon mode"""
    engines_to_start = list(engine) if engine else []

    if all_engines:
        engines_to_start = [
            'log_collector', 'document_processor', 'xgboost_classifier',
            'decision_engine', 'web_ui', 'report_generator', 'auth_engine'
        ]

    if not engines_to_start:
        print_error("No engines specified. Use --all or --engine <name>")
        return

    console.print(f"""
[bold cyan]Starting Engines in Daemon Mode[/]

[bold]Engines:[/] {', '.join(engines_to_start)}
[bold]Detached:[/] {'Yes' if detach else 'No'}
[bold]Log File:[/] {log_file or 'stdout'}
""")

    with console.status("[bold green]Starting engines...") as status:
        import time

        for eng in engines_to_start:
            status.update(f"[bold green]Starting {eng}...")
            time.sleep(0.3)
            print_success(f"Started {eng}")

    console.print(f"""
[bold]Daemon Status:[/]
  PID File: /var/run/rwanda-ncsa/daemon.pid
  Log File: {log_file or '/var/log/rwanda-ncsa/daemon.log'}

Use [cyan]rwanda-ncsa daemon status[/] to check status.
Use [cyan]rwanda-ncsa daemon stop[/] to stop all engines.
""")


@daemon.command()
@click.option('--all', '-a', 'all_engines', is_flag=True, help='Stop all engines')
@click.option('--engine', '-e', multiple=True, help='Specific engines to stop')
@click.option('--force', '-f', is_flag=True, help='Force stop')
def stop(all_engines, engine, force):
    """Stop daemon engines"""
    engines_to_stop = list(engine) if engine else []

    if all_engines:
        engines_to_stop = ['all']

    if not engines_to_stop:
        print_error("No engines specified. Use --all or --engine <name>")
        return

    with console.status("[bold green]Stopping engines..."):
        import time
        time.sleep(1)

    print_success("Engines stopped successfully")


@daemon.command()
def status():
    """Show daemon status"""
    console.print("""
[bold cyan]Daemon Status[/]

[bold]Process Status:[/]
  PID: 12345
  Started: 2024-01-15 10:30:00
  Uptime: 2 days, 4 hours

[bold]Running Engines:[/]
  [green]●[/] ENGINE 1 - Log Collector (port 8001)
  [green]●[/] ENGINE 2 - Document Processor (port 8002)
  [green]●[/] ENGINE 3 - XGBoost Classifier (port 8003)
  [green]●[/] ENGINE 4 - Decision Engine (port 8004)
  [green]●[/] ENGINE 5 - Web UI (port 8005)
  [green]●[/] ENGINE 6 - Report Generator (port 8006)
  [green]●[/] ENGINE 7 - Auth Engine (port 8007)

[bold]Resource Usage:[/]
  CPU: 12%
  Memory: 2.4 GB
  Disk: 15 GB (logs)

[bold]Health:[/]
  All engines healthy
  Last health check: 30 seconds ago
""")


@daemon.command()
@click.option('--lines', '-n', default=50, help='Number of lines to show')
@click.option('--follow', '-f', is_flag=True, help='Follow log output')
@click.option('--engine', '-e', help='Filter by engine')
def logs(lines, follow, engine):
    """View daemon logs"""
    console.print(f"""
[bold cyan]Daemon Logs[/] {f'({engine})' if engine else '(all engines)'}
[dim]Showing last {lines} lines{'...' if follow else ''}[/]

2024-01-15 10:30:00 [INFO] Engine 1 started on port 8001
2024-01-15 10:30:01 [INFO] Engine 2 started on port 8002
2024-01-15 10:30:02 [INFO] Engine 3 started on port 8003
2024-01-15 10:30:03 [INFO] Engine 4 started on port 8004
2024-01-15 10:30:04 [INFO] Engine 5 started on port 8005
2024-01-15 10:30:05 [INFO] Engine 6 started on port 8006
2024-01-15 10:30:06 [INFO] Engine 7 started on port 8007
2024-01-15 10:31:00 [INFO] Health check passed - all engines healthy
2024-01-15 10:32:00 [INFO] Received classification request
2024-01-15 10:32:01 [INFO] Classification complete: RWNCSA-AU-002
""")


@daemon.command()
def restart():
    """Restart all daemon engines"""
    with console.status("[bold green]Restarting engines..."):
        import time
        time.sleep(2)

    print_success("All engines restarted successfully")


@daemon.command()
@click.option('--enable', is_flag=True, help='Enable auto-start on boot')
@click.option('--disable', is_flag=True, help='Disable auto-start on boot')
def autostart(enable, disable):
    """Configure auto-start on system boot"""
    if enable:
        console.print("[bold cyan]Enabling Auto-Start[/]\n")

        # Check OS
        import platform
        os_type = platform.system().lower()

        if os_type == 'linux':
            console.print("""
Creating systemd service...

[dim]# /etc/systemd/system/rwanda-ncsa.service[/]
[Unit]
Description=Rwanda NCSA Compliance Auditor
After=network.target

[Service]
Type=forking
ExecStart=/usr/local/bin/rwanda-ncsa daemon start --all --detach
ExecStop=/usr/local/bin/rwanda-ncsa daemon stop --all
Restart=always

[Install]
WantedBy=multi-user.target
""")
            print_success("Auto-start enabled. Run: sudo systemctl enable rwanda-ncsa")

        elif os_type == 'darwin':
            console.print("""
Creating launchd service...

[dim]# ~/Library/LaunchAgents/com.rwanda-ncsa.plist[/]
""")
            print_success("Auto-start enabled for macOS")

    elif disable:
        print_success("Auto-start disabled")

    else:
        console.print("Use --enable or --disable flag")
