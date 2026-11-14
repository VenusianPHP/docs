# Overview

![CI](https://github.com/php-io-extensions/qt/actions/workflows/ci.yml)

[![CI](https://img.shields.io/github/actions/workflow/status/php-io-extensions/qt/ci.yml?style=flat-square&label=CI)](https://github.com/php-io-extensions/qt/actions/workflows/ci.yml)
[![Qt API](https://img.shields.io/badge/Qt_API-5.7%25_%28647%2F11435%29-blue?style=flat-square)](https://github.com/php-io-extensions/qt/blob/v0.11.0/SUPPORT.md)

1:1 PHP bindings of Qt 6, written directly in C++ against the Zend API. Each
PHP class is its C++ counterpart (`QApplication`, `QTimer`, `QSocketNotifier`,
…) and each method is one Qt call. Nested C++ scopes become PHP namespaces:
`Qt::TimerType` is `Qt\TimerType`, `QMetaObject::Connection` is
`QMetaObject\Connection`. Qt's value classes (`QPoint`, `QSize`, `QRect`,
`QDate`, `QKeySequence`, `QUrl`, …) are PHP value objects. No defaults Qt lacks,
no composites: behaviour is composed by the caller. What Qt does passes through
(invalid values, nullptr as `null`, its warnings on stderr); the extension
refuses a call only where a probe showed it crashes, and `tests/Probes` shows
each one (`./configure --enable-qt --enable-qt-probes`).

Linux first, macOS too. Qt 6.4+ with the Multimedia and MultimediaWidgets
modules, PHP 8.4+, NTS and ZTS.

## What is bound

The calls that create the application, pump Qt's event dispatcher, sleep with a
budget, wake a sleep, open and close windows, build menu bars, lay widgets out,
style them, drive the common controls and play video:

| Class | Qt |
|---|---|
| `QObject` | constructor, `objectName`, `setObjectName`, `inherits`, `parent`, `setParent`, `children`, `deleteLater`, `connect` (string signature), `disconnect` |
| `QCoreApplication`, `QGuiApplication`, `QApplication` | constructors, `instance`, `processEvents` (both overloads), `sendPostedEvents`, `exec`, `quit`, `exit`, `applicationName`, `setApplicationName`, `applicationPid`, `closingDown`, `startingUp`, `setAttribute`, `testAttribute` (`Qt\ApplicationAttribute`), `platformName`, `desktopFileName`, `setDesktopFileName`, `applicationDisplayName`, `setApplicationDisplayName`, `quitOnLastWindowClosed`, `setQuitOnLastWindowClosed` |
| `QTimer` | constructor, `start` (both overloads), `stop`, `isActive`, `interval`, `setInterval`, `isSingleShot`, `setSingleShot`, `timerType`, `setTimerType`, `remainingTime`, `timerId`, `singleShot` (functor overload) |
| `QSocketNotifier` | constructor (fd as int, stream or Socket), `socket`, `type`, `isEnabled`, `setEnabled`, `isValid` |
| `QAbstractEventDispatcher` | `instance`, `processEvents`, `wakeUp`, `interrupt` |
| `QMetaObject\Connection` | `operator bool` as `isValid()` |
| `QMetaObject` | `invokeMethod` (object, member name, `Qt\ConnectionType`, arguments converted to its parameter types: calls a slot or emits a signal) |
| `QWidget` | constructor, `createWindowContainer` (static; the container owns the window), `show`, `hide`, `close`, `isVisible`, `setVisible`, `isWindow`, `window`, `windowFlags`, `setWindowFlags`, `windowModality`, `setWindowModality`, `isActiveWindow`, `activateWindow`, `setFocus`, `clearFocus`, `hasFocus`, `focusPolicy`, `setFocusPolicy` (`Qt\FocusPolicy`), `setTabOrder` (static), `raise`, `windowTitle`, `setWindowTitle`, `resize`, `width`, `height`, `size`, `sizeHint`, `pos`, `geometry`, `setGeometry`, `move`, `setMinimumSize`, `minimumWidth`, `minimumHeight`, `setFixedSize`, `setSizePolicy`, `setLayout`, `layout`, `isEnabled`, `setEnabled`, `styleSheet`, `setStyleSheet`, `font`, `setFont`, `setParent` (widgets only), `parentWidget`, `setAttribute`, `testAttribute` |
| `QWindow`, `QSurface\SurfaceType` | constructor (needs a `QGuiApplication`), `setSurfaceType`, `surfaceType`, `winId` (the native handle: an `NSView` address on macOS; creates the platform window when it has none), `create`, `show`, `hide`, `destroy`, `isExposed`, `resize`, `close`, `width`, `height`, `devicePixelRatio`, `setVulkanInstance`, `vulkanInstance`; the seven surface types |
| `QVulkanInstance` | constructor, `setVkInstance` (adopts a `VkInstance` address, e.g. ext-vulkan's `VkInstance::pointer()`), `create`, `isValid`, `errorCode`, `vkInstance`, `destroy`, static `surfaceForWindow` (a `VkSurfaceKHR` address). Present when Qt was built with Vulkan. On macOS set `QT_VULKAN_LIB` to the loader (`$(pkg-config --variable=libdir vulkan)/libvulkan.1.dylib`): Qt loads it by name and Homebrew's is outside dyld's search path |
| `QMainWindow` | constructor, `menuBar`, `setMenuBar`, `centralWidget`, `setCentralWidget` |
| `QMenuBar`, `QMenu` | constructors, `addMenu(title)`, `addAction`, `clear`, `isNativeMenuBar`, `setNativeMenuBar`; `title`, `setTitle`, `addSeparator`, `isEmpty`, `menuAction`, `popup(QPoint, ?QAction)` |
| `QAction` | constructor, `text`, `setText`, `isCheckable`, `setCheckable`, `isChecked`, `setChecked`, `isEnabled`, `setEnabled`, `isSeparator`, `setSeparator`, `menuRole`, `setMenuRole`, `shortcut`, `setShortcut` (`QKeySequence`), `trigger`, `toggle` |
| `QDialog`, `QMessageBox`, `QFileDialog` | constructors, `open`, `isModal`, `setModal`, `result`, `done`, `accept`, `reject`; `text`, `setText`, `informativeText`, `setInformativeText`, `icon`, `setIcon` (`QMessageBox\Icon`), `checkBox`, `setCheckBox`, `addButton` (`QMessageBox\ButtonRole`), `setDefaultButton`, `setEscapeButton`, `clickedButton`; `setFileMode`, `setAcceptMode`, `setOption` (`QFileDialog\FileMode`, `AcceptMode`, `Option`), `setDirectory`, `selectFile`, `selectedFiles`, `nameFilters`, `setNameFilters`, `filter`, `setFilter` (`QDir\Filter`, or an int of or-ed bits) |
| `QClipboard` | from `QGuiApplication::clipboard()` (null, with Qt's warning, before a `QGuiApplication`): `setText`, `text`, `clear`, `mimeData` (`QClipboard\Mode`) |
| `QMimeData` | constructor, `hasText`, `formats` |
| `QStyle`, `QStyleOption`, `QStyleOptionButton` | `QWidget::style()` (abstract, the application's style object), `subElementRect` (`QStyle\SubElement`); value classes: constructor, `initFrom`; constructor (held as its `QStyleOption` base) |
| `QObject` (filters) | `installEventFilter`, `removeEventFilter` |
| `QOpenGLWidget`, `QOpenGLPainter`, `QSurfaceFormat` | constructor, `makeCurrent`, `doneCurrent`, `isValid`, `defaultFramebufferObject`, `update`, `setFormat`, `format`; `QSurfaceFormat` version, profile and renderable type (`defaultFormat`, `setDefaultFormat`); trampoline: `new QOpenGLPainter(callable, ?QWidget)` runs PHP from `paintGL()` |
| `QEventFilter` | trampoline: `new QEventFilter(callable)`; hands every event of each watched object to PHP as `($watched, QEvent $event)` and returns PHP's bool to Qt, the event alive only during the call |
| `QEvent`, `QInputEvent`, `QMouseEvent`, `QKeyEvent`, `QWheelEvent`, `QContextMenuEvent` | `type`, `accept`, `ignore`, `isAccepted`, `spontaneous`; `modifiers`, `timestamp`, `deviceType` (`QInputDevice\DeviceType`); mouse `button`, `buttons`, `position`, `globalPosition`; key `key` (a `Qt\Key` value), `text`, `isAutoRepeat`, `nativeScanCode`, `nativeVirtualKey`, `matches` (a `QKeySequence\StandardKey`); `QInputMethodEvent` (constructor with the preedit text and its `QInputMethodEvent\Attribute` list, `setCommitString`, `commitString`, `preeditString`; boxed as its class by a filter); wheel `pixelDelta`, `angleDelta`, `position`, `globalPosition`, `source` (`Qt\MouseEventSource`); context menu `reason` (`QContextMenuEvent\Reason`), `pos`, `globalPos`; constructors for the mouse, key, wheel and context-menu events, and a plain `QEvent` of a type Qt sends as one (window activation, the change notices, …; other types are a ValueError), sent with `QCoreApplication::sendEvent` |
| Hit tests, hints | `QApplication::widgetAt`, `QApplication::focusWidget`, `QApplication::activeModalWidget`, `QWidget::mapFromGlobal`, `QGuiApplication::styleHints()` → `QStyleHints` `mousePressAndHoldInterval`, `startDragDistance`, `mouseDoubleClickInterval`, `mouseDoubleClickDistance` |
| `QLayout`, `QLayoutItem` | `setSpacing`, `spacing`, `setContentsMargins`, `count`, `removeWidget`, `indexOf`, `itemAt` (a `QLayoutItem`: `widget`, `layout`, `spacerItem`) |
| `QBoxLayout`, `QVBoxLayout`, `QHBoxLayout` | constructors (optional parent widget), `addWidget(widget, stretch, alignment)`, `insertWidget`, `addLayout`, `addStretch`, `setStretch`, `setAlignment`; widgets added before the layout is installed are held until it is |
| `QGridLayout` | constructor, `addWidget(widget, row, column, rowSpan, columnSpan, alignment)`, `addItem(QSpacerItem, …)`, `rowCount`, `columnCount`, `setRowStretch`, `setColumnStretch`, `rowStretch`, `columnStretch`, `setHorizontalSpacing`, `setVerticalSpacing`, `itemAtPosition` (a `QLayoutItem`) |
| `QSpacerItem` | constructor (w, h, policies), `changeSize`, `sizeHint` |
| `QLabel` | constructor, `text`, `setText`, `alignment`, `setAlignment`, `wordWrap`, `setWordWrap`, `setScaledContents`, `pixmap`, `setPixmap`, `textFormat`, `setTextFormat`, `openExternalLinks`, `setOpenExternalLinks`, `textInteractionFlags`, `setTextInteractionFlags`; signals `linkActivated(QString)`, `linkHovered(QString)` |
| `QDesktopServices` | `openUrl(QUrl)` |
| `QAbstractButton`, `QPushButton`, `QCheckBox` | constructors (text, parent), `text`, `setText`, `isCheckable`, `setCheckable`, `isChecked`, `setChecked`, `click`, `toggle`, push button `isDefault`, `setDefault`; signals `clicked(bool)`, `toggled(bool)` |
| `QAbstractSlider`, `QSlider`, `QScrollBar` | QScrollBar constructor (orientation, parent), or a scroll area's `verticalScrollBar`, `horizontalScrollBar`; QSlider constructor (orientation, vertical by default as in Qt, parent), `minimum`, `maximum`, `setRange`, `value`, `setValue`, `orientation`, `setOrientation`; signal `valueChanged(int)` |
| `QComboBox` | constructor, `addItem`, `addItems`, `clear`, `count`, `currentIndex`, `setCurrentIndex`, `currentText`, `itemText`, `isEditable`, `setEditable`, `lineEdit`, `setCompleter`, `insertPolicy`, `setInsertPolicy`, `setEditText`; signal `currentIndexChanged(int)` |
| `QCompleter`, `QAbstractItemModel`, `QStringListModel` | constructor (model, parent), `setWidget`, `completionMode`, `setCompletionMode`, `setCaseSensitivity`, `completionPrefix`, `setCompletionPrefix`, `complete(rect)`, `popup`; abstract, made through `QStringListModel`; constructor, `setStringList`, `stringList` |
| `QToolButton`, `QIcon`, `QActionGroup` | constructor, `setMenu` (the menu is not taken: its owner outlives the button), `menu`, `popupMode`, `setPopupMode`, `toolButtonStyle`, `setToolButtonStyle`, `autoRaise`, `setAutoRaise`, `showMenu`; value: constructor (`QPixmap`), `isNull`; constructor, `addAction`, `checkedAction` |
| Button icons, tab insert, wheel phase, widget points | `QAbstractButton` `setIcon`, `iconSize`, `setIconSize`; `QPushButton` `isFlat`, `setFlat`; `QTabWidget` `insertTab`; `QWheelEvent` `phase`; `QWidget` `mapToGlobal`, `accessibleName`, `setAccessibleName` |
| `QLineEdit` | constructor (text, parent), `text`, `setText`, `placeholderText`, `setPlaceholderText`, `echoMode`, `setEchoMode`, `isReadOnly`, `setReadOnly`, `cut`, `copy`, `paste`, `selectAll`, `undo`, `redo`, `selectedText`; signals `textChanged(QString)`, `returnPressed()` |
| `QPlainTextEdit` | constructor, `toPlainText`, `setPlainText`, `isReadOnly`, `setReadOnly`, `cut`, `copy`, `paste`, `selectAll`, `undo`, `redo`, `document`, `textCursor`, `setTextCursor`, `ensureCursorVisible`, `setExtraSelections`, `extraSelections`, `lineWrapMode`, `setLineWrapMode`, `textInteractionFlags`, `setTextInteractionFlags`, `verticalScrollBar`, `horizontalScrollBar`, `viewport`; signals `textChanged()`, `cursorPositionChanged()` |
| `QTextDocument` | a text edit's: `findBlockByNumber` (Qt's invalid block past the end), `blockCount`, `characterCount` |
| `QColor`, `QBrush`, `QTextCharFormat`, `QTextCursor`, `QTextBlock`, `QTextEdit\ExtraSelection` | values: `QColor` (`isValid`), `QBrush` (colour, `Qt\BrushStyle`), `QTextCharFormat` (`setForeground`, `setBackground`, `setProperty`, `boolProperty`, `hasProperty`; `QTextFormat::FULL_WIDTH_SELECTION`), `QTextCursor` (UTF-16 positions, `setPosition`, `movePosition` by `QTextCursor\MoveOperation`, `isNull`), `QTextBlock` (`isValid`), `QTextEdit\ExtraSelection` (public `cursor`, `format`) |
| `QFontDatabase` | `systemFont` |
| `QDateEdit`, `QCalendarWidget` | constructor, `date`, `setDate`, `minimumDate`, `setMinimumDate` (`QDate`), `setCalendarPopup`, `calendarWidget`, `setDisplayFormat`; signal `dateChanged(QDate)` hands a `QDate` over |
| `QProgressBar` | constructor, `minimum`, `maximum`, `setRange`, `value`, `setValue`, `setTextVisible`, `reset` |
| `QFrame`, `QScrollArea` | constructors, `frameShape`, `setFrameShape`, `setFrameShadow`; `setWidget`, `widget`, `setWidgetResizable`, `setHorizontalScrollBarPolicy`, `setVerticalScrollBarPolicy` |
| `QSplitter`, `QSplitterHandle`, `QTabWidget` | `QSplitter(Qt\Orientation)`, `orientation`/`setOrientation`, `addWidget`, `insertWidget` (outside 0..count appends), `count`, `widget`, `indexOf`, `setSizes`/`sizes`, `handleWidth`/`setHandleWidth`, `opaqueResize`/`setOpaqueResize`, `childrenCollapsible`/`setChildrenCollapsible`, `setStretchFactor`, `handle`; handle `splitter`; signal `splitterMoved(int,int)`. `addTab`, `removeTab`, `indexOf`, `count`, `currentIndex`/`setCurrentIndex`, `currentWidget`, `setTabText`/`tabText`, `widget`, `documentMode`/`setDocumentMode` (Qt's own index handling: a bad tab index does nothing, `tabText` gives ""); signal `currentChanged(int)` |
| `QAbstractItemView`, `QTableWidget`, `QTableWidgetItem` | `setSelectionBehavior`, `setSelectionMode`, `setEditTriggers`, `NO_EDIT_TRIGGERS`; constructor (rows, columns, parent), `rowCount`, `setRowCount`, `columnCount`, `setColumnCount`, `setHorizontalHeaderLabels`, `horizontalHeaderItem`, `selectedItems`, `clearSelection`, `setItem`, `item`, `clearContents`, `currentRow`, `selectRow`; item constructor, `text`, `setText`, `row`; signals `itemSelectionChanged()`, `cellClicked(int,int)` |
| `QTreeWidget`, `QTreeWidgetItem` | constructor (parent), `columnCount`, `setColumnCount`, `setHeaderLabels`, `addTopLevelItem`, `clear`, `currentItem`, `setCurrentItem`, `scrollToItem` (`QAbstractItemView\ScrollHint`), `expandItem`, `collapseItem`, `selectedItems`; item constructor (type), `text`/`setText`, `foreground`/`setForeground` (`QBrush`), `data`/`setData` (column, role, value as QVariant holds it), `addChild`, `childCount`, `child`, `parent`, `isExpanded`/`setExpanded`, `childIndicatorPolicy`/`setChildIndicatorPolicy`; signals `currentItemChanged(QTreeWidgetItem*,QTreeWidgetItem*)`, `itemSelectionChanged()`, `itemActivated(QTreeWidgetItem*,int)`, `itemExpanded(QTreeWidgetItem*)`, `itemCollapsed(QTreeWidgetItem*)`, their items as the wrappers PHP holds |
| `QFont`, `QPixmap` | values: constructor (family, point size, weight, italic), `family`, `setFamily`, `pointSizeF`, `setPointSizeF`, `weight`, `setWeight`; constructor, `load`, `isNull`, `width`, `height`, `scaled`, `devicePixelRatio`, `setDevicePixelRatio` |
| `QImage`, `QByteArray` | `QImage` borrows the buffer at an address (a `QByteArray`'s or a framebuffer's `pointer()`, trusted), with Qt's cleanup function and info: constructor (data, width, height, bytes per line, `QImage\Format`, cleanup, info), `isNull`, `width`, `height`, `format`, `copy`; `QPixmap::fromImage` turns it into a pixmap. `QByteArray(data, size)`, `size`, `pointer` |
| `QPoint`, `QPointF`, `QSize`, `QRect`, `QDate`, `QKeySequence` | values, as Qt's own: points, sizes and rects in and out of the widget, event and layout calls; `QDate` (`toString`, `fromString` by `Qt\DateFormat`); `QKeySequence` (`toString`, `fromString` by `QKeySequence\SequenceFormat`) |
| `QUrl` | value: constructor (`QUrl\ParsingMode`), `fromLocalFile`, `toString(options)`, `isValid` |
| `QAudioOutput` | constructor, `setMuted`, `isMuted`, `setVolume`, `volume` |
| `QMediaPlayer` | constructor, `setVideoOutput`, `setAudioOutput`, `setSource`, `source`, `play`, `pause`, `stop`, `position`, `duration`, `setPosition`, `playbackState`, `mediaStatus`, `setLoops`, `INFINITE_LOOPS`, `errorString`, `hasVideo`, `isAvailable`; signals `playbackStateChanged`, `mediaStatusChanged`, `errorOccurred`, `positionChanged` |
| `QVideoWidget` | constructor |

Enums: `QEventLoop\ProcessEventsFlag`, `Qt\TimerType`, `QSocketNotifier\Type`,
`QAction\MenuRole`, `Qt\Orientation`, `Qt\AspectRatioMode`, `Qt\ScrollBarPolicy`,
`Qt\ToolButtonStyle`, `Qt\CaseSensitivity`, `QComboBox\InsertPolicy`, `QCompleter\CompletionMode`, `QToolButton\ToolButtonPopupMode`,
`QSizePolicy\Policy`, `QLineEdit\EchoMode`, `QFont\Weight`, `QTextCursor\MoveMode`, `QTextCursor\MoveOperation`, `QPlainTextEdit\LineWrapMode`,
`QFontDatabase\SystemFont`, `Qt\TextInteractionFlag`, `QFrame\Shape`,
`QFrame\Shadow`, `QAbstractItemView\SelectionBehavior`,
`QAbstractItemView\SelectionMode`, `QAbstractItemView\ScrollHint`,
`QTreeWidgetItem\ChildIndicatorPolicy`, `QMediaPlayer\PlaybackState`,
`QMediaPlayer\MediaStatus`, `QMediaPlayer\Error`, and, generated from the Qt
headers by `scripts/gen-enum.php`, `QEvent\Type`, `Qt\WidgetAttribute`,
`Qt\AlignmentFlag`, `Qt\ItemDataRole`, `Qt\ScrollPhase`, `Qt\MouseEventSource` and `Qt\Key` (`KEY_0` … `KEY_9` keep the
prefix; `DEAD_a` / `DEAD_A` keep the case that tells them apart). QFlags parameters (`alignment`) take the enum or an OR'd int.
Function: `qVersion()`. The stubs in `stubs/` are the full declaration.

Signals connect by the signature `SIGNAL()` spells, and the callable receives
the signal's arguments:

```php
QObject::connect($timer, 'timeout()', fn () => …);
QObject::connect($notifier, 'activated(QSocketDescriptor,QSocketNotifier::Type)', fn (int $fd, int $type) => …);
```

## Coverage

[SUPPORT.md](https://github.com/php-io-extensions/qt/blob/v0.11.0/SUPPORT.md) lists every public member function name of the classes QtCore, QtGui and
QtWidgets declare (signals, operators, deprecated members and the value classes the extension
marshals as PHP strings and arrays left out; overloads count once), each marked bound or not; the
API badge is computed from it. Regenerate both after a binding change, and check them:

```bash
php84 scripts/support.php           # writes SUPPORT.md and the badge
php84 scripts/support.php --check   # exits 1 when either is stale
```

## Example

```php
$argc = 1;
$app = new QApplication($argc, [PHP_BINARY]);

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
