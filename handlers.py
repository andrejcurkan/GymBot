# handlers.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler, MessageHandler, filters, CallbackQueryHandler
from database import Client, get_db
from sqlalchemy.orm import Session

# Определяем состояния для ConversationHandler
NAME, LAST_NAME, SUBSCRIPTION = range(3)

# Клавиатура для выбора типа абонемента
def get_subscription_keyboard():
    keyboard = [
        [InlineKeyboardButton("3 месяца 🗓️", callback_data='3')],  # Эмодзи для срока
        [InlineKeyboardButton("6 месяцев 🗓️🗓️", callback_data='6')],
        [InlineKeyboardButton("12 месяцев 🗓️🗓️🗓️", callback_data='12')],
    ]
    return InlineKeyboardMarkup(keyboard)

# Клавиатура для меню
def get_menu_keyboard():
    keyboard = [
        ["🏋️‍♂️ Полезность спорта"],  # Эмодзи и текст
        ["⭐ Отзывы", "🛟 Поддержка", "💲 Сетка цен"],  # Эмодзи для каждой кнопки
        ["💳 Купить абонемент"]  # Эмодзи для кнопки покупки
    ]
    return ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

# Обработчик команды /start
async def start(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text(
        "🌟 *Добро пожаловать в бот по продаже абонементов в спортзал!* 🏋️‍♂️\n"
        "Выберите действие:",
        reply_markup=get_menu_keyboard(),
        parse_mode="Markdown"  # Включаем поддержку Markdown
    )
    return ConversationHandler.END

# Обработчик нажатия на кнопку "Купить абонемент"
async def buy(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text(
        "💳 *Купить абонемент*\n"
        "Введите ваше имя:",
        reply_markup=get_menu_keyboard(),
        parse_mode="Markdown"
    )
    return NAME

# Обработчик для ввода имени
async def get_name(update: Update, context: CallbackContext) -> int:
    context.user_data['first_name'] = update.message.text
    await update.message.reply_text(
        "📝 Введите вашу фамилию:",
        reply_markup=get_menu_keyboard()
    )
    return LAST_NAME

# Обработчик для ввода фамилии
async def get_last_name(update: Update, context: CallbackContext) -> int:
    context.user_data['last_name'] = update.message.text
    await update.message.reply_text(
        "🗓️ *Выберите тип абонемента:*",
        reply_markup=get_subscription_keyboard(),
        parse_mode="Markdown"
    )
    return SUBSCRIPTION

# Обработчик выбора типа абонемента
async def get_subscription(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()

    subscription_type = query.data
    context.user_data['subscription_type'] = subscription_type

    prices = {'3': 1000, '6': 1800, '12': 3000}
    price = prices.get(subscription_type, 0)
    if context.user_data.get('is_wholesale', False):
        price *= 0.9  # 10% скидка для оптовых покупателей

    context.user_data['balance'] = price
    await query.edit_message_text(
        f"💳 *Стоимость вашего абонемента:* {price} руб.\n"
        "Спасибо за покупку! 🎉",
        parse_mode="Markdown"
    )

    # Сохранение данных в базу через SQLAlchemy
    db: Session = next(get_db())
    try:
        # Проверяем, существует ли пользователь с таким chat_id
        existing_client = db.query(Client).filter(Client.chat_id == update.effective_user.id).first()

        if existing_client:
            # Если пользователь существует, обновляем его данные
            existing_client.first_name = context.user_data['first_name']
            existing_client.last_name = context.user_data['last_name']
            existing_client.subscription_type = subscription_type
            existing_client.balance = price
            existing_client.is_wholesale = context.user_data.get('is_wholesale', False)
        else:
            # Если пользователь не существует, создаем новую запись
            client = Client(
                chat_id=update.effective_user.id,
                first_name=context.user_data['first_name'],
                last_name=context.user_data['last_name'],
                subscription_type=subscription_type,
                balance=price,
                is_wholesale=context.user_data.get('is_wholesale', False)
            )
            db.add(client)

        db.commit()
        await query.message.reply_text(
            "✅ *Данные успешно сохранены!*",
            reply_markup=get_menu_keyboard(),
            parse_mode="Markdown"
        )
    except Exception as e:
        db.rollback()
        await query.message.reply_text(
            f"❌ *Ошибка при сохранении данных:* {e}",
            reply_markup=get_menu_keyboard(),
            parse_mode="Markdown"
        )
    finally:
        db.close()

    return ConversationHandler.END

# Обработчик для поддержки
async def support(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        "🛟 *Поддержка*\n"
        "Свяжитесь с нами через @support.",
        reply_markup=get_menu_keyboard(),
        parse_mode="Markdown"
    )

# Обработчик для отзывов
async def reviews(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        "⭐ *Отзывы*\n"
        "Здесь будут отзывы наших клиентов.",
        reply_markup=get_menu_keyboard(),
        parse_mode="Markdown"
    )

# Обработчик для цен
async def prices(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        "💲 *Сетка цен*\n"
        "Цены на абонементы:\n"
        "3 месяца - 1000 руб.\n"
        "6 месяцев - 1800 руб.\n"
        "12 месяцев - 3000 руб.",
        reply_markup=get_menu_keyboard(),
        parse_mode="Markdown"
    )

# Обработчик для меню
async def handle_menu(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    if text == '🏋️‍♂️ Полезность спорта':
        await update.message.reply_text(
            "🏋️‍♂️ *Полезность спорта*\n"
            "Спорт полезен для здоровья и улучшает качество жизни.",
            reply_markup=get_menu_keyboard(),
            parse_mode="Markdown"
        )
    elif text == '⭐ Отзывы':
        await reviews(update, context)
    elif text == '🛟 Поддержка':
        await support(update, context)
    elif text == '💲 Сетка цен':
        await prices(update, context)
    elif text == '💳 Купить абонемент':  # Обработка нажатия на кнопку "Купить абонемент"
        await buy(update, context)