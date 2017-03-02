button = " \
    QPushButton { \
        border: 1px solid #1f1f91; \
        border-radius: 15px; \
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, \
                            stop:0 #a8bdff, stop:1 #789daf); \
        min-width: 30px; \
        min-height: 30px; \
        max-width: 30px; \
        max-height: 30px; \
    }"

progress = " \
    QSlider::groove:horizontal { \
        border: 1px solid #191919; \
        height: 8px; \
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, \
                            stop:0 #a6a6a6, stop:1 #c1c1c1); \
        margin: 2px 0; \
    } \
        \
    QSlider::handle:horizontal { \
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1, \
                            stop:0 #b4b4b4, stop:1 #8f8f8f); \
        border: 1px solid #5c5c5c; \
        width: 18px; \
        margin: -2px 0; \
        border-radius: 3px; \
    }\
    QSlider::sub-page:horizontal { \
        border: 1px solid #191919; \
        height: 8px; \
        background: #737373; \
        margin: 2px 0; \
    }"

progress_without_handle = " \
    QSlider::groove:horizontal { \
        border: 1px solid #191919; \
        height: 8px; \
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, \
                            stop:0 #a6a6a6, stop:1 #c1c1c1); \
        margin: 2px 0; \
    }"

volume = " \
    QSlider::groove:horizontal { \
        border: 1px solid #001a66; \
        height: 4px; \
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, \
                            stop:0 #a88888, stop:1 #a8bdff); \
        margin: 2px 0; \
    } \
    \
    QSlider::handle:horizontal { \
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1, \
                            stop:0 #3b3c3d, stop:1 #3f3f3f); \
        width: 12px; \
        margin: -5px 0; \
        border-radius: 5px; \
    }"

choose = " \
    QPushButton { \
        border: 1px solid #191919; \
        background: #333333; \
        border-radius: 20px; \
        color: #dce1ef; \
    }"

playlist_button = " \
    QPushButton { \
        border: 1px solid #191919; \
        background: #444444; \
        border-radius: 5px; \
        color: #dce1ef; \
    }"

main = " \
    background-color: #b7b7b7; \
    color: #111111; \
"

playlist = " \
    background-color: #c7c7c7; \
    color: #111111; \
"
