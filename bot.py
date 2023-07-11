import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import sqlite3

# Устанавливаем уровень логов
logging.basicConfig(level=logging.INFO)

# Создаем объекты бота, диспетчера и хранилища состояний
bot = Bot(token='TOKEN')
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Создаем подключение к базе данных
conn = sqlite3.connect('messages.db')
cursor = conn.cursor()

# Создаем таблицу для хранения сообщений, если она не существует
cursor.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        chat_id INTEGER,
        message_text TEXT
    )
''')
conn.commit()

# Обработчик всех входящих сообщений
@dp.message_handler()
async def save_message(message: types.Message):
    # Получаем информацию о сообщении
    user_id = message.from_user.id
    chat_id = message.chat.id
    message_text = message.text
    
    # Добавляем сообщение в базу данных
    cursor.execute('''
        INSERT INTO messages (user_id, chat_id, message_text)
        VALUES (?, ?, ?)
    ''', (user_id, chat_id, message_text))
    conn.commit()

    # Получаем случайное сообщение из базы данных
    cursor.execute('SELECT message_text FROM messages ORDER BY RANDOM() LIMIT 1')
    result = cursor.fetchone()
    
    if result:
        random_phrase = result[0]
        await message.answer(random_phrase)
    else:
        await message.answer('Нет сохраненных сообщений')

# Запускаем бота
if __name__ == '__main__':
    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(dp.start_polling())
