import sys
from xmlrpc.client import boolean
from PyQt5.QtWidgets import QMainWindow, QApplication
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
        self.ip = 'localhost'
        self.port = 5000
        self.host = 'http://%s:%s' % (self.ip, self.port)
        self.reconnect = False
        self.connStatus.connect(self.logging)
        self.sio.on('receive', self.receive)
        self.sio.on('listen', self.listen)
        self.sio.on('disconnect', self.server_disconnect)

    def set_host(self, ip, port):
        self.ip = ip
        self.port = port

    def run(self):
        self.connect(self.host)

    def connect(self, host):

        if not self.sio.connected:
            try:
                self.sio.connect(host)
                self.connStatus.emit(True)
            except socketio.exceptions.ConnectionError as err:
                self.connStatus.emit(False)
            self.sio.sleep(1)
        self.talk()

    # real time run only once
    def talk(self):
        if self.sio.connected:
            try:
                self.sio.emit('talk')
            except:
                self.connStatus.emit(False)
        else:
            self.connStatus.emit(False)
    
    # real time working itself
    def listen(self, msg):
        if self.sio.connected:
            if msg:
                self.add_log.emit('[Incoming]:%s' % (msg))
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
            if msg != {}:
                self.add_log.emit('[Server] %s' % (msg))
            else:
                self.add_log.emit('[Server] %s' %
                                  ("server message  is empty !"))

    def logging(self, status):
        if self.reconnect != status:
            self.reconnect = status
            self.add_log.emit('Connected to the server :)') if status else self.add_log.emit(
                'Server not found! Searching !...')

    def server_disconnect(self):
        print("I'm disconnected!")
    
    def client_disconnect(self):
        self.sio.disconnect()


class ChatWindow(QMainWindow, ui_form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # fill inputs for test
        self.INPUT_ip.setPlainText("localhost")
        self.INPUT_port.setPlainText("5000")
        self.connStatus = False
        self.flipImage = 0
        self.sc = SocketClient(self)
        self.sc.add_log.connect(self.add_chat)
        self.sc.dataUpdate.connect(self.read_values)
        self.sc.connStatus.connect(self.check_connection)

        self.BTN_connect.clicked.connect(self.socket_connection)
        self.BTN_send.clicked.connect(self.send_message)
        self.BTN_send.clicked.connect(self.send_message)
        self.BTN_home.clicked.connect(lambda: self.start_function("home"))
        self.BTN_clock.clicked.connect(lambda: self.start_function("clock"))
        self.BTN_weather.clicked.connect(
            lambda: self.start_function("weather"))
        self.BTN_camera.clicked.connect(lambda: self.start_function("camera"))
        self.BTN_scan.clicked.connect(lambda: self.start_function("scan"))
        self.BTN_capture.clicked.connect(
            lambda: self.start_function("capture"))
        self.running_function = "home"
        self.faces = [
            " ", "angry", "cool",
            "faceid_confirm", "faceid_error", "faceid_scan",
            "found", "funny", "listening",
            "love", "notfound", "nowifi",
            "recognise", "sad", "scan_confirm",
            "searching", "searchwifi",
            "wakeup", "yeswifi"]
        for face in self.faces:
            self.LIST_faces.addItem(face)
        self.LIST_faces.currentTextChanged.connect(self.change_face)

    def check_connection(self, status):
        self.connStatus = status
        if status:
            self.BTN_connect.setText("Disconnect")
        else:
            self.BTN_connect.setText("Connect")
        self.BTN_send.setEnabled(status)
        self.CONNECTION_BAR.setEnabled(not status)
        self.LED_connect.setPixmap(
            QPixmap('icons/led-green-on.png' if status else 'icons/led-red-on.png'))
        self.LED_rx_tx.setPixmap(QPixmap(
            'icons/rx-tx-on.png' if (self.flipImage % 2) == 0 else 'icons/rx-tx.png'))
        self.flipImage += 1

    def read_values(self, data):
        new_function = data['function_name']
        if self.running_function != new_function:
            if hasattr(self, "LED_"+new_function):
                led = getattr(self, "LED_"+new_function)
                led.setPixmap(QPixmap('icons/led-green-on.png'))
            if hasattr(self, "LED_"+"BTN_"+new_function):
                getattr(self, "BTN_"+new_function).setChecked(True)
              # change running function name to new one
            self.running_function = new_function
        for key, value in data.items():
            reading = "VALUE_"+key
            if hasattr(self, reading):
                getattr(self, reading).display(value)

    def start_function(self, new_function, data=""):
        # uncheck old button and led
        if self.running_function != new_function:
            if hasattr(self, "LED_"+self.running_function):
                led = getattr(self, "LED_"+self.running_function)
                led.setPixmap(QPixmap('icons/led-red-on.png'))
            if hasattr(self, "BTN_"+self.running_function):
                getattr(self, "BTN_"+self.running_function).setChecked(False)
      
        # send data to server
        print("sending function", new_function)
        package = {'function_name': new_function, 'data': data}
        self.send_message(package)

    def change_face(self, face):
        package = {'face': face}
        self.send_message(package)
        
    def socket_connection(self):
        ip = self.INPUT_ip.toPlainText()
        port = self.INPUT_port.toPlainText()
        if (not ip) or (not port):
            self.add_chat('The ip or port number is empty.')
            return
        self.sc.set_host(ip, port)

        if not self.connStatus:
            self.sc.start()
        if self.connStatus:
            self.sc.client_disconnect()


    def send_message(self, msg):
        if not self.connStatus:
            self.add_chat('Connection Lost!...')
            return
        if not msg:
            msg = self.INPUT_message.toPlainText()
            self.INPUT_message.setPlainText('')
        self.sc.send(msg)


  

    @pyqtSlot(object)
    def add_chat(self, msg):
        self.chats.appendPlainText(msg)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = ChatWindow()
    myWindow.setWindowTitle('Remote Command')
    myWindow.show()
    app.exec_()
