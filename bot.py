import telebot
from logic import ReviewLogic
from config import TOKEN, MESSAGES, MOTIVATION
import random

bot = telebot.TeleBot(TOKEN)
review_logic = ReviewLogic()

def get_main_keyboard():
    """Создать основную клавиатуру"""
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(
        telebot.types.KeyboardButton("📚 Проверить материалы"),
        telebot.types.KeyboardButton("📊 Статистика")
    )
    keyboard.add(
        telebot.types.KeyboardButton("📖 Список материалов"),
        telebot.types.KeyboardButton("🎲 Случайный материал")
    )
    keyboard.add(
        telebot.types.KeyboardButton("🔥 Серия повторений"),
        telebot.types.KeyboardButton("❓ Помощь")
    )
    return keyboard

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, MESSAGES['welcome'], reply_markup=get_main_keyboard())

@bot.message_handler(commands=['help'])
def help_command(message):
    bot.reply_to(message, MESSAGES['help'])

@bot.message_handler(commands=['check'])
def check_reviews(message):
    reviews = review_logic.get_reviews(str(message.chat.id))
    if not reviews:
        bot.reply_to(message, MESSAGES['no_reviews'])
        return

    for material in reviews:
        markup = telebot.types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            telebot.types.InlineKeyboardButton(
                "✅ Повторено",
                callback_data=f"reviewed_{material['text']}"
            ),
            telebot.types.InlineKeyboardButton(
                "🔄 Повторить позже",
                callback_data=f"later_{material['text']}"
            )
        )
        bot.send_message(
            message.chat.id,
            MESSAGES['review_ready'].format(material['text']),
            reply_markup=markup
        )

@bot.message_handler(commands=['stats'])
def stats_command(message):
    stats = review_logic.get_stats(str(message.chat.id))
    achievements = "\n".join(stats['achievements']) if stats['achievements'] else "Пока нет достижений"
    
    bot.reply_to(message, MESSAGES['stats'].format(
        stats['completed'],
        stats['in_progress'],
        stats['streak'],
        stats['level'],
        achievements
    ))

@bot.message_handler(commands=['list'])
def list_command(message):
    materials = review_logic.get_all_materials(str(message.chat.id))
    if not materials:
        bot.reply_to(message, MESSAGES['list_empty'])
        return

    response = MESSAGES['list_header']
    for material in materials:
        status = "✅" if material['completed'] else "📚"
        response += MESSAGES['list_item'].format(f"{status} {material['text']}")
    
    bot.reply_to(message, response)

@bot.message_handler(commands=['random'])
def random_command(message):
    material = review_logic.get_random_material(str(message.chat.id))
    if not material:
        bot.reply_to(message, MESSAGES['no_materials'])
        return

    bot.reply_to(message, MESSAGES['random'] + material['text'])

@bot.message_handler(commands=['streak'])
def streak_command(message):
    stats = review_logic.get_stats(str(message.chat.id))
    motivation = random.choice(MOTIVATION)
    bot.reply_to(message, MESSAGES['streak'].format(
        stats['streak'],
        motivation
    ))

@bot.callback_query_handler(func=lambda call: call.data.startswith('reviewed_'))
def handle_review_callback(call):
    material = call.data.replace('reviewed_', '')
    review_logic.mark_reviewed(str(call.message.chat.id), material)
    
    stats = review_logic.get_stats(str(call.message.chat.id))
    if stats['streak'] > 1:
        response = f"✅ Отмечено! Серия повторений: {stats['streak']} дней! 🔥"
    else:
        response = "✅ Отмечено! " + random.choice(MOTIVATION)
    
    bot.answer_callback_query(call.id, response)
    bot.edit_message_reply_markup(
        call.message.chat.id,
        call.message.message_id,
        reply_markup=None
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('later_'))
def handle_later_callback(call):
    bot.answer_callback_query(call.id, "👌 Хорошо, напомню позже!")
    bot.edit_message_reply_markup(
        call.message.chat.id,
        call.message.message_id,
        reply_markup=None
    )

@bot.message_handler(func=lambda message: True)
def handle_material(message):
    text = message.text
    
    # Обработка кнопок клавиатуры
    if text == "📚 Проверить материалы":
        check_reviews(message)
    elif text == "📊 Статистика":
        stats_command(message)
    elif text == "📖 Список материалов":
        list_command(message)
    elif text == "🎲 Случайный материал":
        random_command(message)
    elif text == "🔥 Серия повторений":
        streak_command(message)
    elif text == "❓ Помощь":
        help_command(message)
    else:
        # Добавление нового материала
        review_logic.add_material(str(message.chat.id), text)
        bot.reply_to(message, MESSAGES['material_added'])

if __name__ == '__main__':
    bot.polling(none_stop=True)
