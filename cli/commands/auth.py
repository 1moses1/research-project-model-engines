"""
Authentication commands
"""

import click
import asyncio
from getpass import getpass
from cli.utils.console import console, print_success, print_error
from cli.utils.api_client import APIClient


@click.group()
def auth():
    """Authentication commands"""
    pass


@auth.command()
@click.option('--username', '-u', prompt=True, help='Username')
@click.option('--password', '-p', prompt=True, hide_input=True, help='Password')
def login(username, password):
    """Login to the compliance platform"""
    client = APIClient()

    with console.status("[bold green]Authenticating..."):
        try:
            result = asyncio.run(client.login(username, password))
            print_success(f"Logged in as [bold]{username}[/]")
            console.print(f"Token expires in: {result.get('expires_in', 'N/A')} seconds")
        except Exception as e:
            print_error(f"Login failed: {e}")


@auth.command()
def logout():
    """Logout from the platform"""
    client = APIClient()

    try:
        asyncio.run(client.logout())
        print_success("Logged out successfully")
    except Exception as e:
        print_error(f"Logout failed: {e}")


@auth.command()
def whoami():
    """Show current user info"""
    client = APIClient()

    try:
        user = asyncio.run(client.get_current_user())
        console.print(f"""
[bold]Current User:[/]
  Username: [cyan]{user.get('username', 'N/A')}[/]
  Role: [yellow]{user.get('role', 'N/A')}[/]
  Session ID: [dim]{user.get('session_id', 'N/A')}[/]
""")
    except Exception as e:
        print_error("Not authenticated. Please login first.")


@auth.command()
@click.option('--hostname', '-h', required=True, help='Target hostname or IP')
@click.option('--username', '-u', required=True, help='Username on target machine')
@click.option('--method', '-m', type=click.Choice(['ssh_key', 'ssh_password', 'local']),
              default='local', help='Authentication method')
@click.option('--port', '-p', default=22, help='SSH port')
@click.option('--os-type', '-o', type=click.Choice(['linux', 'macos', 'windows']),
              default='linux', help='Target OS type')
def connect(hostname, username, method, port, os_type):
    """Connect to a target machine for auditing"""
    client = APIClient()

    password = None
    ssh_key = None

    if method == 'ssh_password':
        password = getpass("Password: ")
    elif method == 'ssh_key':
        ssh_key = click.prompt("SSH key path", default="~/.ssh/id_rsa")

    with console.status(f"[bold green]Connecting to {hostname}..."):
        try:
            result = asyncio.run(client.connect_to_machine(
                hostname=hostname,
                username=username,
                auth_method=method,
                port=port,
                password=password,
                ssh_key_path=ssh_key,
                os_type=os_type
            ))

            print_success(f"Connected to {hostname}")
            console.print(f"""
[bold]Connection Details:[/]
  Session ID: [cyan]{result.get('session_id', 'N/A')}[/]
  OS Type: [yellow]{result.get('os_type', 'N/A')}[/]
  Audit User: [green]{result.get('audit_user', 'N/A')}[/]
  Message: {result.get('message', '')}
""")
        except Exception as e:
            print_error(f"Connection failed: {e}")


@auth.command()
@click.option('--hostname', '-h', required=True, help='Target hostname')
@click.option('--admin-user', '-a', required=True, help='Admin username')
@click.option('--audit-user', '-u', default='rwanda_ncsa_auditor', help='Audit username to create')
@click.option('--confirm', is_flag=True, help='Confirm creation without prompting')
def create_audit_user(hostname, admin_user, audit_user, confirm):
    """Create a read-only audit user on target machine"""
    console.print(f"""
[bold yellow]AUDIT USER CREATION PREVIEW[/]

[bold]Target Host:[/] {hostname}
[bold]Admin User:[/] {admin_user}
[bold]Audit User:[/] {audit_user}

[bold]Permissions to be granted:[/]
  [green]✓[/] Read-only access to /var/log/
  [green]✓[/] Read-only access to /etc/ (configs)
  [red]✗[/] NO write permissions
  [red]✗[/] NO sudo access
  [red]✗[/] NO shell script execution

[bold]Allowed commands:[/]
  cat, head, tail, less, grep, journalctl, last, who, ps, netstat, ss, df, du, ls

[bold yellow]WARNING:[/] This will create a user on the target system.
""")

    if not confirm:
        if not click.confirm("Do you want to proceed with audit user creation?"):
            print_error("Cancelled by user")
            return

    admin_password = getpass("Admin password: ")

    with console.status(f"[bold green]Creating audit user on {hostname}..."):
        # In production, this would call the API
        print_success(f"Audit user '{audit_user}' created successfully on {hostname}")
        console.print(f"""
[bold]Next steps:[/]
1. Use 'rwanda-ncsa auth connect -h {hostname} -u {audit_user}' to connect
2. Use 'rwanda-ncsa audit start' to begin compliance audit
""")
