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
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Замените на ваш API токен
API_TOKEN = '7368730334:AAH9xUG8G_Ro8mvV_fDQxd5ddkwjxHnBoeg'

bot = telebot.TeleBot(API_TOKEN)

user_data = {}

def transliterate_name(full_name):
    # Словарь для транслитерации (оставлен без изменений)
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

def get_parsed_text(url, full_name):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        driver.get(url)
        logger.info(f"Загружена страница: {url}")
        time.sleep(random.uniform(2, 5))
        
        search_input = driver.find_element(By.CSS_SELECTOR, 'input[class="SearchNameInput_input__M6_k8"]')
        search_input.send_keys(full_name)
        logger.info(f"ФИО введено: {full_name}")
        
        time.sleep(5)

        buttons = driver.find_elements(By.TAG_NAME, 'button')
        filtered_buttons = []
        if buttons:
            for button in buttons:
                button_text = button.text.strip()
                if button_text not in ["Пошук за П.І.Б.", "Пошук за телефоном"] and button_text:
                    filtered_buttons.append(button_text)
            
            if filtered_buttons:
                parsed_text = f"Вот найденные люди:\n" + "\n".join(filtered_buttons)
                logger.info(f"Распарсено {len(filtered_buttons)} кнопок.")
            else:
                logger.info("Нужные кнопки не найдены.")
                parsed_text = "Нужные кнопки не найдены."
        else:
            logger.info("Кнопки не найдены.")
            parsed_text = "Кнопки не найдены."
        
        return parsed_text, filtered_buttons

    except Exception as e:
        logger.error(f"Произошла ошибка: {str(e)}")
        return None, None

    finally:
        driver.quit()

def create_inline_keyboard(button_texts):
    keyboard = InlineKeyboardMarkup()
    for text in button_texts:
        transliterated_text = transliterate_name(text).replace("'", "")
        callback_data = f"screenshot_{transliterated_text}"
        keyboard.add(InlineKeyboardButton(text, callback_data=callback_data))
    return keyboard

def take_screenshot(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        driver.get(url)
        logger.info(f"Загружена страница для скриншота: {url}")
        time.sleep(5)  # Ждем загрузку страницы

        screenshot_path = 'screenshot.png'
        S = lambda X: driver.execute_script('return document.body.parentNode.scroll'+X)
        driver.set_window_size(S('Width'), S('Height'))
        driver.save_screenshot(screenshot_path)
        logger.info("Скриншот сохранен.")
        
        return screenshot_path
    except Exception as e:
        logger.error(f"Ошибка при создании скриншота: {str(e)}")
        return None
    finally:
        driver.quit()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Введите ваше ФИО для поиска на сайте.")

@bot.message_handler(func=lambda message: True)
def handle_name(message):
    user_data[message.chat.id] = message.text.strip()
    full_name = user_data[message.chat.id]
    url = "https://dolg.xyz"
    
    parsed_text, button_texts = get_parsed_text(url, full_name)
    
    if parsed_text and button_texts:
        bot.send_message(message.chat.id, parsed_text, reply_markup=create_inline_keyboard(button_texts))
    else:
        bot.reply_to(message, "Произошла ошибка при получении данных. Попробуйте снова.")

@bot.callback_query_handler(func=lambda call: call.data.startswith('screenshot_'))
def callback_query(call):
    transliterated_name = call.data.split('_', 1)[1]
    url = f"https://dolg.xyz/ukr/{transliterated_name}"
    
    bot.answer_callback_query(call.id, "Создаем скриншот...")
    
    screenshot_path = take_screenshot(url)
    
    if screenshot_path:
        with open(screenshot_path, 'rb') as file:
            bot.send_photo(call.message.chat.id, file)
        os.remove(screenshot_path)
    else:
        bot.send_message(call.message.chat.id, "Произошла ошибка при создании скриншота.")

bot.polling()
