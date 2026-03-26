# TelegramCerebroIntegration

Телеграм-бот для создания задач в Cerebro.

## Что делает
- Принимает сообщения только от `chat_id` из `TELEGRAM_CHAT_IDS` в `config.py`.
- Первая строка сообщения используется как имя задачи (до 40 символов, с очисткой запрещенных символов).
- Текст со второй строки и далее отправляется в `definition`.

## Запуск
- Установить зависимости: `pip install -r requirements.txt`
- Создать `config.py` по примеру `config.example.py` и заполнить своими данными.
- Запустить бота: `python telegram_bot.py`
