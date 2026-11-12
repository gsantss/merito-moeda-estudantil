from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.config import DATABASE_URL

class Base(DeclarativeBase):
    pass

E_SQLITE = DATABASE_URL.startswith('sqlite')

engine = create_engine(
    DATABASE_URL,
    connect_args={'check_same_thread': False, 'timeout': 30} if E_SQLITE else {},
    pool_pre_ping=True,
    # PostgreSQL na nuvem: renova conexões ociosas, que o provedor pode encerrar.
    **({} if E_SQLITE else {'pool_recycle': 300, 'pool_size': 5, 'max_overflow': 5}),
)
if E_SQLITE:
    @event.listens_for(engine, 'connect')
    def enable_foreign_keys(conn, _record):
        cur = conn.cursor()
        cur.execute('PRAGMA foreign_keys=ON')
        cur.execute('PRAGMA busy_timeout=30000')
        cur.close()

SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)

def get_db():
    with SessionLocal() as session:
        yield session
