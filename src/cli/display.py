from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.text import Text
from rich.table import Table
from pathlib import Path

class ConsoleDisplay:
    def __init__(self):
        self.console = Console()

    def print_startup(self, root_dir: Path):
        self.console.print(Panel(
            f"[bold blue]Foldy AI Agent[/bold blue]\n[getattr]Target Directory:[/getattr] [green]{root_dir}[/green]",
            title="[bold white]Initializing[/bold white]",
            border_style="blue"
        ))

    def stream_token(self, token: str):
        self.console.print(token, end="", style="italic cyan")

    def print_tool_call(self, tool_name: str, tool_input: dict):
        self.console.print(f"\n[bold yellow]⚙ Executing Tool:[/bold yellow] [bold white]{tool_name}[/bold white]")
        if tool_input:
            table = Table(show_header=False, box=None)
            for key, value in tool_input.items():
                table.add_row(f"[dim]{key}:[/dim]", str(value))
            self.console.print(table)

    def print_tool_result(self, result: str):
        if "Error" in result or "Denied" in result:
            self.console.print(f"[bold red]✘ {result}[/bold red]")
        else:
            self.console.print(f"[bold green]✔ {result}[/bold green]\n")

    def print_final_response(self, text: str):
        self.console.print("\n" + "─" * 20)
        self.console.print(Panel(text, title="Foldy's Summary", border_style="green"))