import os, sqlite3
from pathlib import Path
DB_PATH = os.environ.get('MESA_DB', str(Path(__file__).resolve().parent / 'mesa_ayuda.db'))
def conectar():
    con = sqlite3.connect(DB_PATH, timeout=15)
    con.row_factory = sqlite3.Row
    con.execute('PRAGMA foreign_keys=ON')
    return con
