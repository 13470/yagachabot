import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from sqlalchemy.future import select

from models import Session, User

BOT_TOKEN = ""


logging.basicConfig(level=logging.INFO)


class Gacha:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.bot = Bot(token=BOT_TOKEN)

    async def run(self) -> None:
        try:
            logging.info('Starting yagachabot')
            disp = Dispatcher(bot=self.bot)
            disp.register_message_handler(self.register_user, commands={'start', 'restart'})
            disp.register_callback_query_handler(self.profile_callback_handler, text='profile')
            disp.register_callback_query_handler(self.roll_callback_handler, text='roll')

            button_profile = types.InlineKeyboardButton('Профиль', callback_data='profile')
            button_roll = types.InlineKeyboardButton('Ролл (1$)', callback_data='roll')
            self.keyboard = types.InlineKeyboardMarkup()
            self.keyboard.add(button_profile)
            self.keyboard.add(button_roll)

            await disp.start_polling()
        finally:
            await self.bot.close()
            await self.session.close()

    async def register_user(self, message: types.Message) -> None:
        from_user = message.from_user
        stmt = select(User).where(User.id == from_user.id)
        result = await self.session.execute(stmt)
        user = result.scalars().first()
        logging.info(user)
        if not user:
            logging.info('Registering user id: %s, full_name: %s', from_user.id, from_user.full_name)
            user = User(id=from_user.id, balance=100)
            self.session.add(user)
            await self.session.commit()
        else:
            logging.info('User id: %s, full_name: %s already exists.', from_user.id, from_user.full_name)

        await self.bot.send_message(from_user.id, f'У тебя есть {user.balance}$', reply_markup=self.keyboard)

    async def profile_callback_handler(self, query: types.CallbackQuery) -> None:
        answer_data = query.data
        await query.answer(f'{answer_data!r}')

        from_user = query.from_user
        stmt = select(User).where(User.id == from_user.id)
        result = await self.session.execute(stmt)
        user: User = result.scalars().first()

        await self.bot.send_message(query.from_user.id, f'У тебя есть {user.balance}$', reply_markup=self.keyboard)

    async def roll_callback_handler(self, query: types.CallbackQuery) -> None:
        answer_data = query.data
        await query.answer(f'{answer_data!r}')

        from_user = query.from_user
        stmt = select(User).where(User.id == from_user.id)
        result = await self.session.execute(stmt)
        user: User = result.scalars().first()

        if user.balance > 0:
            user.balance -= 1
            self.session.add(user)
            await self.session.commit()
            if user.balance == 0:
                await self.bot.send_message(query.from_user.id, 'У тебя больше нет $. GAME OVER.')
            await self.bot.send_message(query.from_user.id, f'У тебя есть {user.balance}$', reply_markup=self.keyboard)
        else:
            await self.bot.send_message(query.from_user.id, 'У тебя больше нет $. GAME OVER.')


if __name__ == '__main__':
    session = Session()
    gacha = Gacha(session)
    asyncio.run(gacha.run())
