# v0.0.1
import Metashape
from PySide2 import QtGui, QtCore, QtWidgets, QtPrintSupport


from PySide2.QtCore import QDir, Qt
from PySide2.QtGui import QImage, QPainter, QPalette, QPixmap
from PySide2.QtWidgets import (QAction, QApplication, QFileDialog, QLabel,
                               QMainWindow, QMenu, QMessageBox, QScrollArea, QSizePolicy)
from PySide2.QtPrintSupport import QPrintDialog, QPrinter


import datetime
import os
import concurrent.futures
import shutil 

# Checking compatibility
compatible_major_version = "1.6"
found_major_version = ".".join(Metashape.app.version.split('.')[:2])
if found_major_version != compatible_major_version:
    raise Exception("Incompatible Metashape version: {} != {}".format(
        found_major_version, compatible_major_version))


class CopyChunkPhotosDlg(QtWidgets.QDialog):
    

    def __init__(self, parent):

        QtWidgets.QDialog.__init__(self, parent)
        self.setWindowTitle(
            "COPY CHUNK PHOTOS, CMG (MAROC)")

        # self.adjustSize()
        self.setMaximumHeight(880)
        self.createParamsGridLayout()
        self.createButtonsGridLayout()
        self.createProgressBar()
        self.getChunk()
        self.getPaths()
        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.groupBoxParams)
        vbox.addWidget(self.groupBoxProgressBar)
        vbox.addWidget(self.groupBoxButtons)
        self.setLayout(vbox)
        self.exec()

    def createButtonsGridLayout(self):

        self.groupBoxButtons = QtWidgets.QGroupBox()

        gridBtnLayout = QtWidgets.QGridLayout()

        self.btnQuit = QtWidgets.QPushButton("Cancel")
        self.btnQuit.setFixedSize(150, 23)

        self.btnSubmit = QtWidgets.QPushButton("OK")
        self.btnSubmit.setFixedSize(150, 23)

        gridBtnLayout.addWidget(self.btnSubmit, 0, 0)
        gridBtnLayout.addWidget(self.btnQuit, 0, 1)
        self.btnSubmit.setEnabled(False)
        QtCore.QObject.connect(self.btnQuit, QtCore.SIGNAL(
            "clicked()"), self, QtCore.SLOT("reject()"))

        QtCore.QObject.connect(
            self.btnSubmit, QtCore.SIGNAL("clicked()"), self.copyChunkPhotos)

        self.groupBoxButtons.setLayout(gridBtnLayout)

    def createParamsGridLayout(self):
        self.groupBoxParams = QtWidgets.QGroupBox('Copy')

        gridParamsLayout = QtWidgets.QGridLayout()
        gridParamsLayout.setHorizontalSpacing(50)
        self.label_chunk = QtWidgets.QLabel('Chunk : ')

        self.chunksBox = QtWidgets.QComboBox()
        self.chunksBox.resize(200, 23)

        self.getChunks()
        for chunk in self.chunks:
            self.chunksBox.addItem(chunk.label, chunk.key)

        self.label_folder = QtWidgets.QLabel('Select folder (to copy) : ')
        self.btn_select_folder = QtWidgets.QPushButton("Select...")
        self.btn_select_folder.setFixedSize(150, 23)
        self.path_label = QtWidgets.QLabel('Selected Path : ...')

        self.space = QtWidgets.QLabel('         ')

        self.chunk_create_label = QtWidgets.QLabel("Create new Chunk")

        self.chkCreateChunk = QtWidgets.QCheckBox()
        self.chkCreateChunk.setChecked(True)
        # adding widget
        gridParamsLayout.addWidget(self.label_chunk, 0, 0)
        gridParamsLayout.addWidget(self.chunksBox, 0, 1)
        gridParamsLayout.addWidget(self.label_folder, 0, 2)
        gridParamsLayout.addWidget(self.btn_select_folder, 0, 3)
        gridParamsLayout.addWidget(self.path_label, 1, 0)
        gridParamsLayout.addWidget(self.chunk_create_label, 2, 0)
        gridParamsLayout.addWidget(self.chkCreateChunk, 2, 1)
        QtCore.QObject.connect(
            self.btn_select_folder, QtCore.SIGNAL("clicked()"), self.selectFolder)

        self.chunksBox.currentIndexChanged.connect(self.getChunk)
      
        self.groupBoxParams.setLayout(gridParamsLayout)

    def createProgressBar(self):
        self.groupBoxProgressBar = QtWidgets.QGroupBox()
        gridProgressBar = QtWidgets.QGridLayout()

        self.progressBar = QtWidgets.QProgressBar()
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(100)

        gridProgressBar.addWidget(self.progressBar, 0, 0)
        self.groupBoxProgressBar.setLayout(gridProgressBar)


    def getChunks(self):
        self.chunks = Metashape.app.document.chunks

        if len(self.chunks) == 0:
            Metashape.app.messageBox('No chunk in project')

    def getChunk(self):
        chunk_key = self.chunksBox.currentData()
        self.chunk = doc.findChunk(chunk_key)
        self.getPaths()
        

    def selectFolder(self):

        directoryPath = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Select Directory")
        dossier = directoryPath.split('/')[-1]
        path = 'Selected Path : {}'.format(directoryPath)
        self.path_label.setText(path)
        self.btnSubmit.setEnabled(True)
        self.path_folder = directoryPath

    def getPaths(self):
        self.paths = []
        for c in self.chunk.cameras:
            path = c.photo.path
            self.paths.append(path)

        if len(self.paths) == 0:
            Metashape.app.messageBox('No photos in this chunk')


    def add_new_chunk(self, images):
        doc = Metashape.app.document
        new_chunk = doc.addChunk()
        new_chunk.label = 'Copy of ' + self.chunk.label
        new_chunk.addPhotos(images)

    def copyPhots(self, c):
        self.i = self.i + 1
        self.progressBar.setValue(self.i)
        source = c.photo.path
        destination = self.path_folder

        path_without_drive = os.path.splitdrive(source)[1]
        subfolder = os.path.splitext(path_without_drive)[0]
        path_to_photo = os.path.split(path_without_drive)[0]

        folders = path_to_photo.split('/')
        path_dist = destination + path_to_photo

        path_dist = path_dist.replace(self.commun_without_drive, '')

        try:
            if not os.path.exists(path_dist):
                os.makedirs(path_dist)

         
            distination = path_dist + '/' + c.label + '.jpg'
            print(source)
            print(distination)
            shutil.copy2(source, distination)
            self.imageList.append(distination)
           
        except RuntimeError:
            Metashape.app.messageBox('error')

    def copyChunkPhotos(self):
        print("Import Adjust Photos Script started...")

        self.imageList = []
        commun = os.path.commonpath(self.paths)
        commun_without_drive = os.path.splitdrive(commun)[1]
        self.commun_without_drive = commun_without_drive.replace('\\', '/')
        total = len(self.chunk.cameras)
        self.progressBar.setMaximum(total)
        self.i = 0

        for c in self.chunk.cameras:
            self.copyPhots(c)
            QtWidgets.QApplication.processEvents()

        if self.chkCreateChunk.isChecked():

            self.add_new_chunk(self.imageList)
        self.close()
        print("Script finished!")
        Metashape.app.messageBox(' Copy  successful !')
        return True


def copyChunkPhotos():
    global doc

    doc = Metashape.app.document

    app = QtWidgets.QApplication.instance()
    parent = app.activeWindow()

    dlg = CopyChunkPhotosDlg(parent)


label = "Custom menu/Copy Chunk Photos"
Metashape.app.addMenuItem(label, copyChunkPhotos)
print("To execute this script press {}".format(label))
