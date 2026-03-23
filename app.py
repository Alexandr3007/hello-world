import os
import logging
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.types import Update

API_TOKEN = os.getenv("BOT_TOKEN")
if not API_TOKEN:
    raise ValueError("BOT_TOKEN не задан в переменных окружения")

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- Логика модерации (без изменений, но проверьте ID тем) ---
@dp.message()
async def moderator_logic(message: types.Message):
    if message.from_user is None or message.from_user.is_bot:
        return
    tid = message.message_thread_id
    text = message.text.lower() if message.text else ""
    print(f">>> Сообщение от {message.from_user.full_name} в теме ID: {tid}")
    print(f">>> Сообщение в теме ID: {tid} | Текст: {text[:20]}...")
    
    # ВОДИТЕЛИ
    if tid in [32320, 28845]:
        if any(bad_word in text for bad_word in ['ищу', 'нужно', 'пассажир', 'надо']):
            await message.delete()
            print(f"[-] Удален пассажир из темы Водителей: {text[:20]}")
        elif not any(word in text for word in ['еду','водитель', 'выезжаю', 'возьму', 'выезд', 'мест', 'маршрут', '-', '—']):
            await message.delete()
            print(f"[-] Удалено (не по шаблону) из Водителей")
    
    # ПАССАЖИРЫ
    if tid in [32324, 28846]:
        if not any(word in text for word in ['ищу', 'пассажир', 'нужно', 'едет', 'надо', 'кто', 'едет', 'подвезет']):
            try:
                await message.delete()
                print(f"[-] УДАЛЕНО из Пассажиров: {text}")
            except Exception as e:
                print(f"Ошибка удаления: {e}")
    
    # ПЕРЕДАЧИ
    elif tid == 10:
        if not any(word in text for word in ['передать', 'сумку', 'пакет', 'передачу']):
            await message.delete()
            print(f"[-] Удалено из Передач")
    
    # ПОМОЩЬ (замените ID на актуальный)
    elif tid == 1139:
        if not any(word in text for word in ['помогите', 'сломался', 'трос', 'запаска']):
            await message.delete()
            print(f"[-] Удалено из Помощи")

# --- Обработчик вебхука ---
async def webhook_handler(request):
    json_data = await request.json()
    update = Update(**json_data)
    await dp.feed_update(bot, update)
    return web.Response(text="OK")

async def set_webhook():
    # Получаем публичный URL сервиса на Render
    public_url = os.getenv("RENDER_EXTERNAL_URL")
    if not public_url:
        logging.error("RENDER_EXTERNAL_URL не задан. Проверьте, что это веб-сервис на Render.")
        return
    webhook_url = f"{public_url}/webhook"
    await bot.set_webhook(webhook_url, drop_pending_updates=True)
    logging.info(f"Вебхук установлен: {webhook_url}")

async def on_shutdown(app):
    logging.info("Остановка, удаляем вебхук...")
    await bot.delete_webhook()
    await bot.session.close()

async def main():
    # Устанавливаем вебхук
    await set_webhook()
    
    # Создаём веб-приложение
    app = web.Application()
    app.router.add_post("/webhook", webhook_handler)
    app.router.add_get("/", lambda request: web.Response(text="Bot is running"))
    app.on_shutdown.append(on_shutdown)
    
    # Порт для Render: используем переменную PORT (по умолчанию 10000)
    port = int(os.getenv("PORT", 10000))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    
    logging.info(f"Сервер запущен на порту {port}")
    # Бесконечно ждём (сервер работает)
    await asyncio.Event().wait()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Бот остановлен")
