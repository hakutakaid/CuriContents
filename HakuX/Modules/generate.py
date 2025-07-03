import traceback
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import (
    ApiIdInvalid,
    PhoneNumberInvalid,
    PhoneCodeInvalid,
    PhoneCodeExpired,
    SessionPasswordNeeded,
    PasswordHashInvalid
)
from asyncio.exceptions import TimeoutError
from Config.config import API_ID, API_HASH
from database.db import db
from HakuX.Modules.prem import check_vip_access


SESSION_STRING_SIZE = 351

@Client.on_message(filters.private & ~filters.forwarded & filters.command(["logout"]))
async def logout(client, message):
    if not await check_vip_access(client, message, db):
        return
    user_data = await db.get_session(message.from_user.id)
    if user_data is None:
        return await message.reply("**You're not logged in.**")
    
    await db.set_session(message.from_user.id, session=None)
    await message.reply("**Logout Successfully** ♦")

@Client.on_message(filters.private & ~filters.forwarded & filters.command(["login"]))
async def main(bot: Client, message: Message):
    if not await check_vip_access(bot, message, db):
        return
    user_id = int(message.from_user.id)
    user_data = await db.get_session(user_id)
    
    if user_data is not None:
        await message.reply("**You are already logged in. Use /logout first, then /login again.**")
        return

    try:
        phone_number_msg = await bot.ask(
            chat_id=user_id,
            text="<b>Please send your phone number including country code</b>\nExample: <code>+1234567890</code>",
            filters=filters.text,
            timeout=300
        )
    except TimeoutError:
        return await message.reply("<b>Timeout. Please try /login again.</b>")

    if phone_number_msg.text.lower() == '/cancel':
        return await phone_number_msg.reply('<b>Process cancelled!</b>')

    phone_number = phone_number_msg.text.strip()
    client = Client(":memory:", API_ID, API_HASH)

    await client.connect()
    await phone_number_msg.reply("Sending OTP...")

    try:
        code = await client.send_code(phone_number)
        phone_code_msg = await bot.ask(
            user_id,
            "**Check Telegram for OTP.**\nIf OTP is `12345`, send it as `1 2 3 4 5`.\n\nEnter /cancel to cancel.",
            filters=filters.text,
            timeout=600
        )
    except PhoneNumberInvalid:
        return await phone_number_msg.reply('`PHONE_NUMBER` **is invalid.**')
    except Exception as e:
        return await phone_number_msg.reply(f"**Failed to send code:** `{e}`")

    if phone_code_msg.text.lower() == '/cancel':
        return await phone_code_msg.reply('<b>Process cancelled!</b>')

    try:
        phone_code = phone_code_msg.text.replace(" ", "")
        await client.sign_in(phone_number, code.phone_code_hash, phone_code)
    except PhoneCodeInvalid:
        return await phone_code_msg.reply('**OTP is invalid.**')
    except PhoneCodeExpired:
        return await phone_code_msg.reply('**OTP is expired.**')
    except SessionPasswordNeeded:
        try:
            two_step_msg = await bot.ask(
                user_id,
                "**Two-step verification is enabled. Please enter your password.**\n\nEnter /cancel to cancel.",
                filters=filters.text,
                timeout=300
            )
        except TimeoutError:
            return await message.reply("<b>Timeout. Please try again.</b>")

        if two_step_msg.text.lower() == '/cancel':
            return await two_step_msg.reply('<b>Process cancelled!</b>')

        try:
            await client.check_password(password=two_step_msg.text)
        except PasswordHashInvalid:
            return await two_step_msg.reply('**Invalid Password Provided**')

    string_session = await client.export_session_string()
    await client.disconnect()

    if len(string_session) < SESSION_STRING_SIZE:
        return await message.reply('<b>Invalid session string. Please try again.</b>')

    try:
        user_name = message.from_user.first_name or "Unknown"
        await db.add_user(user_id, user_name)
        await db.set_session(user_id, session=string_session)
    except Exception as e:
        return await message.reply_text(f"<b>ERROR IN LOGIN:</b> `{e}`")

    await bot.send_message(
        message.from_user.id,
        "<b>Account Login Successfully ✅\n\nIf you encounter AUTH_KEY errors, please /logout and then /login again.</b>"
    )