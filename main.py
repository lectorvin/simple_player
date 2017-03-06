# TODO: next/prev song, multidelete, minimize
import sys
import os
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtMultimedia import QMediaPlayer, QMediaPlaylist, QMediaContent
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
         'minus': 'icons/minus.png',
         'previous': 'icons/previous.png',
         'next': 'icons/next.png'}


class Player(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.setWindowFlags(QtCore.Qt.WindowMinimizeButtonHint |
                            QtCore.Qt.FramelessWindowHint)
        self.resize(250, 160)
        self.setFixedSize(self.size())
        screen = QtWidgets.QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width()-2*size.width())/2,
                  (screen.height()-3*size.height())/2)
        self.setWindowTitle("Simple player")
        self.setWindowIcon(QtGui.QIcon(icons['main']))
        self.playlist_widget = None
        self.qplaylist = None
        self.total_time = None
        self.prev_time = 0
        self.prev_state = 'visible'
        self.titlebar = TitleBar("Simple Player", parent=self,
                                 child=self.playlist_widget)

        self.play_button = Button(self._play, 'play', QtCore.Qt.Key_Space)
        stop_button = Button(self._stop, 'stop', QtCore.Qt.Key_S)
        previous_button = Button(self.previous_song, 'previous')
        next_button = Button(self.next_song, 'next')
        self.pl = Button(self.playlist, shortcut=QtCore.Qt.Key_P,
                         name='Playlist', style=style.playlist_button)
        self.volume_label = Button(self.volume0, 'volume3', size=20,
                                   style=style.volume_button)

        self.state = QtWidgets.QLabel()
        self.state.setPixmap(self.smallPixmap(icons['stop_in_circle']))
        self.title = QtWidgets.QLabel("Simple Player")
        self.time = QtWidgets.QLabel()
        self.progress = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.progress.setMinimum(0)
        self.progress.setMaximum(1000)
        self.progress.valueChanged.connect(self.goto)

        self.volume = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.volume.setMinimum(0)
        self.volume.setMaximum(100)
        self.volume.setValue(100)
        self.volume.valueChanged.connect(self.changeVolume)

        self.media = QMediaPlayer()
        self.media.mediaStatusChanged.connect(self.statusChanged)
        self.media.positionChanged.connect(self.positionChanged)
        self.media.durationChanged.connect(self.durationChanged)

        content = QtWidgets.QWidget(self)
        hbox1 = QtWidgets.QHBoxLayout()
        hbox2 = QtWidgets.QHBoxLayout()
        hbox5 = QtWidgets.QHBoxLayout()
        hbox1.addWidget(self.pl)
        hbox1.addWidget(self.volume)
        hbox1.addWidget(self.volume_label)
        hbox2.addWidget(self.state)
        hbox2.addWidget(self.title)
        hbox2.addStretch(1)
        hbox2.addWidget(self.time)
        hbox5.addStretch(1)
        hbox5.addWidget(previous_button)
        hbox5.addWidget(self.play_button)
        hbox5.addWidget(stop_button)
        hbox5.addWidget(next_button)
        vbox = QtWidgets.QVBoxLayout(content)
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        vbox.addWidget(self.progress)
        vbox.addLayout(hbox5)

        vbox2 = QtWidgets.QVBoxLayout(self)
        vbox2.addWidget(self.titlebar)
        vbox2.setContentsMargins(0, 0, 0, 0)
        vbox2.setSpacing(0)
        vbox2.addWidget(content)

        self.progress.setStyleSheet(style.progress)
        self.volume.setStyleSheet(style.volume)
        self.setStyleSheet(style.main)

        self.volume_value = 100

    def playlist(self, parent=None):
        self.playlist_widget.show()

    def _play(self):
        if self.media.state() == QMediaPlayer.PlayingState:
            if self.volume.value() == 0:
                self.volume_label.setIcon(QtGui.QIcon(icons['volume0']))
            self.media.pause()
            self.play_button.setIcon(QtGui.QIcon(icons['play']))
        else:
            if self.volume.value() == 0:
                self.volume_label.setIcon(QtGui.QIcon(icons['volume-']))
            self.media.play()
            self.play_button.setIcon(QtGui.QIcon(icons['pause']))

    def _stop(self):
        if self.volume.value() == 0:
            self.volume_label.setIcon(QtGui.QIcon(icons['volume0']))
        self.play_button.setIcon(QtGui.QIcon(icons['play']))
        self.title.setText("Simple Player")
        self.media.stop()

    def next_song(self):
        self._stop()
        self.qplaylist.next()
        self._play()
        self.title.setText(self.playlist_widget._titles[
            self.qplaylist.currentIndex()])

    def previous_song(self):
        self._stop()
        self.qplaylist.previous()
        self._play()
        self.title.setText(self.playlist_widget._titles[
            self.qplaylist.currentIndex()])

    def volume0(self):
        if self.volume.value() == 0:
            self.media.setVolume(self.volume_value)
            self.volume.setValue(self.volume_value)
        else:
            self.media.setVolume(0)
            self.volume.setValue(0)

    def positionChanged(self, time):
        if self.total_time is None:
            return
        self.time.setText("%02d:%02d" % self.ms2hms(self.total_time - time))
        self.progress.setValue(int(round(time*1000/self.total_time)))
        self.prev_time = time

    def durationChanged(self, time):
        self.total_time = time

    def statusChanged(self, new):
        if new == QMediaPlayer.PlayingState:
            self.state.setPixmap(self.smallPixmap(icons['play_in_circle']))
        elif new == QMediaPlayer.StoppedState:
            self.state.setPixmap(self.smallPixmap(icons['stop_in_circle']))
        elif new == QMediaPlayer.PausedState:
            self.state.setPixmap(self.smallPixmap(icons['pause_in_circle']))
        elif new == QMediaPlayer.EndOfMedia:
            self.media._stop()
            print('end')
        else:
            print(new, 'OOPS')

    def ms2hms(self, time):
        return divmod(int(round(time/1000)), 60)

    def goto(self):
        if self.total_time is None:
            return
        time = int(round(self.progress.value()*self.total_time/1000))
        if abs(self.prev_time - time) > 1500:
            self.media.setPosition(time)
            self.positionChanged(time)

    def changeVolume(self):
        volume = self.volume.value()
        self.media.setVolume(volume)
        if volume != 0:
            self.volume_value = volume
        if volume == 0:
            if self.media.state() == QMediaPlayer.PlayingState:
                self.volume_label.setIcon(QtGui.QIcon(icons['volume-']))
            else:
                self.volume_label.setIcon(QtGui.QIcon(icons['volume0']))
        elif 0 < volume <= 30:
            self.volume_label.setIcon(QtGui.QIcon(icons['volume1']))
        elif 30 < volume <= 70:
            self.volume_label.setIcon(QtGui.QIcon(icons['volume2']))
        elif 70 < volume < 100:
            self.volume_label.setIcon(QtGui.QIcon(icons['volume3']))

    def smallPixmap(self, path):
        small_size = QtCore.QSize(20, 20)
        return QtGui.QPixmap(path).scaled(small_size, QtCore.Qt.KeepAspectRatio)

    def set_song(self, index):
        self.playlist_widget.song_list.setCurrentIndex(index)
        self._stop()
        self.title.setText(index.data())
        self.qplaylist.setCurrentIndex(index.row())
        self._play()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()

    def closeEvent(self, event):
        self.playlist_widget.close()
        event.accept()

    def paintEvent(self, event):
        opt = QtWidgets.QStyleOption()
        opt.initFrom(self)
        painter = QtGui.QPainter(self)
        self.style().drawPrimitive(QtWidgets.QStyle.PE_Widget, opt,
                                   painter, self)

    def changeEvent(self, event):
        if event.type() == QtCore.QEvent.WindowStateChange:
            if self.isVisible() and self.prev_state != 'visible':
                self.prev_state = 'visible'
                self.show()
                if self.playlist_widget.prev_state == 'show':
                    self.playlist_widget.show()
                    self.playlist_widget.showFullScreen()
                else:
                    self.playlist_widget.close()
            if self.isMinimized() and self.prev_state != 'minimized':
                self.prev_state = 'minimized'


class Playlist(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(Playlist, self).__init__()
        self.setWindowTitle("Playlist")
        self.setWindowFlags(QtCore.Qt.WindowMinimizeButtonHint |
                            QtCore.Qt.FramelessWindowHint)
        self.player = parent
        self.player.titlebar.child = self
        self.resize(250, 300)
        self.setFixedSize(self.size())
        self._files = []
        self._titles = []
        self.titlebar = TitleBar('Playlist', minimize=False, parent=self)
        self.titlebar.close_.setShortcut(QtGui.QKeySequence(QtCore.Qt.Key_P))
        self.prev_state = 'hidden'

        content = QtWidgets.QWidget(self)
        plus = Button(icon='plus', size=12, shortcut=QtCore.Qt.Key_Plus)
        menu1 = QtWidgets.QMenu()
        menu1.addAction('add song', self.choose_file,
                        QtGui.QKeySequence(QtCore.Qt.Key_F))
        menu1.addAction('add directory', self.choose_dir,
                        QtGui.QKeySequence(QtCore.Qt.Key_D))
        plus.setMenu(menu1)
        minus = Button(icon='minus', size=12, shortcut=QtCore.Qt.Key_Minus)
        menu2 = QtWidgets.QMenu()
        menu2.addAction('remove selected', self.remove_selected,
                        QtGui.QKeySequence(QtCore.Qt.Key_Delete))
        minus.setMenu(menu2)
        self.playlist = QMediaPlaylist()
        self.player.media.setPlaylist(self.playlist)
        self.player.qplaylist = self.playlist
        self.song_list = QtWidgets.QListView()
        self.stringList = QtCore.QStringListModel()
        self.song_list.setModel(self.stringList)
        self.song_list.doubleClicked.connect(self.player.set_song)
        self.label = QtWidgets.QLabel()
        hbox = QtWidgets.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(plus)
        hbox.addWidget(minus)
        vbox = QtWidgets.QVBoxLayout(content)
        vbox.addWidget(self.song_list)
        vbox.addLayout(hbox)
        vbox2 = QtWidgets.QVBoxLayout(self)
        vbox2.addWidget(self.titlebar)
        vbox2.setContentsMargins(0, 0, 0, 0)
        vbox2.setSpacing(0)
        vbox2.addWidget(content)

        self.song_list.setStyleSheet(style.list_view)
        self.setStyleSheet(style.playlist)
        plus.setStyleSheet(style.small_button)
        minus.setStyleSheet(style.small_button)

    @property
    def files(self):
        return self._files

    def choose_file(self):
        path = QtWidgets.QFileDialog.\
            getOpenFileName(self, 'Open music file', './music',
                            'Music files (*.mp3 *.wav)')
        if path:
            path = path[0]
            self._files.append(path)
            self._titles.append(getTitle(path))
            self.stringList.setStringList(self._titles)
            self.playlist.addMedia(QMediaContent(
                QtCore.QUrl.fromLocalFile(path)))

    def choose_dir(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(self,
                                                          'Open directory', '.')
        if os.path.isdir(path):
            for x in os.listdir(path):
                if x.endswith('.mp3'):
                    self._files.append(os.path.join(path, x))
                    self._titles.append(getTitle(os.path.join(path, x)))
                    self.playlist.addMedia(QMediaContent(
                        QtCore.QUrl.fromLocalFile(os.path.join(path, x))))
            self.stringList.setStringList(self._titles)

    def remove_selected(self):
        indexes = [x.row() for x in self.song_list.selectedIndexes()]
        if len(indexes) > 0:
            for x in reversed(sorted(indexes)):
                self._files.pop(x)
                self._titles.pop(x)
            self.stringList.setStringList(self._titles)
            if len(self._files) > sorted(indexes)[0]+1:
                index = self.stringList.createIndex(sorted(indexes)[0], 0)
            else:
                index = self.stringList.createIndex(len(self._files)-1, 0)
            self.song_list.setCurrentIndex(index)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()

    def showEvent(self, event):
        self.prev_state = 'show'
        self.resize(250, 300)
        if not self.player.isMinimized():
            screen = QtWidgets.QDesktopWidget().screenGeometry()
            event.accept()
            self.move((screen.width()-500)/2, (screen.height()-160)/2)
        else:
            self.close()
            if self.player.prev_state != 'minimized':
                self.player.show()

    def closeEvent(self, event):
        self.prev_state = 'hidden'
        event.accept()


class TitleBar(QtWidgets.QDialog):
    def __init__(self, name, minimize=True, parent=None, child=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.parent = parent
        self.child = child
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

        self.close_ = Button(self.close, 'close', style='')
        name = QtWidgets.QLabel(name)

        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(name)
        hbox.addStretch(1)
        if minimize:
            self.minimize = Button(self.showSmall, 'minimize', style='')
            hbox.addWidget(self.minimize)
        hbox.addWidget(self.close_)
        self.setLayout(hbox)
        self.setStyleSheet(style.titlebar)

    def showSmall(self):
        self.parent.showMinimized()
        self.child.showMinimized()

    def close(self):
        self.parent.close()


class Button(QtWidgets.QPushButton):
    def __init__(self, action=None, icon='', shortcut=None, name='',
                 style=style.button, size=10, parent=None):
        QtWidgets.QPushButton.__init__(self, parent)
        self.setText(name)
        if icon in icons.keys():
            self.setIcon(QtGui.QIcon(icons[icon]))
            self.setIconSize(QtCore.QSize(size, size))
        if shortcut is not None:
            self.setShortcut(QtGui.QKeySequence(shortcut))
        if action is not None:
            self.clicked.connect(action)
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.setStyleSheet(style)


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
    app = QtWidgets.QApplication(sys.argv)
    w = Player()
    w.show()
    w.playlist_widget = Playlist(w)
    app.exec_()
