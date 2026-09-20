from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
import os

raw_db_url = os.getenv("DATABASE_URL")
if not raw_db_url:
    DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "metrolens.db")
    DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"
else:
    # Convert standard Postgres URIs (postgres:// or postgresql://) to asyncpg
    if raw_db_url.startswith("postgres://"):
        DATABASE_URL = raw_db_url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif raw_db_url.startswith("postgresql://"):
        DATABASE_URL = raw_db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    else:
        DATABASE_URL = raw_db_url

engine = create_async_engine(DATABASE_URL, echo=False)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

async def get_db():
    async with async_session_maker() as session:
        yield session
