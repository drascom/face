import sys
from xmlrpc.client import boolean
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QTableWidgetItem, QMessageBox, QApplication
from PyQt5.QtCore import QThread, QTimer, pyqtSlot
from PyQt5 import QtCore
from PyQt5 import uic

import socketio
import time

ui_form = uic.loadUiType("main.ui")[0]


class SocketClient(QThread):
    toServer = QtCore.pyqtSignal(object)
    fromServer = QtCore.pyqtSignal(object)
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
        try:
            SocketClient.sio.connect(host)
            self.connStatus.emit(True)
        except socketio.exceptions.ConnectionError as err:
            self.toServer.emit('Server not found! Try again...')
            self.connStatus.emit(False)
        else:
            self.toServer.emit('Connection to the server has been completed.')
    def send(self, msg):
        if not SocketClient.sio.connected:
            self.connect(self.host)
        try:
            SocketClient.sio.emit('send', msg)
            self.toServer.emit('[Me]:%s' % (msg))
            self.connStatus.emit(True)
        except:
            self.connStatus.emit(False)
            self.fromServer.emit('[Server] %s' % ("Cant send message to server"))

    def receive(self, msg):
        if msg:
            print("received from server", msg)
            self.fromServer.emit('[Server] %s' % (msg))
        else:
            print("server message  is empty !")


class ChatWindow(QMainWindow, ui_form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # fill inputs for test
        self.input_ip.setPlainText("192.168.2.19")
        self.input_port.setPlainText("5000")
        self.btn_send.setDisabled(True)
        self.btn_send.clicked.connect(self.send_message)
        self.btn_connect.clicked.connect(self.socket_connection)
        self.connStatus = False
        self.sc = SocketClient(self)


        self.sc.toServer.connect(self.add_chat)
        self.sc.fromServer.connect(self.add_chat)
        self.sc.connStatus.connect(self.enableSendButton)

    def enableSendButton(self,status):
        self.btn_send.setEnabled(status)
        self.btn_connect.setEnabled(not status)
        self.connStatus = status

    def socket_connection(self):
        ip = self.input_ip.toPlainText()
        port = self.input_port.toPlainText()

        if (not ip) or (not port):
            self.add_chat('The ip or port number is empty.')
            return

        self.sc.set_host(ip, port)

        if not self.connStatus:
            self.sc.start()

    def send_message(self):
        if not self.connStatus:
            self.add_chat('Connection Lost!...')
            return

        msg = self.input_message.toPlainText()
        self.sc.send(msg)
        self.input_message.setPlainText('')

    @pyqtSlot(object)
    def add_chat(self, msg):
        self.chats.appendPlainText(msg)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = ChatWindow()
    myWindow.setWindowTitle('Remote Command')
    myWindow.show()
    app.exec_()
