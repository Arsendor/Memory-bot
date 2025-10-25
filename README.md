# Telegram Spaced-Repetition Bot

Учебный Telegram-бот для интервального повторения (по идеям кривой Эббингауза).

Функции:
- Добавление материалов (отправьте текст боту)
- Интервальные повторения (1, 3, 7, 14, 30 дней)
- Клавиатура для удобства
- Статистика, серия повторений, достижения

Требования:
- Python 3.8+
- Зависимости в `requirements.txt`

Быстрый старт
1. Клонируйте репозиторий
2. Создайте виртуальное окружение и активируйте его
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```
3. Установите зависимости
```powershell
pip install -r requirements.txt
```
4. Скопируйте `config_example.py` в `config.py` и вставьте свой токен от @BotFather
```powershell
cp config_example.py config.py
# затем откройте config.py и вставьте токен
```

5. Запустите бота
```powershell
python bot.py
```

Безопасность
- Никогда не коммитьте `config.py` с реальным токеном. `config.py` добавлен в `.gitignore`.

Как отправить на GitHub
- Следуйте инструкциям в корневом TODO (git init, .gitignore, commit, create remote, push)


Спасибо за внимание!
