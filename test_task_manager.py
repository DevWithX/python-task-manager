import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from task_manager import main


class TaskManagerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.db = Path(self.temp.name) / 'tasks.sqlite3'

    def run_cli(self, *args):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            main(['--db', str(self.db), *args])
        return output.getvalue()

    def test_persistent_lifecycle(self):
        self.assertIn('Added task 1', self.run_cli('add', 'Ship portfolio'))
        self.assertIn('[ ] Ship portfolio', self.run_cli('list'))
        self.run_cli('done', '1')
        self.assertEqual('No open tasks.\n', self.run_cli('list'))
        self.assertIn('[x] Ship portfolio', self.run_cli('list', '--all'))
        self.run_cli('reopen', '1')
        self.assertIn('[ ] Ship portfolio', self.run_cli('list'))
        self.run_cli('delete', '1')
        self.assertEqual('No tasks.\n', self.run_cli('list', '--all'))

    def test_titles_are_data(self):
        title = "Read SQL'); DROP TABLE tasks; --"
        self.run_cli('add', title)
        self.assertIn(title, self.run_cli('list'))
        self.run_cli('add', 'Second task')
        self.assertIn('Second task', self.run_cli('list'))

    def test_invalid_title_is_rejected(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
            self.run_cli('add', '   ')
        self.assertEqual(2, error.exception.code)
        self.assertFalse(self.db.exists())

    def test_missing_task_is_reported(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
            self.run_cli('done', '42')
        self.assertEqual(2, error.exception.code)


if __name__ == '__main__':
    unittest.main()
