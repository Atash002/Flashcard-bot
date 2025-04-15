import csv
import random
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = '8163775386:AAF_9Y3yH3WaI5IGS9cTc4mNHhTxeT_onAY'

# Загружаем базу слов из CSV
def load_words():
    words = []
    with open("words_cleaned.csv", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) == 2:
                words.append((row[0], row[1]))
    return words

flashcards = load_words()

# Генерация кнопок
reply_keyboard = [['Угадать перевод', 'Следующее слово']]
markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hola! Готов учить испанские слова?", reply_markup=markup)

# Показывает случайное слово
async def next_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    word = random.choice(flashcards)
    context.user_data['current_word'] = word
    await update.message.reply_text(f"Слово на испанском: {word[0]}")

# Угадай перевод
async def guess_translation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'current_word' not in context.user_data:
        await update.message.reply_text("Сначала нажми 'Следующее слово'")
        return

    word, translation = context.user_data['current_word']
    options = [translation]

    while len(options) < 4:
        fake = random.choice(flashcards)[1]
        if fake not in options:
            options.append(fake)

    random.shuffle(options)
    keyboard = [[opt] for opt in options]
    markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

    context.user_data['answer'] = translation
    await update.message.reply_text(f"Как переводится '{word}'?", reply_markup=markup)

# Проверка ответа
async def handle_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_answer = update.message.text
    correct = context.user_data.get('answer')

    if correct and user_answer == correct:
        await update.message.reply_text("Правильно!")
    elif correct:
        await update.message.reply_text(f"Неправильно. Правильный ответ: {correct}")

    # Вернуть главные кнопки
    await update.message.reply_text("Что делаем дальше?", reply_markup=markup)
    context.user_data.pop('answer', None)

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex("Следующее слово"), next_word))
    app.add_handler(MessageHandler(filters.Regex("Угадать перевод"), guess_translation))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_response))

    app.run_polling()

if __name__ == '__main__':
    main()