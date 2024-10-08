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

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Замените на ваш API токен
API_TOKEN = '7368730334:AAH9xUG8G_Ro8mvV_fDQxd5ddkwjxHnBoeg'

bot = telebot.TeleBot(API_TOKEN)

user_data = {}

# Функция для создания скриншота и последующего парсинга текста из кнопок
def get_parsed_text(url, full_name):
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
        search_input = driver.find_element(By.CSS_SELECTOR, 'input[class="SearchNameInput_input__M6_k8"]')
        search_input.send_keys(full_name)
        logger.info(f"ФИО введено: {full_name}")
        
        # Пауза для обновления страницы после ввода текста
        time.sleep(5)  # Увеличенная задержка до 5 секунд для симуляции ожидания загрузки страницы

        # Создание полного скриншота страницы
        screenshot_path = 'full_page_screenshot.png'
        
        # Определяем размер страницы для создания полного скриншота
        S = lambda X: driver.execute_script('return document.body.parentNode.scroll'+X)
        driver.set_window_size(S('Width'), S('Height'))  # Задаём размер окна в зависимости от размеров страницы
        driver.save_screenshot(screenshot_path)
        logger.info("Полный скриншот сохранен.")
        
        # Поиск элементов кнопок с текстом результата
        buttons = driver.find_elements(By.CSS_SELECTOR, 'button[class="SearchNameResults_name_V2vWD"]')
        if buttons:
            # Собираем текст из каждой найденной кнопки
            parsed_text = "\n".join([button.text for button in buttons])
            logger.info(f"Распарсено {len(buttons)} кнопок с результатами.")
        else:
            logger.info("Результаты не найдены.")
            parsed_text = "Результаты не найдены."
        
        return parsed_text, screenshot_path

    except Exception as e:
        logger.error(f"Произошла ошибка: {str(e)}")
        return None, None

    finally:
        driver.quit()

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
    
    parsed_text, screenshot_path = get_parsed_text(url, full_name)
    
    if parsed_text:
        bot.reply_to(message, parsed_text)
        
        if screenshot_path:
            with open(screenshot_path, 'rb') as file:
                bot.send_photo(message.chat.id, file)
            os.remove(screenshot_path)
        else:
            bot.reply_to(message, "Произошла ошибка при создании скриншота.")
    else:
        bot.reply_to(message, "Произошла ошибка при получении данных. Попробуйте снова.")

# Запуск бота
bot.polling()
