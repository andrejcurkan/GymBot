# keyboards.py
from telegram import ReplyKeyboardMarkup

def get_menu_keyboard():
    keyboard = [['Полезность спорта', 'Купить абонемент'], ['Отзывы', 'Поддержка', 'Сетка цен']]
    return ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)