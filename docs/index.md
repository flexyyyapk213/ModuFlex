# Информация

![Static Badge](https://img.shields.io/badge/Python-3.8%2B-gray?style=flat&logo=python&logoColor=%23FFD43B&labelColor=%233776AB)
![Static Badge](https://img.shields.io/badge/Library-Pyrogram-gray?style=flat&logo=telegram&labelColor=white)
![Static Badge](https://img.shields.io/badge/SQLite-DataBase-grey?style=flat&logo=sqlite&logoColor=blue&labelColor=white)
![Static Badge](https://img.shields.io/badge/WebFramework-Quart-grey?style=flat&logo=flask&logoColor=black&labelColor=white)
![Static Badge](https://img.shields.io/badge/Sandbox-WASM-grey?style=flat&logo=webassembly&logoColor=%236a55f0&labelColor=white)
![Static Badge](https://img.shields.io/badge/Built--in_Free_AI-grey?style=flat&logo=googlegemini&logoColor=%23388aff&labelColor=white)

> Проект 03.10.2024 21:32:15 UTC+3

> ModuFlex - Модульный Telegram Юзербот

> Особенности:

- 🧩 Плагиновая архитектура
- 📦 Менеджер плагинов
- ⏫ Лёгкое обновление скрипта одной операцией

!!! info

    Данный скрипт создан только для развлекательных целях.

## Установка

Установите python и git в терминале или на официальном сайте.

### Для Android

```bash
pkg install python git -y
```

### Для Linux

#### Ubuntu / Debian

```bash
sudo apt update
sudo apt install python3 python3-pip git
```

#### Fedora

```bash
sudo dnf install python3 python3-pip git
```

#### Arch Linux / Manjaro

```bash
sudo pacman -S python python-pip git
```

#### openSUSE

```bash
sudo zypper install python3 python3-pip git
```

### Клонирование

Далее клонируйте этот репозиторий:

```bash
git clone "https://github.com/flexyyyapk213/ModuFlex"
```

Перейдите в дерикторию

```bash
cd ModuFlex
```

Создайте файл `config.ini` и вставьте шаблон заменив данные на ваши

```python
api_id = 12345679
api_hash = "..."
phone_number = 7123456
password = "..."
```

- `phone_number` - Ваш номер телефона.
- `password` - Ваш пароль от двух факторной аутентификаций(если имеется).

!!! note

    Более подробно расписано в contribution.md в разделе: [Файл конфигураций](contribution.md#config-file)

!!! tip

    О том, как получить **api_id** и **api_hash** вы можете узнать [в этой статье](https://teletype.in/@sakurahost/GetApi)(К данной статье разработчик отношения не имеет)

И запустите файл `run.py`

```bash
python run.py
```

> Контрибьюция

В файле [contribution.md](contribution.md) полная инструкция о том, как создать свой плагин и [как вставить свои данные в конфигурации](contribution.md#config-file).

> Дисклеймер

Я не несу отвественности за использования, скачивание, создания модуля и прочее.Всё на ваш страх и риск.
