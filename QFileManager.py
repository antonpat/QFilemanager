#!/usr/bin/python3
# -*- coding: utf-8 -*-

############################################
## Copyright (C) 2013 Riverbank Computing Limited.
## Copyright (C) 2010 Nokia Corporation and/or its subsidiary(-ies).
## made by Axel Schneider * https://github.com/Axel-Erfurt/
## August 2019
############################################
# 1. stdlib
import sys
import os
import errno
import getpass
import socket
import shutil
import subprocess
import stat
from zipfile import ZipFile
from enum import Enum
import time
class Enabled(Enum):
#    trash = True
#    webview = True
    txtedit = True
    vplay = True
    aplay = True
    imgview = True
# 2. PyQt
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.Qt import QKeySequence, QCursor, QDesktopServices
# 3. 3rd parties
try:
    from send2trash import send2trash
except ModuleNotFoundError:
    Enabled.trash = False
    print("Trash not found", file=sys.stderr)
else:
    Enabled.trash = True
# 4. selfmade
import findFilesWindow
from plugins import QTextEdit
from plugins import Qt5Player
from plugins import QAudioPlayer
from plugins import QImageViewer
try:
    from plugins import QWebViewer
except ImportError:
    Enabled.webview = False
    print("Web not found", file=sys.stderr)
else:
    Enabled.webview = True
from plugins import QTerminalFolder

TREEVIEW = True

def dprint(s):
    print(s, file=sys.stderr)

class helpWindow(QMainWindow):
    def __init__(self):
        super(helpWindow, self).__init__()
        self.setStyleSheet(get_stylesheet(myWindow()))
        self.helpText = """<p style=" margin-top:2px; margin-bottom:2px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><!--StartFragment--><span style=" font-family:'Helvetica'; font-size:11pt; font-weight:600; text-decoration: underline; color:#2e3436;">Shortcuts:</span></p><br>
<p style=" margin-top:2px; margin-bottom:2px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:'Helvetica'; font-size:10pt; color:#2e3436;">rename File (F2)</span></p>
<p style=" margin-top:2px; margin-bottom:2px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:'Helvetica'; font-size:10pt; color:#2e3436;">copy File(s) (Ctrl-C)</span></p>
<p style=" margin-top:2px; margin-bottom:2px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:'Helvetica'; font-size:10pt; color:#2e3436;">paste File(s) (Ctrl-V)</span></p>
<p style=" margin-top:2px; margin-bottom:2px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:'Helvetica'; font-size:10pt; color:#2e3436;">cut File(s) (Ctrl-X)</span></p>
<p style=" margin-top:2px; margin-bottom:2px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:'Helvetica'; font-size:10pt; color:#2e3436;">open with TextEditor (F6)</span></p>
<p style=" margin-top:2px; margin-bottom:2px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:'Helvetica'; font-size:10pt; color:#2e3436;">move File(s) to Trash(Del)</span></p>
<p style=" margin-top:2px; margin-bottom:2px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:'Helvetica'; font-size:10pt; color:#2e3436;">delete File(s) (Shift+Del)</span></p>
<p style=" margin-top:2px; margin-bottom:2px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:'Helvetica'; font-size:10pt; color:#2e3436;">find File(s) (Ctrl-F)</span></p>
<p style=" margin-top:2px; margin-bottom:2px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:'Helvetica'; font-size:10pt; color:#2e3436;">play with vlc (F3)</span></p>
<p style=" margin-top:2px; margin-bottom:2px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:'Helvetica'; font-size:10pt; color:#2e3436;">open folder in Terminal (F7)</span></p>
<p style=" margin-top:2px; margin-bottom:2px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:'Helvetica'; font-size:10pt; color:#2e3436;">execute File in Terminal (F8)</span>
<p style=" margin-top:2px; margin-bottom:2px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:'Helvetica'; font-size:10pt; color:#2e3436;">go back (Backspace)</span></p>
<p style=" margin-top:2px; margin-bottom:2px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:'Helvetica'; font-size:10pt; color:#2e3436;">refresh View (F5)</span></p>
<!--EndFragment--></p>
                                        """
        self.helpViewer = QLabel(self.helpText, self)
        self.helpViewer.setAlignment(Qt.AlignCenter)
        self.btnAbout = QPushButton("about")
        self.btnAbout.setFixedWidth(80)
        self.btnAbout.setIcon(QIcon.fromTheme("help-about"))
        self.btnAbout.clicked.connect(self.aboutApp)

        self.btnClose = QPushButton("Close")
        self.btnClose.setFixedWidth(80)
        self.btnClose.setIcon(QIcon.fromTheme("window-close"))
        self.btnClose.clicked.connect(self.close)

        widget = QWidget(self)
        layout = QVBoxLayout(widget)

        layout.addWidget(self.helpViewer)
        layout.addStretch()
        layout.addWidget(self.btnAbout, alignment=Qt.AlignCenter)
        layout.addWidget(self.btnClose, alignment=Qt.AlignCenter)
        self.setCentralWidget(widget)

        #        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowTitle("Help")
        self.setWindowIcon(QIcon.fromTheme("help-about"))

    def aboutApp(self):
        sysinfo = QSysInfo()
        myMachine = "currentCPU Architecture: " + sysinfo.currentCpuArchitecture() + "<br>" + sysinfo.prettyProductName() + "<br>" + sysinfo.kernelType() + " " + sysinfo.kernelVersion()
        title = "about QFileManager"
        message = """
                    <span style='color: #3465a4; font-size: 20pt;font-weight: bold;text-align: center;'
                    ></span></p><center><h3>QFileManager<br>1.0 Beta</h3></center>created by  
                    <a title='Axel Schneider' href='http://goodoldsongs.jimdo.com' target='_blank'>Axel Schneider</a> with PyQt5<br><br>
                    <span style='color: #555753; font-size: 9pt;'>©2019 Axel Schneider<br><br></strong></span></p>
                        """ + myMachine
        self.infobox(title, message)

    def infobox(self, title, message):
        QMessageBox(QMessageBox.Information, title, message, QMessageBox.NoButton, self,
                    Qt.Dialog | Qt.NoDropShadowWindowHint | Qt.FramelessWindowHint).show()


class myWindow(QMainWindow):
    def __init__(self):
        super(myWindow, self).__init__()

        self.setStyleSheet(get_stylesheet(self))
        self.setWindowTitle("Filemanager")
        self.setWindowIcon(QIcon.fromTheme("system- file-manager"))
        self.process = QProcess()
        self.clip = QApplication.clipboard()

        self.settings = QSettings("QFileManager", "QFileManager")
        self.isInEditMode = False
        self.cut = False
        self.hiddenEnabled = False
        self.folder_copied = ""
        self.copyPath = ""
        self.copyList = []
        self.copyListNew = ""
        path = QDir.rootPath()

        # GUI
        self.treeview = QTreeView()
        if TREEVIEW:
            self.listview = QTreeView()
        else:
            self.listview = QListView()
        self.splitter = QSplitter()
        self.splitter.setOrientation(Qt.Horizontal)
        self.splitter.addWidget(self.treeview)
        self.splitter.addWidget(self.listview)
        self.splitter.setSizes([20, 160])
        hlay = QHBoxLayout()
        hlay.addWidget(self.splitter)
        wid = QWidget()
        wid.setLayout(hlay)
        self.createStatusBar()
        self.setCentralWidget(wid)
        self.setGeometry(0, 26, 900, 500)

        self.createActions()

        # main menu
        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('&File')
        fileMenu.addAction(self.actionFolderNewWin)
        fileMenu.addAction(self.actionFolderNew)
        fileMenu.addAction(self.actionFolderRename)
        fileMenu.addAction(self.actionFolderDel)
        fileMenu.addSeparator()
        fileMenu.addAction(self.actionFileOpen)
        fileOpenMenu = fileMenu.addMenu('Open...')
        fileOpenMenu.addAction(self.actionOpenText)
        fileOpenMenu.addAction(self.actionOpenTextRoot)
        fileOpenMenu.addAction(self.actionOpenImg)
        fileOpenMenu.addAction(self.actionOpenTerm)
        fileMenu.addAction(self.actionFileRename)
        fileMenu.addAction(self.actionFile2Trash)
        fileMenu.addAction(self.actionFileDel)
        fileMenu.addSeparator()
        fileMenu.addAction(self.actionMkExec)
        fileMenu.addSeparator()
        fileMenu.addAction(self.actionExit)
        editMenu = menuBar.addMenu('&Edit')
        editMenu.addAction(self.actionFolderCopy)
        editMenu.addAction(self.actionFolderPaste)
        editMenu.addSeparator()
        editMenu.addAction(self.actionFileCut)
        editMenu.addAction(self.actionFileCopy)
        editMenu.addAction(self.actionFilePaste)
        viewMenu = menuBar.addMenu('&View')
        viewMenu.addAction(self.actionHide)
        viewMenu.addAction(self.actionRefresh)
        goMenu = menuBar.addMenu('&Navigate')
        goMenu.addAction(self.actionGoBack)
        goMenu.addAction(self.actionGoUp)
        goMenu.addAction(self.actionGoHome)
        goMenu.addAction(self.actionGoDocuments)
        goMenu.addAction(self.actionGoDownloads)
        goMenu.addAction(self.actionGoMusic)
        goMenu.addAction(self.actionGoVideo)
        menuHelp = menuBar.addMenu('&Help')
        menuHelp.addAction(self.actionHelp)

        # toolbar
        self.tBar = self.addToolBar("Tools")
        self.tBar.setContextMenuPolicy(Qt.PreventContextMenu)
        self.tBar.setMovable(False)
        self.tBar.setIconSize(QSize(16, 16))
        self.tBar.addAction(self.actionFolderNew)
        self.tBar.addAction(self.actionFolderCopy)
        self.tBar.addAction(self.actionFolderPaste)
        self.tBar.addSeparator()
        self.tBar.addAction(self.actionFileCopy)
        self.tBar.addAction(self.actionFileCut)
        self.tBar.addAction(self.actionFilePaste)
        self.tBar.addAction(self.actionFile2Trash)
        self.tBar.addAction(self.actionFileDel)
        self.tBar.addSeparator()
        self.tBar.addAction(self.actionGoHome)
        self.tBar.addAction(self.actionGoBack)
        self.tBar.addAction(self.actionGoUp)
        self.tBar.addAction(self.actionGoDocuments)
        self.tBar.addAction(self.actionGoDownloads)
        # (fast find)
        self.findfield = QLineEdit()
        self.findfield.addAction(QIcon.fromTheme("edit-find"), QLineEdit.LeadingPosition)
        self.findfield.setClearButtonEnabled(True)
        self.findfield.setFixedWidth(150)
        self.findfield.setPlaceholderText("find")
        self.findfield.setToolTip("press RETURN to find")
        self.findfield.setText("")
        self.findfield.returnPressed.connect(self.findFiles)
        self.findfield.installEventFilter(self)
        self.tBar.addWidget(self.findfield)
        # /toolbar

        # tree panel
        # - model
        self.dirModel = QFileSystemModel()
        self.dirModel.setReadOnly(False)
        self.dirModel.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs | QDir.Drives)
        self.dirModel.setRootPath(QDir.rootPath())
        # - view
        self.treeview.setModel(self.dirModel)
        self.treeview.hideColumn(1)
        self.treeview.hideColumn(2)
        self.treeview.hideColumn(3)
        self.treeview.setRootIsDecorated(True)
        self.treeview.setSortingEnabled(True)
        self.treeview.setRootIndex(self.dirModel.index(path))
        #        self.treeview.clicked.connect(self.on_clicked)
        self.treeview.selectionModel().selectionChanged.connect(self.on_selectionChanged)
        #        self.treeview.expand(self.treeview.currentIndex())
        self.treeview.setTreePosition(0)
        self.treeview.setUniformRowHeights(True)
        self.treeview.setExpandsOnDoubleClick(True)
        self.treeview.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.treeview.setIndentation(12)
        self.treeview.setDragDropMode(QAbstractItemView.DragDrop)
        self.treeview.setDragEnabled(True)
        self.treeview.setAcceptDrops(True)
        self.treeview.setDropIndicatorShown(True)
        self.treeview.sortByColumn(0, Qt.AscendingOrder)
        # files panel
        # - model
        self.fileModel = QFileSystemModel()
        self.fileModel.setReadOnly(False)
        self.fileModel.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs | QDir.Files)
        self.fileModel.setResolveSymlinks(True)
        # - view
        self.listview.setModel(self.fileModel)
        if TREEVIEW:
            self.listview.header().resizeSection(0, 320)
            self.listview.header().resizeSection(1, 80)
            self.listview.header().resizeSection(2, 80)
            self.listview.setSortingEnabled(True)
            self.listview.doubleClicked.connect(self.list_doubleClicked)
        else:   # QListView
            # alternatingRowColors=true, , showDropIndicator=false
            self.listview.setWrapping(True)
            self.listview.setResizeMode(QListView.Adjust)
            self.listview.setModelColumn(0)
            self.listview.activated.connect(self.list_doubleClicked)
        self.listview.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.listview.setDragDropMode(QAbstractItemView.DragDrop)
        self.listview.setDragEnabled(True)
        self.listview.setAcceptDrops(True)
        self.listview.setDropIndicatorShown(True)
        self.listview.setEditTriggers(QAbstractItemView.NoEditTriggers)
        #self.listview.setIndentation(10)
        #self.listview.sortByColumn(0, Qt.AscendingOrder)
        # setup panels
        docs = QStandardPaths.standardLocations(QStandardPaths.DocumentsLocation)[0]
        self.treeview.setCurrentIndex(self.dirModel.index(docs))

        dprint("Welcome to QFileManager")
        self.readSettings()
        self.enableHidden()
        self.getRowCount()

    def closeEvent(self, e):
        dprint("writing settings ...\nGoodbye ...")
        self.writeSettings()

    ### utilities
    def readSettings(self):
        dprint("reading settings ...")
        if self.settings.contains("pos"):
            pos = self.settings.value("pos", QPoint(200, 200))
            self.move(pos)
        else:
            self.move(0, 26)
        if self.settings.contains("size"):
            size = self.settings.value("size", QSize(800, 600))
            self.resize(size)
        else:
            self.resize(800, 600)
        if self.settings.contains("hiddenEnabled"):
            if self.settings.value("hiddenEnabled") == "false":
                self.hiddenEnabled = True
            else:
                self.hiddenEnabled = False

    def writeSettings(self):
        self.settings.setValue("pos", self.pos())
        self.settings.setValue("size", self.size())
        self.settings.setValue("hiddenEnabled", self.hiddenEnabled, )

    def getRowCount(self):
        count = 0
        index = self.treeview.selectionModel().currentIndex()
        path = QDir(self.dirModel.fileInfo(index).absoluteFilePath())
        count = len(path.entryList(QDir.Files))
        self.statusBar().showMessage("%s %s" % (count, "Files"), 0)
        return count

    ### actions
    def createActions(self):
        # icon, title, action
        self.actionExit = QAction(QIcon.fromTheme("quit"), "&Quit", triggered=qApp.quit)
        # go
        self.actionGoBack = QAction(QIcon.fromTheme("go-back"), "&Back", triggered=self.goBack)
        self.actionGoUp = QAction(QIcon.fromTheme("go-up"), "&Up", triggered=self.goUp)
        self.actionGoHome = QAction(QIcon.fromTheme("go-home"), "&Home", triggered=self.goHome)
        self.actionGoDocuments = QAction(QIcon.fromTheme("folder-documents"), "Documents", triggered=self.goDocuments)
        self.actionGoDownloads = QAction(QIcon.fromTheme("folder-downloads"), "Downloads", triggered=self.goDownloads)
        self.actionGoMusic = QAction(QIcon.fromTheme("folder-music"), "&Music", triggered=self.goMusic)
        self.actionGoVideo = QAction(QIcon.fromTheme("folder-video"), "&Video", triggered=self.goVideo)
        #
        # folder/file manipulations
        # - common
        # - folder
        self.actionFolderNewWin = QAction(QIcon.fromTheme("folder-new"), "open in new window", triggered=self.openNewWin)
        self.actionFolderNew = QAction(QIcon.fromTheme("folder-new"), "Folder create", triggered=self.createNewFolder)
        self.actionFolderRename = QAction(QIcon.fromTheme("accessories-text-editor"), "Folder rename", triggered=self.renameFolder)
        self.actionFolderDel = QAction(QIcon.fromTheme("edit-delete"), "Folder delete", triggered=self.deleteFolder)
        self.actionFolderCopy = QAction(QIcon.fromTheme("edit-copy"), "Folder copy", triggered=self.copyFolder)
        self.actionFolderPaste = QAction(QIcon.fromTheme("edit-paste"), "Folder paste", triggered=self.pasteFolder)
        # - file
        self.actionFileOpen = QAction(QIcon.fromTheme("system-run"), "open File", triggered=self.openFile)
        self.actionFileRename = QAction(QIcon.fromTheme("accessories-text-editor"), "rename File", triggered=self.renameFile)
        self.actionFileDel = QAction(QIcon.fromTheme("edit-delete"), "delete File(s)", triggered=self.deleteFile)
        self.actionFile2Trash = QAction(QIcon.fromTheme("user-trash"), "move to trash", triggered=self.deleteFileTrash)
        self.actionFileCut = QAction(QIcon.fromTheme("edit-cut"), "cut File(s)", triggered=self.cutFile)
        self.actionFileCopy = QAction(QIcon.fromTheme("edit-copy"), "copy File(s)", triggered=self.copyFile)
        self.actionFilePaste = QAction(QIcon.fromTheme("edit-paste"), "paste File(s) / Folder", triggered=self.pasteFile)
        # misc
        self.actionMkExec = QAction(QIcon.fromTheme("applications-utilities"), "make executable", triggered=self.makeExecutable)
        self.actionHide = QAction("show hidden Files", triggered=self.enableHidden)
        self.actionRefresh = QAction(QIcon.fromTheme("view-refresh"), "refresh View", triggered=self.refreshList, shortcut="F5")
        self.actionFindFiles = QAction(QIcon.fromTheme("edit-find"), "find in folder", triggered=self.findFiles)
        self.actionHelp = QAction(QIcon.fromTheme("help"), "Help", triggered=self.showHelp)
        # open/plugins
        # - folder
        self.actionFolderZip = QAction(QIcon.fromTheme("zip"), "create zip from folder", triggered=self.createZipFromFolder)
        self.actionFolderTerm = QAction(QIcon.fromTheme("terminal"), "open folder in Terminal", triggered=self.showInTerminal)
        self.playlistAction = QAction(QIcon.fromTheme("audio-x-generic"), "make playlist from all mp3 files", triggered=self.makePlaylist)
        # - files
        self.actionOpenText = QAction(QIcon.fromTheme("system-run"), "open File with built-in Texteditor", triggered=self.openFileText)
        self.actionOpenTextRoot = QAction(QIcon.fromTheme("applications-system"), "edit as root", triggered=self.openFileTextRoot)
        self.actionOpenImg = QAction(QIcon.fromTheme("image-x-generic"), "show Image", triggered=self.showImage)
        self.actionOpenUrl = QAction(QIcon.fromTheme("browser"), "preview Page", triggered=self.showURL)
        self.actionOpenDB = QAction(QIcon.fromTheme("image-x-generic"), "show Database", triggered=self.showDB)
        self.actionOpenPy2 = QAction(QIcon.fromTheme("python"), "run in python", triggered=self.runPy2)
        self.actionOpenPy3 = QAction(QIcon.fromTheme("python3"), "run in python3", triggered=self.runPy3)
        self.actionFilesZip = QAction(QIcon.fromTheme("zip"), "create zip from selected files", triggered=self.createZipFromFiles)
        self.actionUnzipHere = QAction(QIcon.fromTheme("application-zip"), "extract here ...", triggered=self.unzipHere)
        self.actionUnzipTo = QAction(QIcon.fromTheme("application-zip"), "extract to ...", triggered=self.unzipTo)
        self.actionPlayInt = QAction(QIcon.fromTheme("multimedia-player"), "play with Qt5Player", triggered=self.playInternal)
        self.actionPlayVLC = QAction(QIcon.fromTheme("vlc"), "play with vlc", triggered=self.playMedia)
        self.actionToMp3 = QAction(QIcon.fromTheme("audio-x-generic"), "convert to mp3", triggered=self.makeMP3)
        self.actionPlayList = QAction(QIcon.fromTheme("audio-x-generic"), "play Playlist", triggered=self.playPlaylist)
        self.actionOpenTerm = QAction(QIcon.fromTheme("terminal"), "execute in Terminal", triggered=self.startInTerminal)

        # shortcuts
        self.actionFileOpen.setShortcut(QKeySequence(Qt.Key_Return))
        self.actionFolderNewWin.setShortcut(QKeySequence("Ctrl+n"))
        self.actionOpenText.setShortcut(QKeySequence(Qt.Key_F6))
        self.actionFileRename.setShortcut(QKeySequence(Qt.Key_F2))
        self.actionFileCopy.setShortcut(QKeySequence("Ctrl+c"))
        self.actionFileCut.setShortcut(QKeySequence("Ctrl+x"))
        self.actionFilePaste.setShortcut(QKeySequence("Ctrl+v"))
        self.actionFileDel.setShortcut(QKeySequence("Shift+Del"))
        self.actionFile2Trash.setShortcut(QKeySequence("Del"))
        self.actionFindFiles.setShortcut(QKeySequence("Ctrl+f"))
        self.actionPlayInt.setShortcut(QKeySequence(Qt.Key_F3))
        self.actionHide.setShortcut(QKeySequence("Ctrl+h"))
        self.actionGoBack.setShortcut(QKeySequence(Qt.Key_Backspace))
        self.actionHelp.setShortcut(QKeySequence(Qt.Key_F1))
        self.actionFolderTerm.setShortcut(QKeySequence(Qt.Key_F7))
        self.actionOpenTerm.setShortcut(QKeySequence(Qt.Key_F8))
        self.actionFolderNew.setShortcut(QKeySequence("Shift+Ctrl+n"))

        # context visibility
        self.actionFileOpen.setShortcutVisibleInContextMenu(True)
        self.actionFolderNewWin.setShortcutVisibleInContextMenu(True)
        self.actionOpenText.setShortcutVisibleInContextMenu(True)
        self.actionFileRename.setShortcutVisibleInContextMenu(True)
        self.actionFileCopy.setShortcutVisibleInContextMenu(True)
        self.actionFileCut.setShortcutVisibleInContextMenu(True)
        self.actionFilePaste.setShortcutVisibleInContextMenu(True)
        self.actionFileDel.setShortcutVisibleInContextMenu(True)
        self.actionFile2Trash.setShortcutVisibleInContextMenu(True)
        self.actionFindFiles.setShortcutVisibleInContextMenu(True)
        self.actionPlayInt.setShortcutVisibleInContextMenu(True)
        self.actionRefresh.setShortcutVisibleInContextMenu(True)
        self.actionHide.setShortcutVisibleInContextMenu(True)
        self.actionHide.setCheckable(True)
        self.actionGoBack.setShortcutVisibleInContextMenu(True)
        self.actionHelp.setShortcutVisibleInContextMenu(True)
        self.actionFolderTerm.setShortcutVisibleInContextMenu(True)
        self.actionOpenTerm.setShortcutVisibleInContextMenu(True)
        self.actionFolderNew.setShortcutVisibleInContextMenu(True)

        # tree context
        self.treeview.addAction(self.actionFolderNew)
        self.treeview.addAction(self.actionFolderRename)
        self.treeview.addAction(self.actionFolderCopy)
        self.treeview.addAction(self.actionFolderPaste)
        self.treeview.addAction(self.actionFolderDel)
        self.treeview.addAction(self.actionFileRename)
        self.treeview.addAction(self.actionFindFiles)
        self.treeview.addAction(self.actionFolderZip)
        self.treeview.addAction(self.actionFolderTerm)

        # files context
        self.listview.addAction(self.actionFileOpen)
        self.listview.addAction(self.actionFolderNewWin)
        self.listview.addAction(self.actionOpenText)
        self.listview.addAction(self.actionOpenTextRoot)
        self.listview.addAction(self.actionFileRename)
        self.listview.addAction(self.actionFileCopy)
        self.listview.addAction(self.actionFileCut)
        self.listview.addAction(self.actionFilePaste)
        self.listview.addAction(self.actionFileDel)
        self.listview.addAction(self.actionFile2Trash)
        self.listview.addAction(self.actionOpenImg)
        self.listview.addAction(self.actionOpenUrl)
        self.listview.addAction(self.actionOpenDB)
        self.listview.addAction(self.actionOpenPy2)
        self.listview.addAction(self.actionOpenPy3)
        self.listview.addAction(self.actionFilesZip)
        self.listview.addAction(self.actionUnzipHere)
        self.listview.addAction(self.actionUnzipTo)
        self.listview.addAction(self.actionPlayInt)
        self.listview.addAction(self.actionPlayVLC)
        self.listview.addAction(self.actionToMp3)
        self.listview.addAction(self.playlistAction)
        self.listview.addAction(self.actionPlayList)
        self.listview.addAction(self.actionRefresh)
        self.listview.addAction(self.actionHide)
        self.listview.addAction(self.actionFolderTerm)
        self.listview.addAction(self.actionOpenTerm)
        self.listview.addAction(self.actionMkExec)
        #        self.listview.addAction(self.pasteFolderAction)

    def enableHidden(self):
        if self.hiddenEnabled == False:
            self.fileModel.setFilter(QDir.NoDotAndDotDot | QDir.Hidden | QDir.AllDirs | QDir.Files)
            self.dirModel.setFilter(QDir.NoDotAndDotDot | QDir.Hidden | QDir.AllDirs)
            self.hiddenEnabled = True
            self.actionHide.setChecked(True)
            dprint("set hidden files to true")
        else:
            self.fileModel.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs | QDir.Files)
            self.dirModel.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs)
            self.hiddenEnabled = False
            self.actionHide.setChecked(False)
            dprint("set hidden files to false")

    def openNewWin(self):
        self.copyListNew = ""
        index = self.treeview.selectionModel().currentIndex()
        path = self.dirModel.fileInfo(index).absoluteFilePath()
        theApp = sys.argv[0]
        if QDir(path).exists:
            dprint("open '" + path + "' in new window")
            self.process.startDetached("python3", [theApp, path])

    def playPlaylist(self):
        if self.listview.selectionModel().hasSelection():
            index = self.listview.selectionModel().currentIndex()
            path = self.fileModel.fileInfo(index).absoluteFilePath()
            self.player = QAudioPlayer.Player('')
            self.player.setGeometry(100, 100, 500, 350)
            self.player.show()
            self.player.clearList()
            self.player.openOnStart(path)
            dprint("added Files to playlist")

    def showImage(self):
        if self.listview.selectionModel().hasSelection():
            index = self.listview.selectionModel().currentIndex()
            path = self.fileModel.fileInfo(index).absoluteFilePath()
            dprint("show image: " + path)
            self.win = QImageViewer.ImageViewer()
            self.win.show()
            self.win.filename = path
            self.win.loadFile(path)

    def showDB(self):
        if self.listview.selectionModel().hasSelection():
            from plugins import DBViewer
            index = self.listview.selectionModel().currentIndex()
            path = self.fileModel.fileInfo(index).absoluteFilePath()
            dprint("show image: ", path)
            self.db_win = DBViewer.MyWindow()
            self.db_win.show()
            self.db_win.fileOpenStartup(path)

    def checkIsApplication(self, path):
        st = subprocess.check_output("file  --mime-type '" + path + "'", stderr=subprocess.STDOUT,
                                     universal_newlines=True, shell=True)
        dprint(st)
        if "application/x-executable" in st:
            dprint(path + " is an application")
            return True
        else:
            return False

    def makeExecutable(self):
        if self.listview.selectionModel().hasSelection():
            index = self.listview.selectionModel().currentIndex()
            path = self.fileModel.fileInfo(index).absoluteFilePath()
            dprint("set " + path + " executable")
            st = os.stat(path)
            os.chmod(path, st.st_mode | stat.S_IEXEC)

    def showInTerminal(self):
        if self.treeview.hasFocus():
            index = self.treeview.selectionModel().currentIndex()
            path = self.dirModel.fileInfo(index).absoluteFilePath()
        elif self.listview.hasFocus():
            index = self.listview.selectionModel().currentIndex()
            path = self.fileModel.fileInfo(index).absoluteFilePath()
        self.terminal = QTerminalFolder.MainWindow()
        self.terminal.show()
        if self.terminal.isVisible():
            os.chdir(path)
            self.terminal.shellWin.startDir = path
            self.terminal.shellWin.name = (str(getpass.getuser()) + "@" + str(socket.gethostname())
                                           + ":" + str(path) + "$ ")
            self.terminal.shellWin.appendPlainText(self.terminal.shellWin.name)

    def startInTerminal(self):
        if self.listview.selectionModel().hasSelection():
            index = self.listview.selectionModel().currentIndex()
            filename = self.fileModel.fileInfo(index).fileName()
            path = self.fileModel.fileInfo(index).absoluteFilePath()
            folderpath = self.fileModel.fileInfo(index).path()
            if not self.fileModel.fileInfo(index).isDir():
                self.terminal = QTerminalFolder.MainWindow()
                self.terminal.show()
                if self.terminal.isVisible():
                    os.chdir(folderpath)
                    self.terminal.shellWin.startDir = folderpath
                    self.terminal.shellWin.name = (str(getpass.getuser()) + "@" + str(socket.gethostname())
                                                   + ":" + str(folderpath) + "$ ")
                    self.terminal.shellWin.appendPlainText(self.terminal.shellWin.name)
                    self.terminal.shellWin.insertPlainText("./%s" % (filename))
            else:
                self.terminal = QTerminalFolder.MainWindow()
                self.terminal.show()
                if self.terminal.isVisible():
                    os.chdir(path)
                    self.terminal.shellWin.startDir = path
                    self.terminal.shellWin.name = (str(getpass.getuser()) + "@" + str(socket.gethostname())
                                                   + ":" + str(path) + "$ ")
                    self.terminal.shellWin.appendPlainText(self.terminal.shellWin.name)

    def createZipFromFolder(self):
        index = self.treeview.selectionModel().currentIndex()
        path = self.dirModel.fileInfo(index).filePath()
        fname = self.dirModel.fileInfo(index).fileName()
        dprint("folder to zip:" + path)
        self.copyFile()
        target, _ = QFileDialog.getSaveFileName(self, "Save as... (do not add .zip)", path + "/" + fname,
                                                "zip files (*.zip)")
        if (target != ""):
            shutil.make_archive(target, 'zip', path)

    def createZipFromFiles(self):
        if self.listview.selectionModel().hasSelection():
            index = self.treeview.selectionModel().currentIndex()
            path = self.dirModel.fileInfo(index).filePath()
            fname = self.dirModel.fileInfo(index).fileName()
            dprint("folder to zip:" + path)
            self.copyFile()
            target, _ = QFileDialog.getSaveFileName(self, "Save as...", path + "/" + "archive.zip", "zip files (*.zip)")
            if (target != ""):
                zipText = ""
                with ZipFile(target, 'w') as myzip:
                    for file in self.copyList:
                        fname = os.path.basename(file)
                        myzip.write(file, fname)

    def unzipHere(self):
        if self.listview.selectionModel().hasSelection():
            file_index = self.listview.selectionModel().currentIndex()
            file_path = self.fileModel.fileInfo(file_index).filePath()
            folder_index = self.treeview.selectionModel().currentIndex()
            folder_path = self.dirModel.fileInfo(folder_index).filePath()
            with ZipFile(file_path, 'r') as zipObj:
                # Extract zip file in current directory
                zipObj.extractall(folder_path)

    def unzipTo(self):
        file_index = self.listview.selectionModel().currentIndex()
        file_path = self.fileModel.fileInfo(file_index).filePath()
        dirpath = QFileDialog.getExistingDirectory(self, "selectFolder", QDir.homePath(), QFileDialog.ShowDirsOnly)
        if dirpath:
            with ZipFile(file_path, 'r') as zipObj:
                zipObj.extractall(dirpath)

    def findFiles(self):
        dprint("find")
        index = self.treeview.selectionModel().currentIndex()
        path = self.dirModel.fileInfo(index).absoluteFilePath()
        dprint("open findWindow")
        self.w = findFilesWindow.ListBox()
        self.w.show()
        self.w.folderEdit.setText(path)
        self.w.findEdit.setText(self.findfield.text())

    def refreshList(self):
        dprint("refreshing view")
        index = self.listview.selectionModel().currentIndex()
        path = self.fileModel.fileInfo(index).path()
        self.treeview.setCurrentIndex(self.fileModel.index(path))
        self.treeview.setFocus()

    def makeMP3(self):
        if self.listview.selectionModel().hasSelection():
            index = self.listview.selectionModel().currentIndex()
            path = self.fileModel.fileInfo(index).filePath()
            ext = self.fileModel.fileInfo(index).suffix()
            newpath = path.replace("." + ext, ".mp3")
            dprint(ext)
            self.statusBar().showMessage("%s '%s'" % ("converting:", path))
            self.process.startDetached("ffmpeg", ["-i", path, newpath])
            dprint("%s '%s'" % ("converting", path))

    def makePlaylist(self):
        if self.listview.selectionModel().hasSelection():
            index = self.treeview.selectionModel().currentIndex()
            foldername = self.dirModel.fileInfo(index).fileName()

            path = self.currentPath + "/" + foldername + ".m3u"
            pl = QFile(path)
            pl.open(QIODevice.ReadWrite | QIODevice.Truncate)
            mp3List = []

            for name in os.listdir(self.currentPath):
                if os.path.isfile(os.path.join(self.currentPath, name)):
                    if ".mp3" in name:
                        mp3List.append(self.currentPath + "/" + name)

            mp3List.sort(key=str.lower)

            with open(path, 'w') as playlist:
                playlist.write('\n'.join(mp3List))
                playlist.close()

    def showHelp(self):
        top = self.y() + 26
        left = self.width() / 2 - 100
        dprint(top)
        self.w = helpWindow()
        self.w.setWindowFlags(Qt.FramelessWindowHint)
        self.w.setWindowModality(Qt.ApplicationModal)
        self.w.setGeometry(left, top, 300, 360)
        self.w.show()

    def on_clicked(self, index):
        if self.treeview.selectionModel().hasSelection():
            index = self.treeview.selectionModel().currentIndex()
            if not (self.treeview.isExpanded(index)):
                self.treeview.setExpanded(index, True)
            else:
                self.treeview.setExpanded(index, False)

    def getFolderSize(self, path):
        size = sum(os.path.getsize(f) for f in os.listdir(path) if os.path.isfile(f))
        return size

    def on_selectionChanged(self):
        self.treeview.selectionModel().clearSelection()
        index = self.treeview.selectionModel().currentIndex()
        path = self.dirModel.fileInfo(index).absoluteFilePath()
        self.listview.setRootIndex(self.fileModel.setRootPath(path))
        self.currentPath = path
        self.setWindowTitle(path)
        self.getRowCount()

    def openFile(self):
        if self.listview.hasFocus():
            index = self.listview.selectionModel().currentIndex()
            path = self.fileModel.fileInfo(index).absoluteFilePath()
            self.copyFile()
            for files in self.copyList:
                dprint("%s '%s'" % ("open file", files))
                if self.checkIsApplication(path) == True:
                    self.process.startDetached(files)
                else:
                    QDesktopServices.openUrl(QUrl(files, QUrl.TolerantMode | QUrl.EncodeUnicode))

    def openFileText(self):
        if self.listview.selectionModel().hasSelection():
            index = self.listview.selectionModel().currentIndex()
            path = self.fileModel.fileInfo(index).absoluteFilePath()
            self.texteditor = QTextEdit.MainWindow()
            self.texteditor.show()
            self.texteditor.loadFile(path)

    def openFileTextRoot(self):
        if self.listview.selectionModel().hasSelection():
            index = self.listview.selectionModel().currentIndex()
            path = self.fileModel.fileInfo(index).absoluteFilePath()
            file = sys.argv[0]
            mygksu = os.path.join(os.path.dirname(file), "mygksu")
            self.process.startDetached(mygksu, ["xed", path])

    def playInternal(self):
        if self.listview.selectionModel().hasSelection():
            index = self.listview.selectionModel().currentIndex()
            path = self.fileModel.fileInfo(index).filePath()
            self.statusBar().showMessage("%s '%s'" % ("file:", path))
            self.player = Qt5Player.VideoPlayer('')
            self.player.show()
            self.player.loadFilm(path)
            dprint("%s '%s'" % ("playing", path))

    def playMedia(self):
        if self.listview.selectionModel().hasSelection():
            index = self.listview.selectionModel().currentIndex()
            path = self.fileModel.fileInfo(index).filePath()
            self.statusBar().showMessage("%s '%s'" % ("file:", path))
            self.process.startDetached("cvlc", [path])
            dprint("%s '%s'" % ("playing with vlc:", path))

    def showURL(self):
        if not Enabled.webview:
            QMessageBox.warning(self, "Module disabled", "QWebViewer disabled")
            return
        if self.listview.selectionModel().hasSelection():
            index = self.listview.selectionModel().currentIndex()
            path = self.fileModel.fileInfo(index).absoluteFilePath()
            self.webview = QWebViewer.MainWindow()
            self.webview.show()
            self.webview.load_url(path)

    def list_doubleClicked(self):
        index = self.listview.selectionModel().currentIndex()
        path = self.fileModel.fileInfo(index).absoluteFilePath()
        #        folderpath = self.fileModel.fileInfo(index).path()
        if not self.fileModel.fileInfo(index).isDir():
            if self.checkIsApplication(path) == True:
                self.process.startDetached(path)
            else:
                QDesktopServices.openUrl(QUrl(path, QUrl.TolerantMode | QUrl.EncodeUnicode))
        else:
            self.treeview.setCurrentIndex(self.dirModel.index(path))
            self.treeview.setFocus()
            #            self.listview.setRootIndex(self.fileModel.setRootPath(path))
            self.setWindowTitle(path)

    def goBack(self):
        index = self.listview.selectionModel().currentIndex()
        path = self.fileModel.fileInfo(index).path()
        self.treeview.setCurrentIndex(self.dirModel.index(path))

    def goUp(self):
        index = self.treeview.selectionModel().currentIndex()
        path = self.dirModel.fileInfo(index).path()
        dprint(path)
        self.treeview.setCurrentIndex(self.dirModel.index(path))

    def goHome(self):
        docs = QStandardPaths.standardLocations(QStandardPaths.HomeLocation)[0]
        self.treeview.setCurrentIndex(self.dirModel.index(docs))
        self.treeview.setFocus()

    def goMusic(self):
        docs = QStandardPaths.standardLocations(QStandardPaths.MusicLocation)[0]
        self.treeview.setCurrentIndex(self.dirModel.index(docs))
        self.treeview.setFocus()

    def goVideo(self):
        docs = QStandardPaths.standardLocations(QStandardPaths.MoviesLocation)[0]
        self.treeview.setCurrentIndex(self.dirModel.index(docs))
        self.treeview.setFocus()

    def goDocuments(self):
        docs = QStandardPaths.standardLocations(QStandardPaths.DocumentsLocation)[0]
        self.treeview.setCurrentIndex(self.dirModel.index(docs))
        self.treeview.setFocus()

    def goDownloads(self):
        docs = QStandardPaths.standardLocations(QStandardPaths.DownloadLocation)[0]
        self.treeview.setCurrentIndex(self.dirModel.index(docs))
        self.treeview.setFocus()

    def infobox(self, message):
        title = "QFilemager"
        QMessageBox(QMessageBox.Information, title, message, QMessageBox.NoButton, self,
                    Qt.Dialog | Qt.NoDropShadowWindowHint).show()

    def contextMenuEvent(self, event):
        index = self.listview.selectionModel().currentIndex()
        path = self.fileModel.fileInfo(index).absoluteFilePath()
        self.menu = QMenu(self.listview)
        if self.listview.hasFocus():
            self.menu.addAction(self.actionFolderNew)
            self.menu.addAction(self.actionFileOpen)
            self.menu.addAction(self.actionOpenText)
            self.menu.addAction(self.actionOpenTextRoot)
            self.menu.addSeparator()
            if os.path.isdir(path):
                self.menu.addAction(self.actionFolderNewWin)
            self.menu.addSeparator()
            self.menu.addAction(self.actionFileRename)
            self.menu.addSeparator()
            self.menu.addAction(self.actionFileCopy)
            self.menu.addAction(self.actionFileCut)
            self.menu.addAction(self.actionFilePaste)
            #            self.menu.addAction(self.pasteFolderAction)
            self.menu.addAction(self.actionFolderTerm)
            self.menu.addAction(self.actionOpenTerm)
            self.menu.addAction(self.actionMkExec)
            ### database viewer
            db_extension = [".sql", "db", "sqlite", "sqlite3", ".SQL", "DB", "SQLITE", "SQLITE3"]
            for ext in db_extension:
                if ext in path:
                    self.menu.addAction(self.actionOpenDB)
            ### html viewer
            url_extension = [".htm", ".html"]
            for ext in url_extension:
                if ext in path:
                    self.menu.addAction(self.actionOpenUrl)
            ### run in python
            if path.endswith(".py"):
                self.menu.addAction(self.actionOpenPy2)
                self.menu.addAction(self.actionOpenPy3)
            ### image viewer
            image_extension = [".png", "jpg", ".jpeg", ".bmp", "tif", ".tiff", ".pnm", ".svg",
                               ".exif", ".gif"]
            for ext in image_extension:
                if ext in path or ext.upper() in path:
                    self.menu.addAction(self.actionOpenImg)
            self.menu.addSeparator()
            self.menu.addAction(self.actionFile2Trash)
            self.menu.addAction(self.actionFileDel)
            self.menu.addSeparator()
            if ".m3u" in path:
                self.menu.addAction(self.actionPlayList)
            extensions = [".mp3", ".mp4", "mpg", ".m4a", ".mpeg", "avi", ".mkv", ".webm",
                          ".wav", ".ogg", ".flv ", ".vob", ".ogv", ".ts", ".m2v", "m4v", "3gp", ".f4v"]
            for ext in extensions:
                if ext in path or ext.upper() in path:
                    self.menu.addSeparator()
                    self.menu.addAction(self.actionPlayInt)
                    self.menu.addAction(self.actionPlayVLC)
                    self.menu.addSeparator()
            extensions = [".mp4", "mpg", ".m4a", ".mpeg", "avi", ".mkv", ".webm",
                          ".wav", ".ogg", ".flv ", ".vob", ".ogv", ".ts", ".m2v", "m4v", "3gp", ".f4v"]
            for ext in extensions:
                if ext in path or ext.upper() in path:
                    self.menu.addAction(self.actionToMp3)
                    self.menu.addSeparator()
            if ".mp3" in path:
                self.menu.addAction(self.playlistAction)
            self.menu.addAction(self.actionRefresh)
            self.menu.addAction(self.actionHide)
            self.menu.addAction(self.actionFilesZip)
            zip_extension = [".zip", ".tar.gz"]
            for ext in zip_extension:
                if ext in path:
                    self.menu.addAction(self.actionUnzipHere)
                    self.menu.addAction(self.actionUnzipTo)
            self.menu.addSeparator()
            self.menu.addAction(self.actionHelp)
            self.menu.popup(QCursor.pos())
        else:
            index = self.treeview.selectionModel().currentIndex()
            path = self.dirModel.fileInfo(index).absoluteFilePath()
            dprint("current path is: %s" % path)
            self.menu = QMenu(self.treeview)
            if os.path.isdir(path):
                self.menu.addAction(self.actionFolderNewWin)
                self.menu.addAction(self.actionFolderNew)
                self.menu.addAction(self.actionFolderRename)
                self.menu.addAction(self.actionFolderCopy)
                self.menu.addAction(self.actionFolderPaste)
                self.menu.addAction(self.actionFolderDel)
                self.menu.addAction(self.actionFolderTerm)
                self.menu.addAction(self.actionFindFiles)
                self.menu.addAction(self.actionFolderZip)
            self.menu.popup(QCursor.pos())

    def createNewFolder(self):
        index = self.treeview.selectionModel().currentIndex()
        path = self.dirModel.fileInfo(index).absoluteFilePath()
        dlg = QInputDialog(self)
        foldername, ok = dlg.getText(self, 'Folder Name', "Folder Name:", QLineEdit.Normal, "", Qt.Dialog)
        if ok:
            success = QDir(path).mkdir(foldername)

    def runPy2(self):
        if self.listview.selectionModel().hasSelection():
            index = self.listview.selectionModel().currentIndex()
            path = self.fileModel.fileInfo(index).absoluteFilePath()
            self.process.startDetached("python", [path])

    def runPy3(self):
        if self.listview.selectionModel().hasSelection():
            index = self.listview.selectionModel().currentIndex()
            path = self.fileModel.fileInfo(index).absoluteFilePath()
            error = QProcess.error(self.process)
            self.process.startDetached("python3", [path])
            if self.process.errorOccurred():
                self.infobox(error)

    def renameFile(self):
        if self.listview.hasFocus():
            if self.listview.selectionModel().hasSelection():
                index = self.listview.selectionModel().currentIndex()
                path = self.fileModel.fileInfo(index).absoluteFilePath()
                basepath = self.fileModel.fileInfo(index).path()
                dprint(basepath)
                oldName = self.fileModel.fileInfo(index).fileName()
                dlg = QInputDialog()
                newName, ok = dlg.getText(self, 'new Name:', path, QLineEdit.Normal, oldName, Qt.Dialog)
                if ok:
                    newpath = basepath + "/" + newName
                    QFile.rename(path, newpath)
        elif self.treeview.hasFocus():
            self.renameFolder()

    def renameFolder(self):
        index = self.treeview.selectionModel().currentIndex()
        path = self.dirModel.fileInfo(index).absoluteFilePath()
        basepath = self.dirModel.fileInfo(index).path()
        dprint("pasepath: %s" % basepath)
        oldName = self.dirModel.fileInfo(index).fileName()
        dlg = QInputDialog()
        newName, ok = dlg.getText(self, 'new Name:', path, QLineEdit.Normal, oldName, Qt.Dialog)
        if ok:
            newpath = basepath + "/" + newName
            dprint(newpath)
            nd = QDir(path)
            check = nd.rename(path, newpath)

    def copyFile(self):
        self.copyList = []
        selected = self.listview.selectionModel().selectedRows()
        count = len(selected)
        for index in selected:
            path = self.currentPath + "/" + self.fileModel.data(index, self.fileModel.FileNameRole)
            dprint(path + " copied to clipboard")
            self.copyList.append(path)
            self.clip.setText('\n'.join(self.copyList))
        dprint("%s\n%s" % ("filepath(s) copied:", '\n'.join(self.copyList)))

    def copyFolder(self):
        index = self.treeview.selectionModel().currentIndex()
        folderpath = self.dirModel.fileInfo(index).absoluteFilePath()
        dprint("%s\n%s" % ("folderpath copied:", folderpath))
        self.folder_copied = folderpath
        self.copyList = []

    def pasteFolder(self):
        index = self.treeview.selectionModel().currentIndex()
        target = self.folder_copied
        destination = self.dirModel.fileInfo(index).absoluteFilePath() + "/" + QFileInfo(self.folder_copied).fileName()
        dprint("%s %s %s" % (target, "will be pasted to", destination))
        try:
            shutil.copytree(target, destination)
        except OSError as e:
            # If the error was caused because the source wasn't a directory
            if e.errno == errno.ENOTDIR:
                shutil.copy(target, destination)
            else:
                self.infobox('Error', 'Directory not copied. Error: %s' % e)

    def pasteFile(self):
        if len(self.copyList) > 0:
            index = self.treeview.selectionModel().currentIndex()
            file_index = self.listview.selectionModel().currentIndex()
            for target in self.copyList:
                dprint(target)
                destination = self.dirModel.fileInfo(index).absoluteFilePath() + "/" + QFileInfo(target).fileName()
                dprint("%s %s" % ("pasted File to", destination))
                QFile.copy(target, destination)
                if self.cut == True:
                    QFile.remove(target)
                self.cut == False
        else:
            index = self.treeview.selectionModel().currentIndex()
            target = self.folder_copied
            destination = self.dirModel.fileInfo(index).absoluteFilePath() + "/" + QFileInfo(
                self.folder_copied).fileName()
            try:
                shutil.copytree(target, destination)
            except OSError as e:
                # If the error was caused because the source wasn't a directory
                if e.errno == errno.ENOTDIR:
                    shutil.copy(target, destination)
                else:
                    dprint('Directory not copied. Error: %s' % e)

    def cutFile(self):
        self.cut = True
        self.copyFile()

    def deleteFolder(self):
        index = self.treeview.selectionModel().currentIndex()
        delFolder = self.dirModel.fileInfo(index).absoluteFilePath()
        msg = QMessageBox.question(self, "Info", "Caution!\nReally delete this Folder?\n" + delFolder,
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if msg == QMessageBox.Yes:
            dprint('Deletion confirmed.')
            self.statusBar().showMessage("%s %s" % ("folder deleted", delFolder), 0)
            self.fileModel.remove(index)
            dprint("%s %s" % ("folder deleted", delFolder))
        else:
            dprint('No clicked.')

    def deleteFile(self):
        self.copyFile()
        msg = QMessageBox.question(self, "Info", "Caution!\nReally delete this Files?\n" + '\n'.join(self.copyList),
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if msg == QMessageBox.Yes:
            dprint('Deletion confirmed.')
            index = self.listview.selectionModel().currentIndex()
            self.copyPath = self.fileModel.fileInfo(index).absoluteFilePath()
            dprint("%s %s" % ("file deleted", self.copyPath))
            self.statusBar().showMessage("%s %s" % ("file deleted", self.copyPath), 0)
            for delFile in self.listview.selectionModel().selectedIndexes():
                self.fileModel.remove(delFile)
        else:
            dprint('No clicked.')

    def deleteFileTrash(self):
        if not Enabled.trash:
            QMessageBox.warning(self, "Module disabled", "Send2Trash not installed")
            return
        index = self.listview.selectionModel().currentIndex()
        self.copyFile()
        msg = QMessageBox.question(self, "Info",
                                   "Caution!\nReally move this Files to Trash\n" + '\n'.join(self.copyList),
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if msg == QMessageBox.Yes:
            dprint('Deletion confirmed.')
            for delFile in self.copyList:
                try:
                    send2trash(delFile)
                except OSError as e:
                    self.infobox(str(e))
                dprint("%s %s" % ("file moved to trash:", delFile))
                self.statusBar().showMessage("%s %s" % ("file moved to trash:", delFile), 0)
        else:
            dprint('No clicked.')

    def createStatusBar(self):
        sysinfo = QSysInfo()
        myMachine = "current CPU Architecture: " + sysinfo.currentCpuArchitecture() + " *** " + sysinfo.prettyProductName() + " *** " + sysinfo.kernelType() + " " + sysinfo.kernelVersion()
        self.statusBar().showMessage(myMachine, 0)


def get_stylesheet(self, name: str = 'stylesheet'):
    file_path = os.path.join(os.path.dirname(__file__), 'resources', f'{name}.css')
    with open(file_path, 'r') as css_file:
        stylesheet = css_file.read()
    return stylesheet


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = myWindow()
    w.show()
    if len(sys.argv) > 1:
        path = sys.argv[1]
        dprint(path)
        w.listview.setRootIndex(w.fileModel.setRootPath(path))
        w.treeview.setRootIndex(w.dirModel.setRootPath(path))
        w.setWindowTitle(path)
    sys.exit(app.exec_())
