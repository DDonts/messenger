import requests
from datetime import datetime
import time
import threading
import os
import sys
import logging
import ast
import json
import re
def _append_run_path():  # чтоб не матюкалось про PATH при pyinstaller
    if getattr(sys, 'frozen', False):
        pathlist = []

        # If the application is run as a bundle, the pyInstaller bootloader
        # extends the sys module by a flag frozen=True and sets the app
        # path into variable _MEIPASS'.
        pathlist.append(sys._MEIPASS)

        # the application exe path
        _main_app_path = os.path.dirname(sys.executable)
        pathlist.append(_main_app_path)

        # append to system path enviroment
        os.environ["PATH"] += os.pathsep + os.pathsep.join(pathlist)

    logging.error("current PATH: %s", os.environ['PATH'])


_append_run_path()

from PyQt5 import QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import my_interface


class MessengerApp(QtWidgets.QMainWindow, my_interface.Ui_MainWindow):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setFixedSize(300, 335)
        self.pushButton.clicked.connect(self.button_clicked)
        self.lineEdit.returnPressed.connect(self.button_clicked)
        self.lineEdit_3.setEchoMode(self.lineEdit_3.Password)
        self.mutex = threading.Lock()
        self.thread = threading.Thread(target=self.update_messages)
        self.thread.start()
        self.ip = '192.168.1.103'
        self.vklucheno = True
        self.setWindowIcon(QIcon('icon.ico'))

    def send_message(self, username, password, text):
        response = requests.post(
            'http://samsapiel.pythonanywhere.com/auth',
            json={"username": username, "password": password}
        )
        if not response.json()['ok']:
            self.add_to_chat('Сообщение не отправлено/auth \n')
            return

        response = requests.post(
            f'http://samsapiel.pythonanywhere.com/send',
            json={"username": username, "password": password, "text": text}
        )
        if not response.json()['ok']:
            self.add_to_chat('Сообщение не отправлено/send \n')

    def update_messages(self):
        last_time = 0
        while True:
            try:
                response = requests.get('http://samsapiel.pythonanywhere.com/messages',
                                        params={'after': last_time})
                json_data = json.loads(response.text)['messages']
                for message in json_data:
                    beauty_time = datetime.fromtimestamp(float(ast.literal_eval(message)["time"])).strftime('%d/%m/%Y %H:%M:%S')
                    self.add_to_chat(ast.literal_eval(message)["user"] + ' ' + beauty_time)
                    self.add_to_chat(ast.literal_eval(message)["text"] + '\n')
                    last_time = ast.literal_eval(message)["time"]
            except:
                self.add_to_chat('Произошла ошибка при получении сообщений\n')
            time.sleep(1)
            if not self.vklucheno:
                break

    def closeEvent(self, event):
        self.vklucheno = False

    def button_clicked(self):
        regex = r"[:]"
        if re.match(regex, self.lineEdit_3.text()):
            self.add_to_chat('Пароль содержит запрещённые символы\n')
        elif self.lineEdit_2.text() and self.lineEdit_3.text():
            try:
                self.send_message(
                    self.lineEdit_2.text(),
                    self.lineEdit_3.text(),
                    self.lineEdit.text()
                )
                time.sleep(1)
                self.textBrowser.moveCursor(QTextCursor.End)  # QtGui
            except:
                self.add_to_chat('Произошла ошибка отправки\n')
        else:
            self.add_to_chat('Введите имя пользователя и пароль\n')

        self.lineEdit.clear()

    def add_to_chat(self, text):
        self.mutex.acquire()
        self.textBrowser.append(text)
        self.mutex.release()


app = QtWidgets.QApplication(sys.argv)
window = MessengerApp()
window.show()
app.exec_()
window.thread.join()
