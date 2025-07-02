# broadcast.py

from pyrogram.errors import (
    InputUserDeactivated, UserNotParticipant, FloodWait,
    UserIsBlocked, PeerIdInvalid
)
from pyrogram import Client, filters
from Config.config import ADMINS
from database.db import db

import asyncio
import datetime
import time


class BroadcastManager:
    def __init__(self, db_instance):
        self.db = db_instance

    async def _send_message(self, user_id, message):
        try:
            await message.copy(chat_id=user_id)
            return True, "Success"
        except FloodWait as e:
            await asyncio.sleep(e.value)
            return await self._send_message(user_id, message)
        except InputUserDeactivated:
            await self.db.delete_user(user_id)
            return False, "Deleted"
        except UserIsBlocked:
            await self.db.delete_user(user_id)
            return False, "Blocked"
        except PeerIdInvalid:
            await self.db.delete_user(user_id)
            return False, "Error"
        except Exception:
            return False, "Error"

    async def run_broadcast(self, message, b_msg):
        users = self.db.get_all_users()
        total_users = await self.db.total_users_count()

        start_time = time.time()
        success = blocked = deleted = failed = done = 0

        async for user in users:
            user_id = user.get("id")
            if user_id is None:
                failed += 1
                done += 1
                continue

            sent, reason = await self._send_message(user_id, b_msg)
            if sent:
                success += 1
            else:
                if reason == "Blocked":
                    blocked += 1
                elif reason == "Deleted":
                    deleted += 1
                else:
                    failed += 1
            done += 1

            if done % 20 == 0:
                await message.edit_text(
                    f"Broadcast in progress:\n\n"
                    f"Total Users: {total_users}\n"
                    f"Completed: {done} / {total_users}\n"
                    f"Success: {success}\nBlocked: {blocked}\nDeleted: {deleted}"
                )

        time_taken = datetime.timedelta(seconds=int(time.time() - start_time))
        await message.edit_text(
            f"Broadcast Completed in {time_taken}.\n\n"
            f"Total Users: {total_users}\n"
            f"Completed: {done} / {total_users}\n"
            f"Success: {success}\nBlocked: {blocked}\nDeleted: {deleted}\nFailed: {failed}"
        )


broadcast_manager = BroadcastManager(db)


@Client.on_message(filters.command("broadcast") & filters.user(ADMINS) & filters.reply)
async def broadcast_handler(bot, message):
    b_msg = message.reply_to_message
    if not b_msg:
        return await message.reply_text("**Reply This Command To Your Broadcast Message**")

    status = await message.reply_text("Broadcasting your message...")
    await broadcast_manager.run_broadcast(status, b_msg)