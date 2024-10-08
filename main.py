import telebot
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import os
import logging
import time
import random

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Замените на ваш API токен
API_TOKEN = 'YOUR_API_TOKEN'

bot = telebot.TeleBot(API_TOKEN)

user_data = {}

def take_screenshot_with_name(url, full_name):
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Открытие браузера в фоновом режиме
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        driver.get(url)
        logger.info(f"Загружена страница: {url}")
        time.sleep(random.uniform(2, 5))  # Случайная задержка после загрузки страницы
        
        # Ввод ФИО в поле поиска
        search_input = driver.find_element("css selector", 'input[class="SearchNameInput_input__M6_k8"]')
        search_input.send_keys(full_name)
        logger.info(f"ФИО введено: {full_name}")
        
        # Скриншот страницы после ввода ФИО
        time.sleep(3)  # Небольшая задержка для обновления страницы после ввода
        screenshot_path = 'page_screenshot.png'
        driver.save_screenshot(screenshot_path)
        logger.info("Скриншот сохранен")
        return screenshot_path

    except Exception as e:
        logger.error(f"Произошла ошибка: {str(e)}")
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
    
    screenshot_path = take_screenshot_with_name(url, full_name)
    
    if screenshot_path:
        with open(screenshot_path, 'rb') as file:
            bot.send_photo(message.chat.id, file)
        os.remove(screenshot_path)
    else:
        bot.reply_to(message, "Произошла ошибка при создании скриншота. Попробуйте снова.")

bot.polling()
