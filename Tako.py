import os
import sys
from os.path import expanduser

from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon, QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QApplication, QWidget, QTreeView, QFileSystemModel, QVBoxLayout, QMainWindow, QListView, \
    QSplitter, QHBoxLayout, QColumnView
from PyQt5.QtCore import QModelIndex, QProcess, QSettings, Qt, QDir, QSysInfo, QStringListModel, QFileInfo

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

        self.current_path = []

        self.main_column = TakoColumn(self, "Home", expanduser('~'), 0)

        self.files_model = QtWidgets.QFileSystemModel()
        self.files_view = QColumnView()
        self.files_view.setModel(self.files_model)

        self.splitter = QSplitter()
        self.splitter.setOrientation(Qt.Horizontal)
        self.splitter.addWidget(self.main_column)
        self.splitter.addWidget(self.files_view)
        self.splitter.setSizes([20, 160])

        self.path_bar = QListView()
        self.path_bar.setFlow(QListView.Flow.LeftToRight)
        self.path_bar.setFixedHeight(30)

        self.path_model = QStandardItemModel()

        self.populate_path_bar(expanduser('~'))

        self.path_bar.setModel(self.path_model)

        layout = QVBoxLayout()
        layout.addWidget(self.path_bar)

        main_wid = QWidget()
        main_wid.setLayout(layout)

        hlay = QHBoxLayout()
        hlay.addWidget(self.splitter)
        wid = QWidget()
        wid.setLayout(hlay)

        layout.addWidget(wid)

        self.createStatusBar()
        self.setCentralWidget(main_wid)
        self.setGeometry(250, 150, 900, 500)

    def populate_path_bar(self, path: str):
        delimiter = os.path.sep if os.path.sep in path else '/'
        path_items = []
        self.path_model.removeRows(0, self.path_model.rowCount())
        for path_item in path.split(delimiter):
            path_items.append(('' if not path_items else path_items[-1]) + path_item + delimiter)
        for path_item in path_items:
            name = self.files_model.index(path_item).data()
            icon = self.files_model.iconProvider().icon(QFileInfo(path_item))

            self.path_model.appendRow(QStandardItem(icon, name))

    def createStatusBar(self):
        sysinfo = QSysInfo()
        myMachine = "current CPU Architecture: " + sysinfo.currentCpuArchitecture() + " *** " + sysinfo.prettyProductName() + " *** " + sysinfo.kernelType() + " " + sysinfo.kernelVersion()
        self.statusBar().showMessage(myMachine, 0)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = TakoWindow()
    w.show()
    if len(sys.argv) > 1:
        path = sys.argv[1]
        dprint(path)
    sys.exit(app.exec_())
