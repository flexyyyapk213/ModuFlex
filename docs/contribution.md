# Главная

Данная страница рассказывает о всех возможностей ModuFlex. Contribution играет роль как "своя википедия". Он показывает не только, как вызвать функцию, а как настроить конкретный файл, сделать свой плагин и другие вещи, которые были добавлены во всех и последующих версиях.

Это изменённая версия Contribution, которая стала намного удобней и понятней. Причина, по которой Contribution была изменена, так это то, что текст был буквально захламлён и во всех заголовках был разный стиль.

!!! note "Примечание"

    В самом внизу (раздел: [Документация по API](#documentation-api)) подробно расписаны функции/классы: от откуда импортировать до параметров и их описание.

## Создание плагина

Чтобы создать свой плагин, следуйте этим шагам:

1. Перейдите в папку `plugins` в корне папки скрипта.

2. Создайте папку с названием вашего плагина (без пробелов).

3. Создайте файл с названием `__init__.py`.

Внутри `__init__.py` вы можете приступать к написанию вашего плагина.

Пример, как должна выглядеть структура папок:

```
ModuFlex\
├── ...
├── botvenv\
├── temp\
└── plugins\
    ├── StartedPack\
    ├── AnimationPack\
    └── YourNamePack\       # Ваш плагин в виде папки
        └── __init__.py     # Стартовый файл
```

!!! note "Примечание"

    Можно не придерживаться к единому стилю именований плагинов.

!!! tip "Совет"

    Подробнее о том, как создать свой собственный плагин, вы можете почитать [здесь](how_to_create_your_own_plugin.md).

!!! warning "Важно"

    Перед выпуском плагина, обязательно прочитайте разделы:

## Описание {#description}

Чтобы пользователь смог ознакомиться с вашими командами, нужно сделать описание плагина.

Для начала, импортируем нужные классы:

```python
from loads import (
    Description,       # Класс, чтобы описать плагин
    MainDescription,   # Описание плагина (для чего он и прочее)
    FuncDescription    # Описание команды
)
```

Создадим переменную с именем `__description__`:

```python
__description__ = Description(
    MainDescription('Описание плагина.'),
    FuncDescription('test', 'Тестовая команда.', prefixes=('/', '!', '.'), parameters=('тест',))
)
```

Первый параметр в классе `FuncDescription` - `command`, отвечает за название команды, второй параметр `description` отвечает за описание команды. Параметр `prefixes` отвечает за префикс команды, `parameters` отвечает за параметры команды (просто визуал, разбивать команды на параметры нужно вручную).

## Установка библиотек

При работе с вашим плагинов скорее всего вы воспользуетесь библиотеками, которого у пользователя не будет. По этому в ModuFlex есть два встроенных способа, чтобы установить эти самые библиотеки. Первый устарел, второй современный:

> Первый способ

```python
from loads import set_modules

set_modules(['library1', 'library2', '...'])

import library1
import library2
...
```

Мы импортируем функцию `set_modules` и сразу же передаём список строк с названием библиотек.

Хоть первый способ и устарел, но его по прежне можно использовать. Устарел он потому, что есть:

> Второй способ

Создайте в корне плагина файл `__modules__.txt`, впишите библиотеки с новой строки:

```
library1
library2
...
```

Пример, где должен лежать файл `__modules__.txt`:

```
PluginName\
├── __init__.py
├── __modules__.txt
└── ...
```

## Функция инициализации при старте

В `__init__.py` файле можно разместить синхронную функцию `def initialiazation(app: pyrogram.client.Client)`, которая вызовиться автоматически передав первый параметр объект `pyrogram.client.Client`.

Пример:

```python
from pyrogram.client import Client

def initialization(app: Client):
    app.send_message(...)
```

## Работа с общей конфигурацией

Вы можете воспользоваться удобной системой конфигурации, встроенной в классе `Data`. Такая конфигурация удобная тем, что не нужно вручную создавать файл, проверять есть ли она и куча-куча нюансов. Всем этим занимается класс `Data` и удобными фишками `MappingConfig`. Но, имейте ввиду, что эта система конфигураций не подходит для частых изменений данных с большим объёмом. Для этого придётся создавать файл вручную.

### Чтения конфигурации

Начнём с того, что получим конфиг всех плагинов (Не переживайте, это только для чтения):

```python
from loads import Data

configs = Data.get_config() # Ничего не указываем. Возвращается только копия конфига (то есть объект dict), изменить значения получится, но оно сохраниться

print(configs['ModuFlex']) # Выводим все ключи и значения псевдо-плагина ModuFlex

configs['ModuFlex']['new_key'] = 1 # Добавляем новый ключ и значение, но, так как это копия, изменения не сохраняться
```

### Собственная конфигурация

Теперь получим нашу конфигурацию (пока что пустую):

```python
from loads import Data

my_config = Data.get_config(__file__) # Можно написать 'MyConfigName' (то есть название вашего плагина), но так удобней

print(my_config) # Выведется пустой словарь

my_config['new_key'] = 1

print(my_config) # Увидим ключ new_key со значением 1
```

С классом `MappingConfig` можно работать (почти) как с обычным `dict`. Там можно получать значения, добавлять и удалять, там присутствуют базовые вещи для работы со словарём.

### Чужие конфигурации

Можно также отдельно посмотреть конфиги другого плагина:

```python
other_config = Data.get_config('AIFuncs') # Всё также, только для чтения

print(other_config['history_len'])
```

## Сторонние плагины

Можно получить список всех плагинов, которые работают:

```python
from loads import Data

print(Data.get_plugins())
```

## Регистрация событий

Чтобы плагин мог реагировать на определённые события в чатах, нужно воспользоваться декораторами из файла `loads.py`. Существует два способа оформления регистрации событий:

### Регистрация через функцию

```python
from loads import func                 # Декоратор
from pyrogram import filters, types    # Фильтры и типы
from pyrogram.client import Client     # Для аннотации

@func(filters.command('test', prefixes=['/', '!', '.']) & filters.me)
async def test_command(app: Client, message: types.Message): # Можно регистрировать синхронную функцию
    print(message.text)
```

Здесь используется `filters.command` для фильтрации сообщения только с командой и `filters.me` чтобы фильтровало свои сообщения. Если всё подойдёт под фильтры, то вызовется зарегистрированная функция передав первых два параметра: `Client` - объект класса, для взаимодействия с аккаунтом и `Message` - объект класса сообщения, для взаимодействия с сообщением.

Помимо декоратора `func` существует несколько похожих: `chat_func`, `private_func`, `channel_func` и `all_func` - все они устарели и повторяют почти такой же функционал, за исключением того, что в них встроены фильтры.

### Регистрация через метод в классе

```python
from loads import Module, func
from pyrogram import filters, types    # Фильтры и типы
from pyrogram.client import Client     # Для аннотации

class Example(Module):
    @func(filters.command('test', prefixes=['/', '!', '.']) & filters.me)
    async def test_command(self, app: Client, message: types.Message): # Можно регистрировать синхронную функцию
        print(message.text)
```

Здесь импортируется класс `Module` который используется только для наследования. Дальше всё похоже как и с функцией, только первый параметр в `test_command` это `self`.

#### Получение объекта Client внутри класса-наследника Module

Во многих случаях может понадобиться доступ к объекту `Client` внутри методов класса-наследника `Module`. Однако, объект `Client` не передаётся напрямую в конструктор (`__init__`), если не использовать инициализацию через отдельную функцию или декоратор. Ранее обойти это ограничение было сложно из-за архитектуры `main.py`.

Начиная с версии `0.1.0`, появилась более удобная возможность получить объект `Client` без дополнительных костылей. Для этого в своём классе необходимо реализовать вспомогательный метод `__call__`. Пример:

```python
from loads import func, Module
from pyrogram import filters
from pyrogram.client import Client

class Example(Module):
    @func(filters.command('test') & filters.me)
    def test_command(self, app, message):
        ...

    def __call__(self, *args, **kwargs):  # вспомогательный метод
        for arg in args:
            if isinstance(arg, Client):
                ... # Здесь вы получаете объект Client
```

Этот вспомогательный метод будет вызван при регистрации функций, классов и методов, т.е. инициализированный объект класса вызовется как функция и получит в аргументах объект `Client`. Таким образом, здесь вы можете получить доступ к текущему клиенту без необходимости дополнительных параметров.

Можно также не использовать `*args` и `**kwargs`, если дополнительное взаимодействие с этим методом вам не нужно.

Обратите внимание: этот метод будет вызван после инициализации класса, но до момента полной готовности юзербота. Пользовательские команды не смогут быть вызваны раньше, чем выполнится этот метод.

### Веб Интерфейс

Начиная с версии `0.1.0b2`, появилась возможность создавать вспомогательный веб-интерфейс для плагинов.

Данный интерфейс позволяет подключать HTML-шаблоны, CSS, JavaScript и медея.

Чтобы подключится к локальному сайту, обычно нужно перейти к 127.0.0.1:1205, а чтобы перейти к интерфейсу плагина, нужно добавить в поле адреса `ИмяПлагина/`.

#### Структура папок

В корне вашего плагина необходимо создать две папки:

```
templates/
static/
```

- **templates** — хранение HTML-шаблонов
- **static** — хранение CSS, JavaScript и медея

> Папку `static` необходимо создавать **всегда**, даже если в ней не будет файлов.

##### Подпапка в templates (обязательно)

Внутри папки `templates` **обязательно** создайте подпапку с именем вашего плагина:

```
templates/
└─ my_plugin/
    └─ index.html
```

Это необходимо для предотвращения конфликтов между плагинами.

##### Почему это важно

Фреймворк **Quart** (форк Flask) использует общее пространство шаблонов. Все HTML-файлы из разных плагинов добавляются в единый список поиска.

Если два плагина содержат шаблон с одинаковым именем, Quart может отобразить не тот файл.

Использование подпапки с именем плагина полностью решает эту проблему.

#### Подключение CSS / JS в HTML

Для корректного подключения файлов из папки `static` используйте функцию `url_for`.

Пример подключения CSS и JS(и для остального) в `<head>` HTML-файла:

```html
<link
  rel="stylesheet"
  href="{{ url_for('ИмяПлагина.static', filename='styles.css') }}"
/>
<script
  src="{{ url_for('ИмяПлагина.static', filename='script.js') }}"
  defer
></script>
```

Где:

- `ИмяПлагина` — имя вашего плагина
- `filename` — путь к файлу внутри папки `static`

Пример структуры папки `static`:

```
static/
├─ styles.css
├─ script.js
└─ image.png
```

> Создавать подпапку с именем плагина внутри `static` **не нужно**.

#### Создание маршрута (route)

Для обработки запросов необходимо создать маршрут с помощью декоратора `route` из `loads`.

##### Вариант с классом

```python
from loads import Module, route

class Example(Module):
    @route('/')
    async def test(self):
        pass
```

##### Вариант с функцией

```python
from loads import route

@route('/')
async def test():
    pass
```

> Декоратор route имеет точно такие же параметры как и в обычном Quart/Flask

#### Рендер HTML-шаблона

Для возврата HTML-страницы используйте `render_template` из Quart.

Важно: путь к шаблону **всегда указывается с именем плагина**.

```python
from quart import render_template
from loads import route

@route('/')
async def test():
    return await render_template('ИмяПлагина/index.html')
```

Это связано с тем, что Quart использует глобальное пространство шаблонов.

#### Особенности Quart

Quart является асинхронным фреймворком:

- `async def` функции выполняются напрямую
- синхронные функции поддерживаются, но запускаются в отдельном потоке
- `render_template` и прочие функции имеет асинхронную версию и должен вызываться с `await`

В будущем планируется упростить работу с шаблонами, чтобы не указывать имя плагина в пути вручную.

## Песочница и почему это важно для разработчиков

С обновлении `0.1.0` добавлена возможность выполнять код в песочнице, что сделала команду `/code` безопасной для выполнения подозрительного Python кода.

- Плюсы:
- - Код выполняется в изолированной среде выполнения Python на основе WebAssembly (WASM).
- - Вам не смогут удалить или прочитать важные данные и не сольют ваши данные в интернет(к примеру IP адрес).
- Минусы:
- - Заблокирован доступ к интернету, а также отсутствует доступ к файловой системе вне специально отведённых "песочниц". Это означает, что нельзя скачивать данные из интернета и работать с файлами на диске.
- - Не поддерживаются многие сторонние библиотеки, которые не входят в стандартную поставку Python(Но, можно указать в функции параметры globals и locals переменные). Если вашему коду необходимы сетевые запросы или работа с внешними файлами, он не сможет выполняться в песочнице.
- - Ограничение на выполнения работы.Допустим, если вы напишите бесконечный цикл, то через некоторое время выполнения скрипта завершиться из за ограничений по выделенным ресурсам(времени, памяти, числа инструкций).

Использования песочницы очень важно, так как это безопасно для пользователей.

Пример его применения:

```python
from loads import sandbox_exec, func

# ... Декоратор
def running_code(_, __):
    result = sandbox_exec("print('Hello world!')")
    # sandbox_exec("print(x)", _globals={"x": 10})
    print(f'Консоль: {result["output"]}')
```

Импортируем из `loads` функцию `sandbox_exec` который выполняет предоставленный код с глобальными и/или локальными переменными.

`sandbox_exec` возвращает словарь, в котором хранится информация о выполнении кода.

## Файл manifest плагина

Если вы собираетесь выпускать ваш плагин в общий доступ для скачивания, вам нужно сделать файл в корне плагина - `manifest.json`. Это обязательный файл с информацией о вашем плагине. Без него пользователи не смогут установить ваш плагин через автоматическую загрузку.

Вот пример содержимого файла:

```json
{
  "name": "StartedPack",
  "version": "1.0",
  "mf_version": ">=0.1.0b2",
  "description": "Краткое описание предназначения плагина или его нововведений (до ~4096 символов, поддерживается markdown формат Telegram).",
  "author": "flexyyy",
  "tags": ["main"],
  "repository": "empty link"
}
```

Подробнее о ключах и их значения:

- **`name`** - Имя вашего плагина.
- **`version`** - Версия вашего плагина (При обновлении, всегда повышайте значение).
- **`mf_version`** - Диапазон версии совместимая с ModuFlex.
- **`description`** - Описание плагина. Поддерживает форматирование markdown Telegram.
- **`author`** - Автор плагина.
- **`tags`** - Ключевые слова или категории, по которым можно найти ваш плагин. Рекомендуется использовать только одно слово и чем больше тэгов связанные с плагином тем лучше для поиска(которого пока нет xD).
- **`repository`** - Ссылка на ваш репозиторий или страница вашего плагина.

## Файл конфигурации

Для того, чтобы юзербот заработал, нужно создать файл `config.ini` в корне папки ModuFlex, вставить свои данные от аккаунта Telegram и тогда запустить. Иначе ничего не получиться.

Вставьте такой шаблон в файл:

```ini
api_id = 12345679
api_hash = "..."
phone_number = 7123456
password = "..."
send_message = true
one_download_libs = true
use_botvenv = true
```

Замените **`api_id`**, **`api_hash`**, **`phone_number`** и/или `passowrd` на ваши данные от аккаунта.

Подробнее о параметрах:

### Обязательные параметры

- **`api_id`** – Ваш уникальный идентификатор (выдаётся в [my.telegram.org](https://my.telegram.org)).
- **`api_hash`** – Ваш уникальный хэш (всегда указывайте в двойных кавычках `"` как показано в шаблоне) (выдаётся в [my.telegram.org](https://my.telegram.org)).
- **`phone_number`** – номер телефона, привязанный к аккаунту Telegram.

### Дополнительные параметры

- **`password`** – пароль для двухфакторной аутентификации.
- - Можно оставить пустым, но кавычки `" "` должны быть обязательно.
- - Пример:
  ```ini
  password = ""
  ```
- **`timeout_download_lib`** – отвечает за ограничение по времени (в секундах) скачивания библиотеки для плагина. Следует указывать только целое корректное число, по умолчанию - 120 (секунд).
- - Рядом с числом ничего лишнего быть не должно.
- - Пример:
  ```ini
  timeout_download_lib = 90
  ```

### Логические параметры (true / false)

- **`send_message`** – отправлять ли сообщение в избранное при старте и при обновлении.
  - - `true` – отправлять (бот запускается быстрее).
  - - `false` – не отправлять(По умолчанию).
  - - Пример:
  ```ini
  send_message = true
  ```
- **`ask_downloads`** – спрашивать ли подтверждение при установке сторонних библиотек.
- - `true` – не спрашивать (автоматически устанавливает; быстрее запуск, но возможны нюансы).
- - `false` – спрашивать(По умолчанию).
- **`one_download_libs`** – когда устанавливать/обновлять сторонние библиотеки для модулей.
- - `true` – только при установке модуля (не обновлять при запуске)(По умолчанию).
- - `false` – устанавливать при запуске.
- **`use_botvenv`** – использовать ли отдельное виртуальное окружение.
- - `true` – использовать(По умолчанию)
- - `false` – не использовать
- **`check_for_update`** – Проверять ли обновления с интервалом.
- - `true` – Да(По умолчанию.С интервалом в 10 минут.Когда впервые обнаружится обновление, проверка отключается).
- - `false` – Нет.
- **`experimental`** - Использовать ли Экспериментальные функции.
- - `true` - Да.
- - `false` - Нет(По умолчанию).

## Откат версии

Если в новых версиях вы столкнулись с критичной ошибкой, из за которой вы не можете запустить юзербота, на такой случай был создан файл `version_rollback.py`.

Перейдите в корень папки ModuFlex, запустите файл `version_rollback.py`:

### На Windows

```bash
botvenv\Scripts\python.exe version_rollback.py
```

### На Linux

```bash
botvenv\bin\python version_rollback.py
```

### Без botvenv

Если у вас нету или не работает botvenv:

```bash
python version_rollback.py
```

Если у вас не вышло, скорее всего, у вас не имеются нужные библиотеки. Введите это и попробуйте снова:

```bash
pip install requests alive-progress
```

### Последний этап

У вас спросят версию:

```
Введите версию(без префикса v):
```

Введите версию и ожидайте конца установки.

## Запуск {#run-userbot}

Чтобы запустить юзербота, нужно ввести в консоль следующее:

```bash
python run.py
```

Если вы до этого ввели ваши данные в файл `config.ini`, то у вас должен заработать юзербот. Если нет, то [обращайтесь в телеграм канал разработчика](https://t.me/flexyyyapk), вам там помогут решить проблему.

## Установка плагинов

Перед тем, как скачивать, [запустите бота](#run-userbot).

В любом чате отправьте:

```
/dwplg <ссылка на гит хаб плагина>
```

Всё **должно** пройти нормально и отправится сообщение с успешной установкой.

## Документация по API

<style>
    .type {
        font-family: monospace;
        border: 1px solid rgba(0, 0, 0, 0);
        border-radius: 5px;
        padding: 1px;
        background-color: rgba(127, 127, 127, 0.16)
    }

    .parameter {
        color:rgb(66, 123, 245);
    }

    .typed {
        color: #42d1f5;
    }

    .moduflex {
        color:rgb(4, 106, 131);
    }

    .function {
        color: rgb(121, 57, 163)
    }

    .warning {
        color: #ebb134;
    }
</style>

<span class="type"><span class="moduflex">ModuFlex</span>.handling_plugins.<span class="function">handling_plugins</span>() -> <span class="typed">None</span></span>

- Описание: Обрабатывает плагины, проходясь по папке `plugins`. Записывает плагины в кэш `Data` и считывает файлы `__modules__.txt`, `manifest.json`, переменную `__description__` и т.д. <span class="warning">Не рекомендуется вызывать, может сломать всё.</span>
- Первое появление: [ModuFlex v0.0.1 2024-12-29](blog/posts/2024-12-29.md).
- Параметры: отсутствуют.

<span class="type"><span class="moduflex">ModuFlex</span>.handling_plugins.<span class="function">handle_plugin</span>(<span class="parameter">pack_name: </span><span class="typed">str</span>) -> <span class="typed">None</span></span>

- Описание: Обрабатывает плагин, который появился при его установке. Записывает плагин в кэш `Data` и считывает файлы `__modules__.txt`, `manifest.json`, переменную `__description__` и т.д. <span class="warning">Не рекомендуется вызывать, может сломать всё.</span>
- Первое появление: [ModuFlex v0.0.4 2025-01-31](blog/posts/2025-01-31.md).
- Параметры:
- - **`pack_name: str`**: Имя плагина.

<span class="type"><span class="moduflex">ModuFlex</span>.handling_plugins.<span class="function">update_command_information</span>(<span class="parameter">description: </span><span class="typed">Description</span>, <span class="parameter">plugin_name: </span><span class="typed">str</span>) -> <span class="typed">None</span></span>

- Описание: Функция для обновления информвции о плагинах, который собрал декораторы типа `func`. <span class="warning">Не рекомендуется вызывать, может сломать всё.</span>
- Первое появление: [ModuFlex v0.1.0b1 2025-12-27](blog/posts/2025-12-27.md).
- Параметры:
- - **`description`**: Описание плагина
- - **`plugin_name`**: Имя плагина

<span class="type"><span class="moduflex">ModuFlex</span>.loads.<span class="function">ScriptState</span></span>

- Описание: `Enum` класс для обозначения состояния работы юзербота.
- Первое появляение: [ModuFlex v0.1.0b1 2025-12-27](blog/posts/2025-12-27.md).
- Поля:
- - **`started`**: Юзербот запущен.
- - **`restart`**: Юзербот перезапускается.
- - **`error`**: Юзербот словил ошибку во время работы.
- - **`exit`**: Юзербот принудительно завершается.

<span class="type"><span class="moduflex">ModuFlex</span>.loads.<span class="function">MappingConfig</span>(self, <span class="parameter">plugin_name: </span><span class="typed">str</span>, <span class="parameter">keys: </span><span class="typed">List</span>[<span class="typed">str</span>])</span>

- Описание: Класс для управления конфигурации.
- Первое появление: [ModuFlex v0.0.9b1 2025-09-10](blog/posts/2025-09-10.md).
- Параметры:
- - **`plugin_name`**: Имя плагина.
- - **`keys`**: Список ключей, путь к словарю.
- Методы:
- - <span class="type"><span class="function">update</span>(self, <span class="parameter">\_dict: </span><span class="typed">Dict</span>) -> <span class="typed">None</span></span>: Обновляет/добавляет ключи текущего словаря и сохраняет изменения в `configuration.json`.
- - <span class="type"><span class="function">keys</span>(self) -> <span class="typed">List</span>[<span class="typed">Any</span>]</span>: Возвращает ключи текущего словаря конфигурации.
- - <span class="type"><span class="function">values</span>(self) -> <span class="typed">List</span>[<span class="typed">Any</span>]</span>: Возвращает значения текущего словаря конфигурации.
- - <span class="type"><span class="function">items</span>(self) -> <span class="typed">Iterable</span></span>: Возвращает пары `ключ-значение` текущего словаря конфигурации.
- - <span class="type"><span class="function">clear</span>(self) -> <span class="typed">None</span></span>: Очищает текущий словарь конфигурации и сохраняет изменения.
- - <span class="type"><span class="function">popitem</span>(self) -> <span class="typed">Tuple</span></span>: Удаляет и возвращает одну пару `ключ-значение`, затем сохраняет изменения.
- - <span class="type"><span class="function">pop</span>(self, <span class="parameter">key</span>) -> <span class="typed">Any</span></span>: Удаляет ключ, возвращает его значение и сохраняет изменения.
- - <span class="type"><span class="function">copy</span>(self) -> <span class="typed">Dict</span></span>: Возвращает копию текущего словаря конфигурации.
- - <span class="type"><span class="function">get</span>(self, <span class="parameter">key</span>, <span class="parameter">default=None</span>) -> <span class="typed">Union</span>[<span class="typed">Dict</span>, <span class="typed">Any</span>]</span>: Возвращает вложенный `MappingConfig` по ключу или `default`, если ключ отсутствует.
- - <span class="type"><span class="function">\_save</span>(self) -> <span class="typed">None</span></span>: Сохраняет текущее состояние `Data.config` в `configuration.json`.
- - <span class="type"><span class="function">setdefault</span>(self, <span class="parameter">\_dict: </span><span class="typed">Dict</span>) -> <span class="typed">None</span></span>: Добавляет отсутствующие поля из словаря значений по умолчанию.

<span class="type"><span class="moduflex">ModuFlex</span>.loads.<span class="function">Data</span></span>

- Описание: Класс-центр хранения плагинов.
- Первое появление: [ModuFlex v0.0.1 2024-12-29](blog/posts/2024-12-29.md).
- Поля:
- - **`cache`**: Кэш для хранения плагинов.
- - **`description`**: Описания плагинов.
- - **`initializations`**: Список функций инициализаций плагинов.
- - **`config`**: Конфигурация плагинов.
- - **`count_commands`**: Кол-во названий команд плагинов.
- - **`ask_downloads`**: Флаг, спрашивать ли установку.
- - **`skip_downloads`**: Флаг, пропуск установки.
- - **`one_download_libs`**: Флаг, единоразовая установка библиотек.
- - **`failed_modules`**: Кол-во неудачных запусков плагинов.
- - **`check_for_update`**: Флаг, проверять ли обновление.
- - **`timeout_download_lib`**: Таймаут скачивания библиотеки.
- - **`experimental`**: Флаг, экспериментальный запуск.
- - **`sandbox_executor`**: Класс песочницы.
- - **`DEFAULT_MODUFLEX_CONFIG`**: Словарь для конфигурации по умолчанию.
- Методы:
- - <span class="type"><span class="function">get_name_plugins</span>() -> <span class="typed">List</span>[<span class="typed">str</span>]</span>: Метод, который возвращает список запущенных плагинов.
- - <span class="type"><span class="function">get_config</span>() -> <span class="typed">Union</span>[<span class="typed">MappingConfig</span>, <span class="typed">Dict</span>]</span>: Возвращает либо копию конфига или класс, в котором можно изменять значения с автоматическим сохранением.

<span class="type"><span class="moduflex">ModuFlex</span>.loads.<span class="function">Module</span></span>

- Описание: Класс, который используется только для наследования, регистрируя класс-наследник.
- Первое появление: [ModuFlex v0.1.0b2 2026-01-30](blog/posts/2026-01-30.md).

<span class="type"><span class="moduflex">ModuFlex</span>.loads.<span class="function">chatType</span></span>

- Описание: `Enum` класс, обозначающий тип чата/канала.
- Первое появление: [ModuFlex v0.0.7.1 2025-07-15](blog/posts/2025-07-15.md).
- Поля:
- - `DEFAULT`: Все чаты.
- - `PRIVATE`: Приватные чаты.
- - `CHAT`: Группа.
- - `CHANNEL`: Канал.
- - `ALL`: Все чаты.

<span class="type"><span class="moduflex">ModuFlex</span>.loads.<span class="function">Description</span>(self, <span class="parameter">main_description: </span><span class="typed">MainDescription</span>, <span style="color: #ff2e2e">\*</span><span class="parameter">args: </span><span class="typed">FuncDescription</span>)</span>

- Описание: Класс для описания плагина и всех его команд. Подробнее — в разделе [Описание](#description).
- Первое появление: [ModuFlex v0.0.1 2024-12-29](blog/posts/2024-12-29.md).
- Параметры:
- - **`main_description`**: Главное описание плагина.
- - **`args`**: Описания команд (`FuncDescription`).

<span class="type"><span class="moduflex">ModuFlex</span>.loads.<span class="function">MainDescription</span>(self, <span class="parameter">description: </span><span class="typed">str</span>)</span>

- Описание: Главное описание плагина (используется в help и списке плагинов).
- Первое появление: [ModuFlex v0.0.1 2024-12-29](blog/posts/2024-12-29.md).
- Параметры:
- - **`description`**: Текст описания плагина.

<span class="type"><span class="moduflex">ModuFlex</span>.loads.<span class="function">FuncDescription</span>(self, <span class="parameter">command: </span><span class="typed">str</span>, <span class="parameter">description: </span><span class="typed">str</span>=<span class="typed">None</span>, <span class="parameter">hyphen: </span><span class="typed">str</span>=<span class="typed">' - '</span>, <span class="parameter">prefixes: </span><span class="typed">Union</span>[<span class="typed">Tuple</span>, <span class="typed">List</span>]=<span class="typed">None</span>, <span class="parameter">parameters: </span><span class="typed">Union</span>[<span class="typed">Tuple</span>, <span class="typed">List</span>]=<span class="typed">None</span>, <span class="parameter">parameters_style: </span><span class="typed">Union</span>[<span class="typed">Tuple</span>, <span class="typed">List</span>, <span class="typed">str</span>]=<span class="typed">None</span>)</span>

- Описание: Описание конкретной команды плагина.
- Первое появление: [ModuFlex v0.0.1 2024-12-29](blog/posts/2024-12-29.md).
- Параметры:
- - **`command`**: Название (ключ) команды.
- - **`description`**: Описание команды.
- - **`hyphen`**: Разделитель между командой и описанием.
- - **`prefixes`**: Допустимые префиксы команды (например, `['/', '!']`).
- - **`parameters`**: Параметры команды.
- - **`parameters_style`**: Символы скобок для параметров.

<span class="type"><span class="moduflex">ModuFlex</span>.loads.<span class="function">func</span>(<span class="parameter">\_filters: </span><span class="typed">filters</span>, <span class="parameter">description: </span><span class="typed">str</span>=<span class="typed">None</span>) -> <span class="typed">Callable</span></span>

- Описание: Декоратор для регистрации обработчика сообщений (команды).
- Первое появление: [ModuFlex v0.0.1 2024-12-29](blog/posts/2024-12-29.md).
- Параметры:
- - **`_filters`**: Фильтры pyrogram для отбора сообщений.
- - **`description`**: Описание команды.

<span class="type"><span class="moduflex">ModuFlex</span>.loads.<span class="function">private_func</span>(<span class="parameter">\_filters: </span><span class="typed">filters</span>=<span class="typed">None</span>, <span class="parameter">description: </span><span class="typed">str</span>=<span class="typed">'Описание отсутствует.'</span>) -> <span class="typed">Callable</span></span>

- Описание: Декоратор для обработчиков в личных сообщениях. <span class="warning">Устарел, используйте `func`.</span>
- Первое появление: [ModuFlex v0.0.3 2025-01-27](blog/posts/2025-01-27.md).
- Параметры:
- - **`_filters`**: Фильтры pyrogram (или `None`).
- - **`description`**: Описание команды.

<span class="type"><span class="moduflex">ModuFlex</span>.loads.<span class="function">chat_func</span>(<span class="parameter">\_filters: </span><span class="typed">filters</span>=<span class="typed">None</span>, <span class="parameter">description: </span><span class="typed">str</span>=<span class="typed">'Описание отсутствует.'</span>) -> <span class="typed">Callable</span></span>

- Описание: Декоратор для обработчиков в групповых чатах. <span class="warning">Устарел, используйте `func`.</span>
- Первое появление: [ModuFlex v0.0.3 2025-01-27](blog/posts/2025-01-27.md).
- Параметры:
- - **`_filters`**: Фильтры pyrogram (или `None`).
- - **`description`**: Описание команды.

<span class="type"><span class="moduflex">ModuFlex</span>.loads.<span class="function">channel_func</span>(<span class="parameter">\_filters: </span><span class="typed">filters</span>=<span class="typed">None</span>, <span class="parameter">description: </span><span class="typed">str</span>=<span class="typed">'Описание отсутствует.'</span>) -> <span class="typed">Callable</span></span>

- Описание: Декоратор для обработчиков в каналах. <span class="warning">Устарел, используйте `func`.</span>
- Первое появление: [ModuFlex v0.0.3 2025-01-27](blog/posts/2025-01-27.md).
- Параметры:
- - **`_filters`**: Фильтры pyrogram (или `None`).
- - **`description`**: Описание команды.

<span class="type"><span class="moduflex">ModuFlex</span>.loads.<span class="function">all_func</span>(<span class="parameter">\_filters: </span><span class="typed">filters</span>=<span class="typed">None</span>, <span class="parameter">description: </span><span class="typed">str</span>=<span class="typed">'Описание отсутствует.'</span>) -> <span class="typed">Callable</span></span>

- Описание: Декоратор для обработчиков во всех типах чатов. <span class="warning">Устарел, используйте `func`.</span>
- Первое появление: [ModuFlex v0.0.3 2025-01-27](blog/posts/2025-01-27.md).
- Параметры:
- - **`_filters`**: Фильтры pyrogram (или `None`).
- - **`description`**: Описание команды.

<span class="type"><span class="moduflex">ModuFlex</span>.loads.<span class="function">route</span>(<span class="parameter">rule: </span><span class="typed">str</span>, <span style="color: #ff2e2e">\*\*</span><span class="parameter">options</span>) -> <span class="typed">Callable</span></span>

- Описание: Декоратор для регистрации HTTP-маршрута веб-интерфейса плагина. Параметры совпадают с `Blueprint.route` в Quart/Flask.
- Первое появление: [ModuFlex v0.1.0b2 2026-01-30](blog/posts/2026-01-30.md).
- Параметры:
- - **`rule`**: URL-маршрут (например, `'/settings'`).
- - **`options`**: Дополнительные параметры для `Blueprint.route`.

<span class="type"><span class="moduflex">ModuFlex</span>.loads.<span class="function">set_modules</span>(<span class="parameter">modules: </span><span class="typed">List</span>) -> <span class="typed">None</span></span>

- Описание: Указывает сторонние библиотеки для установки через pip. Вызывать до импорта этих библиотек. Для обычных случаев предпочтительнее `__modules__.txt`.
- Первое появление: [ModuFlex v0.0.4 2025-01-31](blog/posts/2025-01-31.md).
- Параметры:
- - **`modules`**: Список имён библиотек.

<span class="type"><span class="moduflex">ModuFlex</span>.loads.<span class="function">download_library</span>(<span class="parameter">libs: </span><span class="typed">List</span>[<span class="typed">str</span>]) -> <span class="typed">None</span></span>

- Описание: Устанавливает указанные библиотеки через pip с учётом флагов `Data.ask_downloads` и `Data.skip_downloads`.
- Первое появление: [ModuFlex v0.0.9b3 2025-09-29](blog/posts/2025-09-29.md).
- Параметры:
- - **`libs`**: Список имён библиотек для установки.

<span class="type"><span class="moduflex">ModuFlex</span>.loads.<span class="function">sandbox_exec</span>(<span class="parameter">code: </span><span class="typed">str</span>, <span class="parameter">\_globals: </span><span class="typed">Optional</span>[<span class="typed">Dict</span>]=<span class="typed">None</span>, <span class="parameter">\_locals: </span><span class="typed">Optional</span>[<span class="typed">Dict</span>]=<span class="typed">None</span>)</span>

- Описание: Выполняет Python-код в изолированной среде (WebAssembly) через `Data.sandbox_executor`.
- Первое появление: [ModuFlex v0.1.0 2026-04-09](blog/posts/2026-04-09.md).
- Параметры:
- - **`code`**: Исходный код Python.
- - **`_globals`**: Глобальные переменные среды выполнения.
- - **`_locals`**: Локальные переменные среды выполнения.

<span class="type"><span class="moduflex">ModuFlex</span>.main.<span class="function">check_updates</span>() -> <span class="typed">None</span></span>

- Описание: Функция для проверки обновления. <span class="warning">Не рекомендуется, скоро будет удалён.</span>.
- Первое появление: [ModuFlex v0.0.2 2025-01-01](blog/posts/2025-01-01.md).
- Параметры: отсутствуют.

<span class="type"><span class="moduflex">ModuFlex</span>.main.<span class="function">handling_updates</span>() -> <span class="typed">None</span></span>

- Описание: Обработка плагинов в кэше при первом запуске. <span class="warning">Не рекомендуется, скоро будет удалён.</span>.
- Первое появление: [ModuFlex v0.0.1 2024-12-29](blog/posts/2024-12-29.md).
- Параметры: отсутствуют.

<span class="type"><span class="moduflex">ModuFlex</span>.main.<span class="function">help</span>(<span class="parameter">\_</span>, <span class="parameter">msg: </span><span class="typed">types.Message</span>) -> <span class="typed">None</span></span>

- Описание: Зарегистрированная функция, которая показывает навигацию по плагинам и их командам.
- Первое появление: [ModuFlex v0.0.1](blog/posts/2024-12-29.md)~[0.0.3](blog/posts/2025-01-27.md) [2024-12-29](blog/posts/2024-12-29.md)~[2025-01-27](blog/posts/2025-01-27.md).
- Параметры:
- - **`_`**: Экземпляр `pyrogram.client.Client` который не используется.
- - **`msg`**: `types.Message` - сообщение.

<span class="type"><span class="moduflex">ModuFlex</span>.main.<span class="function">download_module</span>(<span class="parameter">app: </span><span class="typed">Client</span>, <span class="parameter">msg: </span><span class="typed">types.Message</span>)</span>

- Описание: Обработчик команды `dwplg` - скачивает и устанавливает плагин с GitHub по `manifest.json`. Проверяет совместимость с версией ModuFlex и наличие обновления.
- Первое появление: [ModuFlex v0.0.1 2024-12-29](blog/posts/2024-12-29.md) (как `dwlmd`), переименовано в [v0.1.0b3 2026-03-03](blog/posts/2026-03-03.md).
- Параметры:
- - **`app`**: Экземпляр `pyrogram.Client`.
- - **`msg`**: Сообщение с командой.

<span class="type"><span class="moduflex">ModuFlex</span>.main.<span class="function">old_download_module</span>(<span class="parameter">app: </span><span class="typed">Client</span>, <span class="parameter">msg: </span><span class="typed">types.Message</span>, <span class="parameter">link_path</span>, <span class="parameter">link</span>)</span>

- Описание: Устаревший способ установки плагинов без `manifest.json`. <span class="warning">Не рекомендуется, скоро будет удалён.</span>
- Первое появление: [ModuFlex v0.1.0b2 2026-01-30](blog/posts/2026-01-30.md)
- Параметры:
- - **`app`**: Экземпляр `pyrogram.Client`.
- - **`msg`**: Сообщение с командой.
- - **`link_path`**: Части URL репозитория.
- - **`link`**: Ссылка на репозиторий.

<span class="type"><span class="moduflex">ModuFlex</span>.main.<span class="function">remove_plugin</span>(<span class="parameter">app: </span><span class="typed">Client</span>, <span class="parameter">msg: </span><span class="typed">types.Message</span>)</span>

- Описание: Обработчик команды `rmplg` - удаляет плагин из `plugins/` и из кэша `Data`. Плагины `StartedPack` и `AnimationPack` удалить нельзя.
- Первое появление: [ModuFlex v0.0.1 2024-12-29](blog/posts/2024-12-29.md) (как `rmmd`), переименовано в [v0.1.0b3 2026-03-03](blog/posts/2026-03-03.md).
- Параметры:
- - **`app`**: Экземпляр `pyrogram.Client`.
- - **`msg`**: Сообщение с командой.

<span class="type"><span class="moduflex">ModuFlex</span>.main.<span class="function">update_script</span>(<span class="parameter">app: </span><span class="typed">Client</span>, <span class="parameter">msg: </span><span class="typed">types.Message</span>)</span>

- Описание: Обработчик команды `update` - проверяет и устанавливает обновление ModuFlex с GitHub, затем перезапускает скрипт.
- Первое появление: [ModuFlex v0.0.2 2025-01-01](blog/posts/2025-01-01.md).
- Параметры:
- - **`app`**: Экземпляр `pyrogram.Client`.
- - **`msg`**: Сообщение с командой.

<span class="type"><span class="moduflex">ModuFlex</span>.main.<span class="function">modu_flex_state</span>(<span class="parameter">\_</span>, <span class="parameter">msg: </span><span class="typed">types.Message</span>)</span>

- Описание: Обработчик команды `moduflex` - показывает ASCII-логотип, последние строки `script.log`, версию, статус обновления, число плагинов и параметры из `config.ini`.
- Первое появление: [ModuFlex v0.0.9.2 2025-11-16](blog/posts/2025-11-16.md) (заменила `/version`).
- Параметры:
- - **`_`**: Клиент (не используется).
- - **`msg`**: Сообщение с командой.

<span class="type"><span class="moduflex">ModuFlex</span>.main.<span class="function">send_update_function</span>(<span class="parameter">app: </span><span class="typed">Client</span>, <span class="parameter">message: </span><span class="typed">types.Message</span>)</span>

- Описание: Маршрутизатор входящих сообщений: ищет совпадение команд плагинов (префикс, имя плагина, имя команды), применяет фильтры и вызывает обработчик. <span class="warning">Внутренняя функция, не вызывайте вручную.</span>
- Первое появление: [ModuFlex v0.0.3 2025-01-27](blog/posts/2025-01-27.md).
- Параметры:
- - **`app`**: Экземпляр `pyrogram.Client`.
- - **`message`**: Входящее сообщение.

<span class="type"><span class="moduflex">ModuFlex</span>.main.<span class="function">schedule_check_for_update</span>(<span class="parameter">app: </span><span class="typed">Client</span>, <span class="parameter">auto_check_for_update</span>)</span>

- Описание: Периодическая проверка обновлений (планировщик, раз в 10 минут). Уведомляет в «Избранное» или в консоль. <span class="warning">Внутренняя функция, не вызывайте вручную.</span>
- Первое появление: [ModuFlex v0.1.0b1 2025-12-27](blog/posts/2025-12-27.md).
- Параметры:
- - **`app`**: Экземпляр `pyrogram.Client`.
- - **`auto_check_for_update`**: Экземпляр `AsyncIOScheduler`.

<span class="type"><span class="moduflex">ModuFlex</span>.main.<span class="function">check_plugin_for_webinterface</span>(<span class="parameter">\_</span>, <span class="parameter">message: </span><span class="typed">types.Message</span>)</span>

- Описание: Обработчик команды `webi` - проверяет, есть ли у плагина страница на локальном веб-интерфейсе (`http://127.0.0.1:1205/{имя}/`).
- Первое появление: [ModuFlex v0.1.0b3 2026-03-03](blog/posts/2026-03-03.md).
- Параметры:
- - **`_`**: Клиент (не используется).
- - **`message`**: Сообщение с командой.

<span class="type"><span class="moduflex">ModuFlex</span>.main.<span class="function">ModuFlex</span>(self, <span class="parameter">app: </span><span class="typed">Client</span>, <span class="parameter">approute: </span><span class="typed">Quart</span>, <span class="parameter">is_basic: </span><span class="typed">bool</span>=<span class="typed">False</span>, <span class="parameter">\*\*kwargs</span>)</span>

- Описание: Основной класс запуска юзербота: регистрирует системные команды, инициализирует плагины, опционально поднимает веб-сервер (экспериментальный режим).
- Первое появление: [ModuFlex v0.1.0b3 2026-03-03](blog/posts/2026-03-03.md).
- Параметры:
- - **`app`**: Экземпляр `pyrogram.Client`.
- - **`approute`**: Экземпляр `Quart` для веб-интерфейса.
- - **`is_basic`**: Если `True`, выполняется полная инициализация плагинов и маршрутов.
- - **`kwargs`**: Дополнительные аргументы (зарезервировано).
- Методы:
- - <span class="type"><span class="function">run</span>(self) -> <span class="typed">ScriptState</span></span>: Запускает юзербот, регистрирует обработчики, ждёт завершения и возвращает состояние.
- - <span class="type"><span class="function">check_updates</span>(self) -> <span class="typed">None</span></span>: Проверяет версию на GitHub.
- - <span class="type"><span class="function">handling_updates</span>(self) -> <span class="typed">None</span></span>: Регистрирует функции, классы и HTTP-маршруты плагинов из кэша.
- - <span class="type"><span class="function">all_messages</span>(self, <span class="parameter">app: </span><span class="typed">Client</span>, <span class="parameter">message: </span><span class="typed">types.Message</span>)</span>: Обработчик всех сообщений; передаёт их в `send_update_function` после инициализации.
- - <span class="type"><span class="function">\_stop</span>(self, <span class="parameter">\_</span>, <span class="parameter">message: </span><span class="typed">types.Message</span>)</span>: Обработчик команды `stop` - завершает скрипт.
- - <span class="type"><span class="function">\_restart</span>(self, <span class="parameter">\_</span>, <span class="parameter">message: </span><span class="typed">types.Message</span>)</span>: Обработчик команды `restart` - перезапускает скрипт.

<span class="type"><span class="moduflex">ModuFlex</span>.utils.<span class="function">merge_directories</span>(<span class="parameter">src: </span><span class="typed">str</span>, <span class="parameter">dst: </span><span class="typed">str</span>) -> <span class="typed">None</span></span>

- Описание: Рекурсивно сливает папку `src` в `dst`: копирует новые файлы и подпапки, существующие в `dst` не удаляет.
- Первое появление: [ModuFlex v0.0.9.2 2025-11-16](blog/posts/2025-11-16.md).
- Параметры:
- - **`src`**: Путь к исходной папке.
- - **`dst`**: Путь к целевой папке.

<span class="type"><span class="moduflex">ModuFlex</span>.utils.<span class="function">\_\_find_command\_\_</span>(<span class="parameter">\_filters</span>) -> <span class="typed">Optional</span>[<span class="typed">List</span>[<span class="typed">str</span>]]</span>

- Описание: Извлекает префиксы команды из фильтра pyrogram (`CommandFilter`, вложенные `AndFilter`/`OrFilter`). Используется декоратором `func`. <span class="warning">Внутренняя функция, не вызывайте вручную.</span>
- Первое появление: [ModuFlex v0.0.7.1 2025-07-15](blog/posts/2025-07-15.md).
- Параметры:
- - **`_filters`**: Объект фильтра pyrogram.

<span class="type"><span class="moduflex">ModuFlex</span>.utils.<span class="function">\_\_find_command_name\_\_</span>(<span class="parameter">\_filters</span>) -> <span class="typed">Optional</span>[<span class="typed">str</span>]</span>

- Описание: Извлекает имя команды из фильтра pyrogram. Используется декоратором `func`. <span class="warning">Внутренняя функция, не вызывайте вручную.</span>
- Первое появление: [ModuFlex v0.0.7.1 2025-07-15](blog/posts/2025-07-15.md).
- Параметры:
- - **`_filters`**: Объект фильтра pyrogram.

<span class="type"><span class="moduflex">ModuFlex</span>.utils.<span class="function">check_update</span>(<span class="parameter">version_now: </span><span class="typed">str</span>) -> <span class="typed">Tuple</span></span>

- Описание: Сравнивает текущую версию ModuFlex с последней на GitHub.
- Первое появление: [ModuFlex v0.1.0b1 2025-12-27](blog/posts/2025-12-27.md).
- Параметры:
- - **`version_now`**: Текущая версия (строка, например `'0.1.3'`).

<span class="type"><span class="moduflex">ModuFlex</span>.utils.<span class="function">get_config_data</span>() -> <span class="typed">Dict</span>[<span class="typed">str</span>, <span class="typed">Any</span>]</span>

- Описание: Читает и парсит `config.ini` в корне проекта. При отсутствии или ошибке формата завершает программу через `sys.exit()`.
- Первое появление: [ModuFlex v0.1.0b3 2026-03-03](blog/posts/2026-03-03.md).
- Параметры: отсутствуют.

<span class="type"><span class="moduflex">ModuFlex</span>.wasmexecutor.<span class="function">WasmExecutor</span></span>

- Описание: Класс песочницы для выполнения Python-кода через Node.js и Pyodide (WebAssembly). Запускает фоновый процесс `wasmexecutor.mjs` и передаёт код во временный файл. Используется в `Data.sandbox_executor` и функцией `loads.sandbox_exec`. <span class="warning">Не рекомендуется использовать, т.к это есть в `Data.sandbox_executor` или `loads.sandbox_exec`.</span>
- Первое появление: [ModuFlex v0.1.0 2026-04-09](blog/posts/2026-04-09.md).
- Методы:
- - <span class="type"><span class="function">run_code</span>(self, <span class="parameter">code: </span><span class="typed">str</span>, <span class="parameter">\_globals: </span><span class="typed">Optional</span>[<span class="typed">Dict</span>]=<span class="typed">None</span>, <span class="parameter">\_locals: </span><span class="typed">Optional</span>[<span class="typed">Dict</span>]=<span class="typed">None</span>) -> <span class="typed">Dict</span>[<span class="typed">str</span>, <span class="typed">Any</span>]</span>: Выполняет код в изолированной среде. При отсутствии `node_modules` выбрасывает `FileNotFoundError`.

## Ответы на частые вопросы

Здесь будут постепенно собираться ответы на частые вопросы, чтобы не приходилось дожидаться ответа. Если нужного ответа на вопрос не оказалось, [обращайтесь в телеграм канал разработчика](https://t.me/flexyyyapk).

??? question "При переносе файлов на другое устройство, у меня не запускается юзербот"

    Возможно вы не установили python. Это можно сделать на официальном сайте или [следуя этим инструкциям](index.md#download).
    Потом, удалите файл `configuration.json` и удалите папку `node_modules`. Если у вас там важные данные, зайдите в файл, в ключе `ModuFlex` -> `libs_is_dwnld` замените значение `true` на `false`. После этого юзербот должен запуститься, если нет, [обращайтесь в телеграм канал разработчика с проблемой](https://t.me/flexyyyapk).
