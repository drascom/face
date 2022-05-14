from PyQt5.QtCore import QObject, QThread, pyqtSignal
# Snip...

# Step 1: Create a worker class class Worker(QObject):
class Worker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def run(self):
        """Long-running task."""
        for i in range(5):
            self.progress.emit(i + 1)
        self.finished.emit()

class Window(QMainWindow):
    # Snip...
    def runLongTask(self):
        # Step 2: Create a QThread object
        self.thread = QThread()
        # Step 3: Create a worker object
        self.worker = Worker()
        # Step 4: Move worker to the thread
        self.worker.moveToThread(self.thread)
        # Step 5: Connect signals and slots
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.reportProgress)
        # Step 6: Start the thread
        self.thread.start()


class GenericWorker(QObject):
    def __init__(self, function, *args, **kwargs):
        super(GenericWorker, self).__init__()

        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.start.connect(self.run)

    start = pyqtSignal(str)

    @pyqtSlot()
    def run(self, some_string_arg):
        self.function(*self.args, **self.kwargs)