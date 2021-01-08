import os
import time

import requests
import telegram
import logging
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(
    format='%(asctime)s; %(levelname)s; %(name)s; %(message)s',
    level=logging.INFO, filename='main.log', filemode='w'
)

PRAKTIKUM_TOKEN = os.getenv("PRAKTIKUM_TOKEN")
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
URL = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
HOMEWORK_STATUS = {
    'reviewing': 'Работа взята в ревью.',
    'approved': ('Ревьюеру всё понравилось,'
                 ' можно приступать к следующему уроку.'),
    'rejected': 'К сожалению в работе нашлись ошибки.'
}


def parse_homework_status(homework):
    homework_name = homework.get('homework_name')
    status = homework.get('status')
    if status not in HOMEWORK_STATUS:
        msg = f'Неизвестный статус {homework_name}.'
        logging.info(msg)
        return msg
    verdict = HOMEWORK_STATUS.get(status)
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    headers = {
        'Authorization': f'OAuth {PRAKTIKUM_TOKEN}',
    }
    params = {
        'from_date': current_timestamp,
    }
    try:
        homework_statuses = requests.get(URL, headers=headers, params=params)
        return homework_statuses.json()
    except Exception:
        return []


def send_message(message, bot_client):
    return bot_client.send_message(chat_id=CHAT_ID, text=message)


def main():
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    logging.debug("Бот запущен")
    current_timestamp = int(time.time())
    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(
                    parse_homework_status(new_homework.get('homeworks')[0]),
                    bot
                    )
                logging.info('Сообщение отправлено!')
            current_timestamp = new_homework.get('current_date',
                                                 current_timestamp)
            time.sleep(300)

        except Exception as e:
            logging.error(f'Бот столкнулся с ошибкой: {e}', exc_info=True)
            time.sleep(5)


if __name__ == '__main__':
    main()
