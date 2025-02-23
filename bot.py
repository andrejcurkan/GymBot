# bot.py
from telegram.ext import Application, CommandHandler, ConversationHandler, MessageHandler, filters, CallbackQueryHandler
from config import BOT_TOKEN
from handlers import (
    start, buy, get_name, get_last_name, get_subscription,
    support, reviews, prices, handle_menu, NAME, LAST_NAME, SUBSCRIPTION
)
from database import init_db

def main() -> None:
    # Инициализация базы данных
    init_db()

    # Создание Application и передача токена бота
    application = Application.builder().token(BOT_TOKEN).build()

    # Обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("support", support))
    application.add_handler(CommandHandler("reviews", reviews))
    application.add_handler(CommandHandler("prices", prices))

    # Обработчик для покупки абонемента
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^Купить абонемент$'), buy)],  # Обработка нажатия на кнопку
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            LAST_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_last_name)],
            SUBSCRIPTION: [CallbackQueryHandler(get_subscription, pattern='^(3|6|12)$')],
        },
        fallbacks=[CommandHandler("start", start)],  # Возврат в меню после завершения
        per_message=False,  # Устанавливаем per_message=False
    )

    application.add_handler(conv_handler)

    # Обработчик для меню
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu))

    # Запуск бота
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()