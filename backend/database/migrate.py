import os
import sys
import subprocess
from pathlib import Path
from typing import Optional, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_alembic_command(command: str, *args: str) -> int:
    """Run an Alembic command with the given arguments."""
    cmd = ["alembic"] + command.split() + list(args)
    print(f"Running: {' '.join(cmd)}")
    return subprocess.call(cmd, cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def create_migration(message: str) -> None:
    """Create a new migration."""
    if not message:
        print("Error: Please provide a message for the migration")
        return
    run_alembic_command("revision --autogenerate -m", f'"{message}"')

def upgrade_db(revision: str = "head") -> None:
    """Upgrade the database to the specified revision."""
    run_alembic_command(f"upgrade {revision}")

def downgrade_db(revision: str) -> None:
    """Downgrade the database to the specified revision."""
    run_alembic_command(f"downgrade {revision}")

def show_migrations() -> None:
    """Show the current migration status."""
    run_alembic_command("current")
    run_alembic_command("history")

def init_migrations() -> None:
    """Initialize the migrations directory."""
    migrations_dir = Path(__file__).parent / "migrations"
    if not migrations_dir.exists():
        migrations_dir.mkdir(parents=True, exist_ok=True)
    
    # Create a basic alembic.ini if it doesn't exist
    alembic_ini = Path("alembic.ini")
    if not alembic_ini.exists():
        print("Creating default alembic.ini...")
        alembic_ini.write_text(
            "[alembic]\n"
            "script_location = backend/database/migrations\n"
            "sqlalchemy.url = postgresql://postgres.lflecyuvttemfoyixngi:Ayeshaayesha12@@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres\n"
        )
    
    print("Migrations directory initialized.")

def main() -> None:
    """Main entry point for the migration script."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Database migration utility")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Create migration command
    create_parser = subparsers.add_parser("create", help="Create a new migration")
    create_parser.add_argument("message", help="Migration message")
    
    # Upgrade command
    upgrade_parser = subparsers.add_parser("upgrade", help="Upgrade database")
    upgrade_parser.add_argument("--revision", default="head", help="Target revision")
    
    # Downgrade command
    downgrade_parser = subparsers.add_parser("downgrade", help="Downgrade database")
    downgrade_parser.add_argument("revision", help="Target revision")
    
    # Show migrations command
    subparsers.add_parser("show", help="Show migration status")
    
    # Init command
    subparsers.add_parser("init", help="Initialize migrations directory")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == "create":
        create_migration(args.message)
    elif args.command == "upgrade":
        upgrade_db(args.revision)
    elif args.command == "downgrade":
        downgrade_db(args.revision)
    elif args.command == "show":
        show_migrations()
    elif args.command == "init":
        init_migrations()
    else:
        print(f"Unknown command: {args.command}")
        parser.print_help()

if __name__ == "__main__":
    main()
