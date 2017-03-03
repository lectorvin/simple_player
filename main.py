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


class Player(QtGui.QDialog):
    def __init__(self, parent=None):
        super(Player, self).__init__(parent)
        self.plist = None

        self.resize(250, 140)
        self.setFixedSize(self.size())
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
        self.title = QtGui.QLabel("Simple Player")
        self.time = QtGui.QLabel()
        self.progress = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.progress.setMinimum(0)
        self.progress.setMaximum(1000)
        self.connect(self.progress, QtCore.SIGNAL("valueChanged(int)"),
                     self.goto)
        self.pl = QtGui.QPushButton('Playlist')
        self.pl.clicked.connect(self.playlist)
        self.pl.setFocusPolicy(QtCore.Qt.NoFocus)
        self.pl.setShortcut(QtGui.QKeySequence(QtCore.Qt.Key_P))

        self.volume = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.volume.setMinimum(0)
        self.volume.setMaximum(100)
        self.volume.setValue(100)
        self.connect(self.volume, QtCore.SIGNAL("valueChanged(int)"),
                     self.changeVolume)
        self.volume_label = QtGui.QLabel()
        self.volume_label.setPixmap(self.smallPixmap(icons['volume3']))

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
        hbox5.addStretch(1)
        hbox5.addWidget(self.play_button)
        hbox5.addWidget(stop_button)

        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        vbox.addWidget(self.progress)
        vbox.addLayout(hbox5)
        self.setLayout(vbox)

        self.media = Phonon.MediaObject()
        audio = Phonon.AudioOutput(Phonon.MusicCategory, self)
        Phonon.createPath(self.media, audio)
        self.media.stateChanged.connect(self.handleStateChanged)
        self.media.tick.connect(self.tick)
        self.media.totalTimeChanged.connect(self.set_total_time)
        self.total_time = None

        self.progress.setStyleSheet(style.progress)
        self.volume.setStyleSheet(style.volume)
        self.play_button.setStyleSheet(style.button)
        stop_button.setStyleSheet(style.button)
        self.setStyleSheet(style.main)
        self.pl.setStyleSheet(style.playlist_button)

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
        self.play_button.setIcon(QtGui.QIcon(icons['play']))
        self.media.stop()
        self.title.setText("Simple Player")

    def message(self, name, message):
        reply = QtGui.QMessageBox.question(self, name, message,
                                           QtGui.QMessageBox.Yes)
        return reply

    def tick(self, time):
        if self.total_time is None:
            return
        self.time.setText("%02d:%02d" % self.ms2hms(self.total_time - time))
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
        return divmod(int(round(time/1000)), 60)

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

    def set_song(self, name):
        self._stop()
        self.title.setText(name.data())
        self.media.setCurrentSource(Phonon.MediaSource(
            self.plist.files[name.row()]))
        self._play()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()

    def closeEvent(self, event):
        self.plist.close()
        event.accept()

    def playlist(self, parent=None):
        self.plist.show()


class Playlist(QtGui.QDialog):
    def __init__(self, parent=None):
        super(Playlist, self).__init__()
        self.player = parent
        self.resize(250, 300)
        self.setFixedSize(self.size())
        self.screen = QtGui.QDesktopWidget().screenGeometry()
        self._files = []
        self._titles = []

        choose = QtGui.QPushButton("Choose file")
        choose.clicked.connect(self.choose_file)
        choose.setShortcut(QtGui.QKeySequence(QtCore.Qt.Key_C))
        choose.setStyleSheet(style.choose)
        self.song_list = QtGui.QListView()
        self.stringList = QtGui.QStringListModel()
        self.song_list.setModel(self.stringList)
        self.connect(self.song_list, QtCore.SIGNAL("clicked(QModelIndex)"),
                     self.player.set_song)
        self.label = QtGui.QLabel()
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.song_list)
        vbox.addWidget(choose)
        self.setLayout(vbox)

    def showEvent(self, event):
        self.move((self.screen.width()-500)/2,
                  (self.screen.height()-85)/2)

    @property
    def files(self):
        return self._files

    def choose_file(self):
        path = QtGui.QFileDialog.\
            getOpenFileName(self, 'Open music file', './music',
                            'Music files (*.mp3 *.wav)')
        if path:
            self._files.append(path)
            self._titles.append(getTitle(path))
            self.stringList.setStringList(self._titles)


def strip(s):
    s = ''.join([chr(x) for x in s])
    while len(s) > 0 and s[-1] in [' ', '\0']:
        s = s[:-1]
    return s


def getTitle(path):
    file_ = open(path, 'rb')
    file_.seek(-128, 2)
    if file_.read(3) == b"TAG":
        title, artist = strip(file_.read(30)), strip(file_.read(30))
        return artist + ' - ' + title
    else:
        return os.path.splitext(os.path.basename(path))[0]

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    w = Player()
    w.show()
    w.plist = Playlist(w)
    app.exec_()
