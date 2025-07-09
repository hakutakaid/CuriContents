import os
import asyncio
import pyrogram
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, UserAlreadyParticipant, InviteHashExpired, UsernameNotOccupied
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from Config.config import API_ID, API_HASH, ERROR_MESSAGE
from database.db import db
from HakuX.Modules.strings import HELP_TXT
from HakuX.Modules.prem import check_vip_access

class batch_temp(object):
    IS_BATCH = {}
    # Cache untuk instance Pyrogram Client
    CLIENT_CACHE = {} 

async def get_acc_client(user_id, session_string, api_id, api_hash):
    """
    Mengambil atau membuat instance Pyrogram Client yang di-cache untuk user tertentu.
    """
    if user_id not in batch_temp.CLIENT_CACHE:
        try:
            acc = Client(f"saverestricted_{user_id}", session_string=session_string, api_hash=api_hash, api_id=api_id)
            await acc.connect()
            batch_temp.CLIENT_CACHE[user_id] = acc
        except Exception as e:
            # Tangani error koneksi, misalnya sesi kadaluarsa
            print(f"Error menghubungkan klien untuk user {user_id}: {e}")
            return None
    return batch_temp.CLIENT_CACHE[user_id]

async def downstatus(client, statusfile, message, chat):
    while True:
        if os.path.exists(statusfile):
            break

        await asyncio.sleep(3)  
            
    while os.path.exists(statusfile):  
        with open(statusfile, "r") as downread:  
            txt = downread.read()  
        try:  
            await client.edit_message_text(chat, message.id, f"**Downloaded:** **{txt}**")  
            await asyncio.sleep(10)  
        except:  
            await asyncio.sleep(5)

# upload status
async def upstatus(client, statusfile, message, chat):
    while True:
        if os.path.exists(statusfile):
            break

        await asyncio.sleep(3)        
    while os.path.exists(statusfile):  
        with open(statusfile, "r") as upread:  
            txt = upread.read()  
        try:  
            await client.edit_message_text(chat, message.id, f"**Uploaded:** **{txt}**")  
            await asyncio.sleep(10)  
        except:  
            await asyncio.sleep(5)

def progress(current, total, message, type):
    with open(f'{message.id}{type}status.txt', "w") as fileup:
        fileup.write(f"{current * 100 / total:.1f}%")

@Client.on_message(filters.command(["start"]))
async def send_start(client: Client, message: Message):
    if not await check_vip_access(client, message, db):
        return
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)

    buttons = [[  
        InlineKeyboardButton("❣️ Developer", url="https://t.me/kingvj01")  
    ], [  
        InlineKeyboardButton('🔍 sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ', url='https://t.me/vj_bot_disscussion'),  
        InlineKeyboardButton('🤖 ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ', url='https://t.me/vj_botz')  
    ]]  

    reply_markup = InlineKeyboardMarkup(buttons)  

    await client.send_message(  
        chat_id=message.chat.id,  
        text=f"<b>👋 Hi {message.from_user.mention}, I am Save Restricted Content Bot, I can send you restricted content by its post link.\n\nFor downloading restricted content /login first.\n\nKnow how to use bot by - /help</b>",  
        reply_markup=reply_markup,  
        reply_to_message_id=message.id  
    )

# help command
@Client.on_message(filters.command(["help"]))
async def send_help(client: Client, message: Message):
    if not await check_vip_access(client, message, db):
        return
    await client.send_message(
        chat_id=message.chat.id,
        text=f"{HELP_TXT}"
    )

# cancel command
@Client.on_message(filters.command(["cancel"]))
async def send_cancel(client: Client, message: Message):
    if not await check_vip_access(client, message, db):
        return
    batch_temp.IS_BATCH[message.from_user.id] = True
    await client.send_message(
        chat_id=message.chat.id,
        text="Batch Successfully Cancelled."
    )

@Client.on_message(filters.text & filters.private)
async def save(client: Client, message: Message):
    if not await check_vip_access(client, message, db):
        return
    if "https://t.me/" in message.text:
        if batch_temp.IS_BATCH.get(message.from_user.id) == False:
            return await message.reply_text("One Task Is Already Processing. Wait For Complete It. If You Want To Cancel This Task Then Use - /cancel")
        
        datas = message.text.split("/")
        temp = datas[-1].replace("?single","").split("-")
        fromID = int(temp[0].strip())
        try:
            toID = int(temp[1].strip())
        except:
            toID = fromID
        
        batch_temp.IS_BATCH[message.from_user.id] = False
        
        user_data = await db.get_session(message.from_user.id)
        if user_data is None:
            await message.reply("For Downloading Restricted Content You Have To /login First.")
            batch_temp.IS_BATCH[message.from_user.id] = True
            return

        # Dapatkan atau buat klien yang di-cache
        acc = await get_acc_client(message.from_user.id, user_data, API_ID, API_HASH)
        if acc is None:
            batch_temp.IS_BATCH[message.from_user.id] = True
            return await message.reply("Your Login Session Expired or failed to connect. Please /logout first, then login again by /login.")

        for msgid in range(fromID, toID+1):
            if batch_temp.IS_BATCH.get(message.from_user.id): break

            # private  
            if "https://t.me/c/" in message.text:  
                chatid = int("-100" + datas[4])  
                try:  
                    await handle_private(client, acc, message, chatid, msgid)  
                except Exception as e:  
                    if ERROR_MESSAGE == True:  
                        await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)  
      
            # bot  
            elif "https://t.me/b/" in message.text:  
                username = datas[4]  
                try:  
                    await handle_private(client, acc, message, username, msgid)  
                except Exception as e:  
                    if ERROR_MESSAGE == True:  
                        await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)  
              
            # public  
            else:  
                username = datas[3]  

                try:  
                    msg = await client.get_messages(username, msgid)  
                except UsernameNotOccupied:   
                    await client.send_message(message.chat.id, "The username is not occupied by anyone", reply_to_message_id=message.id)  
                    continue  # Lanjut ke pesan berikutnya dalam batch
                except Exception as e:
                    if ERROR_MESSAGE == True:
                        await client.send_message(message.chat.id, f"Error fetching public message: {e}", reply_to_message_id=message.id)
                    continue

                try:  
                    await client.copy_message(message.chat.id, msg.chat.id, msg.id, reply_to_message_id=message.id)  
                except:  
                    try:      
                        await handle_private(client, acc, message, username, msgid)                 
                    except Exception as e:  
                        if ERROR_MESSAGE == True:  
                            await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)  

            # waktu tunggu  
            await asyncio.sleep(3)  
        batch_temp.IS_BATCH[message.from_user.id] = True

# handle private
async def handle_private(client: Client, acc, message: Message, chatid: int, msgid: int):
    if not await check_vip_access(client, message, db):
        return
    
    try:
        msg: Message = await acc.get_messages(chatid, msgid)
    except Exception as e:
        if ERROR_MESSAGE == True:
            await client.send_message(message.chat.id, f"Error fetching message from restricted chat: {e}", reply_to_message_id=message.id)
        return

    if msg.empty: return
    
    msg_type = get_message_type(msg)
    if not msg_type: return
    
    chat = -1002676263803
    if batch_temp.IS_BATCH.get(message.from_user.id): return
    
    if "Text" == msg_type:
        try:
            await client.send_message(chat, msg.text, entities=msg.entities, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
            return
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
            return

    smsg = await client.send_message(message.chat.id, '**Downloading**', reply_to_message_id=message.id)  
    asyncio.create_task(downstatus(client, f'{message.id}downstatus.txt', smsg, chat))  
    
    try:  
        file = await acc.download_media(msg, progress=progress, progress_args=[message,"down"])  
        os.remove(f'{message.id}downstatus.txt')  
    except Exception as e:  
        if ERROR_MESSAGE == True:  
            await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)   
        return await smsg.delete()  
    
    if batch_temp.IS_BATCH.get(message.from_user.id):
        if os.path.exists(file):
            os.remove(file)
        return await smsg.delete()

    asyncio.create_task(upstatus(client, f'{message.id}upstatus.txt', smsg, chat))  

    if msg.caption:  
        caption = msg.caption  
    else:  
        caption = None  
    if batch_temp.IS_BATCH.get(message.from_user.id):
        if os.path.exists(file):
            os.remove(file)
        return await smsg.delete()
              
    if "Document" == msg_type:  
        ph_path = None
        try:  
            if msg.document and msg.document.thumbs:
                ph_path = await acc.download_media(msg.document.thumbs[0].file_id)  
        except:  
            pass  
          
        try:  
            await client.send_document(chat, file, thumb=ph_path, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message,"up"])  
        except Exception as e:  
            if ERROR_MESSAGE == True:  
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)  
        if ph_path and os.path.exists(ph_path): os.remove(ph_path)  
          
    elif "Video" == msg_type:  
        ph_path = None
        try:  
            if msg.video and msg.video.thumbs:
                ph_path = await acc.download_media(msg.video.thumbs[0].file_id)  
        except:  
            pass  
          
        try:  
            await client.send_video(chat, file, duration=msg.video.duration, width=msg.video.width, height=msg.video.height, thumb=ph_path, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message,"up"])  
        except Exception as e:  
            if ERROR_MESSAGE == True:  
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)  
        if ph_path and os.path.exists(ph_path): os.remove(ph_path)  

    elif "Animation" == msg_type:  
        try:  
            await client.send_animation(chat, file, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)  
        except Exception as e:  
            if ERROR_MESSAGE == True:  
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)  
          
    elif "Sticker" == msg_type:  
        try:  
            await client.send_sticker(chat, file, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)  
        except Exception as e:  
            if ERROR_MESSAGE == True:  
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)       

    elif "Voice" == msg_type:  
        try:  
            await client.send_voice(chat, file, caption=caption, caption_entities=msg.caption_entities, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message,"up"])  
        except Exception as e:  
            if ERROR_MESSAGE == True:  
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)  

    elif "Audio" == msg_type:  
        ph_path = None
        try:  
            if msg.audio and msg.audio.thumbs:
                ph_path = await acc.download_media(msg.audio.thumbs[0].file_id)  
        except:  
            pass  

        try:  
            await client.send_audio(chat, file, thumb=ph_path, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message,"up"])     
        except Exception as e:  
            if ERROR_MESSAGE == True:  
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)  
          
        if ph_path and os.path.exists(ph_path): os.remove(ph_path)  

    elif "Photo" == msg_type:  
        try:  
            await client.send_photo(chat, file, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)  
        except Exception as e: 
            if ERROR_MESSAGE == True:  
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)  
      
    if os.path.exists(f'{message.id}upstatus.txt'):   
        os.remove(f'{message.id}upstatus.txt')  
    if os.path.exists(file): 
        os.remove(file)  
    await client.delete_messages(message.chat.id,[smsg.id])

def get_message_type(msg: pyrogram.types.messages_and_media.message.Message):
    if msg.document: return "Document"
    if msg.video: return "Video"  
    if msg.animation: return "Animation"  
    if msg.sticker: return "Sticker"  
    if msg.voice: return "Voice"  
    if msg.audio: return "Audio"  
    if msg.photo: return "Photo"  
    if msg.text: return "Text"  
    return None