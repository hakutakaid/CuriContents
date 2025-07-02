from pyrogram import *
from pyrogram.types import *
from pyrogram.raw import *
import asyncio
import subprocess

async def extract_userid(message, text):
    def is_int(text):
        try:
            int(text)
        except ValueError:
            return False
        return True

    text = text.strip()

    if is_int(text):
        return int(text)

    entities = message.entities
    app = message._client
    
    if entities is not None and len(entities) > 0:
        entity = entities[1 if message.text.startswith("/") else 0]
        if entity.type == enums.MessageEntityType.MENTION:
            user = await app.get_users(text)
            if user is not None:
                return user.id
        elif entity.type == enums.MessageEntityType.TEXT_MENTION:
            return entity.user.id

    return None


async def extract_user_and_reason(message, sender_chat=False):
    args = message.text.strip().split()
    text = message.text
    user = None
    reason = None

    if message.reply_to_message:
        reply = message.reply_to_message
        if not reply.from_user and (reply.sender_chat and reply.sender_chat != message.chat.id and sender_chat):
            id_ = reply.sender_chat.id
        elif reply.from_user:
            id_ = reply.from_user.id
        else:
            return None, None

        reason = ' '.join(args[1:]) if len(args) > 1 else None
        return id_, reason

    if len(args) >= 2:
        user = ' '.join(args[1:])
        return await extract_userid(message, user), None

    return user, reason


async def extract_user(message):
    return (await extract_user_and_reason(message))[0]

async def bash(cmd):
    process = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    err = stderr.decode().strip()
    out = stdout.decode().strip()
    return out, err