# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('README.md', '.')],
    hiddenimports=['PyQt5', 'PyQt5.QtCore', 'PyQt5.QtGui', 'PyQt5.QtWidgets', 'cv2', 'numpy'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'scipy', 'PIL', 'tkinter', 'PyQt5.QtWebEngineWidgets', 'PyQt5.QtWebEngine', 'PyQt5.QtWebEngineCore', 'PyQt5.QtWebEngineQuick', 'PyQt5.QtWebSockets', 'PyQt5.QtNetwork', 'PyQt5.QtSql', 'PyQt5.QtTest', 'PyQt5.QtXml', 'PyQt5.QtXmlPatterns', 'PyQt5.QtDesigner', 'PyQt5.QtHelp', 'PyQt5.QtOpenGL', 'PyQt5.QtPrintSupport', 'PyQt5.QtQml', 'PyQt5.QtQuick', 'PyQt5.QtQuickWidgets', 'PyQt5.QtSvg', 'PyQt5.QtSvgWidgets', 'PyQt5.QtWebChannel', 'cv2.cuda', 'cv2.gapi', 'cv2.ml', 'cv2.ocl', 'cv2.videoio_registry', 'cv2.utils', 'numpy.random._examples', 'numpy.doc', 'numpy.f2py', 'numpy.distutils', 'numpy.testing', 'numpy.core.tests', 'numpy.lib.tests', 'numpy.linalg.tests', 'numpy.ma.tests', 'numpy.matrixlib.tests', 'numpy.polynomial.tests', 'numpy.random.tests', 'numpy.tests'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='VideoProcessor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    uac_admin=True,
)
