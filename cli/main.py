#!/usr/bin/env python3
"""
Rwanda NCSA Compliance Auditor CLI
Main entry point for command-line interface
"""

import click
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from cli.commands import auth, audit, logs, classify, report, docs, config, daemon
from cli.utils.console import console, print_banner


@click.group()
@click.version_option(version="1.0.0", prog_name="rwanda-ncsa")
@click.pass_context
def cli(ctx):
    """
    Rwanda NCSA Compliance Auditor

    A comprehensive compliance auditing tool for regulatory frameworks
    including Rwanda NCSA and NIST SP 800-53 controls.

    Use 'rwanda-ncsa COMMAND --help' for more information on a command.
    """
    ctx.ensure_object(dict)


# Register command groups
cli.add_command(auth.auth)
cli.add_command(audit.audit)
cli.add_command(logs.logs)
cli.add_command(classify.classify)
cli.add_command(report.report)
cli.add_command(docs.docs)
cli.add_command(config.config)
cli.add_command(daemon.daemon)


@cli.command()
def interactive():
    """Start interactive mode with full UI"""
    from cli.interactive import InteractiveShell
    print_banner()
    shell = InteractiveShell()
    shell.run()


@cli.command()
def status():
    """Show system status and running engines"""
    from cli.commands.status import show_status
    show_status()


@cli.command()
@click.option('--all', '-a', is_flag=True, help='Start all engines')
@click.option('--engine', '-e', multiple=True, help='Specific engines to start')
def start(all, engine):
    """Start compliance auditor engines"""
    from cli.commands.engine_control import start_engines
    start_engines(all_engines=all, specific_engines=engine)


@cli.command()
@click.option('--all', '-a', is_flag=True, help='Stop all engines')
@click.option('--engine', '-e', multiple=True, help='Specific engines to stop')
def stop(all, engine):
    """Stop compliance auditor engines"""
    from cli.commands.engine_control import stop_engines
    stop_engines(all_engines=all, specific_engines=engine)


def main():
    """Main entry point"""
    cli(obj={})


if __name__ == "__main__":
    main()
