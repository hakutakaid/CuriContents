from pyrogram import *
from pyrogram.types import *
from database.db import db
from HakuX.Modules.tools import extract_user
from Config.config import ADMINS

async def check_vip_access(client: Client, message: Message, db):
    user = message.from_user
    vip_users = await db.get_list_from_vars(client.me.id, "Vip_User")
    if user.id not in vip_users:
        await message.reply("Kamu Tidak Mempunyai Akses !")
        return False
    return True

@Client.on_message(filters.command("prem") & filters.user(ADMINS))
async def prem_user(client: Client, message: Message):
    msg = await message.reply("<b>sᴇᴅᴀɴɢ ᴍᴇᴍᴘʀᴏsᴇs...</b>")
    user_id = await extract_user(message)
    if not user_id:
        return await msg.edit(
            f"<b>{message.text} ᴜsᴇʀ_ɪᴅ/ᴜsᴇʀɴᴀᴍᴇ</b>"
        )

    try:
        user = await client.get_users(user_id)
    except Exception as error:
        return await msg.edit(f"<b>Error:</b> {error}")

    sudo_users = await db.get_list_from_vars(client.me.id, "Vip_User")

    if user.id in sudo_users:
        return await msg.edit(f"""
<b>💬 INFORMATION</b>
<b>ɴᴀᴍᴇ:</b> [{user.first_name} {user.last_name or ''}](tg://user?id={user.id})
<b>ɪᴅ:</b> <code>{user.id}</code>
<b>ᴋᴇᴛᴇʀᴀɴɢᴀɴ:</b> <code>sudah vip</code>
""")

    try:
        await db.add_to_vars(client.me.id, "Vip_User", user.id)
        return await msg.edit(f"""
<b>💬 INFORMATION</b>
<b>ɴᴀᴍᴇ:</b> [{user.first_name} {user.last_name or ''}](tg://user?id={user.id})
<b>ɪᴅ:</b> <code>{user.id}</code>
<b>ᴋᴇᴛᴇʀᴀɴɢᴀɴ:</b> <code>vip</code>
""")
    except Exception as error:
        return await msg.edit(f"<b>Error:</b> {error}")

@Client.on_message(filters.command("unprem") & filters.user(ADMINS))
async def unprem_user(client: Client, message: Message):
    msg = await message.reply("<b>ᴍᴇᴍᴘʀᴏsᴇs ᴘᴇɴɢʜᴀᴘᴜsᴀɴ...</b>")
    user_id = await extract_user(message)
    if not user_id:
        return await msg.edit(f"<b>{message.text} ᴜsᴇʀ_ɪᴅ/ᴜsᴇʀɴᴀᴍᴇ</b>")

    try:
        user = await client.get_users(user_id)
        await db.remove_from_vars(client.me.id, "Vip_User", user.id)
        return await msg.edit(f"<b>{user.first_name} telah dihapus dari VIP.</b>")
    except Exception as e:
        return await msg.edit(f"<b>Error:</b> {e}")