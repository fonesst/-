import telebot
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
import time
import random

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Замените на ваш API токен
API_TOKEN = '7368730334:AAH9xUG8G_Ro8mvV_fDQxd5ddkwjxHnBoeg'

bot = telebot.TeleBot(API_TOKEN)

user_data = {}

def parse_text_with_name(url, full_name):
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
        
        # Ввод ФИО в поле поиска
        search_input = driver.find_element(By.CSS_SELECTOR, 'input[class="SearchNameInput_input__M6_k8"]')
        search_input.send_keys(full_name)
        logger.info(f"ФИО введено: {full_name}")
        
        # Пауза для обновления страницы после ввода текста
        time.sleep(5)  # Задержка в 5 секунд
        
        # Парсинг текста из указанного элемента
        try:
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'ul[class="SearchNameResults_content_rDYQT"]'))
            )
            parsed_text = element.text
            logger.info("Текст успешно спарсен")
            return parsed_text
        except:
            logger.error("Элемент не найден или не содержит текста")
            return "Информация не найдена"

    except Exception as e:
        logger.error(f"Произошла ошибка: {str(e)}")
        return "Произошла ошибка при поиске информации"

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
    
    parsed_text = parse_text_with_name(url, full_name)
    
    if parsed_text:
        bot.reply_to(message, f"Результаты поиска для {full_name}:\n\n{parsed_text}")
    else:
        bot.reply_to(message, "Произошла ошибка при поиске информации. Попробуйте снова.")

bot.polling()
