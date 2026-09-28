"""A small, persistent task manager using Python's standard library."""
import argparse
import sqlite3
from contextlib import closing
from pathlib import Path


def main(argv=None):
    parser = argparse.ArgumentParser(description="Manage a local task list.")
    parser.add_argument("--db", type=Path, default=Path("tasks.sqlite3"), help="SQLite file (default: ./tasks.sqlite3)")
    commands = parser.add_subparsers(dest="command", required=True)
    add = commands.add_parser("add", help="Add a task")
    add.add_argument("title")
    listing = commands.add_parser("list", help="List tasks")
    listing.add_argument("--all", action="store_true", help="Include completed tasks")
    for name in ("done", "reopen", "delete"):
        command = commands.add_parser(name)
        command.add_argument("id", type=int)
    args = parser.parse_args(argv)
    if args.command == "add" and (not args.title.strip() or len(args.title.strip()) > 500):
        parser.error("title must contain between 1 and 500 characters")
    try:
        with closing(sqlite3.connect(args.db)) as database, database:
            database.execute("CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, done INTEGER NOT NULL DEFAULT 0 CHECK(done IN (0, 1)))")
            if args.command == "add":
                cursor = database.execute("INSERT INTO tasks (title) VALUES (?)", (args.title.strip(),))
                print(f"Added task {cursor.lastrowid}: {args.title.strip()}")
            elif args.command == "list":
                rows = database.execute("SELECT id, title, done FROM tasks WHERE done = 0 OR ? ORDER BY id", (args.all,)).fetchall()
                if not rows:
                    print("No tasks." if args.all else "No open tasks.")
                for task_id, title, done in rows:
                    print(f"{task_id:>3} [{'x' if done else ' '}] {title}")
            else:
                if args.command == "delete":
                    cursor = database.execute("DELETE FROM tasks WHERE id = ?", (args.id,))
                else:
                    cursor = database.execute("UPDATE tasks SET done = ? WHERE id = ?", (args.command == "done", args.id))
                if not cursor.rowcount:
                    parser.error(f"task {args.id} does not exist")
                print(f"Task {args.id}: {args.command}")
    except sqlite3.Error as error:
        parser.exit(1, f"Database error: {error}\n")


if __name__ == "__main__":
    main()
