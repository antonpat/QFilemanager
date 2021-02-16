import os
import sys
from os.path import expanduser

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QTreeView, QFileSystemModel, QVBoxLayout, QMainWindow, QListView, \
    QSplitter, QHBoxLayout
from PyQt5.QtCore import QModelIndex, QProcess, QSettings, Qt, QDir, QSysInfo

from TakoColumn import TakoColumn


def dprint(s):
    print(s, file=sys.stderr)


def get_stylesheet(self, name: str = 'stylesheet'):
    file_path = os.path.join(os.path.dirname(__file__), 'resources', f'{name}.css')
    with open(file_path, 'r') as css_file:
        stylesheet = css_file.read()
    return stylesheet


class TakoWindow(QMainWindow):
    def __init__(self):
        super(TakoWindow, self).__init__()
        self.setStyleSheet(get_stylesheet(self))
        self.setWindowTitle("Tako File Manager")
        self.setWindowIcon(QIcon.fromTheme("system- file-manager"))
        self.process = QProcess()
        self.clip = QApplication.clipboard()

        self.settings = QSettings("Tako", "Tako")

        self.hiddenEnabled = False

        self.columns = {}
        self.main_column = TakoColumn(self, "Home", expanduser('~'), 0)
        self.columns[0] = self.main_column

        self.splitter = QSplitter()
        self.splitter.setOrientation(Qt.Horizontal)
        self.splitter.addWidget(self.main_column)
        # self.splitter.setSizes([20, 160])
        hlay = QHBoxLayout()
        hlay.addWidget(self.splitter)
        wid = QWidget()
        wid.setLayout(hlay)
        self.createStatusBar()
        self.setCentralWidget(wid)
        self.setGeometry(0, 26, 900, 500)

    def createStatusBar(self):
        sysinfo = QSysInfo()
        myMachine = "current CPU Architecture: " + sysinfo.currentCpuArchitecture() + " *** " + sysinfo.prettyProductName() + " *** " + sysinfo.kernelType() + " " + sysinfo.kernelVersion()
        self.statusBar().showMessage(myMachine, 0)

    def add_column(self, column: TakoColumn):
        n = column.level
        self.columns[n] = column
        if len(self.columns) > n+1:
            self.columns = self.columns[:n]


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = TakoWindow()
    w.show()
    if len(sys.argv) > 1:
        path = sys.argv[1]
        dprint(path)
    sys.exit(app.exec_())
