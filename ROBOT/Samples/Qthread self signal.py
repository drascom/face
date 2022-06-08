import threading,sys
from PyQt5.QtCore import (QCoreApplication, QObject, QRunnable, QThread,
                          QThreadPool, pyqtSignal, pyqtSlot)

class Worker(QObject):
    call_f1 = pyqtSignal(object)
    call_f2 = pyqtSignal()
    def __init__(self):
        super(Worker, self).__init__()
        self.call_f1.connect(self.f1)
        self.call_f2.connect(self.f2)

    @pyqtSlot(object)
    def f1(self,variable):
        print('f1',variable, threading.get_ident())
    
    @pyqtSlot()
    def f2(self):
        print('f2', threading.get_ident())

app = QCoreApplication([])
print('main', threading.get_ident())
my_thread = QThread()
my_thread.start()

my_worker = Worker()
# my_worker.call_f1.connect(my_worker.f1)
my_worker.moveToThread(my_thread)
my_worker.call_f1.emit("test")
# my_worker.call_f2.connect(my_worker.f2)
my_worker.call_f2.emit()
sys.exit(app.exec_())