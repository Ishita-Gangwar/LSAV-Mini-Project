import asyncio
import os
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, DataTable, Button, Label, ProgressBar
from textual.containers import Grid, Vertical

# FIX 1: Read LOG_DIR from the environment so it stays in sync with logmini.sh.
# Default matches the shell script's hardcoded path; override with:
#   LOG_DIR=~/practice/test_logs python dashboard.py
LOG_DIR = os.path.expanduser(os.environ.get("LOG_DIR", "~/practice/logs"))

class LogminiUI(App):
    TITLE = "Logmini — System Distribution Dashboard"

    CSS = """
    #main_grid { layout: grid; grid-size: 2; grid-columns: 1fr 1fr; padding: 1; border: round blue; }
    #log-panel { border: solid green; background: black; color: lightgreen; height: 100%; overflow-y: scroll; padding: 1; }
    #details-panel { border: solid magenta; padding: 1; }

    /* Visualization Styling */
    #viz-container { background: $boost; border: tall white; margin: 1 0; padding: 1; height: auto; }
    #gauge-bar { color: $accent; margin: 1 0; }
    .legend { text-style: italic; color: gray; }

    Button { width: 100%; margin-top: 1; }
    DataTable { height: 8; margin-bottom: 1; }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        yield Grid(
            Vertical(
                Label("📊 Storage Distribution"),
                DataTable(id="stats-table"),
                Vertical(
                    Label("Capacity Distribution (Active vs Archive)"),
                    ProgressBar(id="gauge-bar", total=100, show_eta=False),
                    Label("█ Active Logs | ░ Archived Logs", id="legend-text", classes="legend"),
                    id="viz-container"
                ),
                Button("Run Janitor Sweep", id="run-btn", variant="primary"),
                id="details-panel"
            ),
            Vertical(
                Label("📟 Bash Activity Log"),
                Static("System Ready. Waiting for sweep...", id="console-out"),
                id="log-panel"
            ),
            id="main_grid"
        )
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#stats-table")
        table.add_columns("File Category", "Files", "Total Size")
        self.refresh_data()

    def refresh_data(self) -> None:
        if not os.path.exists(LOG_DIR):
            self.query_one("#console-out").update(
                f"[yellow]Warning:[/] LOG_DIR not found: {LOG_DIR}"
            )
            return

        # FIX 2: Scan for .gz archives in LOG_DIR itself — logmini.sh never creates
        # an archive/ subdirectory; it rotates files in-place as *.log.TIMESTAMP.gz.
        active_logs = [f for f in os.listdir(LOG_DIR) if f.endswith(".log")]
        archives    = [f for f in os.listdir(LOG_DIR) if f.endswith(".gz")]

        log_size = sum(
            os.path.getsize(os.path.join(LOG_DIR, f)) for f in active_logs
        ) / 1024

        arc_size = sum(
            os.path.getsize(os.path.join(LOG_DIR, f)) for f in archives
        ) / 1024

        total_size = log_size + arc_size

        table = self.query_one("#stats-table")
        table.clear()
        table.add_row("Active (.log)",    str(len(active_logs)), f"{log_size:.1f} KB")
        table.add_row("Archived (.gz)",   str(len(archives)),    f"{arc_size:.1f} KB")

        if total_size > 0:
            percentage = (log_size / total_size) * 100
            self.query_one("#gauge-bar").progress = percentage
            self.query_one("#legend-text").update(
                f"Active: {percentage:.1f}% | Archived: {100 - percentage:.1f}%"
            )
        else:
            self.query_one("#gauge-bar").progress = 0

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id != "run-btn":
            return

        console = self.query_one("#console-out")
        console.update("🏃 Executing logmini.sh...")

        # FIX 3: Use asyncio.create_subprocess_exec so the UI stays responsive
        # while the shell script runs. The old subprocess.run blocked the event
        # loop, freezing the entire Textual interface until it finished.
        try:
            proc = await asyncio.create_subprocess_exec(
                "bash", "./logmini.sh",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env={**os.environ, "LOG_DIR": LOG_DIR},
            )
            stdout, stderr = await proc.communicate()

            output = stdout.decode().strip() if stdout else ""
            errors = stderr.decode().strip() if stderr else ""

            if proc.returncode != 0:
                console.update(f"[red]Script error (exit {proc.returncode}):[/]\n{errors or output}")
            else:
                console.update(output if output else "No rotation needed (all files small and recent).")

        except FileNotFoundError:
            console.update("[red]Error:[/] logmini.sh not found. Make sure it's in the same directory.")

        self.refresh_data()


if __name__ == "__main__":
    app = LogminiUI()
    app.run()
