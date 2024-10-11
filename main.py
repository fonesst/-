import telebot
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import os
import logging
import time
import random
from selenium.webdriver.common.by import By
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Замените на ваш API токен
API_TOKEN = '7368730334:AAH9xUG8G_Ro8mvV_fDQxd5ddkwjxHnBoeg'

bot = telebot.TeleBot(API_TOKEN)

user_data = {}

# Функция для транслитерации ФИО и формирования URL
def transliterate_name(full_name):
    translit_dict = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'h', 'ґ': 'g', 'д': 'd', 'е': 'e', 'є': 'ie',
        'ж': 'zh', 'з': 'z', 'и': 'y', 'і': 'i', 'ї': 'i', 'й': 'i', 'к': 'k', 'л': 'l',
        'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
        'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch', 'ь': '',
        'ю': 'iu', 'я': 'ia',
        'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'H', 'Ґ': 'G', 'Д': 'D', 'Е': 'E', 'Є': 'Ie',
        'Ж': 'Zh', 'З': 'Z', 'И': 'Y', 'І': 'I', 'Ї': 'I', 'Й': 'I', 'К': 'K', 'Л': 'L',
        'М': 'M', 'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U',
        'Ф': 'F', 'Х': 'Kh', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Shch', 'Ь': '',
        'Ю': 'Iu', 'Я': 'Ia'
    }
    
    transliterated = ''.join(translit_dict.get(char, char) for char in full_name)
    formatted_name = transliterated.lower().replace(" ", "_")
    return formatted_name

# Функция для парсинга страницы и создания скриншота
def get_screenshot_from_url(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        driver.get(url)
        logger.info(f"Загружена страница: {url}")
        time.sleep(random.uniform(2, 5))  # Случайная задержка после загрузки страницы
        
        screenshot_path = 'full_page_screenshot.png'
        S = lambda X: driver.execute_script('return document.body.parentNode.scroll'+X)
        driver.set_window_size(S('Width'), S('Height'))
        driver.save_screenshot(screenshot_path)
        logger.info("Полный скриншот сохранен.")
        
        return screenshot_path

    except Exception as e:
        logger.error(f"Произошла ошибка: {str(e)}")
        return None

    finally:
        driver.quit()

# Функция для создания инлайн-кнопок
def create_inline_keyboard(button_texts):
    keyboard = InlineKeyboardMarkup()
    for text in button_texts:
        transliterated_text = transliterate_name(text)
        callback_data = transliterated_text  # Используем транслитерированное имя в качестве callback_data
        keyboard.add(InlineKeyboardButton(text, callback_data=callback_data))
    return keyboard

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Введите ваше ФИО для поиска на сайте.")

# Обработчик сообщений, принимающий ФИО пользователя
@bot.message_handler(func=lambda message: True)
def handle_name(message):
    user_data[message.chat.id] = message.text.strip()
    full_name = user_data[message.chat.id]
    url = "https://dolg.xyz"
    
    parsed_text, button_texts, _ = get_parsed_text(url, full_name)
    
    if parsed_text and button_texts:
        bot.send_message(message.chat.id, parsed_text, reply_markup=create_inline_keyboard(button_texts))
    else:
        bot.reply_to(message, "Произошла ошибка при получении данных. Попробуйте снова.")

# Обработчик нажатий на инлайн-кнопки
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call: CallbackQuery):
    full_name = call.data
    url = f"https://dolg.xyz/ukr/{full_name}"
    
    bot.answer_callback_query(call.id, text="Выполняю переход по ссылке и создаю скриншот...")
    
    screenshot_path = get_screenshot_from_url(url)
    
    if screenshot_path:
        with open(screenshot_path, 'rb') as file:
            bot.send_photo(call.message.chat.id, file)
        os.remove(screenshot_path)
    else:
        bot.send_message(call.message.chat.id, "Произошла ошибка при создании скриншота.")

# Запуск бота
bot.polling()
