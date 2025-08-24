На данный момент проект ещё сырой, но он полон надежд и успехов

## Начало

Начнём с того, что создадим папку в файле plugins, название любое(главное, чтобы без пробелов).

Создаём файл \_\_init\_\_.py (без \\)

И можем начать писать плагин!

## Регистрация

```python
#Декоратор для регистрации функции
from loads import func
from pyrogram import filters, Client, types

@func(filters.command('test'))
async def test(client: Client, message: types.Message):
	#client: объект класса pyrogram.Client
	#message: объект класса pyrogram.types.Message
	await client.send_message(message.chat.id, 'test')
```

В теории можно делать и синхронные функции(но это в теории...)

Также можно указать несколько фильтров как и в pyrogram

```python
#Декоратор для регистрации функции
from loads import func
from pyrogram import filters, Client, types

@func(filters.command('test') & filters.me)
async def test(client: Client, message: types.Message):
	#client: объект класса pyrogram.Client
	#message: объект класса pyrogram.types.Message
	await client.send_message(message.chat.id, 'test')
```

С обновления `0.0.3` появились декораторы с помощью которых можно отслеживать приватные сообщения, сообщения из чата, сообщение из канала и все сообщения.
Нужны они потому, что если в обычном декораторе `func()` просто ввести в параметр фильтр `filters.private` и прочее, то остальные плагины не смогут работать как задумано.

```python
#Декораторы для регистрации функций
from loads import private_func, chat_func, channel_func, all_func
from pyrogram import Client, types

@private_func()
async def private_function(client: Client, message: types.Message):
	print('приватный чат')

@chat_func()
async def chat_function(client: Client, message: types.Message):
	print('чат')

@channel_func()
async def channel_function(client: Client, message: types.Message):
	print('канал')

@all_func()
async def private_function(client: Client, message: types.Message):
	print('все сообщения')
```

Если создать синхронную функцию `initialization(client: pyrogram.Client)`, то при запуске скрипта запуститься эта функция.

```python
from pyrogram import Client

def initialization(client: Client):
	client.send_message(...)
	# Другой код...
```

## Описания и модули

Чтобы пользователь смог изучить и использовать команды, нужно описать плагин:

```python
from loads import func, Description, MainDescription, FuncDescription

__description__ = Description(
	MainDescription('Описания плагина'),
	FuncDescription('команда', 'описание команды', parameters=('параметр1', 'параметр2'), prefixes=('/',)),
	FuncDescription('...', '...')
)

#MainDescription используется для описания плагина
#FuncDescription используется чтобы описать команду
```

Также, если вы делаете плагин с другими сторонними модулями(библиотеками), скорее всего у пользователя его не будет, по этому, чтобы обойти ошибки/баги стороной, нужно написать список:

```python
from loads import set_modules

# Делать перед другими импортами
set_modules(['some_module1', 'some_module2'])
# Другие импорты...

import some_module1
import some_module2
```

Или же, вы можете создать файл в вашем плагине `__modules__.txt` и вписать библиотеку вместо предыдущего примера.

```txt
library1
library2
...
```

### Сторонние плагины

Вы можете посмотреть список установленных плагинов

```python
from loads import Data

print(Data.get_name_plugins()) # ['plugin_name1', 'plugin_name2', '...']
```

## Файл конфигураций

Чтобы скрипт успешно взял ваши данные, строго следуйте инструкции.
В корне папки создайте файл `config.ini`.
Зайдите и введите в файл это:

```bash
api_id = 12345679
api_hash = "..."
phone_number = 7123456
password = "...."
send_message = false
```

В `api_hash` и `password` нужно, чтобы справа и слева были двойные кавычки ".
`password` не обязательно указывать, но рекомендую оставить кавычки пустыми, на пример: password = ""
Параметр `send_message`(быстрее для запуска бота) отвечает за отправку сообщение при старте и когда есть обновление.Допустимые параметры: `true` или `false`

## Скачивания плагина и запуск

Чтобы скачать плагин, вам нужно **запустить юзер бота, т.е файл run.py.**

Обязательно введите данные от вашего аккаунта в файл config.ini

О том, как получить **api_id и api_hash** вы можете узнать [в этой статье](https://teletype.in/@sakurahost/GetApi)

Чтобы установить плагин, отправьте сообщение в каком то из чатов: /dwlmd {ссылка на зип файл из гит хаба}
