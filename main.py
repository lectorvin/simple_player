import sys
import os
from PyQt4 import QtGui, QtCore
from PyQt4.phonon import Phonon
import style


icons = {'main': 'icons/main.png',
         'play': 'icons/play.png',
         'stop': 'icons/stop.png',
         'pause': 'icons/pause.png',
         'play_in_circle': 'icons/play_in_circle.png',
         'stop_in_circle': 'icons/stop_in_circle.png',
         'pause_in_circle': 'icons/pause_in_circle.png',
         'volume-': 'icons/volume-.png',
         'volume0': 'icons/volume0.png',
         'volume1': 'icons/volume1.png',
         'volume2': 'icons/volume2.png',
         'volume3': 'icons/volume3.png'}


class Player(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(Player, self).__init__(parent)
        # QtGui.QWidget.__init__(self, parent)
        self.resize(350, 140)
        screen = QtGui.QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width()-2*size.width())/2,
                  (screen.height()-3*size.height())/2)
        self.setWindowTitle("Simple player")
        self.setWindowIcon(QtGui.QIcon(icons['main']))
        self.prev_time = 0
        button_size = QtCore.QSize(20, 20)

        self.play_button = QtGui.QPushButton(QtGui.QIcon(icons['play']), '')
        self.play_button.clicked.connect(self._play)
        self.play_button.setIconSize(button_size)
        self.play_button.setShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Space))
        stop_button = QtGui.QPushButton(QtGui.QIcon(icons['stop']), '')
        stop_button.clicked.connect(self._stop)
        stop_button.setIconSize(button_size)
        stop_button.setShortcut(QtGui.QKeySequence(QtCore.Qt.Key_S))

        self.state = QtGui.QLabel()
        self.state.setPixmap(self.smallPixmap(icons['stop_in_circle']))
        self.title = QtGui.QLabel()
        self.time = QtGui.QLabel()
        choose = QtGui.QPushButton("Choose file")
        choose.clicked.connect(self.choose_file)
        choose.setShortcut(QtGui.QKeySequence(QtCore.Qt.Key_C))
        self.progress = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.progress.setMinimum(0)
        self.progress.setMaximum(1000)
        self.connect(self.progress, QtCore.SIGNAL("valueChanged(int)"),
                     self.goto)
        self.pl = QtGui.QPushButton('Playlist')
        self.pl.clicked.connect(self.playlist)
        self.pl.setShortcut(QtGui.QKeySequence(QtCore.Qt.Key_P))

        self.volume = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.volume.setMinimum(0)
        self.volume.setMaximum(100)
        self.volume.setValue(100)
        self.connect(self.volume, QtCore.SIGNAL("valueChanged(int)"),
                     self.changeVolume)
        self.volume_label = QtGui.QLabel()
        self.volume_label.setPixmap(self.smallPixmap(icons['volume3']))

        w = QtGui.QWidget()
        hbox1 = QtGui.QHBoxLayout()
        hbox2 = QtGui.QHBoxLayout()
        hbox5 = QtGui.QHBoxLayout()
        hbox1.addWidget(self.pl)
        hbox1.addWidget(self.volume)
        hbox1.addWidget(self.volume_label)
        hbox2.addWidget(self.state)
        hbox2.addWidget(self.title)
        hbox2.addStretch(1)
        hbox2.addWidget(self.time)
        hbox5.addWidget(choose)
        hbox5.addWidget(self.play_button)
        hbox5.addWidget(stop_button)

        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        vbox.addWidget(self.progress)
        vbox.addLayout(hbox5)
        w.setLayout(vbox)
        self.setCentralWidget(w)

        self.media = Phonon.MediaObject(self)
        output = Phonon.AudioOutput(Phonon.MusicCategory, self)
        Phonon.createPath(self.media, output)
        self.media.stateChanged.connect(self.handleStateChanged)
        self.media.tick.connect(self.tick)
        self.media.totalTimeChanged.connect(self.set_total_time)
        self.path = ""
        self.total_time = None
        self.connect(self.media, QtCore.SIGNAL("metaDataChanged()"),
                     self.set_name)

        self.progress.setStyleSheet(style.progress_without_handle)
        self.volume.setStyleSheet(style.volume)
        self.play_button.setStyleSheet(style.button)
        stop_button.setStyleSheet(style.button)
        choose.setStyleSheet(style.choose)
        self.setStyleSheet(style.main)
        self.pl.setStyleSheet(style.playlist_button)

        self.setFixedSize(self.size())

    def _play(self):
        if self.media.state() == Phonon.PlayingState:
            if self.volume.value() == 0:
                self.volume_label.setPixmap(self.smallPixmap(icons['volume0']))
            self.media.pause()
            self.play_button.setIcon(QtGui.QIcon(icons['play']))
        else:
            if self.volume.value() == 0:
                self.volume_label.setPixmap(self.smallPixmap(icons['volume-']))
            self.media.play()
            self.play_button.setIcon(QtGui.QIcon(icons['pause']))

    def _stop(self):
        if self.volume.value() == 0:
            self.volume_label.setPixmap(self.smallPixmap(icons['volume0']))
        self.media.stop()

    def choose_file(self):
        self.path = QtGui.QFileDialog.\
                        getOpenFileName(self, 'Open music file', './music',
                                        'Music files (*.mp3 *.wav)')
        if self.path:
            self.media.setCurrentSource(Phonon.MediaSource(self.path))
            self.progress.setStyleSheet(style.progress)

    def message(self, name, message):
        reply = QtGui.QMessageBox.question(self, name, message,
                                           QtGui.QMessageBox.Yes)
        return reply

    def tick(self, time):
        if self.total_time is None:
            return
        remain_time = self.total_time - time
        self.time.setText("%02d:%02d" % self.ms2hms(remain_time))
        self.progress.setValue(int(round(time*1000/self.total_time)))
        self.prev_time = time

    def set_total_time(self, time):
        self.total_time = time

    def handleStateChanged(self, new, old):
        if new == Phonon.PlayingState:
            self.state.setPixmap(self.smallPixmap(icons['play_in_circle']))
        elif new == Phonon.StoppedState:
            self.state.setPixmap(self.smallPixmap(icons['stop_in_circle']))
        elif new == Phonon.PausedState:
            self.state.setPixmap(self.smallPixmap(icons['pause_in_circle']))
        elif new == Phonon.ErrorState:
            self.message("Error", 'Unexpected error!')
        else:
            self.message("Smth strange happened", "Error "+str(new))

    def ms2hms(self, time):
        s = int(round(time/1000))
        m, s = divmod(s, 60)
        return m, s

    def goto(self):
        if self.total_time is None:
            return
        time = int(round(self.progress.value()*self.total_time/1000))
        if abs(self.prev_time - time) > 400:
            self.media.seek(time)
            self.tick(time)

    def changeVolume(self):
        volume = self.volume.value()
        if volume == 0:
            if self.media.state() == Phonon.PlayingState:
                self.volume_label.setPixmap(self.smallPixmap(icons['volume-']))
            else:
                self.volume_label.setPixmap(self.smallPixmap(icons['volume0']))
        elif 0 < volume <= 30:
            self.volume_label.setPixmap(self.smallPixmap(icons['volume1']))
        elif 30 < volume <= 70:
            self.volume_label.setPixmap(self.smallPixmap(icons['volume2']))
        elif 70 < volume < 100:
            self.volume_label.setPixmap(self.smallPixmap(icons['volume3']))

    def smallPixmap(self, path):
        small_size = QtCore.QSize(20, 20)
        return QtGui.QPixmap(path).scaled(small_size, QtCore.Qt.KeepAspectRatio)

    def set_name(self):
        metaData = self.media.metaData()
        title = ''
        if len(metaData) != 0:
            if 'ARTIST' in metaData:
                title += self.media.metaData()['ARTIST'][0]
            if 'TITLE' in metaData:
                title += " - "+self.media.metaData()['TITLE'][0]
        else:
            title += os.path.splitext(os.path.basename(self.path))[0]
        self.title.setText(title)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()

    def playlist(self, parent=None):
        playlist = Playlist(parent)
        playlist.setStyleSheet(style.playlist)
        playlist.exec_()


class Playlist(QtGui.QDialog):
    def __init__(self, parent=None):
        super(Playlist, self).__init__()
        self.resize(350, 300)
        screen = QtGui.QDesktopWidget().screenGeometry()
        self.move((screen.width()-700)/2,
                  (screen.height()-85)/2)
        label = QtGui.QLabel("New Widget")
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(label)
        self.setLayout(vbox)


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    w = Player()
    w.show()
    app.exec_()
