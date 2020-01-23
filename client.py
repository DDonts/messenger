import requests
from datetime import datetime
import time
import threading

import os
import sys
import logging


def _append_run_path():         #чтоб не матюкалось про PATH при pyinstaller
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

from PyQt5 import QtWidgets, QtCore, QtGui
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
        thread = threading.Thread(target=self.update_messages)
        thread.start()
        self.ip = '192.168.1.103'

    def send_message(self, username, password, text):
        response = requests.post(
            f'http://samsapiel.pythonanywhere.com/auth',
            json={"username": username, "password": password}
        )
        if not response.json()['ok']:
            self.add_to_chat('Сообщение не отправлено\n')
            return

        response = requests.post(
            f'http://samsapiel.pythonanywhere.com/send',
            json={"username": username, "password": password, "text": text}
        )
        if not response.json()['ok']:
            self.add_to_chat('Сообщение не отправлено\n')

    def update_messages(self):
        last_time = 0
        while True:
            try:
                response = requests.get('http://samsapiel.pythonanywhere.com/messages',
                                        params={'after': last_time})
                messages = (response.json())["messages"]

                for message in messages:
                    beauty_time = datetime.fromtimestamp(message["time"])
                    beauty_time = beauty_time.strftime('%d/%m/%Y %H:%M:%S')
                    self.add_to_chat(message["username"] + ' ' + beauty_time)
                    self.add_to_chat(message["text"] + '\n')
                    last_time = message["time"]
            except:
                self.add_to_chat('Произошла ошибка при получении сообщений\n')
            time.sleep(1)

    def button_clicked(self):
        try:
            self.send_message(
                self.lineEdit_2.text(),
                self.lineEdit_3.text(),
                self.lineEdit.text()
            )
            time.sleep(1)
            self.textBrowser.moveCursor(QtGui.QTextCursor.End)
        except:
            self.add_to_chat('Произошла ошибка отправки\n')
        self.lineEdit.clear()

    def add_to_chat(self, text):
        self.mutex.acquire()
        self.textBrowser.append(text)
        self.mutex.release()




app = QtWidgets.QApplication([])
window = MessengerApp()
window.show()
app.exec_()

raise SystemExit()
