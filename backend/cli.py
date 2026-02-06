"""
Yakiniku CLI — Database & Server Management

Usage:
    cd backend
    python cli.py --help              # Show all commands
    python cli.py db init             # Create tables (migrate to head)
    python cli.py db seed             # Seed sample data from CSV
    python cli.py db reset            # Drop all + recreate + seed
    python cli.py db migrate MESSAGE  # Generate new migration
    python cli.py db upgrade          # Apply pending migrations
    python cli.py db current          # Show current revision
    python cli.py server              # Start uvicorn dev server
"""
import typer
import asyncio
from rich.console import Console
from rich.table import Table as RichTable
from rich.panel import Panel

app = typer.Typer(
    name="yakiniku",
    help="🍖 Yakiniku Restaurant Platform CLI",
    no_args_is_help=True,
    rich_markup_mode="rich",
)
db_app = typer.Typer(help="🗄️  Database management commands")
app.add_typer(db_app, name="db")

console = Console()


# ──────────────────────────────────────────────
# Database commands
# ──────────────────────────────────────────────

@db_app.command()
def init():
    """Create all tables using Alembic migrations (upgrade to head)."""
    from alembic.config import Config
    from alembic import command

    console.print("\n🗄️  [bold]Initializing database...[/bold]\n")
    cfg = Config("alembic.ini")
    command.upgrade(cfg, "head")
    console.print("✅ [green]Database initialized (migrated to head)[/green]\n")


@db_app.command()
def migrate(message: str = typer.Argument(..., help="Migration description")):
    """Generate a new Alembic migration from model changes."""
    from alembic.config import Config
    from alembic import command

    console.print(f"\n📝 [bold]Generating migration:[/bold] {message}\n")
    cfg = Config("alembic.ini")
    command.revision(cfg, message=message, autogenerate=True)
    console.print("✅ [green]Migration generated in alembic/versions/[/green]\n")


@db_app.command()
def upgrade(revision: str = typer.Argument("head", help="Target revision (default: head)")):
    """Apply pending migrations."""
    from alembic.config import Config
    from alembic import command

    console.print(f"\n⬆️  [bold]Upgrading to:[/bold] {revision}\n")
    cfg = Config("alembic.ini")
    command.upgrade(cfg, revision)
    console.print("✅ [green]Upgrade complete[/green]\n")


@db_app.command()
def downgrade(revision: str = typer.Argument("-1", help="Target revision (default: -1)")):
    """Rollback migrations."""
    from alembic.config import Config
    from alembic import command

    console.print(f"\n⬇️  [bold]Downgrading to:[/bold] {revision}\n")
    cfg = Config("alembic.ini")
    command.downgrade(cfg, revision)
    console.print("✅ [green]Downgrade complete[/green]\n")


@db_app.command()
def current():
    """Show current database revision."""
    from alembic.config import Config
    from alembic import command

    cfg = Config("alembic.ini")
    console.print("\n📋 [bold]Current revision:[/bold]")
    command.current(cfg, verbose=True)
    console.print()


@db_app.command()
def history():
    """Show migration history."""
    from alembic.config import Config
    from alembic import command

    cfg = Config("alembic.ini")
    console.print("\n📜 [bold]Migration history:[/bold]")
    command.history(cfg, verbose=True)
    console.print()


@db_app.command()
def seed(
    drop: bool = typer.Option(False, "--drop", help="Drop all tables before seeding"),
):
    """Seed database with sample data from CSV files."""

    async def _seed():
        from data.seed_data import seed_all
        await seed_all(drop_existing=drop)

    console.print("\n🌱 [bold]Seeding database...[/bold]\n")
    asyncio.run(_seed())


@db_app.command()
def reset():
    """Drop all tables, recreate via migration, and seed data."""

    async def _reset():
        from app.database import engine, Base

        # Import all models
        from app.models import (
            Branch, GlobalCustomer, BranchCustomer, CustomerPreference,
            Booking, ChatMessage, ChatInsight,
            Table, TableAssignment, TableAvailability,
            MenuItem, Item, ItemCategory, ItemOptionGroup, ItemOption, ItemOptionAssignment,
            Combo, ComboItem, Promotion, PromotionUsage,
            Order, OrderItem, TableSession, Staff,
        )
        from app.domains.tableorder.events import OrderEvent
        from app.domains.checkin.models import WaitingList, CheckInLog

        # Drop everything
        console.print("🗑️  Dropping all tables...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

        # Recreate via Alembic
        from alembic.config import Config
        from alembic import command
        cfg = Config("alembic.ini")
        command.upgrade(cfg, "head")
        console.print("✅ Tables recreated via migration")

        # Seed
        from data.seed_data import seed_all
        await seed_all(drop_existing=False)

    console.print(Panel("⚠️  [bold red]This will DELETE ALL DATA[/bold red]", title="Database Reset"))
    confirm = typer.confirm("Are you sure?")
    if not confirm:
        console.print("❌ Cancelled")
        raise typer.Abort()

    asyncio.run(_reset())
    console.print("\n🎉 [bold green]Database reset complete![/bold green]\n")


@db_app.command()
def stamp(revision: str = typer.Argument("head", help="Revision to stamp")):
    """Stamp the database with a revision without running migrations.
    Use this when the database was created with create_all() and you want to
    adopt Alembic for future migrations."""
    from alembic.config import Config
    from alembic import command

    console.print(f"\n🔖 [bold]Stamping revision:[/bold] {revision}\n")
    cfg = Config("alembic.ini")
    command.stamp(cfg, revision)
    console.print("✅ [green]Stamped — Alembic will track future changes[/green]\n")


# ──────────────────────────────────────────────
# Server command
# ──────────────────────────────────────────────

@app.command()
def server(
    host: str = typer.Option("0.0.0.0", help="Bind host"),
    port: int = typer.Option(8000, help="Bind port"),
    reload: bool = typer.Option(True, help="Auto-reload on changes"),
):
    """Start the uvicorn development server."""
    import uvicorn

    console.print(Panel(
        f"[bold]🍖 Yakiniku API Server[/bold]\n"
        f"   Host: {host}:{port}\n"
        f"   Reload: {'✅' if reload else '❌'}\n"
        f"   Docs: http://localhost:{port}/docs",
        title="Starting Server",
    ))
    uvicorn.run("app.main:app", host=host, port=port, reload=reload)


# ──────────────────────────────────────────────
# Info command
# ──────────────────────────────────────────────

@app.command()
def info():
    """Show project configuration info."""
    from app.config import settings

    table = RichTable(title="🍖 Yakiniku Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Database URL", settings.DATABASE_URL)
    table.add_row("Default Branch", settings.DEFAULT_BRANCH)
    table.add_row("CORS Origins", str(len(settings.CORS_ORIGINS)) + " origins")
    table.add_row("OpenAI Model", settings.OPENAI_MODEL)
    table.add_row("OpenAI Key", "✅ Set" if settings.OPENAI_API_KEY else "❌ Not set")

    console.print()
    console.print(table)
    console.print()


if __name__ == "__main__":
    app()
