import os
import configparser
import yadisk
from ftplib import FTP
from rich.console import Console
from rich.progress import track

# Инициализация основных переменных
config = configparser.ConfigParser()
config.read("config.ini", encoding="utf-8")
ya_token = config["YandexToken"]["token"]

console = Console()
y = yadisk.YaDisk(token=ya_token)
print(f'Проверка актуальности токена >>> {y.check_token()}')  # Проверим токен
# Считываем список файлов со всей служебной информацией
listing_photo = list(y.listdir("disk:/Варя фото"))
# Оставляем только имена файлов
listing_file_name = [file_name['name'] for file_name in listing_photo]
print(f'Обнаружено на ЯДиск {len(listing_file_name)} файлов')
print(f'Сканирование телефона ...')
# Подключаемся к телефону по FTP используя CX Проводник
ftp = FTP()
HOST = '192.168.45.108'
PORT = 6844
ftp.connect(HOST, PORT)
print(ftp.login('pc', '860327'))
# Заходим в нужную папку
ftp.cwd('sdcard/Pictures/Варя фото/')
# Получаем список файлов
filenames = ftp.nlst()
print(f'На телефоне обнаружено {len(filenames)} файлов.')
add_file_names = []
# Сравниваем списки на Диске и телефоне, все отличающиеся заносим в отдельный список на копирование
for tel_filenames in filenames:
    if tel_filenames not in listing_file_name:
        add_file_names.append(tel_filenames)
print(f'На ЯДиск отсутсвуют {len(add_file_names)} файлов')

for ff_name in track(add_file_names, description='Копирование ...'):
    # Копируем с телефона на ПК
    load_file = open(ff_name, 'wb')
    ftp.retrbinary('RETR '+ff_name, load_file.write, 1024)
    load_file.close()
    # Отправляем на сервер
    y.upload(ff_name, "disk:/Варя фото/"+ff_name)
    # Удаляем на ПК
    os.remove(ff_name)
    ftp.close()
