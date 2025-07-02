from pyrogram import Client
from Config.config import API_ID, API_HASH, BOT_TOKEN
from database.db import db
import logging
from pyromod import listen

logging.basicConfig(level=logging.INFO)

class Bot(Client):
    def __init__(self):
        super().__init__(
            name="techvj login",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            plugins=dict(root="HakuX"),
            workers=50,
            sleep_threshold=10
        )

    async def start(self, *args, **kwargs):
        await db.init()
        await super().start(*args, **kwargs)
        me = await self.get_me()
        logging.info(f"🤖 Bot @{me.username} Started | ID: {me.id}")

    async def stop(self, *args):
        await super().stop(*args)
        logging.info("🚫 Bot Stopped. Bye!")

def main():
    Bot().run()  # Fungsi ini dipanggil dari entry point 'hakurun'

if __name__ == "__main__":
    main()