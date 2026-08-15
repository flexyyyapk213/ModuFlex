"""
Скрипт для автоматического отправления нововведении о ModuFlex.
Этот файл можно спокойно удалить, т.к он не влияет на сам ModuFlex и не отправляет конф. данные третьим лиц.
Он срабатывает в момент, когда в гитхаб репозиторий был сделан pull.
"""

import importlib.util
import json
import os
import sys
import urllib.request

BOT_TOKEN = os.getenv("BOT_TOKEN") # Скрытый токен бота, для отправки сообщения в канал
CHANNEL_ID = -1001541179675  # Публичный айди главного канала

def send_message(text: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage" # Ссылка апи, для отправки сообщение в канал

    payload = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "parse_mode": "Markdown"
    }

    data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}
    )

    with urllib.request.urlopen(req) as response:
        return response.read()

def load_news_from_init() -> str:
    init_path = "__init__.py"

    if os.path.exists(init_path):
        sys.path.insert(0, os.path.abspath("."))

        try:
            spec = importlib.util.spec_from_file_location("moduflex_init", init_path)
            if spec and spec.loader:
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                return (getattr(mod, "__news__", "🎉 Вышла новая версия ModuFlex!"), getattr(mod, "__version__", " "))
        except Exception as e:
            print(f"Ошибка при импорте __init__.py: {e}")

    return "🎉 Вышла новая версия ModuFlex!"

def main():
    new_features = load_news_from_init()
    text = f"Вышло обновление v{new_features[1]}🎉🎉🎉🎉🎉\n\n{new_features[0]}\n\nЧтобы обновиться, отправьте в чат:\n```\n/update\n```\n\n🔥Давайте наберём как можно много реакций, чтобы у меня была мотивация выпускать обновление по чаще!"
    send_message(text)

if __name__ == "__main__":
    main()