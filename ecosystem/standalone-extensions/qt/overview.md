# Overview

![CI](https://github.com/php-io-extensions/qt/actions/workflows/ci.yml)

[![CI](https://img.shields.io/github/actions/workflow/status/php-io-extensions/qt/ci.yml?style=flat-square&label=CI)](https://github.com/php-io-extensions/qt/actions/workflows/ci.yml)

1:1 PHP bindings of Qt 6, written directly in C++ against the Zend API. Each
PHP class is its C++ counterpart (`QApplication`, `QTimer`, `QSocketNotifier`,
…) and each method is one Qt call. Nested C++ scopes become PHP namespaces:
`Qt::TimerType` is `Qt\TimerType`, `QMetaObject::Connection` is
`QMetaObject\Connection`. No defaults, no composites: behaviour is composed by
the caller.

Linux first, macOS too. Qt 6.4+ with the Multimedia and MultimediaWidgets
modules, PHP 8.4+, NTS and ZTS.

## What is bound

The calls that create the application, pump Qt's event dispatcher, sleep with a
budget, wake a sleep, open and close windows, build menu bars, lay widgets out,
style them, drive the common controls and play video:

| Class | Qt |
|---|---|
| `QObject` | constructor, `objectName`, `setObjectName`, `inherits`, `parent`, `setParent`, `children`, `deleteLater`, `connect` (string signature), `disconnect` |
| `QCoreApplication`, `QGuiApplication`, `QApplication` | constructors, `instance`, `processEvents` (both overloads), `sendPostedEvents`, `exec`, `quit`, `exit`, `applicationName`, `setApplicationName`, `applicationPid`, `closingDown`, `startingUp`, `platformName`, `desktopFileName`, `setDesktopFileName`, `applicationDisplayName`, `setApplicationDisplayName`, `quitOnLastWindowClosed`, `setQuitOnLastWindowClosed` |
| `QTimer` | constructor, `start` (both overloads), `stop`, `isActive`, `interval`, `setInterval`, `isSingleShot`, `setSingleShot`, `timerType`, `setTimerType`, `remainingTime`, `timerId`, `singleShot` (functor overload) |
| `QSocketNotifier` | constructor (fd as int, stream or Socket), `socket`, `type`, `isEnabled`, `setEnabled`, `isValid` |
| `QAbstractEventDispatcher` | `instance`, `processEvents`, `wakeUp`, `interrupt` |
| `QMetaObject\Connection` | `operator bool` as `isValid()` |
| `QMetaObject` | `invokeMethod` (object, member name, arguments converted to its parameter types: calls a slot or emits a signal) |
| `QWidget` | constructor, `createWindowContainer` (static; the container owns the window), `show`, `hide`, `close`, `isVisible`, `setVisible`, `isWindow`, `isActiveWindow`, `activateWindow`, `setFocus`, `hasFocus`, `raise`, `windowTitle`, `setWindowTitle`, `resize`, `width`, `height`, `size`, `sizeHint`, `pos`, `geometry`, `setGeometry`, `move`, `setMinimumSize`, `minimumWidth`, `minimumHeight`, `setFixedSize`, `setSizePolicy`, `setLayout`, `layout`, `isEnabled`, `setEnabled`, `styleSheet`, `setStyleSheet`, `font`, `setFont`, `setParent` (widgets only), `parentWidget`, `setAttribute`, `testAttribute` |
| `QWindow`, `QSurface\SurfaceType` | constructor (needs a `QGuiApplication`), `setSurfaceType`, `surfaceType`, `winId` (the native handle: an `NSView` address on macOS; creates the platform window when it has none), `create`, `show`, `hide`, `destroy`, `isExposed`, `resize`, `close`, `width`, `height`, `devicePixelRatio`, `setVulkanInstance`, `vulkanInstance`; the seven surface types |
| `QVulkanInstance` | constructor, `setVkInstance` (adopts a `VkInstance` address, e.g. ext-vulkan's `VkInstance::pointer()`), `create`, `isValid`, `errorCode`, `vkInstance`, `destroy`, static `surfaceForWindow` (a `VkSurfaceKHR` address). Present when Qt was built with Vulkan. On macOS set `QT_VULKAN_LIB` to the loader (`$(pkg-config --variable=libdir vulkan)/libvulkan.1.dylib`): Qt loads it by name and Homebrew's is outside dyld's search path |
| `QMainWindow` | constructor, `menuBar`, `setMenuBar`, `centralWidget`, `setCentralWidget` |
| `QMenuBar`, `QMenu` | constructors, `addMenu` (both overloads), `addAction`, `clear`, `isNativeMenuBar`, `setNativeMenuBar`; `title`, `setTitle`, `addSeparator`, `isEmpty`, `menuAction`, `popup(x, y)` |
| `QAction` | constructor, `text`, `setText`, `isCheckable`, `setCheckable`, `isChecked`, `setChecked`, `isEnabled`, `setEnabled`, `isSeparator`, `setSeparator`, `menuRole`, `setMenuRole`, `shortcut`, `setShortcut`, `trigger`, `toggle` |
| `QDialog`, `QMessageBox` | constructors, `open`, `isModal`, `setModal`, `result`, `done`, `accept`, `reject`; `text`, `setText`, `informativeText`, `setInformativeText` |
| `QObject` (filters) | `installEventFilter`, `removeEventFilter` |
| `QOpenGLWidget`, `QOpenGLPainter`, `QSurfaceFormat` | constructor, `makeCurrent`, `doneCurrent`, `isValid`, `defaultFramebufferObject`, `update`, `setFormat`, `format`; `QSurfaceFormat` version, profile and renderable type (`defaultFormat`); trampoline: `new QOpenGLPainter(callable, ?QWidget)` runs PHP from `paintGL()` |
| `QEventFilter` | trampoline: `new QEventFilter(callable, ?array $types)`; hands the listed event types of each watched object to PHP as `($watched, $type, QEvent $event)`, the event alive only during the call |
| `QEvent`, `QInputEvent`, `QMouseEvent`, `QContextMenuEvent` | `type`, `accept`, `ignore`, `isAccepted`, `spontaneous`; `modifiers`, `timestamp`, `deviceType` (`QInputDevice\DeviceType`); mouse `button`, `buttons`, `position`, `globalPosition`; context menu `reason` (`QContextMenuEvent\Reason`), `pos`, `globalPos`; constructors for the mouse and context-menu events, sent with `QCoreApplication::sendEvent` |
| Hit tests, hints | `QApplication::widgetAt`, `QApplication::focusWidget`, `QWidget::mapFromGlobal`, `QGuiApplication::styleHints()` → `QStyleHints` `mousePressAndHoldInterval`, `startDragDistance` |
| `QLayout` | `setSpacing`, `spacing`, `setContentsMargins`, `count`, `removeWidget`, `indexOf`, `itemAtWidget` (`itemAt(i)->widget()`) |
| `QBoxLayout`, `QVBoxLayout`, `QHBoxLayout` | constructors (optional parent widget), `addWidget(widget, stretch, alignment)`, `insertWidget`, `addLayout`, `addStretch`, `setStretch`, `setAlignment`; widgets added before the layout is installed are held until it is |
| `QGridLayout` | constructor, `addWidget(widget, row, column, rowSpan, columnSpan, alignment)`, `addItem(QSpacerItem, …)`, `rowCount`, `columnCount`, `setRowStretch`, `setColumnStretch`, `rowStretch`, `columnStretch`, `setHorizontalSpacing`, `setVerticalSpacing`, `itemAtPosition` (its widget) |
| `QSpacerItem` | constructor (w, h, policies), `changeSize`, `sizeHint` |
| `QLabel` | constructor, `text`, `setText`, `alignment`, `setAlignment`, `wordWrap`, `setWordWrap`, `setScaledContents`, `pixmap`, `setPixmap`, `textFormat`, `setTextFormat`, `openExternalLinks`, `setOpenExternalLinks`, `textInteractionFlags`, `setTextInteractionFlags`; signals `linkActivated(QString)`, `linkHovered(QString)` |
| `QDesktopServices` | `openUrl` |
| `QAbstractButton`, `QPushButton`, `QCheckBox` | constructors (text, parent), `text`, `setText`, `isCheckable`, `setCheckable`, `isChecked`, `setChecked`, `click`, `toggle`; signals `clicked(bool)`, `toggled(bool)` |
| `QAbstractSlider`, `QSlider` | constructor (orientation, vertical by default as in Qt, parent), `minimum`, `maximum`, `setRange`, `value`, `setValue`, `orientation`, `setOrientation`; signal `valueChanged(int)` |
| `QComboBox` | constructor, `addItem`, `addItems`, `clear`, `count`, `currentIndex`, `setCurrentIndex`, `currentText`, `itemText`; signal `currentIndexChanged(int)` |
| `QLineEdit` | constructor (text, parent), `text`, `setText`, `placeholderText`, `setPlaceholderText`, `echoMode`, `setEchoMode`, `isReadOnly`, `setReadOnly`, `cut`, `copy`, `paste`, `selectAll`, `undo`, `redo`, `selectedText`; signals `textChanged(QString)`, `returnPressed()` |
| `QPlainTextEdit` | constructor, `toPlainText`, `setPlainText`, `isReadOnly`, `setReadOnly`, `cut`, `copy`, `paste`, `selectAll`, `undo`, `redo`; signal `textChanged()` |
| `QDateEdit` | constructor, `date`, `setDate` (ISO 8601 strings), `setCalendarPopup`, `setDisplayFormat`; signal `dateChanged(QDate)` as the ISO string |
| `QProgressBar` | constructor, `minimum`, `maximum`, `setRange`, `value`, `setValue`, `setTextVisible`, `reset` |
| `QFrame`, `QScrollArea` | constructors, `frameShape`, `setFrameShape`, `setFrameShadow`; `setWidget`, `widget`, `setWidgetResizable`, `setHorizontalScrollBarPolicy`, `setVerticalScrollBarPolicy` |
| `QAbstractItemView`, `QTableWidget`, `QTableWidgetItem` | `setSelectionBehavior`, `setSelectionMode`, `setEditTriggers`, `NO_EDIT_TRIGGERS`; constructor (rows, columns, parent), `rowCount`, `setRowCount`, `columnCount`, `setColumnCount`, `setHorizontalHeaderLabels`, `horizontalHeaderItem`, `selectedItems`, `clearSelection`, `setItem`, `item`, `clearContents`, `currentRow`, `selectRow`; item constructor, `text`, `setText`, `row`; signals `itemSelectionChanged()`, `cellClicked(int,int)` |
| `QFont`, `QPixmap` | values: constructor (family, point size, weight on Qt's 1–1000 scale), `family`, `setFamily`, `pointSizeF`, `setPointSizeF`, `weight`, `setWeight`; constructor, `load`, `isNull`, `width`, `height`, `scaled` |
| `QImage` | a value made from bytes or an address (an ext-fb buffer's `pointer()`, trusted): constructor (data, width, height, bytes per line, `QImage\Format`), `isNull`, `width`, `height`, `format`; `QPixmap::fromImage` turns it into a pixmap |
| `QUrl` | value: `fromLocalFile`, `toString`, `isValid` |
| `QAudioOutput` | constructor, `setMuted`, `isMuted`, `setVolume`, `volume` |
| `QMediaPlayer` | constructor, `setVideoOutput`, `setAudioOutput`, `setSource`, `source`, `play`, `pause`, `stop`, `position`, `duration`, `setPosition`, `playbackState`, `mediaStatus`, `setLoops`, `INFINITE_LOOPS`, `errorString`, `hasVideo`, `isAvailable`; signals `playbackStateChanged`, `mediaStatusChanged`, `errorOccurred`, `positionChanged` |
| `QVideoWidget` | constructor |

Enums: `QEventLoop\ProcessEventsFlag`, `Qt\TimerType`, `QSocketNotifier\Type`,
`QAction\MenuRole`, `Qt\Orientation`, `Qt\AspectRatioMode`, `Qt\ScrollBarPolicy`,
`QSizePolicy\Policy`, `QLineEdit\EchoMode`, `QFont\Weight`, `QFrame\Shape`,
`QFrame\Shadow`, `QAbstractItemView\SelectionBehavior`,
`QAbstractItemView\SelectionMode`, `QMediaPlayer\PlaybackState`,
`QMediaPlayer\MediaStatus`, `QMediaPlayer\Error`, and, generated from the Qt
headers by `scripts/gen-enum.php`, `QEvent\Type`, `Qt\WidgetAttribute` and
`Qt\AlignmentFlag`. QFlags parameters (`alignment`) take the enum or an OR'd int.
Function: `qVersion()`. The stubs in `stubs/` are the full declaration.

Signals connect by the signature `SIGNAL()` spells, and the callable receives
the signal's arguments:

```php
QObject::connect($timer, 'timeout()', fn () => …);
QObject::connect($notifier, 'activated(QSocketDescriptor,QSocketNotifier::Type)', fn (int $fd, int $type) => …);
```

## Example

```php
$app = new QApplication([PHP_BINARY]);

// Sleep up to 16 ms, or until an event arrives, dispatching what does.
$budget = new QTimer();
$budget->setSingleShot(true);
$budget->start(16);
QCoreApplication::processEvents(QEventLoop\ProcessEventsFlag::WAIT_FOR_MORE_EVENTS);

// Wake on a descriptor (a kqueue or epoll fd works: it turns readable when its own events are pending).
$notifier = new QSocketNotifier($fd, QSocketNotifier\Type::READ);
QObject::connect($notifier, 'activated(QSocketDescriptor,QSocketNotifier::Type)', fn () => null);
```

## Install

```bash
bash install-debian-trixie.sh   # Debian, Ubuntu, Raspberry Pi OS (needs qt6-base-dev, qt6-multimedia-dev, libqt6multimediawidgets6, g++)
bash install-macos.sh           # Homebrew php@8.4 and php@8.4-zts (needs brew install qt, which carries Multimedia)
```

Or with PIE: `pie install php-io-extensions/qt`.

`venusian build` reads the system packages from `extra.venusian.system` in composer.json: apt packages to build with and the run-time ones a `.deb` depends on or recommends, and the Homebrew ones.

## Test

```bash
composer install
php vendor/bin/pest
php examples/smoke.php          # bridge: application, pump, sleep, wake; prints SMOKE_OK
php examples/window-smoke.php   # window, menu bar, actions, close filter; prints SMOKE_OK
```

`tests/VideoTest.php` plays `tests/fixtures/clip.mp4` (1.2 s, silent) through the
platform media backend: AVFoundation on macOS, the FFmpeg plugin of
`libqt6multimedia6` on Debian.

On Linux over SSH, export the session's `DISPLAY` (and `WAYLAND_DISPLAY` when
the `qt6-wayland` platform plugin is installed) first. Design notes live in the
OKF bundle under `.okf/`.

## License

MIT
