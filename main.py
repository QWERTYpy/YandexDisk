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
ya_path = config["YandexDisk"]["path"]
ftp_host = config["FTP"]["host"]
ftp_port = int(config["FTP"]["port"])
ftp_login = config["FTP"]["login"]
ftp_pass = config["FTP"]["pass"]
ftp_path = config["FTP"]["path"]

console = Console()
y = yadisk.YaDisk(token=ya_token)
print(f'Проверка актуальности токена >>> {y.check_token()}')  # Проверим токен
if y.check_token():
    # Считываем список файлов со всей служебной информацией
    listing_photo = list(y.listdir(ya_path))
    # Оставляем только имена файлов
    listing_file_name = [file_name['name'] for file_name in listing_photo]
    print(f'Обнаружено на ЯДиск {len(listing_file_name)} файлов')

    print(f'Сканирование телефона ...')
    # Подключаемся к телефону по FTP используя CX Проводник
    ftp = FTP()
    HOST = ftp_host
    PORT = ftp_port
    try:
        ftp.connect(HOST, PORT)
    except WindowsError:
        console.print("[red]Подключение не установлено, т.к. конечный компьютер отверг запрос на подключение[/red]")
    else:
        print(ftp.login(ftp_login, ftp_pass))
        # Заходим в нужную папку
        ftp.cwd(ftp_path)
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
            y.upload(ff_name, ya_path+"/"+ff_name)
            # Удаляем на ПК
            os.remove(ff_name)
        ftp.close()
            #ftp.quit()
else:
    console.print("[red] Проверьте токен. Доступ к ЯндексДиск отклонен[/red]")
    