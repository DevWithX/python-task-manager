# Python Task Manager

A small command-line learning project with persistent SQLite storage. It uses only
the Python standard library and keeps its scope deliberately focused.

Requires Python 3.10 or newer. Run from this directory:

```sh
python3 task_manager.py add "Finish the portfolio case study"
python3 task_manager.py list
python3 task_manager.py done 1
python3 task_manager.py list --all
python3 task_manager.py reopen 1
python3 task_manager.py delete 1
```

Tasks are stored in `tasks.sqlite3` in the working directory. Select another file
with `python3 task_manager.py --db /path/to/tasks.sqlite3 list`. The parent directory
must exist. Deletion is permanent; copy the database first if you need a backup.

The implementation uses parameterized SQL, transactions, bounded non-empty titles,
clear missing-task errors, and a connection that is closed after every command.
There is no account system, cloud sync or web interface.

Run `python3 -m unittest -v` to check persistence, the complete task lifecycle,
input validation and SQL-like text handling.
