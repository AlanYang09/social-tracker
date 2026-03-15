import asyncio
import logging
import os
from dotenv import load_dotenv
from telegram import Bot
from telegram.ext import Application, CommandHandler
from handlers.commands import start, top, sentiment, status
from handlers.alerts import check_and_send_alerts

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
ALERT_INTERVAL = 300  # check every 5 minutes


async def alert_loop(bot: Bot):
    while True:
        await check_and_send_alerts(bot, CHAT_ID)
        await asyncio.sleep(ALERT_INTERVAL)


async def main():
    if not BOT_TOKEN:
        logger.warning("TELEGRAM_BOT_TOKEN not set — notifier idle (set it in .env to enable)")
        while True:
            await asyncio.sleep(3600)
        return

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("top", top))
    app.add_handler(CommandHandler("sentiment", sentiment))
    app.add_handler(CommandHandler("status", status))

    bot = Bot(BOT_TOKEN)
    asyncio.create_task(alert_loop(bot))

    logger.info("Telegram bot starting...")
    await app.run_polling()


if __name__ == "__main__":
    asyncio.run(main())
