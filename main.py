import requests
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# from bs4 import BeautifulSoup
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.firefox.options import Options

TOKEN = '1851851427:AAG31OKFZkRaQeL5pdeExUSvQ3yCzZE8pG4'  
LIMIT = 28.29
ticker_indexes = {
    'USDT': 1,
    'BTC': 2,
    'BNB': 3,
    'BUSD': 4,
    'ETH': 5,
    'DAI': 6
}
clients = {}
request_stop = False
limit = 28.29
current_value = None
current_chat_id = ''


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(update.effective_chat.id, "To start notifying when UAH more than 28.28 press Start")
    await context.bot.send_message(update.effective_chat.id, "You can set a new limit by command /limit. Example: /limit 28.15")
    await context.bot.send_message(update.effective_chat.id, "You can take a look at price changing by the next link: https://io.adafruit.com/closirr/feeds/binance-p2p-uah")



async def set_limit(update, context):
    global limit
    new_limit = float(context.args[0])
    if new_limit:
        limit = new_limit
        chat_id = update.effective_chat.id
        clients[chat_id] = {'limit': new_limit}
        context.bot.send_message(update.effective_chat.id, f"New limit is {new_limit}")

async def get_current(update, context):
    chat_id = update.effective_chat.id
    global current_chat_id
    current_chat_id = chat_id
    if chat_id not in clients:
        clients[chat_id] = {'limit': 28.28}
    current_p2p_rate = get_current_p2p_rate()
    message = f"Profit if sell 29000UAH:\np2p rate: {current_p2p_rate:.2f}"
    await context.bot.send_message(update.effective_chat.id, message)


# Получение текущей стоимости
def get_current_p2p_rate():
    try:
        current_p2p_rate = 28
        response = requests.get('https://api.binance.com/api/v3/depth?symbol=USDTUAH&limit=5')
        data = response.json()
        money = 29000
        mono_without_binance = money - money / 100 * 0.65
        mono = mono_without_binance - mono_without_binance / 100 * 0.075
        privat = mono - mono / 100 * 0.5
        return float(data['asks'][0][0])
        mono_res = mono / float(data['asks'][0][0]) * current_p2p_rate
        privat_res = privat / float(data['asks'][0][0]) * current_p2p_rate

        return f"Profit if sell 29000UAH:\np2p rate: {current_p2p_rate:.2f}\nmarketValue: {float(data['asks'][0][0]):.2f}\nmono: {mono_res:.2f}\nprivat: {privat_res:.2f}"
    except Exception as e:
        print(e)

# # Функция для мониторинга и оповещения
# def monitor_and_notify():
#     try:
#         options = Options()
#         options.headless = True
#         browser = webdriver.Firefox(options=options)
#         browser.get('https://p2p.binance.com/en/trade/sell/USDT')
#         time.sleep(1)
#         print('✅')
#         fiat = 'UAH'
#         browser.find_element(By.ID, 'C2Cfiatfilter_searhbox_fiat').click()
#         time.sleep(1)
#         browser.find_element(By.ID, fiat).click()
#         time.sleep(1)
#         print('✅')
#         is_new_order = True
#         last_order = None
#         while not request_stop:
#             time.sleep(1)
#             p2p_rate = scrape(browser)
#             if p2p_rate:
#                 print(f'Current p2p rate: {p2p_rate}')
#                 current_p2p_rate = get_current_p2p_rate()
#                 print(f'Current P2P rate: {current_p2p_rate}')
#                 for chat_id, client in clients.items():
#                     if current_value != client['lastOrder']:
#                         client['isNewOrder'] = True
#                 for chat_id, client in clients.items():
#                     if client['isNewOrder'] and current_value > client['limit']:
#                         if client['enabled']:
#                             bot.send_message(chat_id, f"Order higher than {client['limit']} was found! - {current_value}UAH")
#                             current_p2p_rate = get_current_p2p_rate()
#                             bot.send_message(chat_id, current_p2p_rate)
#                         client['isNewOrder'] = False
#                         client['lastOrder'] = current_value
#                 browser.refresh()
#                 time.sleep(8)
#     except Exception as e:
#         print(e)

# # Функция для извлечения данных с веб-страницы
# def scrape(browser):
#     try:
#         elements = browser.find_elements(By.CLASS_NAME, 'css-1ld4hhc')
#         if elements:
#             values = [float(element.text.replace(' UAH', '').replace(',', '')) for element in elements]
#             global current_value
#             current_value = min(values)
#             return current_value
#     except Exception as e:
#         print(e)

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    
    # Добавляем обработчики команд
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)
    limit_handler = CommandHandler("limit", set_limit)
    application.add_handler(limit_handler)
    current_handler = CommandHandler("getcurrent", get_current)
    application.add_handler(current_handler)

    
    application.run_polling()