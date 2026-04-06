#!/usr/bin/env python3
"""
Sigil CLI — Every answer has an address.

Commands:
  sigil init              Initialize config in current directory
  sigil index <file>      Index a document
  sigil query <address>   Query the index
  sigil list              List all addresses
  sigil serve             Start MCP + REST servers
  sigil skill-cards       Show document Skill Cards
  sigil conflicts         Show pending conflict flags
  sigil stats             Show index statistics
"""

import sys
import os
import json

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.config import load_config
from core.llm import LLMProvider
from core.indexer import SigilIndexer
from core.router import SigilRouter
from storage.db import SigilStorage

console = Console()


# ── Shared setup ──────────────────────────────────────────────────────────────

def _setup(config_path: str):
    cfg     = load_config(config_path)
    storage = SigilStorage(cfg["storage"]["path"])
    llm     = LLMProvider(cfg["llm"])
    indexer = SigilIndexer(llm, storage)
    router  = SigilRouter(storage)
    return cfg, storage, llm, indexer, router


# ── CLI ───────────────────────────────────────────────────────────────────────

@click.group()
@click.version_option("1.0.0", prog_name="sigil")
def cli():
    """
    \b
    ╔═══════════════════════════════╗
    ║   S  I  G  I  L   v1.0.0     ║
    ║   Every answer has an address ║
    ╚═══════════════════════════════╝

    Symbolic knowledge indexing for LLM systems.
    """


# ── init ──────────────────────────────────────────────────────────────────────

@cli.command()
@click.option("--config", "-c", default="sigil.config.yaml")
def init(config):
    """Initialize Sigil in the current directory."""
    from pathlib import Path
    import shutil

    cfg_path = Path(config)
    if cfg_path.exists():
        console.print(f"[yellow]Config already exists:[/yellow] {config}")
        return

    template = Path(__file__).parent / "sigil.config.yaml"
    if template.exists():
        shutil.copy(template, cfg_path)
    else:
        cfg_path.write_text(
            "llm:\n  provider: anthropic\n  model: claude-sonnet-4-6\n"
            "  api_key: ${ANTHROPIC_API_KEY}\n\nstorage:\n  path: ./sigil.db\n"
            "\ninterface:\n  mcp:\n    enabled: true\n    port: 3000\n"
            "  rest_api:\n    enabled: true\n    port: 3001\n"
        )

    console.print(f"[green]✓[/green] Created [bold]{config}[/bold]")
    console.print()
    console.print("Next steps:")
    console.print("  1. Set your API key:       [cyan]export ANTHROPIC_API_KEY=sk-ant-...[/cyan]")
    console.print("  2. Index a document:       [cyan]sigil index ./document.pdf[/cyan]")
    console.print("  3. Query the index:        [cyan]sigil query 'your.address.here.what'[/cyan]")
    console.print("  4. Start servers:          [cyan]sigil serve[/cyan]")
    console.print()
    console.print("[dim]For other LLMs (OpenAI, Ollama) edit the config file.[/dim]")


# ── index ─────────────────────────────────────────────────────────────────────

@cli.command()
@click.argument("filepath", type=click.Path(exists=True))
@click.option("--title", "-t", default="", help="Document title")
@click.option("--config", "-c", default="sigil.config.yaml")
def index(filepath, title, config):
    """Index a document into the Sigil knowledge base."""
    console.print(f"\n[bold cyan]Sigil[/bold cyan]  Indexing: [yellow]{filepath}[/yellow]\n")

    try:
        _, _, _, indexer, _ = _setup(config)
        with console.status("[green]Calling LLM to generate symbolic address index..."):
            result = indexer.index_file(filepath, title=title or None)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise click.Abort()

    console.print(f"[green]✓[/green] Indexed: [bold]{result['title']}[/bold]")
    console.print(f"  Doc ID : {result['doc_id']}")
    console.print(f"  Domain : {result['domain']}")
    console.print(f"  Nodes  : {result['nodes_indexed']} symbolic addresses")

    sk = result["skill_card"]
    console.print(f"\n[bold]Skill Card[/bold]")
    console.print(f"  Purpose : {sk.get('purpose', '-')}")
    for s in sk.get("strengths", []):
        console.print(f"  [green]✓[/green] {s}")
    for w in sk.get("weaknesses", []):
        console.print(f"  [yellow]✗[/yellow] {w}")

    audit = result.get("audit", {})
    if audit.get("uncovered_concepts"):
        console.print(f"\n[yellow]Audit — uncovered concepts:[/yellow]")
        for c in audit["uncovered_concepts"]:
            console.print(f"  • {c}")
    if audit.get("ambiguity_warnings"):
        console.print(f"\n[yellow]Audit — ambiguity warnings:[/yellow]")
        for w in audit["ambiguity_warnings"]:
            console.print(f"  • {w}")

    console.print(f"\n[dim]Run 'sigil list' to see all generated addresses.[/dim]\n")


# ── query ─────────────────────────────────────────────────────────────────────

@cli.command()
@click.argument("address")
@click.option("--config", "-c", default="sigil.config.yaml")
@click.option("--json", "as_json", is_flag=True, help="Raw JSON output")
def query(address, config, as_json):
    """Query the index by address, prefix, or natural language."""
    _, _, _, _, router = _setup(config)
    result = router.query(address)

    if as_json:
        click.echo(json.dumps(result, ensure_ascii=False, indent=2))
        return

    tier_label = {1: "Exact match", 2: "Prefix match", 3: "Fuzzy search"}
    tier  = result.get("tier", 3)
    count = result.get("count", 0)

    console.print(
        f"\n[bold cyan]Sigil Query[/bold cyan]  "
        f"Tier {tier} · {tier_label[tier]} · {count} result(s)\n"
    )

    if count == 0:
        console.print("[yellow]No results found.[/yellow]")
        console.print("[dim]Try: sigil list   to browse available addresses.[/dim]\n")
        return

    for node in result.get("results", []):
        console.print(Panel(
            f"[bold]{node['address']}[/bold]\n"
            f"[dim]Location :[/dim] {node.get('structural_location', '-')}  "
            f"anchor: \"{node.get('anchor_phrase', '-')}\"\n"
            f"[dim]Source   :[/dim] {node.get('doc_title', '-')}  "
            f"[dim]({node.get('doc_id', '-')})[/dim]\n\n"
            f"{node.get('content', '-')}",
            border_style="cyan",
        ))

    if result.get("note"):
        console.print(f"[dim]{result['note']}[/dim]\n")


# ── list ──────────────────────────────────────────────────────────────────────

@cli.command("list")
@click.option("--prefix", "-p", default="", help="Filter by address prefix")
@click.option("--config", "-c", default="sigil.config.yaml")
def list_addresses(prefix, config):
    """List all symbolic addresses in the index."""
    _, _, _, _, router = _setup(config)
    result = router.list_addresses(prefix=prefix)

    label = f"prefix: {prefix}" if prefix else "all"
    console.print(
        f"\n[bold cyan]Sigil Index[/bold cyan]  "
        f"{result['count']} addresses ({label})\n"
    )
    for addr in result["addresses"]:
        parts  = addr.split(".")
        domain = parts[0]
        rest   = ".".join(parts[1:])
        console.print(f"  [cyan]{domain}[/cyan].[dim]{rest}[/dim]")
    console.print()


# ── skill-cards ───────────────────────────────────────────────────────────────

@cli.command("skill-cards")
@click.option("--config", "-c", default="sigil.config.yaml")
def skill_cards(config):
    """Show Skill Cards for all indexed documents."""
    _, _, _, _, router = _setup(config)
    result = router.get_skill_cards()

    console.print(
        f"\n[bold cyan]Sigil Skill Cards[/bold cyan]  {result['count']} documents\n"
    )
    for item in result["skill_cards"]:
        sk = item.get("skill_card", {})
        console.print(Panel(
            f"[bold]{item.get('title','Untitled')}[/bold]  "
            f"[dim]{item.get('doc_id','')}[/dim]\n\n"
            f"[dim]Purpose   :[/dim] {sk.get('purpose','-')}\n"
            f"[dim]Strengths :[/dim] {' | '.join(sk.get('strengths',[]))}\n"
            f"[dim]Weaknesses:[/dim] {' | '.join(sk.get('weaknesses',[]))}",
            border_style="green",
        ))


# ── conflicts ─────────────────────────────────────────────────────────────────

@cli.command()
@click.option("--config", "-c", default="sigil.config.yaml")
def conflicts(config):
    """Show pending conflict flags requiring human review."""
    _, _, _, _, router = _setup(config)
    result = router.get_conflicts()

    if result["count"] == 0:
        console.print("\n[green]No conflicts pending.[/green]\n")
        return

    console.print(
        f"\n[bold yellow]Conflicts[/bold yellow]  {result['count']} pending review\n"
    )
    for c in result["conflicts"]:
        console.print(Panel(
            f"[bold yellow]⚠  {c['address']}[/bold yellow]\n\n"
            f"[dim]Doc A:[/dim] {c['doc_id_a']}\n{c['content_a']}\n\n"
            f"[dim]Doc B:[/dim] {c['doc_id_b']}\n{c['content_b']}",
            border_style="yellow",
        ))


# ── stats ─────────────────────────────────────────────────────────────────────

@cli.command()
@click.option("--config", "-c", default="sigil.config.yaml")
def stats(config):
    """Show index statistics."""
    _, _, _, _, router = _setup(config)
    s = router.get_stats()

    console.print(f"\n[bold cyan]Sigil Stats[/bold cyan]\n")
    console.print(f"  Documents        {s['total_documents']}")
    console.print(f"  Knowledge nodes  {s['total_nodes']}")
    console.print(f"  Pending conflicts {s['pending_conflicts']}")
    console.print(f"  Domains          {', '.join(s['domains']) or 'none'}")
    console.print(f"  Database         {s['db_path']}")
    console.print()


# ── serve ─────────────────────────────────────────────────────────────────────

@cli.command()
@click.option("--config", "-c", default="sigil.config.yaml")
@click.option("--mcp-port",  default=3000, show_default=True)
@click.option("--api-port",  default=3001, show_default=True)
@click.option("--mcp-only",  is_flag=True)
@click.option("--api-only",  is_flag=True)
def serve(config, mcp_port, api_port, mcp_only, api_only):
    """Start MCP and/or REST API servers."""
    import threading
    import uvicorn

    cfg, storage, llm, indexer, router = _setup(config)

    console.print("\n[bold cyan]Sigil Servers[/bold cyan]\n")

    threads = []

    if not api_only:
        from mcp.server import create_mcp_app
        app = create_mcp_app(router)
        console.print(f"[green]✓[/green] MCP server   http://localhost:{mcp_port}")
        console.print(f"  Tools:        http://localhost:{mcp_port}/tools")
        t = threading.Thread(
            target=uvicorn.run,
            args=(app,),
            kwargs={"host": "0.0.0.0", "port": mcp_port, "log_level": "warning"},
            daemon=True,
        )
        threads.append(t)

    if not mcp_only:
        from api.rest import create_api_app
        app = create_api_app(router, indexer)
        console.print(f"[green]✓[/green] REST API     http://localhost:{api_port}")
        console.print(f"  Docs:         http://localhost:{api_port}/docs")
        t = threading.Thread(
            target=uvicorn.run,
            args=(app,),
            kwargs={"host": "0.0.0.0", "port": api_port, "log_level": "warning"},
            daemon=True,
        )
        threads.append(t)

    console.print(f"\n[dim]Ctrl+C to stop.[/dim]\n")

    for t in threads:
        t.start()

    try:
        for t in threads:
            t.join()
    except KeyboardInterrupt:
        console.print("\n[yellow]Stopped.[/yellow]\n")


if __name__ == "__main__":
    cli()
