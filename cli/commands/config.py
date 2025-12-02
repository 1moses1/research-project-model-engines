"""
Configuration commands
"""

import click
import json
from pathlib import Path
from cli.utils.console import console, print_success, print_error


CONFIG_DIR = Path.home() / ".rwanda-ncsa"
CONFIG_FILE = CONFIG_DIR / "config.json"


def get_config() -> dict:
    """Load configuration"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_config(config: dict):
    """Save configuration"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)


@click.group()
def config():
    """Configuration management commands"""
    pass


@config.command()
def show():
    """Show current configuration"""
    cfg = get_config()

    console.print("[bold cyan]Current Configuration[/]\n")

    if not cfg:
        console.print("[dim]No configuration found. Using defaults.[/]")
        console.print("\nUse [cyan]rwanda-ncsa config set <key> <value>[/] to configure.")
        return

    for key, value in cfg.items():
        if key in ['token', 'password', 'secret']:
            value = '***hidden***'
        console.print(f"  [bold]{key}:[/] {value}")

    console.print(f"\n[dim]Config file: {CONFIG_FILE}[/]")


@config.command()
@click.argument('key')
@click.argument('value')
def set(key, value):
    """Set a configuration value"""
    cfg = get_config()
    cfg[key] = value
    save_config(cfg)
    print_success(f"Set {key} = {value}")


@config.command()
@click.argument('key')
def get(key):
    """Get a configuration value"""
    cfg = get_config()
    value = cfg.get(key)

    if value is None:
        print_error(f"Key '{key}' not found")
    else:
        if key in ['token', 'password', 'secret']:
            console.print(f"{key} = ***hidden***")
        else:
            console.print(f"{key} = {value}")


@config.command()
@click.argument('key')
def unset(key):
    """Remove a configuration value"""
    cfg = get_config()

    if key in cfg:
        del cfg[key]
        save_config(cfg)
        print_success(f"Removed {key}")
    else:
        print_error(f"Key '{key}' not found")


@config.command()
@click.confirmation_option(prompt='Are you sure you want to reset all configuration?')
def reset():
    """Reset all configuration to defaults"""
    if CONFIG_FILE.exists():
        CONFIG_FILE.unlink()
    print_success("Configuration reset to defaults")


@config.command()
def init():
    """Initialize configuration interactively"""
    console.print("[bold cyan]Rwanda NCSA Compliance Auditor Setup[/]\n")

    # Base URL
    base_url = click.prompt(
        "API Base URL",
        default="http://localhost"
    )

    # Default framework
    framework = click.prompt(
        "Default compliance framework",
        type=click.Choice(['rwanda-ncsa', 'nist-800-53', 'all']),
        default='all'
    )

    # Output format
    output_format = click.prompt(
        "Default report format",
        type=click.Choice(['pdf', 'html', 'json']),
        default='pdf'
    )

    # Save
    cfg = {
        "base_url": base_url,
        "default_framework": framework,
        "default_output_format": output_format,
    }

    save_config(cfg)
    print_success("Configuration saved!")

    console.print(f"\n[dim]Config file: {CONFIG_FILE}[/]")
    console.print("\nNext: Use [cyan]rwanda-ncsa auth login[/] to authenticate.")


@config.command()
def engines():
    """Show engine configuration"""
    console.print("""
[bold cyan]Engine Configuration[/]

[bold]Default Ports:[/]
  ENGINE 1 - Log Collector:       8001
  ENGINE 2 - Document Processor:  8002
  ENGINE 3 - XGBoost Classifier:  8003
  ENGINE 4 - Decision Engine:     8004
  ENGINE 5 - Web UI:              8005
  ENGINE 6 - Report Generator:    8006
  ENGINE 7 - Auth Engine:         8007

[bold]Environment Variables:[/]
  ENGINE1_PORT=8001
  ENGINE2_PORT=8002
  ENGINE3_PORT=8003
  ENGINE4_PORT=8004
  ENGINE5_PORT=8005
  ENGINE6_PORT=8006
  ENGINE7_PORT=8007

Use [cyan]rwanda-ncsa config set engine.<name>.port <port>[/] to customize.
""")
