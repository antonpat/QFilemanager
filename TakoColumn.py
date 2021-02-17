import os
from os.path import expanduser
from typing import List

from PyQt5 import QtCore
from PyQt5.QtCore import QDir, QModelIndex
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QListView, QFileSystemModel

class TakoColumn(QWidget):
    def __init__(self, parent: QWidget, title: str, root: str, level: int):
        super(TakoColumn, self).__init__()

        self.level = level
        self.parent = parent
        self.title_panel = QLabel()
        self.title_panel.setText(title)

        self.listview = QListView()

        layout = QVBoxLayout()
        layout.addWidget(self.title_panel)
        layout.addWidget(self.listview)
        self.setLayout(layout)

        # files panel
        # - model
        self.fileModel = QFileSystemModel()
        self.fileModel.setReadOnly(True)
        self.fileModel.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs | QDir.Files)
        self.fileModel.setResolveSymlinks(True)
        self.fileModel.setRootPath(root)
        # - view
        self.listview.setModel(self.fileModel)
        self.listview.setRootIndex(self.fileModel.index(root))

        self.sel_model = self.listview.selectionModel()
        self.sel_model.selectionChanged.connect(self.selection_changed)

    def selection_changed(self, selected):
        self.listview.selectionModel().clearSelection()
        if not selected.isEmpty():
            sel_index = self.sel_model.currentIndex()
            file_info = self.fileModel.fileInfo(sel_index)
            sel_path = file_info.absoluteFilePath()
            if file_info.isDir():
                self.parent.populate_path_bar(sel_path)

                self.parent.files_model.setRootPath(sel_path)
                idx = self.parent.files_model.index(sel_path)
                self.parent.files_view.setRootIndex(idx)



