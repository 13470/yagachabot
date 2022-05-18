import unittest
from unittest import IsolatedAsyncioTestCase
from unittest.mock import MagicMock

import alembic.command
import alembic.config
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker

from main import Gacha
from models import User


class TestRegisterUser(IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        test_db_path = 'sqlite+aiosqlite:///test_db.sqlite'

        engine = create_async_engine(test_db_path, echo=True, future=True)
        Session = sessionmaker(bind=engine, future=True, class_=AsyncSession)
        self.session = Session()

        config = alembic.config.Config()
        config.set_main_option('script_location', 'migrations')
        config.set_main_option('sqlalchemy.url', test_db_path)
        alembic.command.upgrade(config, 'head')

        return super().setUp()

    async def test_register_user(self) -> None:
        message = MagicMock(from_user=MagicMock(id=1))
        gacha = Gacha(session=self.session)

        result = await gacha.register_user(message=message)
        result = await self.session.execute(select(User).where(User.id == 1))
        user: User = result.scalars().first()

        assert user is not None
        assert user.id == 1
        assert user.balance == 100
        await self.session.close()

    async def asyncTearDown(self) -> None:
        await self.session.close()
        return await super().asyncTearDown()


unittest.main()
