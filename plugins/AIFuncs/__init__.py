from g4f.client import AsyncClient
from g4f.Provider import RetryProvider, __providers__, OIVSCodeSer2, PollinationsAI, ApiAirforce
from g4f.models import (
    Chatai,
    Cloudflare,
    Copilot,
    DeepInfra,
    HuggingSpace,
    Grok,
    DeepseekAI_JanusPro7b,
    LambdaChat,
    OIVSCodeSer0501,
    OIVSCodeSer2,
    OperaAria,
    OpenAIFM,
    PollinationsAI,
    TeachAnything,
    Together,
    WeWordle,
    Yqcloud,
)
from g4f.models import _all_models
import json
from loads import all_func, func, MainDescription, Description, FuncDescription, Data
from pyrogram import filters, types, enums
from pyrogram.client import Client
from colorama import init, Fore
import base64
import io
import time
from typing import Any, Union, List, Dict
import g4f.debug
import traceback

g4f.debug.logging = True

__description__ = Description(
    MainDescription("Плагин для работы с ИИ."),
    FuncDescription('rqai', 'Возвращает ответ от ИИ.Также ИИ может смотреть изображение(просто отправьте изображение и в описании его напишите эту команду с промптом)', prefixes=['.', '!', '/'], parameters=['промпт']),
    FuncDescription('genimg', 'Генерирует изображение по запросу.', prefixes=['.', '!', '/'], parameters=['промпт']),
    FuncDescription('txtmodel', 'Меняет текстовую модель.Если не вводить параметр, то в консоль выведет список ИИ.', prefixes=['.', '!', '/'], parameters=['модель']),
    FuncDescription('imgmodel', 'Меняет модель для изображения.Если не вводить параметр, то в консоль выведет список ИИ.', prefixes=['.', '!', '/'], parameters=['модель']),
    FuncDescription('correct', 'Делает предложения корректным и грамотным.', prefixes=['.', '!', '/'], parameters=['предложения']),
    FuncDescription('turn_websrch', 'Включения/выключения технологии web search для ИИ(Может не работать).', prefixes=['.', '!', '/']),
    FuncDescription('aihtry', 'ИИ читает историю чата.', prefixes=['.', '!', '/'], parameters=[r'\-\-c={число} и/или текст']),
    FuncDescription('style', 'Изменяет стиль общения ИИ.По умолчанию он обычный, если нечего не указывать, стиль изменится на по умолчанию.', prefixes=['.', '!', '/'], parameters=['не обязательно(стиль)']),
    FuncDescription('aifk', 'Улучшенная версия afk, где ИИ заменяет вас, пока вы куда то отошли.', prefixes=['.', '!', '/'])
)

init(True)

config = {"text_model": "gpt-4o-mini", "image_model": "gemini-2.5-flash", "history": [], "history_len": 20, "warnings": True, "web_search": False, "style": "обычный", "afk": False}

Data.get_config('AIFuncs').setdefault(config)

config = Data.get_config('AIFuncs')

best_model = Fore.YELLOW + '👑Надёжные модели👑' + Fore.RESET + '\n' + Fore.RED + '[ ДЛЯ ТЕКСТА ]' + Fore.RESET + '\n' + '\n'.join(['gpt-4', 'gpt-4o', 'gpt-4o-mini', 'o1', 'o1-mini', 'o3-mini', 'o3-mini-high', 'o4-mini', 'o4-mini-high', 'gpt-4.1', 'gpt-4.1-mini', 'gpt-4.1-nano', 'gpt-4.5', 'llama-3.1-8b', 'llama-3.1-70b', 'llama-3.1-405b', 'llama-3.2-3b', 'llama-3.2-11b', 'llama-3.2-90b', 'llama-3.3-70b', 'gemini-2.0', 'gemini-2.0-flash', 'gemini-2.0-flash-thinking', 'gemini-2.5-flash', 'gemini-2.5-pro', 'gemma-3-4b', 'gemma-3-12b', 'gemma-3-27b', 'gemma-3n-e4b', 'qwen-3-235b', 'qwen-3-32b', 'qwen-3-30b', 'qwen-3-14b', 'qwen-3-4b', 'qwen-3-1.7b', 'qwen-3-0.6b', 'qwq-32b', 'deepseek-v3', 'deepseek-r1', 'deepseek-r1-turbo', 'deepseek-r1-distill-llama-70b', 'deepseek-v3', 'deepseek-r1', 'deepseek-r1-turbo', 'grok-2', 'grok-3', 'grok-3-r1']) + '\n\n' + Fore.RED + '[ ДЛЯ ИЗОБРАЖЕНИЙ ]' + Fore.RESET + '\n' + '\n'.join(['dall-e-3', 'gpt-image', 'sdxl-turbo', 'sd-3.5-large', 'flux', 'flux-pro', 'flux-dev', 'flux-schnell', 'flux-redux', 'flux-depth', 'flux-canny', 'flux-kontext', 'flux-dev-lora', 'gemini-2.0-flash', 'gemini-2.0-flash-thinking', 'gemini-2.5-flash', 'gemini-2.5-pro'])

def initialization(_):
    if config['history_len'] >= 100 and config['warnings']:
        print(Fore.WHITE + "AIFuncs " + Fore.YELLOW + "| ⚠ Чем больше длинна истории, тем больше нагрузка для юзер бота !")

class Conservation:
    def __init__(self):
        self.client = AsyncClient(provider=RetryProvider([
            Chatai, Cloudflare, Copilot, DeepInfra, HuggingSpace, Grok, 
            DeepseekAI_JanusPro7b, LambdaChat, OIVSCodeSer2, 
            OIVSCodeSer0501, OperaAria, OpenAIFM,
            PollinationsAI, TeachAnything, Together, WeWordle, Yqcloud
        ]))
        self.history = [{
            "role": "system",
            "content": "Ты обычный assistant в телеграмме, ты общаешься с user.Если требуется, используй форматирование: ```lang_programming\ntext\n```, **text**, ~~text~~, __text__, `text_to_copy`.Общайся в стиле(если обычный, игнорируй это): " + config['style']
        }] + config['history']

        self.system_prompts = []

    def add_message(self, role, content) -> None:
        self.history.append({
            "role": role,
            "content": content
        })

        config['history'].append({
            "role": role,
            "content": content
        })

        if len(config['history']) > config['history_len']:
            config['history'] = config['history'][int(config['history_len']/4):]
        
        with open('plugins/AIFuncs/config.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False)
    
    async def get_response(self, user_message, web_search: bool=False, history: bool=True, image: bytes=None) -> Union[str, None]:
        if history: self.add_message("user", user_message)

        messages: list[Dict[str, Any]] = self.system_prompts + self.history + [{"role": "user", "content": user_message}] if history else [{"role": "user", "content": user_message}]

        providers = RetryProvider([OIVSCodeSer2, PollinationsAI, ApiAirforce]) if image != None else None
        
        response = await self.client.chat.completions.create(
            model=config['text_model'],
            messages=messages,
            web_search=web_search if web_search is not None else config['web_search'],
            image=image,
            provider=providers,
            max_tokens=4096
        )
        
        assistant_response = response.choices[0].message.content

        if not isinstance(assistant_response, str):
            return await self.get_response(user_message, web_search, history)

        if len(assistant_response) > 4096:
            assistant_response = None

        if history: self.add_message("assistant", assistant_response)
        
        return assistant_response

    async def generate_image(self, prompt: str, web_search: bool=None) -> bytes:
        response = await self.client.images.generate(
            prompt=prompt,
            model=config['image_model'],
            response_format='b64_json',
            web_search=web_search if web_search is not None else config['web_search']
        )

        img_bytes = base64.b64decode(response.data[0].b64_json)

        return img_bytes
    
    async def response_with_prompt(self, prompt: List[Dict[str, Any]], web_search: bool=None) -> Union[str, None]:
        response = await self.client.chat.completions.create(
            model=config['text_model'],
            messages=prompt,
            web_search=web_search if web_search is not None else config['web_search'] 
        )

        assistant_response = response.choices[0].message.content

        return assistant_response

_ai = Conservation()

@func(filters.command('rqai', prefixes=['.', '!', '/']) & filters.me)
async def request_ai(app: Client, message: types.Message):
    if len(message.text.split()) == 1:
        return await message.edit_text('Вы не верно ввели параметры.Пример: `.rqai Привет!`', parse_mode=enums.ParseMode.MARKDOWN)

    await message.edit_text('__Ожидайте ответ от ИИ...__', parse_mode=enums.ParseMode.MARKDOWN)

    if message.photo is not None:
        _image = await app.download_media(message, in_memory=True)

        file_bytes = bytes(_image.getbuffer())
    else:
        file_bytes = None

    ai_text = await _ai.get_response(message.text.split(maxsplit=1)[1], image=file_bytes)

    if ai_text is None:
        await message.edit_text('__Ожидайте ответ от ИИ...__(повторная попытка)', parse_mode=enums.ParseMode.MARKDOWN)
        return await request_ai(app, message)

    await message.edit_text(ai_text, parse_mode=enums.ParseMode.MARKDOWN)

@func(filters.command('genimg', prefixes=['.', '!', '/']) & filters.me)
async def generate_image(app: Client, message: types.Message):
    if len(message.text.split()) == 1:
        return await message.edit_text('Вы не верно ввели параметры.Пример: `.genimg Коты кушают корм`', parse_mode=enums.ParseMode.MARKDOWN)
    
    await message.edit_text('__Ожидайте, ИИ генерирует изображение...__', parse_mode=enums.ParseMode.MARKDOWN)

    start_time = time.time()
    
    ai_image = await _ai.generate_image(message.text.split(maxsplit=1)[1])

    end_time = time.time()

    try:
        await message.delete()
    except:
        pass

    bytes_image = io.BytesIO(ai_image)
    bytes_image.name = 'ai_image.png'

    await app.send_photo(message.chat.id, bytes_image, f'Сгенерированное изображение на запрос: {" ".join(message.text.split()[1:])}\n\nГенерация заняла: {round(end_time - start_time, 2)} сек.\nМодель: {config["image_model"]}')

@func(filters.command('txtmodel', prefixes=['.', '!', '/']) & filters.me)
async def change_text_model(app: Client, message: types.Message):
    if len(message.text.split()) == 1:
        print(best_model)

        return await message.edit_text('Список моделей было выведено в консоль.')
    
    model = message.text.split()[1]

    if model not in _all_models:
        return await message.edit(f'Данной модели `{model}` не существует.')

    config['text_model'] = model
    
    with open('plugins/AIFuncs/config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False)
    
    await message.edit(f'Установлена текстовая модель: `{model}`')

@func(filters.command('imgmodel', prefixes=['.', '!', '/']) & filters.me)
async def change_image_model(app: Client, message: types.Message):
    if len(message.text.split()) == 1:
        print(best_model)
        
        return await message.edit_text('Список моделей было выведено в консоль.')
    
    model = message.text.split()[1]

    if model not in _all_models:
        return await message.edit(f'Данной модели `{model}` не существует.')

    config['image_model'] = model
    
    with open('plugins/AIFuncs/config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False)
    
    await message.edit(f'Установлена модель: `{model}`')

@func(filters.command('correct', prefixes=['.', '!', '/']) & filters.me)
async def correct_words(app: Client, message: types.Message):
    if len(message.text.split()) == 1:
        return await message.edit_text('Вы не верно ввели параметры.Пример: .correct Некоторое количество предложений.')

    await message.edit_text('__Ожидайте, ИИ редактирует текст...__', parse_mode=enums.ParseMode.MARKDOWN)
    
    ai_correct_text = await _ai.response_with_prompt([{"role": "system", "content": "Твоя задача: исправить грамматику и орфографию, сделать текст грамотным."}, {"role": "user", "content": message.text.split(maxsplit=1)[1]}])

    try:
        await message.edit_text(ai_correct_text)
    except:
        await correct_words(app, message)

@func(filters.command('turn_websrch', prefixes=['.', '!', '/']) & filters.me)
async def turn_web_search(app: Client, message: types.Message):
    if config['web_search']:
        config['web_search'] = False

        await message.edit_text('Web search выключен.')
    else:
        config['web_search'] = True

        await message.edit_text('Web search включен.')

@func(filters.command('aihtry', prefixes=['.', '!', '/']) & filters.me)
async def read_chat_history(app: Client, message: types.Message):
    count = 20
    prompt = ''

    if len(message.text.split()) >= 3 and message.text.split()[1].startswith('--c='):
        count = int(message.text.split()[1].replace('--c=', '')) if message.text.split()[1].replace('--c=', '').isdigit() else 20
        prompt = ' '.join(message.text.split(' ')[2:])
    else:
        prompt = ' '.join(message.text.split(' ')[1:])
    
    history = []

    await message.edit_text('__ИИ читает сообщения...__')
    
    async for messages in app.get_chat_history(message.chat.id, count):
        if messages.text is not None:
            if messages.text == '__ИИ читает сообщения...__':
                continue

            history.append({"role": "user", "content": f"{messages.from_user.first_name}: {messages.text}"})
    
    await message.edit_text('__ИИ генерирует сообщение...__')
    
    ai_text = await _ai.response_with_prompt([_ai.history[0], {"role": "system", "content": "Это история чата пользователей, их имена помечены как: {имя}: {текст}, если никак не помечено, значит это промпт пользователя"}, *history, {"role": "user", "content": f"{prompt}"}])

    await message.edit_text(ai_text, parse_mode=enums.ParseMode.MARKDOWN)

@func(filters.command('aifk', prefixes=['.', '!', '/']) & filters.me)
async def ai_afk(app: Client, message: types.Message):
    global config

    if Data.get_config('AIFuncs')['afk']:
        Data.get_config('AIFuncs')['afk'] = False

        await message.edit_text('AI afk выключен.')
    else:
        Data.get_config('AIFuncs')['afk'] = True

        await message.edit_text('AI afk включен.')

@all_func()
async def ai_afk_privat(app: Client, message: types.Message):
    if Data.get_config('AIFuncs')['afk'] and message.chat.type == enums.ChatType.PRIVATE:
        msg = await app.send_message(message.from_user.id, '__Пользователь не на месте, ИИ генерирует вам сообщение...__')

        ai_text = await _ai.response_with_prompt([{"role": "system", "content": "Ты заменяешь владельца в телеграме, владелец не в онлайне.Если требуется, используй форматирование: ```lang_programming\ntext\n```, **text**, ~~text~~, __text__, `text_to_copy`"}, {"role": "user", "content": message.text}])

        try:
            await msg.edit_text(ai_text)
        except:
            await app.send_message(message.from_user.id, ai_text, parse_mode=enums.ParseMode.MARKDOWN)

@func(filters.command('style', prefixes=['.', '!', '/']) & filters.me)
async def change_style(app: Client, message: types.Message):
    global config
    if len(message.text.split()) == 1:
        config['style'] = 'обычный'

        return await message.edit_text('Стиль общения изменён на `обычный`.', parse_mode=enums.ParseMode.MARKDOWN)
    
    style = ' '.join(message.text.split()[1:])

    config['style'] = style

    await message.edit_text(f'Стиль общения изменён на: `{style}`', parse_mode=enums.ParseMode.MARKDOWN)

@func(filters.command('sysprompt', prefixes=['.', '!', '/']) & filters.me)
async def set_system_prompt(app: Client, message: types.Message):
    if len(message.text.split()) == 1:
        _ai.system_prompts.clear()

        return await message.edit_text('Системный промпт был очищен.')
    
    prompt = ' '.join(message.text.split()[1:])

    _ai.system_prompts.append({"role": "system", "content": prompt})

    await message.edit_text('Системный промпт был задан.')