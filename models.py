from sqlalchemy import Column, Integer
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()
engine = create_async_engine('sqlite+aiosqlite:///db.sqlite', echo=True)
Session = sessionmaker(bind=engine, future=True, class_=AsyncSession, expire_on_commit=False)


class User(Base):  # type: ignore
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    balance = Column(Integer, nullable=False)
