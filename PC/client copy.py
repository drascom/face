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
        self.connStatus.connect(self.logging)
        self.reconnect = True

    def set_host(self, ip, port):
        self.ip = ip
        self.port = port

    def run(self):
        self.connect(self.host)

    def connect(self, host):
        if not self.sio.connected:
            self.sio.on('receive', self.receive)
            self.sio.on('listen', self.listen)
            try:
                self.sio.connect(host)
                self.connStatus.emit(True)
                # self.add_log.emit('Connection to the server has been completed.')
            except socketio.exceptions.ConnectionError as err:
                # self.add_log.emit('Server not found! Try again...')
                self.connStatus.emit(False)
            else:
                pass
            time.sleep(1)

    # real time
    def talk(self):
        if not self.sio.connected:
            try:
                self.sio.emit('talk')
            except:
                self.connStatus.emit(False)
        self.run()
    # real time

    def listen(self, msg):
        if socketio.sio.connected:
            if msg:
                self.connStatus.emit(True)
                # this data will process
                self.dataUpdate.emit(msg)
            else:
                self.connStatus.emit(False)

    # on demand
    def send(self, msg):
        try:
            self.sio.emit('send', msg)
            self.add_log.emit('[Me]:%s' % (msg))
        except:
            self.add_log.emit('[Server] %s' %
                              ("Cant send message to server"))

    # on demand
    def receive(self, msg):
        if self.sio.connected:
            if msg:
                self.add_log.emit('[Server] %s' % (msg))
            else:
                self.add_log.emit('[Server] %s' %
                                  ("server message  is empty !"))

    def logging(self, status):
        if self.reconnect != status:
            self.reconnect = status
            self.add_log.emit('Connected to the server :)') if status else self.add_log.emit(
                'Server not found! Searching !...')
class ChatWindow(QMainWindow, ui_form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # fill inputs for test
        self.INPUT_ip.setPlainText("192.168.2.19")
        self.INPUT_port.setPlainText("5000")
        self.BTN_send.setDisabled(True)
        self.BTN_disconnect.hide()
        self.BTN_disconnect.clicked.connect(self.socket_quit)
        self.connStatus = False
        self.flipImage = 0
        self.sc = SocketClient(self)
        self.timer = QTimer()
        self.timer.timeout.connect(self.realtime_comminication)
        self.sc.add_log.connect(self.add_chat)
        self.sc.dataUpdate.connect(self.read_values)
        self.sc.connStatus.connect(self.enable_send_button)

        self.BTN_camera.clicked.connect(
            lambda: self.start_function(['request_camera', self.BTN_camera.isChecked()]))
        self.BTN_main.clicked.connect(lambda: self.change_page(0))
        self.BTN_clock.clicked.connect(lambda: self.change_page(1))
        self.BTN_weather.clicked.connect(lambda: self.change_page(2))
        self.BTN_send.clicked.connect(self.send_message)
        self.BTN_connect.clicked.connect(self.socket_connection)

    def enable_send_button(self, status):
        self.connStatus = status
        if status:
            self.BTN_disconnect.show()
        else:
            self.BTN_disconnect.hide()
        self.BTN_send.setEnabled(status)
        self.CONNECTION_BAR.setEnabled(not status)
        self.LED_connect.setPixmap(
            QPixmap('icons/led-green-on.png' if status else 'icons/led-red-on.png'))

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
            # button = "BTN_"+key
            # if hasattr(self, button):
            #     getattr(self, button).setChecked(value)
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
            # realtime loop starts here
            self.timer.start(500)

    def socket_quit(self):
        self.sc.quit()
    
    def realtime_comminication(self):
        self.sc.talk()

        self.LED_rx_tx.setPixmap(QPixmap(
            'icons/rx-tx-on.png' if (self.flipImage % 2) == 0 else 'icons/rx-tx.png'))
        self.flipImage += 1

    def send_message(self, msg):
        if not self.connStatus:
            self.add_chat('Connection Lost!...')
            return
        if not msg:
            msg = self.INPUT_message.toPlainText()
            self.INPUT_message.setPlainText('')
        self.sc.send(msg)

    def change_page(self, page):
        package = {'page': page}
        self.send_message(package)

    def start_function(self, data):
        package = {'function_name': data[0], 'function_status': data[1]}
        self.send_message(package)

    @pyqtSlot(object)
    def add_chat(self, msg):
        self.chats.appendPlainText(msg)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = ChatWindow()
    myWindow.setWindowTitle('Remote Command')
    myWindow.show()
    app.exec_()
