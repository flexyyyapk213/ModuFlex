from g4f.client import AsyncClient
from g4f.Provider import RetryProvider, __providers__, OIVSCodeSer2, PollinationsAI, ApiAirforce
from g4f.models import _all_models
import json
from loads import func, MainDescription, Description, FuncDescription, Data
from pyrogram import filters, types, enums
from pyrogram.client import Client
from colorama import init, Fore
import base64
import io
import time
from typing import Union
import g4f.debug
import traceback

g4f.debug.logging = True

__description__ = Description(
    MainDescription("Плагин для работы с ИИ."),
    FuncDescription('rqai', 'Возвращает ответ от ИИ.', prefixes=['.', '!', '/'], parameters=['промпт']),
    FuncDescription('genimg', 'Генерирует изображение по запросу.', prefixes=['.', '!', '/'], parameters=['промпт']),
    FuncDescription('txtmodel', 'Меняет текстовую модель.Если не вводить параметр, то в консоль выведет список ИИ.', prefixes=['.', '!', '/'], parameters=['модель']),
    FuncDescription('imgmodel', 'Меняет модель для изображения.Если не вводить параметр, то в консоль выведет список ИИ.', prefixes=['.', '!', '/'], parameters=['модель']),
    FuncDescription('correct', 'Делает предложения корректным и грамотным.', prefixes=['.', '!', '/'], parameters=['предложения']),
    FuncDescription('vimg', 'ИИ смотрит на изображение, благодаря этому он может знать, что на фото.(Отправляйте фото и в описании/подпись пишите команду)', prefixes=['.', '!', '/'], parameters=['промпт']),
    FuncDescription('turn_websrch', 'Включения/выключения технологии web search для ИИ(Может не работать).', prefixes=['.', '!', '/'])
)

init(True)

config = {"text_model": "gpt-4o-mini", "image_model": "gemini-2.5-flash", "history": [], "history_len": 20, "warnings": True, "web_search": False}

if Data.get_config('AIFuncs') is None:
    Data.get_config('AIFuncs').update(config)

config = Data.get_config('AIFuncs')

best_model = Fore.YELLOW + '👑Надёжные модели👑' + Fore.RESET + '\n' + Fore.RED + '[ ДЛЯ ТЕКСТА ]' + Fore.RESET + '\n' + '\n'.join(['gpt-4', 'gpt-4o', 'gpt-4o-mini', 'o1', 'o1-mini', 'o3-mini', 'o3-mini-high', 'o4-mini', 'o4-mini-high', 'gpt-4.1', 'gpt-4.1-mini', 'gpt-4.1-nano', 'gpt-4.5', 'llama-2-70b', 'llama-3-8b', 'llama-3-70b', 'llama-3.1-8b', 'llama-3.1-70b', 'llama-3.1-405b', 'llama-3.2-3b', 'llama-3.2-11b', 'llama-3.2-90b', 'llama-3.3-70b', 'gemini-2.0', 'gemini-2.0-flash', 'gemini-2.0-flash-thinking', 'gemini-2.5-flash', 'gemini-2.5-pro', 'codegemma-7b', 'gemma-2b', 'gemma-1.1-7b', 'gemma-2-9b', 'gemma-2-27b', 'gemma-3-4b', 'gemma-3-12b', 'gemma-3-27b', 'gemma-3n-e4b', 'qwen-2-72b', 'qwen-2-vl-7b', 'qwen-2-vl-72b', 'qwen-2.5', 'qwen-2.5-7b', 'qwen-2.5-72b', 'qwen-2.5-coder-32b', 'qwen-2.5-1m', 'qwen-2.5-max', 'qwen-2.5-vl-72b', 'qwen-3-235b', 'qwen-3-32b', 'qwen-3-30b', 'qwen-3-14b', 'qwen-3-4b', 'qwen-3-1.7b', 'qwen-3-0.6b', 'qwq-32b', 'deepseek-v3', 'deepseek-r1', 'deepseek-r1-turbo', 'deepseek-r1-distill-llama-70b', 'deepseek-v3', 'deepseek-r1', 'deepseek-r1-turbo', 'grok-2', 'grok-3', 'grok-3-r1']) + '\n\n' + Fore.RED + '[ ДЛЯ ИЗОБРАЖЕНИЙ ]' + Fore.RESET + '\n' + '\n'.join(['gpt-4', 'gpt-4.1-mini', 'dall-e-3', 'gpt-image', 'sdxl-turbo', 'sd-3.5-large', 'flux', 'flux-pro', 'flux-dev', 'flux-schnell', 'flux-redux', 'flux-depth', 'flux-canny', 'flux-kontext', 'flux-dev-lora', 'gemini-2.0-flash', 'gemini-2.0-flash-thinking', 'gemini-2.5-flash', 'gemini-2.5-pro'])

def initialization(_):
    if config['history_len'] >= 50 and config['warnings']:
        print(Fore.WHITE + "AIFuncs " + Fore.YELLOW + "| ⚠ Чем больше длинна истории, тем больше нагрузка для юзер бота !!!")

class Conservation:
    def __init__(self):
        self.client = AsyncClient(provider=RetryProvider(__providers__))
        self.history = [{
            "role": "system",
            "content": "Ты обычный assistant в телеграмме, ты общаешься с user.Если требуется, используй форматирование: ```lang_programming\ntext\n```, **text**, ~~text~~, __text__, `text_to_copy`"
        }] + config['history']

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

        messages = self.history if history else {"role": "user", "content": user_message}

        providers = RetryProvider([OIVSCodeSer2, PollinationsAI, ApiAirforce]) if image != None else None
        
        response = await self.client.chat.completions.create(
            model=config['text_model'],
            messages=messages,
            web_search=web_search if web_search is not None else config['web_search'],
            image=image,
            provider=providers
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
    
    async def response_with_prompt(self, prompt: list[dict], web_search: bool=None) -> Union[str, None]:
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

    ai_text = await _ai.get_response(message.text.split(maxsplit=1)[1])

    if ai_text is None:
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

@func(filters.command('vimg', prefixes=['.', '!', '/']) & filters.me & filters.photo)
async def view_image(app: Client, message: types.Message):
    if len(message.caption.split()) == 1:
        return await message.edit_text('Вы не верно ввели параметры.Пример: .vimg Что то связанное с фото.(Нужно отравить фото с описанием таким)')

    await message.edit_text('__Ожидайте ответ от ИИ...__', parse_mode=enums.ParseMode.MARKDOWN)

    file = await app.download_media(message, in_memory=True)

    file_bytes = bytes(file.getbuffer())

    ai_image_view = await _ai.get_response(message.caption.split(maxsplit=1)[1], image=file_bytes)

    await message.edit_text(ai_image_view, parse_mode=enums.ParseMode.MARKDOWN)

@func(filters.command('turn_websrch', prefixes=['.', '!', '/']) & filters.me)
async def turn_web_search(app: Client, message: types.Message):
    if config['web_search']:
        config['web_search'] = False

        await message.edit_text('Web search выключен.')
    else:
        config['web_search'] = True

        await message.edit_text('Web search включен.')

