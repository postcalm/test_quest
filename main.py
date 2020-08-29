import logging.handlers
import os
import sys
import uuid
from datetime import datetime

from tinkoff_voicekit_client import ClientSTT

audio = sys.argv[1]
phone_num = sys.argv[2]
w_db = bool(int(sys.argv[3]))
stage = int(sys.argv[4])

date = datetime.today().strftime('%Y-%m-%d %H:%M:%S')

sub_yes = ('да конечно', 'говорите', 'слушаю')
sub_no = ('нет', 'не могу', 'занят', 'неудобно')

API_KEY = '...'
SECRET_KEY = '...'


def recognition():
    client = ClientSTT(API_KEY, SECRET_KEY)

    audio_config = {
        'encoding': 'LINEAR16',
        'sample_rate_hertz': 8000,
        'num_channels': 1
    }

    try:
        with open(audio, 'rb') as source:
            responses = client.recognize(source, audio_config)
            for response in responses:
                alter = response['alternatives']
                end_time = response['end_time']
                transcript = alter[0]['transcript']

                if stage == 1:
                    if 'автоответчик' in transcript:
                        return 0, end_time
                    else: return 1, end_time
                elif stage == 2:
                    if any(sub in transcript for sub in sub_yes):
                        return 1, end_time
                    elif any(sub in transcript for sub in sub_no):
                        return 0, end_time
    except:
        MyExseption(f'Файл {audio} не найден')
        return -1, -1


def write_to_db(datetime_, uuid_, result, phone_, time_):
    import psycopg2.sql

    try:
        conn = psycopg2.connect(dbname='...', user='...',
                                password='...', host='...', port='...')

        values = [(..., datetime_, uuid_, result, phone_, time_)]
        cursor = conn.cursor()

        insert = psycopg2.sql.SQL('''INSERT INTO recognition 
        ("id", "datetime", "uuid", "result", "phone", "time") VALUES {}''').format(
            psycopg2.sql.SQL(',').join(map(psycopg2.sql.Literal, values)))
        cursor.execute(insert)
    except psycopg2.OperationalError:
        MyExseption('Неудалось подключиться к базе данных')
    except:
        MyExseption('Неудалось записать в базу данных')
    else:
        conn.commit()
        conn.close()


class MyExseption(Exception):
    def __init__(self, text):
        self.text = text

        err = logging.getLogger('err')
        formatter = logging.Formatter('%(message)s')
        err.setLevel(logging.ERROR)
        logFilePath = "error.log"
        file_handler = logging.handlers.TimedRotatingFileHandler(filename=logFilePath)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.ERROR)
        err.addHandler(file_handler)

        err.error(f'[{date}] {self.text}')


class Logs():
    def __init__(self, text):
        self.text = text

        log = logging.getLogger('log')
        formatter = logging.Formatter('%(message)s')
        log.setLevel(logging.INFO)
        logFilePath = "log.log"
        file_handler = logging.handlers.TimedRotatingFileHandler(filename=logFilePath)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)
        log.addHandler(file_handler)

        log.info(f'{self.text}')


res, time = recognition()
os.remove(audio)
id = uuid.uuid4().hex

if stage == 1:
    if res == 0:
        Logs(f'[{date}] {id} АО {phone_num} {time}')
        if w_db: write_to_db(date, id, 'AO', phone_num, time)

    elif res == 1:
        Logs(f'[{date}] {id} человек {phone_num} {time}')
        if w_db: write_to_db(date, id, 'человек', phone_num, time)

elif stage == 2:
    if res == 1:
        Logs(f'[{date}] {id} положительно {phone_num} {time}')
        if w_db: write_to_db(date, id, 'положительно', phone_num, time)

    elif res == 0:
        Logs(f'[{date}] {id} отрицательно {phone_num} {time}')
        if w_db: write_to_db(date, id, 'отрицательно', phone_num, time)

else:
    MyExseption('Не верное значение этапа распознавания')
