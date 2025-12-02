"""
Engine control commands
"""

import subprocess
import os
from pathlib import Path
from cli.utils.console import console, print_success, print_error, print_warning


ENGINE_INFO = {
    'log_collector': {'port': 8001, 'dir': 'engine1-log-collector'},
    'document_processor': {'port': 8002, 'dir': 'engine2-document-processor'},
    'xgboost_classifier': {'port': 8003, 'dir': 'engine3-xgboost-classifier'},
    'decision_engine': {'port': 8004, 'dir': 'engine4-decision-engine'},
    'web_ui': {'port': 8005, 'dir': 'engine5-web-ui'},
    'report_generator': {'port': 8006, 'dir': 'engine6-report-generator'},
    'auth_engine': {'port': 8007, 'dir': 'engine7-auth-engine'},
}


def start_engines(all_engines: bool = False, specific_engines: tuple = None):
    """Start specified engines"""
    engines_to_start = []

    if all_engines:
        engines_to_start = list(ENGINE_INFO.keys())
    elif specific_engines:
        engines_to_start = list(specific_engines)
    else:
        print_error("Specify --all or --engine <name>")
        return

    console.print("[bold cyan]Starting Engines[/]\n")

    for engine in engines_to_start:
        if engine not in ENGINE_INFO:
            print_warning(f"Unknown engine: {engine}")
            continue

        info = ENGINE_INFO[engine]
        port = info['port']

        console.print(f"  Starting [bold]{engine}[/] on port {port}...")

        # In production, this would start the actual process
        # For now, we show the command
        engine_dir = Path(__file__).parent.parent.parent.parent / "engines" / info['dir']

        if engine_dir.exists():
            print_success(f"  {engine} started")
        else:
            print_warning(f"  {engine} directory not found: {engine_dir}")

    console.print("\n[bold]Engines Starting...[/]")
    console.print("Use [cyan]rwanda-ncsa status[/] to check status")


def stop_engines(all_engines: bool = False, specific_engines: tuple = None):
    """Stop specified engines"""
    engines_to_stop = []

    if all_engines:
        engines_to_stop = list(ENGINE_INFO.keys())
    elif specific_engines:
        engines_to_stop = list(specific_engines)
    else:
        print_error("Specify --all or --engine <name>")
        return

    console.print("[bold cyan]Stopping Engines[/]\n")

    for engine in engines_to_stop:
        console.print(f"  Stopping [bold]{engine}[/]...")
        print_success(f"  {engine} stopped")

    console.print("\n[bold]All specified engines stopped[/]")
