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
         'volume3': 'icons/volume3.png',
         'close': 'icons/close.png',
         'minimize': 'icons/minimize.png',
         'plus': 'icons/plus.png',
         'minus': 'icons/minus.png'}


class Player(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.plist = None
        self.m_titlebar = TitleBar("Simple Player", parent=self,
                                   child=self.plist)
        self.setWindowFlags(QtCore.Qt.WindowMinimizeButtonHint |
                            QtCore.Qt.FramelessWindowHint)

        self.resize(250, 160)
        self.setFixedSize(self.size())
        screen = QtGui.QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width()-2*size.width())/2,
                  (screen.height()-3*size.height())/2)
        self.setWindowTitle("Simple player")
        self.setWindowIcon(QtGui.QIcon(icons['main']))
        self.prev_time = 0
        self.prev_state = 'visible'
        button_size = QtCore.QSize(10, 10)

        self.play_button = QtGui.QPushButton(QtGui.QIcon(icons['play']), '')
        self.play_button.clicked.connect(self._play)
        self.play_button.setIconSize(button_size)
        self.play_button.setShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Space))
        self.play_button.setFocusPolicy(QtCore.Qt.NoFocus)
        stop_button = QtGui.QPushButton(QtGui.QIcon(icons['stop']), '')
        stop_button.clicked.connect(self._stop)
        stop_button.setIconSize(button_size)
        stop_button.setShortcut(QtGui.QKeySequence(QtCore.Qt.Key_S))
        stop_button.setFocusPolicy(QtCore.Qt.NoFocus)

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

        content = QtGui.QWidget(self)
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
        vbox = QtGui.QVBoxLayout(content)
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        vbox.addWidget(self.progress)
        vbox.addLayout(hbox5)

        vbox2 = QtGui.QVBoxLayout(self)
        vbox2.addWidget(self.m_titlebar)
        vbox2.setContentsMargins(0, 0, 0, 0)
        vbox2.setSpacing(0)
        vbox2.addWidget(content)

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

    def playlist(self, parent=None):
        self.plist.showFullScreen()

    def _play(self):
        if self.media.state() == Phonon.PlayingState:
            if self.volume.value() == 0:
                self.volume_label.setPixmap(self.smallPixmap(icons['volume0']))
            self.media.pause()
            self.play_button.setIcon(QtGui.QIcon(icons['play']))
        elif self.media.state() in [Phonon.StoppedState, Phonon.PausedState]:
            if self.volume.value() == 0:
                self.volume_label.setPixmap(self.smallPixmap(icons['volume-']))
            if self.media.currentSource().type() == Phonon.MediaSource.Empty:
                if len(self.plist.stringList.stringList()) > 0:
                    if len(self.plist.song_list.selectedIndexes()) > 0:
                        self.set_song(self.plist.song_list.selectedIndexes()[0])
                    else:
                        index = self.plist.stringList.createIndex(0, 0)
                        self.plist.song_list.setCurrentIndex(index)
                        self.set_song(index)
            else:
                self.media.play()
                self.play_button.setIcon(QtGui.QIcon(icons['pause']))
        else:
            self.message('Error', 'Unexpected error {}!'.format(
                self.media.state()))

    def _stop(self):
        if self.volume.value() == 0:
            self.volume_label.setPixmap(self.smallPixmap(icons['volume0']))
        self.play_button.setIcon(QtGui.QIcon(icons['play']))
        self.media.stop()
        self.title.setText("Simple Player")
        self.media.clear()

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

    def set_song(self, index):
        self.plist.song_list.setCurrentIndex(index)
        self._stop()
        self.title.setText(index.data())
        self.media.setCurrentSource(Phonon.MediaSource(
            self.plist.files[index.row()]))
        self._play()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()

    def closeEvent(self, event):
        self.plist.close()
        event.accept()

    def paintEvent(self, event):
        opt = QtGui.QStyleOption()
        opt.init(self)
        painter = QtGui.QPainter(self)
        self.style().drawPrimitive(QtGui.QStyle.PE_Widget, opt, painter, self)

    def changeEvent(self, event):
        if event.type() == QtCore.QEvent.WindowStateChange:
            if self.isVisible() and self.prev_state != 'visible':
                self.prev_state = 'visible'
                self.show()
                self.showMaximized()
                self.showFullScreen()
                if self.plist.prev_state == 'show':
                    self.plist.show()
                    self.plist.showMaximized()
                    self.plist.showFullScreen()
                else:
                    self.plist.close()
            if self.isMinimized() and self.prev_state != 'minimized':
                self.prev_state = 'minimized'


class Playlist(QtGui.QWidget):
    def __init__(self, parent=None):
        super(Playlist, self).__init__()
        self.setWindowTitle("Playlist")
        self.setWindowFlags(QtCore.Qt.WindowMinimizeButtonHint |
                            QtCore.Qt.FramelessWindowHint)
        self.player = parent
        self.player.m_titlebar.child = self
        self.resize(250, 300)
        self.setFixedSize(self.size())
        self._files = []
        self._titles = []
        self.titlebar = TitleBar('Playlist', minimize=False, parent=self)
        self.titlebar.close_.setShortcut(QtGui.QKeySequence(QtCore.Qt.Key_P))
        self.prev_state = 'hidden'

        content = QtGui.QWidget(self)
        plus = QtGui.QPushButton(QtGui.QIcon(icons['plus']), '')
        plus.setFocusPolicy(QtCore.Qt.NoFocus)
        menu1 = QtGui.QMenu()
        menu1.addAction('add song', self.choose_file)
        menu1.addAction('add directory', self.choose_dir)
        plus.setMenu(menu1)
        minus = QtGui.QPushButton(QtGui.QIcon(icons['minus']), '')
        minus.setFocusPolicy(QtCore.Qt.NoFocus)
        menu2 = QtGui.QMenu()
        menu2.addAction('remove selected', self.remove_selected)
        minus.setMenu(menu2)
        self.song_list = QtGui.QListView()
        self.stringList = QtGui.QStringListModel()
        self.song_list.setModel(self.stringList)
        self.connect(self.song_list,
                     QtCore.SIGNAL("doubleClicked(QModelIndex)"),
                     self.player.set_song)
        self.label = QtGui.QLabel()
        hbox = QtGui.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(plus)
        hbox.addWidget(minus)
        vbox = QtGui.QVBoxLayout(content)
        vbox.addWidget(self.song_list)
        vbox.addLayout(hbox)
        vbox2 = QtGui.QVBoxLayout(self)
        vbox2.addWidget(self.titlebar)
        vbox2.setContentsMargins(0, 0, 0, 0)
        vbox2.setSpacing(0)
        vbox2.addWidget(content)

        self.song_list.setStyleSheet(style.list_view)
        self.setStyleSheet(style.playlist)
        plus.setStyleSheet(style.small_button)
        minus.setStyleSheet(style.small_button)
        # self.set_song(self.plist.song_list.selectedIndexes()[0])

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

    def choose_dir(self):
        path = QtGui.QFileDialog.getExistingDirectory(self, 'Open directory',
                                                      '.')
        if os.path.isdir(path):
            for x in os.listdir(path):
                if x.endswith('.mp3'):
                    self._files.append(os.path.join(path, x))
                    self._titles.append(getTitle(os.path.join(path, x)))
            self.stringList.setStringList(self._titles)

    def remove_selected(self):
        indexes = [x.row() for x in self.song_list.selectedIndexes()]
        for x in reversed(sorted(indexes)):
            self._files.pop(x)
            self._titles.pop(x)
        self.stringList.setStringList(self._titles)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()

    def showEvent(self, event):
        self.prev_state = 'show'
        if not self.player.isMinimized():
            screen = QtGui.QDesktopWidget().screenGeometry()
            event.accept()
            self.move((screen.width()-500)/2,
                      (screen.height()-160)/2)
        else:
            self.close()
            if self.player.prev_state != 'minimized':
                self.player.show()
                self.player.showFullScreen()

    def closeEvent(self, event):
        self.prev_state = 'hidden'
        event.accept()


class TitleBar(QtGui.QDialog):
    def __init__(self, name, minimize=True, parent=None, child=None):
        QtGui.QWidget.__init__(self, parent)
        self.parent = parent
        self.child = child
        self.setWindowTitle(name)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAutoFillBackground(True)
        self.setBackgroundRole(QtGui.QPalette.Highlight)
        self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        self.setStyleSheet(style.titlebar)

        self.close_ = QtGui.QToolButton()
        self.close_.setIcon(QtGui.QIcon(icons['close']))
        self.close_.clicked.connect(self.close)
        self.close_.setFocusPolicy(QtCore.Qt.NoFocus)
        name = QtGui.QLabel(name)
        self.maxNormal = False

        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(name)
        hbox.addStretch(1)
        if minimize:
            self.minimize = QtGui.QToolButton()
            self.minimize.setIcon(QtGui.QIcon(icons['minimize']))
            self.minimize.clicked.connect(self.showSmall)
            self.minimize.setFocusPolicy(QtCore.Qt.NoFocus)
            hbox.addWidget(self.minimize)
        hbox.addWidget(self.close_)
        self.setLayout(hbox)

    def showSmall(self):
        self.parent.showMinimized()
        self.child.showMinimized()

    def close(self):
        self.parent.close()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()


def strip(s):    # from byte array to string without '\0'
    return (''.join([chr(x) for x in s if x > 0])).strip()


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
