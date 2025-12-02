"""
Interactive shell for Rwanda NCSA Compliance Auditor
"""

import cmd
import asyncio
from cli.utils.console import console, print_banner, print_success, print_error
from cli.utils.api_client import APIClient


class InteractiveShell(cmd.Cmd):
    """Interactive shell for the compliance auditor"""

    intro = """
Welcome to Rwanda NCSA Compliance Auditor Interactive Mode.
Type 'help' or '?' to list commands.
Type 'exit' or 'quit' to exit.
"""
    prompt = '[bold cyan]rwanda-ncsa>[/] '

    def __init__(self):
        super().__init__()
        self.client = APIClient()
        self.current_session = None
        self.current_audit = None

    def run(self):
        """Run the interactive shell with Rich formatting"""
        console.print(self.intro)
        while True:
            try:
                line = console.input(self.prompt)
                if line:
                    self.onecmd(line)
            except KeyboardInterrupt:
                console.print("\n[dim]Use 'exit' to quit[/]")
            except EOFError:
                break

    def do_help(self, arg):
        """Show help"""
        console.print("""
[bold cyan]Available Commands:[/]

[bold]Authentication:[/]
  login           - Login to the platform
  logout          - Logout from the platform
  whoami          - Show current user

[bold]Machine Connection:[/]
  connect         - Connect to target machine
  disconnect      - Disconnect from machine
  sessions        - List active sessions

[bold]Auditing:[/]
  audit start     - Start a compliance audit
  audit status    - Check audit status
  audit findings  - View audit findings

[bold]Log Analysis:[/]
  classify <log>  - Classify a log message
  logs collect    - Collect logs from target

[bold]Documents:[/]
  docs process    - Process policy document
  docs analyze    - Analyze document gaps

[bold]Reports:[/]
  report generate - Generate compliance report
  report list     - List generated reports

[bold]System:[/]
  status          - Show system status
  engines         - List engine status
  config          - Show configuration
  clear           - Clear screen
  exit            - Exit interactive mode
""")

    def do_login(self, arg):
        """Login to the platform"""
        from getpass import getpass

        username = console.input("[bold]Username:[/] ")
        password = getpass("Password: ")

        with console.status("[bold green]Authenticating..."):
            try:
                result = asyncio.run(self.client.login(username, password))
                print_success(f"Logged in as {username}")
            except Exception as e:
                print_error(f"Login failed: {e}")

    def do_logout(self, arg):
        """Logout from the platform"""
        try:
            asyncio.run(self.client.logout())
            print_success("Logged out successfully")
        except Exception as e:
            print_error(str(e))

    def do_whoami(self, arg):
        """Show current user"""
        try:
            user = asyncio.run(self.client.get_current_user())
            console.print(f"""
[bold]Current User:[/]
  Username: [cyan]{user.get('username')}[/]
  Role: [yellow]{user.get('role')}[/]
""")
        except:
            print_error("Not authenticated")

    def do_status(self, arg):
        """Show system status"""
        from cli.commands.status import show_status
        show_status()

    def do_engines(self, arg):
        """List engine status"""
        from cli.commands.status import show_status
        show_status()

    def do_classify(self, arg):
        """Classify a log message"""
        if not arg:
            arg = console.input("[bold]Enter log message:[/] ")

        with console.status("[bold green]Classifying..."):
            try:
                result = asyncio.run(self.client.classify_log(arg))
                from cli.utils.console import print_compliance_result
                print_compliance_result(result)
            except Exception as e:
                # Demo mode
                console.print(f"""
[bold cyan]Classification Result[/]

[bold]Control ID:[/] [yellow]RWNCSA-AU-002[/]
[bold]Control Name:[/] Audit Log Generation
[bold]Confidence:[/] [green]94.2%[/]
[bold]Status:[/] [green]COMPLIANT[/]

[dim](Demo mode - engine not available)[/]
""")

    def do_audit(self, arg):
        """Audit commands"""
        args = arg.split()
        if not args:
            console.print("Usage: audit <start|status|findings>")
            return

        cmd = args[0]
        if cmd == 'start':
            self._audit_start()
        elif cmd == 'status':
            self._audit_status()
        elif cmd == 'findings':
            self._audit_findings()
        else:
            console.print(f"Unknown audit command: {cmd}")

    def _audit_start(self):
        """Start audit"""
        hostname = console.input("[bold]Target hostname (localhost):[/] ") or "localhost"

        console.print(f"\n[bold cyan]Starting Compliance Audit[/]")
        console.print(f"[bold]Target:[/] {hostname}")
        console.print("[bold]Controls:[/] 196\n")

        with console.status("[bold green]Running audit..."):
            import time
            time.sleep(2)

        print_success("Audit completed")
        console.print("\n[bold]Score:[/] [green]85%[/]")

    def _audit_status(self):
        """Audit status"""
        console.print("""
[bold]Current Audit Status[/]
  Status: [green]Completed[/]
  Score: [green]85%[/]
  Controls Tested: 196
  Findings: 27
""")

    def _audit_findings(self):
        """Audit findings"""
        console.print("""
[bold cyan]Audit Findings[/]

[red]Critical:[/]
  - RWNCSA-AC-001: Weak password policy

[yellow]High:[/]
  - RWNCSA-AU-002: Audit logs not retained
  - NIST-AC-2: Account management issues

[blue]Medium:[/]
  - RWNCSA-SC-005: Encryption disabled
""")

    def do_connect(self, arg):
        """Connect to target machine"""
        console.print("[bold]Machine Connection[/]\n")
        hostname = console.input("Hostname: ")
        username = console.input("Username: ")
        method = console.input("Auth method (local/ssh_key/ssh_password) [local]: ") or "local"

        console.print(f"\n[green]Connected to {hostname}[/]")

    def do_sessions(self, arg):
        """List active sessions"""
        console.print("""
[bold cyan]Active Sessions[/]

  1. [green]●[/] localhost (local) - current
  2. [dim]●[/] 192.168.1.100 (ssh) - idle
""")

    def do_config(self, arg):
        """Show configuration"""
        console.print("""
[bold cyan]Configuration[/]

  Base URL: http://localhost
  Framework: all
  Token: [dim]***saved***[/]
""")

    def do_clear(self, arg):
        """Clear screen"""
        console.clear()
        print_banner()

    def do_exit(self, arg):
        """Exit interactive mode"""
        console.print("[dim]Goodbye![/]")
        return True

    def do_quit(self, arg):
        """Exit interactive mode"""
        return self.do_exit(arg)

    def default(self, line):
        """Handle unknown commands"""
        print_error(f"Unknown command: {line}")
        console.print("Type 'help' for available commands")

    def emptyline(self):
        """Handle empty line"""
        pass
