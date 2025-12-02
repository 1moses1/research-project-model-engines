#!/usr/bin/env python3
"""
Rwanda NCSA Compliance Auditor - Unified Entry Point

This is the main entry point for the Rwanda NCSA Compliance Auditor platform.
It supports multiple modes of operation:
  - CLI: Command-line interface
  - Interactive: Full interactive shell
  - Daemon: Background service mode
  - UI: Web-based user interface

Usage:
    rwanda-ncsa                    # Show help
    rwanda-ncsa interactive        # Start interactive mode
    rwanda-ncsa status             # Show system status
    rwanda-ncsa start --all        # Start all engines
    rwanda-ncsa daemon start       # Start in daemon mode
"""

import sys
import os
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# Environment setup
os.environ.setdefault('RWANDA_NCSA_HOME', str(PROJECT_ROOT))


def main():
    """Main entry point"""
    # Import CLI after path setup
    from cli.main import cli
    cli()


def run_ui():
    """Run the Web UI"""
    import subprocess
    ui_path = PROJECT_ROOT / "engines" / "engine5-web-ui"

    if not ui_path.exists():
        print("ERROR: Web UI engine not found")
        sys.exit(1)

    subprocess.run([
        sys.executable, "-m", "uvicorn",
        "app.main:app",
        "--host", "0.0.0.0",
        "--port", "8005"
    ], cwd=str(ui_path))


def run_daemon():
    """Run in daemon mode (all engines)"""
    import subprocess
    from concurrent.futures import ThreadPoolExecutor

    engines = [
        ("engine1-log-collector", 8001),
        ("engine2-document-processor", 8002),
        ("engine3-xgboost-classifier", 8003),
        ("engine4-decision-engine", 8004),
        ("engine5-web-ui", 8005),
        ("engine6-report-generator", 8006),
        ("engine7-auth-engine", 8007),
    ]

    def start_engine(engine_info):
        name, port = engine_info
        engine_path = PROJECT_ROOT / "engines" / name
        if engine_path.exists():
            subprocess.run([
                sys.executable, "-m", "uvicorn",
                "app.main:app",
                "--host", "0.0.0.0",
                "--port", str(port)
            ], cwd=str(engine_path))

    with ThreadPoolExecutor(max_workers=len(engines)) as executor:
        executor.map(start_engine, engines)


if __name__ == "__main__":
    # Check for special modes
    if len(sys.argv) > 1:
        if sys.argv[1] == '--ui':
            run_ui()
        elif sys.argv[1] == '--daemon':
            run_daemon()
        else:
            main()
    else:
        main()
