import sys
from xmlrpc.client import boolean
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QTableWidgetItem, QMessageBox, QApplication
from PyQt5.QtCore import QThread, QTimer, pyqtSlot
from PyQt5.QtGui import QPixmap
from PyQt5 import QtCore
from PyQt5 import uic

import socketio
import time

ui_form = uic.loadUiType("UI_client.ui")[0]


class SocketClient(QThread):
    add_log = QtCore.pyqtSignal(object)
    dataUpdate = QtCore.pyqtSignal(object)
    connStatus = QtCore.pyqtSignal(bool)
    sio = socketio.Client()

    def __init__(self, parent=None):
        super().__init__()
        self.main = parent
        self.ip = '192.168.2.19'
        self.port = 5000
        self.host = 'http://%s:%s' % (self.ip, self.port)

    def set_host(self, ip, port):
        self.ip = ip
        self.port = port

    def run(self):
        self.connect(self.host)

    def connect(self, host):
        SocketClient.sio.on('receive', self.receive)
        SocketClient.sio.on('listen', self.listen)
        try:
            SocketClient.sio.connect(host)
            self.connStatus.emit(True)
            self.add_log.emit('Connection to the server has been completed.')
        except socketio.exceptions.ConnectionError as err:
            self.add_log.emit('Server not found! Try again...')
            self.connStatus.emit(False)
        else:
            pass

    # real time
    def talk(self):
        if not SocketClient.sio.connected:
            self.connect(self.host)
        try:
            SocketClient.sio.emit('talk')
        except:
            self.connStatus.emit(False)

    # real time
    def listen(self, msg):
        if msg:
            self.connStatus.emit(True)
            # this data will process
            self.dataUpdate.emit(msg)
        else:
            self.connStatus.emit(False)

    # on demand
    def send(self, msg):
        try:
            SocketClient.sio.emit('send', msg)
            self.add_log.emit('[Me]:%s' % (msg))
        except:
            self.add_log.emit('[Server] %s' %
                              ("Cant send message to server"))
    # on demand

    def receive(self, msg):
        if msg:
            self.add_log.emit('[Server] %s' % (msg))
        else:
            self.add_log.emit('[Server] %s' %
                              ("server message  is empty !"))


class ChatWindow(QMainWindow, ui_form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # fill inputs for test
        self.INPUT_ip.setPlainText("192.168.2.19")
        self.INPUT_port.setPlainText("5000")
        self.BTN_send.setDisabled(True)
        self.BTN_disconnect.hide()
        self.BTN_send.clicked.connect(self.send_message)
        self.BTN_connect.clicked.connect(self.socket_connection)
        self.BTN_disconnect.clicked.connect(self.socket_quit)
        self.connStatus = False
        self.flipImage = 0
        self.sc = SocketClient(self)
        self.timer = QTimer()
        self.timer.timeout.connect(self.realtime_comminication)

        self.sc.add_log.connect(self.add_chat)
        self.sc.dataUpdate.connect(self.read_values)
        self.sc.connStatus.connect(self.enable_send_button)

    def enable_send_button(self, status):
        self.LED_connect.setPixmap(
            QPixmap('icons/led-green-on.png' if status else 'icons/led-red-on.png'))
        self.BTN_send.setEnabled(status)
        self.BTN_disconnect.show()
        self.CONNECTION_BAR.setEnabled(not status)
        self.connStatus = status
        self.LED_rx_tx.setPixmap(QPixmap(
            'icons/rx-tx-on.png' if (self.flipImage % 2) == 0 else 'icons/rx-tx.png'))
        self.flipImage += 1

    def read_values(self, data):
        for key, value in data.items():
            # set LED status
            led = "LED_"+key
            if hasattr(self, led):
                led = getattr(self, led)
                if value:
                    led.setPixmap(QPixmap('icons/led-green-on.png'))
                else:
                    led.setPixmap(QPixmap('icons/led-red-on.png'))
            # set Button Status
            button = "BTN_"+key
            if hasattr(self, button):
                getattr(self, button).setChecked(value)
            reading = "VALUE_"+key
            if hasattr(self, reading):
                getattr(self, reading).display(value)
            if key == "page":
                switcher = ["BTN_main",
                            "BTN_clock",
                            "BTN_weather"]
                for index, name in enumerate(switcher):
                    led = getattr(self, "LED_page_"+str(index))
                    if index == value:
                        getattr(self, switcher[index]).setChecked(True)
                        led.setPixmap(QPixmap('icons/led-green-on.png'))
                    else:
                        getattr(self, switcher[index]).setChecked(False)
                        led.setPixmap(QPixmap('icons/led-red-on.png'))
                # setattr(self, value, True if value else False)

    def socket_connection(self):
        ip = self.INPUT_ip.toPlainText()
        port = self.INPUT_port.toPlainText()

        if (not ip) or (not port):
            self.add_chat('The ip or port number is empty.')
            return

        self.sc.set_host(ip, port)

        if not self.connStatus:
            self.sc.start()
            self.timer.start(500)

    def socket_quit(self):
        sys.exit()

    def realtime_comminication(self):
        self.sc.talk()

    def send_message(self):
        if not self.connStatus:
            self.add_chat('Connection Lost!...')
            return

        msg = self.INPUT_message.toPlainText()
        self.sc.send(msg)
        self.INPUT_message.setPlainText('')

    @pyqtSlot(object)
    def add_chat(self, msg):
        self.chats.appendPlainText(msg)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = ChatWindow()
    myWindow.setWindowTitle('Remote Command')
    myWindow.show()
    app.exec_()
