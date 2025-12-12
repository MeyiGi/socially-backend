import oracledb
from app.core.config import settings

def get_db_connection():
    return oracledb.connect(
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        dsn=settings.DB_DSN
    )