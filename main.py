import telebot
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import logging
import time
import random
from selenium.webdriver.common.by import By
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
    # ... (оставить без изменений)

def create_inline_keyboard(button_texts):
    # ... (оставить без изменений)

def parse_full_page_text(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        driver.get(url)
        logger.info(f"Загружена страница для парсинга: {url}")
        
        # Ждем, пока body не загрузится
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        # Получаем весь текст со страницы
        page_text = driver.find_element(By.TAG_NAME, "body").text
        
        logger.info("Текст успешно спарсен.")
        return page_text
    except Exception as e:
        logger.error(f"Ошибка при парсинге текста: {str(e)}")
        return None
    finally:
        driver.quit()

def clean_parsed_text(text):
    lines_to_remove = [
        "Отримати повну інформацію",
        "Видалення даних",
        "Telegram-перевірка",
        "ПІБ-пошук",
        "Пошук за номером",
        "dolg.xyz 2024",
        "Реєстр судових рішень",
        "Логін",
        "База ухилянтів",
        "Перевірка по номеру",
        "Умови користування",
        "Контакти",
        "Управління аккаунтом"
    ]
    
    cleaned_lines = [line for line in text.split('\n') if line.strip() and line.strip() not in lines_to_remove]
    return '\n'.join(cleaned_lines)

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

@bot.callback_query_handler(func=lambda call: call.data.startswith('parse_'))
def callback_query(call):
    transliterated_name = call.data.split('_', 1)[1]
    url = f"https://dolg.xyz/ukr/{transliterated_name}"
    
    bot.answer_callback_query(call.id, "Парсим информацию...")
    
    parsed_text = parse_full_page_text(url)
    
    if parsed_text:
        cleaned_text = clean_parsed_text(parsed_text)
        # Разделяем текст на части, если он слишком длинный
        max_message_length = 4096
        for i in range(0, len(cleaned_text), max_message_length):
            part = cleaned_text[i:i+max_message_length]
            bot.send_message(call.message.chat.id, part)
    else:
        bot.send_message(call.message.chat.id, "Произошла ошибка при парсинге информации.")

bot.polling()
