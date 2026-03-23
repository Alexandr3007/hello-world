from aiohttp import web  # Добавь этот импорт в самый верх файла!
import asyncio
import logging
from aiogram import Bot, Dispatcher, types

# 1. ТВОЙ ТОКЕН (Вставь его сюда)
API_TOKEN = '8612980599:AAHBegAQJ6VXLso-s-dUW5GJ8Wi8__9NFgo'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

@dp.message()
async def moderator_logic(message: types.Message):
    # 1. ПРОПУСКАЕМ: сообщения от самого бота, от имени каналов/групп и сервисные сообщения
    if message.from_user is None or message.from_user.is_bot:
        return

    # 2. ОПРЕДЕЛЯЕМ ID ТЕМЫ И ТЕКСТ
    tid = message.message_thread_id
    text = message.text.lower() if message.text else ""
    
    # Твой основной код фильтрации ниже...
    print(f">>> Сообщение от {message.from_user.full_name} в теме ID: {tid}")
    
    # Дальше идут твои проверки (if tid == 1142 и т.д.)

    
    
    # ЭТА СТРОЧКА ПОКАЖЕТ ID В ТЕРМИНАЛЕ (Смотри туда!)
    print(f">>> Сообщение в теме ID: {tid} | Текст: {text[:20]}...")

    # --- ЗДЕСЬ НАСТРОЙКИ ФИЛЬТРОВ ---

   # 1. ТЕМА: ВОДИТЕЛИ (ID: 1142)
    if tid in [32320, 28845]: 
        # Если человек пишет "ищу" или "нужно" в водителях — УДАЛЯЕМ (это пассажир)
        if any(bad_word in text for bad_word in ['ищу', 'нужно', 'пассажир', 'надо']):
            await message.delete()
            print(f"[-] Удален пассажир из темы Водителей: {text[:20]}")
        
        # В остальном проверяем обычные слова водителя
        elif not any(word in text for word in ['еду','водитель', 'выезжаю', 'возьму', 'выезд', 'мест', 'маршрут', '-', '—']):
            await message.delete()
            print(f"[-] Удалено (не по шаблону) из Водителей")

        # 2. ТЕМА: ПАССАЖИРЫ (ID: 1143)
    if tid in [32324, 28846]: 
        # Если в тексте НЕТ ни одного из этих слов — УДАЛЯЕМ
        if not any(word in text for word in ['ищу', 'пассажир', 'нужно', 'едет', 'надо', 'кто', 'едет', 'подвезет']):
            try:
                await message.delete()
                print(f"[-] УДАЛЕНО из Пассажиров: {text}")
            except Exception as e:
                print(f"Ошибка удаления: {e}")

    # 3. ТЕМА: ПЕРЕДАЧИ (Замени 6 на свое число из терминала)
    elif tid == 1139:
        if not any(word in text for word in ['передать', 'сумку', 'пакет', 'передачу']):
            await message.delete()
            print(f"[-] Удалено из Передач")

    # 4. ТЕМА: ПОМОЩЬ (Замени 10 на свое число из терминала)
    elif tid == 10:
        if not any(word in text for word in ['помогите', 'сломался', 'трос', 'запаска']):
            await message.delete()
            print(f"[-] Удалено из Помощи")


async def handle(request):
    return web.Response(text="Бот работает 24/7!")

async def main():
    # 1. Запускаем фоновый веб-сервер
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    # Порт 7860 обязателен для Hugging Face
    site = web.TCPSite(runner, "0.0.0.0", 7860)
    await site.start()
    
    print(">>> Бот запущен и веб-сервер активен!")
    
    # 2. Запускаем самого бота
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Бот остановлен")