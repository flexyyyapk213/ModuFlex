from loads import Description, MainDescription, FuncDescription

__description__ = Description(
    MainDescription('ModuFlex - Модульный Telegram Юзербот.Не плагин, а команды из корня!'),
    FuncDescription('help', 'Выводит список плагинов/команд.Пример: .help(вывод плагинов), .help 2(вывод плагинов на 2 странице), .help ModuFlex(показывает команды плагина), help ModuFlex 2(показывает команды плагина на 2 странице)', parameters=['страница/имя плагина(не обязательно)', 'страница(не обязательно и после имя плагина)'], prefixes=['.', '/', '!']),
    FuncDescription('dwlmd', 'Скачивает сторонний плагин по ссылке из GitHub.', prefixes=['.', '/', '!'], parameters=['ссылка .zip файла']),
    FuncDescription('rmmd', 'Удаляет модуль.', prefixes=['.', '/', '!'], parameters=['имя плагина']),
    FuncDescription('update', 'Обновляет скрипт.', prefixes=['.', '/', '!']),
    FuncDescription('version', 'Показывает текущую версию и есть ли обновление.', prefixes=['.', '/', '!'])
)