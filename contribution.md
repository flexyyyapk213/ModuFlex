На данный момент проект ещё сырой, но он полон надежд и успехов

## Начало

Начнём с того, что создадим папку в папке plugins, название любое(главное, чтобы без пробелов).

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
Если декораторы не подходят под ваше требования, допустим нужно отслеживать присланные контакты, воспользуйтесь декоратором `@all_func()` и сортируйте сообщения под ваши нужды.
Не рекомендую использовать несколько раз `@all_func()` но это не сломает код, просто не корректно в плане оптимизации.

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

## Модули

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

Подробнее об `FuncDescription`:

- !`command`: название команды(без префикса)
- !`description`: описание команды(Старайтесь не делать их слишком длинными)
- `hyphen`: разделитель между названием команды и описанием
- `prefixes`: префиксы у команды
- `parameters`: параметры у команды

! - обязательные параметры.

### Библиотеки

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

Вы можете посмотреть список установленных плагинов.

```python
from loads import Data

print(Data.get_name_plugins()) # ['plugin_name1', 'plugin_name2', '...']
```

Вы можете использовать общий файл конфигураций, вместо того, чтобы создавать свой.

```python
from loads import Data

print(Data.get_config('PluginName')) # Если это ваш плагин, вы сможете изменить там данные и изменения внесутся в файл.Если конфига нету, то выведет None и автоматически создаться, что позволит управлять данными

Data.get_config('PluginName').update({"test": "test"})

print(Data.get_config('PluginName')["test"]) # test

Data.get_config('PluginName')["test"] = "test2"
# Функционал примерно как у dict

Data.get_config()['PluginName']["test"] = "test3" # Данные не внесутся в файл автоматически
```

Фишка вся в том, что вызвав `Data.get_config('PluginName')` не в плагине `PluginName`, изменения не смогут коснуться файла.

## Файл конфигураций

Чтобы скрипт корректно работал с Вашими данными, необходимо создать файл настроек:

1. В корневой папке проекта создайте файл **`config.ini`**.
2. Откройте его и вставьте следующий шаблон:

```ini
api_id = 12345679
api_hash = "..."
phone_number = 7123456
password = "..."
send_message = false
ask_downloads = false
one_download_libs = false
```

### Обязательные параметры

- **`api_id`** – Ваш уникальный идентификатор (выдаётся в [my.telegram.org](https://my.telegram.org)).
- **`api_hash`** – Ваш уникальный хэш (всегда указывайте в двойных кавычках `"`).
- **`phone_number`** – номер телефона, привязанный к аккаунту Telegram.

### Дополнительные параметры

- **`password`** – пароль для двухфакторной аутентификации.

  - Можно оставить пустым, но кавычки `" "` должны быть обязательно.
  - Пример:

    ```ini
    password = ""
    ```

### Логические параметры (true / false)

- **`send_message`** – отправлять ли сообщение при старте и при обновлении.

  - `true` – отправлять (бот запускается быстрее).
  - `false` – не отправлять.

- **`ask_downloads`** – спрашивать ли подтверждение при установке сторонних библиотек.

  - `true` – не спрашивать (автоматически устанавливает; быстрее запуск, но возможны нюансы).
  - `false` – спрашивать.

- **`one_download_libs`** – когда устанавливать/обновлять сторонние библиотеки для модулей.

  - `true` – только при установке модуля (не устанавливать/обновлять при запуске).
  - `false` – устанавливать при запуске.

## Скачивания плагина и запуск

Чтобы скачать плагин, вам нужно **запустить юзер бота, т.е файл run.py.**

Обязательно введите данные от вашего аккаунта в файл config.ini

О том, как получить **api_id и api_hash** вы можете узнать [в этой статье](https://teletype.in/@sakurahost/GetApi)

Чтобы установить плагин, отправьте сообщение в каком то из чатов: /dwlmd {ссылка на зип файл из гит хаба}

### Откат версии

Чтобы сделать откат версии, нужно запустить файл `version_rollback.py`

```bash
python version_rollback.py
```

Введите версию(пример: 0.0.9b2 или 0.0.8) и ждите завершения отката.
