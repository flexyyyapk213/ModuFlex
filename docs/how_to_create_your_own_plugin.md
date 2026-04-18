# Пособие по созданию плагинов для ModuFlex

## О чём это пособие

Здесь пошагово объясняется, как создать полноценный плагин для ModuFlex. Вместо сухого перечисления API мы поставим конкретную цель и по мере её достижения изучим каждую функцию и класс фреймворка.

Пособие рассчитано на тех, кто знаком с Python и базово понимает асинхронное программирование.

---

## Структура плагина

Перед написанием кода создайте правильную структуру папок. Зайдите в папку `plugins` и создайте новую папку - это и будет ваш плагин. Внутри обязательно создайте файл `__init__.py`.

```
plugins/
└── my_plugin/
    ├── __init__.py       # Точка входа плагина
    ├── templates/        # HTML-шаблоны (для веб-интерфейса)
    └── static/           # CSS, JS, картинки (для веб-интерфейса)
```

!!! warning "Важно"

    В названии папки используйте только латинские буквы и цифры, без пробелов и кириллицы.

---

## Быстрый старт

Минимальный рабочий плагин:

```python
# plugins/my_plugin/__init__.py

from loads import func
from pyrogram import filters, types
from pyrogram.client import Client

@func(filters.command('hello') & filters.me)
async def hello(client: Client, message: types.Message):
    await message.edit('Привет! Плагин работает.')
```

Напишите в любом чате `/hello` - бот отредактирует сообщение.

---

## Цель: плагин «DevKit»

Чтобы изучить весь API на осмысленном примере, создадим плагин **DevKit** - набор инструментов разработчика прямо в Telegram. Такой плагин логично объединяет в себе всё, что предоставляет фреймворк:

| Возможность                             | Какую часть API изучим                              |
| --------------------------------------- | --------------------------------------------------- |
| Выполнение Python-кода прямо из чата    | `sandbox_exec`                                      |
| Установка pip-библиотек по команде      | `set_modules`                                       |
| Просмотр информации о чате/пользователе | `func`, фильтры pyrogram                            |
| Генерация отчётов в разных форматах     | `set_modules` + сторонние библиотеки                |
| Справка по всем командам                | `Description`, `MainDescription`, `FuncDescription` |
| Класс с объединёнными командами         | `Module`                                            |
| Веб-панель с логами выполнения          | `route`, шаблоны                                    |
| Конфигурация плагина                    | `Data.get_config`                                   |

Получится инструмент, который разработчик реально (возможно) будет использовать каждый день.

---

## Шаг 1. Импорты

```python
# plugins/devkit/__init__.py

from loads import (
    func,
    Module,
    route,
    sandbox_exec,
    set_modules,
    Description,
    MainDescription,
    FuncDescription,
    Data
)
from pyrogram import filters, types
from pyrogram.client import Client
from flask import render_template
import json
import os
import time
```

Что здесь что:

| Импорт                                              | Зачем                                             |
| --------------------------------------------------- | ------------------------------------------------- |
| `func`                                              | Декоратор для регистрации команд                  |
| `Module`                                            | Базовый класс для объединения команд и маршрутов  |
| `route`                                             | Декоратор для HTTP-маршрутов веб-интерфейса       |
| `sandbox_exec`                                      | Выполнение кода в изолированной WebAssembly-среде |
| `set_modules`                                       | Установка pip-зависимостей                        |
| `Description`, `MainDescription`, `FuncDescription` | Описание плагина и его команд                     |
| `Data.get_config`                                   | Доступ к конфигурации и списку плагинов           |

---

## Шаг 2. Установка зависимостей

DevKit будет форматировать данные в виде таблиц. Для этого нужна библиотека `tabulate`. Функция `set_modules` проверит, установлена ли она, и загрузит при необходимости.

```python
set_modules(['tabulate'])
from tabulate import tabulate
```

!!! info "Как работает `set_modules`?"

    Функция принимает список строк - имён библиотек. Для каждой она проверяет, доступна ли библиотека через `importlib.util.find_spec`. Если нет - устанавливает через pip. Уже установленные библиотеки пропускаются.
    **Вызывайте `set_modules` до импорта библиотеки**, иначе получите `ImportError`.

!!! tip "Рекомендация"

    Функция `set_modules` устарела, по этому я рекомендую создать в корне вашего плагина файл `__modules__.txt` и в ряд с новой строки вписать сторонние библиотеки.

---

## Шаг 3. Описание плагина

Система ModuFlex умеет показывать встроенную справку по плагинам. Для этого нужно объявить переменную `__description__`:

```python
__description__ = Description(
    MainDescription('DevKit - инструменты разработчика в Telegram.'),

    FuncDescription(
        command='run',
        description='Выполнить Python-код в песочнице.',
        prefixes=['/', '!', '.'],
        parameters=['код'],
        parameters_style=('`', '`')
    ),

    FuncDescription(
        command='pip',
        description='Установить pip-библиотеку.',
        prefixes=['/', '!', '.'],
        parameters=['библиотека'],
        parameters_style=('{', '}')
    ),

    FuncDescription(
        command='info',
        description='Информация о чате или пользователе.',
        prefixes=['/', '!', '.'],
        parameters=['ID или юзернейм'],
        parameters_style=('[', ']')
    ),

    FuncDescription(
        command='report',
        description='Сгенерировать отчёт о чате.',
        prefixes=['/', '!', '.']
    ),

    FuncDescription(
        command='devstatus',
        description='Статистика работы плагина.',
        prefixes=['/', '!', '.']
    ),

    FuncDescription(
        command='devconfig',
        description='Показать или изменить конфигурацию.',
        prefixes=['/', '!', '.'],
        parameters=['ключ', 'значение'],
        parameters_style=('[', ']')
    ),
)
```

!!! note "Имя переменной обязательно `__description__`"

    Именно по этому имени система находит описание плагина для справки.

Разберём параметры `FuncDescription`:

| Параметр           | Что делает                      | Пример                     |
| ------------------ | ------------------------------- | -------------------------- |
| `command`          | Название команды (без префикса) | `'run'`                    |
| `description`      | Описание команды                | `'Выполнить Python-код'`   |
| `prefixes`         | Допустимые префиксы             | `['/', '!', '.']`          |
| `parameters`       | Список аргументов               | `['код']`                  |
| `parameters_style` | Обрамление параметров           | `('`', '`')` → `` `код` `` |

Если `parameters_style` содержит одну строку или один символ, он используется и как открывающий, и как закрывающий.

---

## Шаг 4. Хранилище логов и конфигурация

DevKit ведёт лог всех выполненных команд - это пригодится для веб-панели.

```python
LOGS_FILE = os.path.join(os.path.dirname(__file__), 'logs.json')


def load_logs() -> list:
    try:
        with open(LOGS_FILE, encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_logs(logs: list) -> None:
    with open(LOGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)


def add_log(command: str, input_text: str, output_text: str, success: bool) -> None:
    """Добавляет запись в лог."""
    logs = load_logs()
    logs.append({
        'time': time.strftime('%Y-%m-%d %H:%M:%S'),
        'command': command,
        'input': input_text,
        'output': output_text[:500],  # Обрезаем слишком длинный вывод
        'success': success
    })
    # Храним не больше 100 последних записей
    config = Data.get_config(__file__)
    max_logs = config.get('max_logs', 100)
    if len(logs) > max_logs:
        logs = logs[-max_logs:]
    save_logs(logs)


logs: list = load_logs()
```

### `Data.get_config`

Обратите внимание на строку:

```python
config = Data.get_config(__file__)
```

Здесь мы получаем конфигурацию нашего плагина. Передаём `__file__` (но можно и само имя вашего плагина), чтобы система определила, какой плагин запрашивает конфиг.

**Правила доступа:**

- Если вы запрашиваете конфиг **своего** плагина - получаете `MappingConfig`, который можно **читать и редактировать**
- Если запрашиваете конфиг **чужого** плагина - получаете **копию** (только чтение)
- Если вызвать без аргумента - вернётся копия всех конфигов

```python
# Свой конфиг - можно менять
my_config = Data.get_config(__file__)
my_config['max_logs'] = 200  # Сохранится

# Чужой конфиг - только чтение
other_config = Data.get_config('other_plugin')
other_config['key'] = 'value'  # Изменение не сохранится - это копия

# Все конфиги - только чтение
all_configs = Data.get_config()
```

---

## Шаг 5. Команда `/run` - выполнение кода в песочнице

Главная команда DevKit. Разработчик пишет код прямо в чате и получает результат.

````python
@func(
    filters.command('run', ['/', '!', '.']) & filters.me,
    description='Выполнить Python-код в песочнице.'
)
async def run_code(client: Client, message: types.Message):
    """
    Использование: /run `код`
    Пример:        /run print([i**2 for i in range(10)])
    """
    parts = message.text.split(' ', maxsplit=1)

    if len(parts) < 2 or not parts[1].strip():
        return await message.edit('Вы не верно ввели параметры, пример: /run <код>')

    code = parts[1].strip()
    await message.edit('Выполняю...')

    # sandbox_exec выполняет код в изолированной WebAssembly-среде.
    # Это безопасно: даже ошибочный или опасный код не повредит основной процесс.
    #
    # _globals - глобальные переменные, доступные внутри кода
    # _locals  - локальные переменные (опционально)
    result = sandbox_exec(
        code,
        _globals={
            'client_info': {
                'plugins': Data.get_name_plugins(),
            }
        }
    )

    if result.get('error', False):
        await message.edit(f'Ошибка:\n```\n{result.error}\n```')
        add_log('run', code, str(result.error), success=False)
    else:
        output = result.output or '(нет вывода)'
        await message.edit(f'Результат:\n```\n{output}\n```')
        add_log('run', code, output, success=True)
````

!!! warning "О безопасности"

    `sandbox_exec` изолирует выполнение, но не давайте доступ к этой команде посторонним. Фильтр `filters.me` гарантирует, что команду может вызвать только владелец аккаунта.

---

## Шаг 6. Команда `/pip` - установка библиотек

Позволяет установить pip-библиотеку прямо из чата.

````python
@func(
    filters.command('pip', ['/', '!', '.']) & filters.me,
    description='Установить pip-библиотеку.'
)
async def install_package(client: Client, message: types.Message):
    """
    Использование: /pip {библиотека}
    Пример:        /pip requests
    """
    parts = message.text.split()

    if len(parts) < 2:
        return await message.edit('Использование: `/pip {библиотека}`')

    package_name = parts[1].strip()
    await message.edit(f'📦 Устанавливаю `{package_name}`...')

    try:
        set_modules([package_name])
        await message.edit(f'`{package_name}` установлена.')
        add_log('pip', package_name, 'Установлена', success=True)
    except Exception as e:
        await message.edit(f'Ошибка установки `{package_name}`:\n```\n{e}\n```')
        add_log('pip', package_name, str(e), success=False)
````

---

## Шаг 7. Команда `/info` - информация о чате

Здесь мы используем возможности pyrogram для получения данных о чате или пользователе, а `tabulate` (установленный через `set_modules`) - для форматирования вывода.

````python
@func(
    filters.command('info', ['/', '!', '.']) & filters.me,
    description='Информация о чате или пользователе.'
)
async def chat_info(client: Client, message: types.Message):
    """
    Использование: /info [ID или @username]
    Без аргумента - информация о текущем чате.
    """
    parts = message.text.split()

    if len(parts) >= 2:
        target = parts[1]
        # Если передали число - это ID
        if target.lstrip('-').isdigit():
            target = int(target)
    else:
        target = message.chat.id

    try:
        chat = await client.get_chat(target)
    except Exception as e:
        return await message.edit(f'Не удалось получить информацию:\n`{e}`')

    rows = [
        ['ID', chat.id],
        ['Тип', chat.type.value],
        ['Название', chat.title or chat.first_name or '-'],
        ['Username', f'@{chat.username}' if chat.username else '-'],
        ['Участников', chat.members_count or '-'],
        ['Описание', (chat.description or '-')[:80]],
    ]

    table = tabulate(rows, tablefmt='simple')
    await message.edit(f'```\n{table}\n```')
    add_log('info', str(target), table, success=True)
````

---

## Шаг 8. Команда `/devconfig` - управление конфигурацией

Позволяет просматривать и изменять настройки плагина прямо из чата.

````python
@func(
    filters.command('devconfig', ['/', '!', '.']) & filters.me,
    description='Показать или изменить конфигурацию.'
)
async def dev_config(client: Client, message: types.Message):
    """
    Использование:
        /devconfig             - показать все настройки
        /devconfig ключ        - показать значение
        /devconfig ключ значение - установить значение
    """
    config = Data.get_config(__file__)
    parts = message.text.split(maxsplit=2)

    if len(parts) == 1:
        # Показать весь конфиг
        if not config:
            return await message.edit('Конфигурация пуста.')

        rows = [[k, str(v)] for k, v in config.items()]
        table = tabulate(rows, headers=['Ключ', 'Значение'], tablefmt='simple')
        await message.edit(f'Конфигурация DevKit:\n```\n{table}\n```')
    elif len(parts) == 2:
        # Показать одно значение
        key = parts[1]
        value = config.get(key)
        if value is None:
            await message.edit(f'Ключ `{key}` не найден.')
        else:
            await message.edit(f'`{key}` = `{value}`')

    else:
        # Установить значение
        key, raw_value = parts[1], parts[2]

        # Пробуем интерпретировать значение
        if raw_value.isdigit():
            value = int(raw_value)
        elif raw_value.lower() in ('true', 'false'):
            value = raw_value.lower() == 'true'
        else:
            value = raw_value

        config[key] = value
        await message.edit(f'`{key}` → `{value}`')
        add_log('devconfig', f'{key} = {value}', 'Изменено', success=True)
````

---

## Шаг 9. Класс `Module` - объединяем команды и веб-интерфейс

Когда несколько обработчиков логически связаны, их удобно объединить в класс. При наследовании от `Module` система автоматически:

1. Создаёт экземпляр класса
2. Находит все методы с декораторами `@func` и `@route`
3. Регистрирует их в обработчиках и веб-сервере

````python
class DevKitPanel(Module):
    """
    Класс объединяет команды статистики и веб-панель.
    """

    @func(filters.command('devstatus', ['/', '!', '.']) & filters.me)
    async def dev_status(self, client: Client, message: types.Message):
        """Статистика работы плагина."""
        logs = load_logs()
        total = len(logs)
        success = sum(1 for log in logs if log['success'])
        failed = total - success
        plugins = Data.get_name_plugins()

        rows = [
            ['Всего выполнено', total],
            ['Успешно', success],
            ['С ошибками', failed],
            ['Загружено плагинов', len(plugins)],
            ['Плагины', ', '.join(plugins)],
        ]
        table = tabulate(rows, tablefmt='simple')
        await message.edit(f'DevKit Status\n```\n{table}\n```')

    @func(filters.command('report', ['/', '!', '.']) & filters.me)
    async def report(self, client: Client, message: types.Message):
        """Генерирует отчёт о текущем чате."""
        chat = message.chat

        # Собираем данные
        report_lines = [
            f'Отчёт о чате',
            f'',
            f'Название: {chat.title or chat.first_name or "-"}',
            f'ID: `{chat.id}`',
            f'Тип: {chat.type.value}',
        ]

        if chat.username:
            report_lines.append(f'Username: @{chat.username}')

        if chat.members_count:
            report_lines.append(f'Участников: {chat.members_count}')

        # Добавляем информацию из конфига
        config = Data.get_config(__file__)
        if config.get('show_config_in_report', False):
            report_lines.append(f'')
            report_lines.append(f'Настройки DevKit: {len(config)} параметров')

        report_text = '\n'.join(report_lines)
        await message.edit(report_text)
        add_log('report', str(chat.id), report_text, success=True)

    @route('/', methods=['GET'])
    def index(self):
        """
        Главная страница веб-панели.
        Доступна по адресу: http://0.0.0.0:1205/devkit/
        """
        logs = load_logs()
        plugins = Data.get_name_plugins()
        config = Data.get_config('devkit')

        return render_template(
            'index.html',
            logs=logs,
            plugins=plugins,
            config=config
        )

    @route('/logs', methods=['GET'])
    def logs_page(self):
        """
        Страница с логами.
        Доступна по адресу: http://0.0.0.0:1205/devkit/logs
        """
        logs = load_logs()
        return render_template('logs.html', logs=logs)
````

!!! info "Как работает `Module` внутри?"

    При наследовании срабатывает `__init_subclass__`. Система определяет имя плагина по пути файла, создаёт экземпляр класса, перебирает все методы и решает, куда их зарегистрировать.

---

## Шаг 10. Шаблоны веб-панели

Создайте папку `plugins/devkit/templates/devkit` и добавьте шаблоны.

**`plugins/devkit/templates/devkit/index.html`** - главная страница:

```html
<!DOCTYPE html>
<html lang="ru">
  <head>
    <meta charset="UTF-8" />
    <title>DevKit - Панель управления</title>
    <link
      rel="stylesheet"
      href="{{ url_for('devkit.static', filename='style.css') }}"
    />
  </head>
  <body>
    <h1>🛠 DevKit</h1>

    <section>
      <h2>Загруженные плагины</h2>
      <ul>
        {% for plugin in plugins %}
        <li>{{ plugin }}</li>
        {% endfor %}
      </ul>
    </section>

    <section>
      <h2>Конфигурация</h2>
      {% if config %}
      <table>
        <tr>
          <th>Ключ</th>
          <th>Значение</th>
        </tr>
        {% for key, value in config.items() %}
        <tr>
          <td>{{ key }}</td>
          <td>{{ value }}</td>
        </tr>
        {% endfor %}
      </table>
      {% else %}
      <p>Конфигурация пуста.</p>
      {% endif %}
    </section>

    <section>
      <h2>Последние действия</h2>
      <p><a href="{{ url_for('devkit.logs_page') }}">Все логи →</a></p>
      <table>
        <tr>
          <th>Время</th>
          <th>Команда</th>
          <th>Статус</th>
        </tr>
        {% for log in logs[-10:] | reverse %}
        <tr>
          <td>{{ log.time }}</td>
          <td>{{ log.command }}</td>
          <td>{{ '✅' if log.success else '❌' }}</td>
        </tr>
        {% endfor %}
      </table>
    </section>
  </body>
</html>
```

**`plugins/devkit/templates/devkit/logs.html`** - страница логов:

```html
<!DOCTYPE html>
<html lang="ru">
  <head>
    <meta charset="UTF-8" />
    <title>DevKit - Логи</title>
  </head>
  <body>
    <h1>📋 Логи выполнения</h1>
    <p><a href="{{ url_for('devkit.index') }}">← Назад</a></p>

    {% if logs %}
    <table border="1" cellpadding="8">
      <tr>
        <th>Время</th>
        <th>Команда</th>
        <th>Ввод</th>
        <th>Вывод</th>
        <th>Статус</th>
      </tr>
      {% for log in logs | reverse %}
      <tr>
        <td>{{ log.time }}</td>
        <td>{{ log.command }}</td>
        <td><code>{{ log.input[:100] }}</code></td>
        <td><code>{{ log.output[:100] }}</code></td>
        <td>{{ '✅' if log.success else '❌' }}</td>
      </tr>
      {% endfor %}
    </table>
    {% else %}
    <p>Логов пока нет.</p>
    {% endif %}
  </body>
</html>
```

---

## Полный код плагина

````python
# plugins/devkit/__init__.py

from loads import (
    func,
    Module,
    route,
    sandbox_exec,
    set_modules,
    Description,
    MainDescription,
    FuncDescription,
    Data
)
from pyrogram import filters, types
from pyrogram.client import Client
from flask import render_template
import json
import os
import time

# ── Зависимости ─────────────────────────────────────────────────────────────

set_modules(['tabulate'])
from tabulate import tabulate

# ── Описание плагина ────────────────────────────────────────────────────────

__description__ = Description(
    MainDescription('DevKit - инструменты разработчика в Telegram.'),
    FuncDescription('run',       'Выполнить Python-код в песочнице.',  prefixes=['/', '!', '.'], parameters=['код'],                 parameters_style=('`', '`')),
    FuncDescription('pip',       'Установить pip-библиотеку.',         prefixes=['/', '!', '.'], parameters=['библиотека'],          parameters_style=('{', '}')),
    FuncDescription('info',      'Информация о чате/пользователе.',    prefixes=['/', '!', '.'], parameters=['ID или юзернейм'],     parameters_style=('[', ']')),
    FuncDescription('report',    'Сгенерировать отчёт о чате.',        prefixes=['/', '!', '.']),
    FuncDescription('devstatus', 'Статистика работы плагина.',         prefixes=['/', '!', '.']),
    FuncDescription('devconfig', 'Показать/изменить конфигурацию.',    prefixes=['/', '!', '.'], parameters=['ключ', 'значение'],    parameters_style=('[', ']')),
)

# ── Логи ────────────────────────────────────────────────────────────────────

LOGS_FILE = os.path.join(os.path.dirname(__file__), 'logs.json')


def load_logs() -> list:
    try:
        with open(LOGS_FILE, encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_logs(logs: list) -> None:
    with open(LOGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)


def add_log(command: str, input_text: str, output_text: str, success: bool) -> None:
    logs = load_logs()
    logs.append({
        'time': time.strftime('%Y-%m-%d %H:%M:%S'),
        'command': command,
        'input': input_text,
        'output': output_text[:500],
        'success': success
    })
    config = Data.get_config(__file__)
    max_logs = config.get('max_logs', 100)
    if len(logs) > max_logs:
        logs = logs[-max_logs:]
    save_logs(logs)

# ── Команды ─────────────────────────────────────────────────────────────────

@func(
    filters.command('run', ['/', '!', '.']) & filters.me,
    description='Выполнить Python-код в песочнице.'
)
async def run_code(client: Client, message: types.Message):
    """
    Использование: /run `код`
    Пример:        /run print([i**2 for i in range(10)])
    """
    parts = message.text.split(' ', maxsplit=1)

    if len(parts) < 2 or not parts[1].strip():
        return await message.edit('Вы не верно ввели параметры, пример: /run <код>')

    code = parts[1].strip()
    await message.edit('Выполняю...')

    # sandbox_exec выполняет код в изолированной WebAssembly-среде.
    # Это безопасно: даже ошибочный или опасный код не повредит основной процесс.
    #
    # _globals - глобальные переменные, доступные внутри кода
    # _locals  - локальные переменные (опционально)
    result = sandbox_exec(
        code,
        _globals={
            'client_info': {
                'plugins': Data.get_name_plugins(),
            }
        }
    )

    if result.get('error', False):
        await message.edit(f'Ошибка:\n```\n{result.error}\n```')
        add_log('run', code, str(result.error), success=False)
    else:
        output = result.output or '(нет вывода)'
        await message.edit(f'Результат:\n```\n{output}\n```')
        add_log('run', code, output, success=True)


@func(
    filters.command('pip', ['/', '!', '.']) & filters.me,
    description='Установить pip-библиотеку.'
)
async def install_package(client: Client, message: types.Message):
    """
    Использование: /pip {библиотека}
    Пример:        /pip requests
    """
    parts = message.text.split()

    if len(parts) < 2:
        return await message.edit('Использование: `/pip {библиотека}`')

    package_name = parts[1].strip()
    await message.edit(f'📦 Устанавливаю `{package_name}`...')

    try:
        set_modules([package_name])
        await message.edit(f'`{package_name}` установлена.')
        add_log('pip', package_name, 'Установлена', success=True)
    except Exception as e:
        await message.edit(f'Ошибка установки `{package_name}`:\n```\n{e}\n```')
        add_log('pip', package_name, str(e), success=False)


@func(
    filters.command('info', ['/', '!', '.']) & filters.me,
    description='Информация о чате или пользователе.'
)
async def chat_info(client: Client, message: types.Message):
    """
    Использование: /info [ID или @username]
    Без аргумента - информация о текущем чате.
    """
    parts = message.text.split()

    if len(parts) >= 2:
        target = parts[1]
        # Если передали число - это ID
        if target.lstrip('-').isdigit():
            target = int(target)
    else:
        target = message.chat.id

    try:
        chat = await client.get_chat(target)
    except Exception as e:
        return await message.edit(f'Не удалось получить информацию:\n`{e}`')

    rows = [
        ['ID', chat.id],
        ['Тип', chat.type.value],
        ['Название', chat.title or chat.first_name or '-'],
        ['Username', f'@{chat.username}' if chat.username else '-'],
        ['Участников', chat.members_count or '-'],
        ['Описание', (chat.description or '-')[:80]],
    ]

    table = tabulate(rows, tablefmt='simple')
    await message.edit(f'```\n{table}\n```')
    add_log('info', str(target), table, success=True)


@func(
    filters.command('devconfig', ['/', '!', '.']) & filters.me,
    description='Показать или изменить конфигурацию.'
)
async def dev_config(client: Client, message: types.Message):
    """
    Использование:
        /devconfig             - показать все настройки
        /devconfig ключ        - показать значение
        /devconfig ключ значение - установить значение
    """
    config = Data.get_config(__file__)
    parts = message.text.split(maxsplit=2)

    if len(parts) == 1:
        # Показать весь конфиг
        if not config:
            return await message.edit('Конфигурация пуста.')

        rows = [[k, str(v)] for k, v in config.items()]
        table = tabulate(rows, headers=['Ключ', 'Значение'], tablefmt='simple')
        await message.edit(f'Конфигурация DevKit:\n```\n{table}\n```')
    elif len(parts) == 2:
        # Показать одно значение
        key = parts[1]
        value = config.get(key)
        if value is None:
            await message.edit(f'Ключ `{key}` не найден.')
        else:
            await message.edit(f'`{key}` = `{value}`')

    else:
        # Установить значение
        key, raw_value = parts[1], parts[2]

        # Пробуем интерпретировать значение
        if raw_value.isdigit():
            value = int(raw_value)
        elif raw_value.lower() in ('true', 'false'):
            value = raw_value.lower() == 'true'
        else:
            value = raw_value

        config[key] = value
        await message.edit(f'`{key}` → `{value}`')
        add_log('devconfig', f'{key} = {value}', 'Изменено', success=True)

# ── Класс с командами и веб-панелью ─────────────────────────────────────────

class DevKitPanel(Module):
    """
    Класс объединяет команды статистики и веб-панель.
    """

    @func(filters.command('devstatus', ['/', '!', '.']) & filters.me)
    async def dev_status(self, client: Client, message: types.Message):
        """Статистика работы плагина."""
        logs = load_logs()
        total = len(logs)
        success = sum(1 for log in logs if log['success'])
        failed = total - success
        plugins = Data.get_name_plugins()

        rows = [
            ['Всего выполнено', total],
            ['Успешно', success],
            ['С ошибками', failed],
            ['Загружено плагинов', len(plugins)],
            ['Плагины', ', '.join(plugins)],
        ]
        table = tabulate(rows, tablefmt='simple')
        await message.edit(f'DevKit Status\n```\n{table}\n```')

    @func(filters.command('report', ['/', '!', '.']) & filters.me)
    async def report(self, client: Client, message: types.Message):
        """Генерирует отчёт о текущем чате."""
        chat = message.chat

        # Собираем данные
        report_lines = [
            f'Отчёт о чате',
            f'',
            f'Название: {chat.title or chat.first_name or "-"}',
            f'ID: `{chat.id}`',
            f'Тип: {chat.type.value}',
        ]

        if chat.username:
            report_lines.append(f'Username: @{chat.username}')

        if chat.members_count:
            report_lines.append(f'Участников: {chat.members_count}')

        # Добавляем информацию из конфига
        config = Data.get_config(__file__)
        if config.get('show_config_in_report', False):
            report_lines.append(f'')
            report_lines.append(f'Настройки DevKit: {len(config)} параметров')

        report_text = '\n'.join(report_lines)
        await message.edit(report_text)
        add_log('report', str(chat.id), report_text, success=True)

    @route('/', methods=['GET'])
    def index(self):
        """
        Главная страница веб-панели.
        Доступна по адресу: http://0.0.0.0:1205/devkit/
        """
        logs = load_logs()
        plugins = Data.get_name_plugins()
        config = Data.get_config('devkit')

        return render_template(
            'index.html',
            logs=logs,
            plugins=plugins,
            config=config
        )

    @route('/logs', methods=['GET'])
    def logs_page(self):
        """
        Страница с логами.
        Доступна по адресу: http://0.0.0.0:1205/devkit/logs
        """
        logs = load_logs()
        return render_template('logs.html', logs=logs)
````

---

## Структура готового плагина

```
plugins/
└── devkit/
    ├── __init__.py          # Весь код плагина
    ├── logs.json            # Логи (создаётся автоматически)
    ├── templates/
    │   └── devkit/
    │       ├── index.html       # Главная страница веб-панели
    │       └── logs.html        # Страница логов
    │
    └── static/
        └── style.css        # Стили (опционально)
```

---

## Справочник API

### Декораторы

| Декоратор                     | Описание                                                      |
| ----------------------------- | ------------------------------------------------------------- |
| `@func(filters, description)` | Регистрирует обработчик команды. **Основной и рекомендуемый** |
| `@route(rule, **options)`     | Регистрирует HTTP-маршрут веб-интерфейса плагина              |

### Устаревшие декораторы

Работают, но выдают `DeprecationWarning`. Используйте `@func` вместо них.

| Устаревший      | Чем заменить                  |
| --------------- | ----------------------------- |
| `@private_func` | `@func` с `filters.private`   |
| `@chat_func`    | `@func` с `filters.group`     |
| `@channel_func` | `@func` с `filters.channel`   |
| `@all_func`     | `@func` без фильтра типа чата |

### Классы

| Класс                       | Назначение                                                               |
| --------------------------- | ------------------------------------------------------------------------ |
| `Module`                    | Базовый класс для группировки команд и маршрутов                         |
| `Description(main, *funcs)` | Описание плагина и его команд                                            |
| `MainDescription(text)`     | Краткое описание плагина                                                 |
| `FuncDescription(...)`      | Описание одной команды                                                   |
| `chatType`                  | Перечисление типов чатов: `DEFAULT`, `PRIVATE`, `CHAT`, `CHANNEL`, `ALL` |

### Утилиты

| Функция                                 | Назначение                                             |
| --------------------------------------- | ------------------------------------------------------ |
| `sandbox_exec(code, _globals, _locals)` | Выполняет Python-код в изолированной WebAssembly-среде |
| `set_modules(modules)`                  | Устанавливает pip-зависимости при необходимости        |
| `Data.get_config(plugin_name)`          | Получает конфигурацию плагина                          |
| `Data.get_name_plugins()`               | Возвращает список имён всех плагинов                   |
