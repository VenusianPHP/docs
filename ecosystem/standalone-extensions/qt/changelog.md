# Changelog

What changed in this package, newest first.

### 2026-10-10

* `QInputEvent::setTimestamp` (ms, not negative), so tests stamp events the way Qt stamps real ones. [surface](/docs/{{version}}/ecosystem/standalone-extensions/qt/guide/binding-surface)
* QLabel openExternalLinks and textInteractionFlags (`Qt\TextInteractionFlag`, generated), its linkActivated / linkHovered signals documented, QDesktopServices::openUrl (toolkit links). [surface](/docs/{{version}}/ecosystem/standalone-extensions/qt/guide/binding-surface)
* `QApplication::focusWidget`, `QWidget::setFocus`/`hasFocus`, and the edit slots (cut, copy, paste, selectAll, undo, redo) of `QLineEdit` and `QPlainTextEdit`, plus `QLineEdit::selectedText`, for the Edit menu (HumanInput slice 29). [surface](/docs/{{version}}/ecosystem/standalone-extensions/qt/guide/binding-surface)

### 2026-10-09

* `QMenu::popup(x, y)`: a menu at a global point, returning at once. For context menus (HumanInput slice 27). [surface](/docs/{{version}}/ecosystem/standalone-extensions/qt/guide/binding-surface)
* Compiled into PHP (`--enable-qt` in php-src, as `venusian build` does), the Qt libraries join PHP's link line (macOS frameworks and their `-F` included); before, only a shared build linked them and the static link failed on every Qt symbol. Compiled in without ext/sockets, `Socket` arguments are not accepted instead of failing to compile. [build](/docs/{{version}}/ecosystem/standalone-extensions/qt/runbooks/build-install-test)
* `extra.venusian.system` in composer.json: the apt packages `venusian build` installs to compile the extension, the run-time packages a `.deb` carrying it depends on or recommends beyond what `dpkg-shlibdeps` sees, and the Homebrew packages for a dev install.
* Floor Qt 6.4 (Ubuntu 24.04): five `QEvent` checks guarded by `gen-enum.php --since`; build.json apps on the 24.04 image compile ext-qt. [generating enums](/docs/{{version}}/ecosystem/standalone-extensions/qt/runbooks/generating-enums)
* `QEventFilter` callbacks get the event as a third argument, alive only during the call; `QEvent`, `QInputEvent`, `QMouseEvent`, `QContextMenuEvent` (+ enums `QContextMenuEvent\Reason`, `QInputDevice\DeviceType`); `QCoreApplication::sendEvent`, `QApplication::widgetAt`, `QWidget::mapFromGlobal`, `QGuiApplication::styleHints()`/`QStyleHints`. For right-click mail (HumanInput slice 26). [surface](/docs/{{version}}/ecosystem/standalone-extensions/qt/guide/binding-surface)

### 2026-10-06

* `QWindow::destroy()`; `QVulkanInstance` is made on the main thread only. Suite 108 on Homebrew PHP 8.4 NTS and ZTS, 107 + 1 skipped on the Pi. [surface](/docs/{{version}}/ecosystem/standalone-extensions/qt/guide/binding-surface)
* `QVulkanInstance` over an application's `VkInstance` and `QVulkanInstance::surfaceForWindow()`; `QWindow::setVulkanInstance()`/`vulkanInstance()`, `resize()`, `close()`. Freeing the instance destroys and detaches the windows using it; `create()` without a QGuiApplication is a QtException (Qt dereferenced a null platform). macOS needs `QT_VULKAN_LIB` naming the loader. Suite 107 on Homebrew PHP 8.4 NTS and ZTS, 106 + 1 skipped on the Pi (Qt on Wayland). [surface](/docs/{{version}}/ecosystem/standalone-extensions/qt/guide/binding-surface)
* `QOpenGLWidget` and the `QOpenGLPainter` trampoline (`paintGL()` runs PHP with the context current and the widget's framebuffer object bound); the build needs Qt6OpenGL and Qt6OpenGLWidgets. `QSurfaceFormat` and `QOpenGLWidget::setFormat()`/`format()`: macOS gives a widget a legacy 2.1 context unless it asks for 4.1 core; the Pi's default is desktop GL 3.1 (GLSL 1.40). A slot Qt destroys frees its callable with its ancestors marked as tearing down: an owned, parentless ancestor freed then goes to `deleteLater()` instead of being deleted under Qt (it segfaulted or deadlocked). Suite 101 on Homebrew PHP 8.4 NTS and ZTS, 100 + 1 skipped on the Pi. [surface](/docs/{{version}}/ecosystem/standalone-extensions/qt/guide/binding-surface), [object model](/docs/{{version}}/ecosystem/standalone-extensions/qt/architecture/object-model)

### 2026-10-05

* Extension version is 0.10.2. `QWindow` (surface type, `winId`, create/show/hide, size, pixel ratio), `QSurface\SurfaceType`, `QWidget::createWindowContainer()`. [surface](/docs/{{version}}/ecosystem/standalone-extensions/qt/guide/binding-surface)

### 2026-10-04

* Extension version is 0.10.1. `QImage` copies from an address as well as a string: the constructor's `$data` widens to `string|int`, an address trusted to hold `$bytesPerLine × $height` readable bytes (an ext-fb buffer's `pointer()`), never 0. [surface](/docs/{{version}}/ecosystem/standalone-extensions/qt/guide/binding-surface)

### 2026-10-03

* Pixels from bytes: `QImage` (a deep copy of the bytes it is given), `QImage\Format`, `QPixmap::fromImage()`. [surface](/docs/{{version}}/ecosystem/standalone-extensions/qt/guide/binding-surface)

### 2026-10-02

* Toolkit primitives slice, ext side. [Surface](/docs/{{version}}/ecosystem/standalone-extensions/qt/guide/binding-surface): QLayout/QBoxLayout/QVBoxLayout/QHBoxLayout/QGridLayout, QWidget geometry/size-policy/style/font/enabled methods, QObject::children; QLabel, QAbstractButton/QPushButton/QCheckBox, QAbstractSlider/QSlider, QComboBox, QLineEdit, QPlainTextEdit, QDateEdit, QProgressBar, QFrame, QScrollArea, QAbstractItemView/QTableWidget/QTableWidgetItem, QFont, QPixmap; QUrl, QAudioOutput, QMediaPlayer, QVideoWidget. Enums `Qt\AlignmentFlag` (generated), `QSizePolicy\Policy`, `Qt\Orientation`, `Qt\AspectRatioMode`, `Qt\ScrollBarPolicy`, `QLineEdit\EchoMode`, `QFont\Weight`, `QFrame\Shape/Shadow`, `QAbstractItemView\SelectionBehavior/SelectionMode`, `QMediaPlayer\PlaybackState/MediaStatus/Error`.
* New: [layout](/docs/{{version}}/ecosystem/standalone-extensions/qt/guide/layout-and-geometry), [video](/docs/{{version}}/ecosystem/standalone-extensions/qt/guide/video). [Object model](/docs/{{version}}/ecosystem/standalone-extensions/qt/architecture/object-model): value objects and the table item's second owner. [Signals](/docs/{{version}}/ecosystem/standalone-extensions/qt/architecture/signals): QDate as ISO string. [Build](/docs/{{version}}/ecosystem/standalone-extensions/qt/runbooks/build-install-test): Qt Multimedia required by `config.m4` and both installers.
* `phpqt_qstring`/`phpqt_return_qstring` and the widget constructor templates moved into `runtime.h`.
* Driver review bindings: `QGridLayout` row/column stretch and `addItem(QSpacerItem)`, `QSpacerItem`, `QBoxLayout::stretch`, `QLayout::invalidate`, `QLabel::textFormat` + `Qt\TextFormat`, slider single/page step, `QPixmap::scaled` transformation + device pixel ratio, `QWidget::devicePixelRatioF`, `QDateEdit::calendarWidget`/`minimumDate`, `invokeMethod` arguments. Value objects gained a `forget` hook so every owner-held kind (table item, spacer) clears its back-pointer the same way.
* `QAbstractItemView::clearSelection`, `QTableWidget::selectedItems`, `QTableWidgetItem::row` ([surface](/docs/{{version}}/ecosystem/standalone-extensions/qt/guide/binding-surface)): a driver reads which row is selected, including none, and clears it.
* `QMetaObject::invokeMethod(object, member)` ([surface](/docs/{{version}}/ecosystem/standalone-extensions/qt/guide/binding-surface)): emits a signal by name, so drivers' tests can drive `returnPressed()` without a keyboard.
* Review fixes: [layout](/docs/{{version}}/ecosystem/standalone-extensions/qt/guide/layout-and-geometry) holds for widgets added before installation; `insertWidget` and `setItem` range checks; Qt-made table items tracked through an item prototype, `horizontalHeaderItem`; `QPixmap` refused before a QGuiApplication; a second `__construct()` refused; `QSlider` defaults to vertical as Qt; `QFont` weight takes the 1–1000 scale; `QMediaPlayer::isAvailable`; installers require a Multimedia backend plugin ([object model](/docs/{{version}}/ecosystem/standalone-extensions/qt/architecture/object-model), [video](/docs/{{version}}/ecosystem/standalone-extensions/qt/guide/video), [build](/docs/{{version}}/ecosystem/standalone-extensions/qt/runbooks/build-install-test)).

### 2026-10-01

* Runbooks [adding a binding](/docs/{{version}}/ecosystem/standalone-extensions/qt/runbooks/adding-a-binding), [generating enums](/docs/{{version}}/ecosystem/standalone-extensions/qt/runbooks/generating-enums).
* [Surface](/docs/{{version}}/ecosystem/standalone-extensions/qt/guide/binding-surface): QWidget, QMainWindow, QMenuBar, QMenu, QAction, QDialog, QMessageBox, QEventFilter, installEventFilter/removeEventFilter, QAction\MenuRole, generated QEvent\Type and Qt\WidgetAttribute with the generator. [Signals](/docs/{{version}}/ecosystem/standalone-extensions/qt/architecture/signals): QEventFilter.

### 2026-09-30

* Bundle created with ext-qt 0.10.0: [surface](/docs/{{version}}/ecosystem/standalone-extensions/qt/guide/binding-surface), [object model](/docs/{{version}}/ecosystem/standalone-extensions/qt/architecture/object-model), [signals](/docs/{{version}}/ecosystem/standalone-extensions/qt/architecture/signals), [errors and threads](/docs/{{version}}/ecosystem/standalone-extensions/qt/architecture/errors-and-threads), [build](/docs/{{version}}/ecosystem/standalone-extensions/qt/runbooks/build-install-test).
