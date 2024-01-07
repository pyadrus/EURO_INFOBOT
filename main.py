import asyncio
import logging
import re
import sys
import configparser
from aiogram import Bot, Dispatcher
from aiogram import F
from aiogram import types
from aiogram.filters import ChatMemberUpdatedFilter, IS_NOT_MEMBER, IS_MEMBER
from aiogram.types import ChatMemberUpdated
from loguru import logger  # https://github.com/Delgan/loguru

dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

phone_number_pattern = re.compile(r'(\+?\d{1,3}[-\s]?\d{3,4}[-\s]?\d{2,4}[-\s]?\d{2,4})')

allowed_user_ids = [53518551]

logger.add("log/log.log")


@dp.chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
async def on_user_join(event: ChatMemberUpdated):
    """
    Пользователь вступил в группу
    IS_NOT_MEMBER >> IS_MEMBER - новый участник
    IS_MEMBER >> IS_NOT_MEMBER - покинул группу участник группы
    """
    logger.info(f'Пользователь: Имя - {event.new_chat_member.user.first_name} {event.new_chat_member.user.last_name} '
                f'username - {event.new_chat_member.user.username} id - {event.new_chat_member.user.id} '
                f'вступил в группу.')


@dp.message(F.new_chat_members)
async def new_chat_member(message: types.Message):
    """
    Пользователь вступил в группу
    ContentType = new_chat_members (https://docs.aiogram.dev/en/v3.1.1/api/enums/content_type.html)
    """
    await message.delete()  # Удаляем системное сообщение о новом участнике группы


@dp.message(F.left_chat_member)
async def left_chat_member(message: types.Message):
    """
    Пользователь покинул группу
    ContentType = left_chat_member (https://docs.aiogram.dev/en/v3.1.1/api/enums/content_type.html)
    """
    await message.delete()  # Удаляем системное сообщение о покидании группы


@dp.message(F.text)
async def any_message(message: types.Message):
    """
    Проверка сообщения на наличие номера телефона, если нет, то удаляем сообщение и предупреждаем пользователя.
    Если есть номер телефона, то проверяем на наличие ссылок, если есть ссылка, то удаляем сообщение и предупреждаем
    пользователя.
    """
    logger.info(f'Проверяем сообщение {message.text} от {message.from_user.username} {message.from_user.id}')
    user_id = message.from_user.id  # Получаем ID пользователя
    if user_id in allowed_user_ids:  # Проверка на наличие пользователя в списке разрешенных
        logger.info(f'Админ {user_id} написал сообщение {message.text}')
    else:
        if not phone_number_pattern.search(message.text):  # Проверка на наличие номера телефона
            logger.info(f'Сообщение от:({message.from_user.username} {message.from_user.id}). '
                        f'Текст сообщения {message.text}')
            warning = await message.answer(f'Пожалуйста, укажите номер телефона в вашем сообщении.')
            await message.delete()  # Удаляем сообщение без номера телефона
            logger.info(f'Сообщения {message.text} от ({message.from_user.username} {message.from_user.id}), удалено')
            logger.info(f'Удаление системного сообщения от бота через 10 сек.')
            await asyncio.sleep(int(10))  # Спим 20 секунд
            await warning.delete()  # Удаляем предупреждение от бота
            logger.info(f'Системное сообщения от бота удалено')
        try:
            for entity in message.entities:  # Проверка на наличие ссылок
                logger.info(f'Тип ссылки: {entity.type}')
                if entity.type in ["url", "text_link"]:
                    warning_url = await message.answer(f'Запрещена публикация сообщений с ссылками')
                    logger.info(f'Сообщение от:({message.from_user.username} {message.from_user.id}). '
                                f'Текст сообщения {message.text}')
                    await message.delete()  # Удаляем сообщение содержащее ссылку
                    logger.info(f'Сообщения {message.text} от ({message.from_user.username} {message.from_user.id}), '
                                f'удалено')
                    logger.info(f'Удаление системного сообщения от бота через 10 сек.')
                    await asyncio.sleep(int(10))  # Спим 20 секунд
                    await warning_url.delete()  # Удаляем предупреждение от бота
                    logger.info(f'Системное сообщения от бота удалено')
        except Exception as e:
            logger.info(f'Возникла ошибка {e}, так как в сообщении {message.text} от {message.from_user.username} '
                        f'{message.from_user.id} нет ссылки')


@dp.edited_message(F.text)
async def edit_message(message: types.Message):
    """
    Проверка изменяемых сообщений на наличие номера телефона, если нет, то удаляем сообщение и предупреждаем
    пользователя.
    Проверяем на наличие ссылок, если есть ссылка, то удаляем сообщение и предупреждаем пользователя.
    """
    logger.info(f'Измененное сообщение пользователем: {message.from_user.id}, текст измененного '
                f'сообщения: {message.text}')
    user_id = message.from_user.id  # Получаем ID пользователя
    if user_id in allowed_user_ids:  # Проверка на наличие пользователя в списке разрешенных
        logger.info(f'Админ {user_id} изменил сообщение {message.text}')
    else:
        if not phone_number_pattern.search(message.text):  # Проверка на наличие номера телефона
            logger.info(f'Измененное сообщение от:({message.from_user.username} {message.from_user.id}). '
                        f'Текст сообщения {message.text}')
            warning = await message.answer(f'Пожалуйста, укажите номер телефона в вашем сообщении.')
            await message.delete()  # Удаляем сообщение без номера телефона
            logger.info(f'Сообщения {message.text} от ({message.from_user.username} {message.from_user.id}), удалено')
            logger.info(f'Удаление системного сообщения от бота через 10 сек.')
            await asyncio.sleep(int(10))  # Спим 20 секунд
            await warning.delete()  # Удаляем предупреждение от бота
            logger.info(f'Системное сообщения от бота удалено')
        try:
            for entity in message.entities:  # Проверка на наличие ссылок
                logger.info(f'Тип ссылки: {entity.type}')
                if entity.type in ["url", "text_link"]:
                    warning_url = await message.answer(f'Запрещена публикация сообщений с ссылками')
                    logger.info(f'Сообщение от:({message.from_user.username} {message.from_user.id}). '
                                f'Текст сообщения {message.text}')
                    await message.delete()  # Удаляем сообщение содержащее ссылку
                    logger.info(f'Сообщения {message.text} от ({message.from_user.username} {message.from_user.id}), '
                                f'удалено')
                    logger.info(f'Удаление системного сообщения от бота через 10 сек.')
                    await asyncio.sleep(int(10))  # Спим 20 секунд
                    await warning_url.delete()  # Удаляем предупреждение от бота
                    logger.info(f'Системное сообщения от бота удалено')
        except Exception as e:
            logger.info(f'Возникла ошибка {e}, так как в сообщении {message.text} от {message.from_user.username} '
                        f'{message.from_user.id} нет ссылки')


async def main() -> None:
    """
    Запуск бота
    """
    config = configparser.ConfigParser(empty_lines_in_values=False, allow_no_value=True)
    config.read("setting/config.ini")  # Чтение файла
    bot_token = config.get('BOT_TOKEN', 'BOT_TOKEN')  # Получение токена
    bot = Bot(token=bot_token)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
