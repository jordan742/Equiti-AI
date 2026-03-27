"""
Memo Formatter — Rich terminal output for Investment Memos.
Uses the `rich` library for styled console display.
"""

from __future__ import annotations

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich import box

from scanner.alpha_scanner import DealAnalysis

console = Console()


def print_deal_analysis(analysis: DealAnalysis) -> None:
    """Render a DealAnalysis to the terminal with rich formatting."""

    # ── Header ─────────────────────────────────────────────────────────────
    tier_colors = {"Strong": "green", "Moderate": "yellow", "Weak": "red", "Insufficient Data": "dim"}
    color = tier_colors.get(analysis.alpha_score.signal_tier, "white")

    console.print(
        Panel(
            f"[bold]{analysis.company_name}[/bold]\n"
            f"Alpha Score: [{color}]{analysis.alpha_score.composite_score}/100 "
            f"({analysis.alpha_score.signal_tier})[/{color}]",
            title="[bold blue]Equiti-AI Alpha Scanner[/bold blue]",
            subtitle="[dim]Safe Mode Active — Data Only[/dim]",
            box=box.DOUBLE_EDGE,
        )
    )

    # ── Score Breakdown Table ──────────────────────────────────────────────
    table = Table(title="Signal Breakdown", box=box.SIMPLE_HEAD, show_header=True)
    table.add_column("Signal", style="bold")
    table.add_column("Score", justify="right")
    table.add_column("Weight", justify="right", style="dim")

    table.add_row("GitHub Momentum", f"{analysis.alpha_score.github_score}/100", "25%")
    table.add_row("Hiring Velocity", f"{analysis.alpha_score.hiring_score}/100", "20%")
    table.add_row("Deal Quality",    f"{analysis.alpha_score.deal_score}/100",    "20%")
    table.add_row("DCF Upside",      f"{analysis.alpha_score.dcf_score}/100",     "35%")
    table.add_row(
        "[bold]Composite[/bold]",
        f"[bold]{analysis.alpha_score.composite_score}/100[/bold]",
        "100%",
    )
    console.print(table)

    # ── Data Gaps ─────────────────────────────────────────────────────────
    if analysis.alpha_score.missing_data_flags:
        console.print("\n[yellow]Data Gaps:[/yellow]")
        for flag in analysis.alpha_score.missing_data_flags:
            console.print(f"  [dim]• {flag}[/dim]")

    # ── Investment Memo ────────────────────────────────────────────────────
    console.print("\n")
    console.print(Markdown(analysis.investment_memo))


def print_feed_summary(analyses: list[DealAnalysis]) -> None:
    """Print a summary table for a batch of Reg CF deals."""
    table = Table(
        title=f"Reg CF Deal Feed — Top {len(analyses)} by Alpha Score",
        box=box.ROUNDED,
        show_header=True,
    )
    table.add_column("#", justify="right", style="dim", width=3)
    table.add_column("Company", style="bold", min_width=25)
    table.add_column("Alpha", justify="right")
    table.add_column("Tier")
    table.add_column("Filed", style="dim")

    tier_colors = {"Strong": "green", "Moderate": "yellow", "Weak": "red", "Insufficient Data": "dim"}

    for i, a in enumerate(analyses, 1):
        color = tier_colors.get(a.alpha_score.signal_tier, "white")
        filed = a.regcf_deal.filing_date if a.regcf_deal else "—"
        table.add_row(
            str(i),
            a.company_name,
            f"[{color}]{a.alpha_score.composite_score}[/{color}]",
            f"[{color}]{a.alpha_score.signal_tier}[/{color}]",
            filed,
        )

    console.print(table)
