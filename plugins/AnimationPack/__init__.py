from loads import func, Description, MainDescription, FuncDescription
from pyrogram import filters, types
from random import choices
from pyrogram.errors import FloodWait
import asyncio

__description__ = Description(
    MainDescription('Плагин анимаций'),
    FuncDescription('spinsq', 'анимация прокрутки коробки', prefixes=['!', '/', '.'])
)

@func(filters.command('spinsq', ['!', '/', '.']))
async def magic_ball(_, msg: types.Message):
    await spin_box(msg)

async def spin_box(msg: types.Message, spin_count: int=10):
    emojis_in_case = ["⬜", "🟦", "🟧", "🟪", "🟨", "🟥", "⬛", "💟"]

    emoji_rare = {
   f"{emojis_in_case[0]}": f"{emojis_in_case[0]} - common",
   f"{emojis_in_case[1]}": f"{emojis_in_case[1]} - uncommon",
   f"{emojis_in_case[2]}": f"{emojis_in_case[2]} - rare",
   f"{emojis_in_case[3]}": f"{emojis_in_case[3]} - epic",
   f"{emojis_in_case[4]}": f"{emojis_in_case[4]} - legendary",
   f"{emojis_in_case[5]}": f"{emojis_in_case[5]} - expensive",
   f"{emojis_in_case[6]}": f"{emojis_in_case[6]} - negr",
   f"{emojis_in_case[7]}": f"{emojis_in_case[7]} - incredible"
    }

    list_emojis = [choices(emojis_in_case)[0] for i in range(42)]

    anim = f"""
{''.join(list_emojis[0:12])}
{list_emojis[41]}⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜{list_emojis[12]}
{list_emojis[40]}⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜{list_emojis[13]}
{list_emojis[39]}⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜{list_emojis[14]}
{list_emojis[38]}⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜{list_emojis[15]}
{list_emojis[37]}⬜⬜⬜⬜🔮⬜⬜⬜⬜⬜{list_emojis[16]}
{list_emojis[36]}⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜{list_emojis[17]}
{list_emojis[35]}⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜{list_emojis[18]}
{list_emojis[34]}⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜{list_emojis[19]}
{list_emojis[33]}⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜{list_emojis[20]}
{''.join(list_emojis[21:33][::-1])}
"""

    await msg.edit(anim+'⬜⬜⬜⬜⬜3️⃣⬜⬜⬜⬜⬜⬜')
    await asyncio.sleep(0.3)
    await msg.edit(anim+'⬜⬜⬜⬜⬜2️⃣⬜⬜⬜⬜⬜⬜')
    await asyncio.sleep(0.3)
    await msg.edit(anim+'⬜⬜⬜⬜⬜1️⃣⬜⬜⬜⬜⬜⬜')
    await asyncio.sleep(0.3)
    await msg.edit(anim+'⬜⬜⬜⬜⬜🔼⬜⬜⬜⬜⬜⬜')
    
    for i in range(spin_count):
        try:
            list_emojis = [list_emojis[-1]] + list_emojis[:-1]
            
            anim = f"""
{''.join(list_emojis[0:12])}
{list_emojis[41]}⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜{list_emojis[12]}
{list_emojis[40]}⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜{list_emojis[13]}
{list_emojis[39]}⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜{list_emojis[14]}
{list_emojis[38]}⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜{list_emojis[15]}
{list_emojis[37]}⬜⬜⬜⬜🔮⬜⬜⬜⬜⬜{list_emojis[16]}
{list_emojis[36]}⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜{list_emojis[17]}
{list_emojis[35]}⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜{list_emojis[18]}
{list_emojis[34]}⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜{list_emojis[19]}
{list_emojis[33]}⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜{list_emojis[20]}
{''.join(list_emojis[21:33][::-1])}
"""
            
            await msg.edit(anim+'⬜⬜⬜⬜⬜🔼⬜⬜⬜⬜⬜⬜')
            await asyncio.sleep(0.5)
        except FloodWait as e:
            await asyncio.sleep(e.value)
    
    if msg.reply_to_message:
        try:
            frsname = msg.reply_to_message.from_user.first_name
        except:
            frsname = msg.from_user.first_name
        await msg.edit(anim+f'⬜⬜⬜⬜⬜🔼⬜⬜⬜⬜⬜⬜\n{frsname} выпало: {emoji_rare[list_emojis[27]]}')
    else:
        await msg.edit(anim+f'⬜⬜⬜⬜⬜🔼⬜⬜⬜⬜⬜⬜\n{msg.from_user.first_name} выпало: {emoji_rare[list_emojis[27]]}')