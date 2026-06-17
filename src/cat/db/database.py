import os
os.environ["PICCOLO_CONF"] = "cat.db.database"

from piccolo.engine.postgres import PostgresEngine
from piccolo.engine.sqlite import SQLiteEngine

from cat.env import get_env

DB_URL = get_env("CCAT_SQL")

if DB_URL.startswith("sqlite"):
    # sqlite:///data/core/core.db
    dialect, path = DB_URL.split(":///")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    db_path = os.path.abspath(path)
    DB_URL = f"{dialect}:///{db_path}"
    DB = SQLiteEngine(path=db_path)
elif DB_URL.startswith("postgresql"):
    # postgresql://user:pass@localhost:5432/dbname
    DB = PostgresEngine(connection_string=DB_URL)
    # DB.startup()
else:
    raise ValueError(f"Unsupported DB URL: {DB_URL}")
