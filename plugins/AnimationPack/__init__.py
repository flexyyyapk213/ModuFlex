from loads import func, Description, MainDescription, FuncDescription
from pyrogram import filters, types
import random
from pyrogram.errors import FloodWait, MessageNotModified
import asyncio
import re

__description__ = Description(
    MainDescription('Плагин анимаций'),
    FuncDescription('spinsq', 'Анимация прокрутки коробки', prefixes=['!', '/', '.']),
    FuncDescription('p', 'Анимация шкалы потужності'),
    FuncDescription('laught', 'Показывает насколько это смехуятина.'),
    FuncDescription('clown', 'Воспроизводит анимацию, которая адресуется тем, кто позер и прочее'),
    FuncDescription('ocase', 'Анимация прокрутки "кейса" в чате', parameters=('необязательно(кол-во прокрутки)',)),
    FuncDescription('ex', 'Показывает текст "Правда" или "Ложь"'),
    FuncDescription('dc', 'Выводит случайно "Чист" или "Заражён"'),
    FuncDescription('ghoul', 'Показывает таблицу где отнимают 7 от 1000'),
    FuncDescription('proc', 'Анимация загрузки в чате.Текст писать в двойных кавычках', parameters=('"загрузка"', '"результат"')),
    FuncDescription('love', 'Выводит анимацию с сердечками'),
    FuncDescription('t', 'Анимация печатания в чате', parameters=('текст',)),
    FuncDescription('hacker', parameters=('текст',))
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

    list_emojis = [random.choices(emojis_in_case)[0] for i in range(42)]

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

@func(filters.command('p', ['!', '/', '.']) & filters.me)
async def riven_potuzhnosti(_, message: types.Message):
    level = "Вимірюється..."
    level_text = "Очікування..."
    MAX_LEVEL = 47
    level_bar = '...............................................'

    level_name = {
        "Рівень потужності дойшов до спокійного рівня": 6,
        "Рівень потужності дойшов до коливального рівня": 12,
        "❗️Рівень потужності дойшов до тривожного рівня": 18,
        "‼️Рівень потужності дойшов до серйозного рівня": 24,
        "‼️❗️Рівень потужності дойшов до ВИСОКОГО рівня": 28,
        "‼️‼️Рівень потужності дойшов до НЕЙМОВІРНО ВИСОКОГО рівня": 36,
        "⚠️⚠️‼️‼️РІЕНЬ ПОТУЖНОСТІ ДОЙШОВ ДО ПОЛУСМЕРТНОГО РІВНЯ": 42,
        "📢⚠️⚠️‼️‼️РІВЕНЬ ПОТУЖНОСТІ ДОЙШОВ ДО СМЕРТЕЛЬНОГО РІВНЯ": 47
    }

    text = f"""Рівень потужності: {level}
🟦🟩🟨🟧🟥🟪⬛️💀
{level_bar}
{level_text}
"""

    await message.edit_text(text)

    await asyncio.sleep(2)

    level = 0

    for i in range(random.randint(5, 15)):
        add_level = random.randint(-2, 8)
        level += add_level
        level = max(0, min(level, MAX_LEVEL))

        level_bar = '.' * (level - 1) + '🔺' + '.' * (MAX_LEVEL - level)

        text = f"""Рівень потужності: {level}
🟦🟩🟨🟧🟥🟪⬛️💀
{level_bar}
{level_text}
"""

        try:
            await message.edit_text(text)
        except Exception as e:
            pass

        await asyncio.sleep(1)
    
    for key, value in level_name.items():
        if level <= value:
            level_text = key
            break
    
    text = f"""Рівень потужності: {level}
🟦🟩🟨🟧🟥🟪⬛️💀
{level_bar}
{level_text}
"""
    try:
        await message.edit_text(text)
    except Exception as e:
        pass

@func(filters.command('laught', ['.', '!', '/']) & filters.me)
async def laughter(_, msg: types.Message):
    laughts = [
        '    Как смишно🤣    ',
        '    Чел, у тебя явно чувство юмора😂    ',
        '    Разрывная😂    ',
        '    Я чуть со стула не упал!🤣    ',
        '    Это гениально!😹    ',
        '    Смешнее не бывает!😆    ',
        '    Угар!🔥    ',
        '    Ну ты даёшь!😜    ',
        '    Я так не смеялся давно!😂    ',
        '    Просто топ!👍    ',
        '    Оруууу!🤣    ',
        '    Слёзы от смеха!😭    ',
        '    Это в мемы!📸    ',
        '    Браво, комик!👏    ',
        '    10 из 10 по шкале юмора!💯    ',
        '    Пиши ещё, стендапер!🎤    ',
        '    Я в голос!😹    ',
        '    Смешно до боли!😂    ',
        '    Это надо записать!📝    ',
        '    Вот это шутка!😆    ',
        '    Смешнее только коты в интернете!🐱    ',
        '    Я так не смеялся с детства!🤣    ',
        '    Просто разрыв!💥    ',
        '    У меня аж живот заболел от смеха!😄    ',
        '    Это шедевр!🎉    ',
        '    Смешно, аж соседи стучат!😅    ',
        '    Ну ты и юморист!😂    ',
        '    Поржал от души!😆    ',
        '    Смешно, не могу!🤣    ',
        '    Это надо в цитатник!📖    ',
        '    Я чуть чай не пролил!☕    ',
        '    Смешно, аж кот проснулся!🐈    ',
        '    У меня слёзы на глазах!😭    ',
        '    Это просто бомба!💣    ',
        '    Я так не смеялся даже на КВН!🎭    ',
        '    Смешно, аж интернет завис!🌐    ',
        '    Это надо друзьям показать!👥    ',
        '    Я в шоке от твоего юмора!😲    ',
        '    Смешно, аж телефон выпал из рук!📱    ',
        '    Это лучше любого анекдота!📚    ',
        '    Я чуть не задохнулся от смеха!😆    ',
        '    Смешно, аж бабушка заулыбалась!👵    ',
        '    Это надо в эфир!📻    ',
        '    Я так не смеялся даже на мемах!😂    ',
        '    Смешно, аж собака залаяла!🐶    ',
        '    Это просто разрыв шаблона!🧩    ',
        '    Я чуть не упал со стула!🪑    ',
        '    Смешно, аж монитор трясётся!🖥️    ',
        '    Это надо в TikTok!🎬    ',
        '    Я в восторге от твоих шуток!🤩    ',
        '    Смешно, аж соседи смеются!🏠    ',
        '    Весь род. дом ржёт с тебя😆    '
    ]

    for i in range(15):
        await msg.edit(random.choice(laughts))
        await asyncio.sleep(3)

@func(filters.command('clown', prefixes=['.', '!', '/']) & filters.me)
async def clown(_, msg: types.Message):
    await msg.edit("""🫲 😐🫱            📷""")
    await asyncio.sleep(1)
    await msg.edit("""🫲 😐🫱      📷""")
    await asyncio.sleep(1)
    await msg.edit("""🫲 😐🫱  📷""")
    await asyncio.sleep(1)
    await msg.edit("""🫲 😐📷""")
    await asyncio.sleep(1)
    await msg.edit("""🫲 😐📸""")
    await asyncio.sleep(1)
    await msg.edit("""🫲 😐📷""")
    await asyncio.sleep(1)
    await msg.edit("""🫲 😐📷
           🖼️""")
    await asyncio.sleep(1)
    await msg.edit("""🫲 😐🫱
           🖼️""")
    await asyncio.sleep(1)
    await msg.edit("""🫲 😐🖼️""")
    await asyncio.sleep(1)
    await msg.edit("""🫵 😐🤡""")

@func(filters.command('ocase', prefixes=['.', '!', '/']) & filters.me)
async def open_case(_, msg: types.Message):
    splited = msg.text.split()
    
    try:
        if int("".join(splited[1])) <= 0:
            return await msg.edit("Нельзя ставить прокрутку меньше 1")
    except Exception as e:
        await spin_case(msg)
    
    try:
        await spin_case(msg, spin=splited[1])
    except:
        pass

async def spin_case(msg, spin=10):
    emojis_in_case = ["⬜", "🟦", "🟧", "🟪", "🟨", "🟥", "⬛", "💟"]
    
    output = "".join([random.choice(emojis_in_case) for i in range(14)])
    
    await msg.edit(f"⬜⬜⬜⬜⬜⬜3️⃣⬜⬜⬜⬜⬜⬜⬜\n{output}")
    
    await asyncio.sleep(0.5)
    
    await msg.edit(f"⬜⬜⬜⬜⬜⬜2️⃣⬜⬜⬜⬜⬜⬜⬜\n{output}")
    
    await asyncio.sleep(0.5)
    
    await msg.edit(f"⬜⬜⬜⬜⬜⬜1️⃣⬜⬜⬜⬜⬜⬜⬜\n{output}")
    
    await asyncio.sleep(0.5)
    
    await msg.edit(f"⬜⬜⬜⬜⬜⬜🔽⬜⬜⬜⬜⬜⬜⬜\n{output}")
    
    for i in range(int(spin)):
        try:
            output = output[1:]
            output += random.choice(emojis_in_case)
            
            await msg.edit(f"⬜⬜⬜⬜⬜⬜🔽⬜⬜⬜⬜⬜⬜⬜\n{output}")

            await asyncio.sleep(0.05)
        except FloodWait as e:
            await asyncio.sleep(e.value)

    await asyncio.sleep(0.5)
    
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
    
    if msg.reply_to_message:
        try:
            name = msg.reply_to_message.from_user.first_name
        except:
            name = msg.from_user.first_name
        await msg.edit(f"⬜⬜⬜⬜⬜⬜🔽⬜⬜⬜⬜⬜⬜⬜\n{output}\n{name} выпало: {emoji_rare.get(output[6])}")
    else:
        await msg.edit(f"⬜⬜⬜⬜⬜⬜🔽⬜⬜⬜⬜⬜⬜⬜\n{output}\nвам выпало: {emoji_rare.get(output[6])}")

@func(filters.command('ex', prefixes=['.', '!', '/']) & filters.me)
async def ex(_, msg: types.Message):
    await msg.edit(random.choice(["Правда", "Ложь"]))

@func(filters.command('dc', prefixes=['.', '!', '/']) & filters.me)
async def doctor(_, msg: types.Message):
    await msg.edit("👨‍⚕️ Здравствуйте, я доктор Floats, сейчас я возьму у вас кровь для анализа болезни \"Кринжанутый\"💉. Пожалуйста не двигайтесь а то дам подзатылок.")
    
    await asyncio.sleep(7)
    
    proc = 0
    
    while (proc < 101):
        try:
            await msg.edit(f"Набрано крови в шприц...{proc}%")
            
            await asyncio.sleep(0.1)
            
            proc += random.randint(1, 5)
        except FloodWait as e:
            await asyncio.sleep(e.value)
    
    proc = 0
    
    while (proc < 101):
        try:
            await msg.edit(f"ИИ анализирует...{proc}%")
            
            await asyncio.sleep(0.1)
            
            proc += random.randint(1, 5)
        except FloodWait as e:
            await asyncio.sleep(e.value)
    
    await msg.edit(random.choice(["Чист", "Заражён, бегите отсюда"]))

@func(filters.command('ghoul', prefixes=['.', '!', '/']) & filters.me)
async def ghoul_table(_, msg: types.Message):
    row = 0
    ghoulich = 1000
    output = ''

    while ghoulich >= 0:
        try:
            row += 1
            ghoulich -= 7

            output += f"{ghoulich + 7} - 7 = {ghoulich}\n\n"

            if row == 10:
                await msg.edit(output)
                output = ''
                row = 0
            
            await asyncio.sleep(0.1)
        except FloodWait as e:
            await asyncio.sleep(e.value)
    
    await msg.edit(output)

@func(filters.command('proc', prefixes=['.', '!', '/']) & filters.me)
async def procents(_, msg: types.Message):
    try:
        find_texts = re.findall(r'"(.*?)"', msg.text)
        text1 = find_texts[0]
        text2 = find_texts[1]
    except IndexError as e:
        return await msg.edit('Вы не верно ввели параметры.Пример: /proc "загрузка" "результат"')
    
    text2 = f"{text2.strip()}"
    
    proc = 0
    
    while (proc < 101):
        try:
            await msg.edit(f"{text1}{proc}%")
            
            await asyncio.sleep(0.2)
            
            proc += random.randint(1, 5)
        except FloodWait as e:
            await asyncio.sleep(e.value)
        
    await msg.edit(f"{text2}")

@func(filters.command('love', prefixes=['.', '!', '/']) & filters.me)
async def love_animation(_, msg: types.Message):
    try:
        await msg.edit("""❤️""")
        await asyncio.sleep(0.1)
        await msg.edit("""🧡""")
        await asyncio.sleep(0.1)
        await msg.edit("""💛""")
        await asyncio.sleep(0.1)
        await msg.edit("""💚""")
        await asyncio.sleep(0.1)
        await msg.edit("""💙""")
        await asyncio.sleep(0.1)
        await msg.edit("""💜""")
        await asyncio.sleep(0.1)
        await msg.edit("""🤎""")
        await asyncio.sleep(0.1)
        await msg.edit("""🖤""")
        await asyncio.sleep(0.1)
        await msg.edit("""🤍""")
        await asyncio.sleep(0.1)
        await msg.edit("""❤️❤️
❤️❤️""")
        await asyncio.sleep(0.1)
        await msg.edit("""🧡🧡
🧡🧡""")
        await asyncio.sleep(0.1)
        await msg.edit("""💛💛
💛💛""")
        await asyncio.sleep(0.1)
        await msg.edit("""💚💚
💚💚""")
        await asyncio.sleep(0.1)
        await msg.edit("""💙💙
💙💙""")
        await asyncio.sleep(0.1)
        await msg.edit("""💜💜
💜💜""")
        await asyncio.sleep(0.1)
        await msg.edit("""🤎🤎
🤎🤎""")
        await asyncio.sleep(0.1)
        await msg.edit("""🖤🖤
🖤🖤""")
        await asyncio.sleep(0.1)
        await msg.edit("""🤍🤍
🤍🤍""")
        await asyncio.sleep(0.1)
        await msg.edit("""❤️❤️❤️
❤️❤️❤️
❤️❤️❤️""")
        await asyncio.sleep(0.1)
        await msg.edit("""🧡🧡🧡
🧡🧡🧡
🧡🧡🧡""")
        await asyncio.sleep(0.1)
        await msg.edit("""💛💛💛
💛💛💛
💛💛💛""")
        await asyncio.sleep(0.1)
        await msg.edit("""💚💚💚
💚💚💚
💚💚💚""")
        await asyncio.sleep(0.1)
        await msg.edit("""💙💙💙
💙💙💙
💙💙💙""")
        await asyncio.sleep(0.1)
        await msg.edit("""💜💜💜
💜💜💜
💜💜💜""")
        await asyncio.sleep(0.1)
        await msg.edit("""🤎🤎🤎
🤎🤎🤎
🤎🤎🤎""")
        await asyncio.sleep(0.1)
        await msg.edit("""🖤🖤🖤
🖤🖤🖤
🖤🖤🖤""")
        await asyncio.sleep(0.1)
        await msg.edit("""🤍🤍🤍
🤍🤍🤍
🤍🤍🤍""")
        await asyncio.sleep(0.1)
        await msg.edit("""❤️❤️❤️❤️❤️❤️
❤️❤️❤️❤️❤️❤️
❤️❤️❤️❤️❤️❤️
❤️❤️❤️❤️❤️❤️
❤️❤️❤️❤️❤️❤️
❤️❤️❤️❤️❤️❤️""")
        await asyncio.sleep(0.1)
        await msg.edit("""🧡🧡🧡🧡🧡🧡
🧡🧡🧡🧡🧡🧡
🧡🧡🧡🧡🧡🧡
🧡🧡🧡🧡🧡🧡
🧡🧡🧡🧡🧡🧡
🧡🧡🧡🧡🧡🧡""")
        await asyncio.sleep(0.1)
        await msg.edit("""💛💛💛💛💛💛
💛💛💛💛💛💛
💛💛💛💛💛💛
💛💛💛💛💛💛
💛💛💛💛💛💛
💛💛💛💛💛💛""")
        await asyncio.sleep(0.1)
        await msg.edit("""💚💚💚💚💚💚
💚💚💚💚💚💚
💚💚💚💚💚💚
💚💚💚💚💚💚
💚💚💚💚💚💚
💚💚💚💚💚💚""")
        await asyncio.sleep(0.1)
        await msg.edit("""💙💙💙💙💙💙
💙💙💙💙💙💙
💙💙💙💙💙💙
💙💙💙💙💙💙
💙💙💙💙💙💙
💙💙💙💙💙💙""")
        await asyncio.sleep(0.1)
        await msg.edit("""💜💜💜💜💜💜
💜💜💜💜💜💜
💜💜💜💜💜💜
💜💜💜💜💜💜
💜💜💜💜💜💜
💜💜💜💜💜💜""")
        await asyncio.sleep(0.1)
        await msg.edit("""🤎🤎🤎🤎🤎🤎
🤎🤎🤎🤎🤎🤎
🤎🤎🤎🤎🤎🤎
🤎🤎🤎🤎🤎🤎
🤎🤎🤎🤎🤎🤎
🤎🤎🤎🤎🤎🤎""")
        await asyncio.sleep(0.1)
        await msg.edit("""🖤🖤🖤🖤🖤🖤
🖤🖤🖤🖤🖤🖤
🖤🖤🖤🖤🖤🖤
🖤🖤🖤🖤🖤🖤
🖤🖤🖤🖤🖤🖤
🖤🖤🖤🖤🖤🖤""")
        await asyncio.sleep(0.1)
        await msg.edit("""🤍🤍🤍🤍🤍🤍
🤍🤍🤍🤍🤍🤍
🤍🤍🤍🤍🤍🤍
🤍🤍🤍🤍🤍🤍
🤍🤍🤍🤍🤍🤍
🤍🤍🤍🤍🤍🤍""")

        hearths = ["🧡", "💛", "💚", "💙", "💜", "🤎", "🖤", "🤍"]
        
        for n in range(10):
            output = ''
            for i in range(5):
                output += "".join([random.choice(["❤", "🧡", "💛", "💚", "💙", "💜", "🤎", "🖤", "🤍"]) for j in range(7)]) + "\n"

            output += "".join([random.choice(["❤", "🧡", "💛", "💚", "💙", "💜", "🤎", "🖤", "🤍"]) for j in range(7)])

            await msg.edit(output)
            await asyncio.sleep(0.1)

        for n in range(10):
            output = ''
            for i in range(5):
                output += "".join([random.choice(["❤", "🧡", "💛", "💚", "💙", "💜", "🤎", "🖤", "🤍"]) for j in range(7)]) + "\n"
            
            output += "".join([random.choice(hearths) for j in range(3)]) + "❤" + "".join([random.choice(hearths) for j in range(3)])
            
            await msg.edit(output)
            await asyncio.sleep(0.1)
        
        for n in range(10):
            output = ''
            for i in range(4):
                output += "".join([random.choice(["❤", "🧡", "💛", "💚", "💙", "💜", "🤎", "🖤", "🤍"]) for j in range(7)]) + "\n"
            
            output += "".join([random.choice(hearths) for j in range(2)]) + "❤❤❤" + "".join([random.choice(hearths) for j in range(2)]) + "\n"
            
            output += "".join([random.choice(hearths) for j in range(3)]) + "❤" + "".join([random.choice(hearths) for j in range(3)])
            
            await msg.edit(output)
            await asyncio.sleep(0.1)
        
        for n in range(10):
            output = ''
            for i in range(3):
                output += "".join([random.choice(["❤", "🧡", "💛", "💚", "💙", "💜", "🤎", "🖤", "🤍"]) for j in range(7)]) + "\n"
            
            output += "".join([random.choice(["❤", "🧡", "💛", "💚", "💙", "💜", "🤎", "🖤", "🤍"]) for j in range(1)]) + "❤❤❤❤❤" + "".join([random.choice(["❤", "🧡", "💛", "💚", "💙", "💜", "🤎", "🖤", "🤍"]) for j in range(1)])  + "\n"
            
            output += "".join([random.choice(hearths) for j in range(2)]) + "❤❤❤" + "".join([random.choice(hearths) for j in range(2)]) + "\n"
            
            output += "".join([random.choice(hearths) for j in range(3)]) + "❤" + "".join([random.choice(hearths) for j in range(3)])
            
            await msg.edit(output)
            await asyncio.sleep(0.1)
        
        for n in range(10):
            output = ''
            for i in range(2):
                output += "".join([random.choice(["❤", "🧡", "💛", "💚", "💙", "💜", "🤎", "🖤", "🤍"]) for j in range(7)]) + "\n"
            
            output += "❤❤❤❤❤❤❤"  + "\n"
            
            output += "".join([random.choice(["❤", "🧡", "💛", "💚", "💙", "💜", "🤎", "🖤", "🤍"]) for j in range(1)]) + "❤❤❤❤❤" + "".join([random.choice(["❤", "🧡", "💛", "💚", "💙", "💜", "🤎", "🖤", "🤍"]) for j in range(1)])  + "\n"
            
            output += "".join([random.choice(hearths) for j in range(2)]) + "❤❤❤" + "".join([random.choice(hearths) for j in range(2)]) + "\n"
            
            output += "".join([random.choice(hearths) for j in range(3)]) + "❤" + "".join([random.choice(hearths) for j in range(3)])
            
            await msg.edit(output)
            await asyncio.sleep(0.1)
        
        for n in range(10):
            output = ''
            for i in range(1):
                output += "".join([random.choice(["❤", "🧡", "💛", "💚", "💙", "💜", "🤎", "🖤", "🤍"]) for j in range(7)]) + "\n"
            
            output += "❤❤❤❤❤❤❤"  + "\n"
            
            output += "❤❤❤❤❤❤❤"  + "\n"
            
            output += "".join([random.choice(["❤", "🧡", "💛", "💚", "💙", "💜", "🤎", "🖤", "🤍"]) for j in range(1)]) + "❤❤❤❤❤" + "".join([random.choice(["❤", "🧡", "💛", "💚", "💙", "💜", "🤎", "🖤", "🤍"]) for j in range(1)])  + "\n"
            
            output += "".join([random.choice(hearths) for j in range(2)]) + "❤❤❤" + "".join([random.choice(hearths) for j in range(2)]) + "\n"
            
            output += "".join([random.choice(hearths) for j in range(3)]) + "❤" + "".join([random.choice(hearths) for j in range(3)])
            
            await msg.edit(output)
            await asyncio.sleep(0.1)
        
        for n in range(10):
            output = ''

            output += "".join([random.choice(["❤", "🧡", "💛", "💚", "💙", "💜", "🤎", "🖤", "🤍"]) for j in range(1)]) + "❤❤" + "".join([random.choice(["❤", "🧡", "💛", "💚", "💙", "💜", "🤎", "🖤", "🤍"]) for j in range(1)]) + "❤❤" + "".join([random.choice(["❤", "🧡", "💛", "💚", "💙", "💜", "🤎", "🖤", "🤍"]) for j in range(1)]) + "\n"
            
            output += "❤❤❤❤❤❤❤"  + "\n"
            
            output += "❤❤❤❤❤❤❤"  + "\n"
            
            output += "".join([random.choice(hearths) for j in range(1)]) + "❤❤❤❤❤" + "".join([random.choice(hearths) for j in range(1)])  + "\n"
            
            output += "".join([random.choice(hearths) for j in range(2)]) + "❤❤❤" + "".join([random.choice(hearths) for j in range(2)]) + "\n"
            
            output += "".join([random.choice(hearths) for j in range(3)]) + "❤" + "".join([random.choice(hearths) for j in range(3)])
            
            await msg.edit(output)
            await asyncio.sleep(0.1)
        
        random.shuffle(hearths)

        for hearth in hearths:
            output = ''
            
            output += "".join([hearth for j in range(1)]) + "❤❤" + "".join([hearth for j in range(1)]) + "❤❤" + "".join([hearth for j in range(1)]) + "\n"
            
            output += "❤❤❤❤❤❤❤"  + "\n"
            
            output += "❤❤❤❤❤❤❤"  + "\n"
            
            output += "".join([random.choice(hearth) for j in range(1)]) + "❤❤❤❤❤" + "".join([random.choice(hearth) for j in range(1)])  + "\n"
                
            output += "".join([hearth for j in range(2)]) + "❤❤❤" + "".join([hearth for j in range(2)]) + "\n"
                
            output += "".join([hearth for j in range(3)]) + "❤" + "".join([hearth for j in range(3)])
                
            await msg.edit(output)
            await asyncio.sleep(0.1)
    except FloodWait as e:
        await asyncio.sleep(e.value)

@func(filters.command('t', prefixes=['.', '!', '/']) & filters.me)
async def type_text(_, msg: types.Message):
    original_text = ' '.join(msg.text.split()[1:])
   
    if not original_text:
        return await msg.edit("Вы не указали параметр: {текст}")
   
    text = ""
    while (len(original_text) != 0):
        try:
            text += original_text[0]
            
            original_text = original_text[1:]
            
            await msg.edit(text + f"{'|' if len(original_text) % 2 == 0 else ''}")
        except FloodWait as e:
            await asyncio.sleep(e.value)
   
    await msg.edit(text)

@func(filters.command('hacker', prefixes=['.', '!', '/']) & filters.me)
async def hacker_animation(_, msg: types.Message):
    original_text = ' '.join(msg.text.split()[1:])

    if not original_text:
        return await msg.edit("Вы не указали параметр: {текст}")
    
    count_sim = int(len(original_text) * 0.30)
    
    hiden_text = ['||' + char + '||' for char in original_text]
    
    shows_text = set()
    tick = 0
    
    while len(shows_text) < len(original_text):
        try:
            take_indexes = []
            
            available_indices = [i for i in range(len(original_text)) 
                               if i not in shows_text]
            
            if not available_indices:
                break
            
            count_to_take = min(count_sim, len(available_indices))
            take_indexes = random.sample(available_indices, count_to_take)
            
            for idx in take_indexes:
                hiden_text[idx] = random.choice(['$', '%', '*', '&'])
            
            if tick == 16:
                shows_text.update(take_indexes)
                
                for idx in take_indexes:
                    hiden_text[idx] = original_text[idx]
                
                take_indexes = []
                tick = -1
            
            tick += 1
            
            await msg.edit_text(''.join(hiden_text))
            await asyncio.sleep(0.1)
            
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except MessageNotModified:
            pass